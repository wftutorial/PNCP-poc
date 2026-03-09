"use client";

import { useCallback, useMemo } from "react";
import { useAnalytics } from "../../../hooks/useAnalytics";
import { formatCurrencyBR } from "../../../lib/format-currency";
import { APP_NAME } from "../../../lib/config";
import { UF_NAMES } from "../../../lib/constants/uf-names";
import { getSectorDisplayName } from "../../../lib/constants/sector-names";
import type { AnalyticsSummary, TopDimensions, DimensionItem } from "./DashboardTypes";

// DEBT-012: References CSS vars defined in globals.css (--chart-1 … --chart-10)
const CHART_COLORS = [
  "var(--chart-1)", "var(--chart-2)", "var(--chart-3)", "var(--chart-4)", "var(--chart-5)",
  "var(--chart-6)", "var(--chart-7)", "var(--chart-8)", "var(--chart-9)", "var(--chart-10)",
];

export interface UfPieDatum {
  name: string;
  value: number;
  fill: string;
}

export type SectorChartDatum = DimensionItem & { name: string };

export function useDashboardDerivedData(
  summary: AnalyticsSummary | null,
  dimensions: TopDimensions | null
) {
  const { trackEvent } = useAnalytics();

  // UX-356 AC1-AC2: Map UF codes to display names for pie chart
  const ufPieData: UfPieDatum[] = useMemo(
    () =>
      dimensions?.top_ufs?.map((u, i) => ({
        name: UF_NAMES[u.name] || u.name,
        value: u.count,
        fill: CHART_COLORS[i % CHART_COLORS.length],
      })) || [],
    [dimensions]
  );

  // UX-356 AC1-AC2: Map sector slugs to display names
  const sectorChartData: SectorChartDatum[] = useMemo(
    () =>
      dimensions?.top_sectors?.map((s) => ({
        ...s,
        name: getSectorDisplayName(s.name),
      })) || [],
    [dimensions]
  );

  const handleExportCSV = useCallback(() => {
    if (!summary || !dimensions) return;
    const rows = [
      ["Metrica", "Valor"],
      ["Total de Análises", String(summary.total_searches)],
      ["Total de Downloads", String(summary.total_downloads)],
      ["Oportunidades Encontradas", String(summary.total_opportunities)],
      ["Valor Total Descoberto", String(summary.total_value_discovered)],
      ["Horas Economizadas", String(summary.estimated_hours_saved)],
      ["Taxa de Sucesso", `${summary.success_rate}%`],
      [""],
      ["Top UFs", "Análises", "Valor"],
      ...dimensions.top_ufs.map((u) => [u.name, String(u.count), String(u.value)]),
      [""],
      ["Top Setores", "Análises", "Valor"],
      ...dimensions.top_sectors.map((s) => [getSectorDisplayName(s.name), String(s.count), String(s.value)]),
    ];
    const csv = rows.map((r) => r.join(",")).join("\n");
    const blob = new Blob(["\uFEFF" + csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${APP_NAME.toLowerCase()}-analytics-${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    trackEvent("analytics_exported", { format: "csv" });
  }, [summary, dimensions, trackEvent]);

  return { ufPieData, sectorChartData, handleExportCSV };
}
