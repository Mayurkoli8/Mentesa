import streamlit as st
import uuid
import json
import sys
import os


# Add root dir (mentesa/) to sys.path so utils/ can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.llm import generate_bot_config_gemini, chat_with_gemini
from utils.bot_ops import load_bots, save_bots, delete_bot, rename_bot, update_personality

from utils.chat_ops import load_chat_history, save_chat_history, clear_chat_history

st.set_page_config(page_title="Mentesa", page_icon="🧠")


def create_and_save_bot():
    """Section 1: Describe & create a new bot via LLM."""
    st.header("🪄 Describe & Create Your Bot")
    prompt = st.text_input("What should your bot do?", key="bot_prompt")
    if st.button("Create & Chat", key="create_chat"):
        if not prompt.strip():
            st.error("Please enter a description.")
            return None, None

        with st.spinner("Generating bot…"):
            cfg_text = generate_bot_config_gemini(prompt)

        try:
            clean = cfg_text.strip().strip("` ")
            cfg = json.loads(clean)
            name = cfg["name"]
            personality = cfg["personality"]
        except json.JSONDecodeError as e:
            st.error("🚨 Invalid JSON from model:")
            st.code(cfg_text, language="json")
            st.error(f"Error: {e}")
            st.stop()

        bots = load_bots()
        bot_id = str(uuid.uuid4())
        bots[bot_id] = {"name": name, "personality": personality}
        save_bots(bots)
        st.success(f"✅ Bot '{name}' created!")
        st.rerun()

    return None, None  # No new bot created this run


def chat_interface():
    """Section 2: Select, chat, clear history, or delete a bot."""
    
    st.markdown("---")
    st.header("💬 Chat with Your Bot")
    bots = load_bots()
    if not bots:
        st.info("No bots available—create one above.")
        return

    bot_items = list(bots.items())
    bot_id, bot_info = st.selectbox(
        "Choose a bot",
        options=bot_items,
        format_func=lambda x: f"{x[1]['name']} ({x[0][:6]})",
        key="chat_select"
    )



    st.markdown(f"**Personality:** {bot_info['personality']}")

    # Render chat history as bubbles
    history = load_chat_history(bot_id)
    for turn in history:
        st.chat_message("user").markdown(turn["user"])
        st.chat_message("assistant", avatar="🤖").markdown(turn["bot"])

    # Input box
    user_input = st.chat_input("Your message…")
    if user_input:
        st.chat_message("user").markdown(user_input)
        with st.spinner("Thinking…"):
            reply = chat_with_gemini(user_input, bot_info["personality"])
        st.chat_message("assistant", avatar="🤖").markdown(reply)

        # Save and rerun
        history.append({"user": user_input, "bot": reply})
        save_chat_history(bot_id, history)
        st.rerun()


def bot_management_ui():
    st.subheader("🤖 Manage Your Bots")

    bots = load_bots()
    if not bots:
        st.info("No bots to manage—create one first.")
        return

    # Create dropdown list
    bot_options = {f"{info['name']} ({bot_id[:6]})": bot_id for bot_id, info in bots.items()}
    selected_label = st.selectbox("Select a bot to manage:", list(bot_options.keys()))
    selected_bot_id = bot_options[selected_label]
    selected_bot_info = bots[selected_bot_id]

    col1, col2, col3, col4 = st.columns([2, 3, 1, 1])

    # Rename
    new_name = col1.text_input("Name", value=selected_bot_info['name'], key=f"name_{selected_bot_id}")
    if col1.button("✏️ Rename", key=f"rename_{selected_bot_id}"):
        from utils.bot_ops import rename_bot
        rename_bot(selected_bot_id, new_name)
        st.success("Renamed!")
        st.rerun()

    # Edit Personality
    new_persona = col2.text_area(
        "Personality", value=selected_bot_info['personality'],
        key=f"persona_{selected_bot_id}", height=80
    )
    if col2.button("✏️ Update", key=f"update_{selected_bot_id}"):
        from utils.bot_ops import update_personality
        update_personality(selected_bot_id, new_persona)
        st.success("Personality updated!")
        st.rerun()

    # Clear Chat
    if col3.button("🧹 Clear Chat", key=f"manage_clear_{selected_bot_id}"):
        from utils.chat_ops import clear_chat_history
        clear_chat_history(selected_bot_id)
        st.success("Chat history cleared!")
        st.rerun()

    # Delete Bot
    if col4.button("🗑️ Delete", key=f"delete_{selected_bot_id}"):
        from utils.bot_ops import delete_bot
        delete_bot(selected_bot_id)
        st.success("Bot deleted!")
        st.rerun()



def main():
    st.set_page_config(page_title="Mentesa", page_icon="🧠", layout="centered")

    st.title("🤖 Mentesa")

    tabs = st.tabs(["➕ Create Bot", "🛠️ Manage Bots", "💬 My Bots"])

    with tabs[0]:
        create_and_save_bot()

    with tabs[1]:
        bot_management_ui()

    with tabs[2]:
        chat_interface()

if __name__ == "__main__":
    main()
