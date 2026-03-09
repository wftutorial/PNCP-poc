"use client";

import { useState, memo } from "react";
import { Button } from "../../../components/ui/button";
import { SECTOR_DISPLAY_NAMES } from "../../../lib/constants/sector-names";
import type { Alert } from "./types";

function formatCurrency(value: number | null): string {
  if (value === null || value === undefined) return "-";
  return value.toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  });
}

export const AlertCard = memo(function AlertCard({
  alert,
  onToggle,
  onEdit,
  onDelete,
}: {
  alert: Alert;
  onToggle: (id: string, active: boolean) => void;
  onEdit: (alert: Alert) => void;
  onDelete: (id: string) => void;
}) {
  const [toggling, setToggling] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  const handleToggle = async () => {
    setToggling(true);
    await onToggle(alert.id, !alert.active);
    setToggling(false);
  };

  const handleDelete = async () => {
    setDeleting(true);
    await onDelete(alert.id);
    setDeleting(false);
    setShowConfirm(false);
  };

  const filterSummary: string[] = [];
  if (alert.filters.setor) {
    filterSummary.push(
      SECTOR_DISPLAY_NAMES[alert.filters.setor] || alert.filters.setor,
    );
  }
  if (alert.filters.ufs && alert.filters.ufs.length > 0) {
    if (alert.filters.ufs.length <= 3) {
      filterSummary.push(alert.filters.ufs.join(", "));
    } else {
      filterSummary.push(`${alert.filters.ufs.length} UFs`);
    }
  }
  if (alert.filters.valor_min !== null || alert.filters.valor_max !== null) {
    const parts: string[] = [];
    if (alert.filters.valor_min !== null) parts.push(`Min ${formatCurrency(alert.filters.valor_min)}`);
    if (alert.filters.valor_max !== null) parts.push(`Max ${formatCurrency(alert.filters.valor_max)}`);
    filterSummary.push(parts.join(" - "));
  }
  if (alert.filters.keywords && alert.filters.keywords.length > 0) {
    filterSummary.push(
      alert.filters.keywords.length === 1
        ? `"${alert.filters.keywords[0]}"`
        : `${alert.filters.keywords.length} palavras-chave`,
    );
  }

  return (
    <div
      className={`rounded-xl border transition-colors ${
        alert.active
          ? "border-[var(--brand-blue)]/30 bg-[var(--surface-0)]"
          : "border-[var(--border)] bg-[var(--surface-0)] opacity-70"
      }`}
      data-testid={`alert-card-${alert.id}`}
    >
      <div className="p-4 sm:p-5">
        {/* Header row: name + toggle */}
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="flex-1 min-w-0">
            <h3 className="text-base font-semibold text-[var(--ink)] truncate">
              {alert.name}
            </h3>
            <p className="text-xs text-[var(--ink-muted)] mt-0.5">
              Criado em{" "}
              {new Date(alert.created_at).toLocaleDateString("pt-BR")}
            </p>
          </div>

          {/* Active toggle */}
          <button
            onClick={handleToggle}
            disabled={toggling}
            className="relative flex-shrink-0"
            aria-label={alert.active ? "Desativar alerta" : "Ativar alerta"}
            data-testid={`alert-toggle-${alert.id}`}
          >
            <div
              className={`w-11 h-6 rounded-full transition-colors ${
                alert.active
                  ? "bg-[var(--brand-blue)]"
                  : "bg-[var(--ink-faint)]"
              } ${toggling ? "opacity-50" : ""}`}
            >
              <div
                className={`absolute top-0.5 w-5 h-5 rounded-full bg-white shadow transition-transform ${
                  alert.active ? "translate-x-[22px]" : "translate-x-0.5"
                }`}
              />
            </div>
          </button>
        </div>

        {/* Filters summary chips */}
        {filterSummary.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mb-3">
            {filterSummary.map((chip, i) => (
              <span
                key={i}
                className="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium bg-[var(--surface-1)] text-[var(--ink-secondary)]"
              >
                {chip}
              </span>
            ))}
          </div>
        )}

        {/* Keywords display */}
        {alert.filters.keywords && alert.filters.keywords.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-3">
            {alert.filters.keywords.map((kw) => (
              <span
                key={kw}
                className="inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-[var(--brand-blue-subtle)] text-[var(--brand-blue)]"
              >
                {kw}
              </span>
            ))}
          </div>
        )}

        {/* Actions row */}
        <div className="flex items-center gap-2 pt-2 border-t border-[var(--border)]">
          <button
            onClick={() => onEdit(alert)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-[var(--ink-secondary)] hover:bg-[var(--surface-1)] hover:text-[var(--ink)] transition-colors"
            data-testid={`alert-edit-${alert.id}`}
          >
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75V8.25A2.25 2.25 0 0 1 5.25 6H10" />
            </svg>
            Editar
          </button>

          {showConfirm ? (
            <div className="flex items-center gap-1.5 ml-auto">
              <span className="text-xs text-[var(--error)]">Excluir?</span>
              <Button
                onClick={handleDelete}
                disabled={deleting}
                variant="destructive"
                size="sm"
                className="h-6 px-2 text-xs"
              >
                {deleting ? "..." : "Sim"}
              </Button>
              <Button
                onClick={() => setShowConfirm(false)}
                variant="ghost"
                size="sm"
                className="h-6 px-2 text-xs"
              >
                Nao
              </Button>
            </div>
          ) : (
            <button
              onClick={() => setShowConfirm(true)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-[var(--error)] hover:bg-[var(--error-subtle)] transition-colors ml-auto"
              data-testid={`alert-delete-${alert.id}`}
            >
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
              </svg>
              Excluir
            </button>
          )}
        </div>
      </div>
    </div>
  );
});
