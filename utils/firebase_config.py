import os
import json
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

load_dotenv()

service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
service_account_info = json.loads(service_account_json)

cred = credentials.Certificate(service_account_info)
firebase_admin.initialize_app(cred)

db = firestore.client()
