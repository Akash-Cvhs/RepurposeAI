# MCP Agent Integration Guide

## Overview

Your agents have been successfully integrated with the MCP (Model Context Protocol) architecture. The system now supports both **node-based agents** (functional) and **class-based agents** (object-oriented).

---

## Architecture

```
User Query
    ↓
MCP Server (/mcp/orchestrate)
    ↓
MCP Orchestrator
    ↓
Master Agent (parses query, extracts molecule/indication)
    ↓
Parallel Agent Execution
    ├─ Clinical Trials Agent (node-based)
    ├─ Patent Agent (node-based)
    ├─ Internal Insights Agent (class-based)
    ├─ Web Intel Agent (class-based)
    └─ Drug Analyzer Agent (class-based)
    ↓
Report Generator Agent (node-based)
    ↓
PDF Report + JSON Response
```

---

## Agent Types

### Node-Based Agents (Functional)
These agents are pure functions that take state and return updated state.

**Agents:**
- `master_agent.py` - Query parsing and state initialization
- `clinical_trials_agent.py` - Clinical trial data fetching
- `patent_agent.py` - Patent landscape analysis
- `report_generator_agent.py` - Final report generation

**Structure:**
```python
def agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    # Process state
    # Update state with results
    return state
```

**Integration:**
```python
# In orchestrator
result = await asyncio.to_thread(agent_node, state.copy())
```

### Class-Based Agents (Object-Oriented)
These agents are classes with async methods.

**Agents:**
- `internal_insights_agent.py` - RAG over internal documents
- `web_intel_agent.py` - Web intelligence gathering
- `drug_analyzer_agent.py` - Molecular analysis

**Structure:**
```python
class Agent:
    def __init__(self):
        self.llm = get_llm()
    
    async def analyze(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Process state
        # Update state with results
        return state
```

**Integration:**
```python
# In orchestrator
agent = Agent()
result = await agent.analyze(state.copy())
```

---

## State Management

### State Structure

```python
state = {
    # Query Information
    "query": str,                    # Original user query
    "molecule": str,                 # Extracted molecule name
    "indication": str,               # Extracted indication/disease
    "run_id": str,                   # Unique run identifier
    
    # Execution Control
    "status": str,                   # "executing", "agents_completed", "completed"
    "execution_plan": Dict[str, bool],  # Which agents to run
    "completed_agents": List[str],   # Agents that finished
    "logs": List[str],               # Execution logs
    "agent_errors": Dict[str, Any],  # Error tracking
    
    # Agent Results
    "trials": List[Dict],            # Clinical trials data
    "patents": List[Dict],           # Patent data
    "fto_risk": str,                 # Freedom-to-operate risk
    "internal_insights": Any,        # Internal document insights
    "web_findings": Any,             # Web intelligence
    "drug_analysis": str,            # Molecular analysis
    "web_intelligence": str,         # Market intelligence
    
    # Report Generation
    "report_path": str,              # Path to generated PDF
    "summary": str,                  # Executive summary
    "risk_assumptions": List[str],   # Risk disclaimers
    
    # Configuration
    "use_live_apis": bool,           # Use live APIs vs mock data
    "archive_run": bool,             # Save to archive
}
```

### State Flow

1. **Master Agent** initializes state with parsed query
2. **Parallel Agents** each receive a copy of state
3. **Orchestrator** merges agent results back into main state
4. **Report Generator** receives final merged state
5. **Response** returns complete state to client

---

## Configuration

### Environment Variables

Add to `.env`:

```bash
# External APIs
ENABLE_LIVE_APIS=false

# Clinical Trials
CLINICAL_TRIALS_API_URL=https://clinicaltrials.gov/api/v2/studies
CLINICAL_TRIALS_PAGE_SIZE=50
CLINICAL_TRIALS_TIMEOUT_SECONDS=30

# Patent Search (SerpAPI)
SERPAPI_API_KEY=your_serpapi_key_here
SERPAPI_API_URL=https://serpapi.com/search
SERPAPI_ENGINE=google_patents
SERPAPI_MAX_RESULTS=50
SERPAPI_TIMEOUT_SECONDS=30

# Web Intelligence (Tavily)
TAVILY_API_KEY=your_tavily_key_here
TAVILY_API_URL=https://api.tavily.com/search
TAVILY_MAX_RESULTS=10
```

