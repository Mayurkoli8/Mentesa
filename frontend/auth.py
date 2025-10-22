# frontend/auth.py
import os
import json
import logging
import requests
import streamlit as st
import firebase_admin
from firebase_admin import auth as admin_auth, firestore
from ui import logo_animation
from cookies import ensure_ready

logging.basicConfig(level=logging.INFO)

cookies = ensure_ready()

# FIREBASE REST helpers (frontend uses admin for user checks, but login itself goes to backend)
FIREBASE_REST_BASE = "https://identitytoolkit.googleapis.com/v1"
FIREBASE_API_KEY = (st.secrets.get("FIREBASE_API_KEY") if hasattr(st, "secrets") else os.environ.get("FIREBASE_API_KEY"))

if not FIREBASE_API_KEY:
    # We still allow auth flow that calls backend, but warn if missing.
    logging.warning("FIREBASE_API_KEY not set in frontend environment (expected on backend)")

# Initialize Firebase Admin in frontend as before (used for some verification)
SERVICE_ACCOUNT_JSON_B64 = (st.secrets.get("SERVICE_ACCOUNT_JSON_B64") if hasattr(st, "secrets") else os.environ.get("SERVICE_ACCOUNT_JSON_B64"))
if not SERVICE_ACCOUNT_JSON_B64:
    st.error("Missing SERVICE_ACCOUNT_JSON_B64 in secrets or env.")
    st.stop()

if not firebase_admin._apps:
    try:
        import base64, json as _json
        svc_json = base64.b64decode(SERVICE_ACCOUNT_JSON_B64).decode("utf-8")
        svc_info = _json.loads(svc_json)
        cred = firebase_admin.credentials.Certificate(svc_info)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Firebase init error: {e}")
        st.stop()

db = firestore.client()

# Backend URL (where we added /auth endpoints)
BACKEND = os.environ.get("BACKEND", "https://mentesav8.onrender.com")


# Restore from cookies if session_id present and no session in st.session_state
def try_restore_from_cookies():
    if st.session_state.get("user"):
        return
    sid = cookies.get("session_id")
    if not sid:
        return
    try:
        r = requests.get(f"{BACKEND}/auth/session", params={"session_id": sid}, timeout=8)
        if r.status_code == 200:
            data = r.json()
            st.session_state["user"] = data.get("user")
        else:
            # invalid/expired session -> cleanup cookie
            try:
                cookies.delete("session_id")
                cookies.save()
            except Exception:
                pass
    except Exception:
        # Could not contact backend; do nothing — user remains not-signed-in
        pass

try_restore_from_cookies()


