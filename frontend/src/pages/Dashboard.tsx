import { useEffect, useRef } from 'react';
import { FlaskConical, Shield, Activity, Globe, FileText, Star } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { ChatInput } from '../components/chat/ChatInput';
import { AgentCard } from '../components/chat/AgentCard';
import { AgentStatusCard } from '../components/agents/AgentStatusCard';
import { ArchiveTable } from '../components/archive/ArchiveTable';
import { AgentCardUSP } from '../components/chat/AgentCardUSP';
import { FinalReportBubble } from '../components/chat/FinalReportBubble';
import { useResearch } from '../hooks/useResearch';
import { useToastStore } from '../store/toastStore';

interface DashboardProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

const AGENT_DATA = [
  { name: 'Patent Agent', icon: Shield, role: 'Searches patent databases, identifies expiry dates, flags Freedom-to-Operate risks', status: 'active' as const, lastRun: '2 min ago', queriesProcessed: 47, isUSP: false },
  { name: 'Clinical Trials Agent', icon: Activity, role: 'Queries ClinicalTrials.gov for trial pipeline by indication or mechanism of action', status: 'active' as const, lastRun: '2 min ago', queriesProcessed: 47, isUSP: false },
  { name: 'Web Intelligence Agent', icon: Globe, role: 'Searches treatment guidelines, real-world evidence and relevant pharma news', status: 'idle' as const, lastRun: '5 min ago', queriesProcessed: 31, isUSP: false },
  { name: 'Internal Insights Agent', icon: FileText, role: 'Summarizes uploaded internal PDFs, research memos and portfolio documents', status: 'idle' as const, lastRun: '8 min ago', queriesProcessed: 12, isUSP: false },
  { name: 'Molecular Validator', icon: Star, role: 'QSAR scoring, ADMET prediction and binding affinity — quantum-inspired USP', status: 'active' as const, lastRun: '2 min ago', queriesProcessed: 47, isUSP: true }
];

export const Dashboard = ({ activeTab, setActiveTab }: DashboardProps) => {
  const navigate = useNavigate();
  const { messages, isLoading, hasStarted, startResearch, resetChat } = useResearch();
  const { addToast } = useToastStore();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleNewResearch = () => {
      resetChat();
      setActiveTab('Research Chat');
    };
    window.addEventListener('new-research', handleNewResearch);
    return () => window.removeEventListener('new-research', handleNewResearch);
  }, [resetChat, setActiveTab]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = (query: string, molecule: string, file: File | null) => {
    startResearch(query, molecule, file ?? undefined);
  };

  if (activeTab === 'Agent Status') {
    return (
      <div className="p-6 overflow-y-auto h-full bg-gray-50 dark:bg-[#0F1117]">
        <div className="flex justify-between items-center mb-6">
          <div>
            <div className="text-lg font-semibold text-gray-900 dark:text-gray-100">Agent Status</div>
            <div className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">5 agents monitoring your research pipeline</div>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            <span className="text-sm text-green-600 dark:text-green-400 font-medium">All Systems Active</span>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {AGENT_DATA.map((agent, i) => (
            <div key={i} className={agent.isUSP ? 'md:col-span-2' : ''}>
              <AgentStatusCard {...agent} />
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (activeTab === 'Report Archive') {
    return (
      <div className="p-6 overflow-y-auto h-full bg-gray-50 dark:bg-[#0F1117]">
        <div className="mb-6">
          <div className="text-lg font-semibold text-gray-900 dark:text-gray-100">Report Archive</div>
          <div className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">All generated Innovation Product Stories</div>
        </div>
        <ArchiveTable onViewReport={(id) => navigate('/report/'+id)} />
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-white dark:bg-[#0F1117]">
      <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-4 flex flex-col">
        {!hasStarted ? (
          <div className="flex-1 flex flex-col items-center justify-center h-full text-center px-4">
            <FlaskConical className="w-16 h-16 text-[#E85D24] opacity-30" />
            <div className="text-xl font-medium text-gray-400 dark:text-gray-500 mt-4">Start a new drug repurposing analysis</div>
            <div className="text-sm text-gray-400 dark:text-gray-600 mt-1">Enter a molecule name or therapeutic area below</div>
          </div>
        ) : (
          <div className="space-y-6">
            {messages.map((msg) => {
              if (msg.type === 'user') {
                return (
                  <div key={msg.id} className="ml-auto w-fit max-w-[85%] md:max-w-lg bg-[#E85D24] text-white rounded-2xl rounded-tr-sm px-4 py-2.5 text-sm shadow-sm animate-in fade-in slide-in-from-bottom-2">
                    {msg.content}
                  </div>
                );
              }
              if (msg.type === 'agent') {
                return (
                  <div key={msg.id} className="max-w-2xl animate-in fade-in slide-in-from-bottom-2">
                    <AgentCard 
                      agentName={msg.agentName!} 
                      result={msg.content || ''} 
                      status={msg.status as 'running' | 'done' | 'failed'} 
                    />
                  </div>
                );
              }
              if (msg.type === 'usp') {
                return (
                  <div key={msg.id} className="max-w-2xl animate-in fade-in slide-in-from-bottom-2">
                    <AgentCardUSP status={msg.status as 'running' | 'done'} />
                  </div>
                );
              }
              if (msg.type === 'final') {
                return (
                  <div key={msg.id} className="max-w-2xl animate-in fade-in slide-in-from-bottom-2">
                    <FinalReportBubble 
                      onDownload={() => {
                        addToast({ type: 'info', title: 'Preparing PDF', message: 'Your report is being generated...' });
                      }}
                      onView={() => navigate('/report/' + (msg.content || 'demo_run'))}
                    />
                  </div>
                );
              }
              return null;
            })}
            <div ref={messagesEndRef} className="h-4" />
          </div>
        )}
      </div>
      <ChatInput onSend={handleSend} isLoading={isLoading} />
    </div>
  );
};
