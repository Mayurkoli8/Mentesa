import os
import json
import uuid
from datetime import datetime

# Data storage path
BOTS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "data/bots.json")
os.makedirs(os.path.dirname(BOTS_FILE), exist_ok=True)

# --- Internal helpers ---
def _load_bots():
    if not os.path.exists(BOTS_FILE):
        return {}
    with open(BOTS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def _save_bots(bots_data):
    with open(BOTS_FILE, "w", encoding="utf-8") as f:
        json.dump(bots_data, f, indent=2, ensure_ascii=False)

# --- Public functions ---
def create_bot(name, personality="", config=None):
    """Create a new bot and return its ID."""
    bots = _load_bots()
    bot_id = str(uuid.uuid4())

    bots[bot_id] = {
        "id": bot_id,
        "name": name,
        "personality": personality,
        "config": config or {},
        "created_at": datetime.utcnow().isoformat()
    }

    _save_bots(bots)
    return bot_id

def get_bot(bot_id):
    """Return a bot's data or None."""
    bots = _load_bots()
    return bots.get(bot_id)

def list_bots():
    """Return a list of all bots."""
    bots = _load_bots()
    return list(bots.values())

def delete_bot(bot_id):
    """Delete a bot. Return True if deleted, False if not found."""
    bots = _load_bots()
    if bot_id in bots:
        del bots[bot_id]
        _save_bots(bots)
        return True
    return False
