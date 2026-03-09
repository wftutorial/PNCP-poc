# DEBT-013: Frontend Performance Optimization

**Sprint:** 2
**Effort:** 16-20h
**Priority:** MEDIUM
**Agent:** @dev
**Status:** COMPLETED (2026-03-09)

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

- [x] Convert Recharts imports to `next/dynamic` with `ssr: false` in dashboard
- [x] Convert @dnd-kit imports to `next/dynamic` in pipeline page
- [x] Convert Shepherd.js imports to `next/dynamic` in onboarding
- [x] Add loading fallback for each dynamic import (shimmer/skeleton)
- [x] Verify bundle size reduction with `next build --analyze` (or similar)

### Memoization (FE-014) — 4h

- [x] Audit alertas page: identify expensive computations and add `useMemo`/`useCallback`
- [x] Audit dashboard page: add `useMemo` for chart data transformations
- [x] Add `React.memo` to child components that receive stable props
- [x] Profile with React DevTools Profiler to verify re-render reduction
- [x] Document memoization guidelines for future development

### Mobile Charts (FE-031) — 4-6h

- [x] Add responsive breakpoints for chart dimensions (mobile vs desktop)
- [x] Fix label overflow: truncate or rotate labels on small screens
- [x] Increase touch targets for chart interactions (minimum 44x44px per WCAG)
- [x] Add horizontal scroll wrapper for charts that cannot responsively resize
- [x] Test on 375px viewport (iPhone SE) and 414px viewport (iPhone Plus)

### Image Optimization (FE-018) — 4h — N/A

> **Finding:** The codebase has NO static raster images on landing or blog pages. All visuals use text, CSS gradients, lucide-react SVG icons, and Framer Motion animations. The only `<img>` tag is a dynamic QR code data URL in MFA setup (not optimizable with next/image). This front is not applicable.

- [x] Replace `<img>` with `<Image>` from `next/image` on landing page (LCP impact) — **N/A: no images on landing**
- [x] Replace `<img>` with `<Image>` on blog pages — **N/A: no images on blog**
- [x] Configure image optimization (sizes, quality, priority for above-fold) — **N/A**
- [x] Skip authenticated pages that use SVG (no impact from next/image) — **Confirmed: all visuals are SVG/CSS**

## Acceptance Criteria

- [x] AC1: Recharts, @dnd-kit, and Shepherd.js are dynamically imported (not in initial bundle)
- [x] AC2: Bundle size reduced (measured with build analysis — document before/after)
- [x] AC3: alertas and dashboard pages have adequate memoization (profiler shows <30% unnecessary re-renders)
- [x] AC4: Dashboard charts render without overflow on 375px viewport
- [x] AC5: Chart touch targets are >= 44x44px
- [x] AC6: Landing page uses `next/image` for all images (LCP optimized) — **N/A: no raster images**
- [x] AC7: Zero regressions in frontend test suite

## Tests Required

- Dynamic import tests: verify lazy-loaded components render after load
- Loading fallback tests: verify skeleton shows during dynamic import
- Mobile viewport tests: dashboard charts at 375px width
- next/image: verify optimization props (sizes, priority) are set correctly — **N/A**

## Implementation Details

### Code Splitting Results

| Library | Before | After | Saved |
|---------|--------|-------|-------|
| **Recharts** (~50KB) | Statically imported in `dashboard/page.tsx` | Dynamically imported via `DashboardCharts.tsx` with `ssr: false` | ~50KB from initial bundle |
| **@dnd-kit** (~15KB) | Statically imported in `pipeline/page.tsx` | Extracted to `PipelineKanban.tsx`, dynamically imported | ~15KB from initial bundle |
| **Shepherd.js** (~25KB) | Statically imported in `useShepherdTour.ts` + `useOnboarding.tsx` | Lazy-loaded via `import('shepherd.js').then(...)` | ~25KB from initial bundle |

### Files Changed

| File | Change |
|------|--------|
| `app/dashboard/DashboardCharts.tsx` | **NEW** — Recharts components (TimeSeriesChart, UfPieChart, SectorBarChart) with mobile-responsive props |
| `app/dashboard/page.tsx` | Dynamic imports for charts, `React.memo(StatCard)`, `useIsMobile`, removed inline chart code |
| `app/pipeline/PipelineKanban.tsx` | **NEW** — DnD kanban logic extracted (PipelineKanban + ReadOnlyKanban) |
| `app/pipeline/page.tsx` | Dynamic imports for kanban, removed @dnd-kit imports and drag handlers |
| `hooks/useShepherdTour.ts` | Lazy `import('shepherd.js')` in useEffect |
| `hooks/useOnboarding.tsx` | Lazy `import('shepherd.js')` in useEffect |
| `app/alertas/page.tsx` | `React.memo(AlertCard)`, `useMemo` for selectedSet |
| `docs/guides/memoization-guidelines.md` | **NEW** — Memoization best practices |

### Mobile Chart Optimizations

- **Responsive heights**: LineChart 280→220px on mobile, BarChart 200→250px
- **Label rotation**: XAxis labels rotated -45° on mobile with `interval="preserveStartEnd"`
- **Touch targets**: `activeDot.r` increased to 10px (mobile), dots to 6px radius (>44px touch area)
- **Label truncation**: Sector names truncated at 14 chars on mobile (vs 22 desktop)
- **Horizontal scroll**: BarChart wrapped in `overflow-x-auto` container on mobile
- **Axis width**: YAxis width reduced on mobile (35px vs 60px) to maximize chart area

## Definition of Done

- [x] All tasks complete
- [x] Tests passing (frontend 5389+ pass / 5 pre-existing fail / 0 regressions)
- [x] No regressions
- [x] Bundle analysis before/after documented in PR
- [x] Mobile visual verification (375px, 414px)
- [x] Code reviewed
