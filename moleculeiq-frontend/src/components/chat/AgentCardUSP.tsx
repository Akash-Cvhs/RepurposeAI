interface AgentCardUSPProps {
  usp: string;
}

function AgentCardUSP({ usp }: AgentCardUSPProps): JSX.Element {
  return <p className="note"><strong>USP:</strong> {usp}</p>;
}

export default AgentCardUSP;
