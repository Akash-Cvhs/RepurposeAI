import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from config import REPORTS_DIR, RUNS_INDEX_FILE
from utils.pdf_utils import generate_report_pdf

def save_report(run_id: str, report_content: str, query: str, molecule: str = None) -> str:
    """Save report and update run history"""
    
    # Generate PDF
    pdf_path = generate_report_pdf(report_content, str(REPORTS_DIR), run_id)
    
    # Update run history
    run_record = {
        "id": run_id,
        "query": query,
        "molecule": molecule,
        "timestamp": datetime.now().isoformat(),
        "report_path": str(pdf_path),
        "status": "completed"
    }
    
    update_run_history(run_record)
    
    return str(pdf_path)

def update_run_history(run_record: Dict[str, Any]) -> None:
    """Update the runs index file"""
    
    # Load existing history
    history = get_run_history()
    
    # Add new record
    history.append(run_record)
    
    # Keep only last 100 runs
    history = history[-100:]
    
    # Save updated history
    RUNS_INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(RUNS_INDEX_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def get_run_history() -> List[Dict[str, Any]]:
    """Get list of previous runs"""
    
    if not RUNS_INDEX_FILE.exists():
        return []
    
    try:
        with open(RUNS_INDEX_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def get_report_by_id(run_id: str) -> Dict[str, Any]:
    """Get specific report by run ID"""
    
    history = get_run_history()
    
    for run in history:
        if run["id"] == run_id:
            return run
    
    return None