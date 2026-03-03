/**
 * useUfProgress - React hook for tracking per-UF search progress via SSE.
 *
 * Maintains a Map of UF statuses (pending -> fetching -> retrying -> success/failed/recovered)
 * and computes aggregated metrics (total found, all complete).
 *
 * STORY-365: Auto-reconnection with exponential backoff + polling fallback.
 * - AC6: Auto-reconnect on EventSource error
 * - AC7: Exponential backoff 1s → 2s → 4s (max 3 attempts)
 * - AC8: Pass last_event_id on reconnect, progress not reset
 * - AC9: After 3 failures, fallback to polling GET /v1/search/{id}/status every 5s
 */

import { useEffect, useState, useRef, useCallback } from 'react';

export type UfStatusType = 'pending' | 'fetching' | 'retrying' | 'success' | 'failed' | 'recovered';

export interface UfStatus {
  status: UfStatusType;
  count?: number;
  attempt?: number;
}

export interface UfStatusEvent {
  uf: string;
  status: UfStatusType;
  count?: number;
  attempt?: number;
}

/** GTM-FIX-031: Batch progress info for phased UF fetching */
export interface BatchProgress {
  batchNum: number;
  totalBatches: number;
  ufsInBatch: string[];
}

interface UseUfProgressOptions {
  searchId: string | null;
  enabled: boolean;
  authToken?: string;
  selectedUfs: string[];
}

interface UseUfProgressReturn {
  ufStatuses: Map<string, UfStatus>;
  totalFound: number;
  allComplete: boolean;
  batchProgress: BatchProgress | null;
  /** GTM-FIX-033 AC2: true when SSE disconnected after retry */
  sseDisconnected: boolean;
}

// STORY-365 AC7: Backoff delays in ms (1s, 2s, 4s)
const RECONNECT_BACKOFF_MS = [1000, 2000, 4000];
const MAX_RECONNECT_ATTEMPTS = 3;

// STORY-365 AC9: Polling interval when SSE fails completely
const POLLING_INTERVAL_MS = 5000;

// Terminal SSE stages that signal search is done
const TERMINAL_STAGES = new Set([
  'complete', 'error', 'degraded', 'refresh_available', 'search_complete',
]);

