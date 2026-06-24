# Mentesa — No-Code AI Chatbot Platform

Mentesa lets anyone build a custom AI chatbot from a plain-language description,
feed it knowledge (websites + documents), and embed it on any website with a
single `<script>` tag. This is the **mentesa-final** rebuild: React frontend,
FastAPI backend, pluggable LLMs, real RAG, rate limiting, and Dodo Payments subscriptions.

## Architecture

```
frontend-react/   React + Vite + Tailwind  (deploy: Vercel)
backend/          FastAPI app              (deploy: Render)
  config.py         env + subscription plan definitions
  llm_provider.py   provider abstraction (Groq | Gemini)
  rag.py            chunking, embeddings, cosine retrieval
  billing.py        subscription state + monthly usage metering (Firestore)
  payment_service.py Dodo Payments checkout + webhook sync
  ratelimit.py      in-memory sliding-window limiter
  main.py           API routes
utils/            Firebase init, scraper, file helpers
data/             local scratch (bots mirror lives in Firestore)
```

### Tech stack
- **Frontend:** React 19, Vite, Tailwind CSS, React Router, Axios
- **Backend:** FastAPI, Uvicorn
- **LLM:** Groq (default, `llama-3.3-70b-versatile`) or Gemini — swap with one env var
- **Embeddings / RAG:** Gemini `gemini-embedding-001` (hash fallback if unavailable)
- **Data / Auth:** Firebase Auth + Firestore
- **Payments:** Dodo Payments (Merchant of Record — Checkout + Customer Portal + webhooks)

## Subscription plans

| Plan     | Price   | Bots      | Messages/mo | Branding |
|----------|---------|-----------|-------------|----------|
| Free     | $0      | 1         | 100         | Yes      |
| Pro      | $19/mo  | 10        | 5,000       | No       |
| Business | $49/mo  | Unlimited | 50,000      | No       |

Limits are enforced on bot creation and on every `/chat` call. Usage is metered
per user per calendar month in Firestore (`usage/{uid}_{YYYYMM}`).

## Local setup

### Backend
```bash
pip install -r requirements.txt
cp .env.example .env        # fill in your keys
uvicorn backend.main:app --reload
```

Required env vars (see `.env.example`):
- `GROQ_API_KEY` (or set `LLM_PROVIDER=gemini` to use `GEMINI_API_KEY`)
- `GEMINI_API_KEY` — used for RAG embeddings
- `FIREBASE_API_KEY`, `SERVICE_ACCOUNT_JSON_B64`
- Dodo Payments keys (optional locally; billing endpoints return 503 until set)

### Frontend
```bash
cd frontend-react
npm install
cp .env.example .env        # set VITE_API_URL if backend isn't on :8000
npm run dev
```

## Deployment

- **Backend → Render:** `render.yaml` blueprint included. Set the secret env
  vars in the dashboard. Health check is `/`.
- **Frontend → Vercel:** `vercel.json` included. Set `VITE_API_URL` to your
  Render backend URL.
- **Dodo webhook:** point it at `https://<backend>/billing/webhook` and set
  `DODO_PAYMENTS_WEBHOOK_KEY`. Subscribe to `subscription.active`,
  `subscription.renewed`, `subscription.on_hold`, `subscription.cancelled`,
  and `subscription.plan_changed` events.

## Embedding a bot

From a bot's **Manage** page, copy the snippet:
```html
<script src="https://<backend>/static/embed.js"
  data-api-key="mentesa_sk_..."
  data-bot-name="My Bot"
  data-backend-url="https://<backend>"></script>
```
The "Powered by Mentesa" footer is hidden automatically for Pro/Business bots.

## Security notes
- `/chat` requires a valid bot **API key** for embedded widgets; raw `bot_id` is
  only accepted as a fallback for the owner's in-app test chat.
- Bot create/delete, key rotation, file upload, and billing all require a valid
  session (`X-Session-Id` header).
- Per-key/IP sliding-window rate limiting protects `/chat` from bursts.
- Secrets (`.env`, `secrets.toml`) are gitignored. **Rotate any keys that were
  previously committed before going to production.**

## License
No license yet.

## Contact
Mayur Koli — kolimohit9595@gmail.com
