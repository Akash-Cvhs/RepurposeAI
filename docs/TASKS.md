# Tasks for AI and Humans

This file tracks prioritized work for the project.
Both humans and AI tools (e.g., GitHub Copilot) should use this as a source of truth.

---

## Priority 1: Core agent pipeline

- [x] Implement `master_agent`:
  - Parse `state["query"]` to infer `molecule` and `indication`.
  - Initialize `state["logs"]` as a list.
- [x] Implement `clinical_trials_agent`:
  - Read `backend/data/trials.csv`.
  - Filter by `molecule` and/or `indication`.
  - Set `state["trials"]` and log how many trials were found.
- [x] Implement `patent_agent`:
  - Read `backend/data/patents.csv`.
  - Filter by `molecule`.
  - Compute `state["fto_risk"]` based on `expiry_date`.
  - Set `state["patents"]` and append a log entry.
- [x] Implement `internal_insights_agent`:
  - Read uploaded PDFs from a temporary folder.
  - Extract text and summarize into `state["internal_insights"]`.
  - Handle the case when no PDFs are uploaded.
- [x] Implement `web_intel_agent`:
  - Read `backend/data/guidelines.json`.
  - Filter by `molecule` and/or `indication`.
  - Set `state["web_findings"]` and append a log entry.
- [x] Implement `report_generator_agent`:
  - Build markdown report from all state fields.
  - Call `pdf_utils.create_report_pdf`.
  - Set `state["report_path"]` and `state["summary"]`.
  - Log that the report was generated.

---

## Priority 2: Workflow and API integration

- [x] Implement `backend/graph/workflow.py`:
  - Define a `State` type or alias.
  - Add nodes for each agent.
  - Set entry point to `master`.
  - Wire edges so that all agents run and then `report_generator` runs last.
- [x] Implement `backend/app.py`:
  - `/run` endpoint:
    - Accept query and PDF uploads.
    - Build initial state and call the LangGraph workflow.
    - Return JSON with `summary`, `report_path` (or `report_url`), and `logs`.
  - `/archives` endpoint:
    - Return a list of past runs from `archives/runs.json`.

---

## Priority 3: UI / UX

- [ ] Implement `frontend/streamlit_app.py`:
  - Text input for query.
  - File uploader for multiple PDFs.
  - Button to call `/run`.
  - Display logs and summary.
  - Show a download link or button for the PDF report.
- [ ] Improve UX:
  - Add minimal theming (title, description).
  - Show loading indicators while the backend is running.

---

## Priority 4: Safety, governance, and RAG (optional)

- [x] Add a "Risks & Assumptions" section in the report:
  - Clearly state that data is mock and for demo only.
  - Highlight if `fto_risk` is high.
  - Encourage domain expert review.
- [ ] Implement simple RAG in `rag_utils.py` for internal PDFs:
  - Create embeddings (e.g., sentence-transformers or LLM API).
  - Support basic similarity search on internal documents.
- [ ] Update `internal_insights_agent` to use RAG when enabled.

---

## How AI tools should use this file

When asked to "work on the next thing":

1. Look at **Priority 1** first and find the first unchecked `[ ]` item.
2. Implement the related code, following:
   - `docs/ARCHITECTURE.md`
   - `docs/PATTERNS.md`
3. Add or update tests in `tests/` when relevant.
4. Mark the task as done (`[x]`) **only after** code and minimal tests are in place.

If a human specifies a particular task, work on that task even if other items are still open.
