import streamlit as st
import uuid
import json
import requests
import sys
import os

# Add project root to path if needed for ui module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ui import apply_custom_styles, show_header

# ---------------- CONFIG ----------------
BACKEND_URL = "http://localhost:8000"

# ---------------- PAGE SETUP ----------------
st.set_page_config(
    page_title="Mentesa",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="expanded"
)
apply_custom_styles()
show_header()

# ---------------- SESSION STATE ----------------
if "chat_bot_id" not in st.session_state:
    st.session_state.chat_bot_id = None
if "history" not in st.session_state:
    st.session_state.history = []
if "awaiting_reply" not in st.session_state:
    st.session_state.awaiting_reply = False

# ---------------- API FUNCTIONS ----------------
def load_bots():
    try:
        resp = requests.get(f"{BACKEND_URL}/bots/")
        resp.raise_for_status()
        return resp.json()  # list of bots
    except Exception as e:
        st.error(f"Failed to load bots: {e}")
        return []

def create_bot_api(name, personality="Neutral"):
    try:
        resp = requests.post(f"{BACKEND_URL}/bots", json={"name": name, "personality": personality})
        resp.raise_for_status()
        return resp.json()  # returns bot dict
    except Exception as e:
        st.error(f"Failed to create bot: {e}")
        return None

def delete_bot_api(bot_id):
    try:
        resp = requests.delete(f"{BACKEND_URL}/bots/{bot_id}")
        resp.raise_for_status()
    except Exception as e:
        st.error(f"Failed to delete bot: {e}")

def rename_bot_api(bot_id, new_name):
    try:
        resp = requests.put(f"{BACKEND_URL}/bots/{bot_id}/name", json={"name": new_name})
        resp.raise_for_status()
    except Exception as e:
        st.error(f"Failed to rename bot: {e}")

def update_personality_api(bot_id, personality):
    try:
        resp = requests.put(f"{BACKEND_URL}/bots/{bot_id}/personality", json={"personality": personality})
        resp.raise_for_status()
    except Exception as e:
        st.error(f"Failed to update personality: {e}")

def chat_with_bot_api(bot_id, message):
    try:
        resp = requests.post(f"{BACKEND_URL}/bots/{bot_id}/chat", json={"message": message})
        resp.raise_for_status()
        return resp.json().get("reply", "")
    except Exception as e:
        st.error(f"Chat failed: {e}")
        return "🤖 Error generating reply."

# ---------------- BOT CREATION ----------------
def create_and_save_bot():
    st.subheader("✨ Create Your Bot")
    st.write("Describe the bot you want, and we'll generate it with AI.")
    prompt = st.text_area("🤔 What type of bot do you want?")
    if st.button("🚀 Create Bot"):
        if not prompt.strip():
            st.warning("Please enter a prompt.")
            return
        # Use prompt as bot name and generate default personality
        with st.spinner("Creating bot..."):
            bot = create_bot_api(name=prompt, personality="Friendly")
        if bot:
            st.success(f"✅ Bot '{bot['name']}' created!")

# ---------------- CHAT ----------------
def normalize_history(raw_history):
    normalized = []
    for turn in raw_history:
        if "role" in turn and "content" in turn:
            normalized.append({"role": turn["role"], "content": turn["content"]})
    return normalized

# ---------------- CHAT INTERFACE ----------------

