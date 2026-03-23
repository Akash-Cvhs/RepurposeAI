export interface ArchiveRun {
  id?: string;
  query: string;
  molecule?: string;
  indication?: string;
  created_at?: string;
  report_path: string;
  report_url?: string;
}

export interface AgentErrorItem {
  code: string;
  message: string;
}

export interface RunResponse {
  request_id?: string;
  summary: string;
  report_path: string;
  report_url?: string;
  logs: string[];
  trials?: Record<string, unknown>[];
  patents?: Record<string, unknown>[];
  fto_risk?: string;
  query_plan?: Record<string, unknown>[];
  master_confidence?: string | number;
  agent_errors?: Record<string, AgentErrorItem>;
  timing_metrics?: Record<string, unknown>;
}

export interface ArchivesResponse {
  runs: ArchiveRun[];
}
