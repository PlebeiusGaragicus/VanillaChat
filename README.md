# VanillaChat

## Project Overview
VanillaChat is a modern, minimal, and extensible chatbot web application. The backend leverages Python's FastAPI and LangGraph for conversational AI, while the frontend is built with vanilla HTML, CSS, and JavaScript. The entire stack is Dockerized for easy deployment and reproducibility.

## Features
### MVP Features
- Real-time chatbot interface (single user, no authentication)
- FastAPI backend serving chat endpoints and integrating LangGraph
- Stateless chat sessions (no persistence yet)
- Responsive, clean UI with vanilla HTML/CSS/JS
- Dockerized backend and frontend for easy local or cloud deployment

### Planned/Future Features
- User authentication (crypto pay-as-you-go tokens)
- Persistent chat history
- Admin dashboard
- Rate limiting and abuse protection
- Multi-user support
- Advanced conversation analytics

## Technology Stack
- **Backend:**
  - Python 3.11+
  - FastAPI (API framework)
  - LangGraph (conversational AI)
  - Docker (containerization)
- **Frontend:**
  - HTML5, CSS3, JavaScript (no frameworks)
- **DevOps:**
  - Docker Compose (for orchestration)
  - (Optional) Nginx for production

## Project Structure
```
VanillaChat/
├── backend/
│   ├── app/
│   │   ├── main.py         # FastAPI app entrypoint
│   │   ├── langgraph.py    # LangGraph integration
│   │   └── ...
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── main.js
├── docker-compose.yml
└── README.md
```

## UI/UX Overview
- Minimalist chat window
- Message bubbles for user and bot
- Input box with send button
- Responsive design for desktop and mobile

## API Overview (MVP)
- `POST /chat` — Accepts user message, returns bot response

## Development & Running
- Clone repo
- Build and run with Docker Compose
- Access frontend at `http://localhost:8080` (default)
- See backend docs at `/docs` (FastAPI Swagger UI)

## Roadmap
- [ ] MVP: Single-user chat with LangGraph backend
- [ ] Add authentication with crypto tokens
- [ ] Add persistent chat history
- [ ] Multi-user and admin feature