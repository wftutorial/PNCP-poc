"use client";

import { useState, useEffect, useMemo, useCallback } from "react";
import { usePlan } from "../../../hooks/usePlan";
import { useTrialPhase } from "../../../hooks/useTrialPhase";
import { useAuth } from "../../components/AuthProvider";
import type { TrialValue } from "../constants/tour-steps";

export interface SearchBillingState {
  planInfo: ReturnType<typeof usePlan>["planInfo"];
  trialPhase: ReturnType<typeof useTrialPhase>["phase"];
  trialDaysRemaining: number | null;
  isTrialExpired: boolean;
  isGracePeriod: boolean;
  graceDaysRemaining: number;
  showTrialConversion: boolean;
  setShowTrialConversion: (show: boolean) => void;
  trialValue: TrialValue | null;
  trialValueLoading: boolean;
  fetchTrialValue: () => Promise<void>;
  showPaymentRecovery: boolean;
  setShowPaymentRecovery: (show: boolean) => void;
}

/**
 * DEBT-FE-001: Extracted from useSearchOrchestration (was lines ~47-101).
 * Owns all trial/billing/plan state used in the search page.
 */
export function useSearchBillingState(): SearchBillingState {
  const { session } = useAuth();
  const { planInfo } = usePlan();
  const { phase: trialPhase } = useTrialPhase();

  const [showTrialConversion, setShowTrialConversion] = useState(false);
  const [trialValue, setTrialValue] = useState<TrialValue | null>(null);
  const [trialValueLoading, setTrialValueLoading] = useState(false);

  const trialDaysRemaining = useMemo(() => {
    if (!planInfo?.trial_expires_at) return null;
    const expiryDate = new Date(planInfo.trial_expires_at);
    const now = new Date();
    const diffTime = expiryDate.getTime() - now.getTime();
    return Math.max(0, Math.ceil(diffTime / (1000 * 60 * 60 * 24)));
  }, [planInfo?.trial_expires_at]);

  const isTrialExpired = useMemo(() => {
    return planInfo?.plan_id === "free_trial" && planInfo?.subscription_status === "expired";
  }, [planInfo?.plan_id, planInfo?.subscription_status]);

  const isGracePeriod = useMemo(() => {
    return planInfo?.dunning_phase === "grace_period";
  }, [planInfo?.dunning_phase]);

  const graceDaysRemaining = useMemo(() => {
    if (!isGracePeriod || planInfo?.days_since_failure == null) return 0;
    return Math.max(0, 21 - planInfo.days_since_failure);
  }, [isGracePeriod, planInfo?.days_since_failure]);

  const [showPaymentRecovery, setShowPaymentRecovery] = useState(false);

  useEffect(() => {
    setShowPaymentRecovery(isGracePeriod);
  }, [isGracePeriod]);

  const fetchTrialValue = useCallback(async () => {
    if (!session?.access_token) return;
    setTrialValueLoading(true);
    try {
      const res = await fetch("/api/analytics?endpoint=trial-value", {
        headers: { Authorization: `Bearer ${session.access_token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setTrialValue(data);
      }
    } catch (err) {
      if (process.env.NODE_ENV !== "production")
        console.error("[GTM-010] Failed to fetch trial value:", err);
    } finally {
      setTrialValueLoading(false);
    }
  }, [session?.access_token]);

  useEffect(() => {
    if (isTrialExpired) {
      setShowTrialConversion(true);
      fetchTrialValue();
    }
  }, [isTrialExpired, fetchTrialValue]);

  return {
    planInfo,
    trialPhase,
    trialDaysRemaining,
    isTrialExpired,
    isGracePeriod,
    graceDaysRemaining,
    showTrialConversion,
    setShowTrialConversion,
    trialValue,
    trialValueLoading,
    fetchTrialValue,
    showPaymentRecovery,
    setShowPaymentRecovery,
  };
}
