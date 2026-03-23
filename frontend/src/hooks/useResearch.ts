import { useState, useRef } from 'react';
import { runResearch, uploadPDF } from '../services/api';
import { useToastStore } from '../store/toastStore';
import { type ResearchResponse } from '../types/agent.types';

export interface Message {
  id: string;
  type: 'user' | 'agent' | 'usp' | 'final';
  content?: string;
  agentName?: string;
  status?: 'running' | 'done' | 'failed';
  molecularData?: ResearchResponse['molecular_validation'];
}

export const useResearch = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasStarted, setHasStarted] = useState(false);
  const timeoutsRef = useRef<ReturnType<typeof setTimeout>[]>([]);
  const { addToast } = useToastStore();

  const addMessage = (msg: Message) => {
    setMessages(prev => [...prev, msg]);
  };

  const updateMessage = (id: string, updates: Partial<Message>) => {
    setMessages(prev => prev.map(m => m.id === id ? { ...m, ...updates } : m));
  };

  const clearTimeouts = () => {
    timeoutsRef.current.forEach(clearTimeout);
    timeoutsRef.current = [];
  };

  const scheduleTimeout = (fn: () => void, delay: number) => {
    const t = setTimeout(fn, delay);
    timeoutsRef.current.push(t);
  };

  const startResearch = async (query: string, molecule: string, uploadedFile?: File | null) => {
    if (!query.trim()) {
      addToast({
        type: 'error',
        title: 'Input required',
        message: 'Please enter a molecule name or therapeutic area'
      });
      return;
    }

    clearTimeouts();
    setHasStarted(true);
    setIsLoading(true);
    
    addMessage({
      id: 'user-' + Date.now(),
      type: 'user',
      content: molecule ? query + ' — ' + molecule : query
    });

    try {
      if (uploadedFile) {
        await uploadPDF(uploadedFile);
        addToast({
          type: 'info',
          title: 'PDF uploaded',
          message: uploadedFile.name + ' processed by Internal Insights Agent'
        });
      }

      const agentSequence = [
        { 
          id: 'patent', 
          name: 'Patent Agent',
          delay: 600,
          doneDelay: 1400,
          mockResult: '12 patents found. 3 expired. FTO risk: LOW'
        },
        { 
          id: 'clinical', 
          name: 'Clinical Trials Agent',
          delay: 1800,
          doneDelay: 2600,
          mockResult: "47 trials found across 8 indications including Alzheimer's, PCOS, Cancer"
        },
        { 
          id: 'web', 
          name: 'Web Intelligence Agent',
          delay: 3000,
          doneDelay: 3800,
          mockResult: 'Strong RWE evidence for neurological applications found'
        },
        { 
          id: 'insights', 
          name: 'Internal Insights Agent',
          delay: 4200,
          doneDelay: 5000,
          mockResult: uploadedFile 
            ? '2 insights extracted from ' + uploadedFile.name
            : 'No internal documents provided'
        },
      ];

      agentSequence.forEach(agent => {
        scheduleTimeout(() => {
          addMessage({
            id: agent.id,
            type: 'agent',
            agentName: agent.name,
            status: 'running',
            content: ''
          });
        }, agent.delay);

        scheduleTimeout(() => {
          updateMessage(agent.id, {
            status: 'done',
            content: agent.mockResult
          });
        }, agent.doneDelay);
      });

      const response = await runResearch({ 
        query, 
        molecule: molecule || undefined 
      });

      scheduleTimeout(() => {
        addMessage({
          id: 'molecular',
          type: 'usp',
          agentName: 'Molecular Validator — USP',
          status: 'running'
        });
      }, 5400);

      scheduleTimeout(() => {
        updateMessage('molecular', {
          status: 'done',
          molecularData: response.molecular_validation
        });
      }, 7000);

      scheduleTimeout(() => {
        addMessage({
          id: 'final',
          type: 'final',
          content: response.run_id
        });
        setIsLoading(false);
        addToast({
          type: 'success',
          title: 'Analysis complete!',
          message: 'Innovation Product Story is ready to download'
        });
      }, 7400);

    } catch (error: unknown) {
      clearTimeouts();
      setIsLoading(false);
      
      scheduleTimeout(() => {
        addMessage({
          id: 'molecular',
          type: 'usp',
          agentName: 'Molecular Validator — USP',
          status: 'done'
        });
      }, 5400);

      scheduleTimeout(() => {
        addMessage({
          id: 'final',
          type: 'final',
          content: 'demo_run'
        });
        setIsLoading(false);
      }, 6000);

      const msg = error instanceof Error ? error.message : 'Unknown error';
      
      if (msg.includes('Network') || msg.includes('ECONNREFUSED')) {
        addToast({
          type: 'warning',
          title: 'Backend offline',
          message: 'Showing demo results. Connect backend to get real analysis.'
        });
      } else {
        addToast({
          type: 'error',
          title: 'Analysis failed',
          message: msg
        });
      }
    }
  };

  const resetChat = () => {
    clearTimeouts();
    setMessages([]);
    setHasStarted(false);
    setIsLoading(false);
  };

  return { messages, isLoading, hasStarted, startResearch, resetChat };
};
