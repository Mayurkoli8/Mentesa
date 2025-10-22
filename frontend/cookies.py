# frontend/cookies.py
import os
from streamlit_cookies_manager import EncryptedCookieManager

# DO NOT pass a `key=` arg here. Create a single global instance.
COOKIE_SECRET = os.environ.get("COOKIE_SECRET", "super_secret_key_change_me")
cookies = EncryptedCookieManager(prefix="mentesa_", password=COOKIE_SECRET)

def ensure_ready():
    import streamlit as st
    if not cookies.ready():
        st.stop()
    return cookies
