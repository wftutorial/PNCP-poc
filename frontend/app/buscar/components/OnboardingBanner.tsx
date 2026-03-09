"use client";

interface OnboardingBannerProps {
  message?: string;
}

export function OnboardingBanner({ message }: OnboardingBannerProps) {
  return (
    <div className="mb-4 p-4 rounded-lg bg-[var(--brand-blue)]/5 border border-[var(--brand-blue)]/20 flex items-center gap-3">
      <div className="w-5 h-5 border-2 border-[var(--brand-blue)] border-t-transparent rounded-full animate-spin flex-shrink-0" />
      <div>
        <p className="text-sm font-medium text-[var(--brand-blue)]">
          {message || "Analisando oportunidades com base no seu perfil..."}
        </p>
        <p className="text-xs text-[var(--ink-secondary)] mt-0.5">
          Isso leva ~15 segundos. Aguarde enquanto analisamos as fontes de dados.
        </p>
      </div>
    </div>
  );
}
