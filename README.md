# Mentesa: A No-Code AI Bot Creation Platform for Everyone

**Mentesa** is an innovative no-code platform that enables users to create intelligent, personalized AI agents using just natural language. Powered by open-source LLMs like Mistral and Mixtral (via Ollama), Mentesa supports RAG, file-based learning, memory, and fine-tuning — all without writing a single line of code.

## ✨ Key Features

- 🤖 Create bots using natural language
- 📄 Upload PDFs, notes, and documents for contextual understanding
- 🧠 Powered by open-source LLMs (via Ollama)
- 🧷 Retrieval-Augmented Generation (RAG)
- 💾 Long-term memory + Fine-tuning (LoRA support)
- 📦 Export bot bundles for integration
- ☁️ Cloud hosting & sharing of your bots

## 🧱 Tech Stack (Initial Plan)

- **Frontend**: Streamlit (for MVP), later React
- **Backend**: FastAPI (or Flask)
- **LLMs**: Mistral / Mixtral (via Ollama)
- **Vector DB**: FAISS or ChromaDB
- **Embeddings**: SentenceTransformers
- **File Parsing**: PyMuPDF / PyPDF2
- **Storage**: Firebase / Firestore / Supabase

## 📂 Suggested Folder Structure
```bash
Mentesa/
├── frontend/ # UI (Streamlit or React)
├── backend/ # FastAPI / Flask server
├── llm_agents/ # Bot creation logic
├── data/ # User files (PDFs, notes, etc.)
├── utils/ # Helper modules (RAG, embeddings, etc.)
├── requirements.txt
└── README.md
```

## 🚀 Getting Started

1. Clone the repo:
```bash
git clone https://github.com/<your-username>/Mentesa.git
cd Mentesa
```

## Create virtual environment & install dependencies:
```bash
python -m venv venv
source venv/bin/activate   # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt
```
⚙️ Requirements (requirements.txt)
streamlit
openai
sentence-transformers
faiss-cpu
langchain
pypdf
fastapi
uvicorn
python-dotenv

📄 License
No License Yet

🤝 Contributing
Fork the repository

Create a feature branch (git checkout -b feature/my-feature)

Commit your changes (git commit -m 'Add something')

Push and create a pull request

📬 Contact
Name: Mayur Koli 
Email: kolimohit9595@gmail.com
