import os
import json
import google.generativeai as genai
import streamlit as st

# Load API key
api_key = st.secrets["GEMINI_API_KEY"]
if not api_key:
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
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

def chat_with_gemini(message: str, personality: str) -> str:
    """
    Generate a chatbot reply using Gemini.

    Args:
        message (str): The user's message.
        personality (str): Bot's personality description.

    Returns:
        str: Bot's reply.
    """
    prompt = (
        f"You are a helpful chatbot with this personality:\n"
        f"{personality}\nUser: {message}\nBot:"
    )
    try:
        response = model.generate_content(prompt)

        # Extract text from response
        try:
            text = response.text
            if text:
                return text.strip()
        except AttributeError:
            # fallback: check response.parts
            parts = []
            for part in getattr(response, "parts", []):
                if hasattr(part, "text"):
                    parts.append(part.text)
            text = " ".join(parts).strip()
            if text:
                return text
                
        return "[Chat Error] Failed to get response from Gemini"

    except Exception as e:
        return f"[Chat Error] {str(e)}"