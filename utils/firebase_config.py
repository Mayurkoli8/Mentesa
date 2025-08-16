import json
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st

# Load JSON from Streamlit secrets
service_account_info = json.loads(st.secrets["FIREBASE"]["SERVICE_ACCOUNT_JSON"])

cred = credentials.Certificate(service_account_info)
firebase_admin.initialize_app(cred)

db = firestore.client()
