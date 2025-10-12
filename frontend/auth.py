# auth.py
import os
import json
import base64
import requests
import streamlit as st
import firebase_admin
from firebase_admin import auth as admin_auth, firestore
import tempfile

# ------------------ CONFIG ------------------
FIREBASE_API_KEY = os.environ.get("FIREBASE_API_KEY")
SERVICE_ACCOUNT_JSON_B64 = os.environ.get("SERVICE_ACCOUNT_JSON_B64")
FIREBASE_AUTH_DOMAIN = os.environ.get("FIREBASE_AUTH_DOMAIN")  # e.g. your-project-id.firebaseapp.com
FIREBASE_PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID")
FIREBASE_APP_ID = os.environ.get("FIREBASE_APP_ID")  # optional but useful for FirebaseUI
# NOTE: For the embedded FirebaseUI to work, you should set FIREBASE_AUTH_DOMAIN and FIREBASE_PROJECT_ID (and optionally FIREBASE_APP_ID).

if not FIREBASE_API_KEY or not SERVICE_ACCOUNT_JSON_B64:
    st.error("Set FIREBASE_API_KEY and SERVICE_ACCOUNT_JSON_B64 environment variables.")
    st.stop()

# ------------------ Init Firebase Admin (from base64 service account) ------------------
try:
    service_account_json = base64.b64decode(SERVICE_ACCOUNT_JSON_B64).decode("utf-8")
    service_account_info = json.loads(service_account_json)
except Exception as e:
    st.error(f"Invalid SERVICE_ACCOUNT_JSON_B64: {e}")
    st.stop()

if not firebase_admin._apps:
    cred = firebase_admin.credentials.Certificate(service_account_info)
    firebase_admin.initialize_app(cred)
db = firestore.client()

FIREBASE_REST_BASE = "https://identitytoolkit.googleapis.com/v1"

# ------------------ Helper functions ------------------
def _rest_post(path: str, payload: dict):
    url = f"{FIREBASE_REST_BASE}/{path}?key={FIREBASE_API_KEY}"
    r = requests.post(url, json=payload)
    # if error, raise with message
    try:
        r.raise_for_status()
    except requests.HTTPError as e:
        # include firebase message if present
        try:
            err_json = r.json()
            raise requests.HTTPError(json.dumps(err_json), response=r)
        except Exception:
            raise e
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
    signs in via REST to obtain idToken (so we can send verification email), returns session dict.
    Also generates and returns an admin-generated verification link (so we can display it during dev).
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

    # sign in to obtain idToken using REST (so the client can also use REST flows)
    signin = rest_sign_in(email, password)
    id_token = signin["idToken"]

    # send verification email via REST (best-effort)
    try:
        rest_send_verification_email(id_token)
    except Exception:
        # ignore failure here (we'll also generate a link for dev/manual sending)
        pass

    # admin-generated verification link (useful for dev or to send via SendGrid)
    try:
        verification_link = admin_auth.generate_email_verification_link(email)
    except Exception:
        verification_link = None

    return {
        "uid": uid,
        "idToken": id_token,
        "refreshToken": signin.get("refreshToken"),
        "emailVerified": False,
        "verification_link": verification_link,
    }

def login_user(email: str, password: str):
    """
    Sign in using REST API and verify token server-side.
    Returns session dict including emailVerified flag.
    """
    resp = rest_sign_in(email, password)
    id_token = resp["idToken"]
    uid = resp["localId"]

    decoded = admin_auth.verify_id_token(id_token)
    return {"uid": uid, "idToken": id_token, "refreshToken": resp.get("refreshToken"), "emailVerified": decoded.get("email_verified", False)}

def login_with_id_token(id_token: str):
    """
    Given an idToken (from client JS firebase SDK), verify it server-side and create session dict.
    """
    decoded = admin_auth.verify_id_token(id_token)
    uid = decoded["uid"]
    # optional: fetch profile
    profile = get_user_profile(uid)
    return {"uid": uid, "idToken": id_token, "refreshToken": None, "emailVerified": decoded.get("email_verified", False), "profile": profile}

def send_password_reset(email: str):
    return rest_send_password_reset(email)

def get_user_profile(uid: str):
    doc = db.collection("users").document(uid).get()
    return doc.to_dict() if doc.exists else None

def generate_verification_link(email: str):
    """
    Generate an email verification link via Admin SDK (useful for sending via your email service).
    """
    return admin_auth.generate_email_verification_link(email)

