from pathlib import Path
from typing import cast

from backend.graph.workflow import build_workflow_graph
from backend.graph.workflow import WorkflowState


def test_workflow_run_minimal_state() -> None:
    app = build_workflow_graph()

    initial_state: WorkflowState = {
        "query": "metformin for breast cancer",
        "logs": [],
        "uploaded_pdf_paths": [],
    }

    result = cast(WorkflowState, app.invoke(initial_state))

    assert result.get("molecule") == "metformin"
    assert "query_plan" in result
    assert "master_confidence" in result
    assert "trials" in result
    assert "patents" in result
    assert "web_findings" in result
    assert "summary" in result
    assert "risk_assumptions" in result
    assert "agent_metrics" in result
    assert isinstance(result["agent_metrics"], dict)
    report_path = result.get("report_path")
    assert isinstance(report_path, str) and report_path
    assert Path(report_path).exists()
