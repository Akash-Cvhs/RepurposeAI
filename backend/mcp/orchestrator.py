"""
Intelligent MCP Orchestrator

Routes user queries to the appropriate agents dynamically using LLM-based planning.
"""

import asyncio
from typing import Dict, Any, List
from datetime import datetime
from utils.llm_utils import get_llm

# Import node-based agent functions
from agents.clinical_trials_agent import clinical_trials_agent_node
from agents.patent_agent import patent_agent_node
from agents.internal_insights_agent import InternalInsightsAgent
from agents.web_intel_agent import WebIntelAgent
from agents.drug_analyzer_agent import DrugAnalyzerAgent
from agents.report_generator_agent import report_generator_agent_node
from agents.master_agent import master_agent_node


class MCPOrchestrator:
    """
    Intelligent orchestrator that:
    1. Analyzes user query
    2. Decides which agents to invoke
    3. Executes agents in parallel
    4. Generates final PDF report
    """

    def __init__(self):
        self.llm = get_llm()
        
        # Initialize class-based agents (those that still use classes)
        self.internal_insights_agent = InternalInsightsAgent()
        self.web_intel_agent = WebIntelAgent()
        self.drug_analyzer_agent = DrugAnalyzerAgent()

    async def analyze_query(self, query: str, molecule: str = None) -> Dict[str, bool]:
        """
        Use LLM to decide which agents should be invoked based on the query.
        """
        prompt = f"""
You are an intelligent agent orchestrator for a drug repurposing analysis system.

User Query: "{query}"
Molecule: {molecule or "Not specified"}

Available agents:
- clinical_trials: Searches clinical trial databases for efficacy/safety data
- patents: Analyzes patent landscape and freedom-to-operate risks
- internal_insights: Searches internal clinical experiment reports (PDFs) and regulatory guidelines
- web_intel: Gathers market intelligence and competitive landscape
- drug_analysis: Analyzes drug properties, mechanisms, pharmacokinetics, interactions

Based on the query, decide which agents are NECESSARY to answer it well.

Rules:
- If query mentions a specific drug/molecule → include drug_analysis
- If query asks about clinical evidence/trials → include clinical_trials
- If query asks about IP/patents/FTO → include patents
- If query asks about regulations/guidelines/internal data → include internal_insights
- If query asks about market/competition/commercial → include web_intel
- Always include report agent (it summarizes everything)

Respond ONLY with a JSON object like:
{{
  "clinical_trials": true,
  "patents": false,
  "internal_insights": true,
  "web_intel": false,
  "drug_analysis": true,
  "report": true
}}
"""

        response = await self.llm.ainvoke(prompt)
        content = response.content.strip()

        # Parse JSON from LLM response
        import json
        try:
            # Extract JSON if wrapped in markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            plan = json.loads(content)
            
            # Ensure report is always included
            plan["report"] = True
            
            return plan
        except json.JSONDecodeError:
            # Fallback: run all agents if parsing fails
            return {
                "clinical_trials": True,
                "patents": True,
                "internal_insights": True,
                "web_intel": True,
                "drug_analysis": bool(molecule),
                "report": True,
            }

    async def execute_agents(
        self, 
        plan: Dict[str, bool], 
        query: str, 
        molecule: str = None
    ) -> Dict[str, Any]:
        """
        Execute selected agents in parallel and collect results.
        Supports both node-based and class-based agents.
        """
        run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize state with master agent
        state = {
            "query": query,
            "molecule": molecule,
            "run_id": run_id,
            "status": "executing",
            "execution_plan": plan,
            "logs": [],
            "agent_errors": {},
        }
        
        # Run master agent first to parse query and set up state
        state = master_agent_node(state)

        # Execute agents based on plan
        tasks = []
        agent_names = []

        for agent_name, should_run in plan.items():
            if should_run and agent_name != "report":
                
                if agent_name == "clinical_trials":
                    # Node-based agent - run synchronously in thread
                    tasks.append(asyncio.to_thread(clinical_trials_agent_node, state.copy()))
                    agent_names.append(agent_name)
                    
                elif agent_name == "patents":
                    # Node-based agent - run synchronously in thread
                    tasks.append(asyncio.to_thread(patent_agent_node, state.copy()))
                    agent_names.append(agent_name)
                    
                elif agent_name == "internal_insights":
                    # Class-based agent - async method
                    tasks.append(self.internal_insights_agent.analyze_guidelines(state.copy()))
                    agent_names.append(agent_name)
                    
                elif agent_name == "web_intel":
                    # Class-based agent - async method
                    tasks.append(self.web_intel_agent.gather_intelligence(state.copy()))
                    agent_names.append(agent_name)
                    
                elif agent_name == "drug_analysis":
                    # Class-based agent - async method
                    tasks.append(self.drug_analyzer_agent.analyze_drug(state.copy()))
                    agent_names.append(agent_name)

        # Wait for all agents to complete
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Merge results into state
            for agent_name, result in zip(agent_names, results):
                if isinstance(result, Exception):
                    state[f"{agent_name}_error"] = str(result)
                    state["logs"].append(f"[orchestrator] {agent_name} failed: {result}")
                elif isinstance(result, dict):
                    # Merge agent results into main state
                    state.update(result)
                    state["logs"].append(f"[orchestrator] {agent_name} completed")

        state["completed_agents"] = agent_names
        state["status"] = "agents_completed"

        # Generate final report
        if plan.get("report", True):
            state = report_generator_agent_node(state)
            state["logs"].append("[orchestrator] report generated")

        return state

    async def orchestrate(
        self, 
        query: str, 
        molecule: str = None
    ) -> Dict[str, Any]:
        """
        Main orchestration flow:
        1. Analyze query to create execution plan
        2. Execute selected agents in parallel
        3. Generate final report
        """
        # Step 1: Intelligent planning
        plan = await self.analyze_query(query, molecule)

        # Step 2: Execute agents
        result = await self.execute_agents(plan, query, molecule)

        return result


# Singleton instance
_orchestrator = None

def get_orchestrator() -> MCPOrchestrator:
    """Get or create the orchestrator singleton"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = MCPOrchestrator()
    return _orchestrator
