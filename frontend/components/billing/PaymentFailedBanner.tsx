"use client";

import { usePlan } from "../../hooks/usePlan";
import { useAuth } from "../../app/components/AuthProvider";
import { useState, useEffect, useRef } from "react";

/**
 * STORY-309 AC12 + AC15: Payment failed banner with 3 urgency levels + recovery banner.
 *
 * AC12 - 3 urgency levels:
 *   Level 1 (recent, 0-7 days / active_retries + days_since_failure < 8): Yellow, informative
 *   Level 2 (critical, 7-14 days / active_retries + days_since_failure >= 8): Red, countdown
 *   Level 3 (grace period / dunning_phase === "grace_period"): Dark red, access limited
 *
 * AC15 - Recovery banner:
 *   Green banner shown when subscription_status transitions past_due → active.
 *   Fades out after 5s.
 */
export function PaymentFailedBanner() {
  const { planInfo } = usePlan();
  const { session } = useAuth();
  const [loading, setLoading] = useState(false);
  const [showRecovery, setShowRecovery] = useState(false);
  const [fadeOut, setFadeOut] = useState(false);
  const prevStatusRef = useRef<string | null>(null);

  // AC15: Detect recovery (past_due → active)
  useEffect(() => {
    if (!planInfo) return;
    const currentStatus = planInfo.subscription_status;
    const prevStatus = prevStatusRef.current;

    if (prevStatus === "past_due" && currentStatus === "active") {
      setShowRecovery(true);
      setFadeOut(false);
      const fadeTimer = setTimeout(() => setFadeOut(true), 4000);
      const hideTimer = setTimeout(() => setShowRecovery(false), 5000);
      return () => {
        clearTimeout(fadeTimer);
        clearTimeout(hideTimer);
      };
    }

    prevStatusRef.current = currentStatus;
  }, [planInfo?.subscription_status]);

  const handleUpdateCard = async () => {
    if (!session?.access_token) return;
    setLoading(true);
    try {
      const response = await fetch("/api/billing-portal", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${session.access_token}`,
          "Content-Type": "application/json",
        },
      });
      if (response.ok) {
        const data = await response.json();
        window.open(data.url, "_blank");
      }
    } catch (error) {
      console.error("Failed to open billing portal:", error);
    } finally {
      setLoading(false);
    }
  };

  // AC15: Recovery banner (green, fades out)
  if (showRecovery) {
    return (
      <div
        role="status"
        data-testid="payment-recovered-banner"
        className={`fixed top-0 left-0 right-0 z-[9999] bg-green-50 border-b-2 border-green-400 px-4 py-3 shadow-lg transition-opacity duration-1000 ${fadeOut ? "opacity-0" : "opacity-100"}`}
      >
        <div className="max-w-4xl mx-auto flex items-center gap-3">
          <svg
            className="w-5 h-5 text-green-600 flex-shrink-0"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M5 13l4 4L19 7"
            />
          </svg>
          <p className="text-sm text-green-800 font-medium">
            Pagamento restaurado com sucesso! Seu acesso está ativo novamente.
          </p>
        </div>
      </div>
    );
  }

  // Only show when past_due
  if (!planInfo || planInfo.subscription_status !== "past_due") return null;

  // Determine urgency level
  const dunningPhase = planInfo?.dunning_phase || "active_retries";
  const daysSinceFailure: number = planInfo?.days_since_failure ?? 0;

  // Calculate days remaining in 21-day window
  const daysRemaining = Math.max(0, 21 - daysSinceFailure);

  let bgClass: string;
  let borderClass: string;
  let iconColor: string;
  let textColor: string;
  let buttonBg: string;
  let message: string;
  let testId: string;

  if (dunningPhase === "grace_period") {
    // Level 3: Grace period (dark red)
    bgClass = "bg-red-100";
    borderClass = "border-red-600";
    iconColor = "text-red-700";
    textColor = "text-red-900";
    buttonBg = "bg-red-700 hover:bg-red-800";
    message = `Acesso limitado — ${daysRemaining} ${daysRemaining === 1 ? "dia restante" : "dias restantes"} para regularizar pagamento`;
    testId = "payment-failed-banner-grace";
  } else if (daysSinceFailure >= 8) {
    // Level 2: Critical (red)
    bgClass = "bg-red-50";
    borderClass = "border-red-400";
    iconColor = "text-red-600";
    textColor = "text-red-800";
    buttonBg = "bg-red-600 hover:bg-red-700";
    message = `Falha no pagamento — ${daysRemaining} ${daysRemaining === 1 ? "dia restante" : "dias restantes"} para regularizar`;
    testId = "payment-failed-banner-critical";
  } else {
    // Level 1: Recent (yellow)
    bgClass = "bg-amber-50";
    borderClass = "border-amber-400";
    iconColor = "text-amber-600";
    textColor = "text-amber-800";
    buttonBg = "bg-amber-600 hover:bg-amber-700";
    message =
      "Falha no pagamento. Atualize sua forma de pagamento para evitar interrupções.";
    testId = "payment-failed-banner-recent";
  }

  return (
    <div
      role="alert"
      aria-live="assertive"
      className={`fixed top-0 left-0 right-0 z-[9999] ${bgClass} border-b-2 ${borderClass} px-4 py-3 shadow-lg`}
      data-testid={testId}
    >
      <div className="max-w-4xl mx-auto flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <svg
            className={`w-5 h-5 ${iconColor} flex-shrink-0`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"
            />
          </svg>
          <p className={`text-sm ${textColor} font-medium`}>{message}</p>
        </div>
        <button
          onClick={handleUpdateCard}
          disabled={loading}
          className={`inline-flex items-center px-4 py-1.5 ${buttonBg} text-white text-sm font-medium rounded-md transition-colors whitespace-nowrap disabled:opacity-50`}
        >
          {loading ? "Abrindo..." : "Atualizar Pagamento"}
        </button>
      </div>
    </div>
  );
}
