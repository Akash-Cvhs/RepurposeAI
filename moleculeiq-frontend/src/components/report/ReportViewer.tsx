interface ReportViewerProps {
  reportUrl?: string;
  reportPath?: string;
}

function ReportViewer({ reportUrl, reportPath }: ReportViewerProps): JSX.Element {
  if (!reportUrl && !reportPath) {
    return <p className="note">No report selected.</p>;
  }

  if (!reportUrl) {
    return (
      <div className="panel">
        <h3 style={{ marginTop: 0 }}>PDF Path</h3>
        <p className="mono">{reportPath ?? "-"}</p>
        <p className="note">
          The report file is not available through a direct URL yet.
        </p>
      </div>
    );
  }

  return (
    <div className="panel">
      <div className="row" style={{ marginBottom: 10 }}>
        <h3 style={{ margin: 0 }}>Report Preview</h3>
        <div className="row">
          <a className="btn secondary" href={reportUrl} target="_blank" rel="noreferrer">
            Open in new tab
          </a>
          <a className="btn" href={reportUrl} download>
            Download PDF
          </a>
        </div>
      </div>
      <iframe title="report-viewer" src={reportUrl} style={{ width: "100%", height: 640, border: "1px solid var(--line)", borderRadius: 8 }} />
    </div>
  );
}

export default ReportViewer;
