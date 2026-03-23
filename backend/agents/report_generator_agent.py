from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List

from backend.config import ENABLE_LIVE_APIS, SERPAPI_API_KEY, TAVILY_API_KEY
from backend.prompts import render_report_template
from backend.utils.pdf_utils import create_report_pdf
from backend.utils.storage_utils import append_archive_entry


def _slugify(parts: Iterable[str]) -> str:
    text = "-".join([p for p in parts if p]).strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "innovation-report"


def _format_list(items: List[Dict[str, Any]], key_fields: List[str]) -> List[str]:
    lines = []
    for item in items:
        values = [str(item.get(field, "")).strip() for field in key_fields]
        row = " | ".join(v for v in values if v)
        if row:
            lines.append(f"- {row}")
    return lines


def _build_risk_assumptions(
    fto_risk: str,
    has_internal_docs: bool,
    has_web_findings: bool,
    use_live_apis: bool,
) -> List[str]:
    provenance_note = (
        "This report combines live external connectors with local processing."
        if use_live_apis
        else "This report is generated from mock datasets for prototype demonstration."
    )
    lines = [
        provenance_note,
        "This output is not medical, regulatory, or legal advice.",
        "Clinical and legal review is mandatory before any portfolio decision.",
    ]

    normalized_risk = str(fto_risk).strip().lower()
    if normalized_risk == "high":
        lines.append("FTO risk is high; patent counsel review is strongly recommended.")
    elif normalized_risk == "medium":
        lines.append("FTO risk is medium; prioritize claim scope and expiry validation.")
    elif normalized_risk == "low":
        lines.append("FTO risk appears low in this mock run; validate against live patent data.")
    else:
        lines.append("FTO risk could not be confidently determined from available data.")

    if not has_internal_docs:
        lines.append("No internal PDFs were provided; internal evidence coverage is incomplete.")
    if not has_web_findings:
        lines.append("No guideline/web evidence matched; run broader web search for completeness.")

    return lines


