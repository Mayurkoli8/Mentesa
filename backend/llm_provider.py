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

    def chat(self, system: str, user: str, history=None) -> str:
        messages = [{"role": "system", "content": system}]
        for turn in (history or []):
            role = "assistant" if turn.get("role") in ("bot", "assistant") else "user"
            content = (turn.get("content") or "").strip()
            if content:
                messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": user})
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
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

    def chat(self, system: str, user: str, history=None) -> str:
        convo = ""
        for turn in (history or []):
            speaker = "Assistant" if turn.get("role") in ("bot", "assistant") else "User"
            content = (turn.get("content") or "").strip()
            if content:
                convo += f"{speaker}: {content}\n"
        prompt = f"{system}\n\n"
        if convo:
            prompt += f"Conversation so far:\n{convo}\n"
        prompt += f"User: {user}\nAssistant:"
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
def chat(system: str, user: str, context: Optional[str] = None, history=None) -> str:
    """Generate a conversational reply. `context` is optional RAG content;
    `history` is a list of prior {role, content} turns for conversation memory."""
    if context:
        system = (
            f"{system}\n\n"
            "Use the following knowledge base as your primary source for factual "
            "questions about the product, company, or documents. If a factual "
            "question isn't covered, say you don't have that information. "
            "Still pay attention to the ongoing conversation and what the user "
            "has told you, and respond naturally to chit-chat and follow-ups.\n\n"
            f"Knowledge base:\n{context}"
        )
    return _get_provider().chat(system, user, history=history)


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
