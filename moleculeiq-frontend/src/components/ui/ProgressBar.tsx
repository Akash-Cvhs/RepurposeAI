interface ProgressBarProps {
  value: number;
}

function ProgressBar({ value }: ProgressBarProps): JSX.Element {
  return (
    <div className="progress-shell" aria-label="Research progress" role="progressbar">
      <div className="progress-fill" style={{ width: `${Math.max(0, Math.min(100, value))}%` }} />
    </div>
  );
}

export default ProgressBar;
