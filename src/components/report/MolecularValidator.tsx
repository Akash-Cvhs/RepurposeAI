import { Star, CheckCircle2, AlertTriangle, Info } from 'lucide-react';
import { CircularProgress } from '../ui/CircularProgress';
import { ProgressBar } from '../ui/ProgressBar';

interface MolecularValidatorProps {
  score: number;
  admet: {
    absorption: number;
    distribution: number;
    metabolism: number;
    excretion: number;
    toxicity: number;
  };
  targetProtein: string;
  bindingAffinity: string;
}

export const MolecularValidator = ({ score, admet, targetProtein, bindingAffinity }: MolecularValidatorProps) => {
  return (
    <div className="border-l-4 border-[#E85D24] pl-6">
      <div className="flex items-center gap-2 mb-6">
        <Star className="w-5 h-5 text-[#E85D24] fill-current" />
        <div className="text-xl font-bold text-gray-900 dark:text-gray-100">Molecular Validation</div>
        <span className="bg-[#FFF3EE] text-[#E85D24] dark:bg-[#2A1F1A] dark:text-[#E85D24] text-xs font-medium rounded-full px-2.5 py-1">USP</span>
        <div className="text-sm text-gray-500 dark:text-gray-400 ml-2">Powered by Quantum-Inspired Analysis</div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* LEFT COLUMN */}
        <div>
          <div className="flex flex-col items-center">
            <CircularProgress value={score} size={160} strokeWidth={12} />
            <div className="text-sm text-gray-500 mt-3">Repurposing Confidence</div>
            <div className="text-xs text-gray-400">Score</div>
          </div>

          <div className="bg-[#FFF3EE] dark:bg-[#2A1F1A] border border-[#FDDDD0] dark:border-[#4A2E20] rounded-xl p-4 mt-6">
            <div className="flex justify-between text-sm py-1.5 border-b border-[#FDDDD0] dark:border-[#4A2E20]">
              <span className="text-gray-600 dark:text-gray-400">Target Protein</span>
              <span className="font-semibold text-gray-900 dark:text-gray-100">{targetProtein}</span>
            </div>
            <div className="flex justify-between text-sm py-1.5 border-b border-[#FDDDD0] dark:border-[#4A2E20]">
              <span className="text-gray-600 dark:text-gray-400">Binding Affinity</span>
              <span className="font-semibold text-gray-900 dark:text-gray-100">{bindingAffinity}</span>
            </div>
            <div className="flex justify-between text-sm py-1.5">
              <span className="text-gray-600 dark:text-gray-400">Confidence</span>
              <span className="bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400 text-xs font-medium rounded-full px-2 py-0.5">High</span>
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN */}
        <div>
          <div className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4 uppercase tracking-wide">
            ADMET Breakdown
          </div>

          {[
            { key: 'absorption', label: 'Absorption', value: admet.absorption, icon: CheckCircle2, colorClass: 'text-green-500', barColor: '#E85D24' },
            { key: 'distribution', label: 'Distribution', value: admet.distribution, icon: CheckCircle2, colorClass: 'text-green-500', barColor: '#E85D24' },
            { key: 'metabolism', label: 'Metabolism', value: admet.metabolism, icon: AlertTriangle, colorClass: 'text-amber-500', barColor: '#F59E0B' },
            { key: 'excretion', label: 'Excretion', value: admet.excretion, icon: CheckCircle2, colorClass: 'text-green-500', barColor: '#E85D24' },
            { key: 'toxicity', label: 'Toxicity', value: admet.toxicity, icon: CheckCircle2, colorClass: 'text-green-500', barColor: '#E85D24' }
          ].map((item) => (
            <div key={item.key} className="mb-4 last:mb-0">
              <div className="flex justify-between items-center mb-1.5">
                <div className="flex items-center gap-2">
                  <item.icon className={`w-4 h-4 ${item.colorClass}`} />
                  <span className="text-sm text-gray-700 dark:text-gray-300">{item.label}</span>
                </div>
                <div className="text-sm font-semibold text-gray-900 dark:text-gray-100">{item.value}%</div>
              </div>
              <ProgressBar value={item.value} animated={true} color={item.barColor} />
            </div>
          ))}

          <div className="mt-6 italic text-xs text-gray-400 dark:text-gray-500 flex items-center gap-1.5">
            <Info className="w-3.5 h-3.5" />
            <span>Molecular feasibility validated using QSAR + ADMET modeling. Results are predictive, not experimental.</span>
          </div>
        </div>
      </div>
    </div>
  );
};
