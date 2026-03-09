"use client";

import { useMemo } from "react";
import { UFS, UF_NAMES } from "../../../lib/constants/uf-names";

export const UF_REGIONS: Record<string, string[]> = {
  Norte: ["AC", "AP", "AM", "PA", "RO", "RR", "TO"],
  Nordeste: ["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"],
  "Centro-Oeste": ["DF", "GO", "MT", "MS"],
  Sudeste: ["ES", "MG", "RJ", "SP"],
  Sul: ["PR", "RS", "SC"],
};

export function UFMultiSelect({
  selected,
  onChange,
}: {
  selected: string[];
  onChange: (ufs: string[]) => void;
}) {
  const selectedSet = useMemo(() => new Set(selected), [selected]);

  const toggleUf = (uf: string) => {
    const newSet = new Set(selectedSet);
    if (newSet.has(uf)) newSet.delete(uf);
    else newSet.add(uf);
    onChange(Array.from(newSet));
  };

  const toggleRegion = (regionUfs: string[]) => {
    const allSelected = regionUfs.every((uf) => selectedSet.has(uf));
    const newSet = new Set(selectedSet);
    if (allSelected) {
      regionUfs.forEach((uf) => newSet.delete(uf));
    } else {
      regionUfs.forEach((uf) => newSet.add(uf));
    }
    onChange(Array.from(newSet));
  };

  const selectAll = () => onChange([...UFS]);
  const clearAll = () => onChange([]);

  return (
    <div>
      <div className="flex items-center justify-between mb-1.5">
        <label className="block text-sm font-medium text-[var(--ink)]">
          Estados (UFs)
        </label>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={selectAll}
            className="text-[11px] text-[var(--brand-blue)] hover:underline"
          >
            Todos
          </button>
          <button
            type="button"
            onClick={clearAll}
            className="text-[11px] text-[var(--ink-muted)] hover:underline"
          >
            Limpar
          </button>
        </div>
      </div>

      {/* Region quick-buttons */}
      <div className="flex flex-wrap gap-1.5 mb-2">
        {Object.entries(UF_REGIONS).map(([region, ufs]) => {
          const allSelected = ufs.every((uf) => selectedSet.has(uf));
          return (
            <button
              key={region}
              type="button"
              onClick={() => toggleRegion(ufs)}
              className={`px-2 py-0.5 rounded text-[11px] font-medium border transition-colors ${
                allSelected
                  ? "bg-[var(--brand-blue)] text-white border-[var(--brand-blue)]"
                  : "bg-[var(--surface-0)] text-[var(--ink-secondary)] border-[var(--border)] hover:border-[var(--brand-blue)]"
              }`}
            >
              {region}
            </button>
          );
        })}
      </div>

      {/* UF grid */}
      <div className="grid grid-cols-5 sm:grid-cols-7 md:grid-cols-9 gap-1">
        {UFS.map((uf) => (
          <label
            key={uf}
            className={`flex items-center justify-center px-1 py-1.5 rounded cursor-pointer text-xs font-medium transition-colors select-none ${
              selectedSet.has(uf)
                ? "bg-[var(--brand-blue)] text-white"
                : "bg-[var(--surface-1)] text-[var(--ink-secondary)] hover:bg-[var(--surface-2,var(--surface-1))] hover:text-[var(--ink)]"
            }`}
            title={UF_NAMES[uf]}
          >
            <input
              type="checkbox"
              checked={selectedSet.has(uf)}
              onChange={() => toggleUf(uf)}
              className="sr-only"
            />
            {uf}
          </label>
        ))}
      </div>
      {selected.length > 0 && (
        <p className="text-[11px] text-[var(--ink-muted)] mt-1">
          {selected.length} {selected.length === 1 ? "estado selecionado" : "estados selecionados"}
        </p>
      )}
    </div>
  );
}
