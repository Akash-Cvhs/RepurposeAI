# VHS Drug Repurposing Platform

## Problem Statement
An AI-powered platform that analyzes drug repurposing opportunities by integrating clinical trials data, patent information, regulatory guidelines, and web intelligence to generate comprehensive reports for pharmaceutical research.

## Architecture
Multi-agent system built with FastAPI backend, LangGraph workflow orchestration, and Streamlit frontend. See `docs/ARCHITECTURE.md` for detailed system design.

## Quick Setup

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --reload
```

### Frontend
```bash
cd frontend
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Project Structure
- `backend/` - FastAPI server with LangGraph agents
- `frontend/` - Streamlit chat interface
- `docs/` - Architecture and development documentation
- `tests/` - Unit and integration tests
- `.github/` - CI/CD and Copilot configuration

For detailed documentation, see:
- [Architecture Overview](docs/ARCHITECTURE.md)
- [Development Patterns](docs/PATTERNS.md)
- [Task Priorities](docs/TASKS.md)