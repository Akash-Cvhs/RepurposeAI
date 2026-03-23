"""
Intelligent MCP Orchestrator

Uses LLM to decide which MCP tools to call and in what order.
Follows true MCP protocol - tools are invoked via MCP server, not directly.
"""

import asyncio
from typing import Dict, Any, List
from datetime import datetime
from utils.llm_utils import get_llm
import json


class IntelligentOrchestrator:
    """
    Orchestrator that:
    1. Analyzes user query with LLM
    2. Decides which MCP tools to invoke
    3. Determines tool invocation order and dependencies
    4. Executes tools via MCP protocol
    5. Synthesizes results into final report
    """

    def __init__(self, mcp_server):
        self.llm = get_llm()
        self.mcp = mcp_server
        
    async def analyze_query_and_plan(self, query: str, molecule: str = None) -> Dict[str, Any]:
        """
        Use LLM to analyze query and create execution plan
        
        Returns:
            {
                "molecule": str,
                "indication": str,
                "tools": [
                    {
                        "name": "search_clinical_trials",
                        "params": {"molecule": "...", "indication": "..."},
                        "depends_on": []  # List of tool names this depends on
                    },
                    ...
                ],
                "reasoning": str
            }
        """
        prompt = f"""
You are an intelligent orchestrator for a drug repurposing analysis system.

User Query: "{query}"
Molecule (if specified): {molecule or "Not specified"}

Available MCP Tools:
1. search_clinical_trials - Search clinical trial databases
   Params: molecule (required), indication (optional)
   
2. search_patents - Search patent databases and analyze FTO risk
   Params: molecule (required), indication (optional)
   
3. internal_rag - Search internal clinical experiment reports
   Params: query (required), top_k (optional)
   
4. gather_web_intelligence - Gather market and competitive intelligence
   Params: query, molecule, indication, focus (market/competitive/regulatory/all)
   
5. analyze_drug - Comprehensive drug analysis (search, SMILES, properties, images)
   Actions:
   - "search": Search drugs by name/category
     Params: query (required), exact_match (optional)
   - "get_smiles": Get SMILES notation for drug
     Params: drug_name (required)
   - "analyze": Analyze molecular properties
     Params: smiles OR drug_name (required), include_admet, generate_image
   - "list_categories": List all drug categories
     Params: none
   - "full_analysis": Complete drug profile
     Params: drug_name (required), disease (optional)

Your task:
1. Extract molecule name and indication from query
2. Decide which tools are needed to answer the query
3. Determine the order of tool execution (some tools may depend on others)
4. Specify parameters for each tool

Respond ONLY with a JSON object:
{{
  "molecule": "extracted molecule name or null",
  "indication": "extracted indication or null",
  "tools": [
    {{
      "name": "tool_name",
      "params": {{"param1": "value1"}},
      "depends_on": ["other_tool_name"],
      "reasoning": "why this tool is needed"
    }}
  ],
  "reasoning": "overall strategy explanation"
}}

Rules:
- If molecule is mentioned → include search_clinical_trials, search_patents
- If asking about molecular properties → include get_drug_smiles, analyze_smiles
- If asking about market/competition → include gather_web_intelligence
- If asking about internal data/guidelines → include internal_rag
- Tools that need SMILES should depend on get_drug_smiles
- Order tools logically (e.g., get_drug_smiles before analyze_smiles)
"""

        response = await self.llm.ainvoke(prompt)
        content = response.content.strip()

        try:
            # Extract JSON from response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            plan = json.loads(content)
            return plan
            
        except json.JSONDecodeError as e:
            # Fallback plan
            return {
                "molecule": molecule,
                "indication": None,
                "tools": [
                    {
                        "name": "search_clinical_trials",
                        "params": {"molecule": molecule or "unknown"},
                        "depends_on": [],
                        "reasoning": "Fallback: search clinical trials"
                    }
                ],
                "reasoning": f"Failed to parse LLM response: {e}. Using fallback plan."
            }

    async def execute_tool(
        self, 
        tool_name: str, 
        params: Dict[str, Any],
        session_id: str
    ) -> Dict[str, Any]:
        """
        Execute a single MCP tool via the MCP server
        """
        from mcp.server import MCPRequest
        
        request = MCPRequest(
            tool_name=tool_name,
            payload=params,
            session_id=session_id
        )
        
        result = await self.mcp.handle(request)
        return result

    async def execute_plan(
        self,
        plan: Dict[str, Any],
        session_id: str
    ) -> Dict[str, Any]:
        """
        Execute the tool invocation plan
        
        Handles dependencies: tools that depend on others wait for their results
        """
        tools = plan.get("tools", [])
        results = {}
        executed = set()
        
        # Keep executing until all tools are done
        while len(executed) < len(tools):
            # Find tools that can be executed now (dependencies met)
            ready_tools = []
            for tool in tools:
                tool_name = tool["name"]
                if tool_name in executed:
                    continue
                    
                depends_on = tool.get("depends_on", [])
                if all(dep in executed for dep in depends_on):
                    ready_tools.append(tool)
            
            if not ready_tools:
                # No tools ready - circular dependency or error
                break
            
            # Execute ready tools in parallel
            tasks = []
            tool_names = []
            
            for tool in ready_tools:
                tool_name = tool["name"]
                params = tool["params"]
                
                # Inject results from dependencies if needed
                for dep in tool.get("depends_on", []):
                    if dep in results:
                        dep_result = results[dep].get("data", {})
                        # Auto-inject common fields
                        if "smiles" in dep_result and "smiles" not in params:
                            params["smiles"] = dep_result["smiles"]
                
                tasks.append(self.execute_tool(tool_name, params, session_id))
                tool_names.append(tool_name)
            
            # Wait for all ready tools to complete
            task_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Store results
            for tool_name, result in zip(tool_names, task_results):
                if isinstance(result, Exception):
                    results[tool_name] = {
                        "error": str(result),
                        "data": {}
                    }
                else:
                    results[tool_name] = result
                executed.add(tool_name)
        
        return results

    async def synthesize_report(
        self,
        query: str,
        plan: Dict[str, Any],
        results: Dict[str, Any]
    ) -> str:
        """
        Use LLM to synthesize tool results into final report
        """
        # Prepare results summary for LLM
        results_summary = []
        for tool_name, result in results.items():
            if result.get("error"):
                results_summary.append(f"- {tool_name}: ERROR - {result['error']}")
            else:
                data = result.get("data", {})
                if tool_name == "search_clinical_trials":
                    count = data.get("count", 0)
                    results_summary.append(f"- {tool_name}: Found {count} clinical trials")
                elif tool_name == "search_patents":
                    count = data.get("count", 0)
                    fto_risk = data.get("fto_risk", "unknown")
                    results_summary.append(f"- {tool_name}: Found {count} patents, FTO risk: {fto_risk}")
                elif tool_name == "internal_rag":
                    count = len(data.get("results", []))
                    results_summary.append(f"- {tool_name}: Found {count} relevant documents")
                elif tool_name == "gather_web_intelligence":
                    confidence = data.get("confidence", 0)
                    results_summary.append(f"- {tool_name}: Generated intelligence (confidence: {confidence:.2f})")
                elif tool_name == "analyze_smiles":
                    mw = data.get("molecular_weight", "N/A")
                    lipinski = data.get("passes_lipinski", False)
                    results_summary.append(f"- {tool_name}: MW={mw}, Lipinski={lipinski}")
                else:
                    results_summary.append(f"- {tool_name}: Completed")
        
        prompt = f"""
Generate a comprehensive drug repurposing analysis report.

Original Query: {query}
Molecule: {plan.get('molecule', 'Unknown')}
Indication: {plan.get('indication', 'Unknown')}

Tools Executed:
{chr(10).join(results_summary)}

Full Results:
{json.dumps(results, indent=2, default=str)}

Generate a structured report with:
1. Executive Summary
2. Clinical Evidence (from clinical trials)
3. Patent Landscape & FTO Risk
4. Molecular Analysis (if available)
5. Market Intelligence (if available)
6. Internal Insights (if available)
7. Recommendations
8. Risk Factors

Format as markdown. Be specific and cite data from the results.
"""

        response = await self.llm.ainvoke(prompt)
        return response.content

    async def orchestrate(
        self,
        query: str,
        molecule: str = None
    ) -> Dict[str, Any]:
        """
        Main orchestration flow following MCP protocol
        
        1. Analyze query and create plan
        2. Execute tools via MCP
        3. Synthesize results
        4. Return comprehensive response
        """
        run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        session_id = f"session_{run_id}"
        
        # Step 1: Plan
        plan = await self.analyze_query_and_plan(query, molecule)
        
        # Step 2: Execute
        results = await self.execute_plan(plan, session_id)
        
        # Step 3: Synthesize
        report = await self.synthesize_report(query, plan, results)
        
        # Step 4: Return
        return {
            "success": True,
            "run_id": run_id,
            "query": query,
            "molecule": plan.get("molecule"),
            "indication": plan.get("indication"),
            "execution_plan": {
                "tools": [t["name"] for t in plan.get("tools", [])],
                "reasoning": plan.get("reasoning")
            },
            "tool_results": results,
            "report": report,
            "status": "completed"
        }


# Singleton instance
_orchestrator = None

def get_intelligent_orchestrator(mcp_server):
    """Get or create the intelligent orchestrator singleton"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = IntelligentOrchestrator(mcp_server)
    return _orchestrator
