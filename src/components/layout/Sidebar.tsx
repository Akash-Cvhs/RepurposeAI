import { useState, useEffect } from 'react';
import { LayoutDashboard, FlaskConical, Archive, Settings, Moon, Sun } from 'lucide-react';
import AppLogo from '../ui/AppLogo';
import { useDarkMode } from '../../utils/useDarkMode';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
  setActiveTab?: (tab: string) => void;
}

export const Sidebar = ({ isOpen = true, onClose, setActiveTab }: SidebarProps) => {
  const { isDark, toggleDark } = useDarkMode();
  const [isConnected, setIsConnected] = useState<boolean>(true);
  const navigate = useNavigate();

  useEffect(() => {
    api.get('/health')
      .then(() => setIsConnected(true))
      .catch(() => setIsConnected(false));
  }, []);

  const handleNewResearch = () => {
    navigate('/');
    window.dispatchEvent(new CustomEvent('new-research'));
    if (setActiveTab) setActiveTab('Research Chat');
    if (onClose) onClose();
  };

  const sidebarContent = (
    <div className="w-[280px] h-full bg-white dark:bg-[#1A1D27] border-r border-gray-200 dark:border-[#2D3148] flex flex-col relative shadow-xl lg:shadow-none">
        <div className="p-5">
          <AppLogo size="md" showText={true} />
        </div>

      <div className="mt-8 flex flex-col gap-1">
        <div onClick={() => { navigate('/'); setActiveTab?.('Research Chat'); if (onClose) onClose(); }} className="flex items-center gap-3 px-4 py-2.5 rounded-lg mx-2 cursor-pointer text-sm transition-all text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-gray-700 dark:hover:text-gray-200">
          <LayoutDashboard className="w-4 h-4" />
          <span>Dashboard</span>
        </div>
        <div onClick={handleNewResearch} className="flex items-center gap-3 px-4 py-2.5 rounded-lg mx-2 cursor-pointer text-sm transition-all bg-[#FFF3EE] dark:bg-[#2A1F1A] text-[#E85D24] font-medium border-l-[3px] border-[#E85D24]">
          <FlaskConical className="w-4 h-4" />
          <span>New Research</span>
        </div>
        <div onClick={() => { navigate('/'); setActiveTab?.('Report Archive'); if (onClose) onClose(); }} className="flex items-center gap-3 px-4 py-2.5 rounded-lg mx-2 cursor-pointer text-sm transition-all text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-gray-700 dark:hover:text-gray-200">
          <Archive className="w-4 h-4" />
          <span>Report Archive</span>
        </div>
        <div onClick={() => { navigate('/settings'); if (onClose) onClose(); }} className="flex items-center gap-3 px-4 py-2.5 rounded-lg mx-2 cursor-pointer text-sm transition-all text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-gray-700 dark:hover:text-gray-200">
          <Settings className="w-4 h-4" />
          <span>Settings</span>
        </div>
      </div>

      <div className="absolute bottom-0 w-full p-4 flex flex-col items-center">
        <button 
          onClick={toggleDark}
          className="flex items-center justify-center gap-2 px-4 py-2 mx-2 mb-4 rounded-lg text-sm transition-all w-full text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800"
        >
          {isDark ? (
            <>
              <Sun className="w-4 h-4" />
              <span>Light Mode</span>
            </>
          ) : (
            <>
              <Moon className="w-4 h-4" />
              <span>Dark Mode</span>
            </>
          )}
        </button>

        <div className="bg-white w-full dark:bg-[#1E2130] border border-gray-200 dark:border-[#2D3148] rounded-xl p-4">
          <div className="text-xs text-gray-400 uppercase tracking-wide">Agents Online</div>
          <div className="text-2xl font-bold text-gray-900 dark:text-gray-100 mt-1">5/5</div>
          <div className="flex items-center gap-1.5 mt-2">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="w-2.5 h-2.5 rounded-full bg-[#E85D24]" />
            ))}
          </div>
          <div className="inline-flex bg-[#FFF3EE] dark:bg-[#2A1F1A] text-[#E85D24] text-xs font-medium rounded-full px-2.5 py-1 mt-3">
            All Active
          </div>
          <div className="mt-3 flex items-center gap-1.5 text-xs text-gray-400">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-amber-500'}`} />
            <span>{isConnected ? 'Backend connected' : 'Demo mode'}</span>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <>
      <div className={`lg:hidden fixed inset-y-0 left-0 z-40 transition-transform duration-300 ${isOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        {sidebarContent}
      </div>
      {isOpen && (
        <div className="lg:hidden fixed inset-0 bg-black/50 z-30 transition-opacity" onClick={onClose} />
      )}
      <div className="hidden lg:flex lg:flex-col h-full z-0 flex-shrink-0">
        {sidebarContent}
      </div>
    </>
  );
};
