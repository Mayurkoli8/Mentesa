# auth.py
import os
import streamlit as st
import requests
import firebase_admin
from firebase_admin import auth as admin_auth, firestore
import json, base64

# ------------------ CONFIG ------------------
FIREBASE_API_KEY = os.environ.get("FIREBASE_API_KEY")
SERVICE_ACCOUNT_JSON_B64 = os.environ.get("SERVICE_ACCOUNT_JSON_B64")

if not FIREBASE_API_KEY or not SERVICE_ACCOUNT_JSON_B64:
    st.error("Set FIREBASE_API_KEY and SERVICE_ACCOUNT_JSON_B64 environment variables.")
    st.stop()

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    try:
        service_account_json = base64.b64decode(SERVICE_ACCOUNT_JSON_B64).decode("utf-8")
        service_account_info = json.loads(service_account_json)
        cred = firebase_admin.credentials.Certificate(service_account_info)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Firebase init error: {e}")
        st.stop()

db = firestore.client()
FIREBASE_REST_BASE = "https://identitytoolkit.googleapis.com/v1"

# ------------------ Helper functions ------------------
def _rest_post(path: str, payload: dict):
    url = f"{FIREBASE_REST_BASE}/{path}?key={FIREBASE_API_KEY}"
    r = requests.post(url, json=payload)
    r.raise_for_status()
    return r.json()

def rest_sign_in(email: str, password: str):
    return _rest_post("accounts:signInWithPassword", {"email": email, "password": password, "returnSecureToken": True})

def rest_send_password_reset(email: str):
    return _rest_post("accounts:sendOobCode", {"requestType": "PASSWORD_RESET", "email": email})

# ------------------ Auth operations ------------------
def signup_user(email: str, password: str, display_name: str):
    """Create Firebase user, Firestore profile, generate verification link"""
    user = admin_auth.create_user(email=email, password=password, display_name=display_name)
    uid = user.uid

    db.collection("users").document(uid).set({
        "displayName": display_name,
        "email": email,
        "createdAt": firestore.SERVER_TIMESTAMP,
        "roles": {"user": True},
    })

    # Generate verification link
    verification_link = admin_auth.generate_email_verification_link(email)

    return {"uid": uid, "email": email, "displayName": display_name, "verificationLink": verification_link, "emailVerified": False}

def login_user(email: str, password: str):
    """Sign in via REST API and check emailVerified"""
    resp = rest_sign_in(email, password)
    id_token = resp["idToken"]
    uid = resp["localId"]
    decoded = admin_auth.verify_id_token(id_token)
    email_verified = decoded.get("email_verified", False)

    profile = db.collection("users").document(uid).get()
    display_name = profile.to_dict().get("displayName") if profile.exists else ""

    return {"uid": uid, "email": email, "displayName": display_name, "emailVerified": email_verified}

def send_password_reset(email: str):
    return rest_send_password_reset(email)

# ------------------ Streamlit UI ------------------
def auth_ui():
    if "user" not in st.session_state:
        st.session_state["user"] = None

    st.title("🚀 Mentesa Login")

    if st.session_state["user"]:
        user = st.session_state["user"]
        st.success(f"Signed in as {user['displayName']} ({user['email']})")
        if not user.get("emailVerified"):
            st.info("⚠️ Email not verified. Click the link below after signup:")
            if user.get("verificationLink"):
                st.markdown(f"[Verify Email]({user['verificationLink']})")
        if st.button("Sign out"):
            st.session_state["user"] = None
            st.rerun()
        return  # skip login/signup UI if logged in

    # Tabs for Login / Signup / OAuth
    tab = st.radio("Choose an option:", ["Login", "Sign Up", "OAuth"])

    if tab == "Login":
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            try:
                user = login_user(email, password)
                st.session_state["user"] = user
                st.rerun()
            except requests.HTTPError as e:
                err = e.response.json().get("error", {}).get("message", str(e))
                st.error(f"Login failed: {err}")
            except Exception as e:
                st.error(f"Login error: {e}")
        if st.button("Forgot password?"):
            if email:
                try:
                    send_password_reset(email)
                    st.info("Password reset email sent!")
                except Exception as e:
                    st.error(f"Reset failed: {e}")
            else:
                st.info("Enter email first.")

    elif tab == "Sign Up":
        name = st.text_input("Full Name", key="signup_name")
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_password")
        if st.button("Create Account"):
            try:
                user = signup_user(email, password, name or email.split("@")[0])
                st.session_state["user"] = user
                st.rerun()
            except Exception as e:
                st.error(f"Signup error: {e}")

    elif tab == "OAuth":
        st.markdown("### Login with:")
        # Google / GitHub buttons using Firebase hosted OAuth links
        st.markdown("[Login with Google](https://your-firebase-app.web.app/__/auth/handler?providerId=google.com)")
        st.markdown("[Login with GitHub](https://your-firebase-app.web.app/__/auth/handler?providerId=github.com)")

# ------------------ Gating ------------------
def require_login(redirect_msg="Please log in to continue"):
    if not st.session_state.get("user"):
        st.warning(redirect_msg)
        st.stop()
    return st.session_state["user"]
