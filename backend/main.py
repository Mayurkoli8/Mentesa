import json
import os
import uuid
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ====== CONFIG ======
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"  # Replace with your actual key securely
genai.configure(api_key=GEMINI_API_KEY)

# ====== FILE & DATA ======
BOTS_FILE = "bots.json"
bots = []

def load_bots():
    global bots
    if os.path.exists(BOTS_FILE):
        with open(BOTS_FILE, "r") as f:
            bots = json.load(f)
    else:
        bots = []

def save_bots():
    with open(BOTS_FILE, "w") as f:
        json.dump(bots, f, indent=2)

load_bots()

# ====== FASTAPI APP ======
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====== Pydantic models ======
class BotCreate(BaseModel):
    name: str
    description: str = "No description provided."

class ChatRequest(BaseModel):
    bot_id: str
    message: str

# ====== ROUTES ======

@app.get("/bots")
def get_bots():
    return bots

@app.post("/bots")
def create_bot(bot: BotCreate):
    bot_id = str(uuid.uuid4())
    new_bot = {
        "id": bot_id,
        "name": bot.name,
        "description": bot.description,
    }
    bots.append(new_bot)
    save_bots()
    return new_bot

@app.delete("/bots/{bot_id}")
def delete_bot(bot_id: str):
    global bots
    bots = [b for b in bots if b["id"] != bot_id]
    save_bots()
    return {"message": "Bot deleted"}

@app.post("/chat")
def chat_with_bot(req: ChatRequest):
    bot = next((b for b in bots if b["id"] == req.bot_id), None)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")

    try:
        model = genai.GenerativeModel("gemini-2.5-pro")
        response = model.generate_content(req.message)
        print("Gemini API response:", response)

        if response.candidates and response.candidates[0].content.parts:
            reply_text = response.candidates[0].content.parts[0].text
        else:
            reply_text = "I couldn't generate a reply."

        return {"reply": reply_text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
