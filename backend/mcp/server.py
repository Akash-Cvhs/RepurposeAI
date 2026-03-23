"""
MCP Server — FastAPI + async tool execution + TTL cache + session management

Endpoints:
    POST /mcp/run              Execute a registered tool
    GET  /mcp/tools            List available tools
    GET  /mcp/session/{id}     Inspect session history
    GET  /mcp/health           Health check

Run:
    cd backend
    uvicorn mcp.server:app --reload --port 8001
"""

import asyncio
import hashlib
import json
import time
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from tools.internal_rag_tool import internal_rag_tool
from tools.clinical_trials_tool import search_clinical_trials
from tools.patent_tool import search_patents
from tools.web_intel_tool import gather_web_intelligence
from tools.drug_analyzer_tool import analyze_drug
from tools.report_generator_tool import generate_report

app = FastAPI(title="VHS MCP Server", version="1.0.0")


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class MCPRequest(BaseModel):
    tool_name: str
    payload: Dict[str, Any]
    session_id: str = "default"


class InternalRAGInput(BaseModel):
    query: str
    top_k: int = 5


class ClinicalTrialsInput(BaseModel):
    molecule: str
    indication: str = ""
    use_live_api: bool = False


class PatentSearchInput(BaseModel):
    molecule: str
    indication: str = ""
    use_live_api: bool = False


class WebIntelInput(BaseModel):
    query: str = ""
    molecule: str = ""
    indication: str = ""
    focus: str = "all"  # market, competitive, regulatory, all


class DrugAnalyzerInput(BaseModel):
    action: str  # search, get_smiles, analyze, list_categories, full_analysis
    query: str = ""
    drug_name: str = ""
    smiles: str = ""
    disease: str = ""
    exact_match: bool = False
    include_admet: bool = True
    include_variants: bool = False
    generate_image: bool = False


class ReportGeneratorInput(BaseModel):
    query: str
    molecule: str = ""
    indication: str = ""
    tool_results: Dict[str, Any]
    format: str = "markdown"


class OrchestrationRequest(BaseModel):
    query: str
    molecule: str | None = None


# ---------------------------------------------------------------------------
# TTL Cache
# ---------------------------------------------------------------------------

class Cache:
    def __init__(self, default_ttl: int = 3600):
        self._store: Dict[str, Dict] = {}
        self.default_ttl = default_ttl

    def _key(self, tool_name: str, payload: dict) -> str:
        raw = f"{tool_name}:{json.dumps(payload, sort_keys=True)}"
        return hashlib.md5(raw.encode()).hexdigest()

    def get(self, tool_name: str, payload: dict) -> Any | None:
        item = self._store.get(self._key(tool_name, payload))
        if item and (time.time() - item["ts"]) < self.default_ttl:
            return item["value"]
        return None

    def set(self, tool_name: str, payload: dict, value: Any) -> None:
        self._store[self._key(tool_name, payload)] = {
            "value": value,
            "ts": time.time(),
        }


# ---------------------------------------------------------------------------
# Session Manager
# ---------------------------------------------------------------------------

class SessionManager:
    def __init__(self):
        self._sessions: Dict[str, Dict] = {}

    def get(self, session_id: str) -> Dict:
        if session_id not in self._sessions:
            self._sessions[session_id] = {"history": []}
        return self._sessions[session_id]

    def append(self, session_id: str, entry: dict) -> None:
        self.get(session_id)["history"].append(entry)


# ---------------------------------------------------------------------------
# Tool Registry
# ---------------------------------------------------------------------------

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Any] = {}

    def register(self, name: str, func) -> None:
        self._tools[name] = func

    def get(self, name: str):
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' is not registered.")
        return self._tools[name]

    def list_tools(self) -> list[str]:
        return list(self._tools.keys())


# ---------------------------------------------------------------------------
# MCP Core
# ---------------------------------------------------------------------------

VALIDATORS: Dict[str, type] = {
    "internal_rag": InternalRAGInput,
    "search_clinical_trials": ClinicalTrialsInput,
    "search_patents": PatentSearchInput,
    "gather_web_intelligence": WebIntelInput,
    "analyze_drug": DrugAnalyzerInput,
    "generate_report": ReportGeneratorInput,
}


class MCPServer:
    def __init__(self):
        self.cache = Cache()
        self.sessions = SessionManager()
        self.registry = ToolRegistry()

    def register_tool(self, name: str, func) -> None:
        self.registry.register(name, func)

    async def handle(self, req: MCPRequest) -> Dict[str, Any]:
        tool_name = req.tool_name
        payload = req.payload
        session_id = req.session_id

        # Validate payload if a schema exists for this tool
        if tool_name in VALIDATORS:
            payload = VALIDATORS[tool_name](**payload).dict()

        # Return cached result if available
        cached = self.cache.get(tool_name, payload)
        if cached is not None:
            return {"cached": True, "data": cached}

        tool = self.registry.get(tool_name)

        # Execute — supports both sync and async tools
        try:
            if asyncio.iscoroutinefunction(tool):
                result = await tool(payload)
            else:
                result = await asyncio.to_thread(tool, payload)
        except Exception as e:
            return {"error": str(e)}

        self.cache.set(tool_name, payload, result)
        self.sessions.append(session_id, {
            "tool": tool_name,
            "input": payload,
            "output": result,
            "ts": time.time(),
        })

        return {"cached": False, "data": result}


# ---------------------------------------------------------------------------
# Bootstrap — register tools
# ---------------------------------------------------------------------------

mcp = MCPServer()

# RAG & Document Search
mcp.register_tool("internal_rag", internal_rag_tool)

# Clinical & Patent Data
mcp.register_tool("search_clinical_trials", search_clinical_trials)
mcp.register_tool("search_patents", search_patents)

# Web Intelligence
mcp.register_tool("gather_web_intelligence", gather_web_intelligence)

# Drug Analysis (consolidated tool)
mcp.register_tool("analyze_drug", analyze_drug)

# Report Generation
mcp.register_tool("generate_report", generate_report)


# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------

@app.post("/mcp/run")
async def run_tool(req: MCPRequest):
    tool_name = req.tool_name
    if tool_name not in mcp.registry.list_tools():
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found.")
    return await mcp.handle(req)


@app.get("/mcp/tools")
def list_tools():
    return {"tools": mcp.registry.list_tools()}


@app.get("/mcp/session/{session_id}")
def get_session(session_id: str):
    return mcp.sessions.get(session_id)


@app.get("/mcp/health")
def health():
    return {"status": "ok", "tools": mcp.registry.list_tools()}


# ---------------------------------------------------------------------------
# Orchestration Endpoint — Main Entry Point
# ---------------------------------------------------------------------------

@app.post("/mcp/orchestrate")
async def orchestrate_analysis(req: OrchestrationRequest):
    """
    Main orchestration endpoint using intelligent MCP protocol.
    
    LLM analyzes query, decides which tools to call, executes via MCP,
    and synthesizes results into comprehensive report.
    """
    from mcp.intelligent_orchestrator import get_intelligent_orchestrator
    
    orchestrator = get_intelligent_orchestrator(mcp)
    
    try:
        result = await orchestrator.orchestrate(
            query=req.query,
            molecule=req.molecule
        )
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "query": req.query
        }


# ---------------------------------------------------------------------------
# Run Server
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
