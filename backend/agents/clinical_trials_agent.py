from typing import Dict, Any
import pandas as pd
from utils.llm_utils import get_llm
from config import TRIALS_CSV

class ClinicalTrialsAgent:
    """Analyzes clinical trials data for drug repurposing opportunities"""
    
    def __init__(self):
        self.llm = get_llm()
    
    async def analyze_trials(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Search and analyze relevant clinical trials"""
        query = state.get("query", "")
        molecule = state.get("molecule", "")
        
        # Load mock trials data
        try:
            trials_df = pd.read_csv(TRIALS_CSV)
            
            # Filter relevant trials
            relevant_trials = self._filter_trials(trials_df, query, molecule)
            
            # Analyze findings
            analysis = await self._analyze_findings(relevant_trials, query, molecule)
            
            state["clinical_trials_data"] = relevant_trials.to_dict('records')
            state["clinical_trials_analysis"] = analysis
            
        except FileNotFoundError:
            state["clinical_trials_data"] = []
            state["clinical_trials_analysis"] = "No clinical trials data available"
        
        return state
    
    def _filter_trials(self, df: pd.DataFrame, query: str, molecule: str) -> pd.DataFrame:
        """Filter trials based on query and molecule"""
        if df.empty:
            return df
            
        # Simple filtering logic - can be enhanced with semantic search
        mask = pd.Series([True] * len(df))
        
        if molecule:
            mask &= df['intervention'].str.contains(molecule, case=False, na=False)
        
        if query:
            mask &= (df['condition'].str.contains(query, case=False, na=False) |
                    df['title'].str.contains(query, case=False, na=False))
        
        return df[mask].head(10)  # Limit results
    
    async def _analyze_findings(self, trials_df: pd.DataFrame, query: str, molecule: str) -> str:
        """Generate analysis of clinical trials findings"""
        if trials_df.empty:
            return "No relevant clinical trials found."
        
        prompt = f"""
        Analyze the following clinical trials data for drug repurposing opportunities:
        
        Query: {query}
        Molecule: {molecule}
        
        Trials found: {len(trials_df)}
        
        Key findings to highlight:
        - Efficacy signals
        - Safety profile
        - Patient populations
        - Repurposing potential
        
        Provide a concise analysis in 2-3 paragraphs.
        """
        
        response = await self.llm.ainvoke(prompt)
        return response.content