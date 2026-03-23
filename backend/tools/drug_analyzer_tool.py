"""
Drug Analyzer MCP Tool

Comprehensive drug analysis tool that handles:
- Drug search by name/category
- SMILES notation retrieval
- Molecular property analysis (Lipinski, ADMET)
- Drug category listing

Consolidates multiple SMILES-related operations into single intelligent tool.
"""

from typing import Dict, Any, List
import pandas as pd
from pathlib import Path

# Import from existing smiles_analyzer_tool
from tools.smiles_analyzer_tool import (
    search_smiles as _search_smiles,
    analyze_smiles as _analyze_smiles,
    get_drug_smiles as _get_drug_smiles,
    list_drug_categories as _list_drug_categories
)


async def analyze_drug(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    MCP Tool: Comprehensive drug analysis
    
    This tool intelligently handles multiple drug analysis operations:
    1. Search drugs by name/category
    2. Get SMILES notation
    3. Analyze molecular properties
    4. Generate structure images
    5. Assess drug-likeness
    
    Args:
        payload: {
            "action": str (required) - "search", "analyze", "get_smiles", "list_categories", "full_analysis"
            
            # For action="search"
            "query": str - Drug name or category to search
            "exact_match": bool - Exact match vs fuzzy search
            
            # For action="get_smiles"
            "drug_name": str - Specific drug name
            
            # For action="analyze"
            "smiles": str - SMILES notation (if known)
            "drug_name": str - Drug name (will fetch SMILES if not provided)
            "include_admet": bool - Include ADMET predictions
            "include_variants": bool - Include structural variants
            "generate_image": bool - Generate 2D structure image
            
            # For action="full_analysis"
            "drug_name": str - Drug name for complete analysis
            "disease": str (optional) - Target disease for repurposing assessment
        }
    
    Returns:
        Depends on action:
        - search: {"results": [...], "count": int}
        - get_smiles: {"drug_name": str, "smiles": str, "category": str}
        - analyze: {"molecular_properties": {...}, "drug_likeness": {...}}
        - list_categories: {"categories": [...]}
        - full_analysis: Complete drug profile with all data
    """
    action = payload.get("action", "").lower()
    
    if not action:
        return {
            "error": "Action is required. Valid actions: search, get_smiles, analyze, list_categories, full_analysis"
        }
    
    # Route to appropriate sub-function
    if action == "search":
        return _handle_search(payload)
    
    elif action == "get_smiles":
        return _handle_get_smiles(payload)
    
    elif action == "analyze":
        return await _handle_analyze(payload)
    
    elif action == "list_categories":
        return _handle_list_categories(payload)
    
    elif action == "full_analysis":
        return await _handle_full_analysis(payload)
    
    else:
        return {
            "error": f"Unknown action: {action}. Valid actions: search, get_smiles, analyze, list_categories, full_analysis"
        }


def _handle_search(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle drug search action"""
    query = payload.get("query", "")
    exact_match = payload.get("exact_match", False)
    
    if not query:
        return {"error": "Query is required for search action", "results": [], "count": 0}
    
    result = _search_smiles({"query": query, "exact_match": exact_match})
    return result


def _handle_get_smiles(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle get SMILES action"""
    drug_name = payload.get("drug_name", "")
    
    if not drug_name:
        return {"error": "drug_name is required for get_smiles action"}
    
    result = _get_drug_smiles({"drug_name": drug_name})
    return result


async def _handle_analyze(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle molecular analysis action"""
    smiles = payload.get("smiles", "")
    drug_name = payload.get("drug_name", "")
    include_admet = payload.get("include_admet", True)
    include_variants = payload.get("include_variants", False)
    generate_image = payload.get("generate_image", False)
    
    # If SMILES not provided, try to get it from drug name
    if not smiles and drug_name:
        smiles_result = _get_drug_smiles({"drug_name": drug_name})
        if "error" in smiles_result:
            return {"error": f"Could not find SMILES for {drug_name}: {smiles_result['error']}"}
        smiles = smiles_result.get("smiles", "")
    
    if not smiles:
        return {"error": "Either smiles or drug_name is required for analyze action"}
    
    # Perform molecular analysis
    analysis_result = _analyze_smiles({
        "smiles": smiles,
        "include_admet": include_admet,
        "include_variants": include_variants
    })
    
    # Add drug name to result if provided
    if drug_name:
        analysis_result["drug_name"] = drug_name
    
    # Generate image if requested
    if generate_image:
        from agents.drug_analyzer_agent import DrugAnalyzerAgent
        analyzer = DrugAnalyzerAgent()
        image_data = analyzer._generate_molecule_image(smiles, drug_name, save_to_disk=True)
        analysis_result["structure_image"] = image_data
    
    return analysis_result


def _handle_list_categories(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle list categories action"""
    result = _list_drug_categories({})
    return result


async def _handle_full_analysis(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle full drug analysis - comprehensive profile
    
    Performs:
    1. Get SMILES notation
    2. Analyze molecular properties
    3. Generate structure image
    4. Assess drug-likeness
    5. Estimate repurposing potential (if disease provided)
    """
    drug_name = payload.get("drug_name", "")
    disease = payload.get("disease", "")
    
    if not drug_name:
        return {"error": "drug_name is required for full_analysis action"}
    
    # Step 1: Get SMILES
    smiles_result = _get_drug_smiles({"drug_name": drug_name})
    if "error" in smiles_result:
        return {"error": f"Drug not found: {smiles_result['error']}"}
    
    smiles = smiles_result.get("smiles", "")
    category = smiles_result.get("category", "")
    
    # Step 2: Analyze molecular properties
    analysis_result = _analyze_smiles({
        "smiles": smiles,
        "include_admet": True,
        "include_variants": False
    })
    
    # Step 3: Generate structure image
    from agents.drug_analyzer_agent import DrugAnalyzerAgent
    analyzer = DrugAnalyzerAgent()
    image_data = analyzer._generate_molecule_image(smiles, drug_name, save_to_disk=True)
    
    # Step 4: Assess repurposing potential if disease provided
    repurposing_assessment = None
    if disease:
        from utils.llm_utils import get_llm
        llm = get_llm()
        
        prompt = f"""
Assess the drug repurposing potential:

Drug: {drug_name}
Current Category: {category}
Target Disease: {disease}

Molecular Properties:
- Molecular Weight: {analysis_result.get('molecular_weight', 'N/A')} g/mol
- LogP: {analysis_result.get('logp', 'N/A')}
- Passes Lipinski: {analysis_result.get('passes_lipinski', False)}
- H-Bond Donors: {analysis_result.get('num_h_donors', 'N/A')}
- H-Bond Acceptors: {analysis_result.get('num_h_acceptors', 'N/A')}

Provide a brief assessment (2-3 sentences):
1. Repurposing potential (High/Medium/Low)
2. Key considerations
3. Recommended next steps
"""
        
        response = await llm.ainvoke(prompt)
        repurposing_assessment = response.content
    
    # Compile full analysis
    return {
        "drug_name": drug_name,
        "category": category,
        "smiles": smiles,
        "molecular_properties": {
            "molecular_formula": analysis_result.get("molecular_formula"),
            "molecular_weight": analysis_result.get("molecular_weight"),
            "logp": analysis_result.get("logp"),
            "num_h_donors": analysis_result.get("num_h_donors"),
            "num_h_acceptors": analysis_result.get("num_h_acceptors"),
            "num_rotatable_bonds": analysis_result.get("num_rotatable_bonds"),
            "tpsa": analysis_result.get("tpsa"),
        },
        "drug_likeness": {
            "passes_lipinski": analysis_result.get("passes_lipinski"),
            "lipinski_violations": analysis_result.get("lipinski_violations"),
            "rule_of_five_compliant": analysis_result.get("passes_lipinski"),
        },
        "admet": analysis_result.get("admet", {}),
        "structure_image": image_data,
        "repurposing_assessment": repurposing_assessment,
        "target_disease": disease if disease else None,
        "analysis_complete": True
    }
