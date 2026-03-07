# DEBT-016: Frontend Advanced Refactoring

**Sprint:** Backlog
**Effort:** 82-104h
**Priority:** MEDIUM
**Agent:** @dev + @ux-design-expert (Uma)

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

- [ ] Decompose alertas page into sub-components (alert list, alert detail, alert creation)
- [ ] Decompose dashboard page into widget components (stats, charts, recent activity)
- [ ] Decompose buscar page into sub-components (search form, results, filters, progress)
- [ ] Each resulting component < 300 lines

### SSR Optimization (FE-004) — 12-16h

- [ ] Identify 3-5 pages that can be partially SSR (planos, historico, ajuda likely candidates)
- [ ] Extract client-only parts into `"use client"` sub-components
- [ ] Convert remaining page shell to Server Component
- [ ] Verify hydration works correctly

### Component Directory Convention (FE-005) — 4h

- [ ] Document convention: `components/` = shared, `app/components/` = providers/layouts, `app/{feature}/components/` = feature-specific
- [ ] Add ESLint import restriction rules to enforce convention
- [ ] Move any misplaced components

### Data Fetching Standardization (FE-007) — 8h

- [ ] Standardize read-only endpoints on SWR (Phase 2: mutations)
- [ ] Replace raw `fetch()` calls with SWR hooks where appropriate
- [ ] Keep SSE hooks custom (not SWR)
- [ ] Ensure consistent error handling and loading states

### useSearch Tests (FE-035) — 8-12h

- [ ] Create dedicated test file for useSearch hook (isolation tests)
- [ ] Test all major code paths: search initiation, SSE progress, error handling, retry, cache
- [ ] Test edge cases: concurrent searches, timeout, partial results
- [ ] Prerequisite for safe useSearch refactoring

### Lower Priority Items

- [ ] Resolve TODO/FIXME in blog content (FE-010) — 8h
- [ ] i18n framework evaluation and setup (FE-003) — 40h (only if international expansion planned)
- [ ] Keyboard shortcut help overlay (FE-024) — 2h
- [ ] Navigation component tests (FE-025) — 8h
- [ ] PWA/offline investigation (FE-027) — 8h
- [ ] Lazy-load fonts (FE-020) — 2h

## Acceptance Criteria

- [ ] AC1: All monolithic pages decomposed (each component < 300 lines)
- [ ] AC2: 3+ pages converted to partial SSR
- [ ] AC3: Component directory convention documented and enforced via ESLint
- [ ] AC4: Majority of GET endpoints use SWR (consistent loading/error patterns)
- [ ] AC5: useSearch has dedicated isolation tests with 80%+ code path coverage
- [ ] AC6: Zero regressions in frontend test suite (2750+ pass)

## Tests Required

- Decomposed component render tests
- SSR hydration tests (no mismatch warnings)
- SWR hook tests (loading, error, success, revalidation)
- useSearch isolation tests (all major paths)
- Navigation component tests (render, active state, responsive)

## Definition of Done

- [ ] All tasks complete
- [ ] Tests passing (frontend 2800+ / 0 fail)
- [ ] No regressions
- [ ] `npx tsc --noEmit` passes
- [ ] Code reviewed
