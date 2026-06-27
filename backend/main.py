# backend/main.py
from __future__ import annotations
import os
import sys
import io
import uuid
import secrets
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

# Ensure repo root is importable (so `backend.*` and `utils.*` resolve
# whether launched as `backend.main:app` or `main:app`).
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, Header, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

import requests as _requests
import docx
from PyPDF2 import PdfReader
from firebase_admin import auth as admin_auth, firestore as fa_firestore

from utils.firebase_config import db
from utils.scraper import scrape_website

from backend import config, llm_provider, rag, billing, payment_service, ratelimit

# -------------------------------------------------
# Init
# -------------------------------------------------
app = FastAPI(title="Mentesa Final")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_path = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# -------------------------------------------------
# Bot cache (mirror of Firestore `bots` collection)
# -------------------------------------------------
bots: List[Dict[str, Any]] = []


def load_bots():
    global bots
    bots = []
    for doc in db.collection("bots").stream():
        data = doc.to_dict()
        data["id"] = doc.id
        bots.append(data)


def _bot_from_doc(doc) -> Optional[Dict[str, Any]]:
    if not doc.exists:
        return None
    data = doc.to_dict() or {}
    data["id"] = doc.id
    return data


def refresh_bot_in_cache(bot: Dict[str, Any]):
    """Keep the in-memory cache in sync with a freshly loaded bot."""
    global bots
    bots = [b for b in bots if b.get("id") != bot.get("id")]
    bots.append(bot)


def save_bot(bot: Dict[str, Any]):
    bot_id = bot.get("id") or str(uuid.uuid4())
    bot["id"] = bot_id
    db.collection("bots").document(bot_id).set(bot)


load_bots()

# -------------------------------------------------
# Models
# -------------------------------------------------
class BotCreate(BaseModel):
    owner_email: Optional[str] = None
    name: Optional[str] = None
    personality: Optional[str] = ""
    prompt: Optional[str] = None
    url: Optional[str] = None
    config: Dict[str, Any] = Field(default_factory=dict)
    files: Optional[List[Dict[str, str]]] = Field(default_factory=list)


class BotPublic(BaseModel):
    id: str
    name: str
    personality: Optional[str] = ""
    config: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[str] = None
    file_data: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    widget: Optional[Dict[str, Any]] = None


class ChatRequest(BaseModel):
    message: str
    bot_id: Optional[str] = None
    history: Optional[List[Dict[str, str]]] = Field(default_factory=list)
    session_id: Optional[str] = None  # widget conversation id for server-side memory


class BotUpdate(BaseModel):
    name: Optional[str] = None
    personality: Optional[str] = None


class UrlAdd(BaseModel):
    url: str


class WidgetConfigUpdate(BaseModel):
    accent: Optional[str] = None          # hex color, e.g. "#00d9d9"
    welcome: Optional[str] = None         # greeting message
    title: Optional[str] = None           # header title (defaults to bot name)
    position: Optional[str] = None        # "right" | "left"
    launcher_icon: Optional[str] = None   # emoji or short text for the toggle button


DEFAULT_WIDGET = {
    "accent": "#00d9d9",
    "welcome": "Hi! 👋 How can I help you today?",
    "title": "",
    "position": "right",
    "launcher_icon": "💬",
}


def get_widget_config(bot: Dict[str, Any]) -> Dict[str, Any]:
    cfg = dict(DEFAULT_WIDGET)
    saved = (bot.get("widget") or {})
    for k, v in saved.items():
        if v:
            cfg[k] = v
    if not cfg["title"]:
        cfg["title"] = bot.get("name", "Mentesa Bot")
    return cfg


# -------------------------------------------------
# Helpers
# -------------------------------------------------
API_KEY_PREFIX = "mentesa_sk_"


def generate_api_key() -> str:
    return API_KEY_PREFIX + secrets.token_urlsafe(32)


def mask_key(k: Optional[str]) -> str:
    return f"{k[:12]}...{k[-4:]}" if k else ""


