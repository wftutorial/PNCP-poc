"use client";

import useSWR from "swr";

/**
 * FE-007: SWR-based public metrics hooks.
 * Replaces manual fetch in InstitutionalSidebar.tsx and StatsSection.tsx.
 * No auth required — these are public endpoints.
 */

const fetchPublic = async (url: string) => {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
};

interface DailyVolumeData {
  display_value: string;
  avg_bids_per_day: number;
}

/** Daily licitações volume for signup sidebar stat. */
export function useDailyVolume() {
  const { data, error, isLoading } = useSWR<DailyVolumeData>(
    "/api/metrics/daily-volume",
    fetchPublic,
    {
      revalidateOnFocus: false,
      dedupingInterval: 300_000, // 5 min — metrics don't change often
      errorRetryCount: 1,
    }
  );

  return {
    displayValue: data?.display_value ?? null,
    isLoading,
    error: error ? String(error) : null,
  };
}

interface DiscardRateData {
  discard_rate_pct: number;
  sample_size: number;
}

/** Discard rate for landing stats section. */
export function useDiscardRate() {
  const { data, error, isLoading } = useSWR<DiscardRateData>(
    "/api/metrics/discard-rate",
    fetchPublic,
    {
      revalidateOnFocus: false,
      dedupingInterval: 300_000, // 5 min
      errorRetryCount: 1,
    }
  );

  const discardRate =
    data && data.sample_size > 0 && data.discard_rate_pct > 0
      ? Math.round(data.discard_rate_pct)
      : null;

  return {
    discardRate,
    isLoading,
    error: error ? String(error) : null,
  };
}
