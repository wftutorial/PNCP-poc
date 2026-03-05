"use client";

import useSWR from "swr";

/**
 * TD-008 AC4: SWR-based /api/plans hook for pricing page.
 */
export function usePlans() {
  const { data, error, isLoading } = useSWR("/api/plans", {
    revalidateOnFocus: false,
    dedupingInterval: 60_000, // 1 min (plans rarely change)
    errorRetryCount: 2,
  });

  return {
    plans: data?.plans || null,
    error,
    isLoading,
  };
}