def report_generator_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logs = state.get("logs", [])
    agent_errors = state.get("agent_errors")
    if not isinstance(agent_errors, dict):
        agent_errors = {}
        state["agent_errors"] = agent_errors

    molecule = state.get("molecule") or "unknown"
    indication = state.get("indication") or "unknown"
    trials = state.get("trials", []) or []
    patents = state.get("patents", []) or []
    fto_risk = state.get("fto_risk", "unknown")
    internal_insights = state.get("internal_insights", [])
    web_findings = state.get("web_findings", [])
    query_plan = state.get("query_plan", []) or []
    use_live_apis = bool(state.get("use_live_apis", ENABLE_LIVE_APIS))

    trial_lines = _format_list(trials, ["nct_id", "title", "phase", "status"]) or ["- No trial matches found."]
    patent_lines = _format_list(patents, ["patent_id", "title", "jurisdiction", "expiry_date"]) or ["- No patent matches found."]

    if isinstance(internal_insights, str):
        insight_lines = [f"- {internal_insights}"]
    else:
        insight_lines = [f"- {line}" for line in internal_insights] or ["- No internal insights available."]

    if isinstance(web_findings, str):
        web_lines = [f"- {web_findings}"]
    else:
        web_lines = [f"- {line}" for line in web_findings] or ["- No web intelligence findings."]

    query_plan_lines = []
    for step in query_plan:
        if not isinstance(step, dict):
            continue
        agent = str(step.get("agent", "")).strip()
        objective = str(step.get("objective", "")).strip()
        enabled = bool(step.get("enabled", False))
        status = "enabled" if enabled else "skipped"
        if agent or objective:
            query_plan_lines.append(f"- {agent}: {objective} ({status})")

    if not query_plan_lines:
        query_plan_lines = ["- No query plan available."]

    risk_lines = _build_risk_assumptions(
        fto_risk=fto_risk,
        has_internal_docs=not (
            isinstance(internal_insights, str)
            and internal_insights.strip().lower() == "no internal documents uploaded."
        ),
        has_web_findings=bool(web_findings),
        use_live_apis=use_live_apis,
    )

    connector_flags = [
        f"clinical_trials={'live' if use_live_apis else 'mock'}",
        f"patents={'live' if use_live_apis and bool(SERPAPI_API_KEY) else 'mock'}",
        f"web_intel={'live' if use_live_apis and bool(TAVILY_API_KEY) else 'mock'}",
    ]

    template = render_report_template(
        {
            "molecule": str(molecule),
            "indication": str(indication),
            "molecule_title": str(molecule).title(),
            "indication_title": str(indication).title(),
            "trial_count": len(trials),
            "patent_count": len(patents),
            "fto_risk": str(fto_risk),
        }
    )

    executive_summary = (
        f"Identified {len(trials)} trial signals and {len(patents)} patent records for {molecule} in {indication}. "
        f"Computed FTO risk is {fto_risk}."
    )

    markdown_lines = [
        "# Innovation Product Story",
        "",
        "## Executive Summary",
        f"- {executive_summary}",
        "",
        "## Context & Query",
        f"- Query: {state.get('query', '')}",
        f"- Molecule: {molecule}",
        f"- Indication: {indication}",
        "",
        "## Key Metrics",
        f"- Trial count: {len(trials)}",
        f"- Patent count: {len(patents)}",
        f"- Web findings: {len(web_findings) if isinstance(web_findings, list) else 1}",
        f"- Internal insight items: {len(internal_insights) if isinstance(internal_insights, list) else 1}",
        f"- FTO risk: {fto_risk}",
        "",
        "## Data Provenance",
        *[f"- {item}" for item in connector_flags],
        "",
        "## Orchestration Plan",
        *query_plan_lines,
        "",
        "## Unmet Medical Needs",
        f"- Candidate indication focus: {indication}",
        "",
        "## Clinical Trial Landscape",
        *trial_lines,
        "",
        "## Patent Landscape & FTO",
        f"- FTO risk: {fto_risk}",
        *patent_lines,
        "",
        "## Internal Insights",
        *insight_lines,
        "",
        "## Web Intelligence & Guidelines",
        *web_lines,
        "",
        "## Risks & Assumptions",
        *[f"- {line}" for line in risk_lines],
    ]

    markdown_str = "\n".join(markdown_lines)
    slug = _slugify([str(molecule), str(indication)])
    report_data = {
        "query": state.get("query", ""),
        "molecule": molecule,
        "indication": indication,
        "summary": (
            f"Found {len(trials)} trials and {len(patents)} patents for {molecule} in {indication}. "
            f"FTO risk is {fto_risk}."
        ),
        "trials": trials,
        "patents": patents,
        "fto_risk": fto_risk,
        "internal_insights": internal_insights,
        "web_findings": web_findings,
        "query_plan": query_plan,
        "risk_assumptions": risk_lines,
        "data_provenance": connector_flags,
        "template": template,
    }

    try:
        report_path = create_report_pdf(markdown_str, slug, report_data=report_data)
    except Exception as exc:
        agent_errors["report_generator"] = {
            "code": "REPORT_GENERATION_FAILED",
            "message": str(exc),
        }
        logs.append(f"[report_generator] error: {exc}")
        state["report_path"] = ""
        state["summary"] = "Report generation failed"
        state["risk_assumptions"] = risk_lines
        state["logs"] = logs
        return state

    state["report_path"] = report_path
    state["summary"] = (
        f"Found {len(trials)} trials and {len(patents)} patents for {molecule} in {indication}. "
        f"FTO risk is {fto_risk}."
    )
    state["risk_assumptions"] = risk_lines
    if bool(state.get("archive_run", False)):
        append_archive_entry(state)

    if bool(state.get("archive_run", False)):
        logs.append("[report_generator] report PDF generated and archived")
    else:
        logs.append("[report_generator] report PDF generated")
    state["logs"] = logs
    return state