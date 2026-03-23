import { ChatMessage } from "../../types/agent.types";
import { RunResponse } from "../../types/report.types";
import { formatDate } from "../../utils/formatters";
import FinalReportBubble from "./FinalReportBubble";

interface ChatWindowProps {
  messages: ChatMessage[];
  latestReport: RunResponse | null;
  onOpenReport: () => void;
}

function ChatWindow({ messages, latestReport, onOpenReport }: ChatWindowProps): JSX.Element {
  return (
    <div className="chat-window">
      {messages.map((message) => (
        <article key={message.id} className={`chat-bubble ${message.role}`}>
          <div>{message.content}</div>
          <div className="chat-time">{formatDate(message.createdAt)}</div>
        </article>
      ))}

      {latestReport ? <FinalReportBubble report={latestReport} onOpenReport={onOpenReport} /> : null}
    </div>
  );
}

export default ChatWindow;
