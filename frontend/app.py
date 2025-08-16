import streamlit as st
import uuid
import json
import sys
import os
import requests


# Add root dir so utils/ can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from streamlit.components.v1 import html as components_html
from utils.llm import generate_bot_config_gemini, chat_with_gemini
from utils.bot_ops import load_bots, save_bots, delete_bot, rename_bot, update_personality
from utils.chat_ops import load_chat_history, save_chat_history, clear_chat_history
from ui import apply_custom_styles, show_header 

from utils.firebase_config import db

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
import uuid
import streamlit as st
from utils.llm import generate_bot_config_gemini

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

        bot_id = str(uuid.uuid4())
        bot_data = {
            "id": bot_id,
            "name": cfg["name"],
            "personality": cfg["personality"],
            "settings": cfg.get("settings", {}),
        }

        # Save to Firebase
        db.collection("bots").document(bot_id).set(bot_data)

        st.success(f"✅ Bot '{cfg['name']}' created and saved!")
        st.experimental_rerun()  # Refresh to show the new bot

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

# ---------------- CHAT INTERFACE ----------------
def chat_interface():
    st.header("💬 Chat with Your Bot")
    st.markdown("---")

    bots = load_bots()  # list of dicts
    if not bots:
        st.info("No bots available — create one above.")
        return

    # Create list of tuples (label, bot_id) for selectbox
    bot_items = [(f"{b['name']} ({b['id'][:6]})", b['id']) for b in bots]

    selected_label, selected_bot_id = st.selectbox(
        "Choose a bot",
        options=bot_items,
        format_func=lambda x: x[0],
        key="chat_selectbox"
    )

    # Fetch selected bot info
    selected_bot_info = next(b for b in bots if b['id'] == selected_bot_id)

    st.markdown("---")

    # Load & normalize chat history once per bot
    if "chat_bot_id" not in st.session_state or st.session_state.chat_bot_id != selected_bot_id:
        st.session_state.chat_bot_id = selected_bot_id
        raw_history = load_chat_history(selected_bot_id)
        st.session_state.history = normalize_history(raw_history)

    history = st.session_state.history

    if "typing" not in st.session_state:
        st.session_state.typing = False

    # Iframe HTML (unchanged UI)
    history_json = json.dumps(history)
    typing_json = json.dumps(bool(st.session_state.typing))
    iframe_html = f"""
    <!doctype html>
    <html>
    <head>
      <meta charset="utf-8" />
      <style>
        body {{ margin:0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial; }}
        .chat-box {{
            height: 500px;
            overflow-y: auto;
            padding: 12px;
            width: 100%;
            box-sizing: border-box;
            background: transparent;
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
                div.textContent = (turn.role === 'user' ? '🧑 ' : '🤖 ') + turn.content;
                box.appendChild(div);
            }}
            if (typing) {{
                const t = document.createElement('div');
                t.className = 'msg-typing';
                t.textContent = '🤖 typing…';
                box.appendChild(t);
            }}
            box.scrollTop = box.scrollHeight;
            setTimeout(()=>{{ box.scrollTop = box.scrollHeight; }}, 50);
            setTimeout(()=>{{ box.scrollTop = box.scrollHeight; }}, 300);
        }}
        setTimeout(renderChat, 10);
      </script>
    </body>
    </html>
    """
    components_html(iframe_html, height=460, width=1200, scrolling=True)

    # User input
    user_input = st.chat_input("Type your message…")
    if user_input:
        history.append({"role": "user", "content": user_input})
        save_chat_history(selected_bot_id, history)
        st.session_state.history = history
        st.session_state.typing = True
        st.rerun()

    if st.session_state.typing:
        reply = chat_with_gemini(history[-1]["content"], selected_bot_info["personality"])
        history.append({"role": "bot", "content": reply})
        save_chat_history(selected_bot_id, history)
        st.session_state.history = history
        st.session_state.typing = False
        st.rerun()

# ---------------- BOT MANAGEMENT ----------------
BACKEND="https://mentesa-2kf8.onrender.com"
from utils.firebase_config import db

import requests
import streamlit as st
from utils.firebase_config import db

BACKEND = "https://your-backend-url.com"  # Set your deployed backend URL

def bot_management_ui():
    st.subheader("🛠️ Manage Your Bots")
    bots = load_bots()
    if not bots:
        st.info("No bots available — create one first.")
        return

    # Select bot
    bot_options = {f"{b['name']} ({b['id'][:6]})": b['id'] for b in bots}
    selected_label = st.selectbox("Choose a bot", list(bot_options.keys()), key="manage_select")
    selected_bot_id = bot_options[selected_label]
    selected_bot_info = next(b for b in bots if b['id'] == selected_bot_id)

    # --- Bot management columns ---
    col1, col2, col3, col4 = st.columns([2, 3, 1, 1])

    new_name = col1.text_input("Name", value=selected_bot_info['name'], key=f"name_{selected_bot_id}")
    if col1.button("✏️ Rename", key=f"rename_{selected_bot_id}"):
        db.collection("bots").document(selected_bot_id).update({"name": new_name})
        st.success("Renamed!")
        st.experimental_rerun()

    new_persona = col2.text_area(
        "Personality", value=selected_bot_info['personality'], key=f"persona_{selected_bot_id}", height=80
    )
    if col2.button("✏️ Update", key=f"update_{selected_bot_id}"):
        db.collection("bots").document(selected_bot_id).update({"personality": new_persona})
        st.success("Personality updated!")
        st.experimental_rerun()

    if col3.button("🧹 Clear Chat", key=f"manage_clear_{selected_bot_id}"):
        # Optional: Implement chat clearing in Firestore
        st.success("Chat history cleared!")
        st.experimental_rerun()

    if col4.button("🗑️ Delete", key=f"delete_{selected_bot_id}"):
        db.collection("bots").document(selected_bot_id).delete()
        st.success("Bot deleted!")
        st.experimental_rerun()

    # --- Embed snippet ---
    st.markdown("---")
    st.write("📄 **Embed this bot on your website:**")

    if "api_keys" not in st.session_state:
        st.session_state.api_keys = {}

    if selected_bot_id not in st.session_state.api_keys:
        try:
            resp = requests.get(f"{BACKEND}/bots/{selected_bot_id}/apikey")
            st.session_state.api_keys[selected_bot_id] = resp.json().get("api_key") if resp.status_code == 200 else None
        except Exception:
            st.session_state.api_keys[selected_bot_id] = None

    api_key = st.session_state.api_keys.get(selected_bot_id)

    if api_key:
        embed_code = f'<script src="{BACKEND}/static/embed.js" data-api-key="{api_key}" data-bot-name="{selected_bot_info["name"]}"></script>'
        st.code(embed_code, language="html")
        st.markdown(f"""
        **How to use this snippet:**

        1. Copy the code above.
        2. Paste it before the closing `</body>` tag on your website.
        3. Save and refresh your site to see the bot.
        """)
    else:
        st.warning("Could not fetch API key for this bot.")

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

