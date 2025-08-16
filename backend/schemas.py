from pydantic import BaseModel

class BotCreateRequest(BaseModel):
    name: str
    personality: str | dict

class BotResponse(BaseModel):
    id: str
    name: str
    personality: str | dict

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str