def sanitize_public(bot: Dict[str, Any]) -> Dict[str, Any]:
    b = dict(bot)
    b.pop("api_key", None)
    b.pop("chunks", None)        # don't ship embeddings to the client
    b.pop("scraped_text", None)  # heavy raw text, not needed by UI
    b.pop("scraped_texts", None)
    # Trim file_data to metadata only (UI shows names, not full text).
    if b.get("file_data"):
        b["file_data"] = [{"id": f.get("id"), "name": f.get("name")} for f in b["file_data"]]
    return b


def find_bot_by_id(bid: str) -> Optional[Dict[str, Any]]:
    cached = next((b for b in bots if b.get("id") == bid), None)
    if cached:
        return cached
    # Cache miss (e.g. bot created on another instance/device) -> read Firestore.
    bot = _bot_from_doc(db.collection("bots").document(bid).get())
    if bot:
        refresh_bot_in_cache(bot)
    return bot


def find_bot_by_api_key(key: str) -> Optional[Dict[str, Any]]:
    cached = next((b for b in bots if b.get("api_key") == key), None)
    if cached:
        return cached
    docs = list(db.collection("bots").where("api_key", "==", key).limit(1).stream())
    if docs:
        bot = _bot_from_doc(docs[0])
        if bot:
            refresh_bot_in_cache(bot)
            return bot
    return None


def extract_file_text(filename: str, content: bytes) -> str:
    name = filename.lower()
    if name.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(content))
        return "\n".join((p.extract_text() or "") for p in reader.pages)
    if name.endswith(".docx"):
        d = docx.Document(io.BytesIO(content))
        return "\n".join(p.text for p in d.paragraphs)
    if name.endswith(".txt"):
        return content.decode("utf-8", errors="replace")
    raise HTTPException(400, "Unsupported file type. Use PDF, DOCX, or TXT.")


def rebuild_bot_index(bot: Dict[str, Any]) -> None:
    """Recompute RAG chunks for a bot from its scraped URLs + uploaded files."""
    sources: List[Dict[str, str]] = []
    # Per-URL scraped text (new model).
    for url, text in (bot.get("scraped_texts") or {}).items():
        if text and text != "-":
            sources.append({"name": url, "text": text})
    # Legacy single scraped_text blob (older bots) — include if no map exists.
    if not bot.get("scraped_texts") and bot.get("scraped_text"):
        sources.append({"name": "website", "text": bot["scraped_text"]})
    for f in bot.get("file_data", []) or []:
        if f.get("text") and f["text"] != "-":
            sources.append({"name": f.get("name", "file"), "text": f["text"]})
    bot["chunks"] = rag.build_chunks(sources)


# -------------------------------------------------
# Sessions (Firestore-backed)
# -------------------------------------------------
FIREBASE_REST_BASE = "https://identitytoolkit.googleapis.com/v1"


def _rest_post(path: str, payload: dict, timeout: int = 10):
    if not config.FIREBASE_API_KEY:
        raise RuntimeError("FIREBASE_API_KEY is not set in backend env")
    url = f"{FIREBASE_REST_BASE}/{path}?key={config.FIREBASE_API_KEY}"
    r = _requests.post(url, json=payload, timeout=timeout)
    r.raise_for_status()
    return r.json()


def create_session(uid: str, email: str, display_name: str) -> str:
    sid = str(uuid.uuid4())
    expires = (datetime.utcnow() + timedelta(days=config.SESSION_TTL_DAYS)).isoformat()
    db.collection("sessions").document(sid).set({
        "uid": uid,
        "email": email,
        "displayName": display_name,
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": expires,
    })
    return sid


def get_session(sid: str) -> Optional[Dict[str, Any]]:
    if not sid:
        return None
    doc = db.collection("sessions").document(sid).get()
    if not doc.exists:
        return None
    data = doc.to_dict() or {}
    exp = data.get("expires_at")
    if exp:
        try:
            if datetime.fromisoformat(exp) < datetime.utcnow():
                db.collection("sessions").document(sid).delete()
                return None
        except Exception:
            pass
    return data


