"use client";

import { useState, useCallback, useEffect } from "react";
import { useAuth } from "../components/AuthProvider";
import { useAnalytics } from "../../hooks/useAnalytics";
import { useBackendStatusContext } from "../../components/BackendStatusIndicator";
import { useFetchWithBackoff } from "../../hooks/useFetchWithBackoff";
import { useProfileCompleteness } from "../../hooks/useProfileCompleteness";
import { PageHeader } from "../../components/PageHeader";
import { AuthLoadingScreen } from "../../components/AuthLoadingScreen";
import { TrialUpsellCTA } from "../../components/billing/TrialUpsellCTA";
import { usePlan } from "../../hooks/usePlan";
import { useIsMobile } from "../../hooks/useIsMobile";
import { formatCurrencyBR } from "../../lib/format-currency";

import { DashboardStatCards } from "./components/DashboardStatCards";
import { DashboardTimeSeriesChart } from "./components/DashboardTimeSeriesChart";
import { DashboardDimensionsWidget } from "./components/DashboardDimensionsWidget";
import { DashboardQuickLinks } from "./components/DashboardQuickLinks";
import {
  DashboardProfileHeaderControls,
  DashboardProfileSection,
} from "./components/DashboardProfileSection";
import {
  DashboardFullPageError,
  DashboardRetryingState,
  DashboardLoadingSkeleton,
  DashboardNotAuthenticated,
  DashboardEmptyState,
  DashboardStaleBanner,
} from "./components/DashboardErrorStates";
import { DashboardViewToggle } from "./components/DashboardViewToggle";
import { useDashboardDerivedData } from "./components/useDashboardDerivedData";
import type { DashboardData, Period } from "./components/DashboardTypes";

// UX-406: Feature flag — organizations/teams not yet implemented in backend
const ORGS_ENABLED = process.env.NEXT_PUBLIC_ORGS_ENABLED === "true";

const LOADING_TIMEOUT_MS = 10_000;

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("pt-BR", {
    day: "2-digit", month: "long", year: "numeric",
  });
}

