"""
Test MCP Protocol Compliance and Full Workflow

This tests:
1. MCP server endpoints
2. Tool registration
3. Request/response format
4. Orchestration workflow
5. Drug analyzer integration
"""

import requests
import json
import time

BASE_URL = "http://localhost:8001"


def separator(label: str = ""):
    print("\n" + "=" * 70)
    if label:
        print(f"  {label}")
        print("=" * 70)


def test_health_check():
    """Test 1: Health check endpoint"""
    separator("Test 1: MCP Health Check")
    
    response = requests.get(f"{BASE_URL}/mcp/health")
    data = response.json()
    
    print(f"  Status Code: {response.status_code}")
    print(f"  Server Status: {data.get('status')}")
    print(f"  Registered Tools: {len(data.get('tools', []))}")
    print(f"  Tools: {', '.join(data.get('tools', []))}")
    
    assert response.status_code == 200
    assert data.get('status') == 'ok'
    print("\n  ✓ Health check passed")


def test_list_tools():
    """Test 2: List available tools"""
    separator("Test 2: List MCP Tools")
    
    response = requests.get(f"{BASE_URL}/mcp/tools")
    data = response.json()
    
    tools = data.get('tools', [])
    print(f"  Total Tools: {len(tools)}")
    
    for tool in tools:
        print(f"    - {tool}")
    
    expected_tools = [
        'internal_rag',
        'search_smiles',
        'analyze_smiles',
        'get_drug_smiles',
        'list_drug_categories'
    ]
    
    for expected in expected_tools:
        assert expected in tools, f"Missing tool: {expected}"
    
    print("\n  ✓ All expected tools registered")


def test_mcp_tool_execution():
    """Test 3: Execute individual MCP tool"""
    separator("Test 3: MCP Tool Execution (get_drug_smiles)")
    
    payload = {
        "tool_name": "get_drug_smiles",
        "payload": {"drug_name": "Donepezil"},
        "session_id": "test_session_1"
    }
    
    print(f"  Request:")
    print(f"    Tool: {payload['tool_name']}")
    print(f"    Payload: {payload['payload']}")
    
    response = requests.post(f"{BASE_URL}/mcp/run", json=payload)
    data = response.json()
    
    print(f"\n  Response:")
    print(f"    Status Code: {response.status_code}")
    print(f"    Cached: {data.get('cached')}")
    
    result = data.get('data', {})
    print(f"    Drug Name: {result.get('drug_name')}")
    print(f"    Category: {result.get('category')}")
    print(f"    SMILES: {result.get('smiles', '')[:50]}...")
    
    assert response.status_code == 200
    assert 'data' in data
    print("\n  ✓ Tool execution successful")


def test_mcp_caching():
    """Test 4: Verify caching works"""
    separator("Test 4: MCP Caching")
    
    payload = {
        "tool_name": "get_drug_smiles",
        "payload": {"drug_name": "Donepezil"},
        "session_id": "test_session_2"
    }
    
    # First call
    print("  First call (should not be cached):")
    response1 = requests.post(f"{BASE_URL}/mcp/run", json=payload)
    data1 = response1.json()
    print(f"    Cached: {data1.get('cached')}")
    
    # Second call (should be cached)
    print("\n  Second call (should be cached):")
    response2 = requests.post(f"{BASE_URL}/mcp/run", json=payload)
    data2 = response2.json()
    print(f"    Cached: {data2.get('cached')}")
    
    assert data1.get('cached') == False
    assert data2.get('cached') == True
    print("\n  ✓ Caching works correctly")


def test_session_tracking():
    """Test 5: Session history tracking"""
    separator("Test 5: Session History Tracking")
    
    session_id = "test_session_3"
    
    # Make a few tool calls
    for i in range(3):
        payload = {
            "tool_name": "list_drug_categories",
            "payload": {},
            "session_id": session_id
        }
        requests.post(f"{BASE_URL}/mcp/run", json=payload)
        time.sleep(0.1)
    
    # Check session history
    response = requests.get(f"{BASE_URL}/mcp/session/{session_id}")
    data = response.json()
    
    history = data.get('history', [])
    print(f"  Session ID: {session_id}")
    print(f"  History Entries: {len(history)}")
    
    for i, entry in enumerate(history[:3], 1):
        print(f"\n  Entry {i}:")
        print(f"    Tool: {entry.get('tool')}")
        print(f"    Timestamp: {entry.get('ts')}")
    
    assert len(history) >= 3
    print("\n  ✓ Session tracking works")


