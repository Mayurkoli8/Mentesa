# utils/llm.py
# utils/llm.py
import requests

MISTRAL_URL = "http://localhost:11434/api/generate"

def generate_bot_config_mistral(prompt: str) -> str:
    instructions = """
You are a JSON generator. Based on the user’s request, return *only* a valid JSON object, matching exactly this schema:

{
  "name": string,
  "personality": {
    "role": string,
    "traits": [ string, ... ],    
    "communication_style": [ string, ... ]
  }
}

* Use double quotes for all keys and strings.  
* Do NOT include any extra fields or comments.  
* Do NOT wrap in markdown or code fences.  
* Return nothing but the JSON.  
"""

    payload = {
        "model": "mistral",
        "prompt": f"{instructions}\nUser request: {prompt}\nJSON:",
        "stream": False
    }
    r = requests.post(MISTRAL_URL, json=payload)
    r.raise_for_status()
    return r.json()["response"]


def chat_with_mistral(message: str, personality: str):
    try:
        url = "http://localhost:11434/api/generate"
        prompt = f"You are a helpful chatbot with this personality: {personality}\nUser: {message}\nBot:"
        payload = {
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json().get("response", "...")
    except Exception as e:
        return f"[Chat Error] {str(e)}"