# ------------------ Streamlit UI helper ------------------
def _render_firebaseui_widget():
    """
    Returns a block of HTML+JS that renders FirebaseUI inside Streamlit.
    The widget will show Google, GitHub and Email sign-in options and will place the idToken into a textarea (#idtoken).
    The user can then copy that token and paste it into the Streamlit 'Paste idToken' field to complete login server-side.
    """
    if not FIREBASE_AUTH_DOMAIN or not FIREBASE_PROJECT_ID:
        return "<p style='color:orange'>Set FIREBASE_AUTH_DOMAIN and FIREBASE_PROJECT_ID to enable embedded FirebaseUI.</p>"

    firebase_config = {
        "apiKey": FIREBASE_API_KEY,
        "authDomain": FIREBASE_AUTH_DOMAIN,
        "projectId": FIREBASE_PROJECT_ID,
    }
    if FIREBASE_APP_ID:
        firebase_config["appId"] = FIREBASE_APP_ID

    # Use firebase compat (works nicely in simple embedded pages) and firebaseui CDN
    html = f"""
    <div>
      <div id="firebaseui-auth-container"></div>
      <div style="margin-top:10px">
        <label><strong>After sign-in, copy the ID token from below and paste into the Streamlit field:</strong></label><br/>
        <textarea id="idtoken" rows="4" style="width:100%" readonly placeholder="Your idToken will appear here after login"></textarea>
      </div>
      <script src="https://www.gstatic.com/firebasejs/9.22.2/firebase-app-compat.js"></script>
      <script src="https://www.gstatic.com/firebasejs/9.22.2/firebase-auth-compat.js"></script>
      <link type="text/css" rel="stylesheet" href="https://cdn.firebase.com/libs/firebaseui/4.8.0/firebaseui.css" />
      <script src="https://cdn.firebase.com/libs/firebaseui/4.8.0/firebaseui.js"></script>
      <script>
        // init firebase
        const firebaseConfig = {json.dumps(firebase_config)};
        firebase.initializeApp(firebaseConfig);

        // Configure FirebaseUI.
        const uiConfig = {{
          callbacks: {{
            signInSuccessWithAuthResult: function(authResult, redirectUrl) {{
              // Get idToken and show in textarea (no redirect)
              firebase.auth().currentUser.getIdToken().then(function(token) {{
                document.getElementById('idtoken').value = token;
              }});
              return false; // don't redirect
            }}
          }},
          signInFlow: 'popup',
          signInOptions: [
            firebase.auth.GoogleAuthProvider.PROVIDER_ID,
            firebase.auth.GithubAuthProvider.PROVIDER_ID,
            firebase.auth.EmailAuthProvider.PROVIDER_ID
          ],
          // You can set a custom signInSuccessUrl if you want
        }};

        // The start method will wait until the DOM is loaded.
        const ui = new firebaseui.auth.AuthUI(firebase.auth());
        ui.start('#firebaseui-auth-container', uiConfig);
      </script>
    </div>
    """
    return html

def auth_ui():
    """
    Call this inside your Streamlit app to render login/signup UI.
    Populates st.session_state['user'] on success.
    """
    if "user" not in st.session_state:
        st.session_state["user"] = None

    st.header("Account")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Login (email)")
        login_email = st.text_input("Email", key="login_email")
        login_password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            try:
                sess = login_user(login_email, login_password)
                st.session_state["user"] = sess
                st.success("Logged in.")
            except requests.HTTPError as e:
                try:
                    err = json.loads(str(e.args[0]))
                    msg = err.get("error", {}).get("message", str(err))
                except Exception:
                    msg = str(e)
                st.error(f"Login failed: {msg}")
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

        st.markdown("---")
        st.subheader("Paste idToken (from embedded FirebaseUI)")
        pasted_token = st.text_input("Paste idToken here", key="pasted_idtoken")
        if st.button("Use idToken"):
            if pasted_token:
                try:
                    sess = login_with_id_token(pasted_token)
                    st.session_state["user"] = sess
                    st.success("Logged in with idToken.")
                except Exception as e:
                    st.error(f"Invalid idToken: {e}")
            else:
                st.info("Paste the idToken from the embedded UI above first.")

    with col2:
        st.subheader("Sign up (email)")
        signup_name = st.text_input("Full name", key="signup_name")
        signup_email = st.text_input("Email", key="signup_email")
        signup_password = st.text_input("Password", type="password", key="signup_password")
        if st.button("Create account"):
            try:
                resp = signup_user(signup_name or signup_email.split("@")[0], signup_email, signup_password)
                st.session_state["user"] = resp
                st.success("Account created.")
                if resp.get("verification_link"):
                    st.info("Email verification link (dev):")
                    st.code(resp["verification_link"])
                    st.caption("Use this link to verify the email (dev/testing). In production, send this link via email provider.")
            except requests.HTTPError as e:
                try:
                    err = json.loads(str(e.args[0]))
                    msg = err.get("error", {}).get("message", str(err))
                except Exception:
                    msg = str(e)
                st.error(f"Signup failed: {msg}")
            except Exception as e:
                st.error(f"Signup error: {e}")

        st.markdown("**Or sign in with**")
        st.info("Use Google or GitHub below (browser-based). After sign-in copy the idToken shown and paste it on the left to complete server-side login.")

        # embed FirebaseUI (client-side) so buttons appear
        from streamlit.components.v1 import html as st_html
        st_html(_render_firebaseui_widget(), height=420)

    st.markdown("---")
    if st.session_state.get("user"):
        user = st.session_state["user"]
        st.write("Signed in:", {"uid": user["uid"], "emailVerified": user.get("emailVerified")})
        if not user.get("emailVerified"):
            if st.button("Generate verification link (dev)"):
                try:
                    # try to generate via admin SDK (dev usage)
                    # need email: try to fetch from profile or decode token
                    uid = user["uid"]
                    profile = get_user_profile(uid)
                    email = profile.get("email") if profile else None
                    if email:
                        link = generate_verification_link(email)
                        st.code(link)
                        st.caption("Developer verification link displayed above. Send via email provider in prod.")
                    else:
                        st.warning("No email found in profile to generate link for.")
                except Exception as e:
                    st.error(f"Could not generate link: {e}")

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
