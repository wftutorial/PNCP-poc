/**
 * ProgressAnimation — Header spinner + descriptive phase label.
 * Extracted from EnhancedLoadingProgress. DEBT-FE-014.
 * DEBT-v3-S2 AC11: Phase labels replace static "Analisando oportunidades..."
 * DEBT-v3-S2 AC9: After 45s shows "Buscando em mais fontes..." with spinner
 */

interface ProgressAnimationProps {
  isDegraded?: boolean;
  /** DEBT-v3-S2 AC11: SSE stage name for phase label */
  sseStage?: string;
  /** DEBT-v3-S2 AC11: 0-100 progress for phase label fallback */
  progress?: number;
  /** DEBT-v3-S2 AC9: Whether search is "stuck" (>45s without result) */
  isStuck?: boolean;
}

/**
 * DEBT-v3-S2 AC11: Map progress/stage to descriptive phase label.
 * No numeric percentage is ever shown (AC12).
 */
function getPhaseLabel(sseStage?: string, progress?: number): string {
  // Prefer SSE stage when available
  if (sseStage) {
    switch (sseStage) {
      case 'connecting':
        return 'Conectando fontes...';
      case 'fetching':
        return 'Analisando editais...';
      case 'filtering':
        return 'Classificando relevância...';
      case 'llm':
        return 'Classificando relevância...';
      case 'excel':
      case 'complete':
        return 'Finalizando...';
      default:
        break;
    }
  }

  // Fallback: derive from progress percentage
  const p = progress ?? 0;
  if (p < 15) return 'Conectando fontes...';
  if (p < 60) return 'Analisando editais...';
  if (p < 75) return 'Classificando relevância...';
  return 'Finalizando...';
}

export function ProgressAnimation({ isDegraded = false, sseStage, progress, isStuck = false }: ProgressAnimationProps) {
  const label = isStuck
    ? 'Buscando em mais fontes, pode demorar...'
    : getPhaseLabel(sseStage, progress);

  return (
    <div className="flex items-center gap-3 mb-4">
      <svg
        className={`animate-spin h-6 w-6 ${isDegraded ? "text-amber-500" : "text-brand-blue"}`}
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
          fill="none"
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
      <p className="text-base sm:text-lg font-semibold text-ink" data-testid="progress-phase-label">
        {label}
      </p>
    </div>
  );
}