def delete_session(sid: str):
    if sid:
        db.collection("sessions").document(sid).delete()


def require_session(session_id: Optional[str]) -> Dict[str, Any]:
    """Resolve a session or raise 401. Returns session dict with uid/email."""
    s = get_session(session_id) if session_id else None
    if not s:
        raise HTTPException(status_code=401, detail="Authentication required")
    return s


# -------------------------------------------------
# Health
# -------------------------------------------------
@app.get("/")
def root():
    return {"service": "Mentesa", "status": "ok", "llm": config.LLM_PROVIDER}


# -------------------------------------------------
# Routes: Bots
# -------------------------------------------------
@app.get("/bots", response_model=List[BotPublic])
def list_bots(owner_email: Optional[str] = None,
              x_session_id: Optional[str] = Header(default=None)):
    # Authenticated callers only ever see their own bots. Ownership comes from
    # the session, never the query param.
    #
    # Firestore exact-equality queries are fragile here because older bots have
    # inconsistent owner_email casing/whitespace and many lack owner_uid. With a
    # modest collection size we scan once and match by uid OR normalized email,
    # which reliably finds every bot the user owns across devices. We also
    # backfill owner_uid so future indexed lookups are accurate.
    session = require_session(x_session_id)
    email = (session.get("email") or "").strip().lower()
    uid = session.get("uid")
    result = []

    try:
        for doc in db.collection("bots").stream():
            data = doc.to_dict() or {}
            doc_email = (data.get("owner_email") or "").strip().lower()
            doc_uid = data.get("owner_uid")
            if (uid and doc_uid == uid) or (email and doc_email == email):
                data["id"] = doc.id
                # Backfill owner_uid for older bots matched by email.
                if uid and not doc_uid:
                    try:
                        db.collection("bots").document(doc.id).update({"owner_uid": uid})
                        data["owner_uid"] = uid
                    except Exception:
                        pass
                refresh_bot_in_cache(data)
                result.append(sanitize_public(data))
    except Exception as e:
        print(f"[bots] Firestore scan failed, falling back to cache: {e}")
        result = [sanitize_public(b) for b in bots
                  if (b.get("owner_email") or "").strip().lower() == email
                  or (uid and b.get("owner_uid") == uid)]
    return result


@app.get("/bots/{bot_id}", response_model=BotPublic)
def get_bot(bot_id: str, x_session_id: Optional[str] = Header(default=None)):
    session = require_session(x_session_id)
    b = find_bot_by_id(bot_id)
    if not b:
        raise HTTPException(status_code=404, detail="Bot not found")
    if b.get("owner_email") != session["email"]:
        raise HTTPException(status_code=403, detail="Not your bot")
    return sanitize_public(b)


@app.patch("/bots/{bot_id}", response_model=BotPublic)
def update_bot(bot_id: str, payload: BotUpdate,
               x_session_id: Optional[str] = Header(default=None)):
    session = require_session(x_session_id)
    b = find_bot_by_id(bot_id)
    if not b:
        raise HTTPException(status_code=404, detail="Bot not found")
    if b.get("owner_email") != session["email"]:
        raise HTTPException(status_code=403, detail="Not your bot")

    updates = payload.model_dump(exclude_none=True)
    if "name" in updates and updates["name"].strip():
        b["name"] = updates["name"].strip()
    if "personality" in updates and updates["personality"].strip():
        b["personality"] = updates["personality"].strip()
    b["updated_at"] = datetime.now().isoformat()
    save_bot(b)
    refresh_bot_in_cache(b)
    return sanitize_public(b)


