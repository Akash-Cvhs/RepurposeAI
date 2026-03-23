import { ArchiveRun } from "../../types/report.types";
import { formatDate } from "../../utils/formatters";
import { resolveReportUrl } from "../../utils/reportUrl";

interface ArchiveTableProps {
  runs: ArchiveRun[];
  onOpen: (run: ArchiveRun) => void;
}

function ArchiveTable({ runs, onOpen }: ArchiveTableProps): JSX.Element {
  if (!runs.length) {
    return <p className="note">No archived reports found yet.</p>;
  }

  return (
    <table className="archive-table">
      <thead>
        <tr>
          <th>Query</th>
          <th>Molecule</th>
          <th>Date</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {runs.map((run, index) => {
          const downloadUrl = resolveReportUrl(run.report_url, run.report_path);

          return (
            <tr key={run.id ?? `${run.query}-${index}`}>
              <td>{run.query}</td>
              <td>{run.molecule ?? "-"}</td>
              <td>{formatDate(run.created_at)}</td>
              <td>
                <div className="row" style={{ justifyContent: "flex-start" }}>
                  <button className="btn secondary" type="button" onClick={() => onOpen(run)}>
                    View
                  </button>
                  {downloadUrl ? (
                    <a className="btn" href={downloadUrl} download>
                      Download
                    </a>
                  ) : null}
                </div>
              </td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}

export default ArchiveTable;
