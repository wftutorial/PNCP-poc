# DEBT-013: Frontend Performance Optimization

**Sprint:** 2
**Effort:** 16-20h
**Priority:** MEDIUM
**Agent:** @dev

## Context

The frontend loads heavy libraries eagerly even when not needed — Recharts (~50KB), @dnd-kit (~15KB), and Shepherd.js (~25KB) are bundled into pages that may not use them. Only 2 files use `next/dynamic`. Dashboard charts are not optimized for mobile (labels overflow, touch targets too small). Large pages (alertas: 1068 lines, dashboard: 1037 lines) lack adequate memoization, causing jank on mid-range devices. CSS styling mixes CSS variables and raw Tailwind in ~10 files.

These optimizations directly impact trial conversion — perceived speed during the 14-day trial window determines conversion probability.

## Scope

| ID | Debito | Horas |
|----|--------|-------|
| FE-019 | No code splitting for Recharts, @dnd-kit, Shepherd.js — loaded eagerly | 4h |
| FE-014 | No memoization in large pages (alertas: 2 useMemo in 1068 lines, dashboard: 6 in 1037) | 4h |
| FE-031 | Dashboard charts not mobile-optimized — labels overflow, small touch targets | 4-6h |
| FE-018 | No `next/image` usage (only 4 files) — LCP impacted on landing/blog | 4h |
| FE-016 | Mix of CSS variables and raw Tailwind in ~10 files | (bundled with DEBT-012 FE-036) |

## Tasks

### Code Splitting (FE-019) — 4h

- [ ] Convert Recharts imports to `next/dynamic` with `ssr: false` in dashboard
- [ ] Convert @dnd-kit imports to `next/dynamic` in pipeline page
- [ ] Convert Shepherd.js imports to `next/dynamic` in onboarding
- [ ] Add loading fallback for each dynamic import (shimmer/skeleton)
- [ ] Verify bundle size reduction with `next build --analyze` (or similar)

### Memoization (FE-014) — 4h

- [ ] Audit alertas page: identify expensive computations and add `useMemo`/`useCallback`
- [ ] Audit dashboard page: add `useMemo` for chart data transformations
- [ ] Add `React.memo` to child components that receive stable props
- [ ] Profile with React DevTools Profiler to verify re-render reduction
- [ ] Document memoization guidelines for future development

### Mobile Charts (FE-031) — 4-6h

- [ ] Add responsive breakpoints for chart dimensions (mobile vs desktop)
- [ ] Fix label overflow: truncate or rotate labels on small screens
- [ ] Increase touch targets for chart interactions (minimum 44x44px per WCAG)
- [ ] Add horizontal scroll wrapper for charts that cannot responsively resize
- [ ] Test on 375px viewport (iPhone SE) and 414px viewport (iPhone Plus)

### Image Optimization (FE-018) — 4h

- [ ] Replace `<img>` with `<Image>` from `next/image` on landing page (LCP impact)
- [ ] Replace `<img>` with `<Image>` on blog pages
- [ ] Configure image optimization (sizes, quality, priority for above-fold)
- [ ] Skip authenticated pages that use SVG (no impact from next/image)

## Acceptance Criteria

- [ ] AC1: Recharts, @dnd-kit, and Shepherd.js are dynamically imported (not in initial bundle)
- [ ] AC2: Bundle size reduced (measured with build analysis — document before/after)
- [ ] AC3: alertas and dashboard pages have adequate memoization (profiler shows <30% unnecessary re-renders)
- [ ] AC4: Dashboard charts render without overflow on 375px viewport
- [ ] AC5: Chart touch targets are >= 44x44px
- [ ] AC6: Landing page uses `next/image` for all images (LCP optimized)
- [ ] AC7: Zero regressions in frontend test suite

## Tests Required

- Dynamic import tests: verify lazy-loaded components render after load
- Loading fallback tests: verify skeleton shows during dynamic import
- Mobile viewport tests: dashboard charts at 375px width
- next/image: verify optimization props (sizes, priority) are set correctly

## Definition of Done

- [ ] All tasks complete
- [ ] Tests passing (frontend 2700+ / 0 fail)
- [ ] No regressions
- [ ] Bundle analysis before/after documented in PR
- [ ] Mobile visual verification (375px, 414px)
- [ ] Code reviewed
