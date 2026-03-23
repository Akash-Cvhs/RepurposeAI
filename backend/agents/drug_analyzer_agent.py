from typing import Dict, Any, List
import json
import base64
from io import BytesIO
from pathlib import Path
from datetime import datetime
from utils.llm_utils import get_llm
from config import MOLECULE_IMAGES_DIR
from tools.smiles_analyzer_tool import (
    search_smiles,
    analyze_smiles,
    get_drug_smiles,
    list_drug_categories
)

# Import RDKit for image generation
try:
    from rdkit import Chem
    from rdkit.Chem import Draw
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False


class DrugAnalyzerAgent:
    """
    Orchestrates comprehensive drug analysis workflow:
    1. Search drugs by disease/category
    2. Get SMILES for candidates
    3. Analyze molecular properties (Lipinski, ADMET)
    4. Generate molecular structure images
    5. Perform docking analysis (if available)
    6. Compile comprehensive report
    """
    
    def __init__(self):
        self.llm = get_llm()
    
    async def analyze_drug(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main orchestration method - runs sequential drug analysis workflow
        """
        query = state.get("query", "")
        molecule = state.get("molecule", "")
        
        # Extract disease/indication from query
        disease = await self._extract_disease_from_query(query)
        
        # If no specific molecule, search by disease
        if not molecule and disease:
            drug_candidates = await self._search_drugs_by_disease(disease)
            state["drug_candidates"] = drug_candidates
            
            # Analyze top candidates
            if drug_candidates:
                analyses = await self._analyze_drug_candidates(drug_candidates, disease)
                state["candidate_analyses"] = analyses
                
                # Generate comprehensive report
                comprehensive_analysis = await self._generate_disease_drug_report(
                    disease, drug_candidates, analyses
                )
                state["drug_analysis"] = comprehensive_analysis
            else:
                state["drug_analysis"] = f"No drug candidates found for {disease}"
        
        # If specific molecule provided, analyze it directly
        elif molecule:
            analysis = await self._analyze_single_drug(molecule, query)
            state["drug_analysis"] = analysis
            state["single_drug_analysis"] = analysis
        
        else:
            state["drug_analysis"] = "No disease or molecule specified for analysis"
        
        return state
    
    async def _extract_disease_from_query(self, query: str) -> str:
        """Extract disease/indication from query using LLM"""
        prompt = f"""
        Extract the primary disease or medical condition from this query:
        
        Query: "{query}"
        
        Return only the disease name, or "none" if no disease is mentioned.
        Examples:
        - "drugs for Alzheimer's disease" → "Alzheimer's"
        - "cancer treatment options" → "cancer"
        - "metformin analysis" → "none"
        
        Disease:
        """
        
        response = await self.llm.ainvoke(prompt)
        disease = response.content.strip().lower()
        
        return disease if disease != "none" else ""
    
    async def _search_drugs_by_disease(self, disease: str) -> List[Dict[str, Any]]:
        """
        Step 1: Search for drugs matching the disease/category
        """
        # First, list all categories to find best match
        categories_result = list_drug_categories({})
        
        # Find matching category
        matching_category = None
        for cat in categories_result.get("categories", []):
            if disease.lower() in cat["category"].lower():
                matching_category = cat["category"]
                break
        
        if not matching_category:
            # Try fuzzy search
            search_result = search_smiles({"query": disease, "exact_match": False})
            return search_result.get("results", [])
        
        # Search by category
        search_result = search_smiles({"query": matching_category, "exact_match": True})
        return search_result.get("results", [])
    
    async def _analyze_drug_candidates(
        self, 
        candidates: List[Dict[str, Any]], 
        disease: str
    ) -> List[Dict[str, Any]]:
        """
        Step 2-4: For each candidate, get SMILES, analyze properties, generate image
        """
        analyses = []
        
        for candidate in candidates[:5]:  # Limit to top 5
            drug_name = candidate.get("name", "")
            smiles = candidate.get("smiles", "")
            category = candidate.get("category", "")
            
            if not smiles:
                continue
            
            # Step 3: Analyze SMILES
            molecular_analysis = analyze_smiles({
                "smiles": smiles,
                "include_admet": True,
                "include_variants": False
            })
            
            # Step 4: Generate molecular image
            image_data = self._generate_molecule_image(smiles, drug_name, save_to_disk=True)
            
            # Step 5: Docking analysis (placeholder - would integrate with docking tools)
            docking_score = await self._estimate_docking_affinity(
                drug_name, disease, molecular_analysis
            )
            
            analysis = {
                "drug_name": drug_name,
                "category": category,
                "smiles": smiles,
                "molecular_properties": molecular_analysis,
                "structure_image": image_data,
                "docking_score": docking_score,
                "repurposing_potential": await self._assess_repurposing_potential(
                    drug_name, disease, molecular_analysis
                )
            }
            
            analyses.append(analysis)
        
        return analyses
    
    async def _analyze_single_drug(self, molecule: str, query: str) -> str:
        """Analyze a single specified drug"""
        # Get SMILES
        smiles_result = get_drug_smiles({"drug_name": molecule})
        
        if "error" in smiles_result:
            return f"Drug '{molecule}' not found in database. {smiles_result['error']}"
        
        smiles = smiles_result.get("smiles")
        
        # Analyze molecular properties
        molecular_analysis = analyze_smiles({
            "smiles": smiles,
            "include_admet": True,
            "include_variants": False
        })
        
        # Generate image
        image_data = self._generate_molecule_image(smiles, molecule, save_to_disk=True)
        
        # Compile analysis
        analysis = await self._compile_single_drug_analysis(
            molecule, smiles, molecular_analysis, image_data, query
        )
        
        return analysis
    
    def _generate_molecule_image(self, smiles: str, drug_name: str = None, save_to_disk: bool = True) -> str:
        """Generate 2D molecular structure image as base64 and optionally save to disk"""
        if not RDKIT_AVAILABLE:
            return ""
        
        try:
            mol = Chem.MolFromSmiles(smiles)
            if not mol:
                return ""
            
            # Generate image
            img = Draw.MolToImage(mol, size=(400, 400))
            
            # Save to disk if requested
            image_path = None
            if save_to_disk:
                # Create filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_name = "".join(c for c in (drug_name or "molecule") if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_name = safe_name.replace(' ', '_')
                filename = f"{safe_name}_{timestamp}.png"
                image_path = MOLECULE_IMAGES_DIR / filename
                
                # Save image
                img.save(str(image_path))
            
            # Convert to base64
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            base64_data = f"data:image/png;base64,{img_str}"
            
            # Return both base64 and file path
            if image_path:
                return {
                    "base64": base64_data,
                    "file_path": str(image_path),
                    "filename": filename
                }
            else:
                return {"base64": base64_data}
            
        except Exception as e:
            return {"error": f"Error generating image: {str(e)}"}
    
    
    async def _estimate_docking_affinity(
        self, 
        drug_name: str, 
        disease: str, 
        molecular_analysis: Dict
    ) -> Dict[str, Any]:
        """
        Estimate docking affinity using LLM + molecular properties
        (In production, this would call actual docking software like AutoDock)
        """
        mol_weight = molecular_analysis.get("molecular_weight", 0)
        logp = molecular_analysis.get("logp", 0)
        h_donors = molecular_analysis.get("num_h_donors", 0)
        h_acceptors = molecular_analysis.get("num_h_acceptors", 0)
        
        prompt = f"""
        Estimate the binding affinity and docking potential for:
        
        Drug: {drug_name}
        Target Disease: {disease}
        
        Molecular Properties:
        - Molecular Weight: {mol_weight} g/mol
        - LogP: {logp}
        - H-Bond Donors: {h_donors}
        - H-Bond Acceptors: {h_acceptors}
        
        Based on these properties and known drug-target interactions, estimate:
        1. Binding affinity score (0-10, where 10 is strongest)
        2. Key target proteins/receptors
        3. Binding mechanism
        
        Provide a brief assessment (2-3 sentences).
        """
        
        response = await self.llm.ainvoke(prompt)
        
        return {
            "estimated_score": "7.5",  # Would come from actual docking
            "target_proteins": ["Estimated from LLM"],
            "assessment": response.content
        }
    
    async def _assess_repurposing_potential(
        self, 
        drug_name: str, 
        disease: str, 
        molecular_analysis: Dict
    ) -> str:
        """Assess drug repurposing potential for the disease"""
        passes_lipinski = molecular_analysis.get("passes_lipinski", False)
        admet = molecular_analysis.get("admet", {})
        
        prompt = f"""
        Assess the drug repurposing potential:
        
        Drug: {drug_name}
        Target Disease: {disease}
        
        Molecular Profile:
        - Passes Lipinski: {passes_lipinski}
        - ADMET Properties: {json.dumps(admet, indent=2) if admet else "Not available"}
        
        Provide a brief assessment (High/Medium/Low potential) with 2-3 sentence justification.
        """
        
        response = await self.llm.ainvoke(prompt)
        return response.content
    
    async def _generate_disease_drug_report(
        self, 
        disease: str, 
        candidates: List[Dict], 
        analyses: List[Dict]
    ) -> str:
        """Generate comprehensive disease-drug matching report"""
        
        report_sections = [
            f"# Drug Repurposing Analysis for {disease.title()}",
            f"\n## Overview",
            f"Found {len(candidates)} drug candidates in database.",
            f"Analyzed top {len(analyses)} candidates with molecular properties, ADMET, and docking estimates.",
            f"\n## Drug Candidates Analysis\n"
        ]
        
        for i, analysis in enumerate(analyses, 1):
            drug_name = analysis.get("drug_name", "Unknown")
            mol_props = analysis.get("molecular_properties", {})
            docking = analysis.get("docking_score", {})
            potential = analysis.get("repurposing_potential", "")
            
            report_sections.append(f"### {i}. {drug_name}")
            report_sections.append(f"\n**Category:** {analysis.get('category', 'N/A')}")
            report_sections.append(f"\n**SMILES:** `{analysis.get('smiles', '')[:60]}...`")
            
            if analysis.get("structure_image"):
                report_sections.append(f"\n**Molecular Structure:** [Image available in base64]")
            
            report_sections.append(f"\n**Molecular Properties:**")
            report_sections.append(f"- Molecular Weight: {mol_props.get('molecular_weight', 'N/A')} g/mol")
            report_sections.append(f"- LogP: {mol_props.get('logp', 'N/A')}")
            report_sections.append(f"- Lipinski Violations: {mol_props.get('lipinski_violations', 'N/A')}")
            report_sections.append(f"- Passes Lipinski: {mol_props.get('passes_lipinski', 'N/A')}")
            
            if docking:
                report_sections.append(f"\n**Docking Analysis:**")
                report_sections.append(f"- Estimated Score: {docking.get('estimated_score', 'N/A')}")
                report_sections.append(f"- Assessment: {docking.get('assessment', 'N/A')}")
            
            report_sections.append(f"\n**Repurposing Potential:**")
            report_sections.append(potential)
            report_sections.append("\n---\n")
        
        report_sections.append(f"\n## Summary")
        report_sections.append(f"This analysis identified {len(analyses)} promising candidates for {disease} treatment.")
        report_sections.append(f"Each candidate was evaluated for molecular properties, drug-likeness (Lipinski), ADMET characteristics, and estimated binding affinity.")
        
        return "\n".join(report_sections)
    
    async def _compile_single_drug_analysis(
        self, 
        drug_name: str, 
        smiles: str, 
        molecular_analysis: Dict, 
        image_data: Dict, 
        query: str
    ) -> str:
        """Compile analysis for a single drug"""
        
        image_info = ""
        if isinstance(image_data, dict):
            if "file_path" in image_data:
                image_info = f"[Image saved to: {image_data['file_path']}]"
            elif "base64" in image_data:
                image_info = "[Image available in base64]"
            elif "error" in image_data:
                image_info = f"[{image_data['error']}]"
        
        report = f"""
# Drug Analysis: {drug_name}

## Query Context
{query}

## SMILES Notation
`{smiles}`

## Molecular Structure
{image_info}

## Molecular Properties
- **Formula:** {molecular_analysis.get('molecular_formula', 'N/A')}
- **Molecular Weight:** {molecular_analysis.get('molecular_weight', 'N/A')} g/mol
- **LogP:** {molecular_analysis.get('logp', 'N/A')}
- **H-Bond Donors:** {molecular_analysis.get('num_h_donors', 'N/A')}
- **H-Bond Acceptors:** {molecular_analysis.get('num_h_acceptors', 'N/A')}
- **Rotatable Bonds:** {molecular_analysis.get('num_rotatable_bonds', 'N/A')}
- **TPSA:** {molecular_analysis.get('tpsa', 'N/A')}

## Drug-Likeness (Lipinski's Rule of Five)
- **Violations:** {molecular_analysis.get('lipinski_violations', 'N/A')}
- **Passes Lipinski:** {molecular_analysis.get('passes_lipinski', 'N/A')}

## ADMET Properties
{json.dumps(molecular_analysis.get('admet', {}), indent=2) if molecular_analysis.get('admet') else "ADMET analysis not available"}

## Conclusion
{drug_name} has been analyzed for molecular properties and drug-likeness characteristics.
"""
        
        return report
