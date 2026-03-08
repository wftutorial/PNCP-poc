/**
 * DEBT-003 FE-002: Streaming loading skeleton for /buscar route.
 * Matches SearchForm + results area layout to minimize CLS.
 */
export default function BuscarLoading() {
  return (
    <div
      className="max-w-7xl mx-auto px-4 sm:px-6 py-6 animate-fade-in"
      data-testid="buscar-loading"
    >
      {/* Search form skeleton */}
      <div className="mb-6 space-y-4">
        {/* Header row: title + action buttons */}
        <div className="flex items-center justify-between">
          <Shimmer className="h-8 w-48 rounded-button" />
          <div className="flex gap-2">
            <Shimmer className="h-9 w-24 rounded-button" />
            <Shimmer className="h-9 w-24 rounded-button" />
          </div>
        </div>

        {/* Filter bar */}
        <div className="rounded-card border border-[var(--border)] bg-[var(--surface-0)] p-4 space-y-4">
          {/* Sector + search mode row */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Shimmer className="h-10 w-full rounded-input" />
            <Shimmer className="h-10 w-full rounded-input" />
          </div>

          {/* UF grid skeleton */}
          <div className="grid grid-cols-9 gap-1.5">
            {Array.from({ length: 27 }, (_, i) => (
              <Shimmer key={i} className="h-8 rounded" />
            ))}
          </div>

          {/* Date range + search button */}
          <div className="flex flex-col sm:flex-row gap-4 items-end">
            <Shimmer className="h-10 w-full sm:w-40 rounded-input" />
            <Shimmer className="h-10 w-full sm:w-40 rounded-input" />
            <Shimmer className="h-11 w-full sm:w-32 rounded-button" />
          </div>
        </div>
      </div>

      {/* Results skeleton */}
      <div className="space-y-4" role="status" aria-label="Carregando busca">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="rounded-card border border-[var(--border)] bg-[var(--surface-0)] p-5 space-y-3"
          >
            <Shimmer className="h-5 w-3/4 rounded" />
            <Shimmer className="h-4 w-1/2 rounded" />
            <div className="flex gap-3">
              <Shimmer className="h-6 w-16 rounded-full" />
              <Shimmer className="h-6 w-20 rounded-full" />
              <Shimmer className="h-6 w-14 rounded-full" />
            </div>
            <Shimmer className="h-4 w-full rounded" />
            <Shimmer className="h-4 w-2/3 rounded" />
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
