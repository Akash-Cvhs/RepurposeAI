# Drug Analyzer Agent - Query Response Examples

## Query: "Will paracetamol cure heart disease?"

### Response Type: **No Match Found**

**What happens:**
1. ✓ Extracts disease: "heart disease"
2. ✓ Searches database for heart disease drugs
3. ✗ Finds 0 candidates (no heart disease category in database)
4. Returns: "No drug candidates found for heart disease"

**Output:**
```
Disease extracted: heart disease
Drug candidates found: 0
Analyses completed: 0

REPORT:
No drug candidates found for heart disease
```

**Why:** The database only contains:
- Tumor (9 drugs)
- Alzheimer's (7 drugs)
- Paracetamol (4 drugs)

---

## Query: "Will paracetamol cure tumor?"

### Response Type: **Disease Match - Multiple Candidates**

**What happens:**
1. ✓ Extracts disease: "tumor"
2. ✓ Searches database for tumor drugs
3. ✓ Finds 9 candidates
4. ✓ Analyzes top 5 with molecular properties
5. ✓ Generates images for each
6. ✓ Estimates docking scores
7. ✓ Assesses repurposing potential
8. Returns comprehensive report

**Output:**
```
Disease extracted: tumor
Drug candidates found: 9

Drugs found:
  - Cisplatin
  - Cyclophosphamide
  - Doxorubicin
  - Imatinib
  - Methotrexate

Analyses completed: 5

REPORT (11,942 characters):
# Drug Repurposing Analysis for Tumor

## Overview
Found 9 drug candidates in database.
Analyzed top 5 candidates with molecular properties, ADMET, and docking estimates.

## Drug Candidates Analysis

### 1. Cisplatin
**Category:** Tumor
**SMILES:** `Cl[Pt](Cl)(Cl)Cl`
**Molecular Structure:** [Image saved to: .../Cisplatin_20260323_170436.png]

**Molecular Properties:**
- Molecular Weight: 336.89 g/mol
- LogP: 2.76
- Lipinski Violations: 0
- Passes Lipinski: True

**Docking Analysis:**
- Estimated Score: 8.5
- Assessment: Cisplatin forms highly stable, covalent cross-links with DNA...

**Repurposing Potential:**
High potential for tumor treatment...

[... continues for 5 drugs ...]
```

---

## Query: "Analyze paracetamol for tumor treatment"

### Response Type: **Specific Drug Analysis**

**What happens:**
1. ✓ Extracts molecule: "paracetamol"
2. ✓ Gets SMILES from database
3. ✓ Analyzes molecular properties
4. ✓ Generates and saves image
5. ✓ Compiles single-drug report

**Output:**
```
REPORT (679 characters):
# Drug Analysis: paracetamol

## Query Context
analyze paracetamol for tumor treatment

## SMILES Notation
`CC(=O)NC1=CC=C(O)C=C1`

## Molecular Structure
[Image saved to: .../paracetamol_20260323_170439.png]

## Molecular Properties
- Formula: C8H9NO2
- Molecular Weight: 151.165 g/mol
- LogP: 1.35
- H-Bond Donors: 2
- H-Bond Acceptors: 2
- Rotatable Bonds: 1
- TPSA: 49.33

## Drug-Likeness (Lipinski's Rule of Five)
- Violations: 0
- Passes Lipinski: True

## Conclusion
paracetamol has been analyzed for molecular properties and drug-likeness characteristics.
```

**Image saved:** `backend/archives/molecule_images/paracetamol_20260323_170439.png`

---

## Query: "What drugs are available for Alzheimer's disease?"

### Response Type: **Disease Match - Multiple Candidates**

**What happens:**
1. ✓ Extracts disease: "alzheimer's"
2. ✓ Searches database
3. ✓ Finds 7 candidates
4. ✓ Analyzes top 5
5. ✓ Generates images
6. Returns comprehensive report

**Output:**
```
Drug candidates found: 7
  - Donepezil (Aricept)
  - Galantamine
  - Rivastigmine (Exelon)
  - Memantine (Namenda)
  - Tacrine

Analyses completed: 5

Each analysis includes:
  ✓ Molecular properties (MW, LogP, Lipinski)
  ✓ Structure image (saved to disk)
  ✓ Docking score estimate
  ✓ Repurposing potential assessment
```

---

## Query: "Analyze Donepezil"

### Response Type: **Specific Drug Analysis**

**What happens:**
1. ✓ Extracts molecule: "Donepezil"
2. ✓ Gets SMILES: `CN(C)C(=O)CCc1ccc(OCC2COCCN2C)cc1`
3. ✓ Analyzes properties
4. ✓ Generates image
5. Returns detailed report

**Output:**
```
# Drug Analysis: Donepezil

Molecular Properties:
- Formula: C17H26N2O3
- Molecular Weight: 306.41 g/mol
- LogP: 1.42
- Lipinski Violations: 0
- Passes Lipinski: True

Image: Donepezil_20260323_170011.png
```

---

## Response Summary Table

| Query Type | Disease Match | Drug in DB | Response |
|------------|---------------|------------|----------|
| "paracetamol cure heart disease" | ✗ No | N/A | "No candidates found" |
| "paracetamol cure tumor" | ✓ Yes | ✓ Yes | Multi-drug analysis (9 tumor drugs) |
| "analyze paracetamol" | N/A | ✓ Yes | Single drug analysis |
| "drugs for Alzheimer's" | ✓ Yes | ✓ Yes | Multi-drug analysis (7 drugs) |
| "analyze UnknownDrug" | N/A | ✗ No | "Drug not found in database" |

---

## Sequential Workflow Steps

For **disease-based queries** (e.g., "paracetamol cure tumor"):

```
1. Extract Disease → "tumor"
2. Search Database → Find 9 tumor drugs
3. For each drug (top 5):
   a. Get SMILES notation
   b. Analyze molecular properties
   c. Generate structure image
   d. Estimate docking score
   e. Assess repurposing potential
4. Compile comprehensive report
5. Return results with images
```

For **specific drug queries** (e.g., "analyze paracetamol"):

```
1. Extract Molecule → "paracetamol"
2. Get SMILES from database
3. Analyze molecular properties
4. Generate structure image
5. Compile single-drug report
6. Return results with image
```

---

## Key Features in Response

✓ **Molecular Properties:** MW, LogP, H-bonds, TPSA  
✓ **Drug-Likeness:** Lipinski's Rule of Five compliance  
✓ **Structure Images:** Saved to disk + base64 for embedding  
✓ **Docking Estimates:** LLM-based binding affinity scores  
✓ **Repurposing Assessment:** High/Medium/Low potential with justification  
✓ **ADMET Properties:** If available from drug_analyser utils  

---

## Error Handling

| Scenario | Response |
|----------|----------|
| Disease not in database | "No drug candidates found for {disease}" |
| Drug not in database | "Drug '{drug}' not found in database" |
| Invalid SMILES | "Invalid SMILES notation" |
| Image generation fails | "[Image generation failed]" |
| No disease or drug specified | "No disease or molecule specified for analysis" |