@app.post("/bots", response_model=Dict[str, Any])
def create_bot(bot: BotCreate, x_session_id: Optional[str] = Header(default=None)):
    session = require_session(x_session_id)
    uid = session["uid"]
    owner_email = session["email"]

    # Enforce plan bot limit
    owned = [b for b in bots if b.get("owner_email") == owner_email]
    check = billing.can_create_bot(uid, len(owned))
    if not check["allowed"]:
        raise HTTPException(
            status_code=402,
            detail=f"Bot limit reached for {check['plan']} plan "
                   f"({check['limit']} bots). Upgrade to create more.",
        )

    # Scrape website if provided
    frontend_urls = (bot.config or {}).get("urls", [])
    site_text = ""
    if frontend_urls:
        try:
            site_text = scrape_website(frontend_urls[0])
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to scrape site: {e}")

    # Generate config via LLM provider
    try:
        cfg = llm_provider.generate_bot_config(bot.prompt or bot.name or "", site_text)
    except Exception:
        cfg = {
            "name": bot.name or "Unnamed Bot",
            "personality": bot.personality or "A helpful assistant.",
            "settings": {},
        }

    # Sanitize incoming inline files
    file_data = []
    for f in (bot.files or []):
        if isinstance(f, dict):
            file_data.append({
                "id": str(uuid.uuid4()),
                "name": f.get("name") or "file",
                "text": (f.get("text") or "")[:15000],
            })

    config_data = cfg.get("settings", {})
    if not isinstance(config_data, dict):
        config_data = {}
    urls_list = config_data.get("urls", [])
    for u in frontend_urls:
        if u and u not in urls_list:
            urls_list.append(u)
    config_data["urls"] = urls_list

    # Store scraped text per URL so it can be managed/deleted individually.
    scraped_texts = {}
    if frontend_urls and site_text:
        scraped_texts[frontend_urls[0]] = site_text

    new_bot = {
        "id": str(uuid.uuid4()),
        "name": cfg.get("name", bot.name or "Unnamed Bot"),
        "personality": cfg.get("personality", "A helpful assistant."),
        "config": config_data,
        "created_at": datetime.now().isoformat(),
        "api_key": generate_api_key(),
        "scraped_text": site_text,
        "scraped_texts": scraped_texts,
        "file_data": file_data,
        "owner_email": owner_email,
        "owner_uid": uid,
    }

    rebuild_bot_index(new_bot)
    bots.append(new_bot)
    save_bot(new_bot)

    return {
        "bot": sanitize_public(new_bot),
        "api_key": new_bot["api_key"],
        "api_key_masked": mask_key(new_bot["api_key"]),
    }


@app.delete("/bots/{bot_id}")
def delete_bot(bot_id: str, x_session_id: Optional[str] = Header(default=None)):
    session = require_session(x_session_id)
    b = find_bot_by_id(bot_id)
    if not b:
        raise HTTPException(status_code=404, detail="Bot not found")
    if b.get("owner_email") != session["email"]:
        raise HTTPException(status_code=403, detail="Not your bot")
    global bots
    bots = [x for x in bots if x.get("id") != bot_id]
    db.collection("bots").document(bot_id).delete()
    return {"message": "Bot deleted"}


@app.post("/bots/{bot_id}/upload_file")
async def upload_file(bot_id: str, file: UploadFile = File(...),
                      x_session_id: Optional[str] = Header(default=None)):
    session = require_session(x_session_id)
    bot = find_bot_by_id(bot_id)
    if not bot:
        raise HTTPException(404, "Bot not found")
    if bot.get("owner_email") != session["email"]:
        raise HTTPException(403, "Not your bot")

    content = await file.read()
    text = extract_file_text(file.filename, content)

    entry = {"id": str(uuid.uuid4()), "name": file.filename, "text": text[:15000]}
    bot.setdefault("file_data", [])
    bot["file_data"] = [f for f in bot["file_data"] if f.get("name") != file.filename]
    bot["file_data"].append(entry)

    rebuild_bot_index(bot)
    refresh_bot_in_cache(bot)
    save_bot(bot)
    return sanitize_public(bot)


