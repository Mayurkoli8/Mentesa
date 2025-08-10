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

def generate_bot_config_gemini(prompt):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("❌ GEMINI_API_KEY not set in environment!")
        st.stop()

    genai.configure(api_key=api_key)

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

        # Show full raw response in Streamlit so we can see the error cause
        st.write("### DEBUG: Raw Gemini response", response)

        if hasattr(response, "text") and response.text:
            text = response.text.strip()
        else:
            parts = []
            for c in getattr(response, "candidates", []):
                if getattr(c, "content", None) and getattr(c.content, "parts", None):
                    for p in c.content.parts:
                        if getattr(p, "text", None):
                            parts.append(p.text)
            text = "\n".join(parts).strip()

        if not text:
            st.error("❌ Gemini returned empty text.")
            st.stop()

        if text.startswith("```"):
            text = text.strip("` \n")
            if text.lower().startswith("json"):
                text = text[4:].strip()

        cfg = json.loads(text)

        if not isinstance(cfg, dict) or "name" not in cfg or "personality" not in cfg:
            st.error(f"❌ Missing keys in output: {cfg}")
            st.stop()

        return cfg

    except Exception as e:
        st.error(f"🚨 Generation Error: {e}")
        st.stop()
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