def chat_interface(bot_id: str):
    API_URL = f"{BACKEND_URL}/bots/{bot_id}/chat"

    st.subheader("💬 Chat")

    # Keep chat history per bot
    if f"messages_{bot_id}" not in st.session_state:
        try:
            resp = requests.get(f"{BACKEND_URL}/bots/{bot_id}/chat")
            resp.raise_for_status()
            raw_msgs = resp.json()

            normalized = []
            for m in raw_msgs:
                # 🔄 expand each {user: "...", bot: "..."} into 2 messages
                if "user" in m and "bot" in m:
                    normalized.append({"role": "user", "content": m["user"]})
                    normalized.append({"role": "bot", "content": m["bot"]})
            st.session_state[f"messages_{bot_id}"] = normalized
        except:
            st.session_state[f"messages_{bot_id}"] = []
    
    messages = st.session_state[f"messages_{bot_id}"]

    # --- HTML / CSS container ---
    st.markdown(
        """
        <style>
        .chat-box {
            border: 1px solid #444;
            border-radius: 10px;
            padding: 10px;
            height: 400px;
            overflow-y: auto;
            background-color: #1e1e1e;
            color: white;
        }
        .msg-user {
            text-align: right;
            margin: 5px;
            padding: 8px;
            border-radius: 8px;
            background-color: #0a84ff;
            color: white;
            display: inline-block;
        }
        .msg-bot {
            text-align: left;
            margin: 5px;
            padding: 8px;
            border-radius: 8px;
            background-color: #333;
            color: white;
            display: inline-block;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Render chat history
    chat_html = "<div class='chat-box'>"
    for msg in messages:
        role = msg.get("role")
        content = msg.get("content")

        # 🔄 Handle old format
        if not role and "user" in msg and "bot" in msg:
            chat_html += f"<div class='msg-user'>🧑 {msg['user']}</div><br>"
            chat_html += f"<div class='msg-bot'>🤖 {msg['bot']}</div><br>"
            continue

        if role == "user":
            chat_html += f"<div class='msg-user'>🧑 {content}</div><br>"
        elif role == "bot":
            chat_html += f"<div class='msg-bot'>🤖 {content}</div><br>"
    chat_html += "</div>"
    st.markdown(chat_html, unsafe_allow_html=True)

    # Input box
    new_message = st.text_input("Type your message:", key=f"input_{bot_id}")

    if st.button("Send", key=f"send_{bot_id}"):
        if new_message.strip():
            # Append user msg locally
            messages.append({"role": "user", "content": new_message})
    
            # Send to backend
            try:
                resp = requests.post(API_URL, json={"message": new_message})
                resp.raise_for_status()
                reply = resp.json().get("reply", "⚠️ No reply from bot")
            except Exception as e:
                reply = f"[Error contacting bot] {e}"
    
            # Append bot reply locally
            messages.append({"role": "bot", "content": reply})
    
            # ✅ Save updated chat back to session_state
            st.session_state[f"messages_{bot_id}"] = messages
    
            # ✅ Clear input box safely
            st.session_state.pop(f"input_{bot_id}", None)
            st.rerun()
    

# ---------------- BOT MANAGEMENT ----------------
def bot_management_ui():
    st.subheader("🛠️ Manage Your Bots")
    bots = load_bots()
    if not bots:
        st.info("No bots to manage — create one first.")
        return

    bot_options = {f"{b['name']} ({b['id'][:6]})": b for b in bots}
    selected_label = st.selectbox("Select a bot to manage:", list(bot_options.keys()))
    bot_info = bot_options[selected_label]
    bot_id = bot_info["id"]

    col1, col2, col3, col4 = st.columns([2, 3, 1, 1])

    new_name = col1.text_input("Name", value=bot_info['name'], key=f"name_{bot_id}")
    if col1.button("✏️ Rename", key=f"rename_{bot_id}"):
        rename_bot_api(bot_id, new_name)
        st.success("Renamed!")
        st.experimental_rerun()

    new_persona = col2.text_area("Personality", value=bot_info['personality'], key=f"persona_{bot_id}", height=80)
    if col2.button("✏️ Update", key=f"update_{bot_id}"):
        update_personality_api(bot_id, new_persona)
        st.success("Personality updated!")
        st.experimental_rerun()

    if col3.button("🧹 Clear Chat", key=f"manage_clear_{bot_id}"):
        st.session_state.history = []
        st.success("Chat history cleared!")
        st.experimental_rerun()

    if col4.button("🗑️ Delete", key=f"delete_{bot_id}"):
        delete_bot_api(bot_id)
        st.success("Bot deleted!")
        st.experimental_rerun()

# ---------------- MAIN ----------------
def main():
    tabs = st.tabs(["➕ Create Bot", "🛠️ Manage Bots", "💬 My Bots"])
    
    with tabs[0]:
        create_and_save_bot()
    
    with tabs[1]:
        bot_management_ui()
    
    with tabs[2]:
        st.subheader("💬 My Bots")
        bots = load_bots()
        if not bots:
            st.info("No bots available. Please create one first.")
        else:
            bot_options = {f"{b['name']} ({b['id'][:6]})": b for b in bots}
            selected_label = st.selectbox("Select a bot to chat with:", list(bot_options.keys()))
            bot_info = bot_options[selected_label]
            bot_id = bot_info["id"]

            chat_interface(bot_id)  # ✅ Pass bot_id here

if __name__ == "__main__":
    main()
