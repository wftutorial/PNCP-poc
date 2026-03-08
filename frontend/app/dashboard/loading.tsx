/**
 * DEBT-003 FE-002: Streaming loading skeleton for /dashboard route.
 * Matches stats cards (3-col grid) + chart area layout to minimize CLS.
 */
export default function DashboardLoading() {
  return (
    <div
      className="max-w-7xl mx-auto px-4 sm:px-6 py-6 animate-fade-in"
      data-testid="dashboard-loading"
    >
      {/* Page title */}
      <Shimmer className="h-8 w-40 rounded-button mb-6" />

      {/* Stats cards row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="rounded-card border border-[var(--border)] bg-[var(--surface-0)] p-5 space-y-3"
          >
            <Shimmer className="h-4 w-24 rounded" />
            <Shimmer className="h-8 w-20 rounded" />
            <Shimmer className="h-3 w-32 rounded" />
          </div>
        ))}
      </div>

      {/* Charts area */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Line chart skeleton */}
        <div className="rounded-card border border-[var(--border)] bg-[var(--surface-0)] p-5">
          <Shimmer className="h-5 w-36 rounded mb-4" />
          <Shimmer className="h-48 w-full rounded" />
        </div>

        {/* Pie chart skeleton */}
        <div className="rounded-card border border-[var(--border)] bg-[var(--surface-0)] p-5">
          <Shimmer className="h-5 w-36 rounded mb-4" />
          <Shimmer className="h-48 w-full rounded" />
        </div>
      </div>

      {/* Bottom section: top UFs + sectors */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {[1, 2].map((i) => (
          <div
            key={i}
            className="rounded-card border border-[var(--border)] bg-[var(--surface-0)] p-5 space-y-3"
          >
            <Shimmer className="h-5 w-32 rounded" />
            {[1, 2, 3, 4, 5].map((j) => (
              <div key={j} className="flex items-center gap-3">
                <Shimmer className="h-4 w-8 rounded" />
                <Shimmer className="h-4 flex-1 rounded" />
                <Shimmer className="h-4 w-16 rounded" />
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

function Shimmer({ className }: { className?: string }) {
  return (
    <div
      className={`relative overflow-hidden bg-[var(--surface-1)] ${className ?? ""}`}
    >
      <div className="absolute inset-0 -translate-x-full animate-shimmer bg-gradient-to-r from-transparent via-white/10 to-transparent" />
    </div>
  );
}
