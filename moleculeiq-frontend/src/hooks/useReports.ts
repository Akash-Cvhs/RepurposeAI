import { useCallback, useEffect, useState } from "react";
import api from "../services/api";
import { ArchiveRun, ArchivesResponse } from "../types/report.types";

export function useReports() {
  const [runs, setRuns] = useState<ArchiveRun[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const { data } = await api.get<ArchivesResponse>("/archives");
      setRuns(data.runs ?? []);
    } catch (err) {
      setError("Could not load archives");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return { runs, loading, error, refresh };
}
