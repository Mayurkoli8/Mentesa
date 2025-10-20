# frontend/auth_oauth.py
import os
import urllib.parse
import streamlit as st

"""
Small frontend helper that renders OAuth buttons which redirect to your backend.
Backend endpoints expected:
  GET {BACKEND_BASE}/oauth/google?redirect_uri={STREAMLIT_HOST}
  GET {BACKEND_BASE}/oauth/github?redirect_uri={STREAMLIT_HOST}

The backend will perform the provider exchange and then redirect back to:
  {STREAMLIT_HOST}?idToken=<FIREBASE_ID_TOKEN>
Your app (app.py) already reads idToken and signs the user into session.
"""

BACKEND_BASE = (st.secrets.get("BACKEND_BASE") if hasattr(st, "secrets") else None) or os.environ.get("BACKEND_BASE")
STREAMLIT_HOST = (st.secrets.get("STREAMLIT_HOST") if hasattr(st, "secrets") else None) or os.environ.get("STREAMLIT_HOST") or "http://localhost:8501"

def oauth_buttons():
    if not BACKEND_BASE:
        st.info("OAuth is not configured. Set BACKEND_BASE in secrets.toml or environment.")
        return

    redirect_uri_encoded = urllib.parse.quote_plus(STREAMLIT_HOST)
    google_url = f"{BACKEND_BASE}/oauth/google?redirect_uri={redirect_uri_encoded}"
    github_url = f"{BACKEND_BASE}/oauth/github?redirect_uri={redirect_uri_encoded}"

    st.markdown("### 🌐 Sign in with Google or GitHub")
    st.markdown(
        f"""
        <div style="display:flex;gap:12px;">
          <a href="{google_url}" target="_self">
            <button style="background:#DB4437;color:white;padding:10px 18px;border-radius:8px;border:none;">
              Login with Google
            </button>
          </a>
          <a href="{github_url}" target="_self">
            <button style="background:#333;color:white;padding:10px 18px;border-radius:8px;border:none;">
              Login with GitHub
            </button>
          </a>
        </div>
        """,
        unsafe_allow_html=True,
    )
