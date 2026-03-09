"use client";

import useSWR from "swr";
import { useAuth } from "../app/components/AuthProvider";
import { FetchError } from "../lib/fetcher";
import type { ConversationSummary } from "../app/types";

/**
 * FE-007: SWR-based conversations list hook.
 * Replaces manual fetch in mensagens/page.tsx.
 * Note: individual thread fetching (fetchThread) remains as direct fetch
 * because it's triggered imperatively on item click (not initial load).
 */

const fetchConversationsWithAuth = async (url: string, token: string) => {
  const res = await fetch(url, {
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });
  if (!res.ok) {
    throw new FetchError("Erro ao carregar conversas", res.status);
  }
  const data = await res.json();
  return (data.conversations || []) as ConversationSummary[];
};

interface UseConversationsOptions {
  statusFilter?: string;
}

export function useConversations({ statusFilter = "" }: UseConversationsOptions = {}) {
  const { session } = useAuth();
  const accessToken = session?.access_token;

  const params = new URLSearchParams();
  if (statusFilter) params.set("status", statusFilter);
  const qs = params.toString();
  const url = `/api/messages/conversations${qs ? `?${qs}` : ""}`;

  const { data, error, isLoading, mutate } = useSWR(
    accessToken ? [url, accessToken] : null,
    ([u, token]: [string, string]) => fetchConversationsWithAuth(u, token),
    {
      revalidateOnFocus: false,
      dedupingInterval: 10_000,
      errorRetryCount: 2,
    }
  );

  return {
    conversations: data ?? [],
    isLoading,
    error: error ? String(error) : null,
    mutate,
    refresh: () => mutate(),
  };
}
