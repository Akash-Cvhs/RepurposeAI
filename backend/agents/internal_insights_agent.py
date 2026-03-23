from typing import Dict, Any
import json
from langchain_openai import ChatOpenAI
from config import DEFAULT_LLM_MODEL, GUIDELINES_JSON

class InternalInsightsAgent:
    """Analyzes internal guidelines and regulatory insights"""
    
    def __init__(self):
        self.llm = ChatOpenAI(model=DEFAULT_LLM_MODEL)
    
    async def analyze_guidelines(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze regulatory guidelines and internal insights"""
        query = state.get("query", "")
        molecule = state.get("molecule", "")
        
        try:
            with open(GUIDELINES_JSON, 'r') as f:
                guidelines_data = json.load(f)
            
            # Filter relevant guidelines
            relevant_guidelines = self._filter_guidelines(guidelines_data, query, molecule)
            
            # Generate insights
            insights = await self._generate_insights(relevant_guidelines, query, molecule)
            
            state["guidelines_data"] = relevant_guidelines
            state["regulatory_insights"] = insights
            
        except FileNotFoundError:
            state["guidelines_data"] = {}
            state["regulatory_insights"] = "No regulatory guidelines data available"
        
        return state
    
    def _filter_guidelines(self, data: Dict, query: str, molecule: str) -> Dict:
        """Filter guidelines based on relevance"""
        # Simple filtering - can be enhanced with semantic matching
        relevant = {}
        
        for category, guidelines in data.items():
            if isinstance(guidelines, list):
                filtered = [g for g in guidelines if 
                           (molecule and molecule.lower() in str(g).lower()) or
                           (query and query.lower() in str(g).lower())]
                if filtered:
                    relevant[category] = filtered
            elif isinstance(guidelines, dict):
                relevant[category] = guidelines
        
        return relevant
    
    async def _generate_insights(self, guidelines: Dict, query: str, molecule: str) -> str:
        """Generate regulatory and strategic insights"""
        if not guidelines:
            return "No specific regulatory guidelines found for this indication."
        
        prompt = f"""
        Analyze regulatory guidelines and generate strategic insights:
        
        Query: {query}
        Molecule: {molecule}
        
        Available Guidelines: {json.dumps(guidelines, indent=2)}
        
        Provide insights on:
        - Regulatory pathway recommendations
        - Key approval requirements
        - Potential regulatory risks
        - Strategic considerations
        - Timeline estimates
        
        Format as structured analysis with clear recommendations.
        """
        
        response = await self.llm.ainvoke(prompt)
        return response.content