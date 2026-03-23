from __future__ import annotations

from copy import deepcopy
from typing import Any

_REPORT_TEMPLATE = {
    "title": "Innovation Product Story",
    "subtitle": "Repurposing {molecule_title} for {indication_title}",
    "objective_line": "Objective: Evaluate repurposing potential and innovation feasibility",
    "unmet_need_bullets": [
        "{indication_title} remains highly prevalent with persistent treatment resistance and recurrence in key subtypes.",
        "There is a need for cost-effective adjunct therapies with acceptable safety and broad accessibility.",
        "A validated repurposing strategy can accelerate innovation timelines and reduce development risk.",
    ],
    "conclusion_line": "This analysis demonstrates how an agentic AI workflow can rapidly synthesize evidence, reveal risks, and support data-driven innovation decisions.",
    "sections": {
        "context": "1. Context & Query",
        "unmet": "2. Unmet Medical Need",
        "clinical": "3. Clinical Trial Landscape",
        "patent": "4. Patent Landscape & FTO Analysis",
        "internal": "5. Internal Insights",
        "web": "6. Web Intelligence & Scientific Evidence",
        "synthesis": "7. Integrated Insight (AI Synthesis)",
        "opportunity": "8. Innovation Opportunity",
        "risks": "9. Risks & Assumptions",
        "recommendation": "10. Final Recommendation",
        "conclusion": "11. Conclusion",
        "references": "References",
    },
}


class _SafeDict(dict):
    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def get_report_template() -> dict[str, Any]:
    """Return a copy of the report narrative template for customization."""
    return deepcopy(_REPORT_TEMPLATE)


def _render_value(value: Any, context: dict[str, Any]) -> Any:
    if isinstance(value, str):
        return value.format_map(_SafeDict(context))
    if isinstance(value, list):
        return [_render_value(item, context) for item in value]
    if isinstance(value, dict):
        return {key: _render_value(item, context) for key, item in value.items()}
    return value


def render_report_template(context: dict[str, Any]) -> dict[str, Any]:
    """Render template placeholders with runtime context values."""
    base = get_report_template()
    return _render_value(base, context)
