import { useState, useRef } from 'react';
import { Send, Paperclip, X } from 'lucide-react';
import { Spinner } from '../ui/Spinner';

interface ChatInputProps {
  onSend: (query: string, molecule: string, file: File | null) => void;
  isLoading?: boolean;
}

export const ChatInput = ({ onSend, isLoading }: ChatInputProps) => {
  const [query, setQuery] = useState('');
  const [molecule, setMolecule] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) {
      setFile(selected);
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSend = () => {
    if ((query.trim() || file) && !isLoading) {
      onSend(query, molecule, file);
      setQuery('');
      setMolecule('');
      setFile(null);
    }
  };

  return (
    <div className="bg-white dark:bg-[#1A1D27] border-t border-gray-200 dark:border-[#2D3148] p-4 flex flex-col items-center">
      <div className="max-w-4xl w-full">
        {file && (
          <div className="flex items-center gap-2 mb-3 bg-[#FFF3EE] dark:bg-[#2A1F1A] border border-[#FDDDD0] dark:border-[#4A2E20] text-[#E85D24] w-fit px-3 py-1.5 rounded-lg text-sm transition-all duration-300 animate-in fade-in slide-in-from-bottom-2">
            <Paperclip className="w-4 h-4" />
            <span className="truncate max-w-[200px]">{file.name}</span>
            <button
              onClick={() => setFile(null)}
              className="ml-1 hover:bg-[#E85D24]/10 p-1 rounded-full transition-colors"
            >
              <X className="w-3 h-3" />
            </button>
          </div>
        )}
        
        <div className="flex items-end gap-3 w-full bg-white dark:bg-[#1E2130] border border-gray-200 dark:border-[#2D3148] rounded-xl p-2 shadow-sm focus-within:ring-2 focus-within:ring-[#E85D24]/20 focus-within:border-[#E85D24] transition-all duration-300">
          <button
            onClick={() => fileInputRef.current?.click()}
            className="p-3 text-gray-400 hover:text-[#E85D24] hover:bg-[#FFF3EE] dark:hover:bg-[#2A1F1A] rounded-lg transition-colors flex-shrink-0"
          >
            <Paperclip className="w-5 h-5" />
          </button>
          <input
            type="file"
            ref={fileInputRef}
            className="hidden"
            onChange={handleFileChange}
            accept=".pdf,.doc,.docx,.txt"
          />

          <div className="flex-1 flex flex-col relative w-full">
            {(molecule || query) && (
              <div className="absolute -top-7 left-0 text-xs font-semibold text-[#E85D24] tracking-wide uppercase px-1 transition-all animate-in fade-in">
                {molecule ? `TARGET: ${molecule}` : 'RESEARCH PROMPT'}
              </div>
            )}
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Design an Innovation Product Story mapping repurposing opportunities for..."
              className="w-full bg-transparent text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 text-sm resize-none focus:outline-none py-3 px-2 min-h-[44px] max-h-[120px]"
              rows={1}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
            />
          </div>

          <button
            onClick={handleSend}
            disabled={(!query.trim() && !file) || isLoading}
            className={`p-3 rounded-lg flex-shrink-0 transition-all duration-300 ${
              (query.trim() || file) && !isLoading
                ? 'bg-[#E85D24] text-white hover:bg-[#C94D1A] shadow-sm'
                : 'bg-gray-100 text-gray-400 dark:bg-gray-800 dark:text-gray-600 cursor-not-allowed'
            }`}
          >
            {isLoading ? <Spinner className="w-5 h-5 border-t-white" /> : <Send className="w-5 h-5" />}
          </button>
        </div>
      </div>
      <div className="text-xs text-gray-400 dark:text-gray-600 text-center mt-2">
        Press Enter to send &middot; Shift+Enter for new line &middot; Attach PDF for internal analysis
      </div>
    </div>
  );
};
