from fastapi import APIRouter, HTTPException
from backend.storage import BotStorage

router = APIRouter(tags=["Bots"])
storage = BotStorage()

@router.delete("/bots/{bot_id}", summary="Delete a bot by ID")
async def delete_bot(bot_id: str):
    success = storage.delete_bot(bot_id)
    if not success:
        raise HTTPException(status_code=404, detail="Bot not found")
    return {"message": "Bot deleted successfully"}
