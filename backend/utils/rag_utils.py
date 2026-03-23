from __future__ import annotations

from typing import List


def chunk_text(text: str, chunk_size: int = 600) -> List[str]:
    cleaned = " ".join((text or "").split())
    if not cleaned:
        return []
    return [cleaned[i : i + chunk_size] for i in range(0, len(cleaned), chunk_size)]


def simple_similarity_search(query: str, chunks: List[str], top_k: int = 3) -> List[str]:
    """Lightweight lexical overlap search as a mock RAG fallback."""
    query_terms = {term for term in (query or "").lower().split() if term}
    scored: list[tuple[int, str]] = []
    for chunk in chunks:
        words = set(chunk.lower().split())
        score = len(query_terms.intersection(words))
        scored.append((score, chunk))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [chunk for score, chunk in scored[:top_k] if score > 0] or chunks[:top_k]
