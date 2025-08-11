import streamlit as st
import uuid
import json
import sys
import os

# Add root dir so utils/ can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from streamlit.components.v1 import html as components_html
from utils.llm import generate_bot_config_gemini, chat_with_gemini
from utils.bot_ops import load_bots, save_bots, delete_bot, rename_bot, update_personality
from utils.chat_ops import load_chat_history, save_chat_history, clear_chat_history
from ui import apply_custom_styles, show_header 
# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Mentesa",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="expanded"
)
# Apply styles
apply_custom_styles()

# Show header
show_header()
# ---------------- BOT CREATION ----------------
def create_and_save_bot():
    st.subheader("✨ Create Your Bot")
    st.write("Describe the bot you want, and we'll generate it with AI.")

    prompt = st.text_area("🤔 What type of bot do you want?")

    if st.button("🚀 Create Bot"):
        if not prompt.strip():
            st.warning("Please enter a prompt before generating.")
            return

        with st.spinner("Generating bot..."):
            cfg = generate_bot_config_gemini(prompt)

        if not cfg or "error" in cfg:
            st.error(f"Failed to generate bot: {cfg.get('error', 'No data returned')}")
            return

        bots = load_bots()
        bot_id = str(uuid.uuid4())
        bots[bot_id] = {
            "name": cfg["name"],
            "personality": cfg["personality"],
            "settings": cfg.get("settings", {})
        }
        save_bots(bots)

        st.success(f"✅ Bot '{cfg['name']}' created and saved!")

# ---------------- CHAT INTERFACE ----------------
def normalize_history(raw_history):
    """Convert old {'user':'', 'bot':''} into [{'role','content'}, ...]."""
    normalized = []
    for turn in raw_history:
        if isinstance(turn, dict):
            if "role" in turn and "content" in turn:
                normalized.append({"role": turn["role"], "content": turn["content"]})
            elif "user" in turn and "bot" in turn:
                normalized.append({"role": "user", "content": turn["user"]})
                normalized.append({"role": "bot", "content": turn["bot"]})
    return normalized

