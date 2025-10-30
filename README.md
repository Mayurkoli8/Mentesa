# Mentesa: Build & Deploy No‑Code AI Bots in Minutes

**Mentesa** is a no‑code multi‑AI bot platform where anyone can create, deploy, and interact with custom AI agents — without writing code.

Designed for creators, founders, educators, and developers, Mentesa lets you build personal or business AI assistants powered by cutting‑edge open‑source LLMs, enhanced with memory, RAG, and multi‑persona support.

## 🌐 Live Platform

🔗 [https://Mentesa.live](https://Mentesa.live)

🔗 [https://developer.Mentesa.live](https://developer.Mentesa.live)

🔗 [https://mayurkoli.Mentesa.live](https://mayurkoli.Mentesa.live)

---

## 🚀 What's New in **Version 7**

* 🌍 **Bots Anywhere** — Embed Mentesa AI bots on any website with 1‑line script
* 💬 **Floating Website Chat Widget** — Add AI assistants to your site like Intercom / Crisp
* ⚙️ **Multiple Model Support** — Gemini 2.5 pro and 2.0 Flash exp
* 🧠 **Improved Memory Engine** — Persistent long‑term memory per bot
* 📁 **Knowledge Uploads** — PDFs, docs, text, website links
* 🎭 **Personality Profiles** — Create role‑based or persona‑based AI

---

## ✨ Core Features

* 🛠️ Create AI bots with natural language prompts
* 📄 Upload docs + website text for knowledge
* 🧠 Built‑in memory + contextual learning
* 🔍 Retrieval‑Augmented Generation (RAG)
* 🧩 Multi‑model: Gemini 2.5 pro and 2.0 Flash exp
* 🌐 Embed bots on websites without coding
* ☁️ Cloud bot storage & instant access
* 🎒 Save, manage & chat with multiple bots

---

## 🧱 Tech Stack

| Layer        | Tech                                             |
| ------------ | ------------------------------------------------ |
| Frontend     | AWS EC2 (Streamlit)                              |
| Backend      | Render (FastAPI)                                 |
| Models       | Google Gemini 2.5 pro and 2.0 Flash exp          |
| Storage      | Firebase / Firestore                             |
| Vector DB    | FAISS                                            |
| URL Scrapping| BeautifulSoup                                    |
| File Parsing | PyPDF2, PyMuPDF                                  |

---

## 📂 Folder Structure

```
Mentesa/
├── .env
├── .gitignore
├── README.md
├── backend/
│   ├── __pycache__/
│   │   └── main.cpython-313.pyc
│   ├── main.py
│   └── static/
│       ├── embed.js
│       ├── html.html
│       └── mentesa_logo.png
├── frontend/
│   ├── .streamlit/
│   │   └── secrets.toml
│   ├── __init__.py
│   ├── app.py
│   ├── auth.py
│   ├── cookies.py
│   ├── logo.png
│   └── ui.py
├── requirements.txt
└── utils/
    ├── __init__.py
    ├── file_handle.py
    ├── firebase_config.py
    ├── llm.py
    └── scraper.py

```

---

## 🧪 Local Setup

```bash
git clone https://github.com/Mayurkoli8/Mentesa.git
cd mentesa
git checkout v7
```

Add your Google Gemini API key to `.streamlit/secrets.toml`:

```
GEMINI_API_KEY="YOUR_KEY"
```

### Install

```bash
pip install -r requirements.txt
```

### Run Frontend

```bash
streamlit run frontend/app.py
```

### Run Backend

```bash
cd backend
uvicorn main:app --reload
```
---

## 📦 Deployment

* ✅ AWS EC2 Cloud for UI 
* ✅ Render / Railway for backend
* ✅ Firebase for storage and Authentication

---

## 🧑‍💻 Contributing

```
Fork → Create Branch → Commit → PR
```

---

## 📬 Contact

**Founder:** Mayur Koli
📧 [kolimohit9595@gmail.com](mailto:kolimohit9595@gmail.com)
🌐 [https://mayurkoli.Mentesa.live](https://mayurkoli.Mentesa.live)

---

> Build AI assistants, not just chatbots. Mentesa lets everyone create AI that works *for* them.
