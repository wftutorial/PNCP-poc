"use client";

import { SWRConfig } from "swr";
import { fetcher } from "../lib/fetcher";

/**
 * TD-008 AC1: Global SWR config provider.
 * - revalidateOnFocus disabled (avoid unnecessary API calls on tab switch)
 * - dedupingInterval 5s (prevent duplicate concurrent requests)
 * - errorRetryCount 3 (built-in retry with exponential backoff)
 */
export function SWRProvider({ children }: { children: React.ReactNode }) {
  return (
    <SWRConfig
      value={{
        fetcher,
        revalidateOnFocus: false,
        dedupingInterval: 5000,
        errorRetryCount: 3,
      }}
    >
      {children}
    </SWRConfig>
  );
}
