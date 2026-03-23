import { formatPercent } from "../../utils/formatters";

interface MolecularValidatorProps {
  molecule?: string;
  indication?: string;
  confidence?: number | string;
}

function MolecularValidator({ molecule, indication, confidence }: MolecularValidatorProps): JSX.Element {
  const parsedConfidence = typeof confidence === "number" ? confidence : Number(confidence);
  const confidenceLabel = Number.isFinite(parsedConfidence)
    ? formatPercent(parsedConfidence)
    : String(confidence ?? "-");

  return (
    <div className="panel">
      <h3 style={{ marginTop: 0 }}>Molecular Validator</h3>
      <p className="note">Entity extraction quality preview before decision review.</p>
      <ul className="card-list">
        <li>Molecule: <strong>{molecule ?? "-"}</strong></li>
        <li>Indication: <strong>{indication ?? "-"}</strong></li>
        <li>Master confidence: <strong>{confidenceLabel}</strong></li>
      </ul>
    </div>
  );
}

export default MolecularValidator;
