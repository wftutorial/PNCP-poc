"use client";

/**
 * DEBT-204 Track 3: BannerStack
 *
 * Priority-driven banner container that reduces cognitive load by limiting
 * visible banners to 2 (the highest-severity ones) and offering a collapsible
 * "Ver mais alertas" panel for the rest.
 *
 * Priority order: error (4) > warning (3) > info (2) > success (1)
 * aria-live="assertive" for errors, aria-live="polite" for others.
 *
 * AC17: Maximum 2 banners visible simultaneously (priority order).
 * AC18: Non-error (informational) banners auto-dismiss after 5 seconds.
 * AC19: Mounting 5 simultaneous banners results in only 2 visible in DOM.
 */

import React, { useState, useEffect } from "react";

// ============================================================================
// Types
// ============================================================================

export type BannerType = "error" | "warning" | "info" | "success";

export interface BannerItem {
  /** Unique identifier for this banner entry */
  id: string;
  /** Severity type — drives sort order and aria-live level */
  type: BannerType;
  /** The content to render inside the banner */
  content: React.ReactNode;
  /**
   * Optional tie-breaking priority within the same type.
   * Higher value = shown first when severities are equal.
   * Default: 0.
   */
  priority?: number;
}

export interface BannerStackProps {
  /** Ordered list of banners to display */
  banners: BannerItem[];
  /**
   * Maximum number of banners shown before collapsing.
   * Default: 2.
   */
  maxVisible?: number;
  /** Extra className on the container element */
  className?: string;
  /** data-testid for the container */
  "data-testid"?: string;
  /**
   * Auto-dismiss delay in milliseconds for non-error banners.
   * Default: 5000 (5 seconds). Set to 0 to disable auto-dismiss.
   */
  autoDismissMs?: number;
}

// ============================================================================
// Helpers
// ============================================================================

const SEVERITY_RANK: Record<BannerType, number> = {
  error: 4,
  warning: 3,
  info: 2,
  success: 1,
};

function sortBanners(banners: BannerItem[]): BannerItem[] {
  return [...banners].sort((a, b) => {
    const rankDiff = SEVERITY_RANK[b.type] - SEVERITY_RANK[a.type];
    if (rankDiff !== 0) return rankDiff;
    // Same severity — higher priority value first
    return (b.priority ?? 0) - (a.priority ?? 0);
  });
}

// ============================================================================
// BannerWrapper — renders a single banner item with aria-live
// ============================================================================

interface BannerWrapperProps {
  item: BannerItem;
}

function BannerWrapper({ item }: BannerWrapperProps) {
  // Errors use "assertive" so screen readers announce immediately.
  const ariaLive: React.AriaAttributes["aria-live"] =
    item.type === "error" ? "assertive" : "polite";

  return (
    <div
      data-testid={`banner-item-${item.id}`}
      aria-live={ariaLive}
      aria-atomic="true"
    >
      {item.content}
    </div>
  );
}

// ============================================================================
// BannerStack — main component
// ============================================================================

export function BannerStack({
  banners,
  maxVisible = 2,
  className = "",
  "data-testid": testId = "banner-stack",
  autoDismissMs = 5000,
}: BannerStackProps) {
  const [expanded, setExpanded] = useState(false);
  // Set of banner IDs that have been auto-dismissed
  const [dismissed, setDismissed] = useState<Set<string>>(new Set());

  // Reset dismissed state when the banners prop changes identity
  // (new search or new banner set)
  useEffect(() => {
    setDismissed(new Set());
  }, [banners]);

  // AC18: Auto-dismiss non-error banners after autoDismissMs
  useEffect(() => {
    if (autoDismissMs <= 0) return;

    const timers: ReturnType<typeof setTimeout>[] = [];

    for (const banner of banners) {
      // Error banners are persistent — never auto-dismiss
      if (banner.type === "error") continue;

      const timer = setTimeout(() => {
        setDismissed((prev) => {
          const next = new Set(prev);
          next.add(banner.id);
          return next;
        });
      }, autoDismissMs);

      timers.push(timer);
    }

    return () => {
      for (const timer of timers) clearTimeout(timer);
    };
  }, [banners, autoDismissMs]);

  // Filter out dismissed banners before sorting/slicing
  const activeBanners = banners.filter((b) => !dismissed.has(b.id));

  // Nothing to render
  if (activeBanners.length === 0) return null;

  // AC17 / AC19: slice to maxVisible after priority sort
  const sorted = sortBanners(activeBanners);
  const visible = sorted.slice(0, maxVisible);
  const hidden = sorted.slice(maxVisible);
  const hasMore = hidden.length > 0;

  return (
    <div
      data-testid={testId}
      className={["flex flex-col gap-2", className].filter(Boolean).join(" ")}
    >
      {/* Always-visible top banners (AC17: max maxVisible items) */}
      {visible.map((item) => (
        <BannerWrapper key={item.id} item={item} />
      ))}

      {/* Overflow section */}
      {hasMore && (
        <div>
          {/* Toggle button */}
          <button
            type="button"
            data-testid="banner-stack-toggle"
            onClick={() => setExpanded((prev) => !prev)}
            aria-expanded={expanded}
            aria-controls="banner-stack-overflow"
            className={[
              "flex items-center gap-1.5 text-xs font-medium",
              "text-[var(--ink-secondary)] hover:text-[var(--ink)]",
              "transition-colors focus-visible:outline-none",
              "focus-visible:ring-2 focus-visible:ring-[var(--brand-blue)] rounded",
              "py-1 px-0",
            ].join(" ")}
          >
            {expanded ? (
              <>
                {/* Chevron up */}
                <svg
                  className="w-3.5 h-3.5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 15l7-7 7 7"
                  />
                </svg>
                Ocultar alertas
              </>
            ) : (
              <>
                {/* Chevron down */}
                <svg
                  className="w-3.5 h-3.5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
                Ver mais alertas (+{hidden.length})
              </>
            )}
          </button>

          {/* Collapsed/expanded overflow banners */}
          <div
            id="banner-stack-overflow"
            data-testid="banner-stack-overflow"
            aria-hidden={!expanded}
            className={[
              "flex flex-col gap-2 overflow-hidden transition-all duration-200",
              expanded ? "mt-2 opacity-100" : "max-h-0 opacity-0 pointer-events-none",
            ].join(" ")}
          >
            {hidden.map((item) => (
              <BannerWrapper key={item.id} item={item} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default BannerStack;
