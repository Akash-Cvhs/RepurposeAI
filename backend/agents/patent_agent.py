from typing import Dict, Any
import pandas as pd
from utils.llm_utils import get_llm
from config import PATENTS_CSV

class PatentAgent:
    """Analyzes patent landscape for freedom-to-operate assessment"""
    
    def __init__(self):
        self.llm = get_llm()
    
    async def analyze_patents(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze patent landscape and FTO risks"""
        query = state.get("query", "")
        molecule = state.get("molecule", "")
        
        try:
            patents_df = pd.read_csv(PATENTS_CSV)
            
            # Filter relevant patents
            relevant_patents = self._filter_patents(patents_df, query, molecule)
            
            # Analyze FTO risks
            fto_analysis = await self._analyze_fto_risks(relevant_patents, query, molecule)
            
            state["patents_data"] = relevant_patents.to_dict('records')
            state["patent_analysis"] = fto_analysis
            
        except FileNotFoundError:
            state["patents_data"] = []
            state["patent_analysis"] = "No patent data available"
        
        return state
    
    def _filter_patents(self, df: pd.DataFrame, query: str, molecule: str) -> pd.DataFrame:
        """Filter patents based on query and molecule"""
        if df.empty:
            return df
            
        mask = pd.Series([True] * len(df))
        
        if molecule:
            mask &= (df['title'].str.contains(molecule, case=False, na=False) |
                    df['abstract'].str.contains(molecule, case=False, na=False))
        
        if query:
            mask &= (df['title'].str.contains(query, case=False, na=False) |
                    df['abstract'].str.contains(query, case=False, na=False))
        
        return df[mask].head(15)  # Limit results
    
    async def _analyze_fto_risks(self, patents_df: pd.DataFrame, query: str, molecule: str) -> str:
        """Analyze freedom-to-operate risks"""
        if patents_df.empty:
            return "No relevant patents found - potentially clear FTO landscape."
        
        prompt = f"""
        Analyze the patent landscape for freedom-to-operate (FTO) assessment:
        
        Query: {query}
        Molecule: {molecule}
        
        Patents found: {len(patents_df)}
        
        Assess:
        - Patent coverage overlap
        - Expiration dates
        - FTO risks (High/Medium/Low)
        - Potential licensing needs
        - Design-around opportunities
        
        Provide a structured FTO risk assessment.
        """
        
        response = await self.llm.ainvoke(prompt)
        return response.content