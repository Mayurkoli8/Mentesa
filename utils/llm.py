import os
import json
import google.generativeai as genai

# Load API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("Gemini API key not found in environment variables.")

# Configure Gemini client
genai.configure(api_key=api_key)

# Default model
MODEL_NAME = "models/gemini-2.5-pro"
model = genai.GenerativeModel(model_name=MODEL_NAME, generation_config={"temperature": 0.7})

# ---------------- Bot Config Generation ----------------
def generate_bot_config(prompt: str) -> dict:
    """
    Generate a bot configuration (name, personality, settings) using Gemini.
    """
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
        text = getattr(response, "text", None)

        # If direct text extraction fails, try parts
        if not text:
            parts = [part.text for part in getattr(response, "parts", []) if hasattr(part, "text")]
            text = " ".join(parts).strip()

        if not text:
            raise RuntimeError("Gemini returned empty response.")

        # Remove markdown/code fences
        if text.startswith("```"):
            text = text.strip("` \n")
            if text.lower().startswith("json"):
                text = text[4:].strip()

        cfg = json.loads(text)

        # Basic validation
        if not isinstance(cfg, dict) or "name" not in cfg or "personality" not in cfg:
            raise RuntimeError(f"Missing required keys in output: {cfg}")

        return cfg

    except Exception as e:
        raise RuntimeError(f"[Generation Error] {e}")

# ---------------- Chat ----------------
# ---------------- Chat ----------------
def chat_with_llm(bot_config: dict, message: str, history: list = None) -> str:
    """
    Chat with Gemini using a bot's personality + chat history.
    """
    if history is None:
        history = []

    # System prompt = bot personality
    system_prompt = f"You are {bot_config['name']}, a chatbot with this personality:\n{bot_config.get('personality', 'helpful')}.\nAlways stay in character."

    # Build conversation for Gemini
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)  # history = [{"role": "user", "content": ...}, {"role": "bot", "content": ...}]
    messages.append({"role": "user", "content": message})

    # Convert to plain text input since Gemini may not support role dicts directly
    formatted_input = []
    for msg in messages:
        if msg["role"] == "system":
            formatted_input.append(f"[System]\n{msg['content']}\n")
        elif msg["role"] == "user":
            formatted_input.append(f"User: {msg['content']}\n")
        else:
            formatted_input.append(f"{bot_config['name']}: {msg['content']}\n")

    try:
        response = model.generate_content("".join(formatted_input))
        text = getattr(response, "text", None)

        if not text:
            parts = [part.text for part in getattr(response, "parts", []) if hasattr(part, "text")]
            text = " ".join(parts).strip()

        return text.strip() if text else "[Chat Error] Empty response"

    except Exception as e:
        return f"[Chat Error] {str(e)}"
