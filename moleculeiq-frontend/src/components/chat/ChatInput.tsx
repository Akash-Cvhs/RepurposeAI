import { FormEvent, useState } from "react";

interface ChatInputProps {
  onSubmit: (query: string, files: File[]) => Promise<void>;
  disabled?: boolean;
}

function ChatInput({ onSubmit, disabled = false }: ChatInputProps): JSX.Element {
  const [query, setQuery] = useState("");
  const [files, setFiles] = useState<File[]>([]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>): Promise<void> => {
    event.preventDefault();
    await onSubmit(query, files);
  };

  return (
    <form className="chat-input-wrap" onSubmit={handleSubmit}>
      <textarea
        className="text-input"
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        placeholder="Example: metformin in oncology with supporting evidence from uploaded PDFs"
        disabled={disabled}
      />

      <div className="row">
        <input
          accept="application/pdf"
          disabled={disabled}
          multiple
          onChange={(event) => setFiles(Array.from(event.target.files ?? []))}
          type="file"
        />
        <button className="btn" disabled={disabled || !query.trim()} type="submit">
          Run Research
        </button>
      </div>
    </form>
  );
}

export default ChatInput;
