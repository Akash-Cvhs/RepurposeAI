import { useState } from 'react';
import type { ReactNode } from 'react';
import { Sidebar } from './Sidebar';
import { Menu } from 'lucide-react';
import { useLocation } from 'react-router-dom';

interface MainLayoutProps {
  children: ReactNode;
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const MainLayout = ({ children, activeTab, setActiveTab }: MainLayoutProps) => {
  const tabs = ['Research Chat', 'Agent Status', 'Report Archive'];
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50 dark:bg-[#0F1117]">
      <Sidebar isOpen={mobileMenuOpen} onClose={() => setMobileMenuOpen(false)} setActiveTab={setActiveTab} />
      <div className="flex-1 flex flex-col overflow-hidden w-full relative">
        <div className="bg-white dark:bg-[#1A1D27] border-b border-gray-200 dark:border-[#2D3148] px-4 lg:px-6 pt-0 flex items-center shadow-sm z-10 min-h-[58px]">
          <button 
            onClick={() => setMobileMenuOpen(true)}
            className="lg:hidden p-2 rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 mr-2 mt-2"
          >
            <Menu className="w-5 h-5" />
          </button>
          
          {location.pathname !== '/settings' && location.pathname !== '/settings/' && (
            <div className="flex items-center pt-2 overflow-x-auto scrollbar-hide flex-1">
              {tabs.map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`py-3 lg:py-4 px-1 mr-6 lg:mr-8 text-sm border-b-2 transition-colors whitespace-nowrap flex-shrink-0 ${
                    activeTab === tab
                      ? 'border-[#E85D24] text-gray-900 dark:text-gray-100 font-medium'
                      : 'border-transparent text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-400'
                  }`}
                >
                  {tab}
                </button>
              ))}
            </div>
          )}
        </div>
        <div className="flex-1 overflow-y-auto w-full">
          {children}
        </div>
      </div>
    </div>
  );
};
