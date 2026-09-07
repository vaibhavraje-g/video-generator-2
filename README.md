# 🎬 Video Generator - Full Stack GenAI Platform

An automated AI-driven video creation platform that transforms raw documents, research papers, and web URLs into scene-level structured scripts, multimodal assets, and synchronized video drafts.

![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi&logoColor=white)
![Angular](https://img.shields.io/badge/Angular-17-dd0031?logo=angular&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-4.4+-47A248?logo=mongodb&logoColor=white)
![WebSockets](https://img.shields.io/badge/WebSockets-Realtime-010101?logo=socketdotio&logoColor=white)

---

## 🏛️ System Architecture & Workflow Pipeline

```
┌─────────────────┐      ┌─────────────────────────┐      ┌─────────────────────────┐
│ Raw Document /  │ ───► │ Context Ingestion &     │ ───► │ Scene-Level Script      │
│ Article URL     │      │ Text Chunking (FastAPI) │      │ Generation (LLM Engine) │
└─────────────────┘      └─────────────────────────┘      └────────────┬────────────┘
                                                                       │
                                                                       ▼
┌─────────────────┐      ┌─────────────────────────┐      ┌─────────────────────────┐
│ Video Preview & │ ◄─── │ Real-time WebSocket     │ ◄─── │ Asset Retrieval & Frame │
│ Timeline Editor │      │ Progress Streaming      │      │ Alignment (Pinecone/DB) │
└─────────────────┘      └─────────────────────────┘      └─────────────────────────┘
```

---

## 🚀 Core Capabilities

1. **📄 Automated Document Ingestion**: Ingests PDFs, Markdown, Word documents, or web URLs with intelligent summarization.
2. **🎭 Scene-by-Scene Script Generation**: Uses LLMs to generate structured JSON scene definitions with narration voiceover, visual cues, and duration timings.
3. **🔍 Semantic Asset Matching**: Retrieves relevant stock imagery, animations, and video b-roll from vector storage using embedding similarity.
4. **⚡ Real-time Progress Streaming**: WebSocket communication provides real-time generation logs and step-by-step progress to the Angular UI.
5. **🎛️ Interactive Timeline Editor**: Angular frontend allows creators to tweak narration lines, swap assets, and adjust scene durations prior to final rendering.

---

## 🛠️ Repository Layout

```
video-generator/
├── backend/
│   ├── app/
│   │   ├── api/              # FastAPI route controllers
│   │   ├── core/             # Configuration & security utilities
│   │   ├── models/           # MongoDB ODM schemas
│   │   └── services/         # Generation pipeline & media logic
│   ├── tests/                # E2E integration test suite
│   └── requirements.txt      # Python dependencies
├── frontend/                 # Angular 17 presentation client
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/   # Context ingestion, video timeline player
│   │   │   └── services/     # WebSocket & generation API clients
│   │   └── styles/           # Modern UI styling
│   └── package.json          # Frontend dependencies
└── AGENTS.md                 # Autonomous engineering directives
```

---

## ⚙️ Setup & Installation

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run start
```
