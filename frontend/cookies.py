# frontend/cookies.py
import os
from streamlit_cookies_manager import EncryptedCookieManager

# Password should be set from env in production; fallback for local dev
COOKIE_PASSWORD = os.environ.get("MENTESA_COOKIE_PASSWORD", "super_secret_key")

# Single instance (do NOT re-create this elsewhere)
cookies = EncryptedCookieManager(prefix="mentesa_", password=COOKIE_PASSWORD)

def ensure_ready():
    """
    Call early (from app.py) and again from auth.py if needed.
    This will st.stop() until the cookie manager is ready.
    """
    import streamlit as st
    if not cookies.ready():
        st.stop()
    return cookies
