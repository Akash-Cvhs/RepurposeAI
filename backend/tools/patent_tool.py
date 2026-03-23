"""
Patent Analysis MCP Tool

Analyzes patent landscape and computes freedom-to-operate risk.
Can be invoked independently via MCP protocol.
"""

from typing import Dict, Any, List
from datetime import date
from urllib.parse import parse_qsl, urlsplit
import pandas as pd

from config import (
    ENABLE_LIVE_APIS,
    PATENTS_CSV_PATH,
    SERPAPI_API_KEY,
    SERPAPI_API_URL,
    SERPAPI_ENGINE,
    SERPAPI_MAX_RESULTS,
    SERPAPI_TIMEOUT_SECONDS,
)
from utils.http_client import request_json


def _extract_year(text: str) -> int | None:
    """Extract year from date string"""
    if not text:
        return None
    for token in text.replace("/", "-").split("-"):
        if token.isdigit() and len(token) == 4:
            return int(token)
    return None


def _estimate_expiry_date(item: Dict[str, Any]) -> str:
    """Estimate patent expiry date (20 years from filing/grant)"""
    publication = str(item.get("publication_date", ""))
    filing = str(item.get("filing_date", ""))
    grant = str(item.get("grant_date", ""))

    base_year = _extract_year(grant) or _extract_year(publication) or _extract_year(filing)
    if not base_year:
        return ""

    expiry_year = base_year + 20
    return f"{expiry_year}-12-31"


def _normalize_live_patent(item: Dict[str, Any], molecule: str) -> Dict[str, Any]:
    """Normalize live API response to standard format"""
    title = str(item.get("title", ""))
    snippet = str(item.get("snippet", ""))
    patent_id = str(item.get("publication_number") or item.get("patent_id") or "")
    assignee = str(item.get("assignee") or item.get("assignee_name") or "")
    
    jurisdiction = ""
    publication_number = str(item.get("publication_number") or "")
    if publication_number and len(publication_number) >= 2:
        jurisdiction = publication_number[:2]
    elif patent_id and len(patent_id) >= 2:
        jurisdiction = patent_id[:2]

    expiry_date = _estimate_expiry_date(item)

    return {
        "patent_id": patent_id,
        "title": title,
        "molecule": molecule,
        "jurisdiction": jurisdiction,
        "expiry_date": expiry_date,
        "assignee": assignee,
        "claims_summary": snippet,
        "source": "serpapi_google_patents",
        "url": str(item.get("patent_link") or item.get("link") or ""),
    }


def _fetch_patents_live(molecule: str, indication: str) -> List[Dict[str, Any]]:
    """Fetch patents from SerpAPI"""
    if not SERPAPI_API_KEY:
        raise RuntimeError("SERPAPI_API_KEY is not configured")
    if not molecule:
        return []

    query = molecule if not indication else f"{molecule} {indication}"

    split_url = urlsplit(SERPAPI_API_URL)
    base_url = split_url._replace(query="").geturl()
    url_params = dict(parse_qsl(split_url.query, keep_blank_values=False))

    request_params = {
        **url_params,
        "engine": SERPAPI_ENGINE,
        "q": query,
        "api_key": SERPAPI_API_KEY,
        "num": max(10, min(100, SERPAPI_MAX_RESULTS)),
    }

    payload = request_json(
        service="serpapi_patents",
        method="GET",
        url=base_url,
        params=request_params,
        timeout=SERPAPI_TIMEOUT_SECONDS,
    )
    
    patent_results = payload.get("patent_results", []) or payload.get("organic_results", []) or []
    normalized = [_normalize_live_patent(item, molecule=molecule) for item in patent_results]

    if indication:
        indication_lower = indication.lower()
        filtered = [
            item for item in normalized
            if indication_lower in str(item.get("title", "")).lower()
            or indication_lower in str(item.get("claims_summary", "")).lower()
        ]
        if filtered:
            normalized = filtered

    return normalized


def _fetch_patents_from_csv(molecule: str) -> List[Dict[str, Any]]:
    """Fetch patents from local CSV (fallback)"""
    df = pd.read_csv(PATENTS_CSV_PATH)
    if molecule:
        df = df[df["molecule"].str.lower().str.contains(molecule, na=False)]
    records = df.to_dict(orient="records")
    return [{str(key): value for key, value in row.items()} for row in records]


def _compute_fto_risk(patents: List[Dict[str, Any]]) -> str:
    """Compute freedom-to-operate risk based on patent landscape"""
    if not patents:
        return "low"

    df = pd.DataFrame(patents)
    if "expiry_date" not in df.columns:
        df["expiry_date"] = ""

    today = date.today()
    expiries = pd.to_datetime(df["expiry_date"], errors="coerce").dt.date

    active_long = sum(1 for expiry in expiries if expiry and (expiry - today).days > 730)
    expiring_soon = sum(1 for expiry in expiries if expiry and 0 <= (expiry - today).days <= 730)
    expired = sum(1 for expiry in expiries if expiry and expiry < today)

    if active_long >= max(2, len(patents) // 2):
        return "high"
    if expiring_soon > 0 and expired > 0:
        return "medium"
    if active_long > 0:
        return "medium"
    return "low"


def search_patents(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    MCP Tool: Search patents and analyze FTO risk
    
    Args:
        payload: {
            "molecule": str (required) - Drug/molecule name
            "indication": str (optional) - Disease/indication
            "use_live_api": bool (optional) - Use live API vs CSV
        }
    
    Returns:
        {
            "patents": List[Dict] - List of patents
            "count": int - Number of patents found
            "fto_risk": str - "low", "medium", or "high"
            "source": str - Data source used
            "error": str (optional) - Error message if failed
        }
    """
    molecule = payload.get("molecule", "").strip().lower()
    indication = payload.get("indication", "").strip().lower()
    use_live_api = payload.get("use_live_api", ENABLE_LIVE_APIS)
    
    if not molecule:
        return {
            "patents": [],
            "count": 0,
            "fto_risk": "unknown",
            "source": "none",
            "error": "Molecule name is required"
        }
    
    # Try live API first if enabled
    if use_live_api and SERPAPI_API_KEY:
        try:
            patents = _fetch_patents_live(molecule=molecule, indication=indication)
            fto_risk = _compute_fto_risk(patents)
            return {
                "patents": patents,
                "count": len(patents),
                "fto_risk": fto_risk,
                "source": "serpapi",
                "molecule": molecule,
                "indication": indication or "any"
            }
        except Exception as exc:
            # Fallback to CSV
            pass
    
    # Use CSV data
    try:
        patents = _fetch_patents_from_csv(molecule=molecule)
        fto_risk = _compute_fto_risk(patents)
        return {
            "patents": patents,
            "count": len(patents),
            "fto_risk": fto_risk,
            "source": "local_csv",
            "molecule": molecule,
            "indication": indication or "any"
        }
    except Exception as exc:
        return {
            "patents": [],
            "count": 0,
            "fto_risk": "unknown",
            "source": "none",
            "error": str(exc)
        }
