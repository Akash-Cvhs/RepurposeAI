import { useEffect, useMemo, useState } from "react";
import { useLocation, useParams } from "react-router-dom";
import ClinicalTimeline from "../components/report/ClinicalTimeline";
import MolecularValidator from "../components/report/MolecularValidator";
import PatentTable from "../components/report/PatentTable";
import ReportViewer from "../components/report/ReportViewer";
import api from "../services/api";
import { ArchiveRun, RunResponse } from "../types/report.types";
import { resolveReportPreviewUrl } from "../utils/reportUrl";

interface ReportLocationState {
  report?: RunResponse;
  archiveRun?: ArchiveRun;
}

function ReportPage(): JSX.Element {
  const params = useParams<{ reportId?: string }>();
  const location = useLocation();
  const state = (location.state as ReportLocationState | null) ?? null;
  const [resolvedArchiveRun, setResolvedArchiveRun] = useState<ArchiveRun | null>(null);
  const [archiveLookupError, setArchiveLookupError] = useState<string | null>(null);

  const report = state?.report;
  const archivedRunFromState = state?.archiveRun;

  useEffect(() => {
    if (report || archivedRunFromState) {
      setResolvedArchiveRun(archivedRunFromState ?? null);
      setArchiveLookupError(null);
      return;
    }

    let cancelled = false;
    const loadFromArchive = async (): Promise<void> => {
      try {
        const { data } = await api.get<{ runs?: ArchiveRun[] }>("/archives");
        const runs = data.runs ?? [];
        if (!runs.length) {
          if (!cancelled) {
            setResolvedArchiveRun(null);
            setArchiveLookupError("No archived reports found.");
          }
          return;
        }

        const reportId = params.reportId;
        const picked = !reportId || reportId === "latest"
          ? runs[runs.length - 1]
          : runs.find((run) => run.id === reportId) ?? null;

        if (!cancelled) {
          setResolvedArchiveRun(picked);
          setArchiveLookupError(picked ? null : "Report not found in archive.");
        }
      } catch (error) {
        if (!cancelled) {
          setResolvedArchiveRun(null);
          setArchiveLookupError("Could not load archive metadata.");
        }
      }
    };

    void loadFromArchive();
    return () => {
      cancelled = true;
    };
  }, [archivedRunFromState, params.reportId, report]);

  const archivedRun = archivedRunFromState ?? resolvedArchiveRun;
  const rawReportPath = report?.report_path ?? archivedRun?.report_path;
  const reportUrl = useMemo(
    () => resolveReportPreviewUrl(report?.report_url ?? archivedRun?.report_url, rawReportPath),
    [archivedRun?.report_url, rawReportPath, report?.report_url],
  );

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

      {archiveLookupError && !report && !archivedRunFromState ? (
        <p className="note" style={{ color: "var(--bad)" }}>{archiveLookupError}</p>
      ) : null}

      <ReportViewer reportUrl={reportUrl ?? undefined} reportPath={rawReportPath} />

      <MolecularValidator
        confidence={report?.master_confidence}
        indication={report?.indication ?? archivedRun?.indication}
        molecule={report?.molecule ?? archivedRun?.molecule}
      />

      <ClinicalTimeline trials={report?.trials ?? []} />
      <PatentTable patents={report?.patents ?? []} />
    </div>
  );
}

export default ReportPage;
