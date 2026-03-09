"use client";

import { SECTOR_DISPLAY_NAMES } from "../../../lib/constants/sector-names";
import { UFS } from "../../../lib/constants/uf-names";
import type { AlertFormData } from "./types";

function formatCurrency(value: number | null): string {
  if (value === null || value === undefined) return "-";
  return value.toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  });
}

export function AlertPreview({ form }: { form: AlertFormData }) {
  return (
    <div className="mt-3 p-4 rounded-lg bg-[var(--surface-1)] border border-[var(--border)]">
      <h4 className="text-sm font-semibold text-[var(--ink)] mb-2">
        Preview: {form.name || "Sem nome"}
      </h4>
      <dl className="space-y-1.5 text-xs">
        {form.setor && (
          <div className="flex gap-2">
            <dt className="font-medium text-[var(--ink-secondary)] min-w-[80px]">Setor:</dt>
            <dd className="text-[var(--ink)]">
              {SECTOR_DISPLAY_NAMES[form.setor] || form.setor}
            </dd>
          </div>
        )}
        {form.ufs.length > 0 && (
          <div className="flex gap-2">
            <dt className="font-medium text-[var(--ink-secondary)] min-w-[80px]">UFs:</dt>
            <dd className="text-[var(--ink)]">
              {form.ufs.length === UFS.length
                ? "Todos os estados"
                : form.ufs.join(", ")}
            </dd>
          </div>
        )}
        {(form.valor_min || form.valor_max) && (
          <div className="flex gap-2">
            <dt className="font-medium text-[var(--ink-secondary)] min-w-[80px]">Valor:</dt>
            <dd className="text-[var(--ink)]">
              {form.valor_min
                ? formatCurrency(Number(form.valor_min))
                : "Sem min."}{" "}
              a{" "}
              {form.valor_max
                ? formatCurrency(Number(form.valor_max))
                : "Sem max."}
            </dd>
          </div>
        )}
        {form.keywords.length > 0 && (
          <div className="flex gap-2">
            <dt className="font-medium text-[var(--ink-secondary)] min-w-[80px]">Keywords:</dt>
            <dd className="text-[var(--ink)]">
              {form.keywords.map((kw) => `"${kw}"`).join(", ")}
            </dd>
          </div>
        )}
      </dl>
    </div>
  );
}
