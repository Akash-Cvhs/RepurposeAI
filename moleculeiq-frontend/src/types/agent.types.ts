export type AgentStatus = "idle" | "running" | "success" | "error";

export type AgentName =
  | "master"
  | "clinical_trials"
  | "patent_landscape"
  | "internal_insights"
  | "web_intel"
  | "report_generator";

export interface AgentCardData {
  id: AgentName;
  title: string;
  description: string;
  usp: string;
  status: AgentStatus;
  latencyMs?: number;
  errorCode?: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  createdAt: string;
}