export function useUfProgress({
  searchId,
  enabled,
  authToken,
  selectedUfs,
}: UseUfProgressOptions): UseUfProgressReturn {
  const [ufStatuses, setUfStatuses] = useState<Map<string, UfStatus>>(new Map());
  const [batchProgress, setBatchProgress] = useState<BatchProgress | null>(null);
  const [sseDisconnected, setSseDisconnected] = useState(false);
  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectAttemptRef = useRef(0);
  const lastEventIdRef = useRef<string | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pollingTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const isTerminalRef = useRef(false);
  const selectedUfsRef = useRef(selectedUfs);

  // Serialize selectedUfs for stable dependency comparison
  const selectedUfsKey = selectedUfs.join(',');

  // Keep ref updated for use in callbacks
  useEffect(() => {
    selectedUfsRef.current = selectedUfs;
  }, [selectedUfsKey]);

  // Initialize all selected UFs with 'pending' status when search starts
  useEffect(() => {
    if (!enabled || !searchId) {
      setUfStatuses(new Map());
      setBatchProgress(null);
      setSseDisconnected(false);
      reconnectAttemptRef.current = 0;
      lastEventIdRef.current = null;
      isTerminalRef.current = false;
      return;
    }

    const initialStatuses = new Map<string, UfStatus>();
    selectedUfsRef.current.forEach(uf => {
      initialStatuses.set(uf, { status: 'pending' });
    });
    setUfStatuses(initialStatuses);
    setBatchProgress(null);
  }, [searchId, enabled, selectedUfsKey]);

  const cleanupPolling = useCallback(() => {
    if (pollingTimerRef.current) {
      clearInterval(pollingTimerRef.current);
      pollingTimerRef.current = null;
    }
  }, []);

  const cleanup = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
    cleanupPolling();
  }, [cleanupPolling]);

  // STORY-365 AC9: Polling fallback when all SSE reconnect attempts exhausted
  const startPollingFallback = useCallback((sid: string, token?: string) => {
    if (pollingTimerRef.current || isTerminalRef.current) return;

    console.warn(`STORY-365 AC9: Starting polling fallback for search ${sid}`);
    setSseDisconnected(true);

    pollingTimerRef.current = setInterval(async () => {
      try {
        const headers: Record<string, string> = {};
        if (token) {
          headers['Authorization'] = `Bearer ${token}`;
        }
        const res = await fetch(`/api/buscar?endpoint=search/${encodeURIComponent(sid)}/status`, {
          headers,
        });
        if (!res.ok) return;

        const data = await res.json();
        const status = data?.status;

        if (status && TERMINAL_STAGES.has(status === 'completed' ? 'complete' : status)) {
          cleanupPolling();
          isTerminalRef.current = true;
        }
      } catch (err) {
        console.warn('STORY-365: Polling fallback error:', err);
      }
    }, POLLING_INTERVAL_MS);
  }, [cleanupPolling]);

  // Attach SSE event handlers to an EventSource instance
  const attachHandlers = useCallback((
    es: EventSource,
    sid: string,
    token?: string,
  ) => {
    // STORY-365 AC8: Track last event ID from all events via onmessage
    es.onmessage = (e: MessageEvent) => {
      // Track the last event ID for reconnection replay
      if (e.lastEventId) {
        lastEventIdRef.current = e.lastEventId;
      }

      try {
        const data = JSON.parse(e.data);

        // Handle uf_status events
        if (data.stage === 'uf_status' || data.uf_status) {
          const uf = data.uf || data.detail?.uf;
          const status = data.uf_status || data.detail?.uf_status;
          if (uf && status) {
            setUfStatuses(prev => {
              const next = new Map(prev);
              next.set(uf, {
                status,
                count: data.detail?.count ?? data.count,
                attempt: data.detail?.attempt ?? data.attempt,
              });
              return next;
            });
          }
        }

        // Handle batch_progress events
        if (data.stage === 'batch_progress') {
          const detail = data.detail || data;
          setBatchProgress({
            batchNum: detail.batch_num ?? detail.batchNum,
            totalBatches: detail.total_batches ?? detail.totalBatches,
            ufsInBatch: detail.ufs_in_batch ?? detail.ufsInBatch ?? [],
          });
        }

        // Check for terminal event
        if (TERMINAL_STAGES.has(data.stage)) {
          isTerminalRef.current = true;
          es.close();
          eventSourceRef.current = null;
        }
      } catch {
        // Non-JSON data (comments, heartbeats) — ignore
      }
    };

    // Also listen via named events for backward compatibility
    es.addEventListener('uf_status', (e: MessageEvent) => {
      if (e.lastEventId) lastEventIdRef.current = e.lastEventId;
      try {
        const event: UfStatusEvent = JSON.parse(e.data);
        setUfStatuses(prev => {
          const next = new Map(prev);
          next.set(event.uf, {
            status: event.status,
            count: event.count,
            attempt: event.attempt,
          });
          return next;
        });
      } catch (err) {
        console.warn('Failed to parse uf_status event:', err);
      }
    });

    es.addEventListener('batch_progress', (e: MessageEvent) => {
      if (e.lastEventId) lastEventIdRef.current = e.lastEventId;
      try {
        const data = JSON.parse(e.data);
        setBatchProgress({
          batchNum: data.batch_num,
          totalBatches: data.total_batches,
          ufsInBatch: data.ufs_in_batch || [],
        });
      } catch (err) {
        console.warn('Failed to parse batch_progress event:', err);
      }
    });

    // STORY-365 AC6+AC7: Auto-reconnect with exponential backoff
    es.onerror = () => {
      // Don't reconnect if search already completed
      if (isTerminalRef.current) {
        es.close();
        eventSourceRef.current = null;
        return;
      }

      console.warn(
        `STORY-365: SSE error (attempt ${reconnectAttemptRef.current + 1}/${MAX_RECONNECT_ATTEMPTS})`
      );
      es.close();
      eventSourceRef.current = null;

      // AC7: Check if we have retries left
      if (reconnectAttemptRef.current < MAX_RECONNECT_ATTEMPTS) {
        const delay = RECONNECT_BACKOFF_MS[reconnectAttemptRef.current] ?? 4000;
        reconnectAttemptRef.current += 1;

        console.log(`STORY-365 AC7: Reconnecting in ${delay}ms...`);
        reconnectTimerRef.current = setTimeout(() => {
          reconnectTimerRef.current = null;
          if (isTerminalRef.current) return;

          // AC8: Build URL with last_event_id for replay
          let reconnUrl = `/api/buscar-progress?search_id=${encodeURIComponent(sid)}`;
          if (token) {
            reconnUrl += `&token=${encodeURIComponent(token)}`;
          }
          if (lastEventIdRef.current) {
            reconnUrl += `&last_event_id=${encodeURIComponent(lastEventIdRef.current)}`;
          }

          const reconnSource = new EventSource(reconnUrl);
          eventSourceRef.current = reconnSource;
          // Recursively attach same handlers (including reconnect logic)
          attachHandlers(reconnSource, sid, token);
        }, delay);
      } else {
        // AC9: All retries exhausted — switch to polling fallback
        startPollingFallback(sid, token);
      }
    };
  }, [startPollingFallback]);

  useEffect(() => {
    if (!enabled || !searchId) {
      cleanup();
      return;
    }

    // Build SSE URL through Next.js proxy
    let url = `/api/buscar-progress?search_id=${encodeURIComponent(searchId)}`;
    if (authToken) {
      url += `&token=${encodeURIComponent(authToken)}`;
    }

    const eventSource = new EventSource(url);
    eventSourceRef.current = eventSource;
    reconnectAttemptRef.current = 0;
    isTerminalRef.current = false;

    attachHandlers(eventSource, searchId, authToken);

    return cleanup;
  }, [searchId, enabled, authToken, cleanup, attachHandlers]);

  // Compute derived values
  const totalFound = Array.from(ufStatuses.values())
    .filter(status => status.status === 'success' || status.status === 'recovered')
    .reduce((sum, status) => sum + (status.count || 0), 0);

  const allComplete = ufStatuses.size > 0 &&
    Array.from(ufStatuses.values()).every(
      status => status.status === 'success' ||
                status.status === 'failed' ||
                status.status === 'recovered'
    );

  return {
    ufStatuses,
    totalFound,
    allComplete,
    batchProgress,
    sseDisconnected,
  };
}
