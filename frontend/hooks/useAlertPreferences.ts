"use client";

import useSWR from "swr";
import { useAuth } from "../app/components/AuthProvider";
import { FetchError } from "../lib/fetcher";

/**
 * FE-007: SWR-based alert preferences hook.
 * Replaces manual fetch in conta/plano/AlertPreferences.tsx.
 */

export interface AlertPreferencesData {
  enabled: boolean;
  frequency: string;
}

const fetchAlertPrefsWithAuth = async (url: string, token: string) => {
  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) {
    throw new FetchError(`Erro ${res.status}`, res.status);
  }
  return res.json();
};

export function useAlertPreferences() {
  const { session } = useAuth();
  const accessToken = session?.access_token;

  const { data, error, isLoading, mutate } = useSWR(
    accessToken ? ["/api/alert-preferences", accessToken] : null,
    ([url, token]: [string, string]) => fetchAlertPrefsWithAuth(url, token),
    {
      revalidateOnFocus: false,
      dedupingInterval: 30_000,
      errorRetryCount: 2,
    }
  );

  return {
    preferences: data
      ? {
          enabled: data.enabled ?? true,
          frequency: data.frequency ?? "daily",
        }
      : null,
    error: error ? String(error) : null,
    isLoading,
    mutate,
  };
}
