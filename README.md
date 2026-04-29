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

  # Intelligent MCP Orchestration

## Overview

The MCP Orchestrator acts as an intelligent router that analyzes user queries and dynamically decides which agents to invoke, rather than running all agents for every query.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         USER                                 │
│                    (sends query)                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    MCP SERVER                                │
│              POST /mcp/orchestrate                           │
│         {"query": "...", "molecule": "..."}                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  MCP ORCHESTRATOR                            │
│                                                              │
│  Step 1: Analyze Query (LLM-based planning)                 │
│  ┌────────────────────────────────────────────┐             │
│  │ "What clinical evidence exists for X?"     │             │
│  │                                             │             │
│  │ LLM decides:                                │             │
│  │  ✓ clinical_trials                         │             │
│  │  ✓ internal_insights                       │             │
│  │  ✗ patents (not needed)                    │             │
│  │  ✗ web_intel (not needed)                  │             │
│  │  ✗ drug_analysis (no molecule specified)   │             │
│  │  ✓ report (always)                         │             │
│  └────────────────────────────────────────────┘             │
│                                                              │
│  Step 2: Execute Selected Agents (parallel)                 │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │  Clinical    │  │  Internal    │                        │
│  │  Trials      │  │  Insights    │                        │
│  │  Agent       │  │  Agent       │                        │
│  └──────┬───────┘  └──────┬───────┘                        │
│         │                  │                                 │
│         └────────┬─────────┘                                │
│                  ▼                                           │
│         ┌────────────────┐                                  │
│         │  Merge Results │                                  │
│         └────────┬───────┘                                  │
│                  │                                           │
│  Step 3: Generate Report                                    │
│                  ▼                                           │
│         ┌────────────────┐                                  │
│         │  Report Agent  │                                  │
│         │  (PDF output)  │                                  │
│         └────────┬───────┘                                  │
└──────────────────┼─────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                    RESPONSE                                  │
│  {                                                           │
│    "run_id": "run_20260323_143022",                         │
│    "execution_plan": {...},                                 │
│    "completed_agents": ["clinical_trials", ...],            │
│    "report": "# Drug Repurposing Analysis\n...",            │
│    "status": "completed"                                    │
│  }                                                           │
└─────────────────────────────────────────────────────────────┘
```

## Flow Comparison

### Old Flow (Fixed Pipeline)
```
User Query → ALL Agents Run → Report
```
- Clinical Trials Agent ✓
- Patent Agent ✓
- Internal Insights Agent ✓
- Web Intel Agent ✓
- Drug Analyzer Agent ✓
- Report Agent ✓

**Problem:** Wastes time and API calls on irrelevant agents

### New Flow (Intelligent Routing)
```
User Query → LLM Planning → Selected Agents → Report
```

**Example 1:** "What clinical evidence exists for aspirin?"
- Clinical Trials Agent ✓
- Internal Insights Agent ✓
- Report Agent ✓

**Example 2:** "What is the patent landscape for metformin?"
- Patent Agent ✓
- Drug Analyzer Agent ✓
- Report Agent ✓

**Example 3:** "Full drug repurposing analysis for compound X"
- ALL Agents ✓

## API Usage

### Endpoint
```
POST http://localhost:8001/mcp/orchestrate
```

### Request
```json
{
  "query": "What are the repurposing opportunities for metformin in cancer?",
  "molecule": "metformin"
}
```

### Response
```json
{
  "success": true,
  "run_id": "run_20260323_143022",
  "execution_plan": {
    "clinical_trials": true,
    "patents": true,
    "internal_insights": true,
    "web_intel": true,
    "drug_analysis": true,
    "report": true
  },
  "completed_agents": [
    "clinical_trials",
    "patents",
    "internal_insights",
    "web_intel",
    "drug_analysis"
  ],
  "report": "# Drug Repurposing Analysis Report\n\n## Query: ...\n\n...",
  "status": "completed"
}
```

## Agent Selection Logic

The orchestrator uses an LLM to analyze the query and decide which agents are needed:

| Query Type | Selected Agents |
|------------|----------------|
| "Clinical evidence for X" | clinical_trials, internal_insights |
| "Patent landscape for X" | patents, drug_analysis |
| "Market opportunity for X" | web_intel, patents |
| "Drug properties of X" | drug_analysis |
| "Internal experiment results" | internal_insights |
| "Full repurposing analysis" | ALL agents |

## Benefits

1. **Efficiency:** Only runs necessary agents
2. **Cost Savings:** Fewer LLM API calls
3. **Speed:** Faster response times
4. **Flexibility:** Adapts to different query types
5. **Scalability:** Easy to add new agents

## Testing

```bash
# Start MCP server
cd backend
uvicorn mcp.server:app --reload --port 8001

# Run orchestration tests
python scripts/test_orchestration.py
```

## Integration with Frontend

The Streamlit frontend can call the orchestration endpoint:

```python
import requests

response = requests.post(
    "http://localhost:8001/mcp/orchestrate",
    json={
        "query": user_query,
        "molecule": molecule_name
    }
)

result = response.json()
report_markdown = result["report"]
```

## Future Enhancements

- **Streaming:** Stream agent results as they complete
- **Caching:** Cache agent results for similar queries
- **Feedback Loop:** Learn from user feedback to improve routing
- **Cost Tracking:** Track API costs per query
- **Agent Prioritization:** Run critical agents first
