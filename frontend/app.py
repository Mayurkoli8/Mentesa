import streamlit as st
import uuid
import json
import sys
import os

# --- DEBUG BLOCK: paste near top of frontend/app.py, after imports ---
# --- MULTI-MODEL DEBUG BLOCK: paste this near the top of frontend/app.py, after imports ---
import os
import streamlit as _st

if _st.sidebar.button("🔎 DEBUG: Multi-model Gemini Test"):
    import google.generativeai as genai
    import time

    key = os.getenv("GEMINI_API_KEY") or _st.secrets.get("GEMINI_API_KEY") or _st.secrets.get("GOOGLE_API_KEY")
    _st.write("Key present in env/secrets:", bool(key))
    if not key:
        _st.error("No GEMINI_API_KEY found.")
        _st.stop()

    genai.configure(api_key=key)

    # shortlist of models to try (from your list). Change or reorder as needed.
    models_to_try = [
        "models/gemini-2.5-pro",
        "models/gemini-1.5-pro",
        "models/gemini-2.5-flash",
        "models/gemini-1.5-flash",
        "models/gemini-1.5-pro-latest"
    ]

    results = []
    for mname in models_to_try:
        _st.write("----")
        _st.write("Trying model:", mname)
        try:
            model = genai.GenerativeModel(mname)
            # very short safe prompt
            resp = model.generate_content("Say hello in one short sentence.")
            _st.write("Response type:", type(resp))
            # safe text access
            text = None
            try:
                if hasattr(resp, "text"):
                    text = resp.text
            except Exception as e:
                _st.write("Accessing resp.text raised:", e)

            # collect candidate parts if available
            cand_dump = []
            for c in getattr(resp, "candidates", []):
                parts = []
                for p in getattr(getattr(c, "content", None), "parts", []):
                    try:
                        parts.append(getattr(p, "text", None))
                    except Exception:
                        parts.append(None)
                cand_dump.append({
                    "finish_reason": getattr(c, "finish_reason", None),
                    "safety": getattr(c, "safety_ratings", None),
                    "parts": parts
                })

            _st.write("resp.text (repr):", repr(text))
            _st.write("Candidates (raw):")
            _st.json(cand_dump)
            results.append((mname, "ok", text, cand_dump))
        except Exception as exc:
            # show full exception
            _st.write("Exception for model:", mname)
            _st.exception(exc)
            results.append((mname, "error", str(exc)))
        # tiny pause to be polite
        time.sleep(0.5)

    _st.write("===== SUMMARY =====")
    _st.json([{"model": r[0], "status": r[1], "text_preview": (r[2][:200] if r[1]=="ok" and r[2] else None)} for r in results])
    _st.stop()
# --- END MULTI-MODEL DEBUG BLOCK ---

# Add root dir (mentesa/) to sys.path so utils/ can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.llm import generate_bot_config_gemini, chat_with_gemini
from utils.bot_ops import load_bots, save_bots, delete_bot, rename_bot, update_personality

from utils.chat_ops import load_chat_history, save_chat_history, clear_chat_history

st.set_page_config(page_title="Mentesa", page_icon="🧠")

import streamlit as st
import json
from utils.llm import generate_bot_config_gemini  # your updated safe function

def create_and_save_bot():
    st.subheader("Create Your Bot")
    prompt = st.text_area("Enter your bot's configuration prompt:")

    if st.button("Generate Bot Config"):
        if not prompt.strip():
            st.warning("Please enter a prompt before generating.")
            return

        with st.spinner("Generating bot configuration..."):
            cfg = generate_bot_config_gemini(prompt)

        # Handle errors or empty responses gracefully
        if isinstance(cfg, dict) and "error" in cfg:
            st.error(f"Failed to generate config: {cfg['error']}")
            return

        if not cfg:
            st.error("Gemini returned no configuration.")
            return

        # Convert to JSON string for saving
        try:
            cfg_str = json.dumps(cfg, indent=2, ensure_ascii=False)
        except Exception as e:
            st.error(f"Error serializing configuration: {e}")
            return

        # Save to file
        try:
            with open("bot_config.json", "w", encoding="utf-8") as f:
                f.write(cfg_str)
            st.success("✅ Bot configuration saved successfully!")
            st.json(cfg)
        except Exception as e:
            st.error(f"Error saving configuration: {e}")

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
