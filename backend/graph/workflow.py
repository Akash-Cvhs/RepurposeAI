from __future__ import annotations

import time
from typing import Any, Dict, TypedDict, cast

from langgraph.graph import END, StateGraph

from backend.agents import (
    clinical_trials_agent_node,
    internal_insights_agent_node,
    master_agent_node,
    patent_agent_node,
    report_generator_agent_node,
    web_intel_agent_node,
)


class WorkflowState(TypedDict, total=False):
    request_id: str
    query: str
    molecule: str
    indication: str
    query_plan: list[dict]
    master_confidence: str
    trials: list[dict]
    patents: list[dict]
    fto_risk: str
    internal_insights: list[str] | str
    web_findings: list[str] | str
    report_path: str
    summary: str
    risk_assumptions: list[str]
    logs: list[str]
    agent_errors: dict[str, dict[str, str]]
    agent_metrics: dict[str, dict[str, float | str]]
    uploaded_pdf_paths: list[str]
    use_live_apis: bool
    archive_run: bool


def _timed_node(node_name: str, fn):
    def _wrapped(state: Dict[str, Any]) -> Dict[str, Any]:
        start = time.perf_counter()

        metrics = state.get("agent_metrics")
        if not isinstance(metrics, dict):
            metrics = {}
            state["agent_metrics"] = metrics

        logs = state.get("logs")
        if not isinstance(logs, list):
            logs = []
            state["logs"] = logs

        try:
            updated = fn(state)
            status = "ok"
            return_state = updated
        except Exception as exc:  # noqa: BLE001
            status = "failed"
            errors = state.get("agent_errors")
            if not isinstance(errors, dict):
                errors = {}
                state["agent_errors"] = errors
            errors[node_name] = {
                "code": f"{node_name.upper()}_UNHANDLED_EXCEPTION",
                "message": str(exc),
            }
            logs.append(f"[{node_name}] unhandled error: {exc}")
            return_state = state

        elapsed_ms = (time.perf_counter() - start) * 1000.0
        metrics[node_name] = {
            "latency_ms": round(elapsed_ms, 3),
            "status": status,
        }
        return return_state

    return _wrapped


def build_workflow_graph():
    graph = StateGraph(WorkflowState)

    graph.add_node("master", cast(Any, _timed_node("master", master_agent_node)))
    graph.add_node("clinical_trials", cast(Any, _timed_node("clinical_trials", clinical_trials_agent_node)))
    graph.add_node("patent_landscape", cast(Any, _timed_node("patent_landscape", patent_agent_node)))
    graph.add_node("internal_insights", cast(Any, _timed_node("internal_insights", internal_insights_agent_node)))
    graph.add_node("web_intel", cast(Any, _timed_node("web_intel", web_intel_agent_node)))
    graph.add_node("report_generator", cast(Any, _timed_node("report_generator", report_generator_agent_node)))

    graph.set_entry_point("master")
    graph.add_edge("master", "clinical_trials")
    graph.add_edge("clinical_trials", "patent_landscape")
    graph.add_edge("patent_landscape", "internal_insights")
    graph.add_edge("internal_insights", "web_intel")
    graph.add_edge("web_intel", "report_generator")
    graph.add_edge("report_generator", END)

    return graph.compile()
