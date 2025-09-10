import json
import os
import requests

# Path to the bots JSON store
BOTS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "bots.json")


def load_bots():
    """Load all bots from the JSON store."""
    if not os.path.exists(BOTS_FILE):
        return {}
    with open(BOTS_FILE, "r") as f:
        return json.load(f)


def save_bots(data):
    """Save the bots dictionary to the JSON store."""
    os.makedirs(os.path.dirname(BOTS_FILE), exist_ok=True)
    with open(BOTS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def delete_bot(bot_id: str):
    """Remove a bot entry and its associated chat history file."""
    # Remove from bots.json
    bots = load_bots()
    if bot_id in bots:
        del bots[bot_id]
        save_bots(bots)

    # Remove chat history file
    from utils.chat_ops import get_chat_file_path
    chat_file = get_chat_file_path(bot_id)
    if os.path.exists(chat_file):
        os.remove(chat_file)


def rename_bot(bot_id: str, new_name: str):
    """Rename an existing bot."""
    bots = load_bots()
    if bot_id in bots:
        bots[bot_id]["name"] = new_name
        save_bots(bots)


def update_personality(bot_id: str, new_personality):
    """Update the personality text of an existing bot."""
    bots = load_bots()
    if bot_id in bots:
        bots[bot_id]["personality"] = new_personality
        save_bots(bots)

