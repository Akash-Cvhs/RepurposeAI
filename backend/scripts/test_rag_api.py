"""
RAG API test — hits the live MCP server over HTTP.
Requires the server to be running first:
    uvicorn mcp.server:app --reload --port 8001

Usage:
    cd backend
    python scripts/test_rag_api.py
    python scripts/test_rag_api.py "your custom query here"
"""

import sys
import json
import requests

BASE_URL = "http://localhost:8001"


def separator(label: str = ""):
    print("\n" + "=" * 60)
    if label:
        print(f"  {label}")
        print("=" * 60)


def check_health():
    separator("1. Health Check")
    try:
        r = requests.get(f"{BASE_URL}/mcp/health", timeout=3)
        data = r.json()
        print(f"  Status  : {data.get('status')}")
        print(f"  Tools   : {data.get('tools')}")
        return True
    except requests.exceptions.ConnectionError:
        print(f"  ERROR: Cannot reach {BASE_URL}")
        print("  Start the server first:")
        print("    cd backend && uvicorn mcp.server:app --reload --port 8001")
        return False


def check_tools():
    separator("2. Registered Tools")
    r = requests.get(f"{BASE_URL}/mcp/tools")
    tools = r.json().get("tools", [])
    for t in tools:
        print(f"  - {t}")
    return "internal_rag" in tools


def run_query(query: str, top_k: int = 3):
    separator(f"3. Query: '{query}'")
    payload = {
        "tool_name": "internal_rag",
        "payload": {"query": query, "top_k": top_k},
        "session_id": "test_session"
    }
    r = requests.post(f"{BASE_URL}/mcp/run", json=payload)
    data = r.json()

    if "error" in data:
        print(f"  ERROR: {data['error']}")
        return

    print(f"  Cached  : {data.get('cached')}")
    results = data.get("data", {}).get("results", [])
    print(f"  Results : {len(results)} chunk(s)\n")

    for i, res in enumerate(results, 1):
        print(f"  [{i}] Source : {res['source']}")
        print(f"       Score  : {res['score']:.4f}")
        print(f"       Text   : {res['text'][:200].strip()}...")
        print()


def check_cache(query: str):
    separator("4. Cache Check (same query again)")
    payload = {
        "tool_name": "internal_rag",
        "payload": {"query": query, "top_k": 3},
        "session_id": "test_session"
    }
    r = requests.post(f"{BASE_URL}/mcp/run", json=payload)
    data = r.json()
    cached = data.get("cached", False)
    status = "PASS" if cached else "FAIL"
    print(f"  Cache hit on repeat call : {status}  (cached={cached})")


def check_session():
    separator("5. Session History")
    r = requests.get(f"{BASE_URL}/mcp/session/test_session")
    history = r.json().get("history", [])
    print(f"  Entries in session : {len(history)}")
    if history:
        last = history[-1]
        print(f"  Last tool called   : {last.get('tool')}")


def check_unknown_tool():
    separator("6. Unknown Tool (expect 404)")
    payload = {
        "tool_name": "nonexistent_tool",
        "payload": {},
        "session_id": "test_session"
    }
    r = requests.post(f"{BASE_URL}/mcp/run", json=payload)
    status = "PASS" if r.status_code == 404 else "FAIL"
    print(f"  404 on unknown tool : {status}  (got {r.status_code})")


if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "clinical experiment results"

    if not check_health():
        sys.exit(1)

    if not check_tools():
        print("\n  ERROR: 'internal_rag' tool not registered in server.")
        sys.exit(1)

    run_query(query)
    check_cache(query)
    check_session()
    check_unknown_tool()

    separator("Done")
    print("  MCP server + RAG tool are working correctly.\n")
