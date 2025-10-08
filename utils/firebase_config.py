import firebase_admin
from firebase_admin import credentials, firestore
import os, json, base64
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

# Decode service account
encoded = os.getenv("SERVICE_ACCOUNT_JSON_B64")
if not encoded:
    raise ValueError("SERVICE_ACCOUNT_JSON_B64 not found in .env")

decoded_str = base64.b64decode(encoded).decode("utf-8")
service_account_info = json.loads(decoded_str)

# Initialize Firebase Admin
if not firebase_admin._apps:
    cred = credentials.Certificate(service_account_info)
    firebase_admin.initialize_app(cred)

# ✅ Always use firebase_admin.firestore
from firebase_admin import firestore as admin_firestore
db = admin_firestore.client()

print("Firestore client type:", type(db))
