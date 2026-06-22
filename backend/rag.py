# backend/rag.py
"""
Lightweight RAG for Mentesa.

Knowledge (scraped pages + uploaded files) is split into chunks, embedded,
and stored in Firestore under each bot. At query time we embed the user's
question and rank chunks by cosine similarity, returning the top-k as context.

This keeps everything inside Firestore (no separate vector DB) while still
giving real retrieval instead of dumping all text into the prompt.
"""
from __future__ import annotations
import math
import hashlib
from typing import List, Dict, Any

from backend import config

CHUNK_SIZE = 1000      # characters per chunk
CHUNK_OVERLAP = 150
TOP_K = 5
MAX_CONTEXT_CHARS = 6000


# -------------------------------------------------
# Chunking
# -------------------------------------------------
def chunk_text(text: str) -> List[str]:
    text = (text or "").strip()
    if not text:
        return []
    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + CHUNK_SIZE, n)
        chunks.append(text[start:end])
        if end >= n:
            break
        start = end - CHUNK_OVERLAP
    return chunks


# -------------------------------------------------
# Embeddings
# -------------------------------------------------
def _hash_embed(text: str, dims: int = 256) -> List[float]:
    """Deterministic fallback embedding (bag-of-hashed-tokens).

    Not as good as a real model but keeps RAG functional with zero
    external dependencies / cost when EMBED_PROVIDER=hash.
    """
    vec = [0.0] * dims
    for token in text.lower().split():
        h = int(hashlib.md5(token.encode()).hexdigest(), 16)
        vec[h % dims] += 1.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def embed_texts(texts: List[str]) -> List[List[float]]:
    if not texts:
        return []
    if config.EMBED_PROVIDER == "gemini" and config.GEMINI_API_KEY:
        try:
            import google.generativeai as genai

            genai.configure(api_key=config.GEMINI_API_KEY)
            out = []
            for t in texts:
                r = genai.embed_content(model=config.EMBED_MODEL, content=t)
                out.append(r["embedding"])
            return out
        except Exception as e:
            print(f"[RAG] Gemini embedding failed, falling back to hash: {e}")
    return [_hash_embed(t) for t in texts]


def embed_query(text: str) -> List[float]:
    return embed_texts([text])[0]


# -------------------------------------------------
# Similarity
# -------------------------------------------------
def cosine(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (na * nb)


# -------------------------------------------------
# Build index from raw sources
# -------------------------------------------------
def build_chunks(sources: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    sources: list of {"name": str, "text": str}
    returns: list of {"source": str, "text": str, "embedding": [float]}
    """
    all_chunks: List[Dict[str, Any]] = []
    pending_texts: List[str] = []
    meta: List[str] = []
    for src in sources:
        name = src.get("name", "source")
        for ch in chunk_text(src.get("text", "")):
            pending_texts.append(ch)
            meta.append(name)
    if not pending_texts:
        return []
    embeddings = embed_texts(pending_texts)
    for text, name, emb in zip(pending_texts, meta, embeddings):
        all_chunks.append({"source": name, "text": text, "embedding": emb})
    return all_chunks


# -------------------------------------------------
# Retrieve
# -------------------------------------------------
def retrieve(query: str, chunks: List[Dict[str, Any]], top_k: int = TOP_K) -> str:
    """Return concatenated top-k chunk texts most relevant to the query."""
    if not chunks:
        return ""
    q_emb = embed_query(query)
    scored = []
    for c in chunks:
        emb = c.get("embedding")
        if emb:
            scored.append((cosine(q_emb, emb), c["text"]))
    scored.sort(key=lambda x: x[0], reverse=True)

    selected, total = [], 0
    for _, text in scored[:top_k]:
        if total + len(text) > MAX_CONTEXT_CHARS:
            text = text[: MAX_CONTEXT_CHARS - total]
        selected.append(text)
        total += len(text)
        if total >= MAX_CONTEXT_CHARS:
            break
    return "\n---\n".join(selected)