@app.delete("/bots/{bot_id}/files/{file_name}")
def delete_bot_file(bot_id: str, file_name: str,
                    x_session_id: Optional[str] = Header(default=None)):
    session = require_session(x_session_id)
    bot = find_bot_by_id(bot_id)
    if not bot:
        raise HTTPException(404, "Bot not found")
    if bot.get("owner_email") != session["email"]:
        raise HTTPException(403, "Not your bot")
    before = len(bot.get("file_data", []) or [])
    bot["file_data"] = [f for f in (bot.get("file_data") or []) if f.get("name") != file_name]
    if len(bot["file_data"]) == before:
        raise HTTPException(404, "File not found")
    rebuild_bot_index(bot)
    save_bot(bot)
    return sanitize_public(bot)


@app.post("/bots/{bot_id}/urls")
def add_bot_url(bot_id: str, payload: UrlAdd,
                x_session_id: Optional[str] = Header(default=None)):
    session = require_session(x_session_id)
    bot = find_bot_by_id(bot_id)
    if not bot:
        raise HTTPException(404, "Bot not found")
    if bot.get("owner_email") != session["email"]:
        raise HTTPException(403, "Not your bot")

    url = (payload.url or "").strip()
    if not url:
        raise HTTPException(400, "url required")
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        text = scrape_website(url)
    except Exception as e:
        raise HTTPException(400, f"Failed to scrape site: {e}")

    bot.setdefault("scraped_texts", {})
    bot["scraped_texts"][url] = text or "-"

    cfg = bot.get("config") or {}
    urls = cfg.get("urls", [])
    if url not in urls:
        urls.append(url)
    cfg["urls"] = urls
    bot["config"] = cfg

    rebuild_bot_index(bot)
    save_bot(bot)
    return sanitize_public(bot)


@app.delete("/bots/{bot_id}/urls")
def delete_bot_url(bot_id: str, url: str,
                   x_session_id: Optional[str] = Header(default=None)):
    session = require_session(x_session_id)
    bot = find_bot_by_id(bot_id)
    if not bot:
        raise HTTPException(404, "Bot not found")
    if bot.get("owner_email") != session["email"]:
        raise HTTPException(403, "Not your bot")

    # Remove from scraped_texts map and config.urls.
    st = bot.get("scraped_texts") or {}
    st.pop(url, None)
    bot["scraped_texts"] = st

    cfg = bot.get("config") or {}
    cfg["urls"] = [u for u in cfg.get("urls", []) if u != url]
    bot["config"] = cfg

    # If this was the legacy single-URL bot, clear the legacy blob too.
    if not st and bot.get("scraped_text"):
        bot["scraped_text"] = ""

    rebuild_bot_index(bot)
    save_bot(bot)
    return sanitize_public(bot)


# -------------------------------------------------
# Routes: API key management
# -------------------------------------------------
@app.get("/bots/{bot_id}/apikey")
def get_bot_api_key(bot_id: str, x_session_id: Optional[str] = Header(default=None)):
    session = require_session(x_session_id)
    b = find_bot_by_id(bot_id)
    if not b:
        raise HTTPException(status_code=404, detail="Bot not found")
    if b.get("owner_email") != session["email"]:
        raise HTTPException(403, "Not your bot")
    key = b.get("api_key")
    if not key:
        key = generate_api_key()
        b["api_key"] = key
        save_bot(b)
    return {"api_key": key, "api_key_masked": mask_key(key)}


@app.post("/bots/{bot_id}/rotate-key")
def rotate_bot_api_key(bot_id: str, x_session_id: Optional[str] = Header(default=None)):
    session = require_session(x_session_id)
    b = find_bot_by_id(bot_id)
    if not b:
        raise HTTPException(status_code=404, detail="Bot not found")
    if b.get("owner_email") != session["email"]:
        raise HTTPException(403, "Not your bot")
    b["api_key"] = generate_api_key()
    save_bot(b)
    return {"api_key": b["api_key"], "api_key_masked": mask_key(b["api_key"])}


