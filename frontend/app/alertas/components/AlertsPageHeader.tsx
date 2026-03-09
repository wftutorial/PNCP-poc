"use client";

import { Button } from "../../../components/ui/button";
import type { Alert } from "./types";

export function AlertsPageHeader({
  alerts,
  onCreateClick,
}: {
  alerts: Alert[];
  onCreateClick: () => void;
}) {
  const activeCount = alerts.filter((a) => a.active).length;

  return (
    <>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-[var(--text-primary)]">
            Alertas por E-mail
          </h1>
          <p className="text-sm text-[var(--text-secondary)] mt-1">
            Receba notificações automáticas sobre novas licitações.
          </p>
        </div>
        {alerts.length > 0 && (
          <Button
            onClick={onCreateClick}
            variant="primary"
            size="default"
            data-testid="alerts-create-button"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
            </svg>
            <span className="hidden sm:inline">Criar alerta</span>
          </Button>
        )}
      </div>

      {alerts.length > 0 && (
        <div className="flex items-center gap-4 mb-5 text-sm text-[var(--ink-secondary)]">
          <span>
            {alerts.length} {alerts.length === 1 ? "alerta" : "alertas"}
          </span>
          <span className="w-px h-4 bg-[var(--border)]" />
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-green-500" />
            {activeCount} {activeCount === 1 ? "ativo" : "ativos"}
          </span>
        </div>
      )}
    </>
  );
}
