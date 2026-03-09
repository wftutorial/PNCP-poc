"use client";

import useSWR from "swr";
import { useAuth } from "../app/components/AuthProvider";
import { FetchError } from "../lib/fetcher";

/**
 * FE-007: SWR-based profile context hook.
 * Replaces manual fetch in conta/perfil/page.tsx.
 */

export interface ProfileContext {
  ufs_atuacao?: string[];
  porte_empresa?: string;
  experiencia_licitacoes?: string;
  faixa_valor_min?: number | null;
  faixa_valor_max?: number | null;
  capacidade_funcionarios?: number | null;
  faturamento_anual?: number | null;
  atestados?: string[];
  [key: string]: unknown;
}

const fetchProfileContextWithAuth = async (url: string, token: string) => {
  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) {
    throw new FetchError(`Erro ${res.status}`, res.status);
  }
  const data = await res.json();
  return (data.context_data ?? {}) as ProfileContext;
};

export function useProfileContext() {
  const { session } = useAuth();
  const accessToken = session?.access_token;

  const { data, error, isLoading, mutate } = useSWR(
    accessToken ? ["/api/profile-context", accessToken] : null,
    ([url, token]: [string, string]) => fetchProfileContextWithAuth(url, token),
    {
      revalidateOnFocus: false,
      dedupingInterval: 30_000,
      errorRetryCount: 2,
    }
  );

  return {
    profileCtx: data ?? null,
    isLoading,
    error: error ? String(error) : null,
    mutate,
    /** Call after a successful PUT to keep cache in sync. */
    updateCache: (updated: ProfileContext) =>
      mutate(updated, { revalidate: false }),
  };
}
