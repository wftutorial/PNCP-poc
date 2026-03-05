"use client";

import { useMemo } from "react";
import { useUserProfile } from "./useUserProfile";

interface QuotaInfo {
  planId: string | null;
  planName: string | null;
  creditsRemaining: number | null; // null = unlimited
  totalSearches: number;
  isUnlimited: boolean;
  isFreeUser: boolean;
  isAdmin: boolean;
  subscriptionStatus?: string;
  subscriptionEndDate?: string;
}

interface UseQuotaReturn {
  quota: QuotaInfo | null;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
}

const FREE_SEARCHES_LIMIT = 1000;
const UNLIMITED_THRESHOLD = 999990;

/**
 * TD-008 AC3: SWR-based quota hook.
 * Delegates to useUserProfile (SWR) for deduplication with usePlan.
 */
export function useQuota(): UseQuotaReturn {
  const { data, error, isLoading, mutate } = useUserProfile();

  const quota = useMemo<QuotaInfo | null>(() => {
    if (!data) return null;

    const planId = data.plan_id as string;
    const planName = data.plan_name as string;
    const quotaRemaining = (data.quota_remaining as number) || 0;
    const quotaUsed = (data.quota_used as number) || 0;
    const isAdmin = data.is_admin === true;
    const subscriptionStatus = data.subscription_status as string | undefined;
    const subscriptionEndDate = data.subscription_end_date as string | undefined;

    const isFreeUser = !isAdmin && (planId === "free" || planId === "free_trial");
    const isUnlimited = !isFreeUser && (quotaRemaining >= UNLIMITED_THRESHOLD || isAdmin);

    let creditsRemaining: number | null = null;
    if (isFreeUser) {
      creditsRemaining = Math.max(0, FREE_SEARCHES_LIMIT - quotaUsed);
    } else if (!isUnlimited) {
      creditsRemaining = quotaRemaining;
    }

    return {
      planId,
      planName,
      creditsRemaining,
      totalSearches: quotaUsed,
      isUnlimited,
      isFreeUser,
      isAdmin,
      subscriptionStatus,
      subscriptionEndDate,
    };
  }, [data]);

  return {
    quota,
    loading: isLoading,
    error: error ? "Erro ao carregar informações de quota" : null,
    refresh: async () => { await mutate(); },
  };
}
