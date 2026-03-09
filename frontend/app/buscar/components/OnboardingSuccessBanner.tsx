"use client";

interface OnboardingSuccessBannerProps {
  count: number;
  onDismiss: () => void;
}

export function OnboardingSuccessBanner({
  count,
  onDismiss,
}: OnboardingSuccessBannerProps) {
  return (
    <div className="mb-4 p-4 rounded-lg bg-green-50 dark:bg-green-900/10 border border-green-200 dark:border-green-800 flex items-center justify-between gap-3">
      <div className="flex items-center gap-3">
        <svg className="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p className="text-sm font-medium text-green-800 dark:text-green-200">
          Encontramos {count} {count === 1 ? "oportunidade" : "oportunidades"} para você! Explore abaixo.
        </p>
      </div>
      <button
        onClick={onDismiss}
        className="px-3 py-1 text-xs font-medium rounded bg-green-100 dark:bg-green-800 text-green-700 dark:text-green-200 hover:bg-green-200 dark:hover:bg-green-700 transition-colors whitespace-nowrap"
      >
        Entendi
      </button>
    </div>
  );
}
