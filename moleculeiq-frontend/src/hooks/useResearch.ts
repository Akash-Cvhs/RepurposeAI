import { useCallback, useRef, useState } from "react";
import api from "../services/api";
import { AgentCardData, AgentName, ChatMessage } from "../types/agent.types";
import { RunResponse } from "../types/report.types";
import { DEFAULT_AGENT_CARDS } from "../utils/constants";

function msg(role: "user" | "assistant", content: string): ChatMessage {
  return {
    id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    role,
    content,
    createdAt: new Date().toISOString(),
  };
}

export function useResearch() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    msg(
      "assistant",
      "Ask for a molecule or therapeutic area. Upload internal PDFs if needed, then run research.",
    ),
  ]);
  const [agentCards, setAgentCards] = useState<AgentCardData[]>(DEFAULT_AGENT_CARDS);
  const [isRunning, setIsRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [latestReport, setLatestReport] = useState<RunResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const timerRef = useRef<number | null>(null);

  const clearProgressTimer = (): void => {
    if (timerRef.current !== null) {
      window.clearInterval(timerRef.current);
      timerRef.current = null;
    }
  };

  const setAgentStatus = useCallback((status: AgentCardData["status"]) => {
    setAgentCards((prev) =>
      prev.map((item) => ({
        ...item,
        status,
        latencyMs: undefined,
        errorCode: undefined,
      })),
    );
  }, []);

  const runResearch = useCallback(async (query: string, files: File[]) => {
    if (!query.trim()) {
      setError("Query required");
      return null;
    }

    setError(null);
    setIsRunning(true);
    setProgress(6);
    setAgentStatus("running");
    setMessages((prev) => [...prev, msg("user", query)]);

    timerRef.current = window.setInterval(() => {
      setProgress((p) => (p >= 85 ? p : p + 5));
    }, 400);

    try {
      const formData = new FormData();
      formData.append("query", query.trim());
      files.forEach((file) => formData.append("files", file));

      const { data } = await api.post<RunResponse>("/run", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      const errors = data.agent_errors ?? {};
      const timings = data.timing_metrics ?? {};

      setAgentCards((prev) =>
        prev.map((item) => {
          const agentError = errors[item.id as AgentName];
          const latencyRaw = timings[item.id as AgentName];
          const latencyMs = typeof latencyRaw === "number" ? latencyRaw : undefined;
          return {
            ...item,
            status: agentError ? "error" : "success",
            errorCode: agentError?.code,
            latencyMs,
          };
        }),
      );

      const assistantText = [
        data.summary,
        data.logs?.length ? `Logs captured: ${data.logs.length}` : "",
      ]
        .filter(Boolean)
        .join("\n\n");

      setMessages((prev) => [...prev, msg("assistant", assistantText)]);
      setLatestReport(data);
      setProgress(100);
      return data;
    } catch (err) {
      setAgentStatus("error");
      setError("Research request failed. Check backend and try again.");
      setMessages((prev) => [
        ...prev,
        msg("assistant", "I could not complete the run. Please retry in a few seconds."),
      ]);
      return null;
    } finally {
      clearProgressTimer();
      setIsRunning(false);
      window.setTimeout(() => setProgress(0), 800);
    }
  }, [setAgentStatus]);

  const resetSession = useCallback(() => {
    clearProgressTimer();
    setIsRunning(false);
    setProgress(0);
    setLatestReport(null);
    setError(null);
    setAgentCards(DEFAULT_AGENT_CARDS);
    setMessages([
      msg(
        "assistant",
        "Session reset. Ask for a molecule or indication to generate a fresh report.",
      ),
    ]);
  }, []);

  return {
    messages,
    agentCards,
    isRunning,
    progress,
    latestReport,
    error,
    runResearch,
    resetSession,
  };
}
