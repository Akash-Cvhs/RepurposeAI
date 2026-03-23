# Code Patterns for This Repo

The goal is to keep all agents and graph code **consistent and simple**, so humans + AI tools (Copilot, etc.) can extend it easily.

---

## Agent node signature

Each agent node should follow this pattern:

```python
from typing import Dict, Any

def some_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reads from `state`, performs its task,
    updates `state`, and returns it.
    """
    # read inputs from state
    # do the work
    # write outputs into state
    return state
```

Guidelines:

- No global state.
- Avoid side effects outside `state` except where clearly intended (e.g., writing a PDF to disk).
- All new info must be added into `state` using the agreed keys.

---

## State keys and access

- Use the state keys defined in `docs/ARCHITECTURE.md`.
- Always access with `state.get("key")` to avoid `KeyError`.
- If your node depends on a field, handle missing values gracefully.

Example:

```python
molecule = state.get("molecule") or state.get("query", "")
if not molecule:
    logs = state.get("logs", [])
    logs.append("[clinical_trials] no molecule found; skipping")
    state["logs"] = logs
    return state
```

---

## Logging pattern

Use `state["logs"]` (list of strings) to record what happened in each node:

```python
logs = state.get("logs", [])
logs.append("[patent_landscape] fetched 8 patents, FTO risk=medium")
state["logs"] = logs
```

- Keep messages short and human-readable.
- Prefix with node name in square brackets for clarity.

---

## Error handling pattern

We prefer **soft failures**: log the error and continue when possible.

```python
logs = state.get("logs", [])

try:
    # do the work
except Exception as e:
    logs.append(f"[internal_insights] error: {e}")
    state["logs"] = logs
    return state
```

- Only raise exceptions if the system cannot continue safely.
- For the hackathon demo, robustness and user feedback are more important than strict correctness.

---

## Data access pattern

- `clinical_trials_agent`:
  - Reads `backend/data/trials.csv`
  - Uses `pandas.read_csv` or `csv` module
  - Filters by `molecule` / `indication`

- `patent_agent`:
  - Reads `backend/data/patents.csv`
  - Computes patent expiry and simple FTO risk
  - Returns list of patent dicts + `fto_risk` string

- `web_intel_agent`:
  - Reads `backend/data/guidelines.json`
  - Optionally other mock JSONs (e.g., `rwe_news.json`)

- All file paths should be **relative** to `backend/` and configurable via `config.py` if needed.

---

## Report generation pattern

- `report_generator_agent`:
  - Constructs a **markdown string** with consistent sections:

    1. Context & Query
    2. Unmet Medical Needs
    3. Clinical Trial Landscape
    4. Patent Landscape & FTO
    5. Internal Insights
    6. Web Intelligence & Guidelines
    7. Risks & Assumptions (optional)

  - Calls:

    ```python
    from backend.utils.pdf_utils import create_report_pdf

    output_path = create_report_pdf(markdown_str, filename_slug)
    state["report_path"] = output_path
    state["summary"] = short_summary
    ```

- Keep formatting simple but clean: headings, bullet lists, small tables where needed.

---

## Testing pattern

- Tests live in `tests/`.
- Basic test examples:

```python
def test_clinical_trials_agent_basic():
    state = {"molecule": "metformin"}
    new_state = clinical_trials_agent(state)
    assert "trials" in new_state

def test_patent_agent_sets_fto_risk():
    state = {"molecule": "aspirin"}
    new_state = patent_agent(state)
    assert "fto_risk" in new_state
```

- Tests do not need to be exhaustive but should ensure:
  - No crashes with typical inputs
  - Key state fields are set
