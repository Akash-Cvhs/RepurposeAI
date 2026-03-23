import { ChevronLeft, Share2, Download } from 'lucide-react';
import AppLogo from '../ui/AppLogo';
import { useNavigate } from 'react-router-dom';

interface ReportHeaderProps {
  molecule: string;
  date: string;
  score: number;
  opportunities: number;
}

export const ReportHeader = ({ molecule, score, opportunities }: ReportHeaderProps) => {
  const navigate = useNavigate();

  return (
    <div className="sticky top-0 z-50 bg-white dark:bg-[#1A1D27] border-b border-gray-200 dark:border-[#2D3148] px-8 py-4 flex justify-between items-center shadow-sm">
      <div className="flex items-center gap-3">
        <button 
          onClick={() => navigate(-1)}
          className="text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-100 p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        >
          <ChevronLeft className="w-5 h-5" />
        </button>
        <div className="w-px h-6 bg-gray-200 dark:bg-[#2D3148]" />
        <div className="flex items-center gap-1.5">
          <AppLogo size="sm" showText={true} />
        </div>
      </div>

      <div className="flex flex-col md:flex-row items-center gap-1 mt-2 md:mt-0">
        <div className="font-bold text-gray-900 dark:text-gray-100 text-base md:text-lg uppercase tracking-wide">
          {molecule}
        </div>
        <div className="text-xs text-gray-400 dark:text-gray-500 text-center">
          <span className="hidden md:inline">· </span>Innovation Product Story
        </div>
      </div>

      <div className="flex items-center gap-2 md:gap-3 mt-3 sm:mt-0 w-full sm:w-auto">
        <div className="hidden sm:block bg-[#FFF3EE] dark:bg-[#2A1F1A] text-[#E85D24] font-bold text-sm rounded-full px-3 py-1.5 border border-[#FDDDD0] dark:border-[#4A2E20]">
          {score}/100 Confidence
        </div>
        <div className="hidden md:block bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400 text-sm rounded-full px-3 py-1.5 font-medium">
          {opportunities} Opportunities
        </div>
        <button className="hidden md:flex border border-gray-200 dark:border-[#2D3148] text-gray-600 dark:text-gray-400 rounded-lg px-3 py-2 text-sm hover:bg-gray-50 dark:hover:bg-gray-800 items-center gap-2 transition-colors">
          <Share2 className="w-4 h-4" />
          Share
        </button>
        <button className="w-full sm:w-auto justify-center bg-[#E85D24] hover:bg-[#C94D1A] text-white rounded-lg px-4 py-2 text-sm font-medium flex items-center gap-2 transition-colors">
          <Download className="w-4 h-4" />
          Download PDF
        </button>
      </div>
    </div>
  );
};
