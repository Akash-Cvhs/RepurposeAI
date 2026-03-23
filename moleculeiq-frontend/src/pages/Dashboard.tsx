import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import ArchiveTable from "../components/archive/ArchiveTable";
import AgentCard from "../components/chat/AgentCard";
import ChatInput from "../components/chat/ChatInput";
import ChatWindow from "../components/chat/ChatWindow";
import ProgressBar from "../components/ui/ProgressBar";
import { useReports } from "../hooks/useReports";
import { useResearch } from "../hooks/useResearch";
import { ArchiveRun } from "../types/report.types";

interface DashboardProps {
  defaultTab?: "research" | "archive";
}

function Dashboard({ defaultTab = "research" }: DashboardProps): JSX.Element {
  const navigate = useNavigate();
  const [tab, setTab] = useState<"research" | "archive">(defaultTab);
  const { runs, loading: archivesLoading, refresh } = useReports();
  const {
    messages,
    agentCards,
    isRunning,
    progress,
    latestReport,
    error,
    runResearch,
    resetSession,
  } = useResearch();

  useEffect(() => {
    setTab(defaultTab);
  }, [defaultTab]);

  const handleOpenReport = (): void => {
    if (!latestReport) {
      return;
    }

    navigate("/report/latest", { state: { report: latestReport } });
  };

  const handleOpenArchivedReport = (run: ArchiveRun): void => {
    navigate(`/report/${run.id ?? "archive"}`, { state: { archiveRun: run } });
  };

  return (
    <>
      <header className="page-header">
        <div>
          <h1 className="page-title">Research Command Center</h1>
          <p className="page-subtitle">
            Multi-agent repurposing workflow with archive and report visualization.
          </p>
        </div>
        <div className="row">
          <button className="btn secondary" type="button" onClick={() => setTab("research")}>
            Research
          </button>
          <button className="btn secondary" type="button" onClick={() => setTab("archive")}>
            Archive
          </button>
          <button className="btn secondary" type="button" onClick={resetSession}>
            Reset
          </button>
        </div>
      </header>

      {tab === "research" ? (
        <section className="dashboard-grid">
          <div className="panel">
            <h2 style={{ marginTop: 0 }}>Research Chat</h2>
            <ChatWindow messages={messages} latestReport={latestReport} onOpenReport={handleOpenReport} />
            <ChatInput
              disabled={isRunning}
              onSubmit={async (query, files) => {
                const result = await runResearch(query, files);
                if (result) {
                  await refresh();
                }
              }}
            />
            {isRunning || progress > 0 ? <ProgressBar value={progress} /> : null}
            {error ? <p className="note" style={{ color: "var(--bad)" }}>{error}</p> : null}
          </div>

          <div className="panel">
            <h2 style={{ marginTop: 0 }}>Agent Status</h2>
            <div className="agent-grid">
              {agentCards.map((agent) => (
                <AgentCard key={agent.id} agent={agent} />
              ))}
            </div>
          </div>
        </section>
      ) : (
        <section className="panel">
          <div className="row">
            <h2 style={{ marginTop: 0 }}>Report Archive</h2>
            <button className="btn secondary" onClick={() => void refresh()} type="button">
              Refresh
            </button>
          </div>
          {archivesLoading ? <p className="note">Loading archives...</p> : null}
          <ArchiveTable runs={runs} onOpen={handleOpenArchivedReport} />
        </section>
      )}
    </>
  );
}

export default Dashboard;
