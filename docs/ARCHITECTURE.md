# Architecture: Agentic AI for Drug Repurposing

## Goal

A user enters a **molecule name** or **therapeutic area**.
The system runs multiple agents (clinical trials, patents, internal docs, web) and produces a **PDF "Innovation Product Story"** report.

This is a hackathon prototype using:
- Python + FastAPI
- LangGraph for multi-agent orchestration
- Streamlit for UI
- Mock CSV/JSON datasets instead of real external APIs

---

## High-level components

- **Backend (`backend/`)**
  - FastAPI app (`app.py`)
  - LangGraph workflow (`graph/workflow.py`)
  - Agent implementations (`agents/`)
  - Utils (PDF generation, parsing, storage)
  - Mock data (`data/`)
  - Archives (`archives/`)

- **Frontend (`frontend/`)**
  - Streamlit chat-style UI (`streamlit_app.py`)

- **Docs (`docs/`)**
  - Architecture, patterns, data schemas, tasks

- **Tests (`tests/`)**
  - Basic tests for agents and workflow

---

## Agent graph (LangGraph)

Nodes (in `backend/agents/`):

- **master** (`master_agent.py`)
  - Parse user query
  - Identify molecule and indication (therapeutic area)
  - Initialize shared state (`query`, `molecule`, `indication`, `logs`)

- **clinical_trials** (`clinical_trials_agent.py`)
  - Read `backend/data/trials.csv`
  - Filter by molecule / indication
  - Return list of trials and aggregated counts
  - Set `state["trials"]`

- **patent_landscape** (`patent_agent.py`)
  - Read `backend/data/patents.csv`
  - Filter by molecule / mechanism of action
  - Compute basic Freedom-to-Operate (FTO) risk from expiry dates
  - Set `state["patents"]` and `state["fto_risk"]`

- **internal_insights** (`internal_insights_agent.py`)
  - Process uploaded internal PDFs
  - Extract text and summarize key points
  - Optionally use simple RAG from `rag_utils.py`
  - Set `state["internal_insights"]`

- **web_intel** (`web_intel_agent.py`)
  - Read `backend/data/guidelines.json` (and optionally other mock JSONs)
  - Summarize treatment guidelines, RWE, and relevant mock "news"
  - Set `state["web_findings"]`

- **report_generator** (`report_generator_agent.py`)
  - Read all prior state keys:
    - `trials`, `patents`, `fto_risk`
    - `internal_insights`, `web_findings`
  - Build a structured markdown report with sections:
    - Unmet Medical Needs
    - Clinical Trial Landscape
    - Patent Landscape & FTO
    - Internal Insights
    - Web Intelligence & Guidelines
    - (Optional) Risks & Assumptions
  - Call `pdf_utils.create_report_pdf(...)`
  - Set:
    - `state["report_path"]` (filesystem path / URL)
    - `state["summary"]` (short textual summary)

---

## State model

All nodes share a single `State` dict (or a typed model later). Expected keys:

- **Input / core**
  - `query`: original user query string
  - `molecule`: parsed molecule name (if found)
  - `indication`: parsed therapeutic area (if found)

- **Agent outputs**
  - `trials`: list[dict] of clinical trial records
  - `patents`: list[dict] of patent records
  - `fto_risk`: `"low"` | `"medium"` | `"high"` or similar
  - `internal_insights`: string or list of bullet-point strings
  - `web_findings`: string or list of bullet-point strings with URLs

- **Report / UI**
  - `report_path`: path/URL to generated PDF
  - `summary`: 2-5 line summary for display in UI
  - `logs`: list[str] of step-by-step log messages from each agent

---

## Backend request flow

1. **Frontend -> Backend**
   - Streamlit posts to `POST /run` with:
     - query string
     - uploaded PDF files

2. **Backend / FastAPI (`app.py`)**
   - Saves uploaded PDFs to a temp location
   - Builds initial `state` with `query` and empty defaults
   - Calls LangGraph compiled app (`app_graph.invoke(initial_state)`)

3. **LangGraph workflow (`graph/workflow.py`)**

   Example flow (simplified):

   - Entry point: `"master"`
   - Parallel / sequential calls:
     - `"clinical_trials"`
     - `"patent_landscape"`
     - `"internal_insights"`
     - `"web_intel"`
   - Final node: `"report_generator"` -> `END`

4. **Backend response**
   - Returns JSON:
     - `summary`
     - `report_url` or `report_path`
     - optionally `logs` (for debugging / UI)

5. **Frontend**
   - Shows progress / logs
   - Shows summary
   - Provides download link for PDF

---

## Archives

- PDF reports stored under: `backend/archives/reports/`
- Simple index file: `backend/archives/runs.json` with entries like:

```json
{
  "id": "uuid-or-timestamp",
  "query": "metformin oncology",
  "molecule": "metformin",
  "indication": "oncology",
  "created_at": "2026-03-23T10:30:00Z",
  "report_path": "backend/archives/reports/metformin-oncology-20260323T1030.pdf"
}
```

These archives are used to:
- List past runs (`GET /archives`)
- Potentially re-download old reports from the UI.
