import { useLocation, useParams } from "react-router-dom";
import ClinicalTimeline from "../components/report/ClinicalTimeline";
import MolecularValidator from "../components/report/MolecularValidator";
import PatentTable from "../components/report/PatentTable";
import ReportViewer from "../components/report/ReportViewer";
import { ArchiveRun, RunResponse } from "../types/report.types";
import { resolveReportUrl } from "../utils/reportUrl";

interface ReportLocationState {
  report?: RunResponse;
  archiveRun?: ArchiveRun;
}

function ReportPage(): JSX.Element {
  const params = useParams<{ reportId?: string }>();
  const location = useLocation();
  const state = (location.state as ReportLocationState | null) ?? null;

  const report = state?.report;
  const archivedRun = state?.archiveRun;
  const rawReportPath = report?.report_path ?? archivedRun?.report_path;
  const reportUrl = resolveReportUrl(report?.report_url ?? archivedRun?.report_url, rawReportPath);

  return (
    <div className="report-grid">
      <header className="page-header">
        <div>
          <h1 className="page-title">Report Viewer</h1>
          <p className="page-subtitle">
            Report ID: <span className="mono">{params.reportId ?? "latest"}</span>
          </p>
        </div>
      </header>

      <ReportViewer reportUrl={reportUrl ?? undefined} reportPath={rawReportPath} />

      <MolecularValidator
        confidence={report?.master_confidence}
        indication={archivedRun?.indication}
        molecule={archivedRun?.molecule}
      />

      <ClinicalTimeline trials={report?.trials ?? []} />
      <PatentTable patents={report?.patents ?? []} />
    </div>
  );
}

export default ReportPage;
