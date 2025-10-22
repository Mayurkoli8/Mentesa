# cookies.py
from streamlit_cookies_manager import EncryptedCookieManager

# Create exactly ONE EncryptedCookieManager instance for the whole app.
# Do not instantiate this class anywhere else.
cookies = EncryptedCookieManager(prefix="mentesa_", password="super_secret_key")

def ensure_ready():
    """
    Return the shared cookies object. This function avoids permanently blocking the UI.
    The cookie manager component mounts asynchronously; sometimes `cookies.ready()` returns
    False for one run. We *don't* call st.stop() here because that can make the screen
    appear blank for users. Instead we return the cookies object unconditionally.
    Client code should tolerate cookies not having values yet.
    """
    # keep this import local so this file can be imported without side effects in tests
    import streamlit as st
    # If you want an explicit short message while cookies mount, uncomment the line below:
    # if not cookies.ready(): st.info("Restoring session…")
    return cookies
