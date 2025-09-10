# backend/main.py
from __future__ import annotations
import os
import uuid
import secrets
from pathlib import Path
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import google.generativeai as genai
from datetime import datetime

from utils.scraper import scrape_website

from fastapi.staticfiles import StaticFiles

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.firebase_config import db

# -------------------------------------------------
# Init
# -------------------------------------------------
app = FastAPI(title="Mentesa API (v1 branch) — Bots & Embeds")

# Serve static folder (for embed.js)
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

# --- Load bots from Firebase ---
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

def save_bots(bots):
    for bot in bots:
        bot_id = bot.get("id") or str(uuid.uuid4())
        bot["id"] = bot_id
        db.collection("bots").document(bot_id).set(bot)

# -------------------------------------------------
# Config: Gemini
# -------------------------------------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("[WARN] GEMINI_API_KEY not set. Running in echo mode.")

# -------------------------------------------------
# Middleware
# -------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or explicitly ["https://your-portfolio-site.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],   # ensure exposed headers too
)

# -------------------------------------------------
# Models
# -------------------------------------------------
class BotCreate(BaseModel):
    prompt: Optional[str] = ""
    url: Optional[str] = None
    name: Optional[str] = None
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
    bot_id: Optional[str] = None  # fallback if no API key

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
    return b

def find_bot_by_id(bid: str) -> Optional[Dict[str, Any]]:
    return next((b for b in bots if b.get("id") == bid), None)

def find_bot_by_api_key(key: str) -> Optional[Dict[str, Any]]:
    return next((b for b in bots if b.get("api_key") == key), None)

# -------------------------------------------------
# Routes: Bots
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
    site_text = ""
    if bot.url:
        try:
            site_text = scrape_website(bot.url)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to scrape site: {e}")

    # ----------------------
    # Call Gemini to build bot config
    # ----------------------
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.5-pro")

    prompt_text = f"""
    You are creating a bot based on this description: "{bot.prompt}"

    Website content:
    {site_text}

    Rules:
    - Only use the website content.
    - If information is missing, say 'Not mentioned on the website'.
    - Do NOT invent or hallucinate.
    - Output JSON with fields: name, personality, settings.
    """

    try:
        response = model.generate_content(prompt_text)
        raw = response.text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini error: {e}")

    import json
    try:
        cfg = json.loads(raw)
    except Exception:
        cfg = {
            "name": bot.name or "New Bot",
            "personality": bot.personality or "No personality provided",
            "settings": {}
        }

    new_bot = {
        "id": str(uuid.uuid4()),
        "name": cfg.get("name", bot.name or "Unnamed Bot"),
        "personality": cfg.get("personality", bot.personality or ""),
        "config": cfg.get("settings", bot.config or {}),
        "created_at": datetime.now().isoformat(),
        "api_key": generate_api_key(),
        "scraped_text": site_text,  # 🔑 store raw scraped content
    }

    bots.append(new_bot)
    save_bots(bots)
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
# Routes: API key management
# -------------------------------------------------
@app.get("/bots/{bot_id}/apikey")
def get_bot_api_key(bot_id: str):
    b = find_bot_by_id(bot_id)
    if not b:
        raise HTTPException(status_code=404, detail="Bot not found")
    key = b.get("api_key")
    if not key:
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
# Route: Chat
# -------------------------------------------------
@app.post("/chat")
def chat(req: ChatRequest, 
         authorization: Optional[str] = Header(default=None), 
         x_api_key: Optional[str] = Header(default=None)):

    api_key = None

    # 1. Check Authorization: Bearer
    if authorization and authorization.lower().startswith("bearer "):
        api_key = authorization.split(" ", 1)[1].strip()
    # 2. Check x-api-key header
    elif x_api_key:
        api_key = x_api_key.strip()
    # 3. Fallback to bot_id
    elif req.bot_id:
        api_key = req.bot_id
    else:
        raise HTTPException(status_code=400, detail="Provide Authorization, x-api-key, or bot_id")

    # 🔑 Find bot
    bot = find_bot_by_api_key(api_key) or find_bot_by_id(api_key)
    if not bot:
        raise HTTPException(status_code=401, detail="Invalid API key or bot_id")

    # ------------------------------
    # ✅ Use GEMINI_API_KEY here
    # ------------------------------
    genai.configure(api_key=GEMINI_API_KEY)

    # Build prompt
    name = bot["name"]
    personality = bot.get("personality", "")
    scraped=bot.get("scraped_content","")
    prompt = f"You are '{name}'. Personality: {personality}\n Here is information from the website (if available):{scraped}, Only answer based on the website content. User: {req.message}"

    try:
        model = genai.GenerativeModel("gemini-2.5-pro")
        response = model.generate_content(prompt)

        reply_text = "I couldn't generate a reply."
        try:
            if getattr(response, "candidates", None):
                parts = response.candidates[0].content.parts
                if parts and hasattr(parts[0], "text"):
                    reply_text = parts[0].text
        except Exception:
            pass

        return {"reply": reply_text, "bot_id": bot["id"]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
