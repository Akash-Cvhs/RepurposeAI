from __future__ import annotations

import re


def sanitize_query(value: str, max_length: int = 500) -> str:
    """Normalize user query for safer downstream processing."""
    cleaned = re.sub(r"\s+", " ", (value or "").strip())
    return cleaned[:max_length]


def is_pdf_filename(filename: str) -> bool:
    return bool(filename) and filename.lower().endswith(".pdf")
