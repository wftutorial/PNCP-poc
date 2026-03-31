"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import { toast } from "sonner";
import { useBackendStatusContext } from "../../components/BackendStatusIndicator";
import { safeSetItem } from "../../../lib/storage";

interface UseSearchSSEParams {
  /** The raw buscar() from useSearch — wraps it with offline-queue + scroll. */
  originalBuscar: () => void;
  /** search.loading — drives elapsed counter + partialDismissed reset. */
  searchLoading: boolean;
  /**
   * Called synchronously when a search is about to execute (collapse filters,
   * mark user-has-searched in localStorage, hide first-use tip).
   */
  onSearchStart: () => void;
  /** filters.setUfsSelecionadas — used by handleRetryWithUfs. */
  setUfsSelecionadas: (ufs: Set<string>) => void;
}

export interface UseSearchSSEReturn {
  backendStatus: ReturnType<typeof useBackendStatusContext>;
  /** Search action wrapped with backend-offline queue + scroll-to-progress. */
  buscarWithCollapse: () => void;
  /** Retry with a reduced UF set (timeout recovery). */
  handleRetryWithUfs: (ufs: string[]) => void;
  /** Ref to attach to the progress area for auto-scroll on search start. */
  progressAreaRef: React.RefObject<HTMLDivElement | null>;
  /** Seconds elapsed since search started (reset on completion). */
  searchElapsed: number;
  /** Whether the user dismissed the partial results prompt. */
  partialDismissed: boolean;
  setPartialDismissed: (v: boolean) => void;
}

/**
 * DEBT-FE-001: Extracted from useSearchOrchestration.
 * Owns backend-status monitoring, offline search queuing, elapsed progress timer.
 */
export function useSearchSSE(params: UseSearchSSEParams): UseSearchSSEReturn {
  const { originalBuscar, searchLoading, onSearchStart, setUfsSelecionadas } = params;

  const backendStatus = useBackendStatusContext();
  const queuedSearchRef = useRef<(() => void) | null>(null);
  const progressAreaRef = useRef<HTMLDivElement>(null);

  const [searchElapsed, setSearchElapsed] = useState(0);
  const [partialDismissed, setPartialDismissed] = useState(false);

  // ── Search execution (offline-aware) ────────────────────────────────
  const buscarWithCollapse = useCallback(() => {
    const executeSearch = () => {
      onSearchStart();
      safeSetItem('smartlic-has-searched', 'true');
      originalBuscar();
      setTimeout(() => {
        progressAreaRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 100);
    };

    if (backendStatus.status === "offline") {
      toast.info("Servidor indisponivel no momento. A analise sera iniciada quando o servidor estiver disponivel.");
      queuedSearchRef.current = executeSearch;
      return;
    }

    executeSearch();
  }, [originalBuscar, backendStatus.status, onSearchStart]);

  // UX-436: Retry with a reduced set of UFs (timeout recovery)
  const handleRetryWithUfs = useCallback((ufs: string[]) => {
    setUfsSelecionadas(new Set(ufs));
    setTimeout(() => {
      originalBuscar();
    }, 100);
  }, [setUfsSelecionadas, originalBuscar]);

  // Drain queued search when backend comes back online
  useEffect(() => {
    if ((backendStatus.status === "online" || backendStatus.status === "recovering") && queuedSearchRef.current) {
      const queuedFn = queuedSearchRef.current;
      queuedSearchRef.current = null;
      toast.success("Servidor disponivel. Executando analise...");
      queuedFn();
    }
  }, [backendStatus.status]);

  // ── Elapsed timer ────────────────────────────────────────────────────
  useEffect(() => {
    if (!searchLoading) {
      setSearchElapsed(0);
      setPartialDismissed(false);
      return;
    }
    const interval = setInterval(() => setSearchElapsed(prev => prev + 1), 1000);
    return () => clearInterval(interval);
  }, [searchLoading]);

  return {
    backendStatus,
    buscarWithCollapse,
    handleRetryWithUfs,
    progressAreaRef,
    searchElapsed,
    partialDismissed,
    setPartialDismissed,
  };
}
