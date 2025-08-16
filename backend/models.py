# backend/models.py
from pydantic import BaseModel
from typing import Optional, Dict, List

# Basic Bot model
class Bot(BaseModel):
    bot_id: str
    name: str
    personality: str
    settings: Optional[Dict] = {}

# Request model for creating a bot
class BotCreateRequest(BaseModel):
    name: str
    personality: str
    settings: Optional[Dict] = {}

# Response model for a single bot
class BotResponse(BaseModel):
    bot_id: str
    name: str
    personality: str
    settings: Optional[Dict] = {}

# Request model for chat messages
class ChatRequest(BaseModel):
    bot_id: str
    message: str

# Response model for chat messages
class ChatResponse(BaseModel):
    bot_id: str
    message: str

# Response model for listing multiple bots
class BotsListResponse(BaseModel):
    bots: List[BotResponse]
