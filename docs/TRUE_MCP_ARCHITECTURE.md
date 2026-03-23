# True MCP Protocol Architecture

## Overview

Your system now follows **true MCP (Model Context Protocol)** architecture where:
- ✅ All agents are **MCP tools** that can be invoked independently
- ✅ Tools are registered in MCP server and called via protocol
- ✅ LLM decides which tools to call and in what order
- ✅ Tools can have dependencies (tool A waits for tool B)
- ✅ No linear workflow - dynamic, intelligent orchestration

---

## Architecture Diagram

```
User Query
    ↓
POST /mcp/orchestrate
    ↓
Intelligent Orchestrator
    ├─ LLM analyzes query
    ├─ Creates execution plan
    ├─ Determines tool dependencies
    └─ Decides invocation order
    ↓
MCP Server (Tool Registry)
    ├─ search_clinical_trials
    ├─ search_patents
    ├─ internal_rag
    ├─ gather_web_intelligence
    ├─ search_smiles
    ├─ analyze_smiles
    ├─ get_drug_smiles
    └─ list_drug_categories
    ↓
Parallel/Sequential Tool Execution
    ├─ Tools with no dependencies run in parallel
    ├─ Dependent tools wait for prerequisites
    └─ Results cached and passed between tools
    ↓
LLM Synthesis
    ├─ Analyzes all tool results
    ├─ Generates comprehensive report
    └─ Returns structured response
```

---

## Key Differences from Previous Architecture

### Before (Linear Workflow)
```python
# ❌ Old way - hardcoded linear flow
state = master_agent(state)
state = clinical_trials_agent(state)
state = patent_agent(state)
state = report_generator(state)
```

### Now (MCP Protocol)
```python
# ✅ New way - LLM decides dynamically
plan = llm.analyze_query(query)
# Plan might be:
# 1. get_drug_smiles (get SMILES first)
# 2. analyze_smiles (depends on #1)
# 3. search_clinical_trials (parallel with #2)
# 4. search_patents (parallel with #2)

results = execute_plan(plan)  # Handles dependencies automatically
report = llm.synthesize(results)
```

---

## Registered MCP Tools

### 1. Clinical Trials Tool
**Name:** `search_clinical_trials`
**File:** `backend/tools/clinical_trials_tool.py`

**Parameters:**
```json
{
  "molecule": "string (required)",
  "indication": "string (optional)",
  "use_live_api": "boolean (optional, default: false)"
}
```

**Returns:**
```json
{
  "trials": [...],
  "count": 15,
  "source": "clinicaltrials.gov",
  "molecule": "Donepezil",
  "indication": "Alzheimer's"
}
```

**Example:**
```bash
curl -X POST http://localhost:8001/mcp/run \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "search_clinical_trials",
    "payload": {
      "molecule": "Donepezil",
      "indication": "Alzheimer"
    },
    "session_id": "test"
  }'
```

---

### 2. Patent Search Tool
**Name:** `search_patents`
**File:** `backend/tools/patent_tool.py`

**Parameters:**
```json
{
  "molecule": "string (required)",
  "indication": "string (optional)",
  "use_live_api": "boolean (optional)"
}
```

**Returns:**
```json
{
  "patents": [...],
  "count": 23,
  "fto_risk": "medium",
  "source": "serpapi",
  "molecule": "Donepezil"
}
```

---

### 3. Internal RAG Tool
**Name:** `internal_rag`
**File:** `backend/tools/internal_rag_tool.py`

**Parameters:**
```json
{
  "query": "string (required)",
  "top_k": "integer (optional, default: 5)"
}
```

**Returns:**
```json
{
  "query": "clinical trial results",
  "results": [
    {
      "text": "...",
      "source": "report.pdf",
      "score": 0.85
    }
  ]
}
```

---

### 4. Web Intelligence Tool
**Name:** `gather_web_intelligence`
**File:** `backend/tools/web_intel_tool.py`

**Parameters:**
```json
{
  "query": "string (optional)",
  "molecule": "string (optional)",
  "indication": "string (optional)",
  "focus": "string (optional: market/competitive/regulatory/all)"
}
```

**Returns:**
```json
{
  "intelligence": "Market analysis text...",
  "focus_areas": ["Market size", "Competitive landscape"],
  "sources": ["mock_data"],
  "confidence": 0.6
}
```

