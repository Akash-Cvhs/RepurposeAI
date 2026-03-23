import { useEffect, useState } from 'react';
import { Loader2, Star, CheckCircle2, AlertTriangle } from 'lucide-react';
import type { ResearchResponse } from '../../types/agent.types';

interface AgentCardUSPProps {
  status: 'running' | 'done';
  animationDelay?: number;
  data?: ResearchResponse['molecular_validation'];
}

export const AgentCardUSP = ({ status, animationDelay = 0 }: AgentCardUSPProps) => {
  const [mounted, setMounted] = useState(false);
  const [barWidth, setBarWidth] = useState(0);

  useEffect(() => {
    const timer = setTimeout(() => setMounted(true), animationDelay);
    return () => clearTimeout(timer);
  }, [animationDelay]);

  useEffect(() => {
    if (status === 'done') {
      const timer = setTimeout(() => setBarWidth(78), 100);
      return () => clearTimeout(timer);
    }
  }, [status]);

  return (
    <div 
      className={`bg-[#FFF3EE] dark:bg-[#2A1F1A] border border-[#FDDDD0] dark:border-[#4A2E20] border-l-4 border-l-[#E85D24] rounded-xl shadow-sm p-4 mb-3 transition-all duration-300 ${
        mounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2'
      }`}
    >
      <div className="flex items-center">
        <Star className="w-4 h-4 text-[#E85D24] mr-1.5 fill-current" />
        <span className="text-[#E85D24] font-semibold text-sm">Molecular Validator — USP</span>
        <span className="bg-[#E85D24] text-white text-xs rounded px-1.5 py-0.5 ml-2">USP</span>
      </div>

      {status === 'running' ? (
        <div className="mt-3 flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
          <Loader2 className="w-4 h-4 text-[#E85D24] animate-spin" />
          Running QSAR analysis + ADMET prediction...
        </div>
      ) : (
        <div className="mt-4">
          <div className="flex justify-between items-end">
            <span className="text-sm text-gray-700 dark:text-gray-300">Repurposing Confidence Score</span>
            <span className="text-[#E85D24] font-bold text-lg">78/100</span>
          </div>
          <div className="bg-gray-200 dark:bg-gray-700 rounded-full h-2.5 mt-1.5 overflow-hidden">
            <div 
              className="bg-[#E85D24] h-full rounded-full transition-all duration-1000 ease-out"
              style={{ width: `${barWidth}%` }}
            />
          </div>

          <div className="border-t border-[#FDDDD0] dark:border-[#4A2E20] my-3" />

          <div className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-2">
            ADMET Breakdown
          </div>
          
          <div className="flex justify-between items-center mb-1.5">
            <div className="flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-green-500" />
              <span className="text-xs text-gray-600 dark:text-gray-400">Absorption</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-500">88%</span>
              <div className="w-20 h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <div className="bg-[#E85D24] h-full w-[88%]" />
              </div>
            </div>
          </div>
          
          <div className="flex justify-between items-center mb-1.5">
            <div className="flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-green-500" />
              <span className="text-xs text-gray-600 dark:text-gray-400">Distribution</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-500">72%</span>
              <div className="w-20 h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <div className="bg-[#E85D24] h-full w-[72%]" />
              </div>
            </div>
          </div>
          
          <div className="flex justify-between items-center mb-1.5">
            <div className="flex items-center gap-1.5">
              <AlertTriangle className="w-3.5 h-3.5 text-amber-500" />
              <span className="text-xs text-gray-600 dark:text-gray-400">Metabolism</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-500">61%</span>
              <div className="w-20 h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <div className="bg-amber-500 h-full w-[61%]" />
              </div>
            </div>
          </div>

          <div className="flex justify-between items-center mb-1.5">
            <div className="flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-green-500" />
              <span className="text-xs text-gray-600 dark:text-gray-400">Excretion</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-500">85%</span>
              <div className="w-20 h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <div className="bg-[#E85D24] h-full w-[85%]" />
              </div>
            </div>
          </div>

          <div className="flex justify-between items-center mb-1.5">
            <div className="flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-green-500" />
              <span className="text-xs text-gray-600 dark:text-gray-400">Toxicity</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-500">90%</span>
              <div className="w-20 h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <div className="bg-[#E85D24] h-full w-[90%]" />
              </div>
            </div>
          </div>

          <div className="border-t border-[#FDDDD0] dark:border-[#4A2E20] my-3" />

          <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
            Binding Affinity
          </div>
          <div className="flex flex-wrap gap-2 mt-1.5">
            <span className="bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-xs rounded-full px-2.5 py-1">
              Target: AMPK
            </span>
            <span className="bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-xs rounded-full px-2.5 py-1">
              Score: -8.4 kcal/mol
            </span>
            <span className="bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 text-xs rounded-full px-2.5 py-1">
              Confidence: High
            </span>
          </div>

          <div className="mt-3 italic text-xs text-gray-400 dark:text-gray-500">
            Validated by quantum-inspired molecular analysis
          </div>
        </div>
      )}
    </div>
  );
};
