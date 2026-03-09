/**
 * DEBT-003 FE-002: Streaming loading skeleton for /pipeline route.
 * Matches kanban layout (5 columns) to minimize CLS.
 */
export default function PipelineLoading() {
  const columns = ["Descoberta", "Analise", "Proposta", "Negociacao", "Concluido"];

  return (
    <div
      className="max-w-7xl mx-auto px-4 sm:px-6 py-6 animate-fade-in"
      data-testid="pipeline-loading"
      role="status"
      aria-busy="true"
      aria-label="Carregando pipeline"
    >
      {/* Page header */}
      <div className="flex items-center justify-between mb-6">
        <Shimmer className="h-8 w-32 rounded-button" />
        <Shimmer className="h-9 w-36 rounded-button" />
      </div>

      {/* Kanban columns */}
      <div className="flex gap-4 overflow-x-auto pb-4">
        {columns.map((col) => (
          <div
            key={col}
            className="flex-shrink-0 w-64 rounded-card border border-[var(--border)] bg-[var(--surface-0)] p-3"
          >
            {/* Column header */}
            <div className="flex items-center justify-between mb-3">
              <Shimmer className="h-5 w-24 rounded" />
              <Shimmer className="h-5 w-6 rounded-full" />
            </div>

            {/* Card skeletons (2-3 per column) */}
            <div className="space-y-3">
              {Array.from({ length: col === "Descoberta" ? 3 : 2 }, (_, i) => (
                <div
                  key={i}
                  className="rounded-lg border border-[var(--border)] bg-[var(--surface-1)] p-3 space-y-2"
                >
                  <Shimmer className="h-4 w-full rounded" />
                  <Shimmer className="h-3 w-2/3 rounded" />
                  <div className="flex gap-2">
                    <Shimmer className="h-5 w-10 rounded-full" />
                    <Shimmer className="h-5 w-16 rounded-full" />
                  </div>
                </div>
              ))}
            </div>
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
