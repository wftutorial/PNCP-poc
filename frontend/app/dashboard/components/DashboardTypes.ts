// Shared types for dashboard components

export interface AnalyticsSummary {
  total_searches: number;
  total_downloads: number;
  total_opportunities: number;
  total_value_discovered: number;
  estimated_hours_saved: number;
  avg_results_per_search: number;
  success_rate: number;
  member_since: string;
}

export interface TimeSeriesPoint {
  label: string;
  searches: number;
  opportunities: number;
  value: number;
}

export interface DimensionItem {
  name: string;
  count: number;
  value: number;
}

export interface TopDimensions {
  top_ufs: DimensionItem[];
  top_sectors: DimensionItem[];
}

export type Period = "day" | "week" | "month";

// CRIT-018 AC4/AC5: Per-section error flags for independent failure handling
export interface DashboardData {
  summary: AnalyticsSummary | null;
  timeSeries: TimeSeriesPoint[];
  dimensions: TopDimensions | null;
  summaryError?: boolean;
  timeSeriesError?: boolean;
  dimensionsError?: boolean;
}
