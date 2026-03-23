from __future__ import annotations

from datetime import date
from typing import Any, Dict, List
from urllib.parse import parse_qsl, urlsplit

import pandas as pd

from backend.config import (
    ENABLE_LIVE_APIS,
    PATENTS_CSV_PATH,
    SERPAPI_API_KEY,
    SERPAPI_API_URL,
    SERPAPI_ENGINE,
    SERPAPI_MAX_RESULTS,
    SERPAPI_TIMEOUT_SECONDS,
)
from backend.utils.http_client import request_json


def _extract_year(text: str) -> int | None:
    if not text:
        return None
    for token in text.replace("/", "-").split("-"):
        if token.isdigit() and len(token) == 4:
            return int(token)
    return None


def _estimate_expiry_date(item: Dict[str, Any]) -> str:
    publication = str(item.get("publication_date", ""))
    filing = str(item.get("filing_date", ""))
    grant = str(item.get("grant_date", ""))

    base_year = _extract_year(grant) or _extract_year(publication) or _extract_year(filing)
    if not base_year:
        return ""

    # Simple proxy for demo: 20-year patent term estimate.
    expiry_year = base_year + 20
    return f"{expiry_year}-12-31"


def _normalize_live_patent(item: Dict[str, Any], molecule: str) -> Dict[str, Any]:
    title = str(item.get("title", ""))
    snippet = str(item.get("snippet", ""))
    patent_id = str(item.get("publication_number") or item.get("patent_id") or "")
    assignee = str(item.get("assignee") or item.get("assignee_name") or "")
    jurisdiction = ""
    publication_number = str(item.get("publication_number") or "")
    if publication_number and len(publication_number) >= 2:
        jurisdiction = publication_number[:2]
    elif patent_id.startswith("patent/"):
        patent_parts = patent_id.split("/")
        if len(patent_parts) >= 2 and len(patent_parts[1]) >= 2:
            jurisdiction = patent_parts[1][:2]
    elif patent_id and len(patent_id) >= 2:
        jurisdiction = patent_id[:2]

    expiry_date = _estimate_expiry_date(item)

    return {
        "patent_id": patent_id,
        "title": title,
        "molecule": molecule,
        "moa": "",
        "jurisdiction": jurisdiction,
        "expiry_date": expiry_date,
        "assignee": assignee,
        "claims_summary": snippet,
        "source": "serpapi_google_patents",
        "url": str(item.get("patent_link") or item.get("link") or ""),
    }


def _fetch_patents_live(molecule: str, indication: str) -> List[Dict[str, Any]]:
    if not SERPAPI_API_KEY:
        raise RuntimeError("SERPAPI_API_KEY is not configured")
    if not molecule:
        return []

    query = molecule if not indication else f"{molecule} {indication}"

    split_url = urlsplit(SERPAPI_API_URL)
    base_url = split_url._replace(query="").geturl()
    url_params = dict(parse_qsl(split_url.query, keep_blank_values=False))

    # URL query params are accepted, but explicit params below take precedence.
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
            item
            for item in normalized
            if indication_lower in str(item.get("title", "")).lower()
            or indication_lower in str(item.get("claims_summary", "")).lower()
        ]
        if filtered:
            normalized = filtered

    return normalized


def _fetch_patents_from_csv(molecule: str) -> List[Dict[str, Any]]:
    df = pd.read_csv(PATENTS_CSV_PATH)
    if molecule:
        df = df[df["molecule"].str.lower().str.contains(molecule, na=False)]
    records = df.to_dict(orient="records")
    return [{str(key): value for key, value in row.items()} for row in records]


def _compute_fto_risk(df: pd.DataFrame) -> str:
    if df.empty:
        return "low"

    today = date.today()
    expiries = pd.to_datetime(df["expiry_date"], errors="coerce").dt.date

    active_long = sum(1 for expiry in expiries if expiry and (expiry - today).days > 730)
    expiring_soon = sum(1 for expiry in expiries if expiry and 0 <= (expiry - today).days <= 730)
    expired = sum(1 for expiry in expiries if expiry and expiry < today)

    if active_long >= max(2, len(df) // 2):
        return "high"
    if expiring_soon > 0 and expired > 0:
        return "medium"
    if active_long > 0:
        return "medium"
    return "low"


def patent_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
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
            patents = _fetch_patents_live(molecule=molecule, indication=indication)
            logs.append(f"[patent_landscape] SerpAPI fetched {len(patents)} patents")
        except Exception as exc:
            logs.append(f"[patent_landscape] SerpAPI unavailable: {exc}; using local CSV fallback")
            try:
                patents = _fetch_patents_from_csv(molecule=molecule)
            except Exception as csv_exc:
                state["patents"] = []
                state["fto_risk"] = "unknown"
                agent_errors["patent_landscape"] = {
                    "code": "PATENT_DATA_UNAVAILABLE",
                    "message": str(csv_exc),
                }
                logs.append(f"[patent_landscape] error: {csv_exc}")
                state["logs"] = logs
                return state
    else:
        try:
            patents = _fetch_patents_from_csv(molecule=molecule)
            if use_live_apis and not molecule:
                logs.append(f"[patent_landscape] molecule missing; CSV fetched {len(patents)} patents")
            else:
                logs.append(f"[patent_landscape] mock CSV fetched {len(patents)} patents")
        except Exception as csv_exc:
            state["patents"] = []
            state["fto_risk"] = "unknown"
            agent_errors["patent_landscape"] = {
                "code": "PATENT_DATA_UNAVAILABLE",
                "message": str(csv_exc),
            }
            logs.append(f"[patent_landscape] error: {csv_exc}")
            state["logs"] = logs
            return state

    try:
        df = pd.DataFrame(patents)
        if "expiry_date" not in df.columns:
            df["expiry_date"] = ""
        fto_risk = _compute_fto_risk(df)

        state["patents"] = patents
        state["fto_risk"] = fto_risk
        logs.append(f"[patent_landscape] final count={len(patents)}, FTO risk={fto_risk}")
    except Exception as exc:
        state["patents"] = []
        state["fto_risk"] = "unknown"
        agent_errors["patent_landscape"] = {
            "code": "PATENT_STATE_UPDATE_FAILED",
            "message": str(exc),
        }
        logs.append(f"[patent_landscape] error: {exc}")

    state["logs"] = logs
    return state