/**
 * DEBT-FE-012 + DEBT-205: Feature gate configuration.
 *
 * Static gates: Pages listed in GATED_FEATURES show ComingSoonPage.
 * These are the SSR/module-level fallback for unreleased features.
 *
 * Dynamic flags: Use `useFeatureFlags()` hook from hooks/useFeatureFlags.ts
 * to consume backend flags via API at runtime (DEBT-SYS-009 / DEBT-FE-008).
 *
 * The backend feature flags API (/api/feature-flags) is the source of truth.
 * GATED_FEATURES is a static fallback for pages that need module-level checks
 * before the API response is available.
 *
 * SHIP-002 AC9: Alertas are feature-gated.
 */

export const GATED_FEATURES = new Set([
  "alertas",
]);

export function isFeatureGated(feature: string): boolean {
  return GATED_FEATURES.has(feature);
}
