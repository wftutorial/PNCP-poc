"use client";

import { useState, useRef, useCallback } from "react";
import { isTransientError, getRetryMessage } from "../../../lib/error-messages";
import type { SearchError } from "./useSearch";

export interface UseSearchRetryReturn {
  retryCountdown: number | null;
  retryMessage: string | null;
  retryExhausted: boolean;
  retryAttemptRef: React.MutableRefObject<number>;
  retryTimerRef: React.MutableRefObject<ReturnType<typeof setInterval> | null>;
  autoRetryInProgressRef: React.MutableRefObject<boolean>;
  buscarRef: React.MutableRefObject<((options?: { forceFresh?: boolean }) => Promise<void>) | null>;
  /** Ref for clearing error — orchestrator wires this to setError(null) */
  clearErrorRef: React.MutableRefObject<(() => void) | null>;
  setRetryCountdown: (v: number | null) => void;
  setRetryMessage: (v: string | null) => void;
  setRetryExhausted: (v: boolean) => void;
  getRetryCooldown: (errorMessage: string | null, httpStatus?: number) => number;
  retryNow: () => void;
  cancelRetry: () => void;
  /** Reset retry state for a new user-initiated search */
  resetForNewSearch: () => void;
  /** Start auto-retry countdown after a transient error */
  startAutoRetry: (searchError: SearchError, setError: (e: SearchError | null) => void) => void;
}

export function useSearchRetry(): UseSearchRetryReturn {
  // CRIT-008 AC5: Auto-retry for transient errors
  const [retryCountdown, setRetryCountdown] = useState<number | null>(null);
  // GTM-UX-003 AC4-AC7: Contextual retry message
  const [retryMessage, setRetryMessage] = useState<string | null>(null);
  // GTM-UX-003 AC9: All retry attempts exhausted
  const [retryExhausted, setRetryExhausted] = useState(false);
  const retryAttemptRef = useRef(0);
  const retryTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const buscarRef = useRef<((options?: { forceFresh?: boolean }) => Promise<void>) | null>(null);
  const autoRetryInProgressRef = useRef(false);
  // Ref for clearing error state — wired by orchestrator
  const clearErrorRef = useRef<(() => void) | null>(null);

  // CRIT-006 AC18: Retry cooldown scaling by error type
  const getRetryCooldown = useCallback((errorMessage: string | null, httpStatus?: number): number => {
    if (httpStatus === 429) return 30; // Rate limit
    if (httpStatus === 500) return 20; // Server error
    if (errorMessage?.includes('demorou demais') || errorMessage?.includes('timeout') || errorMessage?.includes('TIMEOUT') || httpStatus === 504) return 15; // Timeout
    return 10; // Network error default
  }, []);

  // CRIT-008 AC5: Immediate retry during countdown
  const retryNow = useCallback(() => {
    if (retryTimerRef.current) {
      clearInterval(retryTimerRef.current);
      retryTimerRef.current = null;
    }
    setRetryCountdown(null);
    setRetryMessage(null);
    retryAttemptRef.current++;
    autoRetryInProgressRef.current = true;
    clearErrorRef.current?.();
    buscarRef.current?.();
  }, []);

  // CRIT-008 AC5: Cancel auto-retry countdown
  const cancelRetry = useCallback(() => {
    if (retryTimerRef.current) {
      clearInterval(retryTimerRef.current);
      retryTimerRef.current = null;
    }
    setRetryCountdown(null);
    setRetryMessage(null);
    // Keep the error displayed — user chose to stop retrying
  }, []);

  // Reset retry state on new user-initiated search (not auto-retry)
  const resetForNewSearch = useCallback(() => {
    if (!autoRetryInProgressRef.current) {
      retryAttemptRef.current = 0;
      if (retryTimerRef.current) {
        clearInterval(retryTimerRef.current);
        retryTimerRef.current = null;
      }
      setRetryCountdown(null);
      setRetryMessage(null);
      setRetryExhausted(false);
    }
    autoRetryInProgressRef.current = false;
  }, []);

  // DEBT-v3-S2 AC13-AC14: Silent auto-retry with backoff [10s, 20s].
  // No countdown, no attempt counter visible to user. Retries happen silently.
  // After 2 retries exhausted, show AC15 message.
  const startAutoRetry = useCallback((searchError: SearchError, setError: (e: SearchError | null) => void) => {
    if (isTransientError(searchError.httpStatus, searchError.rawMessage) && retryAttemptRef.current < 2) {
      const RETRY_DELAYS = [10, 20];
      const delaySeconds = RETRY_DELAYS[retryAttemptRef.current] ?? 20;
      let remaining = delaySeconds;
      // AC13: Show humanized message during silent retry (no countdown exposed)
      setRetryMessage(getRetryMessage(searchError.httpStatus, searchError.rawMessage));
      setRetryCountdown(remaining);
      setRetryExhausted(false);

      if (retryTimerRef.current) clearInterval(retryTimerRef.current);
      retryTimerRef.current = setInterval(() => {
        remaining--;
        if (remaining <= 0) {
          if (retryTimerRef.current) clearInterval(retryTimerRef.current);
          retryTimerRef.current = null;
          setRetryCountdown(null);
          retryAttemptRef.current++;
          autoRetryInProgressRef.current = true;
          setError(null);
          setRetryMessage(null);
          buscarRef.current?.();
        } else {
          setRetryCountdown(remaining);
        }
      }, 1000);
    } else if (isTransientError(searchError.httpStatus, searchError.rawMessage) && retryAttemptRef.current >= 2) {
      // AC15: All 2 attempts exhausted — show final humanized message
      setRetryExhausted(true);
      setRetryMessage(null);
      setRetryCountdown(null);
    }
  }, []);

  return {
    retryCountdown,
    retryMessage,
    retryExhausted,
    retryAttemptRef,
    retryTimerRef,
    autoRetryInProgressRef,
    buscarRef,
    clearErrorRef,
    setRetryCountdown,
    setRetryMessage,
    setRetryExhausted,
    getRetryCooldown,
    retryNow,
    cancelRetry,
    resetForNewSearch,
    startAutoRetry,
  };
}
