import os
import json
import google.generativeai as genai
import streamlit as st

# Load API key
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        raise ValueError("Gemini API key not found in environment or Streamlit secrets.")

# Configure Gemini client
genai.configure(api_key=api_key)

MODEL_NAME = "models/gemini-2.5-pro"
model = genai.GenerativeModel(model_name=MODEL_NAME, generation_config={"temperature": 0.7})

def generate_bot_config_gemini(prompt):
    instruction = f"""
    You are to output ONLY a valid JSON object.
    No explanations, no markdown formatting, no extra text.
    JSON format:
    {{
      "name": "string",
      "personality": "string",
      "settings": {{}}
    }}
    Now generate JSON for: {prompt}
    """

    try:
        response = model.generate_content(instruction)

        # Extract text from response
        try:
            text = response.text
        except ValueError:
            # If direct text access fails, try to get it from parts
            try:
                parts = []
                for part in response.parts:
                    if hasattr(part, "text"):
                        parts.append(part.text)
                text = " ".join(parts).strip()
                if not text:
                    raise RuntimeError("No text found in response parts")
            except Exception as e:
                raise RuntimeError(f"Failed to extract text from response: {str(e)}")
        
        if not text:
            raise RuntimeError("Gemini returned empty response.")

        # Remove markdown fences
        if text.startswith("```"):
            text = text.strip("` \n")
            if text.lower().startswith("json"):
                text = text[4:].strip()

        # Parse JSON
        try:
            cfg = json.loads(text)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"[Generation Error] Gemini returned invalid JSON:\n{text}") from e

        # Validate JSON
        if not isinstance(cfg, dict) or "name" not in cfg or "personality" not in cfg:
            raise RuntimeError(f"[Generation Error] Missing keys in output: {cfg}")

        return cfg

    except Exception as e:
        raise RuntimeError(f"[Generation Error] {e}")

import requests
import os

# Example function to chat with Gemini
def chat_with_gemini(user_message, personality, api_key=None):
    """
    Sends a message to Gemini and returns the bot's reply.

    Args:
        user_message (str): The message from the user.
        personality (str): Personality description of the bot.
        api_key (str, optional): API key for authentication if required.

    Returns:
        str: Bot's response.
    """
    # Replace this URL with your Gemini API endpoint
    GEMINI_API_URL = "https://api.gemini.ai/generate"

    headers = {
        "Content-Type": "application/json",
    }

    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload = {
        "prompt": f"Personality: {personality}\nUser: {user_message}\nBot:",
        "max_tokens": 200
    }

    try:
        response = requests.post(GEMINI_API_URL, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        # Adjust the key depending on Gemini response format
        return data.get("text", "🤖 Sorry, I didn't understand that.")
    except Exception as e:
        print("Error in chat_with_gemini:", e)
        return "🤖 Sorry, I couldn't generate a response."
