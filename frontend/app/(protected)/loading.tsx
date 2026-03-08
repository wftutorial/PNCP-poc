/**
 * DEBT-003 FE-002: Streaming loading skeleton for protected layout.
 * Shows AppHeader skeleton + generic content area while auth resolves.
 */
export default function ProtectedLoading() {
  return (
    <div
      className="min-h-screen bg-[var(--canvas)] animate-fade-in"
      data-testid="protected-loading"
    >
      {/* AppHeader skeleton */}
      <header className="border-b border-[var(--border)] bg-[var(--surface-0)]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
          {/* Logo */}
          <Shimmer className="h-7 w-28 rounded" />

          {/* Right side: nav items + avatar */}
          <div className="flex items-center gap-3">
            <Shimmer className="h-8 w-8 rounded-full hidden sm:block" />
            <Shimmer className="h-8 w-8 rounded-full hidden sm:block" />
            <Shimmer className="h-8 w-8 rounded-full" />
          </div>
        </div>
      </header>

      {/* Content area skeleton */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-6">
        {/* Breadcrumb skeleton */}
        <div className="flex items-center gap-2 mb-6">
          <Shimmer className="h-4 w-16 rounded" />
          <Shimmer className="h-4 w-4 rounded" />
          <Shimmer className="h-4 w-24 rounded" />
        </div>

        {/* Page title */}
        <Shimmer className="h-8 w-48 rounded-button mb-6" />

        {/* Content cards */}
        <div className="space-y-4" role="status" aria-label="Carregando pagina">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="rounded-card border border-[var(--border)] bg-[var(--surface-0)] p-5 space-y-3"
            >
              <Shimmer className="h-5 w-2/3 rounded" />
              <Shimmer className="h-4 w-full rounded" />
              <Shimmer className="h-4 w-1/2 rounded" />
            </div>
          ))}
        </div>
      </main>
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
