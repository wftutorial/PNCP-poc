"use client";

interface OnboardingEmptyStateProps {
  onAdjustFilters: () => void;
}

export function OnboardingEmptyState({ onAdjustFilters }: OnboardingEmptyStateProps) {
  return (
    <div className="mb-4 p-6 rounded-lg bg-[var(--surface-1)] border border-[var(--border)] text-center">
      <svg className="w-12 h-12 mx-auto mb-3 text-[var(--ink-secondary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
      <h3 className="text-lg font-semibold text-[var(--ink)] mb-2">
        Sua análise foi concluída
      </h3>
      <p className="text-sm text-[var(--ink-secondary)] mb-4 max-w-md mx-auto">
        Não encontramos oportunidades compatíveis no período selecionado. Isso acontece em análises mais específicas — e pode mudar nos próximos dias.
      </p>
      <div className="space-y-2 text-sm text-[var(--ink-secondary)] mb-4">
        <p>Para ampliar resultados, tente:</p>
        <ul className="list-disc list-inside text-left max-w-sm mx-auto space-y-1">
          <li>Incluir estados vizinhos</li>
          <li>Ampliar a faixa de valor estimado</li>
          <li>Estender o período para 15 ou 30 dias</li>
        </ul>
      </div>
      <button
        onClick={onAdjustFilters}
        className="px-4 py-2 rounded-lg bg-[var(--brand-blue)] text-white text-sm font-medium hover:bg-[var(--brand-blue-hover)] transition-colors"
      >
        Refinar análise
      </button>
    </div>
  );
}
