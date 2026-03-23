from rdkit import Chem
import random

#🔄Generate Random SMILES Permutations
def generate_permutations(smiles: str, count: int = 5) -> list:
    mol = Chem.MolFromSmiles(smiles)
    variants = []
    for _ in range(count):
        permuted = Chem.MolToSmiles(mol, canonical=False, doRandom=True)
        variants.append(permuted)
    return variants

#  Dummy Combinations for Testing
def generate_combinations(core: str, fragments: list) -> list:
    return [core + frag for frag in fragments if Chem.MolFromSmiles(core + frag)]

#   MSimpleutation Logic: O ➡️ N
def apply_mutation(smiles: str) -> str:
    mol = Chem.MolFromSmiles(smiles)
    for atom in mol.GetAtoms():
        if atom.GetSymbol() == "O":
            atom.SetAtomicNum(7)  # Change O to N
    return Chem.MolToSmiles(mol)