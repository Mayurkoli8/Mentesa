# frontend/auth.py
import os
import json
import base64
import logging
import requests
import streamlit as st
import firebase_admin
from firebase_admin import auth as admin_auth, firestore
from ui import logo_animation

logging.basicConfig(level=logging.INFO)

# ---------------- CONFIG ----------------
FIREBASE_API_KEY = (
    (st.secrets.get("FIREBASE_API_KEY") if hasattr(st, "secrets") else None)
    or os.environ.get("FIREBASE_API_KEY")
)
SERVICE_ACCOUNT_JSON_B64 = (
    (st.secrets.get("SERVICE_ACCOUNT_JSON_B64") if hasattr(st, "secrets") else None)
    or os.environ.get("SERVICE_ACCOUNT_JSON_B64")
)

if not FIREBASE_API_KEY or not SERVICE_ACCOUNT_JSON_B64:
    # friendly message for deployment environments if missing
    st.error("❌ Missing Firebase configuration. Set FIREBASE_API_KEY and SERVICE_ACCOUNT_JSON_B64 in secrets or env.")
    st.stop()

# Initialize Firebase Admin (idempotent)
if not firebase_admin._apps:
    try:
        svc_json = base64.b64decode(SERVICE_ACCOUNT_JSON_B64).decode("utf-8")
        svc_info = json.loads(svc_json)
        cred = firebase_admin.credentials.Certificate(svc_info)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Firebase init error: {e}")
        st.stop()

db = firestore.client()
FIREBASE_REST_BASE = "https://identitytoolkit.googleapis.com/v1"

# ---------------- REST helpers ----------------
def _rest_post(path: str, payload: dict, timeout: int = 15):
    url = f"{FIREBASE_REST_BASE}/{path}?key={FIREBASE_API_KEY}"
    r = requests.post(url, json=payload, timeout=timeout)
    r.raise_for_status()
    return r.json()

def rest_sign_in(email: str, password: str):
    return _rest_post("accounts:signInWithPassword", {"email": email, "password": password, "returnSecureToken": True})

def rest_send_password_reset(email: str):
    return _rest_post("accounts:sendOobCode", {"requestType": "PASSWORD_RESET", "email": email})

def rest_send_verification_email_with_token(id_token: str):
    return _rest_post("accounts:sendOobCode", {"requestType": "VERIFY_EMAIL", "idToken": id_token})

# ---------------- Auth operations ----------------
def create_user_profile_if_missing(uid: str, email: str, display_name: str = None, oauth: bool = False):
    """Create Firestore user profile if missing."""
    doc = db.collection("users").document(uid)
    if not doc.get().exists:
        doc.set({
            "displayName": display_name or email.split("@")[0],
            "email": email,
            "createdAt": firestore.SERVER_TIMESTAMP,
            "roles": {"user": True},
            "oauth": oauth
        })

def signup_user(email: str, password: str, display_name: str):
    """
    Create a Firebase Auth user (Admin SDK), create Firestore profile,
    attempt to trigger verification email via REST. Do NOT auto-sign-in the user.
    Returns: {"email":..., "verificationLink": optional_admin_link}
    """
    try:
        # ensure no pre-existing account
        try:
            admin_auth.get_user_by_email(email)
            raise ValueError("User with this email already exists. Please log in instead.")
        except admin_auth.UserNotFoundError:
            pass

        user = admin_auth.create_user(email=email, password=password, display_name=display_name)
        uid = user.uid

        create_user_profile_if_missing(uid, email, display_name, oauth=False)

        # Try REST sign-in to obtain idToken, which allows asking Firebase to send verification email
        try:
            signin = rest_sign_in(email, password)
            id_token = signin.get("idToken")
            if id_token:
                try:
                    rest_send_verification_email_with_token(id_token)
                except Exception as e:
                    logging.warning("REST verification email send failed: %s", e)
            else:
                logging.warning("No idToken after sign-in; cannot request verification via REST.")
        except Exception as e:
            logging.warning("REST sign-in after signup failed: %s", e)

        # Admin SDK fallback verification link (useful for dev/debug)
        try:
            verification_link = admin_auth.generate_email_verification_link(email)
        except Exception:
            verification_link = None

        return {"email": email, "verificationLink": verification_link}

    except ValueError:
        raise
    except Exception as e:
        logging.exception("Signup failed")
        raise Exception(f"Signup failed: {e}")

def login_user(email: str, password: str):
    """
    Attempt REST sign-in. If user is not email-verified, return unverified status and id_token to allow resending.
    If verified, return the session-like dict.
    """
    try:
        resp = rest_sign_in(email, password)
    except requests.HTTPError as e:
        # prefer firebase's error message
        try:
            err = e.response.json()
            msg = err.get("error", {}).get("message", str(e))
        except Exception:
            msg = str(e)
        raise requests.HTTPError(msg)

    id_token = resp.get("idToken")
    uid = resp.get("localId")

    try:
        user_record = admin_auth.get_user(uid)
        email_verified = bool(user_record.email_verified)
        display_name = user_record.display_name or email.split("@")[0]
    except Exception:
        logging.exception("Could not fetch Admin user record during login_user")
        email_verified = False
        display_name = email.split("@")[0]

    if not email_verified:
        # try to resend verification
        try:
            if id_token:
                rest_send_verification_email_with_token(id_token)
        except Exception as e:
            logging.warning("Could not send verification email on login: %s", e)

        return {
            "status": "unverified",
            "email": email,
            "id_token": id_token,
            "displayName": display_name
        }

    # verified
    return {
        "uid": uid,
        "email": email,
        "displayName": display_name,
        "emailVerified": True
    }

