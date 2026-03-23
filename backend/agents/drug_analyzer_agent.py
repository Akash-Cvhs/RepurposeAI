from typing import Dict, Any, List
import json
from langchain_openai import ChatOpenAI
from config import DEFAULT_LLM_MODEL

class DrugAnalyzerAgent:
    """Analyzes drug properties, mechanisms, pharmacokinetics, and interactions"""
    
    def __init__(self):
        self.llm = ChatOpenAI(model=DEFAULT_LLM_MODEL)
        self.drug_database = self._load_drug_database()
    
    async def analyze_drug(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive drug analysis including properties and interactions"""
        query = state.get("query", "")
        molecule = state.get("molecule", "")
        
        if not molecule:
            # Try to extract molecule from query
            molecule = await self._extract_molecule_from_query(query)
        
        if molecule:
            # Perform comprehensive drug analysis
            drug_properties = await self._analyze_drug_properties(molecule)
            mechanism_analysis = await self._analyze_mechanism_of_action(molecule, query)
            pharmacokinetics = await self._analyze_pharmacokinetics(molecule)
            interactions = await self._analyze_drug_interactions(molecule)
            repurposing_potential = await self._assess_repurposing_potential(molecule, query)
            
            # Compile analysis
            comprehensive_analysis = await self._compile_drug_analysis(
                molecule, drug_properties, mechanism_analysis, 
                pharmacokinetics, interactions, repurposing_potential
            )
            
            state["drug_properties"] = drug_properties
            state["mechanism_of_action"] = mechanism_analysis
            state["pharmacokinetics"] = pharmacokinetics
            state["drug_interactions"] = interactions
            state["repurposing_potential"] = repurposing_potential
            state["drug_analysis"] = comprehensive_analysis
        else:
            state["drug_analysis"] = "No specific drug identified for detailed analysis"
            state["drug_properties"] = {}
            state["mechanism_of_action"] = ""
            state["pharmacokinetics"] = ""
            state["drug_interactions"] = []
            state["repurposing_potential"] = ""
        
        return state
    
    async def _extract_molecule_from_query(self, query: str) -> str:
        """Extract drug/molecule name from query using LLM"""
        prompt = f"""
        Extract the primary drug or molecule name from this research query:
        
        Query: "{query}"
        
        Return only the drug/molecule name if clearly identifiable, or "none" if no specific drug is mentioned.
        Examples:
        - "aspirin for Alzheimer's" → "aspirin"
        - "metformin in cancer treatment" → "metformin"
        - "cardiovascular disease treatments" → "none"
        
        Drug/Molecule:
        """
        
        response = await self.llm.ainvoke(prompt)
        extracted = response.content.strip().lower()
        
        return extracted if extracted != "none" else ""
    
    async def _analyze_drug_properties(self, molecule: str) -> Dict[str, Any]:
        """Analyze basic drug properties and characteristics"""
        prompt = f"""
        Provide a comprehensive analysis of the drug properties for: {molecule}
        
        Include the following information:
        - Chemical class and structure type
        - Molecular weight and formula (if known)
        - Physical properties (solubility, stability)
        - Therapeutic class and primary indications
        - Route of administration
        - Dosage forms available
        - Generic/brand names
        
        Format as structured information with clear categories.
        """
        
        response = await self.llm.ainvoke(prompt)
        
        # Parse response into structured format
        properties = {
            "molecule_name": molecule,
            "analysis": response.content,
            "therapeutic_class": self._extract_therapeutic_class(response.content),
            "primary_indications": self._extract_indications(response.content)
        }
        
        return properties
    
    async def _analyze_mechanism_of_action(self, molecule: str, indication: str) -> str:
        """Analyze mechanism of action for the drug"""
        prompt = f"""
        Analyze the mechanism of action for {molecule} in the context of {indication}:
        
        Provide detailed information on:
        - Primary molecular targets (receptors, enzymes, pathways)
        - Cellular and tissue-level effects
        - Physiological outcomes
        - Relevant for repurposing: off-target effects and secondary mechanisms
        - Potential synergistic pathways for new indications
        
        Focus on mechanisms that could be relevant for drug repurposing opportunities.
        """
        
        response = await self.llm.ainvoke(prompt)
        return response.content
    
    async def _analyze_pharmacokinetics(self, molecule: str) -> str:
        """Analyze pharmacokinetic properties"""
        prompt = f"""
        Analyze the pharmacokinetic profile of {molecule}:
        
        Cover the following ADME properties:
        - Absorption: bioavailability, food effects, formulation considerations
        - Distribution: tissue penetration, protein binding, volume of distribution
        - Metabolism: primary metabolic pathways, CYP enzymes involved, active metabolites
        - Excretion: elimination routes, half-life, clearance
        
        Highlight any PK properties that could impact repurposing potential:
        - Blood-brain barrier penetration
        - Tissue-specific accumulation
        - Drug-drug interaction potential
        - Dose-dependent kinetics
        """
        
        response = await self.llm.ainvoke(prompt)
        return response.content
    
    async def _analyze_drug_interactions(self, molecule: str) -> List[Dict[str, str]]:
        """Analyze potential drug-drug interactions"""
        prompt = f"""
        Identify significant drug-drug interactions for {molecule}:
        
        Focus on:
        - Major CYP enzyme interactions (inhibition/induction)
        - Transporter interactions (P-gp, OATP, etc.)
        - Pharmacodynamic interactions
        - Contraindicated combinations
        - Clinically significant interactions requiring dose adjustment
        
        For each interaction, specify:
        - Interacting drug/class
        - Mechanism of interaction
        - Clinical significance (major/moderate/minor)
        - Management recommendations
        
        Format as a structured list.
        """
        
        response = await self.llm.ainvoke(prompt)
        
        # Parse interactions into structured format
        interactions = self._parse_interactions(response.content)
        return interactions
    
    async def _assess_repurposing_potential(self, molecule: str, indication: str) -> str:
        """Assess drug repurposing potential based on properties"""
        prompt = f"""
        Assess the drug repurposing potential of {molecule} for {indication}:
        
        Consider:
        - Existing safety profile and known adverse effects
        - Mechanism of action alignment with new indication
        - Pharmacokinetic suitability for new indication
        - Dosing considerations for repurposed use
        - Regulatory pathway advantages (505(b)(2), etc.)
        - Formulation or delivery modifications needed
        - Competitive landscape and IP considerations
        
        Provide a structured assessment with:
        - Repurposing feasibility score (High/Medium/Low)
        - Key advantages for repurposing
        - Major challenges or limitations
        - Recommended development strategy
        """
        
        response = await self.llm.ainvoke(prompt)
        return response.content
    
    async def _compile_drug_analysis(self, molecule: str, properties: Dict, mechanism: str,
                                   pharmacokinetics: str, interactions: List, 
                                   repurposing: str) -> str:
        """Compile comprehensive drug analysis report"""
        prompt = f"""
        Compile a comprehensive drug analysis summary for {molecule}:
        
        Based on the following analyses:
        
        DRUG PROPERTIES:
        {properties.get('analysis', '')}
        
        MECHANISM OF ACTION:
        {mechanism}
        
        PHARMACOKINETICS:
        {pharmacokinetics}
        
        REPURPOSING ASSESSMENT:
        {repurposing}
        
        Create a concise executive summary (2-3 paragraphs) that:
        - Highlights key drug characteristics relevant to repurposing
        - Identifies the most promising aspects for new indications
        - Notes critical limitations or safety considerations
        - Provides an overall assessment of repurposing viability
        """
        
        response = await self.llm.ainvoke(prompt)
        return response.content
    
    def _load_drug_database(self) -> Dict[str, Any]:
        """Load drug database (mock implementation)"""
        # In production, this would load from a comprehensive drug database
        return {
            "aspirin": {
                "class": "NSAID",
                "targets": ["COX-1", "COX-2"],
                "indications": ["pain", "inflammation", "cardiovascular protection"]
            },
            "metformin": {
                "class": "Biguanide",
                "targets": ["AMPK", "Complex I"],
                "indications": ["diabetes", "metabolic syndrome"]
            },
            "statins": {
                "class": "HMG-CoA reductase inhibitor",
                "targets": ["HMG-CoA reductase"],
                "indications": ["hypercholesterolemia", "cardiovascular disease"]
            }
        }
    
    def _extract_therapeutic_class(self, analysis: str) -> str:
        """Extract therapeutic class from analysis text"""
        # Simple extraction - could be enhanced with NLP
        classes = ["NSAID", "ACE inhibitor", "Beta blocker", "Statin", "Antibiotic", "Antiviral"]
        
        for drug_class in classes:
            if drug_class.lower() in analysis.lower():
                return drug_class
        
        return "Unknown"
    
    def _extract_indications(self, analysis: str) -> List[str]:
        """Extract primary indications from analysis text"""
        # Simple extraction - could be enhanced with NLP
        common_indications = [
            "hypertension", "diabetes", "pain", "inflammation", "infection",
            "cancer", "depression", "anxiety", "cardiovascular disease"
        ]
        
        found_indications = []
        for indication in common_indications:
            if indication.lower() in analysis.lower():
                found_indications.append(indication)
        
        return found_indications[:3]  # Return top 3
    
    def _parse_interactions(self, interaction_text: str) -> List[Dict[str, str]]:
        """Parse drug interactions from text into structured format"""
        # Simple parsing - could be enhanced with NLP
        interactions = []
        
        # Mock parsing for demonstration
        if "warfarin" in interaction_text.lower():
            interactions.append({
                "drug": "Warfarin",
                "mechanism": "Increased bleeding risk",
                "severity": "Major",
                "management": "Monitor INR closely"
            })
        
        if "cyp" in interaction_text.lower():
            interactions.append({
                "drug": "CYP substrates",
                "mechanism": "Enzyme inhibition/induction",
                "severity": "Moderate",
                "management": "Consider dose adjustment"
            })
        
        return interactions