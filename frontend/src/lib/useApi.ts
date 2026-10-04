import { useCallback, useEffect, useRef, useState } from "react";
import { api, errorMessage } from "../api/client";

/** GET a backend resource with loading / error state and a reload() to refetch after mutations. */
export function useApi<T>(url: string | null, deps: unknown[] = []) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<number | null>(null);
  const [loading, setLoading] = useState<boolean>(!!url);
  const seq = useRef(0);

  const load = useCallback(async () => {
    if (!url) { setLoading(false); return; }
    const id = ++seq.current;
    setLoading(true);
    setError(null);
    try {
      const r = await api.get<T>(url);
      if (id === seq.current) { setData(r.data); setStatus(r.status); }
    } catch (e) {
      if (id === seq.current) {
        setError(errorMessage(e));
        setStatus((e as { response?: { status?: number } })?.response?.status ?? null);
      }
    } finally {
      if (id === seq.current) setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [url, ...deps]);

  useEffect(() => { load(); }, [load]);
  return { data, error, status, loading, reload: load, setData };
}
