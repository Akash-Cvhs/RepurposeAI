from __future__ import annotations

import json
from typing import Any, Dict, List

from backend.config import (
    ENABLE_LIVE_APIS,
    GUIDELINES_JSON_PATH,
    TAVILY_API_KEY,
    TAVILY_API_URL,
    TAVILY_MAX_RESULTS,
    TAVILY_TIMEOUT_SECONDS,
)
from backend.utils.http_client import request_json


def _build_web_query(molecule: str, indication: str) -> str:
    parts = [
        molecule.strip(),
        indication.strip(),
        "treatment guideline",
        "clinical evidence",
        "drug repurposing",
    ]
    return " ".join(part for part in parts if part).strip()


def _fetch_tavily_findings(molecule: str, indication: str) -> List[str]:
    if not TAVILY_API_KEY:
        raise RuntimeError("TAVILY_API_KEY is not configured")

    query = _build_web_query(molecule=molecule, indication=indication)
    if not query:
        return []

    payload = request_json(
        service="tavily",
        method="POST",
        url=TAVILY_API_URL,
        json_body={
            "api_key": TAVILY_API_KEY,
            "query": query,
            "search_depth": "advanced",
            "max_results": TAVILY_MAX_RESULTS,
            "include_answer": False,
            "include_images": False,
            "include_raw_content": False,
        },
        timeout=TAVILY_TIMEOUT_SECONDS,
    )
    results = payload.get("results", []) or []

    findings = []
    for item in results:
        title = str(item.get("title", "")).strip()
        content = str(item.get("content", "")).strip()
        url = str(item.get("url", "")).strip()

        if not any([title, content, url]):
            continue

        summary = content[:300] + ("..." if len(content) > 300 else "")
        findings.append(f"{title}: {summary} (source: Tavily, {url})")

    return findings


def _fetch_mock_findings(molecule: str, indication: str) -> List[str]:
    entries: List[Dict[str, Any]] = json.loads(GUIDELINES_JSON_PATH.read_text(encoding="utf-8"))
    filtered = entries
    if molecule:
        filtered = [e for e in filtered if molecule in str(e.get("molecule", "")).lower()]
    if indication:
        filtered = [e for e in filtered if indication in str(e.get("disease", "")).lower()]

    findings = []
    for item in filtered:
        findings.append(
            f"{item.get('guideline_title')}: {item.get('summary')} (source: {item.get('source')}, {item.get('url')})"
        )
    return findings


def web_intel_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logs = state.get("logs", [])
    agent_errors = state.get("agent_errors")
    if not isinstance(agent_errors, dict):
        agent_errors = {}
        state["agent_errors"] = agent_errors

    molecule = (state.get("molecule") or "").strip().lower()
    indication = (state.get("indication") or "").strip().lower()
    use_live_apis = bool(state.get("use_live_apis", ENABLE_LIVE_APIS))

    if use_live_apis:
        try:
            findings = _fetch_tavily_findings(molecule=molecule, indication=indication)
            state["web_findings"] = findings
            logs.append(f"[web_intel] Tavily fetched {len(findings)} web findings")
        except Exception as tavily_exc:
            logs.append(f"[web_intel] Tavily unavailable: {tavily_exc}; using mock guidelines")
            try:
                findings = _fetch_mock_findings(molecule=molecule, indication=indication)
                state["web_findings"] = findings
                logs.append(f"[web_intel] mock guidelines fetched {len(findings)} entries")
            except Exception as exc:
                state["web_findings"] = []
                agent_errors["web_intel"] = {
                    "code": "WEB_INTEL_DATA_UNAVAILABLE",
                    "message": str(exc),
                }
                logs.append(f"[web_intel] error: {exc}")
    else:
        try:
            findings = _fetch_mock_findings(molecule=molecule, indication=indication)
            state["web_findings"] = findings
            logs.append(f"[web_intel] mock guidelines fetched {len(findings)} entries")
        except Exception as exc:
            state["web_findings"] = []
            agent_errors["web_intel"] = {
                "code": "WEB_INTEL_DATA_UNAVAILABLE",
                "message": str(exc),
            }
            logs.append(f"[web_intel] error: {exc}")

    state["logs"] = logs
    return state
