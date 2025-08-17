# backend/main.py
from __future__ import annotations
import os
import json
import uuid
import secrets
from pathlib import Path
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

import google.generativeai as genai
from dotenv import load_dotenv

from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Absolute path to 'static' folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_path = os.path.join(BASE_DIR, "static")

app.mount("/static", StaticFiles(directory=static_path), name="static")


# -------------------------------------------------
# Paths & persistence
# -------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parents[1]  # repo root
DATA_DIR = ROOT_DIR / "data"
BOTS_FILE = DATA_DIR / "bots.json"
DATA_DIR.mkdir(parents=True, exist_ok=True)
if not BOTS_FILE.exists():
    BOTS_FILE.write_text("[]", encoding="utf-8")

from utils.firebase_config import db

# --- Load bots from Firebase at startup ---
bots = []
def load_bots():
    global bots
    bots_ref = db.collection("bots").stream()
    bots = []
    for doc in bots_ref:
        data = doc.to_dict()
        data["id"] = doc.id
        bots.append(data)

load_bots()

print("Loaded bots:", [b["name"] for b in bots])


bot_id = str(uuid.uuid4())
bot_doc = {
    "id": bot_id,
    "name": cfg["name"],
    "personality": cfg["personality"],
    "settings": cfg.get("settings", {})
}

# Save bot to Firebase
db.collection("bots").document(bot_id).set(bot_doc)

# Create API key
api_key = str(uuid.uuid4())
db.collection("bot_api_keys").document(bot_id).set({"api_key": api_key})


def save_bots(bots):
    """Save or update a list of bots in Firestore."""
    for bot in bots:
        bot_id = bot.get("id") or str(uuid.uuid4())
        bot["id"] = bot_id
        db.collection("bots").document(bot_id).set(bot)

# -------------------------------------------------
# Config: Gemini
# -------------------------------------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("[WARN] GEMINI_API_KEY not set. Set it in .env")
else:
    genai.configure(api_key=GEMINI_API_KEY)

# -------------------------------------------------
# FastAPI app
# -------------------------------------------------
app = FastAPI(title="Mentesa API (v1 branch) — Bots & Embeds")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# Models
# -------------------------------------------------
class BotCreate(BaseModel):
    name: str
    personality: Optional[str] = ""
    config: Dict[str, Any] = Field(default_factory=dict)

class BotPublic(BaseModel):
    id: str
    name: str
    personality: Optional[str] = ""
    config: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    bot_id: Optional[str] = None  # optional if using API key

# -------------------------------------------------
# Helpers
# -------------------------------------------------
API_KEY_PREFIX = "mentesa_sk_"

def generate_api_key() -> str:
    # ~256-bit random; URL-safe
    return API_KEY_PREFIX + secrets.token_urlsafe(32)

def mask_key(k: Optional[str]) -> str:
    if not k:
        return ""
    return f"{k[:12]}...{k[-4:]}"

def sanitize_public(bot: Dict[str, Any]) -> Dict[str, Any]:
    """Return bot without secrets for public listing."""
    b = dict(bot)
    b.pop("api_key", None)
    return b

def find_bot_by_id(bid: str) -> Optional[Dict[str, Any]]:
    return next((b for b in bots if b.get("id") == bid), None)

print("Incoming API key:", api_key)
print("Available keys:", [b["api_key"] for b in bots])

def find_bot_by_api_key(key: str) -> Optional[Dict[str, Any]]:
    return next((b for b in bots if b.get("api_key") == key), None)

# -------------------------------------------------
# Routes: Bots (no secrets in list/detail)
# -------------------------------------------------
@app.get("/bots", response_model=List[BotPublic])
def list_bots():
    return [sanitize_public(b) for b in bots]

@app.get("/bots/{bot_id}", response_model=BotPublic)
def get_bot(bot_id: str):
    b = find_bot_by_id(bot_id)
    if not b:
        raise HTTPException(status_code=404, detail="Bot not found")
    return sanitize_public(b)

