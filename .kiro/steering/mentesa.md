# Mentesa Project Conventions

Mentesa is a no-code AI chatbot platform. React (Vite) frontend, FastAPI backend,
Firebase/Firestore for data & auth, pluggable LLM (Groq default, Gemini fallback),
real RAG, Stripe subscriptions.

## Architecture
- `frontend-react/` — React 19 + Vite + Tailwind. Deploy: Vercel (root dir = `frontend-react`).
- `backend/` — FastAPI. Deploy: Render. Start: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`.
- `utils/` — shared Firebase init + scraper.

## Frontend conventions
- Theming uses CSS variables on `[data-theme]` (dark default, light alternative).
  ALWAYS use `var(--text-primary)`, `var(--bg-secondary)`, `var(--accent-cyan)`, etc.
  NEVER hardcode hex colors that won't adapt to light mode (e.g. `text-gray-400`, `#1a2332`).
- Use the `useToast()` hook for user feedback, not `alert()`.
- Use the `card`, `card-hover`, `stat-tile`, `brand-gradient`, `logo-mark` helper classes.
- API calls go through `src/utils/api.js` (auto-attaches `X-Session-Id`).
- Backend URL comes from `VITE_API_URL` env var.

## Backend conventions
- LLM access ONLY through `backend/llm_provider.py` (never import groq/genai directly in routes).
- RAG via `backend/rag.py` (chunk -> embed -> cosine retrieve), chunks cached per-bot in Firestore.
- Plan limits & usage metering via `backend/billing.py`; enforce on bot-create and `/chat`.
- Owner-only routes require a valid session (`X-Session-Id` header -> `require_session`).
- Embedded `/chat` requires a valid bot API key; raw `bot_id` is owner-test fallback only.
- Subscription plans defined in `backend/config.py` PLANS dict.

## Security
- Secrets live in `.env` (gitignored). Never commit keys.
- Keep CORS, rate limiting (`backend/ratelimit.py`), and ownership checks intact.

## Testing
- Verify backend with `python -c "from backend import main"` after changes.
- Verify frontend with `npm run build` in `frontend-react/`.
- For LLM-dependent tests locally, set `LLM_PROVIDER=gemini` (working key) and restore to `groq` after.
