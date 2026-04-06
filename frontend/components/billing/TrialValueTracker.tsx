"use client";

import useSWR from "swr";
import { useAuth } from "../../app/components/AuthProvider";
import { usePlan } from "../../hooks/usePlan";

/**
 * P0 zero-churn: Trial Value Dashboard widget.
 *
 * Shows accumulated value during trial period so users see ROI in real-time.
 * Only visible for free_trial users. Fetches from /v1/analytics/trial-value.
 */

interface TrialStats {
  total_opportunities: number;
  total_value: number;
  searches_executed: number;
}

const formatCompact = (val: number): string => {
  if (val >= 1_000_000) return `R$ ${(val / 1_000_000).toFixed(1)}M`;
  if (val >= 1_000) return `R$ ${(val / 1_000).toFixed(0)}K`;
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
    maximumFractionDigits: 0,
  }).format(val);
};

export function TrialValueTracker() {
  const { session } = useAuth();
  const { planInfo } = usePlan();

  const isTrial = planInfo?.plan_id === "free_trial";
  const daysRemaining = planInfo?.trial_expires_at
    ? Math.max(0, Math.ceil((new Date(planInfo.trial_expires_at).getTime() - Date.now()) / 86_400_000))
    : 0;

  const { data } = useSWR<TrialStats>(
    isTrial && session?.access_token ? "/api/analytics?endpoint=trial-value" : null,
    async (url: string) => {
      const res = await fetch(url, {
        headers: { Authorization: `Bearer ${session!.access_token}` },
      });
      if (!res.ok) throw new Error("fetch_failed");
      return res.json();
    },
    {
      revalidateOnFocus: false,
      dedupingInterval: 300_000, // 5 min
      errorRetryCount: 1,
    }
  );

  if (!isTrial || !data || data.total_value === 0) return null;

  return (
    <div
      className="flex items-center gap-3 px-4 py-2.5 rounded-xl bg-gradient-to-r from-emerald-50 to-blue-50 dark:from-emerald-900/20 dark:to-blue-900/20 border border-emerald-200/60 dark:border-emerald-800/40"
      data-testid="trial-value-tracker"
    >
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-emerald-100 dark:bg-emerald-800 flex items-center justify-center">
        <svg className="w-4 h-4 text-emerald-600 dark:text-emerald-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
        </svg>
      </div>
      <div className="flex items-center gap-2 text-sm flex-wrap">
        <span className="font-bold text-emerald-700 dark:text-emerald-300">
          {formatCompact(data.total_value)} analisados
        </span>
        <span className="text-[var(--ink-muted)]">|</span>
        <span className="text-[var(--ink-secondary)]">
          {data.total_opportunities} oportunidades
        </span>
        {daysRemaining > 0 && (
          <>
            <span className="text-[var(--ink-muted)]">|</span>
            <span className="text-[var(--ink-secondary)]">
              {daysRemaining} {daysRemaining === 1 ? "dia restante" : "dias restantes"}
            </span>
          </>
        )}
      </div>
    </div>
  );
}
