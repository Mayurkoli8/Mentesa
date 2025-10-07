# utils/file_handle.py
from utils.firebase_config import db
from firebase_admin import firestore as fa_firestore
import uuid

def safe_text(text: str) -> str:
    """Sanitize text so Firestore won't error on encoding."""
    return text.encode("utf-8", errors="replace").decode("utf-8")

def upload_file(bot_id: str, filename: str, content: str) -> str:
    """
    Store (or replace) a single file entry in bots/{bot_id}.file_data atomically.
    - filename: string name
    - content: full text (already extracted)
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

        transaction.update(bot_ref, {"file_data": file_list})

    db.run_transaction(txn_update)
    return filename

def delete_file(bot_id: str, filename: str):
    """Delete file entry by filename."""
    bot_ref = db.collection("bots").document(bot_id)
    snap = bot_ref.get()
    if not snap.exists:
        return False
    file_list = snap.to_dict().get("file_data", []) or []
    new_list = [f for f in file_list if f.get("name") != filename]
    bot_ref.update({"file_data": new_list})
    return True

def dedupe_files(bot_id: str) -> tuple:
    """
    Clean existing file_data by keeping only one entry per filename.
    Preference: keep the longest non-empty text.
    Returns (original_count, deduped_count)
    """
    bot_ref = db.collection("bots").document(bot_id)
    snap = bot_ref.get()
    if not snap.exists:
        return (0, 0)
    file_list = snap.to_dict().get("file_data", []) or []
    best = {}
    for f in file_list:
        name = f.get("name")
        text = f.get("text", "") or ""
        if name not in best:
            best[name] = f
        else:
            # choose one with longer text or non "-" sentinel
            cur = best[name].get("text", "") or ""
            if (cur == "-" and text != "-") or (len(text) > len(cur)):
                best[name] = f
    new_list = list(best.values())
    bot_ref.update({"file_data": new_list})
    return (len(file_list), len(new_list))



def scrape_and_add_url(bot_id: str, url: str):
    bot_ref = db.collection("bots").document(bot_id)
    bot_doc = bot_ref.get()
    if not bot_doc.exists:
        raise ValueError("Bot not found")

    # Scrape new URL
    from utils.scraper import scrape_website
    new_content = scrape_website(url)

    # Fetch current scraped_texts from Firestore
    current_scraped_texts = bot_doc.to_dict().get("scraped_texts", {})

    # Add new URL content
    current_scraped_texts[url] = new_content

    # Update Firestore
    bot_ref.update({
        "scraped_texts": current_scraped_texts,
        "config.urls": firestore.ArrayUnion([url])
    })

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
