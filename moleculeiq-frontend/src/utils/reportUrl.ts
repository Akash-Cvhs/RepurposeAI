const API_BASE = (import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");

export function resolveReportUrl(reportUrl?: string, reportPath?: string): string | null {
  if (reportUrl) {
    if (/^https?:\/\//i.test(reportUrl)) {
      return reportUrl;
    }
    if (reportUrl.startsWith("/")) {
      return `${API_BASE}${reportUrl}`;
    }
    return `${API_BASE}/${reportUrl}`;
  }

  if (!reportPath) {
    return null;
  }

  const fileName = reportPath.split(/[/\\]/).pop();
  if (!fileName) {
    return null;
  }

  return `${API_BASE}/reports/${encodeURIComponent(fileName)}`;
}
