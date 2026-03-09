"use client";

import dynamic from "next/dynamic";
import { ErrorStateWithRetry } from "../../../components/ErrorStateWithRetry";
import type { TimeSeriesPoint, Period } from "./DashboardTypes";

const ChartSkeleton = () => (
  <div className="h-64 bg-[var(--surface-1)] rounded-card animate-pulse" />
);

const TimeSeriesChart = dynamic(
  () => import("../DashboardCharts").then((mod) => mod.TimeSeriesChart),
  { ssr: false, loading: ChartSkeleton }
);

export function DashboardTimeSeriesChart({
  timeSeries,
  timeSeriesError,
  period,
  setPeriod,
  isMobile,
  onRetry,
}: {
  timeSeries: TimeSeriesPoint[];
  timeSeriesError: boolean;
  period: Period;
  setPeriod: (p: Period) => void;
  isMobile: boolean;
  onRetry: () => void;
}) {
  if (timeSeriesError) {
    return (
      <div
        className="bg-[var(--surface-0)] border border-[var(--border)] rounded-card p-6 mb-8"
        data-testid="timeseries-error"
      >
        <h2 className="text-lg font-display font-semibold text-[var(--ink)] mb-4">
          Buscas ao longo do tempo
        </h2>
        <ErrorStateWithRetry
          message={`Dados indisponíveis.`}
          onRetry={onRetry}
          compact
        />
      </div>
    );
  }

  return (
    <div className="bg-[var(--surface-0)] border border-[var(--border)] rounded-card p-6 mb-8">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-display font-semibold text-[var(--ink)]">
          Buscas ao longo do tempo
        </h2>
        <div className="flex bg-[var(--surface-1)] rounded-button p-0.5">
          {(["day", "week", "month"] as Period[]).map((p) => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`px-3 py-1 text-xs rounded-button transition-colors ${
                period === p
                  ? "bg-[var(--brand-blue)] text-white"
                  : "text-[var(--ink-secondary)] hover:text-[var(--ink)]"
              }`}
            >
              {p === "day" ? "Dia" : p === "week" ? "Semana" : `Mês`}
            </button>
          ))}
        </div>
      </div>

      {timeSeries.length > 0 ? (
        <TimeSeriesChart data={timeSeries} isMobile={isMobile} />
      ) : (
        <div className="h-64 flex items-center justify-center text-[var(--ink-muted)]">
          {`Sem dados para o período selecionado`}
        </div>
      )}
    </div>
  );
}
