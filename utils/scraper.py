# utils/scraper.py
import requests
from bs4 import BeautifulSoup
from readability import Document  # pip install readability-lxml

def scrape_website(url: str, max_chars: int = 15000) -> str:
    headers = {"User-Agent": "MentesaBot/1.0"}
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    text = "\n".join(soup.stripped_strings)
    return text[:max_chars]
