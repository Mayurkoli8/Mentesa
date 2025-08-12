import os
from utils import bot_ops
import google.generativeai as genai

# --- Gemini API Setup ---
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-pro"  # You can change to "gemini-1.5-pro" if needed

def chat_with_bot(bot_id, user_message):
    """
    Generate a bot reply using its personality and Gemini Pro.
    """
    # Load bot details
    bot = bot_ops.get_bot(bot_id)
    if not bot:
        return "❌ Bot not found."

    personality = bot.get("personality", "You are a helpful AI assistant.")
    
    # Prepare prompt
    prompt = f"""
    You are {bot['name']}.
    Personality: {personality}

    The user says: {user_message}
    Respond in character.
    """

    try:
        response = genai.GenerativeModel(MODEL_NAME).generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"⚠️ Error generating response: {e}"
