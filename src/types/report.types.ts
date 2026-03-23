export interface ArchiveRun {
  id: string;
  query?: string;
  molecule: string;
  date: string;
  timestamp?: string;
  status: string;
  opportunities: number;
  confidenceScore: number;
  report_path?: string;
}
