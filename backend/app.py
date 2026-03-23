"""
VHS Drug Repurposing Platform - Unified Backend API

Single endpoint with integrated MCP orchestration.
No separate MCP server needed - everything runs in one process.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path

# Import MCP components directly
from mcp.intelligent_orchestrator import IntelligentOrchestrator
from mcp.server import mcp

app = FastAPI(title="VHS Drug Repurposing API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Archives directory
ARCHIVES_DIR = Path(__file__).parent / "archives" / "reports"
ARCHIVES_DIR.mkdir(parents=True, exist_ok=True)

# Initialize orchestrator
orchestrator = IntelligentOrchestrator(mcp)


# ---------------------------------------------------------------------------
# Request/Response Models
# ---------------------------------------------------------------------------

class QueryRequest(BaseModel):
    query: str
    molecule: Optional[str] = None


class AgentResult(BaseModel):
    agent_name: str
    status: str
    result: str
    duration_ms: Optional[int] = None


class MolecularValidation(BaseModel):
    confidence_score: float
    admet: Dict[str, float]
    binding_affinity: str
    target_protein: str
    rationale: str


class RunResponse(BaseModel):
    run_id: str
    status: str
    report_path: Optional[str] = None
    report_text: Optional[str] = None
    agents: Optional[list[AgentResult]] = None
    molecular_validation: Optional[MolecularValidation] = None
    execution_plan: Optional[Dict[str, Any]] = None
    tool_results: Optional[Dict[str, Any]] = None


# ---------------------------------------------------------------------------
# Main Endpoints
# ---------------------------------------------------------------------------

@app.post("/run", response_model=RunResponse)
async def run_analysis(request: QueryRequest):
    """
    Execute drug repurposing analysis with intelligent MCP orchestration.
    
    This endpoint:
    1. Analyzes the query using LLM
    2. Decides which tools to invoke
    3. Executes tools via MCP protocol
    4. Synthesizes results into comprehensive report
    5. Saves report to file
    6. Transforms response for frontend compatibility
    """
    try:
        # Execute orchestration
        result = await orchestrator.orchestrate(
            query=request.query,
            molecule=request.molecule
        )
        
        # Extract data
        run_id = result.get("run_id", f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        report_text = result.get("report", "")
        status = "completed" if result.get("success") else "failed"
        
        # Save report to file
        report_path = None
        if report_text:
            report_filename = f"{run_id}_report.md"
            report_filepath = ARCHIVES_DIR / report_filename
            
            with open(report_filepath, "w", encoding="utf-8") as f:
                f.write(report_text)
            
            report_path = str(report_filepath)
        
        # Transform tool results into agent results for frontend
        agents = []
        tool_results = result.get("tool_results", {})
        
        # Map tool names to agent names
        tool_to_agent_map = {
            "search_patents": "patent",
            "search_clinical_trials": "clinical",
            "gather_web_intelligence": "web_intel",
            "internal_rag": "insights",
            "analyze_drug": "molecular_validator"
        }
        
        for tool_name, tool_result in tool_results.items():
            agent_name = tool_to_agent_map.get(tool_name, tool_name)
            
            if tool_result.get("error"):
                agents.append(AgentResult(
                    agent_name=agent_name,
                    status="failed",
                    result=f"Error: {tool_result['error']}"
                ))
            else:
                data = tool_result.get("data", {})
                
                # Format result based on tool type
                if tool_name == "search_patents":
                    count = data.get("count", 0)
                    fto_risk = data.get("fto_risk", "unknown")
                    result_text = f"{count} patents found. FTO risk: {fto_risk.upper()}"
                elif tool_name == "search_clinical_trials":
                    count = data.get("count", 0)
                    result_text = f"{count} clinical trials found"
                elif tool_name == "internal_rag":
                    count = len(data.get("results", []))
                    result_text = f"{count} internal documents found"
                elif tool_name == "gather_web_intelligence":
                    confidence = data.get("confidence", 0)
                    result_text = f"Intelligence gathered (confidence: {confidence:.2f})"
                elif tool_name == "analyze_drug":
                    result_text = "Molecular analysis completed"
                else:
                    result_text = "Completed"
                
                agents.append(AgentResult(
                    agent_name=agent_name,
                    status="done",
                    result=result_text
                ))
        
        # Extract molecular validation data from drug analyzer
        molecular_validation = None
        if "analyze_drug" in tool_results:
            drug_data = tool_results["analyze_drug"].get("data", {})
            
            # Extract ADMET if available
            admet_data = drug_data.get("admet", {})
            if admet_data:
                molecular_validation = MolecularValidation(
                    confidence_score=drug_data.get("confidence_score", 0.85),
                    admet={
                        "absorption": admet_data.get("absorption", 0.8),
                        "distribution": admet_data.get("distribution", 0.75),
                        "metabolism": admet_data.get("metabolism", 0.7),
                        "excretion": admet_data.get("excretion", 0.8),
                        "toxicity": admet_data.get("toxicity", 0.65)
                    },
                    binding_affinity=drug_data.get("binding_affinity", "Moderate"),
                    target_protein=drug_data.get("target_protein", "Unknown"),
                    rationale=drug_data.get("rationale", "Molecular analysis completed")
                )
        
        # Return response in frontend-compatible format
        return RunResponse(
            run_id=run_id,
            status=status,
            report_path=report_path,
            report_text=report_text,
            agents=agents,
            molecular_validation=molecular_validation,
            execution_plan=result.get("execution_plan"),
            tool_results=tool_results
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@app.get("/archives")
async def get_archives():
    """
    Get list of previous analysis runs from archives directory
    """
    try:
        archives = []
        
        if ARCHIVES_DIR.exists():
            for report_file in ARCHIVES_DIR.glob("*.md"):
                archives.append({
                    "filename": report_file.name,
                    "path": str(report_file),
                    "size": report_file.stat().st_size,
                    "created": datetime.fromtimestamp(
                        report_file.stat().st_ctime
                    ).isoformat()
                })
        
        return archives
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch archives: {str(e)}"
        )


@app.post("/upload")
async def upload_pdf(file: Any):
    """
    Upload PDF for internal insights analysis
    
    Note: This is a placeholder. In production, this would:
    1. Save the PDF to internal_docs directory
    2. Re-index the FAISS vector store
    3. Make it available for internal_rag tool
    """
    try:
        # For now, just acknowledge the upload
        return {
            "success": True,
            "message": "PDF upload acknowledged. Feature coming soon.",
            "filename": "uploaded_file.pdf"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """
    Health check endpoint - verifies all components are operational
    """
    try:
        # Check if tools are registered
        tools = mcp.registry.list_tools()
        
        return {
            "status": "healthy",
            "tools_registered": len(tools),
            "tools": tools,
            "archives_dir": str(ARCHIVES_DIR),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@app.get("/tools")
async def list_tools():
    """
    List all available MCP tools
    """
    return {
        "tools": mcp.registry.list_tools(),
        "count": len(mcp.registry.list_tools())
    }


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    print("=" * 60)
    print("🚀 VHS Drug Repurposing Platform - Backend Starting")
    print("=" * 60)
    print(f"📦 Registered Tools: {mcp.registry.list_tools()}")
    print(f"📁 Archives Directory: {ARCHIVES_DIR}")
    print(f"🌐 Server: http://localhost:8000")
    print("=" * 60)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
