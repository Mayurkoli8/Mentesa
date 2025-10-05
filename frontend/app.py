import streamlit as st
import uuid
import json
import sys
import os
import requests
import google.generativeai


# Add root dir so utils/ can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from streamlit.components.v1 import html as components_html
from utils.llm import generate_bot_config_gemini, chat_with_gemini
from utils.bot_ops import load_bots, save_bots, delete_bot, rename_bot, update_personality
from utils.chat_ops import load_chat_history, save_chat_history, clear_chat_history
from ui import apply_custom_styles, show_header, logo_animation

from utils.firebase_config import db
BACKEND="https://mentesav7.onrender.com"


# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Mentesa V7",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <meta name="description" content="Mentesa – A no-code platform to create, manage, and chat with your own AI bots.">
    <meta name="keywords" content="AI bots, chatbot builder, Mentesa, generative AI, Streamlit">
""", unsafe_allow_html=True)


# Apply styles
apply_custom_styles()

# Logo Mentesa animation
logo_animation()

# # Show header
# show_header()

# ---------------- BOT CREATION ----------------
import uuid
import streamlit as st
from utils.llm import generate_bot_config_gemini


def create_and_save_bot():
    st.subheader("✨ Create Your Bot")
    st.write("Describe the bot you want, and we'll generate it with AI.")

    name="Mentesa_Bot"
    prompt = st.text_area("🤔 What type of bot do you want?")
    url = st.text_input("🌐 (Optional) Website URL for the bot to ingest (include https://)")

    if st.button("🚀 Create Bot"):
        if not prompt.strip():
            st.warning("Please enter a prompt before generating.")
            return

        # Auto-generate name if not given
        import time
        bot_name = name.strip() if name.strip() else f"Bot_{int(time.time())}"

        payload = {
            "name": bot_name.strip(),
            "prompt": prompt.strip(),
            "url": url.strip() if url.strip() else None,
            "config": {}
        }


        with st.spinner("Generating bot..."):
            try:
                response = requests.post(f"{BACKEND}/bots", json=payload, timeout=120)
            except Exception as e:
                st.error(f"Request failed: {e}")
                return

        if response.status_code in (200, 201):
            data = response.json()
            bot_name = data["bot"]["name"]
            st.success(f"✅ Bot '{bot_name}' created and saved!")
        else:
            st.error(f"Failed to save bot: {response.text}")

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

    # --- Load bots from Firebase ---
    bots_ref = db.collection("bots").stream()
    bots = []
    for doc in bots_ref:
        data = doc.to_dict()
        data["id"] = doc.id
        bots.append(data)

    if not bots:
        st.info("No bots available — create one above.")
        return

    # --- Select bot ---
    bot_items = [(f"{b['name']} ({b['id'][:6]})", b['id']) for b in bots]

    selected_label, selected_bot_id = st.selectbox(
        "Choose a bot",
        options=bot_items,
        format_func=lambda x: x[0],
        key="chat_selectbox"
    )

    selected_bot_info = next(b for b in bots if b['id'] == selected_bot_id)

    st.markdown("---")

    # --- Load chat history from Firebase ---
    if "chat_bot_id" not in st.session_state or st.session_state.chat_bot_id != selected_bot_id:
        st.session_state.chat_bot_id = selected_bot_id
        history_doc = db.collection("bot_chats").document(selected_bot_id).get()
        if history_doc.exists:
            st.session_state.history = history_doc.to_dict().get("history", [])
        else:
            st.session_state.history = []

    history = st.session_state.history

    if "typing" not in st.session_state:
        st.session_state.typing = False

    # --- Iframe for chat UI ---
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

    # --- User input ---
    user_input = st.chat_input("Type your message…")
    if user_input:
        history.append({"role": "user", "content": user_input})
        st.session_state.history = history
        st.session_state.typing = True
        # Save immediately to Firebase
        db.collection("bot_chats").document(selected_bot_id).set({"history": history})
        st.rerun()

    # --- Generate bot reply ---
    if st.session_state.typing:
        response = requests.post(
            f"{BACKEND}/chat",
            json={"bot_id": selected_bot_id, "message": history[-1]["content"]},
            timeout=60
        )
        
        if response.status_code != 200:
            st.error(f"❌ Chat request failed: {response.status_code}\n{response.text}")
            return
        
        try:
            data = response.json()
            reply = data.get("reply", "⚠️ No reply received")
        except Exception as e:
            st.error(f"❌ Failed to parse JSON: {e}\nRaw response:\n{response.text}")
            return
        
        
        history.append({"role": "bot", "content": reply})
        st.session_state.history = history
        st.session_state.typing = False
        # Save reply to Firebase
        db.collection("bot_chats").document(selected_bot_id).set({"history": history})
        st.rerun()

# ---------------- BOT MANAGEMENT ----------------

def bot_management_ui():
    st.subheader("🛠️ Manage Your Bots")

    # Load bots from Firebase
    bots = []
    for doc in db.collection("bots").stream():
        bot = doc.to_dict()
        bot["id"] = doc.id  # add the document ID
        bots.append(bot)

    if not bots:
        st.info("No bots available — create one first.")
        return

    # --- Select bot ---
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
        st.rerun()

    new_persona = col2.text_area("Personality", value=selected_bot_info['personality'], key=f"persona_{selected_bot_id}", height=80)
    if col2.button("✏️ Update", key=f"update_{selected_bot_id}"):
        db.collection("bots").document(selected_bot_id).update({"personality": new_persona})
        st.success("Personality updated!")
        st.rerun()

    if col3.button("🧹 Clear Chat", key=f"manage_clear_{selected_bot_id}"):
        db.collection("bot_chats").document(selected_bot_id).delete()
        if "history" in st.session_state:
            st.session_state.history=[]
        st.success("Chat history cleared!")
        st.rerun()

    if col4.button("🗑️ Delete", key=f"delete_{selected_bot_id}"):
        db.collection("bots").document(selected_bot_id).delete()
        st.success("Bot deleted!")
        st.rerun()

    # --- Embed snippet ---
    st.markdown("---")
    st.write("📄 **Embed this bot on your website:**")

    api_key = selected_bot_info.get("api_key")
    if api_key:
        embed_code = f'<script src="{BACKEND}/static/embed.js" data-api-key="{api_key}" data-bot-name="{selected_bot_info["name"]}"></script>'
        st.code(embed_code, language="html")


        # Instructions
        st.markdown(f"""
        **How to use this snippet:**

        1. Copy the code above (click inside the box and use Ctrl+C or your preferred copy method).
        2. Open your website’s HTML (index.html) file.
        3. Paste the snippet **before the closing `</body>` tag**.
        4. Save your file and refresh your website.
        5. The chat widget for **{selected_bot_info['name']}** will appear in the bottom-right corner.
        6. Users can now chat with your bot directly on your site!

        > ⚠️ Make sure your website allows external scripts if hosting backend separately.
        """)
    else:
        st.warning("API key not found for this bot.")

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

