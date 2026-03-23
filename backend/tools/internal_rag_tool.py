import faiss
import pickle
from pathlib import Path
from sentence_transformers import SentenceTransformer
from functools import lru_cache

# Always resolve relative to this file — safe regardless of cwd
BASE_DIR = Path(__file__).parent.parent
INDEX_PATH = BASE_DIR / "vectorstore" / "faiss_index"

model = SentenceTransformer("all-MiniLM-L6-v2")


@lru_cache()
def load_index():
    index_file = INDEX_PATH / "index.faiss"
    meta_file = INDEX_PATH / "meta.pkl"

    if not index_file.exists() or not meta_file.exists():
        raise FileNotFoundError(
            f"FAISS index not found at {INDEX_PATH}. "
            "Run: python scripts/index_internal_docs.py"
        )

    index = faiss.read_index(str(index_file))
    with open(meta_file, "rb") as f:
        data = pickle.load(f)

    return index, data["chunks"], data["meta"]


def internal_rag_tool(payload: dict) -> dict:
    query = payload.get("query", "")
    top_k = int(payload.get("top_k", 5))

    if not query:
        return {"error": "query is required", "results": []}

    try:
        index, chunks, metadata = load_index()
    except FileNotFoundError as e:
        return {"error": str(e), "results": []}

    q_emb = model.encode([query])
    D, I = index.search(q_emb, top_k)

    results = [
        {
            "text": chunks[idx],
            "source": metadata[idx]["source"],
            "score": float(D[0][rank]),
        }
        for rank, idx in enumerate(I[0])
        if idx < len(chunks)
    ]

    return {"query": query, "results": results}


# Helper functions for agent use
def search_internal_docs(payload: dict) -> dict:
    """Alias for internal_rag_tool for backward compatibility"""
    return internal_rag_tool(payload)


def format_results_as_context(results: list) -> str:
    """Format RAG results as readable context for LLM"""
    if not results:
        return "No relevant internal documents found."
    
    formatted = []
    for i, result in enumerate(results, 1):
        formatted.append(f"[Document {i}] {result['source']}")
        formatted.append(f"Relevance Score: {result['score']:.4f}")
        formatted.append(f"{result['text']}")
        formatted.append("---")
    
    return "\n".join(formatted)