def send_password_reset(email: str):
    return rest_send_password_reset(email)

# ---------------- Streamlit UI ----------------
def auth_ui():
    """
    Email-only auth UI (no OAuth). Blocks access until st.session_state['user'] is present and verified.
    """

    logo_animation()

    # Simple accessible styles & card
    st.markdown("""
    <style>
    .auth-card {
        max-width:720px;
        margin:18px auto;
        padding:20px;
        border-radius:12px;
        background: linear-gradient(180deg,#071126,#0f1724);
        color:#e6eef8;
        box-shadow: 0 8px 24px rgba(2,6,23,0.6);
    }
    .auth-title { font-size:1.6rem; font-weight:700; margin-bottom:6px; color:#f0f7ff; }
    .auth-sub { color:#9fb0d6; margin-bottom:14px; }
    .small-muted { color:#9fb0d6; font-size:0.95rem; }
    .btn-row { display:flex; gap:8px; }
    </style>
    """, unsafe_allow_html=True)

    # session keys
    if "user" not in st.session_state:
        cookies["user_email"] = email
        cookies["user_uid"] = uid
        cookies.save()
        st.session_state["user"] = {"email": email, "uid": uid}
        st.rerun()

    if "pending_unverified" not in st.session_state:
        st.session_state["pending_unverified"] = None

    # If already signed-in (and verified)
    if st.session_state.get("user"):
        u = st.session_state["user"]
        st.success(f"✅ Signed in as **{u.get('displayName')}** ({u.get('email')})")
        if st.button("Sign out"):
            st.session_state["user"] = None
            st.rerun()
        return

    # If pending unverified (user tried login but hasn't verified yet)
    pending = st.session_state.get("pending_unverified")
    if pending:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        st.markdown(f"<div class='auth-title'>🔔 Please verify your email</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='auth-sub'>We sent a verification email to <b>{pending['email']}</b>. Check your inbox and spam folder.</div>", unsafe_allow_html=True)

        col1, col2 = st.columns([1,1])
        with col1:
            if st.button("📧 Resend verification email"):
                idt = pending.get("id_token")
                if idt:
                    try:
                        rest_send_verification_email_with_token(idt)
                        st.success("✅ Verification email resent. Check your inbox.")
                    except Exception as e:
                        st.error(f"Could not resend verification email: {e}")
                else:
                    st.error("No id_token available to resend. Please try 'Login' again to regenerate.")
        with col2:
            if st.button("✅ I clicked verification link — check now"):
                try:
                    rec = admin_auth.get_user_by_email(pending["email"])
                    if rec.email_verified:
                        st.session_state["user"] = {
                            "uid": rec.uid,
                            "email": rec.email,
                            "displayName": rec.display_name or pending.get("displayName", rec.email.split("@")[0]),
                            "emailVerified": True
                        }
                        st.session_state["pending_unverified"] = None
                        st.success("✅ Email verified — signed in!")
                        st.rerun()
                    else:
                        st.warning("Email still not verified. Make sure you clicked the link in your inbox.")
                except Exception as e:
                    st.error(f"Could not check verification status: {e}")

        st.markdown("</div>", unsafe_allow_html=True)
        return

    # --- Main card for Login / Signup (no OAuth) ---
    # st.markdown('<div class="auth-card">', unsafe_allow_html=True)
    st.markdown('<div class="auth-title">🔐 Welcome to Mentesa</div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-sub">Create an account or sign in with your email to continue.</div>', unsafe_allow_html=True)

    # Use an explicit label for accessibility (Streamlit warns when label is empty)
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
                    try:
                        resp = login_user(email, password)
                        if resp.get("status") == "unverified":
                            st.session_state["pending_unverified"] = {
                                "email": resp["email"],
                                "id_token": resp.get("id_token"),
                                "displayName": resp.get("displayName")
                            }
                            st.warning("Your email is not verified. A verification email was sent. Check your inbox.")
                            st.rerun()
                        else:
                            st.session_state["user"] = resp
                            st.success("✅ Logged in successfully.")
                            st.rerun()
                    except requests.HTTPError as e:
                        st.error(f"Login failed: {e}")
                    except Exception as e:
                        st.error(f"Login error: {e}")

        with col2:
            if st.button("Forgot password?"):
                if email:
                    try:
                        send_password_reset(email)
                        st.info("Password reset email sent (check spam).")
                    except Exception as e:
                        st.error(f"Could not send reset email: {e}")
                else:
                    st.info("Enter your email above and press 'Forgot password?'")

    elif action == "Sign Up":
        name = st.text_input("Full name", key="signup_name", placeholder="Jane Doe")
        email = st.text_input("Email", key="signup_email", placeholder="you@example.com")
        password = st.text_input("Password", key="signup_password", type="password", placeholder="Choose a strong password")
        if st.button("Create Account"):
            if not email or not password:
                st.warning("Please provide both email and password.")
            else:
                try:
                    result = signup_user(email, password, name or email.split("@")[0])
                    st.success("✅ Account created. A verification email was sent to your inbox (check spam).")
                    if result.get("verificationLink"):
                        st.info("Development fallback verification link (click only if email doesn't arrive):")
                        st.markdown(f"[Verify (admin link)]({result['verificationLink']})")
                    st.info("After verification, come back and log in.")
                except ValueError as e:
                    st.warning(str(e))
                except requests.HTTPError as e:
                    st.error(f"Signup failed: {e}")
                except Exception as e:
                    st.error(f"Signup error: {e}")

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- Protected helper ----------------
def require_login(msg="Please log in to continue"):
    if not st.session_state.get("user"):
        st.warning(msg)
        st.stop()
    return st.session_state["user"]
