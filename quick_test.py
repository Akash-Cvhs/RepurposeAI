"""Quick Backend Test - No user input required"""
import requests
import json

BACKEND_URL = "http://localhost:8000"

print("Testing Unified Backend...")
print("="*60)

# Test 1: Health
print("\n1. Health Check...")
try:
    r = requests.get(f"{BACKEND_URL}/health", timeout=5)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"   Tools: {data.get('tools_registered')}")
        print("   ✅ PASSED")
    else:
        print("   ❌ FAILED")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

# Test 2: Tools
print("\n2. List Tools...")
try:
    r = requests.get(f"{BACKEND_URL}/tools", timeout=5)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"   Count: {data.get('count')}")
        print(f"   Tools: {data.get('tools')}")
        print("   ✅ PASSED")
    else:
        print("   ❌ FAILED")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

# Test 3: Simple Analysis
print("\n3. Drug Analysis (aspirin)...")
print("   ⏳ This will take 30-90 seconds...")
try:
    r = requests.post(
        f"{BACKEND_URL}/run",
        json={"query": "Analyze aspirin for pain relief", "molecule": "aspirin"},
        timeout=180
    )
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"   Run ID: {data.get('run_id')}")
        print(f"   Status: {data.get('status')}")
        print(f"   Report Length: {len(data.get('report_text', ''))} chars")
        if data.get('execution_plan'):
            print(f"   Tools Used: {data['execution_plan'].get('tools')}")
        print("   ✅ PASSED")
    else:
        print(f"   ❌ FAILED: {r.text[:200]}")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

print("\n" + "="*60)
print("Testing complete!")
