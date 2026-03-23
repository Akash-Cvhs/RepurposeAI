function valueAsString(value: unknown): string {
  if (value === null || value === undefined) {
    return "-";
  }

  if (typeof value === "string" || typeof value === "number") {
    return String(value);
  }

  return JSON.stringify(value);
}

interface PatentTableProps {
  patents: Record<string, unknown>[];
}

function PatentTable({ patents }: PatentTableProps): JSX.Element {
  if (!patents.length) {
    return <p className="note">No patent rows available in this response.</p>;
  }

  return (
    <div className="panel">
      <h3 style={{ marginTop: 0 }}>Patent Landscape</h3>
      <table className="archive-table">
        <thead>
          <tr>
            <th>Title</th>
            <th>Assignee</th>
            <th>Expiry</th>
          </tr>
        </thead>
        <tbody>
          {patents.slice(0, 12).map((item, index) => (
            <tr key={`${valueAsString(item.patent_id)}-${index}`}>
              <td>{valueAsString(item.title)}</td>
              <td>{valueAsString(item.assignee)}</td>
              <td>{valueAsString(item.expiry_date)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default PatentTable;
