# bot_ops.py
from firebase_admin import firestore
import uuid

db = firestore.client()

def upload_file(bot_id, file, filename):
    """
    Stores uploaded file content directly in Firestore under bot's file_data.
    """
    # Read content safely
    try:
        content = file.read().decode("utf-8")
    except UnicodeDecodeError:
        content = file.read().decode("latin-1")

    bot_doc = db.collection("bots").document(bot_id)
    bot_snapshot = bot_doc.get()

    if bot_snapshot.exists:
        file_list = bot_snapshot.to_dict().get("file_data", [])
    else:
        file_list = []

    # Append new file
    file_list.append({
        "name": filename,
        "text": content
    })

    # Update Firestore
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
