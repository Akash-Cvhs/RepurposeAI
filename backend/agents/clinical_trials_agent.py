from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd

from backend.config import (
    CLINICAL_TRIALS_API_URL,
    CLINICAL_TRIALS_PAGE_SIZE,
    CLINICAL_TRIALS_TIMEOUT_SECONDS,
    ENABLE_LIVE_APIS,
    TRIALS_CSV_PATH,
)
from backend.utils.http_client import request_json


def _normalize_live_study(study: Dict[str, Any], molecule: str) -> Dict[str, Any]:
    protocol = study.get("protocolSection", {})
    identification = protocol.get("identificationModule", {})
    status = protocol.get("statusModule", {})
    conditions_module = protocol.get("conditionsModule", {})
    design_module = protocol.get("designModule", {})
    sponsor_module = protocol.get("sponsorCollaboratorsModule", {})
    locations_module = protocol.get("contactsLocationsModule", {})

    conditions = conditions_module.get("conditions", []) or []
    phases = design_module.get("phases", []) or []
    locations = locations_module.get("locations", []) or []
    lead_sponsor = sponsor_module.get("leadSponsor", {})

    location = ""
    if locations:
        first_location = locations[0]
        city = first_location.get("city", "")
        country = first_location.get("country", "")
        location = ", ".join([part for part in [city, country] if part])

    nct_id = identification.get("nctId", "")
    return {
        "nct_id": nct_id,
        "title": identification.get("briefTitle", ""),
        "molecule": molecule,
        "condition": "; ".join(str(item) for item in conditions if item),
        "phase": phases[0] if phases else "",
        "status": status.get("overallStatus", ""),
        "start_date": (status.get("startDateStruct") or {}).get("date", ""),
        "completion_date": (status.get("completionDateStruct") or {}).get("date", ""),
        "location": location,
        "sponsor": lead_sponsor.get("name", ""),
        "source": "clinicaltrials.gov",
        "url": f"https://clinicaltrials.gov/study/{nct_id}" if nct_id else "",
    }


def _fetch_trials_live(molecule: str, indication: str) -> List[Dict[str, Any]]:
    if not molecule:
        return []

    payload = request_json(
        service="clinicaltrials",
        method="GET",
        url=CLINICAL_TRIALS_API_URL,
        params={
            "query.term": molecule,
            "pageSize": CLINICAL_TRIALS_PAGE_SIZE,
        },
        timeout=CLINICAL_TRIALS_TIMEOUT_SECONDS,
    )
    studies = payload.get("studies", []) or []

    normalized = [_normalize_live_study(study, molecule) for study in studies]
    if indication:
        indication_lower = indication.lower()
        normalized = [
            item
            for item in normalized
            if indication_lower in str(item.get("condition", "")).lower()
            or indication_lower in str(item.get("title", "")).lower()
        ]

    return normalized


def _fetch_trials_from_csv(molecule: str, indication: str) -> List[Dict[str, Any]]:
    df = pd.read_csv(TRIALS_CSV_PATH)
    if molecule:
        df = df[df["molecule"].str.lower().str.contains(molecule, na=False)]
    if indication:
        df = df[df["condition"].str.lower().str.contains(indication, na=False)]
    records = df.to_dict(orient="records")
    return [{str(key): value for key, value in row.items()} for row in records]


def clinical_trials_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logs = state.get("logs", [])
    agent_errors = state.get("agent_errors")
    if not isinstance(agent_errors, dict):
        agent_errors = {}
        state["agent_errors"] = agent_errors

    molecule = (state.get("molecule") or "").strip().lower()
    indication = (state.get("indication") or "").strip().lower()
    use_live_apis = bool(state.get("use_live_apis", ENABLE_LIVE_APIS))

    if molecule and use_live_apis:
        try:
            trials = _fetch_trials_live(molecule=molecule, indication=indication)
            logs.append(f"[clinical_trials] live API fetched {len(trials)} trials")
        except Exception as exc:
            logs.append(f"[clinical_trials] live API unavailable: {exc}; using local CSV fallback")
            try:
                trials = _fetch_trials_from_csv(molecule=molecule, indication=indication)
            except Exception as csv_exc:
                state["trials"] = []
                agent_errors["clinical_trials"] = {
                    "code": "CLINICAL_TRIALS_DATA_UNAVAILABLE",
                    "message": str(csv_exc),
                }
                logs.append(f"[clinical_trials] error: {csv_exc}")
                state["logs"] = logs
                return state
    else:
        try:
            trials = _fetch_trials_from_csv(molecule=molecule, indication=indication)
            if use_live_apis and not molecule:
                logs.append(f"[clinical_trials] molecule missing; CSV fetched {len(trials)} trials")
            else:
                logs.append(f"[clinical_trials] mock CSV fetched {len(trials)} trials")
        except Exception as csv_exc:
            state["trials"] = []
            agent_errors["clinical_trials"] = {
                "code": "CLINICAL_TRIALS_DATA_UNAVAILABLE",
                "message": str(csv_exc),
            }
            logs.append(f"[clinical_trials] error: {csv_exc}")
            state["logs"] = logs
            return state

    try:
        state["trials"] = trials
        logs.append(f"[clinical_trials] final trial count={len(trials)}")
    except Exception as exc:
        state["trials"] = []
        agent_errors["clinical_trials"] = {
            "code": "CLINICAL_TRIALS_STATE_UPDATE_FAILED",
            "message": str(exc),
        }
        logs.append(f"[clinical_trials] error: {exc}")

    state["logs"] = logs
    return state
