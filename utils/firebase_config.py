import os
import json
import base64
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# Only try to import Streamlit if available
try:
    import streamlit as st
    USE_STREAMLIT = True
except ImportError:
    USE_STREAMLIT = False

service_account_info = None

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

# Try Streamlit secrets only if running inside Streamlit
if USE_STREAMLIT:
    try:
        service_account_json = st.secrets.get("SERVICE_ACCOUNT_JSON")
        if service_account_json:
            service_account_info = json.loads(service_account_json)
    except Exception:
        print("Warning: Invalid or missing Streamlit secrets, will fallback to local .env")

# Fallback to local .env (base64 encoded JSON string)
if not service_account_info:
    encoded = os.getenv("SERVICE_ACCOUNT_JSON_B64")
    if not encoded:
        raise ValueError("SERVICE_ACCOUNT_JSON_B64 not found in .env")
    decoded_str = base64.b64decode(encoded).decode("utf-8")
    service_account_info = json.loads(decoded_str)

# Initialize Firebase if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate(service_account_info)
    firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()

print("Firebase initialized successfully")
