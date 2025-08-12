# Mentesa V2: Modern AI Bot Creation & Management Platform

**Mentesa V2** is a sleek and modern platform for creating and managing AI bots with an intuitive web interface. This version brings a complete redesign with a focus on user experience, real-time chat capabilities, and a modern tech stack.

## � Overview

Mentesa V2 provides a streamlined way to create and interact with AI bots through a modern web interface. The platform features real-time chat, bot management, and a clean, professional design that makes AI bot creation and interaction accessible to everyone.

## ✨ Key Features

- 🎨 Modern, responsive web interface
- � Easy bot creation and management
- � Real-time chat interface
- 🎭 Customizable bot personalities
- ⚡ Fast and lightweight
- 🛠️ Easy configuration options
- 🌐 API-first architecture

## 🧱 Tech Stack

- **Frontend**: 
  - Pure HTML/CSS/JavaScript
  - Modern responsive design
  - Real-time updates
  
- **Backend**: 
  - FastAPI
  - RESTful API architecture
  - Async support
  
- **Features**:
  - Bot creation & management
  - Real-time chat
  - Persistent storage
  - Configuration management

## 📂 Project Structure
```bash
Mentesa/
├── frontend/           # Web interface
│   ├── index.html     # Main HTML
│   ├── style.css      # Styles
│   ├── script.js      # Frontend logic
│   └── app.py         # Launcher script
├── backend/           # FastAPI server
│   ├── main.py       # Server entry point
│   ├── config.py     # Configuration
│   ├── routes/       # API routes
│   └── services/     # Business logic
├── utils/            # Helper modules
│   ├── bot_ops.py   # Bot operations
│   ├── chat_ops.py  # Chat handling
│   └── file_ops.py  # File operations
├── data/            # Storage
│   ├── bots.json   # Bot configurations
│   └── chats/      # Chat history
└── README.md
```

## 🚀 Getting Started

1. Clone the repository:
```bash
git clone https://github.com/Mayurkoli8/Mentesa.git
cd Mentesa
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the backend server:
```bash
cd backend
uvicorn main:app --reload
```

4. Launch the frontend:
```bash
cd frontend
python -m http.server 3000
```

The application will be available at:
- Frontend: http://localhost:5000
- Backend API: http://localhost:8000

## ⚙️ Requirements

Main dependencies:
- FastAPI
- Uvicorn
- Python 3.8+

## �️ API Endpoints

The backend provides the following REST API endpoints:

- `GET /bots` - List all bots
- `POST /bots` - Create a new bot
- `DELETE /bots/{id}` - Delete a bot
- `POST /chat` - Send a message to a bot

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add some amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📬 Contact

- **Developer**: Mayur Koli
- **Email**: kolimohit9595@gmail.com
- **GitHub**: [@Mayurkoli8](https://github.com/Mayurkoli8)

## 📄 License

No License Yet - All Rights Reserved
