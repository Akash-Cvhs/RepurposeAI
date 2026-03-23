from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader


def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract plain text from all pages in a PDF file."""
    reader = PdfReader(str(pdf_path))
    page_texts = []
    for page in reader.pages:
        page_texts.append(page.extract_text() or "")
    return "\n".join(page_texts).strip()
