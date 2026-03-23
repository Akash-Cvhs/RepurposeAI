import { AgentCardData } from "../types/agent.types";

export const APP_TITLE = "MoleculeIQ";

export const DEFAULT_AGENT_CARDS: AgentCardData[] = [
  {
    id: "master",
    title: "Master Orchestrator",
    description: "Parses query intent, molecule and indication before orchestration.",
    usp: "Intent-first routing for cleaner downstream signals",
    status: "idle",
  },
  {
    id: "clinical_trials",
    title: "Clinical Trials Agent",
    description: "Builds trial landscape and timeline from mock/live connectors.",
    usp: "Trial density and recency surfaced quickly",
    status: "idle",
  },
  {
    id: "patent_landscape",
    title: "Patent/FTO Agent",
    description: "Highlights patent coverage and computes FTO risk level.",
    usp: "Risk labels that are report-ready for decision support",
    status: "idle",
  },
  {
    id: "internal_insights",
    title: "Internal Insights Agent",
    description: "Extracts evidence from uploaded PDFs and summarizes key notes.",
    usp: "Your private documents influence the narrative directly",
    status: "idle",
  },
  {
    id: "web_intel",
    title: "Web Intelligence Agent",
    description: "Collects guideline and market context from configured data source.",
    usp: "Latest external context blended with internal findings",
    status: "idle",
  },
  {
    id: "report_generator",
    title: "Report Generator",
    description: "Composes innovation story and exports a final PDF report.",
    usp: "Decision-ready artifact generated in one pass",
    status: "idle",
  },
];
