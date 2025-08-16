from fastapi import APIRouter
from backend.schemas import BotResponse
from backend.storage import BotStorage

router = APIRouter(tags=["Bots"])
storage = BotStorage()

@router.get("/bots/", response_model=list[BotResponse], summary="List all bots")
async def list_bots():
    return storage.list_bots()
