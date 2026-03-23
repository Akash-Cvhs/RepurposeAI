from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from backend.utils.parsing_utils import extract_text_from_pdf
from backend.utils.llm_utils import summarize_text_with_llm


def _summarize_text(text: str, context: str = "") -> str:
    cleaned = " ".join(text.split())
    if not cleaned:
        return "No extractable text found in uploaded documents."

    try:
        llm_summary = summarize_text_with_llm(cleaned, context=context)
        if llm_summary:
            return llm_summary
    except Exception:
        # Soft-fail to deterministic summary in hackathon mode.
        pass

    return cleaned[:500] + ("..." if len(cleaned) > 500 else "")


def internal_insights_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logs = state.get("logs", [])
    agent_errors = state.get("agent_errors")
    if not isinstance(agent_errors, dict):
        agent_errors = {}
        state["agent_errors"] = agent_errors

    pdf_paths: List[str] = state.get("uploaded_pdf_paths", []) or []

    if not pdf_paths:
        state["internal_insights"] = "No internal documents uploaded."
        logs.append("[internal_insights] no PDFs uploaded; skipping")
        state["logs"] = logs
        return state

    insights = []
    for path_str in pdf_paths:
        pdf_path = Path(path_str)
        if not pdf_path.exists():
            insights.append(f"{pdf_path.name}: file not found")
            continue
        try:
            text = extract_text_from_pdf(pdf_path)
            context = f"molecule={state.get('molecule')}, indication={state.get('indication')}"
            insights.append(f"{pdf_path.name}: {_summarize_text(text, context=context)}")
        except Exception as exc:
            insights.append(f"{pdf_path.name}: extraction error ({exc})")
            agent_errors["internal_insights"] = {
                "code": "INTERNAL_INSIGHTS_EXTRACTION_FAILED",
                "message": str(exc),
            }

    state["internal_insights"] = insights
    logs.append(f"[internal_insights] processed {len(pdf_paths)} uploaded PDFs")
    state["logs"] = logs
    return state
