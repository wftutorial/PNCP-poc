"use client";

import { useState, useEffect } from "react";
import { Button } from "../../../components/ui/button";
import { CurrencyInput } from "../../../components/ui/CurrencyInput";
import { SECTOR_DISPLAY_NAMES } from "../../../lib/constants/sector-names";
import { UFMultiSelect } from "./UFMultiSelect";
import { KeywordsInput } from "./KeywordsInput";
import { AlertPreview } from "./AlertPreview";
import type { Alert, AlertFormData } from "./types";
import { EMPTY_FORM } from "./types";

const SECTOR_OPTIONS = Object.entries(SECTOR_DISPLAY_NAMES).map(
  ([slug, label]) => ({ value: slug, label }),
);

export function AlertFormModal({
  editingAlert,
  onSave,
  onClose,
  saving,
}: {
  editingAlert: Alert | null;
  onSave: (data: AlertFormData) => Promise<void>;
  onClose: () => void;
  saving: boolean;
}) {
  const [form, setForm] = useState<AlertFormData>(() => {
    if (editingAlert) {
      return {
        name: editingAlert.name,
        setor: editingAlert.filters.setor || "",
        ufs: editingAlert.filters.ufs || [],
        valor_min:
          editingAlert.filters.valor_min !== null
            ? String(editingAlert.filters.valor_min)
            : "",
        valor_max:
          editingAlert.filters.valor_max !== null
            ? String(editingAlert.filters.valor_max)
            : "",
        keywords: editingAlert.filters.keywords || [],
      };
    }
    return { ...EMPTY_FORM };
  });

  const [showPreview, setShowPreview] = useState(false);

  const isValid = form.name.trim().length >= 3;

  const hasFilters =
    form.setor !== "" ||
    form.ufs.length > 0 ||
    form.valor_min !== "" ||
    form.valor_max !== "" ||
    form.keywords.length > 0;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isValid) return;
    await onSave(form);
  };

  // Close on Escape
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", handleKey);
    return () => document.removeEventListener("keydown", handleKey);
  }, [onClose]);

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center pt-[5vh] sm:pt-[10vh]"
      role="dialog"
      aria-modal="true"
      aria-label={editingAlert ? "Editar alerta" : "Criar novo alerta"}
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/40 backdrop-blur-sm"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Modal panel */}
      <div className="relative w-full max-w-xl mx-4 max-h-[85vh] overflow-y-auto rounded-2xl bg-[var(--surface-0)] border border-[var(--border)] shadow-2xl">
        {/* Header */}
        <div className="sticky top-0 z-10 flex items-center justify-between px-5 py-4 border-b border-[var(--border)] bg-[var(--surface-0)] rounded-t-2xl">
          <h2 className="text-lg font-semibold text-[var(--ink)]">
            {editingAlert ? "Editar Alerta" : "Criar Novo Alerta"}
          </h2>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-[var(--ink-muted)] hover:bg-[var(--surface-1)] hover:text-[var(--ink)] transition-colors"
            aria-label="Fechar"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-5 space-y-5">
          {/* Alert name */}
          <div>
            <label
              htmlFor="alert-name"
              className="block text-sm font-medium text-[var(--ink)] mb-1.5"
            >
              Nome do alerta <span className="text-[var(--error)]">*</span>
            </label>
            <input
              id="alert-name"
              type="text"
              value={form.name}
              onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
              placeholder='Ex.: "Uniformes SP e RJ"'
              maxLength={100}
              className="w-full px-3 py-2 rounded-lg border border-[var(--border)] bg-[var(--surface-0)] text-sm text-[var(--ink)] placeholder:text-[var(--ink-muted)] focus:border-[var(--brand-blue)] focus:ring-1 focus:ring-[var(--brand-blue)]/20 outline-none transition-colors"
              autoFocus
            />
            {form.name.length > 0 && form.name.trim().length < 3 && (
              <p className="text-[11px] text-[var(--error)] mt-1">
                Nome deve ter pelo menos 3 caracteres
              </p>
            )}
          </div>

          {/* Sector dropdown */}
          <div>
            <label
              htmlFor="alert-setor"
              className="block text-sm font-medium text-[var(--ink)] mb-1.5"
            >
              Setor
            </label>
            <select
              id="alert-setor"
              value={form.setor}
              onChange={(e) => setForm((f) => ({ ...f, setor: e.target.value }))}
              className="w-full px-3 py-2 rounded-lg border border-[var(--border)] bg-[var(--surface-0)] text-sm text-[var(--ink)] focus:border-[var(--brand-blue)] focus:ring-1 focus:ring-[var(--brand-blue)]/20 outline-none transition-colors"
            >
              <option value="">Todos os setores</option>
              {SECTOR_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          {/* UFs multi-select */}
          <UFMultiSelect
            selected={form.ufs}
            onChange={(ufs) => setForm((f) => ({ ...f, ufs }))}
          />

          {/* Value range with BRL currency mask */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label
                htmlFor="alert-valor-min"
                className="block text-sm font-medium text-[var(--ink)] mb-1.5"
              >
                Valor mínimo
              </label>
              <CurrencyInput
                id="alert-valor-min"
                value={form.valor_min}
                onChange={(raw) => setForm((f) => ({ ...f, valor_min: raw }))}
                placeholder="0,00"
              />
            </div>
            <div>
              <label
                htmlFor="alert-valor-max"
                className="block text-sm font-medium text-[var(--ink)] mb-1.5"
              >
                Valor máximo
              </label>
              <CurrencyInput
                id="alert-valor-max"
                value={form.valor_max}
                onChange={(raw) => setForm((f) => ({ ...f, valor_max: raw }))}
                placeholder="Sem limite"
              />
            </div>
          </div>

          {/* Keywords */}
          <KeywordsInput
            keywords={form.keywords}
            onChange={(kws) => setForm((f) => ({ ...f, keywords: kws }))}
          />

          {/* Preview toggle */}
          {hasFilters && (
            <div>
              <button
                type="button"
                onClick={() => setShowPreview(!showPreview)}
                className="flex items-center gap-1.5 text-sm text-[var(--brand-blue)] hover:underline"
              >
                <svg
                  className={`w-4 h-4 transition-transform ${showPreview ? "rotate-90" : ""}`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  strokeWidth={1.5}
                >
                  <path strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
                </svg>
                {showPreview ? "Ocultar preview" : "Preview do alerta"}
              </button>
              {showPreview && <AlertPreview form={form} />}
            </div>
          )}

          {/* Action buttons */}
          <div className="flex items-center justify-end gap-3 pt-3 border-t border-[var(--border)]">
            <Button
              type="button"
              onClick={onClose}
              variant="ghost"
              size="default"
            >
              Cancelar
            </Button>
            <Button
              type="submit"
              disabled={!isValid || saving}
              loading={saving}
              variant="primary"
              size="default"
              data-testid="alert-save-button"
            >
              {editingAlert ? "Salvar alterações" : "Criar alerta"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
