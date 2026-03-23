import { useState } from 'react';
import { Search, Eye, Download } from 'lucide-react';
import { Badge } from '../ui/Badge';
import { useReports } from '../../hooks/useReports';

interface ArchiveTableProps {
  onViewReport: (runId: string) => void;
}

export const ArchiveTable = ({ onViewReport }: ArchiveTableProps) => {
  const [searchQuery, setSearchQuery] = useState('');
  const { reports, isLoading } = useReports();

  const filteredReports = reports.filter(report => 
    report.molecule.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getScoreVariant = (score: number) => {
    if (score >= 75) return 'success';
    if (score >= 60) return 'warning';
    return 'danger';
  };

  return (
    <div>
      <div className="relative mb-4">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input 
          type="text"
          className="w-full pl-9 pr-4 py-2.5 text-sm border border-gray-300 dark:border-[#2D3148] bg-white dark:bg-[#1E2130] text-gray-900 dark:text-gray-100 rounded-lg outline-none focus:border-[#E85D24] focus:ring-1 focus:ring-[#E85D24] placeholder-gray-400"
          placeholder="Search by molecule name..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      <div className="bg-white dark:bg-[#1E2130] border border-gray-200 dark:border-[#2D3148] rounded-xl shadow-sm overflow-hidden min-h-[200px]">
        {isLoading ? (
          <div className="p-6 space-y-4 w-full">
            {[1, 2, 3].map((n) => (
              <div key={n} className="animate-pulse bg-gray-200 dark:bg-gray-700 rounded h-12 w-full" />
            ))}
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-gray-50 dark:bg-[#161927] border-b border-gray-200 dark:border-[#2D3148]">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">Molecule</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">Date</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">Opportunities</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">Confidence Score</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">Status</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredReports.map((row) => (
                <tr key={row.id} className="hover:bg-[#FFF3EE] dark:hover:bg-[#2A1F1A] transition-colors border-b border-gray-100 dark:border-[#2D3148] last:border-0">
                  <td className="px-6 py-4 font-semibold text-gray-900 dark:text-gray-100">{row.molecule}</td>
                  <td className="px-6 py-4 text-gray-500 dark:text-gray-400">{row.date}</td>
                  <td className="px-6 py-4 text-gray-900 dark:text-gray-100 font-medium">
                    {row.opportunities}
                    <span className="bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded-full px-2 py-0.5 text-xs ml-1">
                      found
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <Badge label={`${row.confidenceScore}/100`} variant={getScoreVariant(row.confidenceScore)} />
                  </td>
                  <td className="px-6 py-4">
                    <Badge label="Completed" variant="success" />
                  </td>
                  <td className="px-6 py-4 flex gap-2">
                    <button 
                      onClick={() => onViewReport(row.id)}
                      className="border border-[#E85D24] text-[#E85D24] hover:bg-[#FFF3EE] dark:hover:bg-[#2A1F1A] rounded-lg px-3 py-1.5 text-xs font-medium flex items-center gap-1.5"
                    >
                      <Eye className="w-3.5 h-3.5" />
                      View
                    </button>
                    <button className="bg-[#E85D24] hover:bg-[#C94D1A] text-white rounded-lg px-3 py-1.5 text-xs font-medium flex items-center gap-1.5">
                      <Download className="w-3.5 h-3.5" />
                      Download
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        
        {!isLoading && filteredReports.length === 0 && (
          <div className="py-12 text-center">
            <Search className="w-10 h-10 text-gray-300 mx-auto" />
            <div className="text-gray-500 mt-3">No reports found</div>
            <div className="text-gray-400 text-sm">Try a different search term</div>
          </div>
        )}
      </div>

      <div className="flex justify-between items-center mt-3 px-1">
        <div className="text-xs text-gray-400">
          Showing {filteredReports.length} reports
        </div>
        <button className="text-xs text-[#E85D24] hover:underline flex items-center gap-1">
          <Download className="w-3 h-3" />
          Export All
        </button>
      </div>
    </div>
  );
};
