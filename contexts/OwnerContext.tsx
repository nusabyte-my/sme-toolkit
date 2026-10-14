import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from "react";
import { apiCall } from "../services/apiClient";
import type { OwnerOverview } from "../types/owner";

interface OwnerState {
  overview: OwnerOverview | null;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  days: number;
  setDays: (days: number) => void;
}
const OwnerContext = createContext<OwnerState | null>(null);
export function OwnerProvider({ children }: { children: React.ReactNode }) {
  const [overview, setOverview] = useState<OwnerOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [days, setDays] = useState(30);
  const request = useRef(0);
  const refresh = useCallback(async () => {
    const sequence = ++request.current;
    setLoading(true);
    try {
      const next = await apiCall<OwnerOverview>(
        `/api/v1/owner/overview?days=${days}`,
      );
      if (sequence === request.current) {
        setOverview(next);
        setError(null);
      }
    } catch (err) {
      if (sequence === request.current)
        setError(
          err instanceof Error
            ? err.message
            : "Business data could not be loaded. Retry the request.",
        );
    } finally {
      if (sequence === request.current) setLoading(false);
    }
  }, [days]);
  useEffect(() => {
    void refresh();
    return () => {
      request.current += 1;
    };
  }, [refresh]);
  return (
    <OwnerContext.Provider
      value={{ overview, loading, error, refresh, days, setDays }}
    >
      {children}
    </OwnerContext.Provider>
  );
}
export function useOwner() {
  const context = useContext(OwnerContext);
  if (!context) throw new Error("OwnerProvider is required");
  return context;
}
