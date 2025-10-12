# auth.py
import os
import requests
import streamlit as st
import firebase_admin
from firebase_admin import auth as admin_auth, firestore
from google.oauth2 import service_account

# ------------------ CONFIG ------------------
FIREBASE_API_KEY = os.environ.get("FIREBASE_API_KEY")
SERVICE_ACCOUNT_JSON_B64 = os.environ.get("SERVICE_ACCOUNT_JSON")

if not FIREBASE_API_KEY or not SERVICE_ACCOUNT_JSON_B64:
    # In production, raise or handle securely; here we show a friendly message.
    st.error("Set FIREBASE_API_KEY and SERVICE_ACCOUNT_JSON environment variables.")
    st.stop()

# Initialize Firebase Admin SDK (idempotent)
if not firebase_admin._apps:
    firebase_admin.initialize_app(firebase_admin.credentials.Certificate(SERVICE_ACCOUNT_JSON))
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

def rest_send_verification_email(id_token: str):
    return _rest_post("accounts:sendOobCode", {"requestType": "VERIFY_EMAIL", "idToken": id_token})

# ------------------ Auth operations ------------------
def signup_user(display_name: str, email: str, password: str):
    """
    Creates a Firebase Auth user via Admin SDK, creates Firestore profile,
    signs in to obtain idToken (so we can send verification email), returns session dict.
    """
    user = admin_auth.create_user(email=email, password=password, display_name=display_name)
    uid = user.uid

    profile = {
        "displayName": display_name,
        "email": email,
        "createdAt": firestore.SERVER_TIMESTAMP,
        "roles": {"user": True},
    }
    db.collection("users").document(uid).set(profile)

    signin = rest_sign_in(email, password)
    id_token = signin["idToken"]
    # send verification email (non-blocking)
    try:
        rest_send_verification_email(id_token)
    except Exception:
        # swallow - verification email may fail sometimes (log in prod)
        pass

    return {"uid": uid, "idToken": id_token, "refreshToken": signin["refreshToken"], "emailVerified": False}

def login_user(email: str, password: str):
    """
    Sign in using REST API and verify token server-side.
    Returns session dict including emailVerified flag.
    """
    resp = rest_sign_in(email, password)
    id_token = resp["idToken"]
    uid = resp["localId"]

    decoded = admin_auth.verify_id_token(id_token)
    return {"uid": uid, "idToken": id_token, "refreshToken": resp["refreshToken"], "emailVerified": decoded.get("email_verified", False)}

def send_password_reset(email: str):
    return rest_send_password_reset(email)

def get_user_profile(uid: str):
    doc = db.collection("users").document(uid).get()
    return doc.to_dict() if doc.exists else None

# ------------------ Streamlit UI helper ------------------
def auth_ui():
    """
    Call this inside your Streamlit app to render a small login/signup UI.
    It will populate st.session_state['user'] upon successful auth.
    """
    if "user" not in st.session_state:
        st.session_state["user"] = None

    st.header("Account")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Login")
        login_email = st.text_input("Email", key="login_email")
        login_password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            try:
                sess = login_user(login_email, login_password)
                st.session_state["user"] = sess
                st.success("Logged in.")
            except requests.HTTPError as e:
                err = e.response.json().get("error", {}).get("message", str(e))
                st.error(f"Login failed: {err}")
            except Exception as e:
                st.error(f"Login error: {e}")

        if st.button("Forgot password?"):
            if login_email:
                try:
                    send_password_reset(login_email)
                    st.info("Password reset email sent (if account exists).")
                except Exception as e:
                    st.error(f"Could not send reset email: {e}")
            else:
                st.info("Enter your email above and press 'Forgot password?'")

    with col2:
        st.subheader("Sign up")
        signup_name = st.text_input("Full name", key="signup_name")
        signup_email = st.text_input("Email", key="signup_email")
        signup_password = st.text_input("Password", type="password", key="signup_password")
        if st.button("Create account"):
            try:
                resp = signup_user(signup_name or signup_email.split("@")[0], signup_email, signup_password)
                st.session_state["user"] = resp
                st.success("Account created. Verification email sent.")
            except requests.HTTPError as e:
                err = e.response.json().get("error", {}).get("message", str(e))
                st.error(f"Signup failed: {err}")
            except Exception as e:
                st.error(f"Signup error: {e}")

    st.markdown("---")
    if st.session_state.get("user"):
        user = st.session_state["user"]
        st.write("Signed in:", {"uid": user["uid"], "emailVerified": user.get("emailVerified")})
        if st.button("Sign out"):
            st.session_state["user"] = None
            st.success("Signed out.")

# ------------------ Small util for gating ------------------
def require_login(redirect_msg="Please sign in to continue."):
    """
    Convenience: check if user is in session_state; if not, show message and stop.
    Use in pages that require authentication.
    """
    if not st.session_state.get("user"):
        st.warning(redirect_msg)
        st.stop()
    return st.session_state["user"]
