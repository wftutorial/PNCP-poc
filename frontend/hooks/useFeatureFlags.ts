"use client";

import useSWR from "swr";

interface FeatureFlag {
  name: string;
  value: boolean;
  description: string;
  category: string;
}

interface FeatureFlagResponse {
  flags: FeatureFlag[];
  total: number;
}

/**
 * DEBT-205 / DEBT-FE-008: SWR-based feature flag consumer.
 * Fetches flags from /api/feature-flags (backend public endpoint).
 * Cache: 5 min dedup, no revalidation on focus.
 */
export function useFeatureFlags() {
  const { data, error, isLoading } = useSWR<FeatureFlagResponse>(
    "/api/feature-flags",
    {
      revalidateOnFocus: false,
      dedupingInterval: 300_000, // 5 min
      errorRetryCount: 2,
    },
  );

  const flagMap = new Map<string, boolean>();
  if (data?.flags) {
    for (const flag of data.flags) {
      flagMap.set(flag.name, flag.value);
    }
  }

  return {
    flags: flagMap,
    flagList: data?.flags || [],
    isLoading,
    error,
    isEnabled: (name: string, fallback = false): boolean =>
      flagMap.has(name) ? flagMap.get(name)! : fallback,
  };
}