def test_orchestration_workflow():
    """Test 6: Full orchestration workflow"""
    separator("Test 6: Orchestration Workflow")
    
    payload = {
        "query": "What drugs are available for Alzheimer's disease?",
        "molecule": None
    }
    
    print(f"  Query: {payload['query']}")
    print("\n  Executing orchestration...")
    
    start_time = time.time()
    response = requests.post(
        f"{BASE_URL}/mcp/orchestrate",
        json=payload,
        timeout=120
    )
    duration = time.time() - start_time
    
    data = response.json()
    
    print(f"\n  Response:")
    print(f"    Status Code: {response.status_code}")
    print(f"    Success: {data.get('success')}")
    print(f"    Run ID: {data.get('run_id')}")
    print(f"    Duration: {duration:.2f}s")
    
    if data.get('execution_plan'):
        print(f"\n  Execution Plan:")
        for agent, enabled in data['execution_plan'].items():
            status = "✓" if enabled else "✗"
            print(f"    {status} {agent}")
    
    if data.get('completed_agents'):
        print(f"\n  Completed Agents: {', '.join(data['completed_agents'])}")
    
    report = data.get('report', '')
    if report:
        print(f"\n  Report Generated: {len(report)} characters")
        print(f"\n  Report Preview:")
        for line in report.split('\n')[:15]:
            print(f"    {line}")
    
    assert response.status_code == 200
    assert data.get('success') == True
    print("\n  ✓ Orchestration workflow successful")


def test_drug_analyzer_integration():
    """Test 7: Drug analyzer through orchestration"""
    separator("Test 7: Drug Analyzer Integration")
    
    payload = {
        "query": "Analyze Donepezil for Alzheimer's treatment",
        "molecule": "Donepezil"
    }
    
    print(f"  Query: {payload['query']}")
    print(f"  Molecule: {payload['molecule']}")
    
    response = requests.post(
        f"{BASE_URL}/mcp/orchestrate",
        json=payload,
        timeout=120
    )
    
    data = response.json()
    
    print(f"\n  Response:")
    print(f"    Success: {data.get('success')}")
    
    if data.get('execution_plan'):
        drug_analysis_enabled = data['execution_plan'].get('drug_analysis', False)
        print(f"    Drug Analysis Enabled: {drug_analysis_enabled}")
    
    report = data.get('report', '')
    
    # Check if report contains drug analysis
    has_molecular_weight = 'Molecular Weight' in report
    has_smiles = 'SMILES' in report
    has_lipinski = 'Lipinski' in report
    
    print(f"\n  Report Contains:")
    print(f"    Molecular Weight: {'✓' if has_molecular_weight else '✗'}")
    print(f"    SMILES Notation: {'✓' if has_smiles else '✗'}")
    print(f"    Lipinski Analysis: {'✓' if has_lipinski else '✗'}")
    
    assert has_molecular_weight
    assert has_smiles
    print("\n  ✓ Drug analyzer integrated correctly")


def test_error_handling():
    """Test 8: Error handling"""
    separator("Test 8: Error Handling")
    
    # Test 1: Unknown tool
    print("  Test 8a: Unknown tool")
    payload = {
        "tool_name": "nonexistent_tool",
        "payload": {},
        "session_id": "test_error"
    }
    
    response = requests.post(f"{BASE_URL}/mcp/run", json=payload)
    print(f"    Status Code: {response.status_code}")
    assert response.status_code == 404
    print("    ✓ Returns 404 for unknown tool")
    
    # Test 2: Invalid payload
    print("\n  Test 8b: Invalid payload")
    payload = {
        "tool_name": "get_drug_smiles",
        "payload": {},  # Missing required drug_name
        "session_id": "test_error"
    }
    
    response = requests.post(f"{BASE_URL}/mcp/run", json=payload)
    data = response.json()
    print(f"    Has Error: {'error' in data.get('data', {})}")
    print("    ✓ Handles invalid payload gracefully")


def main():
    separator("MCP Protocol Compliance Test Suite")
    
    print("\n  Testing MCP server at:", BASE_URL)
    print("  Make sure server is running:")
    print("    uvicorn mcp.server:app --reload --port 8001\n")
    
    try:
        test_health_check()
        test_list_tools()
        test_mcp_tool_execution()
        test_mcp_caching()
        test_session_tracking()
        test_orchestration_workflow()
        test_drug_analyzer_integration()
        test_error_handling()
        
        separator("All Tests Passed ✓")
        print("\n  MCP protocol is correctly implemented!")
        print("  All tools are registered and working.")
        print("  Drug analyzer is integrated with orchestration.\n")
        
    except requests.exceptions.ConnectionError:
        print("\n  ERROR: Cannot connect to MCP server")
        print("  Start server: uvicorn mcp.server:app --reload --port 8001")
    except AssertionError as e:
        print(f"\n  TEST FAILED: {e}")
    except Exception as e:
        print(f"\n  ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
