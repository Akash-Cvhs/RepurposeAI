# SMILES Analyzer Integration

## ✅ Configured

Your drug_analyser service is now integrated with the MCP workflow and drug_analyzer_agent.

## What Was Added

### 1. SMILES Analyzer Tool (`tools/smiles_analyzer_tool.py`)

Four MCP tools for molecular analysis:

| Tool | Purpose | Input |
|------|---------|-------|
| `search_smiles` | Search drugs by name/category | `query`, `exact_match` |
| `analyze_smiles` | Analyze molecular properties | `smiles`, `include_admet`, `include_variants` |
| `get_drug_smiles` | Get SMILES for specific drug | `drug_name` |
| `list_drug_categories` | List all drug categories | none |

### 2. MCP Server Registration

All 4 tools registered in `backend/mcp/server.py`:
- Available at `http://localhost:8001/mcp/run`
- Includes Pydantic validation schemas
- Cached results for performance

### 3. Drug Analyzer Agent Integration

`backend/agents/drug_analyzer_agent.py` now:
- Automatically fetches SMILES notation for molecules
- Performs molecular property analysis (Lipinski, ADMET)
- Includes SMILES data in drug properties analysis
- Passes molecular data to LLM for enhanced insights

## Data Source

**Location:** `backend/services/drug_analyser/data/data.csv`

**Current Database:**
- 20 drugs total
- 3 categories: Tumor (9), Alzheimer's (7), Paracetamol (4)
- Each entry: category, name, SMILES notation

## Molecular Properties Analyzed

From SMILES notation:
- Molecular formula & weight
- LogP (lipophilicity)
- H-bond donors/acceptors
- Rotatable bonds
- TPSA (topological polar surface area)
- Lipinski's Rule of Five compliance
- ADMET properties (if utils available)

## Usage Examples

### Direct Tool Usage

```python
from tools.smiles_analyzer_tool import get_drug_smiles, analyze_smiles

# Get SMILES for a drug
result = get_drug_smiles({"drug_name": "Donepezil"})
# Returns: {"drug_name": "Donepezil (Aricept)", "category": "Alzheimer's", "smiles": "..."}

# Analyze molecular properties
analysis = analyze_smiles({
    "smiles": "CN(C)C(=O)CCc1ccc(OCC2COCCN2C)cc1",
    "include_admet": True
})
# Returns: molecular_weight, logp, lipinski_violations, etc.
```

### Via MCP Server

```bash
curl -X POST http://localhost:8001/mcp/run \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "get_drug_smiles",
    "payload": {"drug_name": "Donepezil"},
    "session_id": "test"
  }'
```

### Via Drug Analyzer Agent

When the orchestrator runs the drug_analyzer_agent:
1. Agent extracts molecule name from query
2. Fetches SMILES from database
3. Analyzes molecular properties
4. Includes in comprehensive drug analysis
5. LLM uses molecular data for insights

## Test Results

```
✓ List Categories: 20 drugs, 3 categories
✓ Search SMILES: Found 7 Alzheimer's drugs
✓ Get Drug SMILES: Retrieved Donepezil successfully
✓ Analyze SMILES: 
  - Molecular Weight: 306.41 g/mol
  - LogP: 1.42
  - Lipinski Violations: 0
  - Passes Lipinski: True
✓ Invalid SMILES: Correctly rejected
```

## Adding More Drugs

Edit `backend/services/drug_analyser/data/data.csv`:

```csv
category,name,smiles
Alzheimer's,Donepezil (Aricept),CN(C)C(=O)CCc1ccc(OCC2COCCN2C)cc1
Cancer,Metformin,CN(C)C(=N)NC(=N)N
...
```

No code changes needed — tools automatically load the updated CSV.

## Dependencies Added

- `rdkit==2023.9.6` - Molecular analysis
- `langchain-groq==0.1.5` - LLM provider support

## Testing

```bash
cd backend
python scripts/test_smiles_tools.py
```

## Integration Flow

```
User Query
    ↓
MCP Orchestrator
    ↓
Drug Analyzer Agent
    ↓
get_drug_smiles() → SMILES notation
    ↓
analyze_smiles() → Molecular properties
    ↓
LLM Analysis (with molecular data)
    ↓
Comprehensive Drug Report
```

The SMILES data enriches the drug analysis with quantitative molecular properties that complement the LLM's qualitative insights.
