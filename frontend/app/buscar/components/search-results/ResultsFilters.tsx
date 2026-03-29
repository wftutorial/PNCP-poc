"use client";

import type { StatusLicitacao } from "../StatusFilter";

const STATUS_LABELS: Record<StatusLicitacao, string> = {
  recebendo_proposta: "Licitações abertas",
  em_julgamento: "Em Julgamento",
  encerrada: "Encerradas",
  todos: "Todas as licitações",
};

interface ResultsFiltersProps {
  ufsSelecionadas: Set<string>;
  searchMode: "setor" | "termos";
  sectorName: string;
  status?: StatusLicitacao;
}

/**
 * TD-007 AC6: ResultsFilters — inline filter chips, active filters display.
 * Shows the active filter chips for UFs, search mode, and sector.
 */
export function ResultsFilters({
  ufsSelecionadas,
  searchMode,
  sectorName,
  status = "recebendo_proposta",
}: ResultsFiltersProps) {
  return (
    <div className="flex flex-wrap items-center gap-2 text-sm text-ink-secondary">
      <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
      </svg>
      <span className="font-medium text-ink">Filtros ativos:</span>
      <span className="inline-flex items-center px-2 py-0.5 rounded-full bg-brand-blue-subtle text-brand-navy text-xs font-medium">
        {ufsSelecionadas.size === 27 ? '27 UFs (todo o Brasil)' : `${ufsSelecionadas.size} UF${ufsSelecionadas.size !== 1 ? 's' : ''}`}
      </span>
      <span className="text-ink-faint">•</span>
      <span className="inline-flex items-center px-2 py-0.5 rounded-full bg-brand-blue-subtle text-brand-navy text-xs font-medium">
        {STATUS_LABELS[status]}
      </span>
      {searchMode === 'setor' && (
        <>
          <span className="text-ink-faint">•</span>
          <span className="inline-flex items-center px-2 py-0.5 rounded-full bg-brand-blue-subtle text-brand-navy text-xs font-medium">
            {sectorName}
          </span>
        </>
      )}
    </div>
  );
}
