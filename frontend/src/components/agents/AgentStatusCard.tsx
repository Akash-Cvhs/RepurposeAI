import { type LucideIcon, Clock, Activity } from 'lucide-react';

interface AgentStatusCardProps {
  name: string;
  icon: LucideIcon;
  role: string;
  status: 'active' | 'idle' | 'processing';
  lastRun: string;
  queriesProcessed: number;
  isUSP?: boolean;
}

export const AgentStatusCard = ({
  name,
  icon: Icon,
  role,
  status,
  lastRun,
  queriesProcessed,
  isUSP = false
}: AgentStatusCardProps) => {
  return (
    <div className={`border rounded-xl p-5 shadow-sm transition-all hover:shadow-md ${
      isUSP 
        ? 'bg-[#FFF3EE] dark:bg-[#2A1F1A] border-[#E85D24] dark:border-[#E85D24]' 
        : 'bg-white dark:bg-[#1E2130] border-gray-200 dark:border-[#2D3148]'
    }`}>
      <div className="flex justify-between items-start">
        <div className="flex items-center gap-3">
          <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
            isUSP ? 'bg-[#E85D24]/10' : 'bg-gray-100 dark:bg-gray-800'
          }`}>
            <Icon className={`w-5 h-5 ${
              isUSP ? 'text-[#E85D24]' : 'text-gray-600 dark:text-gray-400'
            }`} />
          </div>
          <div className="font-semibold text-gray-900 dark:text-gray-100 text-sm">
            {name}
          </div>
        </div>
        
        <div className="flex items-center">
          {isUSP && (
            <span className="bg-[#FFF3EE] text-[#E85D24] dark:bg-[#2A1F1A] dark:text-[#E85D24] text-xs font-medium rounded-full px-2.5 py-1 mr-2">
              ⭐ USP
            </span>
          )}
          <div className="flex items-center gap-1.5">
            <div className={`w-2 h-2 rounded-full ${
              status === 'active' ? 'bg-green-500 animate-pulse' :
              status === 'processing' ? 'bg-amber-500 animate-pulse' :
              'bg-gray-400'
            }`} />
            <span className={`text-xs ${
              status === 'active' ? 'text-green-600 dark:text-green-400' :
              status === 'processing' ? 'text-amber-600' :
              'text-gray-400'
            }`}>
              {status}
            </span>
          </div>
        </div>
      </div>
      
      <div className="mt-2 text-xs text-gray-500 dark:text-gray-400 leading-relaxed">
        {role}
      </div>
      
      <div className="border-t border-gray-100 dark:border-[#2D3148] my-3" />
      
      <div className="flex justify-between items-center">
        <div className="text-xs text-gray-400 dark:text-gray-500 flex items-center">
          <Clock className="w-3.5 h-3.5 text-gray-400 inline mr-1" />
          Last run: {lastRun}
        </div>
        <div className="text-xs text-gray-400 dark:text-gray-500 flex items-center">
          <Activity className="w-3.5 h-3.5 text-gray-400 inline mr-1" />
          {queriesProcessed} queries
        </div>
      </div>
    </div>
  );
};
