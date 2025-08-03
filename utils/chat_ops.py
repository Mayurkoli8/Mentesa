import os
import json

CHATS_FOLDER = "data/chats"

def get_chat_file_path(bot_id):
    os.makedirs(CHATS_FOLDER, exist_ok=True)
    return os.path.join(CHATS_FOLDER, f"{bot_id}.json")

def load_chat_history(bot_id):
    path = get_chat_file_path(bot_id)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []

def save_chat_history(bot_id, history):
    path = get_chat_file_path(bot_id)
    with open(path, "w") as f:
        json.dump(history, f, indent=2)
        
def clear_chat_history(bot_id):
    path = get_chat_file_path(bot_id)
    if os.path.exists(path):
        os.remove(path)

