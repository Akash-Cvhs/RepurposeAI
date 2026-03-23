import { AgentStatus } from "../../types/agent.types";

interface BadgeProps {
  status: AgentStatus;
  label?: string;
}

function Badge({ status, label }: BadgeProps): JSX.Element {
  return <span className={`badge ${status}`}>{label ?? status.toUpperCase()}</span>;
}

export default Badge;
