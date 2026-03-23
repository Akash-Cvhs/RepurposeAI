import { Download, Eye } from 'lucide-react';

interface FinalReportBubbleProps {
  onView?: () => void;
  onDownload?: () => void;
}

export const FinalReportBubble = ({ onView, onDownload }: FinalReportBubbleProps) => {
  return (
    <div className="bg-white dark:bg-[#1E2130] border border-gray-200 dark:border-[#2D3148] rounded-xl overflow-hidden shadow-sm animate-in fade-in slide-in-from-bottom-2">
      <div className="bg-[#FFF3EE] dark:bg-[#2A1F1A] border-b border-[#FDDDD0] dark:border-[#4A2E20] px-4 py-3 pb-0">
        <div className="flex justify-between items-start">
          <div className="flex gap-2">
            <span className="text-xl">🏆</span>
            <div>
              <div className="font-semibold text-gray-900 dark:text-gray-100">Innovation Product Story Complete</div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-0.5">Your comprehensive analysis is ready.</p>
            </div>
          </div>
        </div>
      </div>
      <div className="p-4 flex gap-3">
        <button 
          onClick={onView}
          className="flex-1 bg-white dark:bg-[#1A1D27] border border-gray-200 dark:border-[#2D3148] hover:bg-gray-50 dark:hover:bg-[#252840] text-gray-700 dark:text-gray-300 rounded-lg py-2 text-sm font-medium transition-colors flex justify-center items-center gap-2"
        >
          <Eye className="w-4 h-4" />
          View Report
        </button>
        <button 
          onClick={onDownload}
          className="flex-1 bg-[#E85D24] text-white hover:bg-[#C94D1A] rounded-lg py-2 text-sm font-medium transition-colors flex justify-center items-center gap-2 shadow-sm"
        >
          <Download className="w-4 h-4" />
          Download PDF
        </button>
      </div>
    </div>
  );
};