# ---------------- Auth UI ----------------
def auth_ui():
    logo_animation()

    st.markdown("""
    <style>
    .auth-card { max-width:720px; margin:18px auto; padding:20px; border-radius:12px;
                background: linear-gradient(180deg,#071126,#0f1724); color:#e6eef8; }
    .auth-title { font-size:1.6rem; font-weight:700; margin-bottom:6px; color:#f0f7ff; }
    .auth-sub { color:#9fb0d6; margin-bottom:14px; }
    </style>
    """, unsafe_allow_html=True)

    # already signed in?
    if st.session_state.get("user"):
        u = st.session_state["user"]
        st.success(f"✅ Signed in as **{u.get('displayName')}** ({u.get('email')})")
        if st.button("Sign out"):
            sid = cookies.get("session_id")
            if sid:
                try:
                    requests.post(f"{BACKEND}/auth/logout", json={"session_id": sid}, timeout=6)
                except Exception:
                    pass
            st.session_state["user"] = None
            try:
                cookies.delete("session_id")
                cookies.delete("user_email")
                cookies.delete("user_displayName")
                cookies.save()
            except Exception:
                pass
            st.rerun()
        return

    st.markdown('<div class="auth-title">🔐 Welcome to Mentesa</div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-sub">Create an account or sign in with your email to continue.</div>', unsafe_allow_html=True)

    action = st.radio("Choose action", ["Login", "Sign Up"], horizontal=True)

    if action == "Login":
        email = st.text_input("Email", key="login_email", placeholder="you@example.com")
        password = st.text_input("Password", key="login_password", type="password", placeholder="At least 8 characters")
        col1, col2 = st.columns([1,1])
        with col1:
            if st.button("Login"):
                if not email or not password:
                    st.warning("Please enter both email and password.")
                else:
                    # call our backend login endpoint
                    try:
                        r = requests.post(f"{BACKEND}/auth/login", json={"email": email, "password": password}, timeout=10)
                        if r.status_code == 200:
                            data = r.json()
                            sid = data.get("session_id")
                            user = data.get("user")  # {uid,email,displayName}
                            if sid and user:
                                st.session_state["user"] = user
                                # persist cookie for browser so reloads restore session
                                try:
                                    cookies["session_id"] = sid
                                    cookies["user_email"] = user.get("email")
                                    cookies["user_displayName"] = user.get("displayName")
                                    cookies.save()
                                except Exception:
                                    pass
                                st.success("✅ Logged in successfully.")
                                st.rerun()
                            else:
                                st.error("Invalid login response from server.")
                        else:
                            try:
                                err = r.json().get("detail") or r.text
                            except Exception:
                                err = r.text
                            st.error(f"Login failed: {err}")
                    except Exception as e:
                        st.error(f"Login error: {e}")

        with col2:
            if st.button("Forgot password?"):
                if email:
                    try:
                        # use REST for password reset
                        _r = _rest_post("accounts:sendOobCode", {"requestType": "PASSWORD_RESET", "email": email})
                        st.info("Password reset email sent (check spam).")
                    except Exception as e:
                        st.error(f"Could not send reset email: {e}")
                else:
                    st.info("Enter your email above and press 'Forgot password?'")

    else:  # Sign Up
        name = st.text_input("Full name", key="signup_name", placeholder="Jane Doe")
        email = st.text_input("Email", key="signup_email", placeholder="you@example.com")
        password = st.text_input("Password", key="signup_password", type="password", placeholder="Choose a strong password")
        if st.button("Create Account"):
            if not email or not password:
                st.warning("Please provide both email and password.")
            else:
                # Create via Admin SDK (same as before)
                try:
                    # ensure no pre-existing account
                    try:
                        admin_auth.get_user_by_email(email)
                        st.warning("User already exists — please log in.")
                    except admin_auth.UserNotFoundError:
                        user = admin_auth.create_user(email=email, password=password, display_name=name or email.split("@")[0])
                        create_user_profile_if_missing(user.uid, email, name or email.split("@")[0], oauth=False)
                        # try to send verification via REST sign-in
                        try:
                            signin = _rest_post("accounts:signInWithPassword", {"email": email, "password": password, "returnSecureToken": True})
                            id_token = signin.get("idToken")
                            if id_token:
                                _rest_post("accounts:sendOobCode", {"requestType": "VERIFY_EMAIL", "idToken": id_token})
                        except Exception:
                            pass
                        st.success("✅ Account created. Verification email sent. Please verify then login.")
                except Exception as e:
                    st.error(f"Signup error: {e}")

# helper used above (simple copy of the REST wrapper)
def _rest_post(path: str, payload: dict, timeout: int = 10):
    if not FIREBASE_API_KEY:
        raise RuntimeError("FIREBASE_API_KEY not set in frontend env")
    url = f"{FIREBASE_REST_BASE}/{path}?key={FIREBASE_API_KEY}"
    rr = requests.post(url, json=payload, timeout=timeout)
    rr.raise_for_status()
    return rr.json()


# protected helper for pages
def require_login(msg="Please log in to continue"):
    if not st.session_state.get("user"):
        st.warning(msg)
        st.stop()
    return st.session_state["user"]
