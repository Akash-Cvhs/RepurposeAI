from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import json
import os
from datetime import datetime
from graph.workflow import run_drug_repurposing_workflow
from utils.storage_utils import save_report, get_run_history

app = FastAPI(title="VHS Drug Repurposing API")

class QueryRequest(BaseModel):
    query: str
    molecule: Optional[str] = None
    
class RunResponse(BaseModel):
    run_id: str
    status: str
    report_path: Optional[str] = None

@app.post("/run", response_model=RunResponse)
async def run_analysis(request: QueryRequest):
    """Execute drug repurposing analysis workflow"""
    try:
        run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Execute workflow
        result = await run_drug_repurposing_workflow(
            query=request.query,
            molecule=request.molecule,
            run_id=run_id
        )
        
        # Save report and update archive
        report_path = save_report(run_id, result["report"], request.query, request.molecule)
        
        return RunResponse(
            run_id=run_id,
            status="completed",
            report_path=report_path
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/archives")
async def get_archives():
    """Get list of previous analysis runs"""
    try:
        return get_run_history()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)