# -------------------------------------------------
# Routes: Widget customization
# -------------------------------------------------
@app.get("/widget/config")
def public_widget_config(authorization: Optional[str] = Header(default=None),
                         x_api_key: Optional[str] = Header(default=None),
                         api_key: Optional[str] = None):
    """Public endpoint the embed widget calls on load to get its appearance
    and whether to show Mentesa branding (based on the owner's plan)."""
    key = None
    if authorization and authorization.lower().startswith("bearer "):
        key = authorization.split(" ", 1)[1].strip()
    elif x_api_key:
        key = x_api_key.strip()
    elif api_key:
        key = api_key.strip()
    if not key:
        raise HTTPException(status_code=400, detail="api key required")

    bot = find_bot_by_api_key(key)
    if not bot:
        raise HTTPException(status_code=401, detail="Invalid API key")

    branding = True
    owner_uid = bot.get("owner_uid")
    if owner_uid:
        branding = billing.current_plan(owner_uid).get("branding", True)

    cfg = get_widget_config(bot)
    cfg["branding"] = branding
    cfg["bot_name"] = bot.get("name", "Mentesa Bot")
    return cfg


@app.get("/bots/{bot_id}/widget")
def get_bot_widget(bot_id: str, x_session_id: Optional[str] = Header(default=None)):
    session = require_session(x_session_id)
    b = find_bot_by_id(bot_id)
    if not b:
        raise HTTPException(status_code=404, detail="Bot not found")
    if b.get("owner_email") != session["email"]:
        raise HTTPException(403, "Not your bot")
    return get_widget_config(b)


@app.put("/bots/{bot_id}/widget")
def update_bot_widget(bot_id: str, payload: WidgetConfigUpdate,
                      x_session_id: Optional[str] = Header(default=None)):
    session = require_session(x_session_id)
    b = find_bot_by_id(bot_id)
    if not b:
        raise HTTPException(status_code=404, detail="Bot not found")
    if b.get("owner_email") != session["email"]:
        raise HTTPException(403, "Not your bot")
    widget = dict(b.get("widget") or {})
    for field, value in payload.model_dump(exclude_none=True).items():
        widget[field] = value
    b["widget"] = widget
    save_bot(b)
    return get_widget_config(b)


