from typing import Dict, Any
from langchain.schema import BaseMessage
from langchain_openai import ChatOpenAI
from config import DEFAULT_LLM_MODEL

class MasterAgent:
    """Orchestrates the drug repurposing analysis workflow"""
    
    def __init__(self):
        self.llm = ChatOpenAI(model=DEFAULT_LLM_MODEL)
    
    async def plan_analysis(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Create analysis plan based on query and molecule"""
        query = state.get("query", "")
        molecule = state.get("molecule", "")
        
        # Determine which agents to activate
        plan = {
            "clinical_trials": True,
            "patents": True,
            "internal_insights": True,
            "web_intel": bool(query),
            "drug_analysis": bool(molecule or query),
            "report_generation": True
        }
        
        state["analysis_plan"] = plan
        state["status"] = "planned"
        
        return state
    
    async def coordinate_agents(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate execution of specialized agents"""
        plan = state.get("analysis_plan", {})
        
        # Track agent completion
        completed_agents = []
        
        for agent_name, should_run in plan.items():
            if should_run and agent_name != "report_generation":
                completed_agents.append(agent_name)
        
        state["completed_agents"] = completed_agents
        state["status"] = "coordinated"
        
        return state