---

### 5. SMILES Search Tool
**Name:** `search_smiles`
**File:** `backend/tools/smiles_analyzer_tool.py`

**Parameters:**
```json
{
  "query": "string (required)",
  "exact_match": "boolean (optional)"
}
```

**Returns:**
```json
{
  "results": [
    {
      "name": "Donepezil",
      "category": "Alzheimer's",
      "smiles": "CC(C)NCC(COc1ccccc1CC=C)O"
    }
  ]
}
```

---

### 6. SMILES Analysis Tool
**Name:** `analyze_smiles`
**File:** `backend/tools/smiles_analyzer_tool.py`

**Parameters:**
```json
{
  "smiles": "string (required)",
  "include_admet": "boolean (optional)",
  "include_variants": "boolean (optional)"
}
```

**Returns:**
```json
{
  "molecular_weight": 379.49,
  "logp": 4.2,
  "num_h_donors": 1,
  "num_h_acceptors": 4,
  "passes_lipinski": true,
  "admet": {...}
}
```

---

### 7. Get Drug SMILES Tool
**Name:** `get_drug_smiles`
**File:** `backend/tools/smiles_analyzer_tool.py`

**Parameters:**
```json
{
  "drug_name": "string (required)"
}
```

**Returns:**
```json
{
  "drug_name": "Donepezil",
  "category": "Alzheimer's",
  "smiles": "CC(C)NCC(COc1ccccc1CC=C)O"
}
```

---

### 8. List Drug Categories Tool
**Name:** `list_drug_categories`
**File:** `backend/tools/smiles_analyzer_tool.py`

**Parameters:** None

**Returns:**
```json
{
  "categories": [
    {"category": "Alzheimer's", "count": 7},
    {"category": "Tumor", "count": 9}
  ]
}
```

---

## Intelligent Orchestration Flow

### Step 1: Query Analysis

**Input:**
```json
{
  "query": "Analyze Donepezil for Alzheimer's treatment",
  "molecule": "Donepezil"
}
```

**LLM Analysis:**
```json
{
  "molecule": "Donepezil",
  "indication": "Alzheimer's",
  "tools": [
    {
      "name": "get_drug_smiles",
      "params": {"drug_name": "Donepezil"},
      "depends_on": [],
      "reasoning": "Need SMILES for molecular analysis"
    },
    {
      "name": "analyze_smiles",
      "params": {"smiles": "...", "include_admet": true},
      "depends_on": ["get_drug_smiles"],
      "reasoning": "Analyze molecular properties"
    },
    {
      "name": "search_clinical_trials",
      "params": {"molecule": "Donepezil", "indication": "Alzheimer's"},
      "depends_on": [],
      "reasoning": "Find clinical evidence"
    },
    {
      "name": "search_patents",
      "params": {"molecule": "Donepezil", "indication": "Alzheimer's"},
      "depends_on": [],
      "reasoning": "Assess patent landscape"
    }
  ],
  "reasoning": "Comprehensive analysis requires molecular properties, clinical evidence, and patent landscape"
}
```

### Step 2: Dependency Resolution

**Execution Order:**
```
Round 1 (Parallel):
  - get_drug_smiles
  - search_clinical_trials
  - search_patents

Round 2 (After get_drug_smiles completes):
  - analyze_smiles (uses SMILES from Round 1)
```

### Step 3: Tool Execution

Each tool is called via MCP protocol:
```python
request = MCPRequest(
    tool_name="search_clinical_trials",
    payload={"molecule": "Donepezil", "indication": "Alzheimer's"},
    session_id="session_123"
)
result = await mcp.handle(request)
```

### Step 4: Result Synthesis

LLM receives all tool results and generates comprehensive report:
```markdown
# Drug Repurposing Analysis: Donepezil for Alzheimer's

## Executive Summary
Donepezil shows strong evidence for Alzheimer's treatment with 15 clinical trials...

## Clinical Evidence
Found 15 clinical trials, including 3 Phase 3 studies...

## Patent Landscape
Identified 23 patents with medium FTO risk...

## Molecular Analysis
Molecular weight: 379.49 g/mol
Passes Lipinski's Rule of Five: Yes
...
```

---

## Example Queries and Tool Selection

