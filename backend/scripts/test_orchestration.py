"""
Test the intelligent MCP orchestration.

Usage:
    cd backend
    # Start server first: uvicorn mcp.server:app --reload --port 8001
    python scripts/test_orchestration.py
"""

import requests
import json

BASE_URL = "http://localhost:8001"


def separator(label: str = ""):
    print("\n" + "=" * 70)
    if label:
        print(f"  {label}")
        print("=" * 70)


def test_query(query: str, molecule: str = None, test_name: str = ""):
    separator(test_name or f"Query: {query[:50]}...")
    
    payload = {"query": query}
    if molecule:
        payload["molecule"] = molecule
    
    print(f"  Query    : {query}")
    print(f"  Molecule : {molecule or 'Not specified'}\n")
    
    try:
        response = requests.post(
            f"{BASE_URL}/mcp/orchestrate",
            json=payload,
            timeout=120
        )
        
        if response.status_code != 200:
            print(f"  ERROR: HTTP {response.status_code}")
            print(f"  {response.text}")
            return
        
        result = response.json()
        
        if not result.get("success"):
            print(f"  ERROR: {result.get('error')}")
            return
        
        print(f"  Run ID   : {result.get('run_id')}")
        print(f"  Status   : {result.get('status')}")
        print(f"\n  Execution Plan:")
        plan = result.get("execution_plan", {})
        for agent, enabled in plan.items():
            status = "✓" if enabled else "✗"
            print(f"    {status} {agent}")
        
        print(f"\n  Completed Agents: {', '.join(result.get('completed_agents', []))}")
        
        report = result.get("report", "")
        if report:
            lines = report.split("\n")
            print(f"\n  Report Preview (first 10 lines):")
            for line in lines[:10]:
                print(f"    {line}")
            print(f"    ... ({len(lines)} total lines)")
        
    except requests.exceptions.ConnectionError:
        print(f"  ERROR: Cannot connect to {BASE_URL}")
        print("  Start server: uvicorn mcp.server:app --reload --port 8001")
    except Exception as e:
        print(f"  ERROR: {e}")


if __name__ == "__main__":
    separator("MCP Orchestration Tests")
    
    # Test 1: Drug-specific query
    test_query(
        query="What are the repurposing opportunities for metformin in cancer treatment?",
        molecule="metformin",
        test_name="Test 1: Drug Repurposing Query"
    )
    
    # Test 2: Patent-focused query
    test_query(
        query="What is the patent landscape for aspirin in Alzheimer's disease?",
        molecule="aspirin",
        test_name="Test 2: Patent Landscape Query"
    )
    
    # Test 3: Clinical evidence query
    test_query(
        query="What clinical trial evidence exists for statins in neuroprotection?",
        test_name="Test 3: Clinical Evidence Query"
    )
    
    # Test 4: Market intelligence query
    test_query(
        query="What is the competitive landscape for COVID-19 therapeutics?",
        test_name="Test 4: Market Intelligence Query"
    )
    
    # Test 5: Internal data query
    test_query(
        query="What do our internal clinical experiments show about adverse events?",
        test_name="Test 5: Internal Data Query"
    )
    
    separator("All Tests Complete")
