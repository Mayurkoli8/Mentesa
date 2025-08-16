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
app.mount("/static", StaticFiles(directory="static"), name="static")


# -------------------------------------------------
# Paths & persistence
# -------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parents[1]  # repo root
DATA_DIR = ROOT_DIR / "data"
BOTS_FILE = DATA_DIR / "bots.json"
DATA_DIR.mkdir(parents=True, exist_ok=True)
if not BOTS_FILE.exists():
    BOTS_FILE.write_text("[]", encoding="utf-8")

def load_bots() -> List[Dict[str, Any]]:
    try:
        data = json.loads(BOTS_FILE.read_text(encoding="utf-8"))
        # If stored as dict keyed by ID, convert to list
        if isinstance(data, dict):
            return [
                {**v, "id": k} for k, v in data.items()
            ]
        return data
    except Exception:
        return []

def save_bots(bots: List[Dict[str, Any]]) -> None:
    BOTS_FILE.write_text(json.dumps(bots, indent=2), encoding="utf-8")

bots: List[Dict[str, Any]] = load_bots()

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
(function(){
  // Identify the current script tag
  var s = document.currentScript || (function(){
    var scripts = document.getElementsByTagName('script');
    return scripts[scripts.length - 1];
  })();

  var API_KEY = s.getAttribute('data-api-key');
  var BACKEND = (new URL(s.src)).origin; // same origin as where embed.js is served

  if(!API_KEY){
    console.warn("[Mentesa] Missing data-api-key on embed.js script tag.");
    return;
  }

  // Basic styles
  var css = ".mentesa-widget{position:fixed;right:20px;bottom:20px;z-index:999999;font-family:Inter,system-ui,Arial,sans-serif}"+
            ".mentesa-fab{width:56px;height:56px;border-radius:50%;border:none;box-shadow:0 8px 20px rgba(0,0,0,.15);cursor:pointer}"+
            ".mentesa-panel{position:fixed;right:20px;bottom:90px;width:340px;max-height:60vh;background:#fff;border-radius:12px;box-shadow:0 20px 40px rgba(0,0,0,.2);display:none;overflow:hidden;border:1px solid #eee}"+
            ".mentesa-header{padding:12px 14px;font-weight:600;border-bottom:1px solid #f1f1f1;background:#fafafa}"+
            ".mentesa-body{padding:12px;overflow:auto;height:280px}"+
            ".mentesa-msg{margin-bottom:8px;line-height:1.4}"+
            ".mentesa-msg.user{text-align:right}"+
            ".mentesa-msg .bubble{display:inline-block;padding:8px 10px;border-radius:10px;max-width:80%}"+
            ".mentesa-msg.user .bubble{background:#e8f0fe}"+
            ".mentesa-msg.bot .bubble{background:#f5f5f5}"+
            ".mentesa-input{display:flex;border-top:1px solid #f1f1f1}"+
            ".mentesa-input input{flex:1;padding:10px;border:none;outline:none}"+
            ".mentesa-input button{padding:0 12px;border:none;background:#111;color:#fff;cursor:pointer}";

  var elStyle = document.createElement('style');
  elStyle.type = 'text/css';
  elStyle.appendChild(document.createTextNode(css));
  document.head.appendChild(elStyle);

  // Root containers
  var root = document.createElement('div');
  root.className = 'mentesa-widget';
  var fab = document.createElement('button');
  fab.className = 'mentesa-fab';
  fab.title = 'Chat with Mentesa Bot';
  fab.innerHTML = '💬';
  var panel = document.createElement('div');
  panel.className = 'mentesa-panel';

  var header = document.createElement('div');
  header.className = 'mentesa-header';
  header.textContent = 'Mentesa Bot';
  var body = document.createElement('div');
  body.className = 'mentesa-body';
  var inputWrap = document.createElement('div');
  inputWrap.className = 'mentesa-input';
  var input = document.createElement('input');
  input.placeholder = 'Type a message...';
  var sendBtn = document.createElement('button');
  sendBtn.textContent = 'Send';

  inputWrap.appendChild(input);
  inputWrap.appendChild(sendBtn);
  panel.appendChild(header);
  panel.appendChild(body);
  panel.appendChild(inputWrap);

  root.appendChild(fab);
  document.body.appendChild(root);
  document.body.appendChild(panel);

  fab.addEventListener('click', function(){
    panel.style.display = (panel.style.display === 'block') ? 'none' : 'block';
    if(panel.style.display === 'block'){ input.focus(); }
  });

  function appendMsg(side, text){
    var row = document.createElement('div');
    row.className = 'mentesa-msg ' + side;
    var b = document.createElement('div');
    b.className = 'bubble';
    b.textContent = text;
    row.appendChild(b);
    body.appendChild(row);
    body.scrollTop = body.scrollHeight;
  }

  async function send(){
    var text = (input.value || "").trim();
    if(!text) return;
    appendMsg('user', text);
    input.value = "";
    try{
      var res = await fetch(BACKEND + "/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer " + API_KEY
        },
        body: JSON.stringify({ message: text })
      });
      var data = await res.json();
      appendMsg('bot', data && data.reply ? data.reply : "No reply");
    }catch(err){
      appendMsg('bot', "⚠️ Error: " + err.message);
    }
  }

  input.addEventListener('keydown', function(e){ if(e.key === 'Enter'){ send(); }});
  sendBtn.addEventListener('click', send);
})();
    """.strip()
    return js
