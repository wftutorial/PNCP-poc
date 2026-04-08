import { Suspense } from "react";
import { Metadata } from "next";
import ObrigadoContent from "./ObrigadoContent";

/**
 * Thank-you page after a successful Stripe checkout.
 *
 * Server Component shell: exports metadata and wraps the dynamic content
 * in Suspense (required because ObrigadoContent reads useSearchParams).
 * The actual subscription polling and UI are handled by ObrigadoContent ("use client").
 */
export const metadata: Metadata = {
  title: "Assinatura Confirmada",
  description: "Seu acesso ao SmartLic Pro foi ativado com sucesso.",
  robots: { index: false, follow: false },
};

export default function ObrigadoPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-[var(--canvas)] flex items-center justify-center">
        <div className="animate-pulse text-[var(--ink-muted)]">Carregando...</div>
      </div>
    }>
      <ObrigadoContent />
    </Suspense>
  );
}
