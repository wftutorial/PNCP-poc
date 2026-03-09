"use client";

import { memo } from "react";
import { ErrorStateWithRetry } from "../../../components/ErrorStateWithRetry";
import { formatCurrencyBR } from "../../../lib/format-currency";
import type { AnalyticsSummary } from "./DashboardTypes";

// SAB-012 AC5: PT-BR currency formatting with abbreviations (bi/mi)
const formatCurrency = formatCurrencyBR;

function formatNumber(val: number): string {
  return new Intl.NumberFormat("pt-BR").format(val);
}

// DEBT-013 FE-014: React.memo to prevent unnecessary re-renders
const StatCard = memo(function StatCard({
  icon,
  label,
  value,
  subtitle,
  accent = false,
  tooltip,
}: {
  icon: string;
  label: string;
  value: string;
  subtitle?: string;
  accent?: boolean;
  tooltip?: string;
}) {
  return (
    <div
      className={`p-5 rounded-card border transition-colors ${
        accent
          ? "bg-[var(--brand-blue-subtle)] border-[var(--border-accent)]"
          : "bg-[var(--surface-0)] border-[var(--border)]"
      }`}
      title={tooltip}
    >
      <div className="flex items-start justify-between mb-3">
        <span className="text-2xl">{icon}</span>
      </div>
      <p className="text-2xl font-display font-bold text-[var(--ink)]">{value}</p>
      <p className="text-sm text-[var(--ink-secondary)] mt-1">{label}</p>
      {subtitle && (
        <p className="text-xs text-[var(--ink-muted)] mt-1">{subtitle}</p>
      )}
    </div>
  );
});

export function DashboardStatCards({
  summary,
  summaryError,
  onRetry,
}: {
  summary: AnalyticsSummary | null;
  summaryError: boolean;
  onRetry: () => void;
}) {
  if (summaryError) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4 mb-8">
        <div
          className="col-span-full bg-[var(--surface-0)] border border-[var(--border)] rounded-card"
          data-testid="summary-error"
        >
          <ErrorStateWithRetry
            message={`Dados indisponíveis.`}
            onRetry={onRetry}
            compact
          />
        </div>
      </div>
    );
  }

  if (!summary) return null;

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4 mb-8">
      <StatCard
        icon={"\uD83D\uDD0D"}
        label="Análises realizadas"
        value={formatNumber(summary.total_searches)}
      />
      <StatCard
        icon={"\uD83D\uDCCB"}
        label="Oportunidades encontradas"
        value={formatNumber(summary.total_opportunities)}
        subtitle={`~${summary.avg_results_per_search} por análise`}
      />
      <StatCard
        icon={"\uD83D\uDCB0"}
        label="Valor total descoberto"
        value={formatCurrency(summary.total_value_discovered)}
        accent
      />
      <StatCard
        icon={"\u23F1\uFE0F"}
        label="Horas economizadas"
        value={`${formatNumber(summary.estimated_hours_saved)}h`}
        subtitle="vs análise manual em portais"
        tooltip={`Estimativa: ${formatNumber(summary.total_searches)} análises × 2h por análise manual em portais governamentais`}
      />
      <StatCard
        icon={"\u2705"}
        label="Taxa de sucesso"
        value={`${summary.success_rate}%`}
        subtitle={`${summary.total_downloads} com resultados`}
      />
    </div>
  );
}
