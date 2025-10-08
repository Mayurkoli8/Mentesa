# utils/file_handle.py
from utils.firebase_config import db
from firebase_admin import firestore as fa_firestore
import uuid
import re
import io
from typing import Tuple

# -----------------------
# Text safety helpers
# -----------------------
def safe_text(text: str) -> str:
    """
    Make text safe for Firestore:
      - ensure str
      - remove lone surrogate codepoints (U+D800..U+DFFF)
      - encode/decode with 'replace' so no encoding errors remain
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

    # remove lone surrogate code units (these cause "surrogates not allowed")
    text = re.sub(r'[\uD800-\uDFFF]', '', text)
    safe = text.encode("utf-8", errors="replace").decode("utf-8")
    return safe

# -----------------------
# File (RAG) helpers
# -----------------------
def upload_file(bot_id: str, filename: str, content: str) -> str:
    """
    Safe Firestore update without transaction.
    """
    content = safe_text(content or "")
    if not content.strip():
        content = "-"

    bot_ref = db.collection("bots").document(bot_id)

    # Get existing bot data
    snap = bot_ref.get()
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

    # Update Firestore directly (no transaction)
    bot_ref.set({"file_data": file_list}, merge=True)
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
        from PyPDF2 import PdfReader
    except Exception:
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

# -----------------------
# URL helpers
# -----------------------
def scrape_and_add_url(bot_id: str, url: str, scraper_func=None) -> bool:
    """
    Scrape the URL (uses scraper_func if provided, otherwise tries to import utils.scraper.scrape_website).
    Saves scraped text into bots/{bot_id}.scraped_texts[url] and appends url to config.urls (deduped).
    Returns True on success.
    """
    if scraper_func is None:
        try:
            from utils.scraper import scrape_website as _scrape
        except Exception:
            raise RuntimeError("scraper not available")

        scraper_func = _scrape

    text = ""
    try:
        text = scraper_func(url)
    except Exception as e:
        raise RuntimeError(f"Scrape failed: {e}")

    text = safe_text(text or "-")

    bot_ref = db.collection("bots").document(bot_id)
    snap = bot_ref.get()
    data = snap.to_dict() if snap.exists else {}

    # update scraped_texts map
    scraped_texts = data.get("scraped_texts", {})
    scraped_texts[url] = text

    # update config.urls list (dedupe)
    config = data.get("config", {}) or {}
    urls = config.get("urls", [])
    if url not in urls:
        urls.append(url)
    config["urls"] = urls

    # Also update primary scraped_text (concatenate/append)
    primary_scraped = data.get("scraped_text", "") or ""
    # append new scraped content separated by newline if not already included
    if text and text != "-" and text not in primary_scraped:
        primary_scraped = (primary_scraped + "\n" + text).strip()

    bot_ref.update({
        "scraped_texts": scraped_texts,
        "config": config,
        "scraped_text": primary_scraped
    })
    return True

def delete_url(bot_id: str, url: str) -> bool:
    """
    Remove a URL from bot.scraped_texts and from bot.config.urls.
    Returns True on success.
    """
    bot_ref = db.collection("bots").document(bot_id)
    bot_doc = bot_ref.get()
    if not bot_doc.exists:
        return False

    data = bot_doc.to_dict() or {}
    scraped_texts = data.get("scraped_texts", {}) or {}
    if url in scraped_texts:
        scraped_texts.pop(url, None)

    # remove url from config.urls safely
    config = data.get("config", {}) or {}
    urls = config.get("urls", []) or []
    urls = [u for u in urls if u != url]
    config["urls"] = urls

    # Rebuild primary scraped_text from remaining scraped_texts map
    primary = []
    for v in scraped_texts.values():
        if v and v != "-":
            primary.append(v)
    primary_scraped = "\n".join(primary).strip()

    bot_ref.update({
        "scraped_texts": scraped_texts,
        "config": config,
        "scraped_text": primary_scraped
    })
    return True
