from fastapi import APIRouter
from backend.schemas import BotCreateRequest, BotResponse
from backend.storage import BotStorage
import uuid

router = APIRouter(tags=["Bots"])
storage = BotStorage()

@router.post("/bots/", response_model=BotResponse, summary="Create a new bot")
async def create_bot(request: BotCreateRequest):
    bot_id = str(uuid.uuid4())
    bot = {
        "id": bot_id,
        "name": request.name,
        "personality": request.personality,
    }
    storage.save_bot(bot_id, bot)
    return bot
