from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

app = FastAPI(title="Mentesa Backend V2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}

# Import routers
from backend.routes import create_bot, list_bots, delete_bot, chat

app.include_router(create_bot.router)
app.include_router(list_bots.router)
app.include_router(delete_bot.router)
app.include_router(chat.router)