### Query 1: "What drugs are available for Alzheimer's?"
**Tools Selected:**
- `search_smiles` (query="Alzheimer")
- `search_clinical_trials` (indication="Alzheimer's")
- `internal_rag` (query="Alzheimer's treatment")

### Query 2: "Analyze molecular properties of Donepezil"
**Tools Selected:**
- `get_drug_smiles` (drug_name="Donepezil")
- `analyze_smiles` (depends on get_drug_smiles)

### Query 3: "Patent landscape for metformin in cancer"
**Tools Selected:**
- `search_patents` (molecule="metformin", indication="cancer")
- `search_clinical_trials` (molecule="metformin", indication="cancer")

### Query 4: "Market opportunity for aspirin repurposing"
**Tools Selected:**
- `gather_web_intelligence` (molecule="aspirin", focus="market")
- `search_clinical_trials` (molecule="aspirin")

---

## Testing Individual Tools

### Test Clinical Trials Tool
```bash
curl -X POST http://localhost:8001/mcp/run \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "search_clinical_trials",
    "payload": {
      "molecule": "Donepezil",
      "indication": "Alzheimer"
    },
    "session_id": "test"
  }'
```

### Test Patent Tool
```bash
curl -X POST http://localhost:8001/mcp/run \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "search_patents",
    "payload": {
      "molecule": "metformin"
    },
    "session_id": "test"
  }'
```

### Test Full Orchestration
```bash
curl -X POST http://localhost:8001/mcp/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Analyze Donepezil for Alzheimer'\''s treatment",
    "molecule": "Donepezil"
  }'
```

---

## Benefits of True MCP Architecture

### 1. Flexibility
- LLM decides which tools to use based on query
- No hardcoded workflows
- Adapts to different types of questions

### 2. Efficiency
- Only runs necessary tools
- Parallel execution when possible
- Caching prevents redundant calls

### 3. Extensibility
- Add new tools without changing orchestrator
- Tools are independent and reusable
- Easy to test individual tools

### 4. Transparency
- Clear execution plan shows reasoning
- Tool results are traceable
- Easy to debug and optimize

### 5. Scalability
- Tools can be distributed across services
- Independent scaling of different tools
- Load balancing at tool level

---

## Adding New Tools

### Step 1: Create Tool Function
```python
# backend/tools/my_new_tool.py
def my_new_tool(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    MCP Tool: Description of what it does
    
    Args:
        payload: {
            "param1": str (required),
            "param2": int (optional)
        }
    
    Returns:
        {
            "result": Any,
            "error": str (optional)
        }
    """
    param1 = payload.get("param1")
    
    if not param1:
        return {"error": "param1 is required"}
    
    # Your logic here
    result = process(param1)
    
    return {"result": result}
```

### Step 2: Register in MCP Server
```python
# backend/mcp/server.py

# Import
from tools.my_new_tool import my_new_tool

# Create validator
class MyNewToolInput(BaseModel):
    param1: str
    param2: int = 0

# Add to validators
VALIDATORS["my_new_tool"] = MyNewToolInput

# Register tool
mcp.register_tool("my_new_tool", my_new_tool)
```

### Step 3: Update LLM Prompt
```python
# backend/mcp/intelligent_orchestrator.py

# Add to available tools list in prompt:
"""
8. my_new_tool - Description
   Params: param1 (required), param2 (optional)
"""
```

That's it! The tool is now available and LLM will automatically consider it when analyzing queries.

---

## Summary

✅ **True MCP Protocol Implementation:**
- All agents converted to MCP tools
- Tools registered in MCP server
- LLM-based intelligent orchestration
- Dynamic tool selection and ordering
- Dependency resolution
- Parallel execution where possible

✅ **8 MCP Tools Registered:**
1. search_clinical_trials
2. search_patents
3. internal_rag
4. gather_web_intelligence
5. search_smiles
6. analyze_smiles
7. get_drug_smiles
8. list_drug_categories

✅ **Key Files:**
- `backend/tools/clinical_trials_tool.py`
- `backend/tools/patent_tool.py`
- `backend/tools/web_intel_tool.py`
- `backend/mcp/intelligent_orchestrator.py`
- `backend/mcp/server.py`

Your system now follows true MCP architecture with intelligent, dynamic orchestration!
