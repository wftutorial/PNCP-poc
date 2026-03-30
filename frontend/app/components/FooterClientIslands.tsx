'use client';

import { useBackendStatusContext, type BackendStatus } from '@/app/components/BackendStatusIndicator';

/**
 * DEBT-FE-017: Client islands extracted from Footer to enable Footer RSC.
 * StatusFooterBadge requires useBackendStatusContext (CRIT-008).
 * ManageCookiesButton requires window.dispatchEvent.
 */

/**
 * STORY-316 AC16-AC17: Status badge in footer.
 * Reuses BackendStatusIndicator polling data (CRIT-008).
 */
export function StatusFooterBadge() {
  const { status } = useBackendStatusContext();

  const config: Record<BackendStatus, { dot: string; label: string }> = {
    online: { dot: 'bg-green-500', label: 'Operacional' },
    offline: { dot: 'bg-red-500 animate-pulse', label: 'Indisponível' },
    recovering: { dot: 'bg-yellow-500', label: 'Recuperando' },
  };

  const c = config[status];

  return (
    <a
      href="/status"
      className="flex items-center gap-1.5 text-sm text-ink-secondary hover:text-brand-blue transition-colors"
      aria-label={`Status: ${c.label}`}
    >
      <span className={`inline-block w-2 h-2 rounded-full ${c.dot}`} />
      Status: {c.label}
    </a>
  );
}

/**
 * Manage Cookies button — requires window.dispatchEvent (client-only).
 */
export function ManageCookiesButton() {
  return (
    <button
      onClick={() => window.dispatchEvent(new Event('manage-cookies'))}
      className="
        relative
        inline-block
        hover:text-brand-blue
        transition-colors
        focus-visible:outline-none
        focus-visible:ring-[3px]
        focus-visible:ring-[var(--ring)]
        focus-visible:ring-offset-2
        rounded
        px-1
        group
        text-left
      "
    >
      Gerenciar Cookies
      <span className="
        absolute
        bottom-0
        left-0
        w-0
        h-[2px]
        bg-brand-blue
        transition-all
        duration-300
        group-hover:w-full
      " />
    </button>
  );
}
