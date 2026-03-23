from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from backend.config import DATA_DIR
from backend.prompts import MOLECULAR_VALIDATION_PROMPT

ADMET_PATH = DATA_DIR / "admet_scores.json"


def _load_admet_scores() -> dict[str, dict[str, float]]:
    if not ADMET_PATH.exists():
        return {}
    data = json.loads(ADMET_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return {}
    return data


class MolecularValidatorAgent:
    async def validate_molecule(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return molecular_validator_agent_node(state)


def molecular_validator_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logs = state.get("logs", [])
    molecule = str(state.get("molecule") or "").strip().lower()

    admet_scores = _load_admet_scores()
    record = admet_scores.get(molecule, {})

    if record:
        score = int(round(sum(float(v) for v in record.values()) / max(len(record), 1) * 100))
        factors = sorted(record.items(), key=lambda item: item[1], reverse=True)
        rationale = [f"{name}={value:.2f}" for name, value in factors[:3]]
        risks = [f"{name}={value:.2f}" for name, value in factors[-2:]]
    else:
        score = 50
        rationale = ["No ADMET baseline found; using neutral default"]
        risks = ["Insufficient molecular baseline data"]

    state["molecular_validation"] = {
        "confidence_score": max(0, min(100, score)),
        "rationale": rationale,
        "risks": risks,
        "prompt_used": MOLECULAR_VALIDATION_PROMPT,
    }
    logs.append(f"[molecular_validator] confidence score={state['molecular_validation']['confidence_score']}")
    state["logs"] = logs
    return state
