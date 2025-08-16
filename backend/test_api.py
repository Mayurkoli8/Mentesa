import requests

url = "http://127.0.0.1:8000/chat"
payload = {
    "bot_id": "897c4e2e-f14f-4277-8d79-a0c5a666b32b",   # <-- replace with real bot_id
    "message": "Hello! How are you?"
}

resp = requests.post(url, json=payload)

print("Status Code:", resp.status_code)
print("Raw Response:", resp.text)   # 👈 this will show what server actually returned

try:
    print("As JSON:", resp.json())
except Exception as e:
    print("JSON Decode Error:", e)
