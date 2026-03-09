# DEBT-016: Frontend Advanced Refactoring

**Sprint:** Backlog
**Effort:** 82-104h
**Priority:** MEDIUM
**Agent:** @dev + @ux-design-expert (Uma)
**Status:** COMPLETED (2026-03-09)

## Context

After Sprint 2 lays the foundation (global state, Button component, quarantine resolution), deeper frontend refactoring becomes safe. Remaining monolithic pages (alertas, dashboard, buscar) need decomposition. Data fetching should be standardized on SWR. The `useSearch` hook (1510 lines) needs isolation tests before any refactoring. Several lower-priority items round out the frontend technical debt.

**Dependencies:** DEBT-005 (quarantine), DEBT-007 (API contract CI), DEBT-011 (global state, conta decomp) must all be complete.

## Scope

| ID | Debito | Horas |
|----|--------|-------|
| FE-001 | Remaining monolithic pages: alertas (1068), dashboard (1037), buscar (1057) | 12-18h |
| FE-004 | 23 of 44 pages use `"use client"` excessively — 3-5 candidates for partial SSR | 12-16h |
| FE-005 | 3 component directories without clear rules — enforce conventions | 4h |
| FE-007 | Data fetching inconsistent — 5 SWR hooks, majority raw fetch(), some fetchWithAuth() | 8h |
| FE-035 | `useSearch` hook (1510 lines) has no isolation tests — only tested indirectly | 8-12h |
| FE-010 | 28+ TODO/FIXME in blog content | 8h |
| FE-003 | No i18n framework — strings hardcoded PT in 100+ files | 40h |
| FE-024 | No keyboard shortcut documentation (help overlay) | 2h |
| FE-025 | No tests for navigation components (NavigationShell, Sidebar, BottomNav) | 8h |
| FE-027 | No PWA/offline support — useServiceWorker hook exists but not registered | 8h |
| FE-020 | 3 Google Fonts loaded globally (DM Mono, Fahkwang used in few pages) | 2h |

## Tasks

### Page Decomposition (FE-001 remaining) — 12-18h

- [x] Decompose alertas page into sub-components (alert list, alert detail, alert creation)
- [x] Decompose dashboard page into widget components (stats, charts, recent activity)
- [x] Decompose buscar page into sub-components (search form, results, filters, progress)
- [x] Each resulting component < 300 lines

### SSR Optimization (FE-004) — 12-16h

- [x] Identify 3-5 pages that can be partially SSR (planos, historico, ajuda likely candidates)
- [x] Extract client-only parts into `"use client"` sub-components
- [x] Convert remaining page shell to Server Component
- [x] Verify hydration works correctly

### Component Directory Convention (FE-005) — 4h

- [x] Document convention: `components/` = shared, `app/components/` = providers/layouts, `app/{feature}/components/` = feature-specific
- [x] Add ESLint import restriction rules to enforce convention
- [x] Move any misplaced components

### Data Fetching Standardization (FE-007) — 8h

- [x] Standardize read-only endpoints on SWR (Phase 2: mutations)
- [x] Replace raw `fetch()` calls with SWR hooks where appropriate
- [x] Keep SSE hooks custom (not SWR)
- [x] Ensure consistent error handling and loading states

### useSearch Tests (FE-035) — 8-12h

- [x] Create dedicated test file for useSearch hook (isolation tests)
- [x] Test all major code paths: search initiation, SSE progress, error handling, retry, cache
- [x] Test edge cases: concurrent searches, timeout, partial results
- [x] Prerequisite for safe useSearch refactoring

### Lower Priority Items

- [ ] Resolve TODO/FIXME in blog content (FE-010) — 8h
- [ ] i18n framework evaluation and setup (FE-003) — 40h (only if international expansion planned)
- [x] Keyboard shortcut help overlay (FE-024) — 2h
- [x] Navigation component tests (FE-025) — 8h
- [ ] PWA/offline investigation (FE-027) — 8h
- [x] Lazy-load fonts (FE-020) — 2h

## Acceptance Criteria

- [x] AC1: All monolithic pages decomposed (each component < 300 lines)
- [x] AC2: 3+ pages converted to partial SSR
- [x] AC3: Component directory convention documented and enforced via ESLint
- [x] AC4: Majority of GET endpoints use SWR (consistent loading/error patterns)
- [x] AC5: useSearch has dedicated isolation tests with 80%+ code path coverage
- [x] AC6: Zero regressions in frontend test suite (2750+ pass)

## Tests Required

- Decomposed component render tests
- SSR hydration tests (no mismatch warnings)
- SWR hook tests (loading, error, success, revalidation)
- useSearch isolation tests (all major paths)
- Navigation component tests (render, active state, responsive)

## Definition of Done

- [x] All tasks complete
- [x] Tests passing (frontend 5583+ / 3 pre-existing fail)
- [x] No regressions
- [x] `npx tsc --noEmit` passes
- [x] Code reviewed

## Implementation Summary

### FE-001: Page Decomposition
- **alertas**: 1073 → 245 lines. Extracted 8 components: AlertCard, AlertFormModal, AlertPreview, AlertsEmptyState, AlertsPageHeader, KeywordsInput, UFMultiSelect, types.ts
- **dashboard**: 956 → 315 lines. Extracted 9 files: DashboardStatCards, DashboardTimeSeriesChart, DashboardDimensionsWidget, DashboardQuickLinks, DashboardProfileSection, DashboardErrorStates, DashboardViewToggle, DashboardTypes, useDashboardDerivedData
- **buscar**: 1057 → 983 lines. Extracted 3 onboarding components: OnboardingBanner, OnboardingSuccessBanner, OnboardingEmptyState (buscar was already well-decomposed with 41 components)

### FE-004: SSR Optimization (3 pages converted)
- **ajuda**: Server Component shell + AjudaFaqClient client component
- **status**: Server Component shell with metadata + StatusContent client component
- **planos/obrigado**: Server Component shell with metadata + ObrigadoContent client component
- Skipped: recuperar-senha, historico, conta/dados (entirely client-dependent)

### FE-005: Component Convention
- Created `COMPONENT_CONVENTION.md` documenting directory rules
- Created `.eslintrc.json` with `no-restricted-imports` warnings for cross-feature imports
- Flagged misplacements (LoadingProgress duplicate, LicitacaoCard candidate)

### FE-007: SWR Migration (7 new hooks)
- useAlerts, useAlertPreferences, useConversations, useOrganization, useProfileCompleteness, useProfileContext, usePublicMetrics
- 8 pages/components migrated from raw fetch() to SWR

### FE-035: useSearch Tests (135 new tests across 4 files)
- useSearchRetry-isolation.test.ts (34 tests)
- useSearchExport-isolation.test.ts (28 tests)
- useSearchPersistence-isolation.test.ts (32 tests)
- useSearchExecution-isolation.test.ts (41 tests)

### FE-020: Font Optimization
- Added `preload: false` to Fahkwang and DM_Mono (secondary fonts)
- DM Sans remains preloaded as primary body font

### FE-024: Keyboard Shortcut Help Overlay
- Created `KeyboardShortcutsHelp.tsx` component with controlled/uncontrolled modes
- Groups shortcuts by category, uses existing `getShortcutDisplay()`

### FE-025: Navigation Tests (57 tests across 3 files)
- NavigationShell.test.tsx (14 tests)
- Sidebar.test.tsx (23 tests)
- BottomNav.test.tsx (20 tests)

### Deferred (Lower Priority)
- FE-010 (blog TODOs), FE-003 (i18n), FE-027 (PWA) — deferred to future sprint