def chat_interface():
    st.header("💬 Chat with Your Bot")
    st.markdown("---")

    bots = load_bots()
    if not bots:
        st.info("No bots available — create one above.")
        return

    bot_items = list(bots.items())
    bot_id, bot_info = st.selectbox(
        "Choose a bot",
        options=bot_items,
        format_func=lambda x: f"{x[1]['name']} ({x[0][:6]})",
        key="chat_select",
    )
    st.markdown("---")

    # load & normalize once per bot
    if "chat_bot_id" not in st.session_state or st.session_state.chat_bot_id != bot_id:
        st.session_state.chat_bot_id = bot_id
        raw_history = load_chat_history(bot_id)
        st.session_state.history = normalize_history(raw_history)

    history = st.session_state.history

    # typing flag default
    if "typing" not in st.session_state:
        st.session_state.typing = False

    # Prepare the JSON that we'll embed in the iframe
    # Ensure it's in proper role/content format
    history_json = json.dumps(history)
    typing_json = json.dumps(bool(st.session_state.typing))

    # Build the iframe HTML which will render messages and reliably scroll
    iframe_html = f"""
    <!doctype html>
    <html>
    <head>
      <meta charset="utf-8" />
      <style>
        body {{ margin:0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial; }}
        .chat-box {{
            height: 420px;
            overflow-y: auto;
            padding: 12px;
            max-width: 80%;
            box-sizing: border-box;
            background: transaparent;
        }}
        .msg-user {{
            background: #0084ff;
            color: white;
            padding: 8px 12px;
            border-radius: 12px;
            max-width: max-content;
            margin-bottom: 8px;
            margin-left: auto;
            text-align: right;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        .msg-bot {{
            background: #f1f0f0;
            color: #000;
            padding: 8px 12px;
            border-radius: 12px;
            max-width: 70%;
            margin-bottom: 8px;
            margin-right: auto;
            text-align: left;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        .msg-typing {{
            background: #f1f0f0;
            color: black;
            padding: 8px 12px;
            border-radius: 12px;
            max-width: 30%;
            margin-bottom: 8px;
            margin-right: auto;
            font-style: italic;
            opacity: 1;
        }}
      </style>
    </head>
    <body>
      <div id="chat-scroll-box" class="chat-box"></div>

      <script>
        const history = {history_json};
        const typing = {typing_json};

        function renderChat() {{
            const box = document.getElementById('chat-scroll-box');
            box.innerHTML = "";
            for (let i=0;i<history.length;i++) {{
                const turn = history[i];
                const div = document.createElement('div');
                div.className = turn.role === 'user' ? 'msg-user' : 'msg-bot';
                // Use textContent so it's safe; CSS pre-wrap preserves newlines
                div.textContent = (turn.role === 'user' ? '🧑 ' : '🤖 ') + turn.content;
                box.appendChild(div);
            }}
            if (typing) {{
                const t = document.createElement('div');
                t.className = 'msg-typing';
                t.textContent = '🤖 typing…';
                box.appendChild(t);
            }}
            // Scroll to bottom multiple times to be robust
            box.scrollTop = box.scrollHeight;
            setTimeout(()=>{{ box.scrollTop = box.scrollHeight; }}, 50);
            setTimeout(()=>{{ box.scrollTop = box.scrollHeight; }}, 300);
        }}

        // Wait a tick so the element is surely painted, then render
        setTimeout(renderChat, 10);
      </script>
    </body>
    </html>
    """

    # Render chat in an iframe. Height slightly larger than chat-box to accommodate padding.
    components_html(iframe_html, height=460, scrolling=True)

    # User input area below the iframe
    user_input = st.chat_input("Type your message…")

    if user_input:
        # append user message immediately and save
        history.append({"role": "user", "content": user_input})
        save_chat_history(bot_id, history)
        st.session_state.history = history

        # set typing and rerun to render typing bubble inside iframe
        st.session_state.typing = True
        st.rerun()

    # If typing flag is set, generate bot reply (this runs after the rerun that showed typing)
    if st.session_state.typing:
        reply = chat_with_gemini(history[-1]["content"], bot_info["personality"])
        history.append({"role": "bot", "content": reply})
        save_chat_history(bot_id, history)
        st.session_state.history = history
        st.session_state.typing = False
        st.rerun()

# ---------------- BOT MANAGEMENT ----------------
def bot_management_ui():
    st.subheader("🛠️ Manage Your Bots")
    bots = load_bots()
    if not bots:
        st.info("No bots to manage — create one first.")
        return

    bot_options = {
        f"{info['name']} ({bot_id[:6]})": bot_id
        for bot_id, info in bots.items()
    }
    selected_label = st.selectbox("Select a bot to manage:", list(bot_options.keys()))
    selected_bot_id = bot_options[selected_label]
    selected_bot_info = bots[selected_bot_id]

    col1, col2, col3, col4 = st.columns([2, 3, 1, 1])

    new_name = col1.text_input(
        "Name", value=selected_bot_info['name'], key=f"name_{selected_bot_id}"
    )
    if col1.button("✏️ Rename", key=f"rename_{selected_bot_id}"):
        rename_bot(selected_bot_id, new_name)
        st.success("Renamed!")
        st.rerun()

    new_persona = col2.text_area(
        "Personality",
        value=selected_bot_info['personality'],
        key=f"persona_{selected_bot_id}",
        height=80,
    )
    if col2.button("✏️ Update", key=f"update_{selected_bot_id}"):
        update_personality(selected_bot_id, new_persona)
        st.success("Personality updated!")
        st.rerun()

    if col3.button("🧹 Clear Chat", key=f"manage_clear_{selected_bot_id}"):
        clear_chat_history(selected_bot_id)
        st.success("Chat history cleared!")
        st.rerun()

    if col4.button("🗑️ Delete", key=f"delete_{selected_bot_id}"):
        delete_bot(selected_bot_id)
        st.success("Bot deleted!")
        st.rerun()

# ---------------- MAIN APP ----------------
def main():
    tabs = st.tabs(["➕ Create Bot", "🛠️ Manage Bots", "💬 My Bots"])

    with tabs[0]:
        create_and_save_bot()
    with tabs[1]:
        bot_management_ui()
    with tabs[2]:
        chat_interface()

if __name__ == "__main__":
    main()

