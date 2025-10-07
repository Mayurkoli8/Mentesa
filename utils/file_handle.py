# utils/file_handle.py
from utils.firebase_config import db
from firebase_admin import firestore as fa_firestore
import uuid
import io
from typing import Optional

def safe_text(text: str) -> str:
    return text.encode("utf-8", errors="replace").decode("utf-8")

def upload_file(bot_id: str, filename: str, content: str) -> str:
    """
    Store (or replace) a single file entry in bots/{bot_id}.file_data atomically.
    - filename: name of uploaded file
    - content: extracted text (string)
    """
    # sanitize & normalize
    content = safe_text(content or "")
    if not content.strip():
        content = "-"  # sentinel for "no usable text"

    bot_ref = db.collection("bots").document(bot_id)

    def txn_update(transaction):
        snap = bot_ref.get(transaction=transaction)
        data = snap.to_dict() or {}
        file_list = data.get("file_data", []) if data else []

        # Remove any existing entries with same filename
        file_list = [f for f in file_list if f.get("name") != filename]

        # Append a single entry
        file_list.append({
            "id": str(uuid.uuid4()),
            "name": filename,
            "text": content,
            "uploaded_at": fa_firestore.SERVER_TIMESTAMP
        })

        # Use update for existing doc, or set if missing
        if snap.exists:
            transaction.update(bot_ref, {"file_data": file_list})
        else:
            transaction.set(bot_ref, {"file_data": file_list}, merge=True)

    db.run_transaction(txn_update)
    return filename

def delete_file(bot_id: str, filename: str) -> bool:
    bot_ref = db.collection("bots").document(bot_id)
    snap = bot_ref.get()
    if not snap.exists:
        return False
    file_list = snap.to_dict().get("file_data", []) or []
    new_list = [f for f in file_list if f.get("name") != filename]
    bot_ref.update({"file_data": new_list})
    return True

def delete_url(bot_id: str, url: str):
    bot_ref = db.collection("bots").document(bot_id)
    bot_doc = bot_ref.get()
    if not bot_doc.exists:
        raise ValueError("Bot not found")

    # Remove URL from scraped_texts
    current_scraped_texts = bot_doc.to_dict().get("scraped_texts", {})
    if url in current_scraped_texts:
        current_scraped_texts.pop(url)

    # Remove URL from config
    bot_ref.update({
        "scraped_texts": current_scraped_texts,
        "config.urls": firestore.ArrayRemove([url])
    })
