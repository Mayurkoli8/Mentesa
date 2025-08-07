import requests

# — Replace with your newly created Gemini API key —
API_KEY = "PASTE_YOUR_GEMINI_API_KEY_HERE"

# — Pick a model you saw in your list —
MODEL = "gemini-2.5-pro"

# — Use the v1beta endpoint now —
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateText"

payload = {
    "prompt": {
        "text": "Say hello like a pirate."
    },
    "temperature": 0.7,
    "maxOutputTokens": 64
}

resp = requests.post(URL, params={"key": API_KEY}, json=payload)

print("Status code:", resp.status_code)
print(resp.text)
