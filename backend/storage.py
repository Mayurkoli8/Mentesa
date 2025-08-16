import os
import json
import threading
import uuid
from typing import Optional, List, Dict, Any

# File location
BOTS_FILE = os.path.join(os.path.dirname(__file__), "../data/bots.json")
LOCK = threading.Lock()


class BotStorage:
    """Thread-safe JSON-based bot storage."""

    def __init__(self, file_path: str = BOTS_FILE):
        self.file_path = file_path
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            self._write_file({})  # initialize with empty dict

    # ---------------- Internal helpers ----------------
    def _read_file(self) -> Dict[str, Any]:
        with LOCK:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)

    def _write_file(self, data: Dict[str, Any]):
        with LOCK:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

    # ---------------- CRUD methods ----------------
    def create_bot(self, name: str, personality: str | dict = "Neutral") -> dict:
        bots = self._read_file()
        bot_id = str(uuid.uuid4())
        bot = {
            "id": bot_id,
            "name": name,
            "personality": personality,
            "settings": {}
        }
        bots[bot_id] = bot
        self._write_file(bots)
        return bot

    def list_bots(self) -> List[dict]:
        """Return all bots as a list of dicts"""
        data = self._read_file()

        # If file is mistakenly a list, just return it
        if isinstance(data, list):
            return data

        # Otherwise, assume dict
        return list(data.values())

    def get_bot(self, bot_id: str) -> dict | None:
        data = self._read_file()
    
        if isinstance(data, list):
            # Search in list
            for bot in data:
                if bot["id"] == bot_id:
                    return bot
            return None
    
        if isinstance(data, dict):
            return data.get(bot_id)
    
        return None
    
    def update_bot(self, bot_id: str, updates: Dict[str, Any]) -> Optional[dict]:
        bots = self._read_file()
        bot = bots.get(bot_id)
        if not bot:
            return None
        bot.update(updates)
        bots[bot_id] = bot
        self._write_file(bots)
        return bot

    def delete_bot(self, bot_id: str) -> bool:
        bots = self._read_file()
        if bot_id in bots:
            del bots[bot_id]
            self._write_file(bots)
            return True
        return False
