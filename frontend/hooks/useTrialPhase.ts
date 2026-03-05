"use client";

import useSWR from "swr";
import { useAuth } from "../app/components/AuthProvider";
import { FetchError } from "../lib/fetcher";

/**
 * STORY-320 AC11: Trial phase information for soft paywall.
 */
export interface TrialPhaseInfo {
  phase: "full_access" | "limited_access" | "not_trial";
  day: number;
  daysRemaining: number;
  loading: boolean;
}

const fetchTrialStatus = async (url: string, token: string) => {
  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) return null;
  return res.json();
};

/**
 * TD-008 AC8: SWR-based trial phase hook.
 * Replaces manual fetch + sessionStorage cache with SWR deduplication + built-in cache.
 */
export function useTrialPhase(): TrialPhaseInfo {
  const { session } = useAuth();
  const accessToken = session?.access_token;

  const { data, isLoading } = useSWR(
    accessToken ? ["/api/trial-status", accessToken] : null,
    ([url, token]: [string, string]) => fetchTrialStatus(url, token),
    {
      revalidateOnFocus: false,
      dedupingInterval: 300_000, // 5 min (matches old sessionStorage TTL)
      errorRetryCount: 1,
      fallbackData: null,
    }
  );

  if (!accessToken || isLoading) {
    return { phase: "full_access", day: 0, daysRemaining: 999, loading: isLoading };
  }

  if (!data) {
    return { phase: "full_access", day: 0, daysRemaining: 999, loading: false };
  }

  return {
    phase: (data.trial_phase || "full_access") as TrialPhaseInfo["phase"],
    day: data.trial_day || 0,
    daysRemaining: data.days_remaining || 0,
    loading: false,
  };
}
