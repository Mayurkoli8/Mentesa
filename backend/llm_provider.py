# backend/llm_provider.py
"""
LLM provider abstraction.

Exposes two functions used across the app:
  - chat(system, user, context) -> str      : conversational reply
  - generate_json(prompt) -> dict           : structured bot-config generation

Provider is selected via LLM_PROVIDER env var (groq | gemini).
Swapping providers requires no code changes elsewhere.
"""
from __future__ import annotations
import json
import re
from typing import Optional

from backend import config


# -------------------------------------------------
# Helpers
# -------------------------------------------------
def _extract_json(text: str) -> dict:
    """Pull the first JSON object out of an LLM response."""
    if not text:
        raise ValueError("Empty LLM response")
    cleaned = text.strip()
    # strip markdown fences
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```[a-zA-Z]*", "", cleaned).strip().strip("`").strip()
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON object found in response: {text[:200]}")
    return json.loads(match.group(0))


# -------------------------------------------------
# Groq backend (OpenAI-compatible)
# -------------------------------------------------
class _GroqProvider:
    def __init__(self):
        from groq import Groq

        if not config.GROQ_API_KEY:
            raise RuntimeError("GROQ_API_KEY not set")
        self.client = Groq(api_key=config.GROQ_API_KEY)
        self.model = config.GROQ_MODEL

    def chat(self, system: str, user: str) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.7,
        )
        return (resp.choices[0].message.content or "").strip()

    def generate_json(self, prompt: str) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You output only valid minified JSON. No markdown, no prose.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
            response_format={"type": "json_object"},
        )
        return (resp.choices[0].message.content or "").strip()


# -------------------------------------------------
# Gemini backend
# -------------------------------------------------
class _GeminiProvider:
    def __init__(self):
        import google.generativeai as genai

        if not config.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY not set")
        genai.configure(api_key=config.GEMINI_API_KEY)
        self._genai = genai
        self.model = genai.GenerativeModel(config.GEMINI_MODEL)

    def _text(self, response) -> str:
        try:
            if getattr(response, "text", None):
                return response.text.strip()
        except Exception:
            pass
        try:
            parts = response.candidates[0].content.parts
            return " ".join(p.text for p in parts if hasattr(p, "text")).strip()
        except Exception:
            return ""

    def chat(self, system: str, user: str) -> str:
        prompt = f"{system}\n\n{user}"
        return self._text(self.model.generate_content(prompt))

    def generate_json(self, prompt: str) -> str:
        instruction = (
            "Respond ONLY with a single valid JSON object. "
            "No markdown fences, no explanation.\n\n" + prompt
        )
        return self._text(self.model.generate_content(instruction))


# -------------------------------------------------
# Singleton selection
# -------------------------------------------------
_provider = None


def _get_provider():
    global _provider
    if _provider is None:
        if config.LLM_PROVIDER == "gemini":
            _provider = _GeminiProvider()
        else:
            _provider = _GroqProvider()
    return _provider


# -------------------------------------------------
# Public API
# -------------------------------------------------
def chat(system: str, user: str, context: Optional[str] = None) -> str:
    """Generate a conversational reply. `context` is optional RAG content."""
    if context:
        system = f"{system}\n\nUse ONLY the following knowledge to answer. " \
                 f"If the answer isn't here, say you don't have that information.\n\n{context}"
    return _get_provider().chat(system, user)


def generate_bot_config(description: str, site_text: str = "") -> dict:
    """Ask the LLM to design a bot (name, personality) from a description."""
    if site_text.strip():
        prompt = (
            f'Create a chatbot from this description: "{description}"\n\n'
            f"Website content:\n{site_text[:8000]}\n\n"
            "Use both the description and website content. Do not invent facts. "
            'Return JSON: {"name": string, "personality": string, "settings": {}}'
        )
    else:
        prompt = (
            f'Create a chatbot from this description: "{description}"\n'
            "Use only the description. Do not invent facts. "
            'Return JSON: {"name": string, "personality": string, "settings": {}}'
        )
    raw = _get_provider().generate_json(prompt)
    cfg = _extract_json(raw)
    if "name" not in cfg or "personality" not in cfg:
        raise ValueError(f"Missing keys in generated config: {cfg}")
    cfg.setdefault("settings", {})
    return cfg
