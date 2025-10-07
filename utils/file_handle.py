from firebase_admin import firestore
from PyPDF2 import PdfReader

db = firestore.client()

def safe_text(text: str) -> str:
    """Sanitize text to avoid Firestore UnicodeEncodeError."""
    return text.encode("utf-8", errors="replace").decode("utf-8")

def upload_file(bot_id, file, filename):
    # 1️⃣ Extract content
    content = ""
    if filename.lower().endswith(".pdf"):
        reader = PdfReader(file)
        content = "\n".join([page.extract_text() or "" for page in reader.pages])
    else:
        try:
            content = file.read().decode("utf-8")
        except UnicodeDecodeError:
            file.seek(0)
            content = file.read().decode("latin-1")
    
    # sanitize
    content = safe_text(content)
    if not content.strip():
        content = "-"

    # 2️⃣ Load bot
    bot_doc = db.collection("bots").document(bot_id)
    bot_snapshot = bot_doc.get()
    file_list = bot_snapshot.to_dict().get("file_data", []) if bot_snapshot.exists else []

    # 3️⃣ Remove old entry if exists
    file_list = [f for f in file_list if f["name"] != filename]

    # 4️⃣ Append new file
    file_list.append({"name": filename, "text": content})

    # 5️⃣ Update Firestore once
    bot_doc.update({"file_data": file_list})

    return filename


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
