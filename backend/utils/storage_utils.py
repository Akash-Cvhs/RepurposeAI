from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from backend.config import ARCHIVES_DIR, RUNS_INDEX_PATH


def _ensure_archive_index() -> None:
    ARCHIVES_DIR.mkdir(parents=True, exist_ok=True)
    if not RUNS_INDEX_PATH.exists():
        RUNS_INDEX_PATH.write_text("[]\n", encoding="utf-8")


def read_archive_entries() -> List[Dict[str, Any]]:
    _ensure_archive_index()
    raw = RUNS_INDEX_PATH.read_text(encoding="utf-8").strip() or "[]"
    try:
        entries = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if not isinstance(entries, list):
        return []
    return entries


def append_archive_entry(state: Dict[str, Any]) -> Dict[str, Any]:
    entries = read_archive_entries()
    entry = {
        "id": str(uuid4()),
        "query": state.get("query"),
        "molecule": state.get("molecule"),
        "indication": state.get("indication"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "report_path": state.get("report_path"),
    }
    entries.append(entry)
    tmp_path = Path(f"{RUNS_INDEX_PATH}.tmp")
    tmp_path.write_text(json.dumps(entries, indent=2), encoding="utf-8")
    tmp_path.replace(RUNS_INDEX_PATH)
    return entry
