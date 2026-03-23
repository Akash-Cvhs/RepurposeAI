import streamlit as st
import pandas as pd
import random
from rdkit import Chem
from mordred import Calculator, descriptors

# Sample genes and RNA/DNA structures
genes = ['GENE_A1', 'GENE_B2', 'GENE_C3', 'GENE_X1', 'GENE_Z9', 'AKASH']
structures = ['Human mRNA-202','ALPHA223', 'Human tRNA-α', 'Human DNA-PROMOTER-GCX', 'Human miRNA-β']

# QSAR descriptor keys
QSAR_KEYS = ["MolWt", "LogP", "NumHAcceptors", "NumHDonors", "TPSA"]

def simulate_compatibility(gene, structure):
    score = round(random.uniform(0.1, 1.0), 2)
    verdict = "High Merge Potential" if score > 0.7 else "Low Merge Potential"
    return score, verdict

def check_qsar_properties(smiles: str) -> dict:
    mol = Chem.MolFromSmiles(smiles)
    if not mol:
        return {"error": "Invalid SMILES"}
    try:
        calc = Calculator(descriptors, ignore_3D=True)
        desc = dict(calc(mol))
        filtered = {k: round(desc.get(k, 0), 2) for k in QSAR_KEYS}
        return filtered
    except Exception as e:
        return {"error": f"QSAR calculation failed: {str(e)}"}

# UI starts here
st.title("🧬 Gene-RNA/DNA Simulator + QSAR Property Checker")

st.write("Simulate genetic compatibility + analyze molecular descriptors using RDKit & Mordred.")

selected_gene = st.selectbox("🔬 Choose a Gene", genes)
selected_structure = st.selectbox("🧪 Choose a Human Structure", structures)
smiles = st.text_input("🔹 Enter SMILES string for QSAR check")

if st.button("🔍 Analyze Merge + QSAR"):
    score, verdict = simulate_compatibility(selected_gene, selected_structure)
    st.metric(label="Compatibility Score", value=score)
    st.success(f"Verdict: {verdict}")

    if smiles:
        qsar = check_qsar_properties(smiles)
        if "error" in qsar:
            st.error(qsar["error"])
        else:
            st.subheader("📊 QSAR Property Summary")
            for prop, val in qsar.items():
                tamil_map = {
                    "MolWt": "அணுக்கடை எடை",
                    "LogP": "இயக்க திறன் (LogP)",
                    "NumHAcceptors": "ஹைட்ரஜன் ஏற்கும் பொருள்கள்",
                    "NumHDonors": "ஹைட்ரஜன் அளிக்கும் பொருள்கள்",
                    "TPSA": "தொலைதூர பொது மேற்பரப்பு"
                }
                label = f"{prop} ({tamil_map.get(prop, '')})"
                st.write(f"🔹 {label}: `{val}`")

# Optional table of merge simulations
st.subheader("📋 Full Gene-Structure Simulation")
results = [
    {
        "Gene": gene,
        "Structure": structure,
        "Score": simulate_compatibility(gene, structure)[0],
        "Verdict": simulate_compatibility(gene, structure)[1]
    }
    for gene in genes for structure in structures
]
df = pd.DataFrame(results)
st.dataframe(df)