### Config File

All configuration is centralized in `backend/config.py`:

```python
# External API Configuration
ENABLE_LIVE_APIS = os.getenv("ENABLE_LIVE_APIS", "false").lower() == "true"

# Clinical Trials API
CLINICAL_TRIALS_API_URL = os.getenv("CLINICAL_TRIALS_API_URL", "...")
CLINICAL_TRIALS_PAGE_SIZE = int(os.getenv("CLINICAL_TRIALS_PAGE_SIZE", 50))

# Patent Search API
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY", "")
SERPAPI_API_URL = os.getenv("SERPAPI_API_URL", "...")

# CSV Fallback Paths
TRIALS_CSV_PATH = DATA_DIR / "trials.csv"
PATENTS_CSV_PATH = DATA_DIR / "patents.csv"
```

---

## API Endpoints

### 1. Orchestrate Analysis

**Endpoint:** `POST /mcp/orchestrate`

**Request:**
```json
{
  "query": "What drugs are available for Alzheimer's disease?",
  "molecule": "Donepezil"
}
```

**Response:**
```json
{
  "success": true,
  "run_id": "run_20260323_173000",
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
  "report": "# Innovation Product Story\n\n...",
  "status": "completed"
}
```

### 2. Run Individual Tool

**Endpoint:** `POST /mcp/run`

**Request:**
```json
{
  "tool_name": "search_smiles",
  "payload": {
    "query": "Alzheimer",
    "exact_match": false
  },
  "session_id": "test_session"
}
```

**Response:**
```json
{
  "cached": false,
  "data": {
    "results": [
      {
        "name": "Donepezil",
        "category": "Alzheimer's",
        "smiles": "CC(C)NCC(COc1ccccc1CC=C)O"
      }
    ]
  }
}
```

---

## Error Handling

### Agent-Level Errors

Agents catch errors and store them in `state["agent_errors"]`:

```python
try:
    trials = fetch_trials(molecule)
    state["trials"] = trials
except Exception as exc:
    state["trials"] = []
    state["agent_errors"]["clinical_trials"] = {
        "code": "CLINICAL_TRIALS_DATA_UNAVAILABLE",
        "message": str(exc)
    }
    state["logs"].append(f"[clinical_trials] error: {exc}")
```

### Orchestrator-Level Errors

Orchestrator catches agent exceptions:

```python
results = await asyncio.gather(*tasks, return_exceptions=True)

for agent_name, result in zip(agent_names, results):
    if isinstance(result, Exception):
        state[f"{agent_name}_error"] = str(result)
        state["logs"].append(f"[orchestrator] {agent_name} failed: {result}")
```

### Graceful Degradation

- If live API fails → fallback to CSV data
- If agent fails → continue with other agents
- If all agents fail → still generate report with available data

---

## Testing

### Test Individual Agent

```python
from agents.clinical_trials_agent import clinical_trials_agent_node

state = {
    "query": "metformin for diabetes",
    "molecule": "metformin",
    "indication": "diabetes",
    "logs": [],
    "agent_errors": {}
}

result = clinical_trials_agent_node(state)
print(f"Found {len(result['trials'])} trials")
```

### Test Orchestration

```bash
curl -X POST http://localhost:8001/mcp/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Analyze Donepezil for Alzheimer'\''s treatment",
    "molecule": "Donepezil"
  }'
```

### Test with Mock Data

```python
# Set in state
state["use_live_apis"] = False

# Or set environment variable
ENABLE_LIVE_APIS=false
```

---

## Adding New Agents

### Option 1: Node-Based Agent

