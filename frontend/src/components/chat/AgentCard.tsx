import { useEffect, useState } from 'react';
import { Loader2, CheckCircle2, XCircle } from 'lucide-react';

interface AgentCardProps {
  agentName: string;
  result: string;
  status: 'running' | 'done' | 'failed';
  animationDelay?: number;
}

export const AgentCard = ({ agentName, result, status, animationDelay = 0 }: AgentCardProps) => {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setMounted(true);
    }, animationDelay);
    return () => clearTimeout(timer);
  }, [animationDelay]);

  return (
    <div 
      className={`bg-white dark:bg-[#1E2130] border border-gray-200 dark:border-[#2D3148] border-l-4 border-l-[#E85D24] rounded-xl shadow-sm p-4 mb-3 transition-all duration-300 ${
        mounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2'
      }`}
    >
      <div className="flex justify-between items-center">
        <div className="text-[#E85D24] font-semibold text-sm">{agentName}</div>
        <div>
          {status === 'running' && <Loader2 className="w-4 h-4 text-[#E85D24] animate-spin" />}
          {status === 'done' && <CheckCircle2 className="w-4 h-4 text-green-500 dark:text-green-400" />}
          {status === 'failed' && <XCircle className="w-4 h-4 text-red-500" />}
        </div>
      </div>
      {(result || status === 'running') && (
        <div className="mt-2 text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
          {result || 'Processing data...'}
        </div>
      )}
    </div>
  );
};
