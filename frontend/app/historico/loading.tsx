/**
 * DEBT-003 FE-002: Streaming loading skeleton for /historico route.
 * Matches session list layout (filter bar + session cards) to minimize CLS.
 */
export default function HistoricoLoading() {
  return (
    <div
      className="max-w-7xl mx-auto px-4 sm:px-6 py-6 animate-fade-in"
      data-testid="historico-loading"
    >
      {/* Page title */}
      <Shimmer className="h-8 w-36 rounded-button mb-6" />

      {/* Filter bar */}
      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <Shimmer className="h-10 w-full sm:w-48 rounded-input" />
        <Shimmer className="h-10 w-full sm:w-40 rounded-input" />
        <Shimmer className="h-10 w-full sm:w-32 rounded-input" />
      </div>

      {/* Session cards list */}
      <div className="space-y-4" role="status" aria-label="Carregando historico">
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className="rounded-card border border-[var(--border)] bg-[var(--surface-0)] p-5 space-y-3"
          >
            {/* Session header: sector + date + status */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Shimmer className="h-5 w-32 rounded" />
                <Shimmer className="h-5 w-16 rounded-full" />
              </div>
              <Shimmer className="h-4 w-24 rounded" />
            </div>

            {/* Session details */}
            <div className="flex flex-wrap gap-4">
              <Shimmer className="h-4 w-20 rounded" />
              <Shimmer className="h-4 w-28 rounded" />
              <Shimmer className="h-4 w-24 rounded" />
            </div>

            {/* UF badges */}
            <div className="flex flex-wrap gap-1.5">
              {Array.from({ length: 5 }, (_, j) => (
                <Shimmer key={j} className="h-6 w-10 rounded" />
              ))}
            </div>

            {/* Executive summary line */}
            <Shimmer className="h-4 w-full rounded" />
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
