"""
Build the FAISS vector index from internal PDF reports.

Usage (run from repo root or backend/):
    cd backend
    python scripts/index_internal_docs.py
"""

import os
import sys
import pickle
from pathlib import Path

import fitz  # PyMuPDF
import faiss
from sentence_transformers import SentenceTransformer

# Resolve paths relative to this file so the script works from any cwd
BASE_DIR = Path(__file__).parent.parent
DOCS_PATH = BASE_DIR / "data" / "internal_docs"
INDEX_PATH = BASE_DIR / "vectorstore" / "faiss_index"

model = SentenceTransformer("all-MiniLM-L6-v2")


def extract_text(pdf_path: Path) -> str:
    doc = fitz.open(str(pdf_path))
    return " ".join(page.get_text() for page in doc)


def chunk_text(text: str, size: int = 200, overlap: int = 30) -> list[str]:
    words = text.split()
    chunks = []
    for i in range(0, len(words), size - overlap):
        chunk = " ".join(words[i : i + size])
        if chunk:
            chunks.append(chunk)
    return chunks


def main():
    if not DOCS_PATH.exists():
        print(f"ERROR: internal_docs directory not found: {DOCS_PATH}")
        sys.exit(1)

    pdf_files = list(DOCS_PATH.glob("*.pdf"))
    if not pdf_files:
        print(f"ERROR: No PDF files found in {DOCS_PATH}")
        sys.exit(1)

    all_chunks: list[str] = []
    metadata: list[dict] = []

    print(f"Processing {len(pdf_files)} PDFs from {DOCS_PATH}...\n")

    for pdf_path in pdf_files:
        print(f"  Loading: {pdf_path.name}")
        try:
            text = extract_text(pdf_path)
            chunks = chunk_text(text)
            for chunk in chunks:
                all_chunks.append(chunk)
                metadata.append({"source": pdf_path.name})
        except Exception as e:
            print(f"  WARNING: Could not process {pdf_path.name}: {e}")

    if not all_chunks:
        print("ERROR: No text extracted from PDFs.")
        sys.exit(1)

    print(f"\nTotal chunks: {len(all_chunks)}")
    print("Embedding chunks...")

    embeddings = model.encode(all_chunks, show_progress_bar=True)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    INDEX_PATH.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(INDEX_PATH / "index.faiss"))

    with open(INDEX_PATH / "meta.pkl", "wb") as f:
        pickle.dump({"chunks": all_chunks, "meta": metadata}, f)

    print(f"\nFAISS index saved to: {INDEX_PATH}")
    print("Done.")


if __name__ == "__main__":
    main()
