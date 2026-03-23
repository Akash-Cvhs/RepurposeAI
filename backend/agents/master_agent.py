from __future__ import annotations

import re
from typing import Any, Dict, Optional

# Small, explicit vocabulary for demo query parsing.
KNOWN_INDICATIONS = {
    "oncology",
    "cancer",
    "breast cancer",
    "lung cancer",
    "diabetes",
    "type 2 diabetes",
    "cardiology",
    "heart failure",
    "obesity",
    "neurology",
    "alzheimer",
    "parkinson",
    "arthritis",
}


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def _infer_indication(query: str) -> Optional[str]:
    normalized = _normalize_text(query)

    # Prefer longest match to avoid returning "cancer" when "breast cancer" is present.
    for term in sorted(KNOWN_INDICATIONS, key=len, reverse=True):
        if term in normalized:
            return term

    return None


def _infer_molecule(query: str, indication: Optional[str]) -> Optional[str]:
    normalized = _normalize_text(query)

    # Common phrasings in prompts: "metformin oncology", "metformin for breast cancer".
    tokens = [t for t in re.split(r"[^a-z0-9]+", normalized) if t]
    if not tokens:
        return None

    stopwords = {
        "find",
        "for",
        "in",
        "on",
        "about",
        "repurposing",
        "repurpose",
        "drug",
        "molecule",
        "indication",
        "innovation",
        "story",
        "report",
        "and",
        "or",
        "the",
        "of",
        "with",
    }

    indication_words = set((indication or "").split())
    for token in tokens:
        if token in stopwords or token in indication_words:
            continue
        if token.isdigit():
            continue
        return token

    return None


def master_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Parse query and initialize shared orchestration keys."""
    query = str(state.get("query", "")).strip()

    logs = state.get("logs")
    if not isinstance(logs, list):
        logs = []

    indication = _infer_indication(query) if query else None
    molecule = _infer_molecule(query, indication) if query else None

    query_plan = [
        {
            "agent": "clinical_trials",
            "objective": "Fetch trial landscape by molecule and indication",
            "enabled": bool(molecule or indication),
        },
        {
            "agent": "patent_landscape",
            "objective": "Assess patent signals and compute FTO risk",
            "enabled": bool(molecule),
        },
        {
            "agent": "internal_insights",
            "objective": "Summarize uploaded internal PDFs",
            "enabled": True,
        },
        {
            "agent": "web_intel",
            "objective": "Collect guideline and web evidence",
            "enabled": bool(molecule or indication),
        },
        {
            "agent": "report_generator",
            "objective": "Synthesize outputs into Innovation Product Story",
            "enabled": True,
        },
    ]

    confidence = "high" if molecule and indication else "medium" if (molecule or indication) else "low"

    state["query"] = query
    state["molecule"] = molecule
    state["indication"] = indication
    state["query_plan"] = query_plan
    state["master_confidence"] = confidence
    state["logs"] = logs
    logs.append(
        f"[master] parsed query; molecule={molecule or 'unknown'}, indication={indication or 'unknown'}, confidence={confidence}"
    )

    return state