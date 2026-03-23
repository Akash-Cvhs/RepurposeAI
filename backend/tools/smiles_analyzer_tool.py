"""
MCP Tool: SMILES Analyzer

Analyzes drug molecules using SMILES notation.
Integrates with the drug_analyser service for molecular property analysis.
"""

import sys
from pathlib import Path
import pandas as pd

# Add drug_analyser to path
DRUG_ANALYSER_PATH = Path(__file__).parent.parent / "services" / "drug_analyser"
sys.path.insert(0, str(DRUG_ANALYSER_PATH))

from rdkit import Chem
from rdkit.Chem import Descriptors, Lipinski, RDKFingerprint

# Import drug_analyser utilities
try:
    from utils.admet import check_admet_properties
    from utils.molecule_ops import generate_permutations, generate_combinations
except ImportError:
    # Fallback if utils not available
    check_admet_properties = None
    generate_permutations = None
    generate_combinations = None

# Path to SMILES database
SMILES_DATA_PATH = DRUG_ANALYSER_PATH / "data" / "data.csv"

# Cache for SMILES database
_smiles_db = None


def _load_smiles_database():
    """Load SMILES database from CSV"""
    global _smiles_db
    if _smiles_db is None:
        if SMILES_DATA_PATH.exists():
            _smiles_db = pd.read_csv(SMILES_DATA_PATH)
        else:
            _smiles_db = pd.DataFrame(columns=["category", "name", "smiles"])
    return _smiles_db


def search_smiles(payload: dict) -> dict:
    """
    Search for SMILES notation by drug name or category.
    
    Payload:
        query (str): Drug name or category to search
        exact_match (bool): Whether to require exact match (default: False)
    
    Returns:
        results (list): List of matching drugs with SMILES
    """
    query = payload.get("query", "").lower()
    exact_match = payload.get("exact_match", False)
    
    if not query:
        return {"error": "query is required", "results": []}
    
    db = _load_smiles_database()
    
    if exact_match:
        matches = db[
            (db["name"].str.lower() == query) |
            (db["category"].str.lower() == query)
        ]
    else:
        matches = db[
            db["name"].str.lower().str.contains(query, na=False) |
            db["category"].str.lower().str.contains(query, na=False)
        ]
    
    results = matches.to_dict("records")
    
    return {
        "query": query,
        "count": len(results),
        "results": results
    }


def analyze_smiles(payload: dict) -> dict:
    """
    Analyze a SMILES string for molecular properties.
    
    Payload:
        smiles (str): SMILES notation
        include_admet (bool): Include ADMET analysis (default: True)
        include_variants (bool): Generate and analyze variants (default: False)
    
    Returns:
        analysis (dict): Molecular properties and analysis
    """
    smiles = payload.get("smiles", "")
    include_admet = payload.get("include_admet", True)
    include_variants = payload.get("include_variants", False)
    
    if not smiles:
        return {"error": "smiles is required"}
    
    # Parse molecule
    mol = Chem.MolFromSmiles(smiles)
    if not mol:
        return {"error": "Invalid SMILES notation"}
    
    # Basic properties
    analysis = {
        "smiles": smiles,
        "valid": True,
        "molecular_formula": Chem.rdMolDescriptors.CalcMolFormula(mol),
        "molecular_weight": Descriptors.MolWt(mol),
        "logp": Descriptors.MolLogP(mol),
        "num_h_donors": Lipinski.NumHDonors(mol),
        "num_h_acceptors": Lipinski.NumHAcceptors(mol),
        "num_rotatable_bonds": Lipinski.NumRotatableBonds(mol),
        "tpsa": Descriptors.TPSA(mol),
    }
    
    # Lipinski's Rule of Five
    analysis["lipinski_violations"] = sum([
        analysis["molecular_weight"] > 500,
        analysis["logp"] > 5,
        analysis["num_h_donors"] > 5,
        analysis["num_h_acceptors"] > 10
    ])
    analysis["passes_lipinski"] = analysis["lipinski_violations"] == 0
    
    # Fingerprint
    fingerprint = RDKFingerprint(mol)
    analysis["fingerprint_on_bits"] = list(fingerprint.GetOnBits())[:20]  # First 20
    
    # ADMET analysis (if available)
    if include_admet and check_admet_properties:
        try:
            admet_result = check_admet_properties(smiles)
            analysis["admet"] = admet_result
        except Exception as e:
            analysis["admet_error"] = str(e)
    
    # Variants (if requested)
    if include_variants:
        variants = []
        
        if generate_permutations:
            try:
                perms = generate_permutations(smiles)
                variants.extend([{"type": "permutation", "smiles": s} for s in perms[:3]])
            except:
                pass
        
        if generate_combinations:
            try:
                combs = generate_combinations(smiles, ["C", "CC", "CO"])
                variants.extend([{"type": "combination", "smiles": s} for s in combs[:3]])
            except:
                pass
        
        analysis["variants"] = variants
    
    return analysis


def get_drug_smiles(payload: dict) -> dict:
    """
    Get SMILES notation for a specific drug by name.
    
    Payload:
        drug_name (str): Name of the drug
    
    Returns:
        smiles (str): SMILES notation
        category (str): Drug category
    """
    drug_name = payload.get("drug_name", "").lower()
    
    if not drug_name:
        return {"error": "drug_name is required"}
    
    db = _load_smiles_database()
    
    # Try exact match first
    match = db[db["name"].str.lower() == drug_name]
    
    if match.empty:
        # Try partial match
        match = db[db["name"].str.lower().str.contains(drug_name, na=False)]
    
    if match.empty:
        return {"error": f"Drug '{drug_name}' not found in database"}
    
    result = match.iloc[0].to_dict()
    
    return {
        "drug_name": result["name"],
        "category": result["category"],
        "smiles": result["smiles"]
    }


def list_drug_categories(payload: dict) -> dict:
    """
    List all available drug categories in the database.
    
    Returns:
        categories (list): List of unique categories with counts
    """
    db = _load_smiles_database()
    
    category_counts = db["category"].value_counts().to_dict()
    
    categories = [
        {"category": cat, "count": count}
        for cat, count in category_counts.items()
    ]
    
    return {
        "total_drugs": len(db),
        "categories": categories
    }
