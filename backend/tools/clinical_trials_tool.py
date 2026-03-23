"""
Clinical Trials MCP Tool

Searches clinical trial databases for efficacy and safety data.
Can be invoked independently via MCP protocol.
"""

from typing import Dict, Any, List
import pandas as pd
from config import (
    CLINICAL_TRIALS_API_URL,
    CLINICAL_TRIALS_PAGE_SIZE,
    CLINICAL_TRIALS_TIMEOUT_SECONDS,
    ENABLE_LIVE_APIS,
    TRIALS_CSV_PATH,
)
from utils.http_client import request_json


def _normalize_live_study(study: Dict[str, Any], molecule: str) -> Dict[str, Any]:
    """Normalize live API response to standard format"""
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
    """Fetch trials from ClinicalTrials.gov API"""
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
            item for item in normalized
            if indication_lower in str(item.get("condition", "")).lower()
            or indication_lower in str(item.get("title", "")).lower()
        ]

    return normalized


def _fetch_trials_from_csv(molecule: str, indication: str) -> List[Dict[str, Any]]:
    """Fetch trials from local CSV (fallback)"""
    df = pd.read_csv(TRIALS_CSV_PATH)
    if molecule:
        df = df[df["molecule"].str.lower().str.contains(molecule, na=False)]
    if indication:
        df = df[df["condition"].str.lower().str.contains(indication, na=False)]
    records = df.to_dict(orient="records")
    return [{str(key): value for key, value in row.items()} for row in records]


def search_clinical_trials(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    MCP Tool: Search clinical trials by molecule and indication
    
    Args:
        payload: {
            "molecule": str (required) - Drug/molecule name
            "indication": str (optional) - Disease/indication
            "use_live_api": bool (optional) - Use live API vs CSV
        }
    
    Returns:
        {
            "trials": List[Dict] - List of clinical trials
            "count": int - Number of trials found
            "source": str - Data source used
            "error": str (optional) - Error message if failed
        }
    """
    molecule = payload.get("molecule", "").strip().lower()
    indication = payload.get("indication", "").strip().lower()
    use_live_api = payload.get("use_live_api", ENABLE_LIVE_APIS)
    
    if not molecule:
        return {
            "trials": [],
            "count": 0,
            "source": "none",
            "error": "Molecule name is required"
        }
    
    # Try live API first if enabled
    if use_live_api:
        try:
            trials = _fetch_trials_live(molecule=molecule, indication=indication)
            return {
                "trials": trials,
                "count": len(trials),
                "source": "clinicaltrials.gov",
                "molecule": molecule,
                "indication": indication or "any"
            }
        except Exception as exc:
            # Fallback to CSV
            pass
    
    # Use CSV data
    try:
        trials = _fetch_trials_from_csv(molecule=molecule, indication=indication)
        return {
            "trials": trials,
            "count": len(trials),
            "source": "local_csv",
            "molecule": molecule,
            "indication": indication or "any"
        }
    except Exception as exc:
        return {
            "trials": [],
            "count": 0,
            "source": "none",
            "error": str(exc)
        }
