"use client";

import Link from "next/link";

export function DashboardQuickLinks() {
  return (
    <div className="bg-[var(--surface-0)] border border-[var(--border)] rounded-card p-6">
      <h2 className="text-lg font-display font-semibold text-[var(--ink)] mb-4">
        {`Acesso rápido`}
      </h2>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <Link
          href="/buscar"
          className="flex items-center gap-3 p-3 rounded-card border border-[var(--border)]
                     hover:border-[var(--border-strong)] hover:bg-[var(--surface-1)] transition-colors"
        >
          <span className="text-xl">{"\uD83D\uDD0D"}</span>
          <span className="text-sm text-[var(--ink)]">Nova Busca</span>
        </Link>
        <Link
          href="/historico"
          className="flex items-center gap-3 p-3 rounded-card border border-[var(--border)]
                     hover:border-[var(--border-strong)] hover:bg-[var(--surface-1)] transition-colors"
        >
          <span className="text-xl">{"\uD83D\uDCDC"}</span>
          <span className="text-sm text-[var(--ink)]">{`Histórico`}</span>
        </Link>
        <Link
          href="/conta"
          className="flex items-center gap-3 p-3 rounded-card border border-[var(--border)]
                     hover:border-[var(--border-strong)] hover:bg-[var(--surface-1)] transition-colors"
        >
          <span className="text-xl">{"\u2699\uFE0F"}</span>
          <span className="text-sm text-[var(--ink)]">Minha Conta</span>
        </Link>
        <Link
          href="/planos"
          className="flex items-center gap-3 p-3 rounded-card border border-[var(--border)]
                     hover:border-[var(--border-strong)] hover:bg-[var(--surface-1)] transition-colors"
        >
          <span className="text-xl">{"\uD83D\uDC8E"}</span>
          <span className="text-sm text-[var(--ink)]">Planos</span>
        </Link>
      </div>
    </div>
  );
}
