#!/usr/bin/env python3
"""
Rapid MCP Testing Script

Quick tests for all 6 MCP tools without starting server.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

# Import tools directly
from tools.clinical_trials_tool import search_clinical_trials
from tools.patent_tool import search_patents
from tools.internal_rag_tool import internal_rag_tool
from tools.web_intel_tool import gather_web_intelligence
from tools.drug_analyzer_tool import analyze_drug
from tools.report_generator_tool import generate_report


def print_result(test_name, result):
    """Print test result"""
    print(f"\n{'='*70}")
    print(f"TEST: {test_name}")
    print(f"{'='*70}")
    
    if isinstance(result, dict):
        if "error" in result:
            print(f"❌ ERROR: {result['error']}")
        else:
            # Print key fields
            for key, value in result.items():
                if key in ["trials", "patents", "results", "intelligence", "tool_results"]:
                    if isinstance(value, list):
                        print(f"✓ {key}: {len(value)} items")
                    else:
                        print(f"✓ {key}: {len(str(value))} chars")
                elif key == "report":
                    print(f"✓ {key}: {len(value)} chars")
                    print(f"  Preview: {value[:200]}...")
                else:
                    print(f"✓ {key}: {value}")
    else:
        print(result)


async def test_clinical_trials():
    """Test 1: Clinical Trials Search"""
    result = search_clinical_trials({
        "molecule": "metformin",
        "indication": "diabetes"
    })
    print_result("Clinical Trials Search", result)
    return result


async def test_patents():
    """Test 2: Patent Search"""
    result = search_patents({
        "molecule": "aspirin"
    })
    print_result("Patent Search", result)
    return result


async def test_internal_rag():
    """Test 3: Internal RAG"""
    result = internal_rag_tool({
        "query": "clinical trial results",
        "top_k": 3
    })
    print_result("Internal RAG", result)
    return result


async def test_web_intelligence():
    """Test 4: Web Intelligence"""
    result = await gather_web_intelligence({
        "query": "Alzheimer's drug market",
        "molecule": "Donepezil",
        "focus": "market"
    })
    print_result("Web Intelligence", result)
    return result


async def test_drug_analyzer_search():
    """Test 5a: Drug Analyzer - Search"""
    result = await analyze_drug({
        "action": "search",
        "query": "Alzheimer"
    })
    print_result("Drug Analyzer - Search", result)
    return result


async def test_drug_analyzer_full():
    """Test 5b: Drug Analyzer - Full Analysis"""
    result = await analyze_drug({
        "action": "full_analysis",
        "drug_name": "Donepezil",
        "disease": "Alzheimer's"
    })
    print_result("Drug Analyzer - Full Analysis", result)
    return result


async def test_report_generation():
    """Test 6: Report Generation"""
    # Mock tool results
    mock_results = {
        "search_clinical_trials": {
            "data": {
                "trials": [{"nct_id": "NCT123", "title": "Test Trial"}],
                "count": 1,
                "source": "mock"
            }
        },
        "search_patents": {
            "data": {
                "patents": [{"patent_id": "US123", "title": "Test Patent"}],
                "count": 1,
                "fto_risk": "low"
            }
        },
        "analyze_drug": {
            "data": {
                "drug_name": "Donepezil",
                "molecular_weight": 379.49,
                "passes_lipinski": True,
                "analysis_complete": True
            }
        }
    }
    
    result = await generate_report({
        "query": "Analyze Donepezil for Alzheimer's",
        "molecule": "Donepezil",
        "indication": "Alzheimer's",
        "tool_results": mock_results
    })
    print_result("Report Generation", result)
    return result


async def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("MCP RAPID TESTING - 6 Tools")
    print("="*70)
    
    tests = [
        ("Clinical Trials", test_clinical_trials),
        ("Patents", test_patents),
        ("Internal RAG", test_internal_rag),
        ("Web Intelligence", test_web_intelligence),
        ("Drug Analyzer - Search", test_drug_analyzer_search),
        ("Drug Analyzer - Full", test_drug_analyzer_full),
        ("Report Generation", test_report_generation),
    ]
    
    results = {}
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            result = await test_func()
            if isinstance(result, dict) and "error" not in result:
                passed += 1
                results[name] = "✅ PASS"
            else:
                failed += 1
                results[name] = "❌ FAIL"
        except Exception as e:
            failed += 1
            results[name] = f"❌ ERROR: {e}"
            print(f"\n❌ Exception in {name}: {e}")
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    for name, status in results.items():
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed + failed} | Passed: {passed} | Failed: {failed}")
    
    if failed == 0:
        print("\n✅ ALL TESTS PASSED!")
    else:
        print(f"\n⚠️  {failed} test(s) failed")
    
    print("\n" + "="*70)
    print("6 MCP Tools Registered:")
    print("  1. search_clinical_trials")
    print("  2. search_patents")
    print("  3. internal_rag")
    print("  4. gather_web_intelligence")
    print("  5. analyze_drug")
    print("  6. generate_report")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(main())
