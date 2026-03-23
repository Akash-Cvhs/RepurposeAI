"""
Test Unified Backend - Single Server Testing

Tests the unified backend API (port 8000 only)
"""

import requests
import json
import time

# Configuration
BACKEND_URL = "http://localhost:8000"

def test_health():
    """Test backend health"""
    print("\n" + "="*60)
    print("TEST 1: Backend Health Check")
    print("="*60)
    
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_tools():
    """Test tools listing"""
    print("\n" + "="*60)
    print("TEST 2: List Available Tools")
    print("="*60)
    
    try:
        response = requests.get(f"{BACKEND_URL}/tools", timeout=5)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Tools Count: {result.get('count')}")
            print(f"Tools: {json.dumps(result.get('tools'), indent=2)}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_simple_analysis():
    """Test simple drug analysis"""
    print("\n" + "="*60)
    print("TEST 3: Simple Drug Analysis")
    print("="*60)
    
    payload = {
        "query": "Analyze aspirin for cardiovascular disease",
        "molecule": "aspirin"
    }
    
    print(f"Request: {json.dumps(payload, indent=2)}")
    print("\n⏳ Sending request... (this may take 30-90 seconds)")
    print("   The LLM is analyzing the query and planning tool execution...")
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BACKEND_URL}/run",
            json=payload,
            timeout=180
        )
        elapsed = time.time() - start_time
        
        print(f"\n⏱️  Time taken: {elapsed:.2f} seconds")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Run ID: {result.get('run_id')}")
            print(f"Status: {result.get('status')}")
            print(f"Report Path: {result.get('report_path')}")
            
            if result.get('execution_plan'):
                plan = result['execution_plan']
                print(f"\nExecution Plan:")
                print(f"  Tools Used: {plan.get('tools')}")
                if plan.get('reasoning'):
                    reasoning = plan['reasoning'][:200]
                    print(f"  Reasoning: {reasoning}...")
            
            if result.get('tool_results'):
                print(f"\nTool Results:")
                for tool_name, tool_result in result['tool_results'].items():
                    if tool_result.get('error'):
                        print(f"  ❌ {tool_name}: {tool_result['error']}")
                    else:
                        print(f"  ✅ {tool_name}: Success")
            
            if result.get('report_text'):
                report_preview = result['report_text'][:500]
                print(f"\nReport Preview (first 500 chars):")
                print("-" * 60)
                print(report_preview)
                print("-" * 60)
                print(f"Full report length: {len(result['report_text'])} characters")
            else:
                print("\n⚠️  No report_text in response!")
            
            return True
        else:
            print(f"❌ Error Response:")
            print(response.text)
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out after 180 seconds")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_archives():
    """Test archives listing"""
    print("\n" + "="*60)
    print("TEST 4: List Archives")
    print("="*60)
    
    try:
        response = requests.get(f"{BACKEND_URL}/archives", timeout=5)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            archives = response.json()
            print(f"Archives Count: {len(archives)}")
            
            if archives:
                print("\nRecent Archives:")
                for archive in archives[-5:]:  # Show last 5
                    print(f"  - {archive.get('filename')} ({archive.get('size')} bytes)")
            else:
                print("No archives found yet")
            
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("🧪 UNIFIED BACKEND TESTING SUITE")
    print("="*60)
    print("\nThis will test the unified backend API (port 8000)")
    print("\nMake sure the backend is running:")
    print("  Option 1: Double-click start_backend.bat")
    print("  Option 2: cd backend && python app.py")
    print("="*60)
    
    input("\nPress Enter to start testing...")
    
    results = []
    
    # Test 1: Health
    results.append(("Health Check", test_health()))
    
    # Test 2: Tools
    results.append(("List Tools", test_tools()))
    
    # Test 3: Analysis
    results.append(("Drug Analysis", test_simple_analysis()))
    
    # Test 4: Archives
    results.append(("List Archives", test_archives()))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:20s} {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Backend is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
    
    print("="*60)

if __name__ == "__main__":
    main()
