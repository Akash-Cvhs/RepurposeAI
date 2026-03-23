import { AgentCardData } from "../../types/agent.types";
import Badge from "../ui/Badge";
import Spinner from "../ui/Spinner";
import AgentCardUSP from "./AgentCardUSP";

interface AgentCardProps {
  agent: AgentCardData;
}

function AgentCard({ agent }: AgentCardProps): JSX.Element {
  return (
    <article className="agent-card">
      <div className="agent-top">
        <strong>{agent.title}</strong>
        <div style={{ display: "inline-flex", alignItems: "center", gap: 8 }}>
          {agent.status === "running" ? <Spinner /> : null}
          <Badge status={agent.status} />
        </div>
      </div>
      <p className="note">{agent.description}</p>
      <AgentCardUSP usp={agent.usp} />
      {agent.latencyMs !== undefined ? (
        <p className="note mono">Latency: {Math.round(agent.latencyMs)} ms</p>
      ) : null}
      {agent.errorCode ? <p className="note mono">Error: {agent.errorCode}</p> : null}
    </article>
  );
}

export default AgentCard;
