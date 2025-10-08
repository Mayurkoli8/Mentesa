# utils/file_handle.py
from utils.firebase_config import db
from firebase_admin import firestore as fa_firestore
import uuid
import re
import io
from typing import Tuple

def safe_text(text: str) -> str:
    """
    Make text safe for Firestore:
    - ensure str type
    - remove lone surrogate codepoints U+D800..U+DFFF
    - encode with 'replace' to avoid encoding errors
    """
    if text is None:
        return ""
    if not isinstance(text, str):
        try:
            text = text.decode("utf-8")
        except Exception:
            try:
                text = text.decode("latin-1")
            except Exception:
                text = str(text)

    # remove lone surrogate code units
    text = re.sub(r'[\uD800-\uDFFF]', '', text)
    safe = text.encode("utf-8", errors="replace").decode("utf-8")
    return safe

def upload_file(bot_id: str, filename: str, content: str) -> str:
    """
    Atomically store (or replace) a single file entry in bots/{bot_id}.file_data.
    content should be a plain text string. This function sanitizes it again.
    """
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

        # Append a single sanitized entry
        file_list.append({
            "id": str(uuid.uuid4()),
            "name": filename,
            "text": content,
            "uploaded_at": fa_firestore.SERVER_TIMESTAMP
        })

        if snap.exists:
            transaction.update(bot_ref, {"file_data": file_list})
        else:
            transaction.set(bot_ref, {"file_data": file_list}, merge=True)

    db.run_transaction(txn_update)
    return filename

def delete_file(bot_id: str, filename: str) -> bool:
    """Delete a file entry by filename from bots/{bot_id}.file_data"""
    bot_ref = db.collection("bots").document(bot_id)
    snap = bot_ref.get()
    if not snap.exists:
        return False
    file_list = snap.to_dict().get("file_data", []) or []
    new_list = [f for f in file_list if f.get("name") != filename]
    bot_ref.update({"file_data": new_list})
    return True

def dedupe_files(bot_id: str) -> Tuple[int, int]:
    """
    Deduplicate file_data entries for a bot.
    Keeps the longest non-empty text per filename.
    Returns (original_count, deduped_count).
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
            cur = best[name].get("text", "") or ""
            # prefer longer or non-sentinel
            if (cur == "-" and text != "-") or (len(text) > len(cur)):
                best[name] = f
    new_list = list(best.values())
    bot_ref.update({"file_data": new_list})
    return (len(file_list), len(new_list))

def salvage_pdf_entries(bot_id: str) -> dict:
    """
    Try to recover entries that accidentally contain raw PDF bytes stored as text.
    Returns {'checked': n, 'fixed': m}.
    """
    try:
        from PyPDF2 import PdfReader  # local import
    except Exception:
        # PyPDF2 not installed or import failed
        return {"checked": 0, "fixed": 0}

    bot_ref = db.collection("bots").document(bot_id)
    snap = bot_ref.get()
    if not snap.exists:
        return {"checked": 0, "fixed": 0}
    file_list = snap.to_dict().get("file_data", []) or []
    fixed = 0
    new_list = []
    for f in file_list:
        name = f.get("name")
        text = f.get("text", "") or ""
        if isinstance(text, str) and text.startswith("%PDF-"):
            try:
                pdf_bytes = text.encode("latin-1")
                reader = PdfReader(io.BytesIO(pdf_bytes))
                extracted = "\n".join([p.extract_text() or "" for p in reader.pages]).strip()
                if extracted:
                    f["text"] = safe_text(extracted)
                    fixed += 1
                else:
                    f["text"] = "-"
            except Exception:
                f["text"] = "-"
        new_list.append(f)
    if new_list != file_list:
        bot_ref.update({"file_data": new_list})
    return {"checked": len(file_list), "fixed": fixed}

# URL

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