export default function DashboardPage() {
  const { session, loading: authLoading } = useAuth();
  const { trackEvent } = useAnalytics();
  const { status: backendStatus } = useBackendStatusContext();
  const { planInfo } = usePlan();
  const isMobile = useIsMobile();

  const [period, setPeriod] = useState<Period>("week");
  const [viewMode, setViewMode] = useState<"personal" | "team">("personal");
  const [userOrg, setUserOrg] = useState<{ id: string; name: string; user_role: string } | null>(null);
  const [teamData, setTeamData] = useState<DashboardData | null>(null);
  const [teamLoading, setTeamLoading] = useState(false);

  // STORY-260: Profile completeness (FE-007: SWR)
  // Local override allows ProfileCompletionPrompt to show immediate feedback;
  // SWR revalidates on next render cycle.
  const { completenessPct: swrProfilePct } = useProfileCompleteness();
  const [profilePctOverride, setProfilePctOverride] = useState<number | null>(null);
  const profilePct = profilePctOverride ?? swrProfilePct;

  // AC19: Fetch org membership — show team toggle only for owners/admins
  // UX-406: Gated by ORGS_ENABLED — backend endpoint doesn't exist yet
  useEffect(() => {
    if (!ORGS_ENABLED || !session?.access_token) return;
    fetch("/api/organizations/me", {
      headers: { Authorization: `Bearer ${session.access_token}` },
    })
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data?.organization && ["owner", "admin"].includes(data.organization.user_role)) {
          setUserOrg(data.organization);
        }
      })
      .catch(() => {});
  }, [session?.access_token]);

  // AC19: Fetch team dashboard data when switching to team view
  // UX-406: Gated by ORGS_ENABLED — backend endpoint doesn't exist yet
  useEffect(() => {
    if (!ORGS_ENABLED || viewMode !== "team" || !userOrg || !session?.access_token) return;
    setTeamLoading(true);
    fetch(`/api/organizations/${userOrg.id}/dashboard`, {
      headers: { Authorization: `Bearer ${session.access_token}` },
    })
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data) {
          setTeamData({
            summary: data.summary ?? null,
            timeSeries: data.time_series ?? [],
            dimensions: data.dimensions ?? null,
          });
        }
      })
      .catch(() => {})
      .finally(() => setTeamLoading(false));
  }, [viewMode, userOrg, session?.access_token]);

  const fetchAnalytics = useCallback(
    async (endpoint: string, params?: Record<string, string>, signal?: AbortSignal) => {
      if (!session?.access_token) return null;
      const searchParams = new URLSearchParams(params);
      searchParams.set("endpoint", endpoint);
      const res = await fetch(`/api/analytics?${searchParams}`, {
        headers: { Authorization: `Bearer ${session.access_token}` },
        signal,
      });
      if (!res.ok) throw new Error("Erro ao carregar dados");
      return res.json();
    },
    [session?.access_token]
  );

  // CRIT-018 AC1-AC6: Fetch function consumed by useFetchWithBackoff
  // AC4/AC5: Use Promise.allSettled so individual sections can fail independently
  const fetchDashboard = useCallback(
    async (signal: AbortSignal): Promise<DashboardData> => {
      const results = await Promise.allSettled([
        fetchAnalytics("summary", undefined, signal),
        fetchAnalytics("searches-over-time", { period, range_days: "90" }, signal),
        fetchAnalytics("top-dimensions", { limit: "7" }, signal),
      ]);
      trackEvent("dashboard_viewed", { period });
      return {
        summary: results[0].status === "fulfilled" ? results[0].value : null,
        timeSeries: results[1].status === "fulfilled" ? (results[1].value?.data || []) : [],
        dimensions: results[2].status === "fulfilled" ? results[2].value : null,
        summaryError: results[0].status === "rejected",
        timeSeriesError: results[1].status === "rejected",
        dimensionsError: results[2].status === "rejected",
      };
    },
    [period, fetchAnalytics, trackEvent]
  );

  const {
    data,
    loading,
    error,
    retryCount,
    hasExhaustedRetries,
    manualRetry,
  } = useFetchWithBackoff<DashboardData>(fetchDashboard, {
    enabled: !authLoading && !!session && backendStatus !== "offline",
    maxRetries: 3,
    initialDelayMs: 2000,
    maxDelayMs: 30000,
    timeoutMs: LOADING_TIMEOUT_MS,
  });

  // AC4/AC5: Per-section error flags (always from personal data)
  const summaryError = data?.summaryError ?? false;
  const timeSeriesError = data?.timeSeriesError ?? false;
  const dimensionsError = data?.dimensionsError ?? false;

  // AC19: Active dataset — personal or team view
  const activeData = viewMode === "team" && teamData ? teamData : data;
  const summary = activeData?.summary ?? null;
  const timeSeries = activeData?.timeSeries ?? [];
  const dimensions = activeData?.dimensions ?? null;

  const { ufPieData, sectorChartData, handleExportCSV } = useDashboardDerivedData(
    summary,
    dimensions
  );

  // ── Auth guard ──────────────────────────────────────────────────────────────

  if (authLoading) return <AuthLoadingScreen />;
  if (!session) return <DashboardNotAuthenticated />;

  // ── CRIT-018 AC8 / CRIT-031: Error states ──────────────────────────────────

  const allSectionsFailed = summaryError && timeSeriesError && dimensionsError;

  if (error && hasExhaustedRetries && !data) {
    return <DashboardFullPageError onRetry={manualRetry} />;
  }
  if (data && allSectionsFailed) {
    return <DashboardFullPageError onRetry={manualRetry} />;
  }
  if (error && !hasExhaustedRetries && !data) {
    return <DashboardRetryingState retryCount={retryCount} />;
  }

  // ── Loading skeleton ────────────────────────────────────────────────────────

  if (loading && !data) return <DashboardLoadingSkeleton />;

  // ── Empty state ─────────────────────────────────────────────────────────────

  if (summary && summary.total_searches === 0) {
    return (
      <div className="min-h-screen bg-[var(--canvas)]">
        <PageHeader title="Dashboard" />
        <div className="max-w-6xl mx-auto py-8 px-4">
          <DashboardEmptyState />
        </div>
      </div>
    );
  }

  // ── Dashboard content ───────────────────────────────────────────────────────

  return (
    <div className="min-h-screen bg-[var(--canvas)]">
      {error && hasExhaustedRetries && data && (
        <DashboardStaleBanner onRetry={manualRetry} />
      )}

      <PageHeader
        title="Dashboard"
        extraControls={
          <>
            <DashboardProfileHeaderControls profilePct={profilePct} />
            <button
              onClick={handleExportCSV}
              className="hidden sm:flex px-3 py-1.5 text-sm border border-[var(--border)] rounded-button
                         text-[var(--ink-secondary)] hover:bg-[var(--surface-1)] transition-colors items-center gap-1.5"
            >
              <svg aria-hidden="true" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              CSV
            </button>
          </>
        }
      />

      <div className="max-w-6xl mx-auto py-8 px-4">
        {ORGS_ENABLED && (
          <DashboardViewToggle
            viewMode={viewMode}
            setViewMode={setViewMode}
            userOrg={userOrg}
            teamLoading={teamLoading}
          />
        )}

        {summary && viewMode === "personal" && (
          <p className="text-sm text-[var(--ink-muted)] mb-6">
            Membro desde {formatDate(summary.member_since)}
          </p>
        )}
        {ORGS_ENABLED && viewMode === "team" && userOrg && (
          <p className="text-sm text-[var(--ink-muted)] mb-6">
            Dados agregados da equipe — {userOrg.name}
          </p>
        )}

        <DashboardProfileSection
          session={session}
          profilePct={profilePct}
          onProfileUpdated={setProfilePctOverride}
        />

        <DashboardStatCards
          summary={summary}
          summaryError={summaryError}
          onRetry={manualRetry}
        />

        {/* STORY-312 AC4: Dashboard CTA for trial users with >= 3 searches */}
        {summary && summary.total_searches >= 3 && (
          <div className="mb-8">
            <TrialUpsellCTA
              variant="dashboard"
              planId={planInfo?.plan_id}
              subscriptionStatus={planInfo?.subscription_status}
              contextData={{
                valor: formatCurrencyBR(summary.total_value_discovered).replace("R$ ", ""),
              }}
            />
          </div>
        )}

        <DashboardTimeSeriesChart
          timeSeries={timeSeries}
          timeSeriesError={timeSeriesError}
          period={period}
          setPeriod={setPeriod}
          isMobile={isMobile}
          onRetry={manualRetry}
        />

        <DashboardDimensionsWidget
          dimensions={dimensions}
          dimensionsError={dimensionsError}
          ufPieData={ufPieData}
          sectorChartData={sectorChartData}
          isMobile={isMobile}
          onRetry={manualRetry}
        />

        <DashboardQuickLinks />
      </div>
    </div>
  );
}
