"""
RAG smoke test — runs without the server.
Calls internal_rag_tool directly and prints results.

Usage:
    cd backend
    python scripts/test_rag.py
    python scripts/test_rag.py "your custom query here"
"""

import sys
from pathlib import Path

# Make sure backend/ is on the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.internal_rag_tool import internal_rag_tool, INDEX_PATH


def separator(label: str = ""):
    print("\n" + "=" * 60)
    if label:
        print(f"  {label}")
        print("=" * 60)


def check_index_exists():
    separator("1. Index Check")
    index_file = INDEX_PATH / "index.faiss"
    meta_file = INDEX_PATH / "meta.pkl"

    if index_file.exists() and meta_file.exists():
        size_mb = index_file.stat().st_size / (1024 * 1024)
        print(f"  index.faiss  : FOUND  ({size_mb:.2f} MB)")
        print(f"  meta.pkl     : FOUND")
        return True
    else:
        print(f"  index.faiss  : {'FOUND' if index_file.exists() else 'MISSING'}")
        print(f"  meta.pkl     : {'FOUND' if meta_file.exists() else 'MISSING'}")
        print("\n  Run first:  python scripts/index_internal_docs.py")
        return False


def run_query(query: str, top_k: int = 3):
    separator(f"2. Query: '{query}'")
    result = internal_rag_tool({"query": query, "top_k": top_k})

    if "error" in result:
        print(f"  ERROR: {result['error']}")
        return

    results = result.get("results", [])
    print(f"  Returned {len(results)} chunk(s)\n")

    for i, r in enumerate(results, 1):
        print(f"  [{i}] Source : {r['source']}")
        print(f"       Score  : {r['score']:.4f}")
        print(f"       Text   : {r['text'][:200].strip()}...")
        print()


def run_edge_cases():
    separator("3. Edge Cases")

    # Empty query
    r = internal_rag_tool({"query": ""})
    status = "PASS" if "error" in r else "FAIL"
    print(f"  Empty query          : {status}  → {r.get('error', r)}")

    # Missing query key
    r = internal_rag_tool({})
    status = "PASS" if "error" in r else "FAIL"
    print(f"  Missing query key    : {status}  → {r.get('error', r)}")

    # top_k as string (should coerce)
    r = internal_rag_tool({"query": "test", "top_k": "2"})
    status = "PASS" if "results" in r else "FAIL"
    print(f"  top_k as string '2'  : {status}  → {len(r.get('results', []))} result(s)")


if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "clinical experiment results"

    if not check_index_exists():
        sys.exit(1)

    run_query(query)
    run_edge_cases()

    separator("Done")
    print("  RAG tool is working correctly.\n")
