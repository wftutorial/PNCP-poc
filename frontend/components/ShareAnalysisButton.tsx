"use client";

import { useState, useCallback } from "react";
import type { LicitacaoItem } from "../app/types";

interface ShareAnalysisButtonProps {
  item: LicitacaoItem;
  accessToken?: string | null;
}

/**
 * SEO-PLAYBOOK P6: Button to create a shareable viability analysis link.
 * Calls POST /api/share, copies URL to clipboard, shows toast.
 * Uses Web Share API on mobile when available.
 */
export function ShareAnalysisButton({ item, accessToken }: ShareAnalysisButtonProps) {
  const [status, setStatus] = useState<"idle" | "loading" | "copied" | "error">("idle");

  const handleShare = useCallback(async () => {
    if (!accessToken) return;
    setStatus("loading");

    try {
      const res = await fetch("/api/share", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({
          bid_id: item.pncp_id || "",
          bid_title: item.objeto,
          bid_orgao: item.orgao,
          bid_uf: item.uf,
          bid_valor: item.valor,
          bid_modalidade: item.modalidade,
          viability_score: item.viability_score,
          viability_level: item.viability_level || "media",
          viability_factors: item.viability_factors || {},
        }),
      });

      if (!res.ok) {
        setStatus("error");
        setTimeout(() => setStatus("idle"), 2000);
        return;
      }

      const data = await res.json();
      const url = data.url;

      // Try Web Share API on mobile
      if (typeof navigator !== "undefined" && navigator.share) {
        try {
          await navigator.share({
            title: `Análise: ${item.objeto.slice(0, 60)}`,
            text: `Score de viabilidade: ${item.viability_score}/100`,
            url,
          });
          setStatus("copied");
          setTimeout(() => setStatus("idle"), 2000);
          return;
        } catch {
          // User cancelled or API unavailable — fall through to clipboard
        }
      }

      // Fallback: copy to clipboard
      await navigator.clipboard.writeText(url);
      setStatus("copied");
      setTimeout(() => setStatus("idle"), 2000);
    } catch {
      setStatus("error");
      setTimeout(() => setStatus("idle"), 2000);
    }
  }, [item, accessToken]);

  if (!accessToken) return null;

  return (
    <button
      onClick={handleShare}
      disabled={status === "loading"}
      className="inline-flex items-center gap-1 px-3 py-1.5 text-sm font-medium text-ink-secondary border border-border rounded-button hover:bg-surface-1 hover:text-brand-blue transition-colors disabled:opacity-50"
      data-testid="share-analysis-btn"
      aria-label="Compartilhar análise de viabilidade"
    >
      {status === "loading" ? (
        <svg className="w-3.5 h-3.5 animate-spin" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
      ) : status === "copied" ? (
        <svg className="w-3.5 h-3.5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
      ) : (
        <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
        </svg>
      )}
      {status === "copied" ? "Link copiado!" : status === "error" ? "Erro" : "Compartilhar"}
    </button>
  );
}
