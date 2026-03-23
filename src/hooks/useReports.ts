import { useState, useEffect } from 'react';
import { getArchives } from '../services/api';
import { type ArchiveRun } from '../types/report.types';
import { useToastStore } from '../store/toastStore';

export const useReports = () => {
  const [reports, setReports] = useState<ArchiveRun[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const { addToast } = useToastStore();

  useEffect(() => {
    const fetch = async () => {
      try {
        const data = await getArchives();
        setReports(data);
      } catch {
        addToast({
          type: 'warning',
          title: 'Archive unavailable',
          message: 'Could not load reports from backend'
        });
      } finally {
        setIsLoading(false);
      }
    };
    fetch();
  }, [addToast]);

  return { reports, isLoading };
};