@app.post("/bots", response_model=Dict[str, Any])
def create_bot(bot: BotCreate):
    new_bot = {
        "id": str(uuid.uuid4()),
        "name": bot.name,
        "personality": bot.personality or "",
        "config": bot.config or {},
        "created_at": uuid.uuid1().ctime() if hasattr(uuid, "uuid1") else None,
        "api_key": generate_api_key(),  # 🔑 secret per-bot
    }
    bots.append(new_bot)
    save_bots(bots)
    # Return bot with masked key for UI + full key separately
    return {
        "bot": sanitize_public(new_bot),
        "api_key": new_bot["api_key"],
        "api_key_masked": mask_key(new_bot["api_key"]),
    }

@app.delete("/bots/{bot_id}")
def delete_bot(bot_id: str):
    global bots
    before = len(bots)
    bots = [b for b in bots if b.get("id") != bot_id]
    if len(bots) == before:
        raise HTTPException(status_code=404, detail="Bot not found")
    save_bots(bots)
    return {"message": "Bot deleted"}

# -------------------------------------------------
# Routes: API key management (owner-side UI)
# -------------------------------------------------
@app.get("/bots/{bot_id}/apikey")
def get_bot_api_key(bot_id: str):
    b = find_bot_by_id(bot_id)
    if not b:
        raise HTTPException(status_code=404, detail="Bot not found")
    key = b.get("api_key")
    if not key:
        # create on demand if missing (migration scenario)
        key = generate_api_key()
        b["api_key"] = key
        save_bots(bots)
    return {"api_key": key, "api_key_masked": mask_key(key)}

@app.post("/bots/{bot_id}/rotate-key")
def rotate_bot_api_key(bot_id: str):
    b = find_bot_by_id(bot_id)
    if not b:
        raise HTTPException(status_code=404, detail="Bot not found")
    b["api_key"] = generate_api_key()
    save_bots(bots)
    return {"api_key": b["api_key"], "api_key_masked": mask_key(b["api_key"])}

