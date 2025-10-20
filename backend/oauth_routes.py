# backend/oauth_routes.py  (FastAPI)
import os
import requests
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import RedirectResponse

app = FastAPI()

FIREBASE_API_KEY = os.environ["FIREBASE_API_KEY"]
BACKEND_HOST = os.environ.get("BACKEND_HOST", "http://localhost:8000")  # your backend base
STREAMLIT_URL = os.environ.get("STREAMLIT_URL", "http://localhost:8501")

# Google config
GOOGLE_CLIENT_ID = os.environ["GOOGLE_CLIENT_ID"]
GOOGLE_CLIENT_SECRET = os.environ["GOOGLE_CLIENT_SECRET"]
GOOGLE_REDIRECT_URI = f"{BACKEND_HOST}/oauth/google/callback"

# GitHub config
GITHUB_CLIENT_ID = os.environ["GITHUB_CLIENT_ID"]
GITHUB_CLIENT_SECRET = os.environ["GITHUB_CLIENT_SECRET"]
GITHUB_REDIRECT_URI = f"{BACKEND_HOST}/oauth/github/callback"

# Helper to call Firebase signInWithIdp
def firebase_signin_with_idp(post_body, request_uri):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp?key={FIREBASE_API_KEY}"
    payload = {
        "postBody": post_body,
        "requestUri": request_uri,
        "returnSecureToken": True,
    }
    r = requests.post(url, json=payload, timeout=15)
    r.raise_for_status()
    return r.json()

@app.get("/oauth/google")
def oauth_google_start(redirect_uri: str):
    # redirect client to Google auth
    auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        "?response_type=code"
        f"&client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={GOOGLE_REDIRECT_URI}"
        "&scope=openid%20email%20profile"
        "&access_type=offline"
        "&prompt=select_account"
    )
    # we keep redirect_uri param so later we know where to send idToken
    return RedirectResponse(url=auth_url + f"&state={requests.utils.quote(redirect_uri)}")

@app.get("/oauth/google/callback")
def oauth_google_callback(request: Request, code: str = None, state: str = None):
    if not code:
        raise HTTPException(status_code=400, detail="Missing code")
    # exchange code for tokens
    token_resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        },
        timeout=15,
    )
    token_resp.raise_for_status()
    tok = token_resp.json()
    id_token = tok.get("id_token")
    access_token = tok.get("access_token")

    # Build postBody for Firebase signInWithIdp
    post_body = f"id_token={id_token}&providerId=google.com"
    # requestUri must be a valid url and should match the one used in your Firebase console allowed domains
    request_uri = state or STREAMLIT_URL

    firebase_resp = firebase_signin_with_idp(post_body, request_uri)
    firebase_id_token = firebase_resp.get("idToken")
    if not firebase_id_token:
        raise HTTPException(status_code=500, detail="Firebase did not return idToken")

    # redirect to Streamlit app with idToken
    redirect_target = f"{request_uri}?idToken={firebase_id_token}"
    return RedirectResponse(url=redirect_target)

@app.get("/oauth/github")
def oauth_github_start(redirect_uri: str):
    auth_url = (
        "https://github.com/login/oauth/authorize"
        f"?client_id={GITHUB_CLIENT_ID}"
        f"&redirect_uri={GITHUB_REDIRECT_URI}"
        "&scope=read:user%20user:email"
    )
    return RedirectResponse(url=auth_url + f"&state={requests.utils.quote(redirect_uri)}")

@app.get("/oauth/github/callback")
def oauth_github_callback(request: Request, code: str = None, state: str = None):
    if not code:
        raise HTTPException(status_code=400, detail="Missing code")
    # exchange code for access_token
    token_resp = requests.post(
        "https://github.com/login/oauth/access_token",
        headers={"Accept": "application/json"},
        data={
            "client_id": GITHUB_CLIENT_ID,
            "client_secret": GITHUB_CLIENT_SECRET,
            "code": code,
            "redirect_uri": GITHUB_REDIRECT_URI,
        },
        timeout=15,
    )
    token_resp.raise_for_status()
    tok = token_resp.json()
    access_token = tok.get("access_token")
    if not access_token:
        raise HTTPException(status_code=500, detail="No access_token from GitHub")

    # postBody for Firebase signInWithIdp (GitHub uses access_token)
    post_body = f"access_token={access_token}&providerId=github.com"
    request_uri = state or STREAMLIT_URL

    firebase_resp = firebase_signin_with_idp(post_body, request_uri)
    firebase_id_token = firebase_resp.get("idToken")
    if not firebase_id_token:
        raise HTTPException(status_code=500, detail="Firebase did not return idToken")

    redirect_target = f"{request_uri}?idToken={firebase_id_token}"
    return RedirectResponse(url=redirect_target)
