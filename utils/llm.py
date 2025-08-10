import os
import json
import google.generativeai as genai
import streamlit as st

# Load API key from env or Streamlit secrets
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        raise ValueError("Gemini API key not found in environment or Streamlit secrets.")

# Configure Gemini client
genai.configure(api_key=api_key)

# Use one consistent model everywhere
MODEL_NAME = "models/gemini-2.5-pro"
model = genai.GenerativeModel(model_name=MODEL_NAME, generation_config={"temperature": 0.7})

# utils/llm.py

import json
import google.generativeai as genai
import os

def generate_bot_config_gemini(prompt):
    api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Gemini API key not found in env or Streamlit secrets.")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-pro")  # change to your actual model

    try:
        response = model.generate_content(
            f"Respond ONLY with valid JSON config for a bot. Example: {{'name': '...', 'personality': '...'}}.\nUser request: {prompt}"
        )
    except Exception as e:
        raise RuntimeError(f"[Gemini request failed] {e}")

    # --- Unified text extraction ---
    if hasattr(response, "text") and response.text:
        text = response.text.strip()
    elif hasattr(response, "candidates") and response.candidates:
        # Pull text from the first candidate part
        parts = response.candidates[0].content.parts
        text = "".join(getattr(p, "text", "") for p in parts if hasattr(p, "text", ""))
    elif isinstance(response, dict):
        # Sometimes it's a dict — check for 'candidates'
        if "candidates" in response:
            parts = response["candidates"][0]["content"]["parts"]
            text = "".join(p.get("text", "") for p in parts)
        else:
            text = json.dumps(response)
    else:
        raise RuntimeError(f"Gemini returned unexpected format: {type(response)} {response}")

    if not text.strip():
        raise RuntimeError("[Gemini returned empty response]")

    # --- Cleanup markdown wrapping ---
    if text.startswith("```"):
        text = text.strip("` \n")
        if text.lower().startswith("json"):
            text = text[4:].strip()

    return text

def chat_with_gemini(message: str, personality: str) -> str:
    prompt = (
        f"You are a helpful chatbot with this personality:\n"
        f"{personality}\nUser: {message}\nBot:"
    )
    try:
        response = model.generate_content(prompt)
        if not hasattr(response, "text") or not response.text.strip():
            return "[Chat Error] Gemini returned empty response."
        return response.text.strip()
    except Exception as e:
        return f"[Chat Error] {str(e)}"
