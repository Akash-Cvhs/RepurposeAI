interface ClinicalTimelineProps {
  trials: Record<string, unknown>[];
}

function text(value: unknown): string {
  if (typeof value === "string") {
    return value;
  }

  if (typeof value === "number") {
    return String(value);
  }

  return "-";
}

function ClinicalTimeline({ trials }: ClinicalTimelineProps): JSX.Element {
  if (!trials.length) {
    return <p className="note">No clinical trial data available in this report.</p>;
  }

  const rows = [...trials].sort((a, b) => text(a.start_date).localeCompare(text(b.start_date)));

  return (
    <div className="panel">
      <h3 style={{ marginTop: 0 }}>Clinical Timeline</h3>
      <ul className="card-list">
        {rows.slice(0, 15).map((trial, index) => (
          <li key={`${text(trial.nct_id)}-${index}`}>
            <strong>{text(trial.phase)}</strong> | {text(trial.start_date)} | {text(trial.status)}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default ClinicalTimeline;
