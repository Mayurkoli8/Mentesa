# backend/config.py
"""
Central configuration for Mentesa.
Holds environment settings, subscription plan definitions, and shared constants.
"""
from __future__ import annotations
import os
from dotenv import load_dotenv

load_dotenv()

# -------------------------------------------------
# Environment
# -------------------------------------------------
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
SESSION_TTL_DAYS = int(os.getenv("SESSION_TTL_DAYS", "30"))

# LLM
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()  # groq | gemini
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Embeddings (used for RAG). Gemini's embedding API is free and avoids
# loading a heavy local model on small deployment instances.
EMBED_PROVIDER = os.getenv("EMBED_PROVIDER", "gemini").lower()  # gemini | hash
EMBED_MODEL = os.getenv("EMBED_MODEL", "models/gemini-embedding-001")

# Firebase
FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")

# Dodo Payments (Merchant of Record)
DODO_API_KEY = os.getenv("DODO_PAYMENTS_API_KEY")
DODO_WEBHOOK_KEY = os.getenv("DODO_PAYMENTS_WEBHOOK_KEY")
DODO_ENVIRONMENT = os.getenv("DODO_PAYMENTS_ENVIRONMENT", "test_mode")  # test_mode | live_mode
DODO_PRODUCT_PRO = os.getenv("DODO_PRODUCT_PRO")
DODO_PRODUCT_BUSINESS = os.getenv("DODO_PRODUCT_BUSINESS")

# -------------------------------------------------
# Subscription plans
# -------------------------------------------------
# message_limit: messages allowed per billing month (per user, across all bots)
# bot_limit: max number of bots a user can own (None = unlimited)
# branding: whether the "Powered by Mentesa" footer is forced on embeds
PLANS = {
    "free": {
        "name": "Free",
        "price_usd": 0,
        "bot_limit": 1,
        "message_limit": 100,
        "branding": True,
        "product_id": None,
    },
    "pro": {
        "name": "Pro",
        "price_usd": 4.99,
        "bot_limit": 10,
        "message_limit": 5000,
        "branding": False,
        "product_id": DODO_PRODUCT_PRO,
    },
    "business": {
        "name": "Business",
        "price_usd": 9.99,
        "bot_limit": None,  # unlimited
        "message_limit": 50000,
        "branding": False,
        "product_id": DODO_PRODUCT_BUSINESS,
    },
}

DEFAULT_PLAN = "free"


def get_plan(plan_id: str | None) -> dict:
    """Return plan definition, falling back to free for unknown ids."""
    return PLANS.get((plan_id or DEFAULT_PLAN).lower(), PLANS[DEFAULT_PLAN])


def plan_id_from_product(product_id: str | None) -> str:
    """Map a Dodo product id back to our internal plan id."""
    for pid, plan in PLANS.items():
        if plan.get("product_id") and plan["product_id"] == product_id:
            return pid
    return DEFAULT_PLAN
