# backend/main.py
from __future__ import annotations
import os
import uuid
import secrets
from pathlib import Path
from typing import Optional, Dict, Any, List
import firebase_admin

from fastapi import FastAPI, HTTPException, Header, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import google.generativeai as genai
from datetime import datetime

import io
import docx

from utils.scraper import scrape_website

from fastapi.staticfiles import StaticFiles

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.firebase_config import db

# -------------------------------------------------
# Init
# -------------------------------------------------
app = FastAPI(title="Mentesa V8")

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
    import re, json, uuid
    from datetime import datetime

    # Get the first URL from frontend config (if any)
    frontend_urls = getattr(bot, "config", {}).get("urls", [])
    site_text = ""
    if frontend_urls:
        try:
            site_text = scrape_website(frontend_urls[0])
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to scrape site: {e}")
    
    # ----------------------
    # Call Gemini to build bot config
    # ----------------------
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.5-pro")

    if site_text.strip():
        prompt_text = f"""
        You are creating a bot from this description: "{bot.prompt}"

        Website content:
        {site_text}

        Rules:
        - Use BOTH the website content and the description.
        - If something is missing in both, write "Not mentioned on the website".
        - Do NOT hallucinate or invent things.
        - Respond ONLY with valid JSON in this format:

        {{
          "name": "string",
          "personality": "string",
          "settings": {{}}
        }}
        """
    else:
        prompt_text = f"""
        You are creating a bot from this description: "{bot.prompt}"

        Rules:
        - Use ONLY the description (no website is provided).
        - Do NOT hallucinate extra things.
        - Respond ONLY with valid JSON in this format:

        {{
          "name": "string",
          "personality": "string",
          "settings": {{}}
        }}
        """

    # --- Generate bot config from Gemini ---
    try:
        response = model.generate_content(prompt_text)
        raw = response.text.strip()

        # Extract JSON only
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            cfg = json.loads(match.group(0))
        else:
            raise ValueError("No JSON found in Gemini response")

    except Exception:
        cfg = {
            "name": bot.name or "Unnamed Bot",
            "personality": "Not mentioned on the website",
            "settings": {}
        }

    # --- Sanitize incoming files ---
    incoming_files = getattr(bot, "files", []) or []
    file_data = []
    for f in incoming_files:
        if isinstance(f, dict):
            fname = f.get("name") or "file"
            ftext = f.get("text") or ""
            ftext = ftext[:15000]  # truncate to 15k chars
            file_data.append({"id": str(uuid.uuid4()), "name": fname, "text": ftext})

    # --- Merge frontend URL with Gemini config safely ---
    config_data = cfg.get("settings", {})
    if not isinstance(config_data, dict):
        config_data = {}

    # Preserve existing URLs from Gemini + add frontend URL
    urls_list = config_data.get("urls", [])
    frontend_url = getattr(bot, "config", {}).get("urls", [])
    for u in frontend_url:
        if u and u not in urls_list:
            urls_list.append(u)
    config_data["urls"] = urls_list

    # --- Create new bot object ---
    new_bot = {
        "id": str(uuid.uuid4()),
        "name": cfg.get("name", bot.name or "Unnamed Bot"),
        "personality": cfg.get("personality", "Not mentioned on the website"),
        "config": config_data,
        "created_at": datetime.now().isoformat(),
        "api_key": generate_api_key(),
        "scraped_text": site_text,
        "file_data": file_data,
    }

    # --- Save bot ---
    bots.append(new_bot)
    save_bots(bots)

    # --- Return sanitized response ---
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


@app.post("/bots/{bot_id}/upload_file")
async def upload_file(bot_id: str, file: UploadFile = File(...)):
    content = await file.read()
    text = ""

    # Extract text depending on file type
    if file.filename.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(content))
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text()

    elif file.filename.endswith(".docx"):
        doc = docx.Document(io.BytesIO(content))
        for para in doc.paragraphs:
            text += para.text + "\n"

    elif file.filename.endswith(".txt"):
        text = content.decode("utf-8")

    else:
        raise HTTPException(400, "Unsupported file type. Use PDF, DOCX, or TXT.")

    # Reference the bot document in Firestore
    bot_ref = db.collection("bots").document(bot_id)
    bot_snapshot = bot_ref.get()
    if not bot_snapshot.exists:
        raise HTTPException(404, "Bot not found")

    # Append to file_data array in Firestore
    bot_ref.update({
        "file_data": firestore.ArrayUnion([{"name": file.filename, "text": text}])
    })

    return {"message": f"{file.filename} uploaded successfully", "text_length": len(text)}


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

    # 1️⃣ Get API key
    api_key = None
    if authorization and authorization.lower().startswith("bearer "):
        api_key = authorization.split(" ", 1)[1].strip()
    elif x_api_key:
        api_key = x_api_key.strip()
    elif req.bot_id:
        api_key = req.bot_id
    else:
        raise HTTPException(status_code=400, detail="Provide Authorization, x-api-key, or bot_id")

    # 2️⃣ Find bot
    bot = find_bot_by_api_key(api_key) or find_bot_by_id(api_key)
    if not bot:
        raise HTTPException(status_code=401, detail="Invalid API key or bot_id")

    # 3️⃣ Configure Gemini
    genai.configure(api_key=GEMINI_API_KEY)

    # 4️⃣ Gather all context
    name = bot.get("name", "Bot")
    personality = bot.get("personality", "")
    scraped_text = bot.get("scraped_text", "")

    # Include uploaded files
    file_texts = []
    bot_doc = db.collection("bots").document(bot["id"]).get()
    if bot_doc.exists:
        data = bot_doc.to_dict()
        for f in data.get("file_data", []):
            text = f.get("text", "")
            if text.strip() and text != "-":
                file_texts.append(text)

    # Combine everything for RAG
    rag_context = "\n".join([scraped_text] + file_texts)

    # 5️⃣ Build prompt
    prompt = (
        f"You are '{name}'. Personality: {personality}\n"
        f"Here is information from the website and uploaded files (if available):\n{rag_context}\n"
        f"Only answer based on this content. User: {req.message}"
    )

    # 6️⃣ Generate response
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
