import requests
import os

FIREBASE_API_KEY = os.environ.get("FIREBASE_API_KEY")

data = {
    "email": "newtest123@example.com",
    "password": "test1234",
    "returnSecureToken": True
}

r = requests.post(
    f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}",
    json=data
)

print(r.status_code, r.json())
