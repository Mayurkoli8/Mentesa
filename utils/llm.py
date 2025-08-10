import os
import json
import google.generativeai as genai
import streamlit as st

# Load API key from env or Streamlit secrets
api_key = os.getenv("GEMINI_API_KEY")
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
        model = genai.GenerativeModel("models/gemini-2.5-pro")
        response = model.generate_content(instruction)

        # --- Handle both normal and streaming responses ---
        if hasattr(response, "text") and response.text:
            text = response.text.strip()
        elif hasattr(response, "candidates") and response.candidates:
            # Some environments don't expose .text
            parts = []
            for c in response.candidates:
                if c.content and c.content.parts:
                    for p in c.content.parts:
                        if hasattr(p, "text") and p.text:
                            parts.append(p.text)
            text = "\n".join(parts).strip()
        else:
            raise RuntimeError("Gemini returned empty response.")

        # --- Remove markdown fences ---
        if text.startswith("```"):
            text = text.strip("` \n")
            if text.lower().startswith("json"):
                text = text[4:].strip()

        # --- Parse JSON ---
        try:
            cfg = json.loads(text)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"[Generation Error] Gemini returned invalid JSON:\n{text}") from e

        # --- Validate ---
        if not isinstance(cfg, dict) or "name" not in cfg or "personality" not in cfg:
            raise RuntimeError(f"[Generation Error] Missing keys in output: {cfg}")

        return cfg

    except Exception as e:
        raise RuntimeError(f"[Generation Error] {e}")

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
