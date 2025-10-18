import os
import json
import base64
import requests
import streamlit as st
import firebase_admin
from ui import logo_animation
from firebase_admin import auth as admin_auth, firestore

# ------------------ CONFIG ------------------
FIREBASE_API_KEY = os.environ.get("FIREBASE_API_KEY")
SERVICE_ACCOUNT_JSON_B64 = os.environ.get("SERVICE_ACCOUNT_JSON_B64")

if not FIREBASE_API_KEY or not SERVICE_ACCOUNT_JSON_B64:
    st.error("❌ Set FIREBASE_API_KEY and SERVICE_ACCOUNT_JSON_B64 environment variables.")
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

# ------------------ HELPER FUNCTIONS ------------------
def _rest_post(path: str, payload: dict):
    url = f"{FIREBASE_REST_BASE}/{path}?key={FIREBASE_API_KEY}"
    r = requests.post(url, json=payload)
    r.raise_for_status()
    return r.json()

def rest_sign_in(email: str, password: str):
    return _rest_post("accounts:signInWithPassword", {"email": email, "password": password, "returnSecureToken": True})

def rest_send_password_reset(email: str):
    return _rest_post("accounts:sendOobCode", {"requestType": "PASSWORD_RESET", "email": email})

# ------------------ AUTH OPS ------------------
def signup_user(email: str, password: str, display_name: str):
    """Create Firebase user via Admin SDK and store Firestore profile."""
    try:
        # Try creating the user directly (Firebase will raise if exists)
        user = admin_auth.create_user(
            email=email,
            password=password,
            display_name=display_name
        )
        uid = user.uid

        # Create Firestore profile
        db.collection("users").document(uid).set({
            "displayName": display_name,
            "email": email,
            "createdAt": firestore.SERVER_TIMESTAMP,
            "roles": {"user": True},
        })

        # Generate email verification link
        try:
            verification_link = admin_auth.generate_email_verification_link(email)
        except Exception:
            verification_link = None

        return {
            "uid": uid,
            "email": email,
            "displayName": display_name,
            "verificationLink": verification_link,
            "emailVerified": False
        }

    except firebase_admin._auth_utils.EmailAlreadyExistsError:
        # Handle existing user gracefully
        raise ValueError("User with this email already exists. Please log in instead.")
    except Exception as e:
        raise Exception(f"Signup failed: {e}")

def login_user(email: str, password: str):
    resp = rest_sign_in(email, password)
    id_token = resp["idToken"]
    uid = resp["localId"]
    decoded = admin_auth.verify_id_token(id_token)
    email_verified = decoded.get("email_verified", False)

    doc = db.collection("users").document(uid).get()
    display_name = doc.to_dict().get("displayName") if doc.exists else ""

    return {"uid": uid, "email": email, "displayName": display_name, "emailVerified": email_verified}

def send_password_reset(email: str):
    return rest_send_password_reset(email)

# ------------------ STYLISH STREAMLIT UI ------------------
def auth_ui():
    
    logo_animation()
    
    st.markdown("""
        <style>
        .auth-card input {
            border-radius: 8px !important;
        }
        .auth-title {
            font-size: 2rem;
            font-weight: 600;
            color: #f5f5f5;
            margin-bottom: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)

    if "user" not in st.session_state:
        st.session_state["user"] = None

    if st.session_state["user"]:
        user = st.session_state["user"]
        st.success(f"✅ Signed in as **{user['displayName']}** ({user['email']})")
        if not user.get("emailVerified"):
            st.info("⚠️ Please verify your email before continuing.")
            if user.get("verificationLink"):
                st.markdown(f"[👉 Click here to verify your email]({user['verificationLink']})")
        if st.button("Sign out"):
            st.session_state["user"] = None
            st.rerun()
        return

    st.markdown('<div class="auth-card">', unsafe_allow_html=True)
    st.markdown('<div class="auth-title">🔐 Welcome to Mentesa</div>', unsafe_allow_html=True)

    tab = st.radio("", ["Login", "Sign Up", "OAuth"], horizontal=True)

    if tab == "Login":
        email = st.text_input("📧 Email", key="login_email")
        password = st.text_input("🔑 Password", type="password", key="login_password")

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
        name = st.text_input("👤 Full Name", key="signup_name")
        email = st.text_input("📧 Email", key="signup_email")
        password = st.text_input("🔒 Password", type="password", key="signup_password")

        if st.button("Create Account"):
            try:
                user = signup_user(email, password, name or email.split("@")[0])
                st.session_state["user"] = user
                st.success("✅ Account created successfully! A verification link has been generated below.")
                st.rerun()
            except ValueError as e:
                st.warning(str(e))
            except Exception as e:
                st.error(str(e))
        

    elif tab == "OAuth":
        st.markdown("### 🌐 Login using:")
        st.markdown(
            """
            <a href="https://mentesav4.firebaseapp.com/__/auth/handler?providerId=google.com">
                <button style='background:#DB4437;color:white;padding:10px 20px;border:none;border-radius:8px;margin:5px;'>Login with Google</button>
            </a>
            <a href="https://mentesav4.firebaseapp.com/__/auth/handler?providerId=github.com">
                <button style='background:#333;color:white;padding:10px 20px;border:none;border-radius:8px;margin:5px;'>Login with GitHub</button>
            </a>
            """,
            unsafe_allow_html=True
        )

    st.markdown('</div>', unsafe_allow_html=True)

# ------------------ PROTECTED PAGE HELPER ------------------
def require_login(msg="Please log in to continue"):
    if not st.session_state.get("user"):
        st.warning(msg)
        st.stop()
    return st.session_state["user"]