# -------------------------------------------------
# Route: Chat (public via api key, or owner via session)
# -------------------------------------------------
@app.post("/chat")
def chat(req: ChatRequest, request: Request,
         authorization: Optional[str] = Header(default=None),
         x_api_key: Optional[str] = Header(default=None)):

    # Resolve API key. We no longer accept a raw bot_id as authentication
    # for embedded widgets; a valid api key is required there.
    api_key = None
    if authorization and authorization.lower().startswith("bearer "):
        api_key = authorization.split(" ", 1)[1].strip()
    elif x_api_key:
        api_key = x_api_key.strip()

    bot = None
    if api_key:
        bot = find_bot_by_api_key(api_key)
    # Allow bot_id only as a fallback for the owner's in-app chat tester.
    if not bot and req.bot_id:
        bot = find_bot_by_id(req.bot_id)

    if not bot:
        raise HTTPException(status_code=401, detail="Invalid API key or bot_id")

    # Rate limit (sliding window) keyed by api key or client ip
    rl_key = api_key or (request.client.host if request.client else "anon")
    if not ratelimit.check(rl_key, max_requests=20, window_seconds=60):
        raise HTTPException(status_code=429, detail="Too many requests. Slow down.")

    # Monthly quota enforced against the bot owner's plan
    owner_uid = bot.get("owner_uid")
    if owner_uid:
        quota = billing.can_send_message(owner_uid)
        if not quota["allowed"]:
            raise HTTPException(
                status_code=402,
                detail=f"Monthly message limit reached ({quota['limit']}). "
                       f"Upgrade the plan to continue.",
            )

    # Retrieve relevant context via RAG
    chunks = bot.get("chunks") or []
    if not chunks and (bot.get("scraped_text") or bot.get("file_data")):
        rebuild_bot_index(bot)
        chunks = bot.get("chunks") or []
        save_bot(bot)
    context = rag.retrieve(req.message, chunks) if chunks else bot.get("scraped_text", "")

    system = (
        f"You are '{bot.get('name', 'Bot')}'. "
        f"Personality: {bot.get('personality', '')}. "
        f"Be helpful and concise. Use the conversation so far to stay in context."
    )

    # Build conversation memory. Prefer client-sent history; fall back to / merge
    # with server-persisted history keyed by the widget's session_id.
    convo_id = (req.session_id or "").strip()
    server_history = []
    if convo_id:
        doc = db.collection("widget_chats").document(f"{bot['id']}_{convo_id}").get()
        if doc.exists:
            server_history = (doc.to_dict() or {}).get("history", [])

    history = req.history if req.history else server_history
    # Keep only the most recent turns to bound prompt size.
    history = [h for h in history if isinstance(h, dict) and h.get("content")][-12:]

    try:
        reply = llm_provider.chat(system, req.message, context=context, history=history)
        if owner_uid:
            billing.increment_usage(owner_uid, 1)
        branding = True
        if owner_uid:
            branding = billing.current_plan(owner_uid).get("branding", True)

        # Persist updated conversation for this widget session (best-effort).
        if convo_id:
            try:
                updated = history + [
                    {"role": "user", "content": req.message},
                    {"role": "bot", "content": reply or ""},
                ]
                db.collection("widget_chats").document(f"{bot['id']}_{convo_id}").set(
                    {"history": updated[-40:], "updated_at": datetime.now().isoformat()}
                )
            except Exception as e:
                print(f"[chat] failed to persist widget history: {e}")

        return {"reply": reply or "I couldn't generate a reply.",
                "bot_id": bot["id"], "branding": branding}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------
# Routes: Auth
# -------------------------------------------------
@app.post("/auth/login")
def auth_login(payload: Dict[str, str]):
    email = payload.get("email")
    password = payload.get("password")
    if not email or not password:
        raise HTTPException(status_code=400, detail="email and password required")

    try:
        resp = _rest_post("accounts:signInWithPassword",
                          {"email": email, "password": password, "returnSecureToken": True})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Sign-in failed: {e}")

    uid = resp.get("localId")
    if not uid:
        raise HTTPException(status_code=400, detail="Sign-in did not return user id")

    try:
        ur = admin_auth.get_user(uid)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not fetch user record: {e}")

    if not getattr(ur, "email_verified", False):
        raise HTTPException(status_code=403, detail="Email not verified")

    sid = create_session(uid, email, ur.display_name or email.split("@")[0])
    return {
        "session_id": sid,
        "user": {"uid": uid, "email": email, "displayName": ur.display_name},
    }


@app.post("/auth/logout")
def auth_logout(payload: Dict[str, str] = None):
    sid = payload.get("session_id") if payload else None
    if not sid:
        raise HTTPException(status_code=400, detail="session_id required")
    delete_session(sid)
    return {"ok": True}


@app.get("/auth/session")
def auth_get_session(session_id: Optional[str] = None):
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id required")
    s = get_session(session_id)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"user": {"uid": s.get("uid"), "email": s.get("email"),
                     "displayName": s.get("displayName")}}


