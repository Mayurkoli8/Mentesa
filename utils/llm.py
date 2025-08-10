import os
import json
import google.generativeai as genai

# Load API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    try:
        import streamlit as st
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        raise ValueError("Gemini API key not found in environment or Streamlit secrets.")

genai.configure(api_key=api_key)

# ✅ DON'T use api_version — this causes the error
model = genai.GenerativeModel(
    model_name="gemini-pro-1.5-pro",
    generation_config={"temperature": 0.7}
)

def generate_bot_config_gemini(prompt: str) -> dict:
    instruction = (
        "Generate a valid JSON object based on this one-line description:\n"
        f"{prompt}\n\n"
        "The JSON should strictly follow this format:\n"
        "{\n"
        '  "name": string,\n'
        '  "personality": {\n'
        '    "role": string,\n'
        '    "traits": [ string, ... ],\n'
        '    "communication_style": [ string, ... ]\n'
        "  }\n"
        "}\n"
        "Only return the JSON, no explanation."
    )
    try:
        response = model.generate_content(instruction)
        return json.loads(response.text)
    except Exception as e:
        raise RuntimeError(f"[Generation Error] {e}")

def chat_with_gemini(message: str, personality: str) -> str:
    prompt = (
        f"You are a helpful chatbot with this personality:\n"
        f"{personality}\nUser: {message}\nBot:"
    )
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"[Chat Error] {str(e)}"
