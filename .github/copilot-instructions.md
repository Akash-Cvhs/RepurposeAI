# Copilot Instructions for VHS Drug Repurposing Project

## What this project is

- This repo implements an Agentic AI system for **drug repurposing and innovation discovery**.
- A user enters a molecule name or therapeutic area and receives an **Innovation Product Story** PDF report.
- The report is built by a **Master/Orchestrator agent** that coordinates specialized sub-agents:
  - Clinical Trials
  - Patent Landscape & FTO
  - Internal Insights (uploaded PDFs)
  - Web Intelligence (guidelines / news)
  - Report Generator

## Tech stack

- Backend: **Python + FastAPI**
- Agent framework: **LangGraph** for multi-agent orchestration
- LLM: OpenAI / compatible client via environment variables
- Frontend: **Streamlit** for chat-style UI and report download
- Data: **mock CSV/JSON** files in `backend/data` (trials, patents, guidelines)
- PDF generation: helpers in `backend/utils/pdf_utils.py`
- Archives: generated reports stored in `backend/archives/reports` with a JSON index

## Project structure (important folders)

- `backend/app.py`: FastAPI entrypoint (`/run`, `/archives`)
- `backend/graph/workflow.py`: LangGraph `State` definition and node wiring
- `backend/agents/`:
  - `master_agent.py`: orchestrates agents, parses query, sets `molecule`/`indication`
  - `clinical_trials_agent.py`: reads `data/trials.csv`, sets `state["trials"]`
  - `patent_agent.py`: reads `data/patents.csv`, sets `state["patents"]`, `state["fto_risk"]`
  - `internal_insights_agent.py`: summarizes uploaded PDFs into `state["internal_insights"]`
  - `web_intel_agent.py`: reads `data/guidelines.json`, sets `state["web_findings"]`
  - `report_generator_agent.py`: builds report markdown and calls `pdf_utils.create_report_pdf`
- `backend/utils/`: PDF creation, parsing, storage, optional RAG helpers
- `backend/archives/`: generated PDFs + `runs.json` index
- `frontend/streamlit_app.py`: Streamlit UI (query, PDF upload, logs, download)
- `docs/ARCHITECTURE.md`: overall architecture and state keys
- `docs/PATTERNS.md`: node signature, logging, error handling patterns
- `docs/TASKS.md`: prioritized TODOs for humans and AI
- `tests/`: basic tests for agents and workflow

## Coding guidelines

- Prefer **simple, explicit functions** over complex abstractions; this is a hackathon-style project but should stay readable.
- Use **type hints** for public functions.
- Use **Pydantic models** for FastAPI request/response payloads when helpful.
- Keep each agent **single-responsibility**:
  - Do not mix multiple domains (e.g., patents + trials) in one file.
- Handle **errors softly**:
  - Do not crash the whole workflow if one agent fails.
  - Log errors into `state["logs"]` instead of raising, unless absolutely necessary.

### Agent node pattern

- Each agent node is a function with the pattern:

  ```python
  from typing import Dict, Any

  def some_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
      # read from state
      # do the work
      # write results back into state
      return state
  ```

- Shared **state keys** used across nodes (see `docs/ARCHITECTURE.md` for full list):
  - `query`, `molecule`, `indication`
  - `trials`, `patents`, `fto_risk`
  - `internal_insights`, `web_findings`
  - `report_path`, `summary`
  - `logs` (list of strings describing each step)

### Data access

- Always read data from `backend/data`:
  - Trials: `trials.csv`
  - Patents: `patents.csv`
  - Guidelines/RWE: `guidelines.json`
- Use `pandas` or Python stdlib (`csv`, `json`) to load mock data.
- **Do not** integrate real external APIs in this repo; simulate with mock data.

### Logging & observability

- Every agent should append a log entry to `state["logs"]`, e.g.:

  ```python
  logs = state.get("logs", [])
  logs.append("[clinical_trials] fetched 12 trials for metformin")
  state["logs"] = logs
  ```

- The UI reads `logs` after the workflow completes and shows them to the user.

## How to help in this repo

When I ask you to implement something:

- If it is about **agents**:
  - Work inside `backend/agents/`.
  - Follow the node pattern and state keys.
  - Return structured data (lists of dicts) suitable for tables in the report.

- If it is about the **graph/workflow**:
  - Edit `backend/graph/workflow.py`.
  - Wire nodes and edges clearly.
  - Use the same `State` keys defined in `docs/ARCHITECTURE.md`.

- If it is about the **API**:
  - Modify `backend/app.py`.
  - Expose simple, JSON-based endpoints (`/run`, `/archives`).
  - Use FastAPI best practices.

- If it is about the **UI**:
  - Modify `frontend/streamlit_app.py`.
  - Keep the core flow:
    - text input (query),
    - PDF upload,
    - call `/run`,
    - display logs,
    - show summary and report download link.

- If it is about **tests**:
  - Place tests under `tests/`.
  - Add small, focused tests for each agent node and for the workflow.

## Things to avoid

- Do not add heavyweight frameworks or databases.
- Do not rely on real API credentials or cloud resources.
- Avoid breaking the agreed state keys; extend them carefully and update docs when you do.

## Using docs and tasks

- Before large changes, **consult**:
  - `docs/ARCHITECTURE.md`
  - `docs/PATTERNS.md`
  - `docs/TASKS.md`
- When I say "implement the next task", check `docs/TASKS.md` and work on the first unchecked item in Priority 1 unless specified otherwise.
