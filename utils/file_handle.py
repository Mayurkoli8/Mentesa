# bot_ops.py
from firebase_admin import firestore
import uuid

db = firestore.client()

def upload_file(bot_id, file_obj, filename):
    unique_name = f"{bot_id}/{uuid.uuid4()}_{filename}"
    blob = bucket.blob(unique_name)
    blob.upload_from_file(file_obj)
    blob.make_public()
    file_url = blob.public_url

    bot_ref = db.collection("bots").document(bot_id)
    bot_ref.update({
        "config.files": firestore.ArrayUnion([file_url])
    })

    return file_url

def add_bot_url(bot_id: str, url: str):
    bot_ref = db.collection("bots").document(bot_id)
    bot_doc = bot_ref.get()
    if not bot_doc.exists:
        raise ValueError("Bot not found")

    bot_data = bot_doc.to_dict()

    # 1️⃣ Scrape the new URL
    from utils.scraper import scrape_website  # your existing scraper
    new_content = scrape_website(url)

    # 2️⃣ Append scraped content to existing scraped_text
    existing_scraped = bot_data.get("scraped_text", "")
    updated_scraped = existing_scraped + "\n\n" + new_content

    # 3️⃣ Update Firestore
    bot_ref.update({
        "scraped_text": updated_scraped,
        "config.urls": firestore.ArrayUnion([url])
    })

