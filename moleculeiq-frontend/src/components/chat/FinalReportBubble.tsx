import { RunResponse } from "../../types/report.types";
import { resolveReportUrl } from "../../utils/reportUrl";

interface FinalReportBubbleProps {
  report: RunResponse;
  onOpenReport: () => void;
}

function FinalReportBubble({ report, onOpenReport }: FinalReportBubbleProps): JSX.Element {
  const downloadUrl = resolveReportUrl(report.report_url, report.report_path);

  return (
    <section className="report-bubble">
      <h3 style={{ margin: "0 0 8px" }}>Final Report Ready</h3>
      <p className="note" style={{ marginBottom: 10 }}>
        {report.summary}
      </p>
      <button className="btn" onClick={onOpenReport} type="button">
        Open Report Viewer
      </button>
      {downloadUrl ? (
        <a className="btn secondary" href={downloadUrl} download style={{ marginLeft: 8 }}>
          Download PDF
        </a>
      ) : null}
    </section>
  );
}

export default FinalReportBubble;