# -------------------------------------------------
# Route: Chat (supports API key OR bot_id)
#   - Prefer Authorization: Bearer <api_key>
#   - Fallback to body.bot_id for internal calls
# -------------------------------------------------
@app.post("/chat")
def chat(req: ChatRequest, authorization: Optional[str] = Header(default=None), x_api_key: Optional[str] = Header(default=None)):
    # 1) Auth via API key if provided
    api_key = None
    if authorization and authorization.lower().startswith("bearer "):
        api_key = authorization.split(" ", 1)[1].strip()
    elif x_api_key:
        api_key = x_api_key.strip()

    bot = None
    if api_key:
        bot = find_bot_by_api_key(api_key)
        if not bot:
            raise HTTPException(status_code=401, detail="Invalid API key")
    else:
        # 2) Fallback: use bot_id from body (internal/admin usage)
        if not req.bot_id:
            raise HTTPException(status_code=400, detail="Provide Authorization: Bearer <api_key> or bot_id in body")
        bot = find_bot_by_id(req.bot_id)
        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found")

    # Build prompt with personality/context
    personality = bot.get("personality") or ""
    name = bot.get("name") or "Mentesa Bot"
    prompt = f"You are '{name}'. Personality: {personality}\nUser: {req.message}"

    try:
        if not GEMINI_API_KEY:
            # Allow running without key (useful for UI plumbing)
            return {"reply": "[Gemini key missing] Echo: " + req.message}

        model = genai.GenerativeModel("gemini-2.5-pro")
        response = model.generate_content(prompt)

        # Defensive parse
        reply_text = "I couldn't generate a reply."
        try:
            if getattr(response, "candidates", None):
                parts = response.candidates[0].content.parts
                if parts and hasattr(parts[0], "text"):
                    reply_text = parts[0].text
        except Exception:
            reply_text = "I couldn't generate a reply."

        return {"reply": reply_text, "bot_id": bot["id"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------------------------------------------------
# Embeddable widget
# GET /embed.js -> returns a small JS snippet that renders a widget
# Usage on user site:
# <script src="https://YOUR_BACKEND_HOST/embed.js" data-api-key="MENTESA_API_KEY"></script>
# -------------------------------------------------
@app.get("/embed.js", response_class=PlainTextResponse)
def embed_js():
    js = r"""
document.addEventListener("DOMContentLoaded", function() {
    const botName = document.currentScript.getAttribute("data-bot-name") || "Mentesa Bot";
    const apiKey = document.currentScript.getAttribute("data-api-key") || "";

    // Create main container
    const chatBox = document.createElement("div");
    chatBox.id = "mentesa-chat-widget";
    chatBox.style.position = "fixed";
    chatBox.style.bottom = "20px";
    chatBox.style.right = "20px";
    chatBox.style.width = "300px";
    chatBox.style.height = "400px";
    chatBox.style.backgroundColor = "#fff";
    chatBox.style.border = "1px solid #ccc";
    chatBox.style.borderRadius = "12px";
    chatBox.style.boxShadow = "0 4px 12px rgba(0,0,0,0.3)";
    chatBox.style.zIndex = "9999";
    chatBox.style.display = "flex";
    chatBox.style.flexDirection = "column";
    chatBox.style.overflow = "hidden";

    // Header
    const header = document.createElement("div");
    header.style.backgroundColor = "#0084ff";
    header.style.color = "#fff";
    header.style.padding = "10px";
    header.style.fontWeight = "bold";
    header.style.textAlign = "center";
    header.textContent = botName + " (powered by Mentesa)";
    chatBox.appendChild(header);

    // Chat content
    const chatContent = document.createElement("div");
    chatContent.id = "mentesa-chat-content";
    chatContent.style.flex = "1";
    chatContent.style.padding = "10px";
    chatContent.style.overflowY = "auto";
    chatContent.style.backgroundColor = "#f9f9f9";
    chatBox.appendChild(chatContent);

    // Input container
    const inputContainer = document.createElement("div");
    inputContainer.style.display = "flex";
    inputContainer.style.borderTop = "1px solid #ccc";

    const input = document.createElement("input");
    input.type = "text";
    input.placeholder = "Type a message…";
    input.style.flex = "1";
    input.style.padding = "10px";
    input.style.border = "none";
    input.style.outline = "none";

    const sendBtn = document.createElement("button");
    sendBtn.textContent = "Send";
    sendBtn.style.backgroundColor = "#0084ff";
    sendBtn.style.color = "#fff";
    sendBtn.style.border = "none";
    sendBtn.style.padding = "0 15px";
    sendBtn.style.cursor = "pointer";

    inputContainer.appendChild(input);
    inputContainer.appendChild(sendBtn);
    chatBox.appendChild(inputContainer);

    document.body.appendChild(chatBox);

    // Dummy send function
    sendBtn.addEventListener("click", function() {
        const message = input.value.trim();
        if (!message) return;

        const userMsg = document.createElement("div");
        userMsg.textContent = "🧑 " + message;
        userMsg.style.backgroundColor = "#0084ff";
        userMsg.style.color = "#fff";
        userMsg.style.padding = "6px 10px";
        userMsg.style.margin = "5px 0";
        userMsg.style.borderRadius = "10px";
        userMsg.style.textAlign = "right";

        chatContent.appendChild(userMsg);
        chatContent.scrollTop = chatContent.scrollHeight;
        input.value = "";

        // Placeholder bot reply
        const botMsg = document.createElement("div");
        botMsg.textContent = "🤖 This is a reply from " + botName;
        botMsg.style.backgroundColor = "#f1f0f0";
        botMsg.style.color = "#000";
        botMsg.style.padding = "6px 10px";
        botMsg.style.margin = "5px 0";
        botMsg.style.borderRadius = "10px";
        botMsg.style.textAlign = "left";

        setTimeout(() => {
            chatContent.appendChild(botMsg);
            chatContent.scrollTop = chatContent.scrollHeight;
        }, 500);
    });
});

    """.strip()
    return js
