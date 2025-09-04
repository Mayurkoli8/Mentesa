🚀 Mentesa: A No-Code AI Bot Creation Platform

Mentesa is a no-code platform that lets anyone create, manage, and chat with personalized AI bots — no coding required.
Built for students, creators, and businesses, Mentesa combines powerful LLMs, memory, and file-based learning into a simple, user-friendly interface.

🌐 Live Demo

🔗 Mentesa on Streamlit

✨ Features

🤖 Create bots with natural language — just describe the personality you want

📄 Upload documents (PDFs, notes, text files) to teach your bot

🧠 Contextual memory — bots remember conversations

🔍 RAG support for accurate, context-aware answers

🔑 Multiple LLMs supported (via Ollama: Mistral, Mixtral, etc.)

📦 Exportable bot bundles for integration into apps

☁️ Cloud-synced storage of bots and chats

🧱 Tech Stack

Frontend: Streamlit (MVP), later migrating to React

Backend: FastAPI

LLMs: Mistral / Mixtral (via Ollama, Gemini planned)

Vector DB: FAISS (previously ChromaDB)

Embeddings: SentenceTransformers

Storage: Firebase Firestore

File Parsing: PyMuPDF / PyPDF2

📂 Project Structure
Mentesa/
├── frontend/        # Streamlit app (UI)
├── backend/         # FastAPI server
├── llm_agents/      # Bot creation & LLM logic
├── data/            # Uploaded files & chat history
├── utils/           # Helper modules (RAG, embeddings, etc.)
├── requirements.txt # Dependencies
└── README.md

🚀 Getting Started
1. Clone the repo
git clone https://github.com/Mayurkoli8/Mentesa.git
cd Mentesa

2. Install dependencies
pip install -r requirements.txt

3. Run the app
streamlit run frontend/app.py

⚙️ Requirements

Streamlit

Ollama
 with Mistral/Mixtral installed

Firebase project (Firestore enabled)

📦 Roadmap

 Multi-bot support

 Firebase integration for storage

 Real-time collaboration (share bots)

 Custom training & fine-tuning (LoRA)

 React-based frontend

📄 License

Currently unlicensed (all rights reserved).

🤝 Contributing

1. Fork the repo

2. Create a feature branch:
"""bash
git checkout -b feature/my-feature
"""

3. Commit changes:
"""bash
git commit -m "Add my feature"
"""

4. Push & open a pull request

📬 Contact

👤 Mayur Koli
📧 Email: kolimohit9595@gmail.com