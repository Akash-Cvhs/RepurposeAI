import { useState } from 'react';
import { Palette, Key, Database, Info, Shield, Activity, Globe, FileText, Star, RefreshCw, Trash2, Download, Rocket } from 'lucide-react';
import AppLogo from '../components/ui/AppLogo';
import { useSettingsStore } from '../utils/settingsStore';
import { useDarkMode } from '../utils/useDarkMode';
import { useToastStore } from '../store/toastStore';
import api from '../services/api';

export const SettingsPage = () => {
  const { isDark, toggleDark } = useDarkMode();
  const settings = useSettingsStore();
  const { addToast } = useToastStore();

  const [localApiUrl, setLocalApiUrl] = useState(settings.apiUrl);
  const [isTestingApi, setIsTestingApi] = useState(false);
  const [isConnected, setIsConnected] = useState<boolean | null>(null);
  const [latency, setLatency] = useState<number>(0);
  const [clearConfirm, setClearConfirm] = useState(false);

  const handleSaveApiUrl = () => {
    settings.setApiUrl(localApiUrl);
    addToast({ type: 'success', title: 'Success', message: 'API URL updated' });
  };

  const testConnection = async () => {
    setIsTestingApi(true);
    const start = Date.now();
    try {
      await api.get('/health');
      setLatency(Date.now() - start);
      setIsConnected(true);
      addToast({ type: 'success', title: 'Connection Successful', message: `Ping success: ${Date.now() - start}ms` });
    } catch (error) {
      setIsConnected(false);
      addToast({ type: 'error', title: 'Connection Failed', message: 'Unable to reach backend' });
    } finally {
      setIsTestingApi(false);
    }
  };

  const handleClear = () => {
    if (clearConfirm) {
      addToast({ type: 'error', title: 'Archive Cleared', message: 'All reports deleted' });
      setClearConfirm(false);
    } else {
      setClearConfirm(true);
    }
  };

  const colors = ['#E85D24', '#3B82F6', '#10B981', '#8B5CF6', '#F59E0B'];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-[#0F1117] p-8">
      <div className="max-w-3xl mx-auto">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Settings</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Manage your MoleculeIQ preferences and API configuration</p>
        </div>

        {/* SECTION 1: Appearance */}
        <div className="bg-white dark:bg-[#1E2130] border border-gray-200 dark:border-[#2D3148] rounded-xl shadow-sm mb-6">
          <div className="px-6 py-4 border-b border-gray-100 dark:border-[#2D3148] flex items-center">
            <Palette className="text-[#E85D24] w-5 h-5 mr-3" />
            <h2 className="font-semibold text-gray-900 dark:text-gray-100 text-sm">Appearance</h2>
            <span className="text-xs text-gray-400 ml-auto">Customize your display</span>
          </div>
          <div className="px-6 py-5 space-y-5">
            <div className="flex justify-between items-center">
              <div>
                <div className="text-sm font-medium text-gray-700 dark:text-gray-300">Color Theme</div>
                <div className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">Choose between light and dark mode</div>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-sm text-gray-600 dark:text-gray-400">{isDark ? 'Dark' : 'Light'}</span>
                <button onClick={toggleDark} className={`w-11 h-6 rounded-full transition-colors relative ${isDark ? 'bg-[#E85D24]' : 'bg-gray-200 dark:bg-gray-700'}`}>
                  <div className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform ${isDark ? 'left-6' : 'left-1'}`} />
                </button>
              </div>
            </div>

            <div className="flex justify-between items-center">
              <div>
                <div className="text-sm font-medium text-gray-700 dark:text-gray-300">Accent Color</div>
                <div className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">Primary brand color used across the app</div>
              </div>
              <div className="flex items-center gap-2">
                {colors.map(color => (
                  <div 
                    key={color}
                    onClick={() => settings.setAccentColor(color)}
                    style={{ backgroundColor: color }}
                    className={`w-6 h-6 rounded-full cursor-pointer border-2 transition-all ${
                      settings.accentColor === color ? 'border-gray-900 dark:border-white scale-110' : 'border-transparent'
                    }`}
                  />
                ))}
              </div>
            </div>

            <div className="flex justify-between items-center">
              <div>
                <div className="text-sm font-medium text-gray-700 dark:text-gray-300">Compact Mode</div>
                <div className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">Reduce spacing for more content density</div>
              </div>
              <button onClick={() => settings.setCompactMode(!settings.compactMode)} className={`w-11 h-6 rounded-full transition-colors relative ${settings.compactMode ? 'bg-[#E85D24]' : 'bg-gray-200 dark:bg-gray-700'}`}>
                <div className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform ${settings.compactMode ? 'left-6' : 'left-1'}`} />
              </button>
            </div>
          </div>
        </div>

        {/* SECTION 2: API Configuration */}
        <div className="bg-white dark:bg-[#1E2130] border border-gray-200 dark:border-[#2D3148] rounded-xl shadow-sm mb-6">
          <div className="px-6 py-4 border-b border-gray-100 dark:border-[#2D3148] flex items-center">
            <Key className="text-[#E85D24] w-5 h-5 mr-3" />
            <h2 className="font-semibold text-gray-900 dark:text-gray-100 text-sm">API Configuration</h2>
            <span className="text-xs text-gray-400 ml-auto">Backend connection settings</span>
          </div>
          <div className="px-6 py-5 space-y-5">
            <div className="flex justify-between items-center">
              <div>
                <div className="text-sm font-medium text-gray-700 dark:text-gray-300">Backend API URL</div>
                <div className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">FastAPI server endpoint</div>
              </div>
              <div className="flex items-center gap-2">
                <input 
                  type="text" 
                  value={localApiUrl}
                  onChange={(e) => setLocalApiUrl(e.target.value)}
                  className="border border-gray-300 dark:border-[#2D3148] dark:bg-[#161927] rounded-lg px-3 py-2 text-sm w-64 outline-none focus:border-[#E85D24] focus:ring-1 focus:ring-[#E85D24] dark:text-gray-100"
                />
                <button onClick={handleSaveApiUrl} className="bg-[#E85D24] text-white rounded-lg px-3 py-2 text-sm hover:bg-[#C94D1A] transition-colors">Save</button>
              </div>
            </div>

            <div className="flex justify-between items-center">
              <div>
                <div className="text-sm font-medium text-gray-700 dark:text-gray-300">Connection Status</div>
                <div className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">Current backend connectivity</div>
              </div>
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full animate-pulse ${isConnected === true ? 'bg-green-500' : isConnected === false ? 'bg-amber-500' : 'bg-gray-400'}`} />
                  {isConnected === true ? (
                    <div>
                      <span className="text-green-600 dark:text-green-400 text-sm font-medium">Connected</span>
                      <span className="text-xs text-gray-400 ml-2">Latency: {latency}ms</span>
                    </div>
                  ) : isConnected === false ? (
                    <span className="text-amber-600 text-sm font-medium">Offline — Demo Mode</span>
                  ) : (
                    <span className="text-gray-400 text-sm font-medium">Unknown</span>
                  )}
                </div>
                <button onClick={testConnection} disabled={isTestingApi} className="border border-gray-200 dark:border-[#2D3148] text-gray-600 dark:text-gray-400 rounded-lg px-3 py-2 text-sm hover:bg-gray-50 dark:hover:bg-gray-800 flex items-center transition-colors">
                  <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${isTestingApi ? 'animate-spin' : ''}`} />
                  Test Connection
                </button>
              </div>
            </div>

            <div className="flex justify-between items-center">
              <div>
                <div className="text-sm font-medium text-gray-700 dark:text-gray-300">Request Timeout</div>
                <div className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">Maximum wait time for agent analysis</div>
              </div>
              <select 
                value={settings.requestTimeout}
                onChange={(e) => settings.setRequestTimeout(Number(e.target.value))}
                className="border border-gray-300 dark:border-[#2D3148] dark:bg-[#161927] rounded-lg px-3 py-2 text-sm outline-none focus:border-[#E85D24] dark:text-gray-100"
              >
                <option value={120000}>2 min</option>
                <option value={300000}>5 min</option>
                <option value={600000}>10 min</option>
                <option value={99999999}>No limit</option>
              </select>
            </div>
          </div>
        </div>

        {/* SECTION 3: Agent Configuration */}
        <div className="bg-white dark:bg-[#1E2130] border border-gray-200 dark:border-[#2D3148] rounded-xl shadow-sm mb-6">
          <div className="px-6 py-4 border-b border-gray-100 dark:border-[#2D3148] flex items-center">
            <Rocket className="text-[#E85D24] w-5 h-5 mr-3" />
            <h2 className="font-semibold text-gray-900 dark:text-gray-100 text-sm">Agent Configuration</h2>
            <span className="text-xs text-gray-400 ml-auto">Control which agents run</span>
          </div>
          <div className="px-6 py-5 space-y-5">
            
            {[
              { id: 'patent', icon: Shield, name: 'Patent Agent', desc: 'Freedom-to-operate and patent landscape' },
              { id: 'clinical', icon: Activity, name: 'Clinical Trials Agent', desc: 'Trial pipeline and efficacy data' },
              { id: 'web', icon: Globe, name: 'Web Intelligence Agent', desc: 'Real-world evidence and guidelines' },
              { id: 'insights', icon: FileText, name: 'Internal Insights Agent', desc: 'Uploaded PDF document analysis' },
              { id: 'molecular', icon: Star, name: 'Molecular Validator', desc: 'QSAR + ADMET molecular validation', isUSP: true },
            ].map(agent => (
              <div key={agent.id} className="flex justify-between items-center">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-gray-100 dark:bg-gray-800 flex items-center justify-center flex-shrink-0">
                    <agent.icon className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                  </div>
                  <div>
                    <div className="text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center gap-2">
                      {agent.name}
                      {agent.isUSP && <span className="bg-[#FFF3EE] dark:bg-[#2A1F1A] text-[#E85D24] text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider">USP</span>}
                    </div>
                    <div className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">{agent.desc}</div>
                    {agent.isUSP && !settings.agents[agent.id as keyof typeof settings.agents] && (
                      <div className="text-[11px] text-amber-500 mt-1">Disabling this removes your key differentiator</div>
                    )}
                  </div>
                </div>
                <button 
                  onClick={() => settings.setAgent(agent.id, !settings.agents[agent.id as keyof typeof settings.agents])} 
                  className={`w-11 h-6 rounded-full transition-colors relative flex-shrink-0 ${settings.agents[agent.id as keyof typeof settings.agents] ? 'bg-[#E85D24]' : 'bg-gray-200 dark:bg-gray-700'}`}
                >
                  <div className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform ${settings.agents[agent.id as keyof typeof settings.agents] ? 'left-6' : 'left-1'}`} />
                </button>
              </div>
            ))}
            
          </div>
        </div>

        {/* SECTION 4: Data & Privacy */}
        <div className="bg-white dark:bg-[#1E2130] border border-gray-200 dark:border-[#2D3148] rounded-xl shadow-sm mb-6">
          <div className="px-6 py-4 border-b border-gray-100 dark:border-[#2D3148] flex items-center">
            <Database className="text-[#E85D24] w-5 h-5 mr-3" />
            <h2 className="font-semibold text-gray-900 dark:text-gray-100 text-sm">Data & Privacy</h2>
            <span className="text-xs text-gray-400 ml-auto">Manage your research data</span>
          </div>
          <div className="px-6 py-5 space-y-5">
            <div className="flex justify-between items-center">
              <div>
                <div className="text-sm font-medium text-gray-700 dark:text-gray-300">Auto-save Reports</div>
                <div className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">Automatically save all analyses to archive</div>
              </div>
              <button onClick={() => settings.setAutoSave(!settings.autoSave)} className={`w-11 h-6 rounded-full transition-colors relative ${settings.autoSave ? 'bg-[#E85D24]' : 'bg-gray-200 dark:bg-gray-700'}`}>
                <div className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform ${settings.autoSave ? 'left-6' : 'left-1'}`} />
              </button>
            </div>

            <div className="flex justify-between items-center">
              <div>
                <div className="text-sm font-medium text-gray-700 dark:text-gray-300">Export Archive</div>
                <div className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">Download all reports as a ZIP file</div>
              </div>
              <button 
                onClick={() => addToast({ type: 'info', title: 'Export', message: 'Export feature available in production' })}
                className="border border-gray-200 dark:border-[#2D3148] text-gray-600 dark:text-gray-400 rounded-lg px-4 py-2 text-sm hover:bg-gray-50 dark:hover:bg-gray-800 flex items-center gap-2 transition-colors"
              >
                <Download className="w-4 h-4" />
                Export ZIP
              </button>
            </div>

            <div className="flex justify-between items-center">
              <div>
                <div className="text-sm font-medium text-gray-700 dark:text-gray-300">Clear Research Archive</div>
                <div className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">Permanently delete all saved reports</div>
              </div>
              
              {!clearConfirm ? (
                <button 
                  onClick={handleClear}
                  className="border border-red-200 dark:border-red-900/50 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg px-4 py-2 text-sm flex items-center gap-2 transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                  Clear All
                </button>
              ) : (
                <div className="flex items-center gap-3">
                  <span className="text-sm text-red-500">Are you sure?</span>
                  <button onClick={handleClear} className="bg-red-500 hover:bg-red-600 text-white rounded-lg px-4 py-2 text-sm transition-colors">Yes, clear</button>
                  <button onClick={() => setClearConfirm(false)} className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 px-2 py-2 text-sm transition-colors">Cancel</button>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* SECTION 5: About */}
        <div className="bg-white dark:bg-[#1E2130] border border-gray-200 dark:border-[#2D3148] rounded-xl shadow-sm mb-6">
          <div className="px-6 py-4 border-b border-gray-100 dark:border-[#2D3148] flex items-center">
            <Info className="text-[#E85D24] w-5 h-5 mr-3" />
            <h2 className="font-semibold text-gray-900 dark:text-gray-100 text-sm">About RepurposeAI</h2>
          </div>
          
          <div className="px-6 py-5">
            <div className="flex items-start gap-4 mb-6">
              <AppLogo size="lg" showText={true} />
              <div className="pt-1">
                <span className="bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 text-xs font-medium px-2 py-0.5 rounded-full border border-gray-200 dark:border-gray-700">v1.2.0</span>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1.5 leading-relaxed">
                  Agentic AI platform for pharmaceutical drug repurposing and molecular innovation discovery. Built for VHS Hackathon 1.0 by Nehru Institute of Technology.
                </p>
              </div>
            </div>

            <div className="space-y-2 text-xs text-gray-400">
              <div className="font-medium text-gray-700 dark:text-gray-300 mb-2">Built with:</div>
              <div className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-[#009688]"></div>FastAPI + LangGraph (backend)</div>
              <div className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-[#61DAFB]"></div>React + TypeScript (frontend)</div>
              <div className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-[#CC525F]"></div>Claude Sonnet 4.5 (AI engine)</div>
              <div className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-[#336791]"></div>PostgreSQL on Railway (database)</div>
              <div className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-[#38BDF8]"></div>Tailwind CSS (styling)</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
