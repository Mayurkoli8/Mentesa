from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.storage import BotStorage
from utils.llm import chat_with_llm
import json, os

router = APIRouter(prefix="/bots", tags=["chat"])
storage = BotStorage()

CHAT_DIR = "data/chats"
os.makedirs(CHAT_DIR, exist_ok=True)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

# ✅ Load old chat
@router.get("/{bot_id}/chat")
async def get_chat(bot_id: str):
    chat_file = os.path.join(CHAT_DIR, f"{bot_id}.json")
    if os.path.exists(chat_file):
        with open(chat_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# ✅ Send message
@router.post("/{bot_id}/chat", response_model=ChatResponse)
async def chat(bot_id: str, request: ChatRequest):
    bot = storage.get_bot(bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")

    reply = chat_with_llm(bot, request.message)
    if not reply or reply.startswith("[Chat Error]"):
        raise HTTPException(status_code=500, detail=reply)

    # Save to chat file
    chat_file = os.path.join(CHAT_DIR, f"{bot_id}.json")
    if os.path.exists(chat_file):
        with open(chat_file, "r", encoding="utf-8") as f:
            chat_history = json.load(f)
    else:
        chat_history = []

    chat_history.append({"user": request.message, "bot": reply})

    with open(chat_file, "w", encoding="utf-8") as f:
        json.dump(chat_history, f, indent=2, ensure_ascii=False)

    return {"reply": reply}