1. Create agent file:
```python
# backend/agents/my_agent.py
def my_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logs = state.get("logs", [])
    
    # Your logic here
    result = process_data(state)
    
    state["my_result"] = result
    logs.append("[my_agent] completed")
    state["logs"] = logs
    
    return state
```

2. Import in orchestrator:
```python
from agents.my_agent import my_agent_node
```

3. Add to execution plan:
```python
if agent_name == "my_agent":
    tasks.append(asyncio.to_thread(my_agent_node, state.copy()))
    agent_names.append(agent_name)
```

### Option 2: Class-Based Agent

1. Create agent class:
```python
# backend/agents/my_agent.py
class MyAgent:
    def __init__(self):
        self.llm = get_llm()
    
    async def analyze(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Your async logic here
        result = await self.process_data(state)
        state["my_result"] = result
        return state
```

2. Initialize in orchestrator:
```python
def __init__(self):
    self.my_agent = MyAgent()
```

3. Add to execution:
```python
if agent_name == "my_agent":
    tasks.append(self.my_agent.analyze(state.copy()))
    agent_names.append(agent_name)
```

---

## Best Practices

### 1. State Immutability
Always work with copies of state in parallel execution:
```python
tasks.append(agent_node(state.copy()))  # ✅ Good
tasks.append(agent_node(state))         # ❌ Bad - race conditions
```

### 2. Error Handling
Always catch and log errors:
```python
try:
    result = risky_operation()
    state["result"] = result
except Exception as exc:
    state["agent_errors"]["my_agent"] = {
        "code": "ERROR_CODE",
        "message": str(exc)
    }
    state["logs"].append(f"[my_agent] error: {exc}")
```

### 3. Logging
Add logs for debugging:
```python
logs = state.get("logs", [])
logs.append("[my_agent] starting analysis")
logs.append(f"[my_agent] found {count} results")
state["logs"] = logs
```

### 4. Fallback Data
Provide fallback when external APIs fail:
```python
if use_live_apis:
    try:
        data = fetch_from_api()
    except Exception:
        data = load_from_csv()  # Fallback
else:
    data = load_from_csv()
```

### 5. Type Hints
Use type hints for clarity:
```python
def agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    pass
```

---

## Troubleshooting

### Agent Not Running

**Check execution plan:**
```python
print(state["execution_plan"])
# Should show: {"my_agent": true}
```

**Check orchestrator mapping:**
```python
# In orchestrator.py
if agent_name == "my_agent":  # Must match plan key
    tasks.append(...)
```

### State Not Updating

**Check state merging:**
```python
# Agent must return updated state
return state  # ✅ Good
return {}     # ❌ Bad - loses data
```

**Check for exceptions:**
```python
print(state.get("agent_errors"))
print(state.get("logs"))
```

### Import Errors

**Check module paths:**
```python
# Correct
from agents.my_agent import my_agent_node

# Incorrect
from backend.agents.my_agent import my_agent_node  # Don't use 'backend' prefix
```

**Check __init__.py exists:**
```bash
touch backend/agents/__init__.py
```

---

## Summary

✅ **Integrated Components:**
- Master agent for query parsing
- Clinical trials agent (node-based)
- Patent agent (node-based)
- Internal insights agent (class-based)
- Web intel agent (class-based)
- Drug analyzer agent (class-based)
- Report generator (node-based)

✅ **Created Files:**
- `backend/utils/http_client.py` - HTTP client for external APIs
- `backend/prompts.py` - Report templates
- `docs/MCP_AGENT_INTEGRATION.md` - This guide

✅ **Updated Files:**
- `backend/mcp/orchestrator.py` - Supports both agent types
- `backend/config.py` - Added API configuration
- `backend/tools/internal_rag_tool.py` - Added helper functions

✅ **Ready to Use:**
- Start server: `uvicorn mcp.server:app --reload --port 8001`
- Test endpoint: `POST /mcp/orchestrate`
- All agents integrated and working

Your MCP architecture is now fully configured and ready for production!