@app.post("/auth/register")
def auth_register(payload: Dict[str, str]):
    email = payload.get("email")
    password = payload.get("password")
    display_name = payload.get("display_name")
    if not email or not password:
        raise HTTPException(status_code=400, detail="email and password required")

    try:
        try:
            admin_auth.get_user_by_email(email)
            raise HTTPException(status_code=400, detail="User already exists")
        except admin_auth.UserNotFoundError:
            pass

        admin_auth.create_user(email=email, password=password, display_name=display_name)
        signin = _rest_post("accounts:signInWithPassword",
                            {"email": email, "password": password, "returnSecureToken": True})
        id_token = signin.get("idToken")
        if id_token:
            _rest_post("accounts:sendOobCode",
                       {"requestType": "VERIFY_EMAIL", "idToken": id_token})
        return {"message": "User created. Verification email sent."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------
# Routes: Chat history
# -------------------------------------------------
@app.get("/bots/{bot_id}/history")
def get_chat_history(bot_id: str, x_session_id: Optional[str] = Header(default=None)):
    session = require_session(x_session_id)
    b = find_bot_by_id(bot_id)
    if not b:
        raise HTTPException(status_code=404, detail="Bot not found")
    if b.get("owner_email") != session["email"]:
        raise HTTPException(status_code=403, detail="Not your bot")
    doc = db.collection("bot_chats").document(bot_id).get()
    if doc.exists:
        return doc.to_dict().get("history", [])
    return []


@app.post("/bots/{bot_id}/history")
def save_chat_history(bot_id: str, payload: Dict[str, Any],
                      x_session_id: Optional[str] = Header(default=None)):
    session = require_session(x_session_id)
    b = find_bot_by_id(bot_id)
    if not b:
        raise HTTPException(status_code=404, detail="Bot not found")
    if b.get("owner_email") != session["email"]:
        raise HTTPException(status_code=403, detail="Not your bot")
    history = payload.get("history", [])
    db.collection("bot_chats").document(bot_id).set({"history": history})
    return {"status": "ok"}


# -------------------------------------------------
# Routes: Billing
# -------------------------------------------------
@app.get("/billing/plans")
def billing_plans():
    return {
        "plans": [
            {
                "id": pid,
                "name": p["name"],
                "price_usd": p["price_usd"],
                "bot_limit": p["bot_limit"],
                "message_limit": p["message_limit"],
                "branding": p["branding"],
            }
            for pid, p in config.PLANS.items()
        ]
    }


@app.get("/billing/usage")
def billing_usage(x_session_id: Optional[str] = Header(default=None)):
    session = require_session(x_session_id)
    return billing.usage_summary(session["uid"])


@app.post("/billing/sync")
def billing_sync(x_session_id: Optional[str] = Header(default=None)):
    """Reconcile subscription state from Dodo (safety net after checkout)."""
    session = require_session(x_session_id)
    if not payment_service.enabled():
        raise HTTPException(status_code=503, detail="Billing is not configured")
    try:
        result = payment_service.sync_from_dodo(session["uid"])
        return {**result, **billing.usage_summary(session["uid"])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/billing/checkout")
def billing_checkout(payload: Dict[str, str],
                     x_session_id: Optional[str] = Header(default=None)):
    session = require_session(x_session_id)
    if not payment_service.enabled():
        raise HTTPException(status_code=503, detail="Billing is not configured")
    plan_id = payload.get("plan_id")
    if plan_id not in config.PLANS or plan_id == config.DEFAULT_PLAN:
        raise HTTPException(status_code=400, detail="Invalid plan")
    try:
        return payment_service.create_checkout_session(
            session["uid"], session["email"], session.get("displayName", ""), plan_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/billing/portal")
def billing_portal(x_session_id: Optional[str] = Header(default=None)):
    session = require_session(x_session_id)
    if not payment_service.enabled():
        raise HTTPException(status_code=503, detail="Billing is not configured")
    try:
        return payment_service.create_portal_session(session["uid"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/billing/webhook")
async def billing_webhook(request: Request):
    payload = await request.body()
    headers = {
        "webhook-id": request.headers.get("webhook-id", ""),
        "webhook-signature": request.headers.get("webhook-signature", ""),
        "webhook-timestamp": request.headers.get("webhook-timestamp", ""),
    }
    try:
        event = payment_service.verify_and_parse_webhook(payload, headers)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Webhook verification failed: {e}")
    try:
        payment_service.handle_event(event)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    return {"received": True}
