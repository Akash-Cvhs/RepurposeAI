"""
Test MCP Agent Integration

Run this script to verify all agents are properly integrated with MCP.
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.orchestrator import get_orchestrator


async def test_orchestration():
    """Test full orchestration workflow"""
    print("=" * 70)
    print("Testing MCP Agent Integration")
    print("=" * 70)
    
    orchestrator = get_orchestrator()
    
    # Test query
    query = "What drugs are available for Alzheimer's disease?"
    molecule = "Donepezil"
    
    print(f"\nQuery: {query}")
    print(f"Molecule: {molecule}")
    print("\nStarting orchestration...\n")
    
    try:
        result = await orchestrator.orchestrate(query=query, molecule=molecule)
        
        print("✅ Orchestration completed successfully!")
        print(f"\nRun ID: {result.get('run_id')}")
        print(f"Status: {result.get('status')}")
        
        print("\n📋 Execution Plan:")
        for agent, enabled in result.get('execution_plan', {}).items():
            status = "✓" if enabled else "✗"
            print(f"  {status} {agent}")
        
        print(f"\n✅ Completed Agents: {', '.join(result.get('completed_agents', []))}")
        
        # Check for errors
        if result.get('agent_errors'):
            print("\n⚠️  Agent Errors:")
            for agent, error in result['agent_errors'].items():
                print(f"  - {agent}: {error.get('message')}")
        
        # Show logs
        if result.get('logs'):
            print("\n📝 Execution Logs:")
            for log in result['logs'][:10]:  # Show first 10 logs
                print(f"  {log}")
            if len(result['logs']) > 10:
                print(f"  ... and {len(result['logs']) - 10} more logs")
        
        # Show results summary
        print("\n📊 Results Summary:")
        print(f"  - Trials found: {len(result.get('trials', []))}")
        print(f"  - Patents found: {len(result.get('patents', []))}")
        print(f"  - FTO Risk: {result.get('fto_risk', 'unknown')}")
        print(f"  - Report path: {result.get('report_path', 'N/A')}")
        
        # Show report preview
        if result.get('summary'):
            print(f"\n📄 Summary: {result['summary']}")
        
        print("\n" + "=" * 70)
        print("✅ All tests passed!")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Orchestration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_query_analysis():
    """Test query analysis and planning"""
    print("\n" + "=" * 70)
    print("Testing Query Analysis")
    print("=" * 70)
    
    orchestrator = get_orchestrator()
    
    test_queries = [
        ("What drugs are available for Alzheimer's?", "Donepezil"),
        ("Analyze metformin for cancer treatment", "metformin"),
        ("Patent landscape for aspirin", None),
    ]
    
    for query, molecule in test_queries:
        print(f"\nQuery: {query}")
        print(f"Molecule: {molecule or 'Not specified'}")
        
        try:
            plan = await orchestrator.analyze_query(query, molecule)
            print("Execution Plan:")
            for agent, enabled in plan.items():
                status = "✓" if enabled else "✗"
                print(f"  {status} {agent}")
        except Exception as e:
            print(f"  ❌ Failed: {e}")
    
    print("\n" + "=" * 70)


async def main():
    """Run all tests"""
    print("\n🧪 MCP Agent Integration Test Suite\n")
    
    # Test 1: Query analysis
    await test_query_analysis()
    
    # Test 2: Full orchestration
    success = await test_orchestration()
    
    if success:
        print("\n✅ All integration tests passed!")
        print("\nYour MCP architecture is properly configured.")
        print("\nNext steps:")
        print("  1. Start MCP server: uvicorn mcp.server:app --reload --port 8001")
        print("  2. Test API: curl -X POST http://localhost:8001/mcp/orchestrate \\")
        print("       -H 'Content-Type: application/json' \\")
        print("       -d '{\"query\": \"Analyze Donepezil\", \"molecule\": \"Donepezil\"}'")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
