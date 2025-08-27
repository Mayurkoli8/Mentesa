import streamlit as st
import requests
import firebase_admin
from firebase_admin import credentials, firestore
import os

# --- BACKEND URL ---
BACKEND = "http://localhost:8000"

# --- FIREBASE INIT (for chat history only) ---
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccount.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

# --- UI HELPERS ---
def create_and_save_bot():
    st.header("🤖 Create a New Bot")

    name = st.text_input("Bot Name")
    personality = st.text_area("Bot Personality / Description")
    system_prompt = st.text_area("System Prompt (optional)")
    api_key = st.text_input("Gemini API Key (required)", type="password")

    if st.button("Create Bot"):
        if not api_key or not name:
            st.error("❌ Name and API key are required")
            return

        # Send to backend
        payload = {
            "name": name,
            "personality": personality,
            "config": {"system_prompt": system_prompt, "api_key": api_key},
        }
        try:
            res = requests.post(f"{BACKEND}/bots", json=payload)
            if res.status_code == 200:
                data = res.json()
                st.success(f"✅ Bot '{name}' created!")
                st.code(data["api_key"], language="text")
                st.caption(f"🔒 Masked Key: {data['api_key_masked']}")
            else:
                st.error(f"❌ Backend error: {res.text}")
        except Exception as e:
            st.error(f"⚠️ Request failed: {e}")


def chat_interface():
    st.header("💬 Chat with a Bot")

    # Fetch bots from backend
    try:
        bots_res = requests.get(f"{BACKEND}/bots").json()
        bots = bots_res.get("bots", [])
    except Exception as e:
        st.error(f"⚠️ Could not load bots: {e}")
        return

    if not bots:
        st.warning("No bots available. Create one first.")
        return

    bot_options = {bot["name"]: bot["id"] for bot in bots}
    selected_bot_name = st.selectbox("Choose a Bot", list(bot_options.keys()))
    selected_bot_id = bot_options[selected_bot_name]

    # Chat history in Firebase
    chat_ref = db.collection("chats").document(selected_bot_id)
    chat_doc = chat_ref.get()
    history = chat_doc.to_dict().get("messages", []) if chat_doc.exists else []

    # Display history
    for msg in history:
        role = "🧑 You" if msg["role"] == "user" else "🤖 Bot"
        st.write(f"**{role}:** {msg['content']}")

    # Input
    user_msg = st.text_input("Type your message...")
    if st.button("Send") and user_msg.strip():
        # Append user message
        history.append({"role": "user", "content": user_msg})

        try:
            res = requests.post(f"{BACKEND}/chat", json={"bot_id": selected_bot_id, "message": user_msg})
            if res.status_code == 200:
                bot_reply = res.json()["reply"]
                history.append({"role": "assistant", "content": bot_reply})
            else:
                st.error(f"❌ Chat error: {res.text}")
                return
        except Exception as e:
            st.error(f"⚠️ Request failed: {e}")
            return

        # Save updated history
        chat_ref.set({"messages": history})
        st.rerun()


def bot_management_ui():
    st.header("🛠 Manage Bots")

    # Load from backend
    try:
        bots_res = requests.get(f"{BACKEND}/bots").json()
        bots = bots_res.get("bots", [])
    except Exception as e:
        st.error(f"⚠️ Could not load bots: {e}")
        return

    if not bots:
        st.info("No bots created yet.")
        return

    for bot in bots:
        with st.expander(f"🤖 {bot['name']}"):
            st.write(f"**Personality:** {bot.get('personality', '')}")
            st.json(bot.get("config", {}))

            if st.button(f"❌ Delete {bot['name']}", key=bot["id"]):
                try:
                    res = requests.delete(f"{BACKEND}/bots/{bot['id']}")
                    if res.status_code == 200:
                        st.success(f"Bot '{bot['name']}' deleted.")
                        st.rerun()
                    else:
                        st.error(f"❌ Delete failed: {res.text}")
                except Exception as e:
                    st.error(f"⚠️ Request failed: {e}")


# --- MAIN APP ---
st.sidebar.title("Mentesa v2")
page = st.sidebar.radio("Go to", ["Create", "Chat", "Manage"])

if page == "Create":
    create_and_save_bot()
elif page == "Chat":
    chat_interface()
elif page == "Manage":
    bot_management_ui()
