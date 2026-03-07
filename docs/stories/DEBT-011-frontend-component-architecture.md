# DEBT-011: Frontend Component Architecture

**Sprint:** 2
**Effort:** 24-28h
**Priority:** HIGH
**Agent:** @dev + @ux-design-expert (Uma)

## Context

Four pages exceed 1000 lines (conta: 1420, alertas: 1068, buscar: 1057, dashboard: 1037), causing unnecessary re-renders and making changes risky. The root cause is lack of global state management — auth, plan, quota, and search data are passed via prop drilling, causing stale data display when values change. This story addresses the foundation (global state) and begins page decomposition with `conta` (largest page, best candidate for sub-routes). It also fixes `any` types in 8 production files.

**Critical dependency chain:** DEBT-005.FE-026 (quarantine resolution) must be complete before page decomposition begins. DEBT-011.FE-006 (global state) must be complete before FE-001 decomposition.

## Scope

| ID | Debito | Horas |
|----|--------|-------|
| FE-006 | No global state management — auth+plan+quota+search via prop drilling causes stale data | 8h |
| FE-001 | Monolithic pages (partial: decompose `conta/page.tsx` 1420 lines into sub-routes) | 8-10h |
| FE-008 | `any` types in 8 production files (pipeline, filters, analytics proxy + 5 others) | 2h |
| FE-030 | No `<Suspense>` boundaries in any page | 4-6h |

## Tasks

### Global State Management (FE-006) — 8h

- [ ] Evaluate SWR vs Zustand vs React Context for global state (auth, plan, quota)
- [ ] Implement global state for auth/user data (replace prop drilling in 5+ pages)
- [ ] Implement global state for plan/subscription data (replace localStorage polling)
- [ ] Implement global state for quota data (replace per-page fetching)
- [ ] Ensure state updates propagate to all consumers (no stale display)
- [ ] Leave SSE/search hooks as custom hooks (not global state)

### Page Decomposition: conta (FE-001 partial) — 8-10h

- [ ] Decompose `conta/page.tsx` (1420 lines) into sub-routes:
  - `/conta/perfil` — profile editing
  - `/conta/seguranca` — password, MFA
  - `/conta/plano` — plan/subscription management
  - `/conta/dados` — data export/deletion
- [ ] Create shared layout for `/conta` sub-routes (sidebar navigation)
- [ ] Each sub-route < 300 lines
- [ ] Migrate all state management to global state (from FE-006)
- [ ] Verify all existing functionality preserved

### Type Safety (FE-008) — 2h

- [ ] Replace `any` with proper types in all 8 production files
- [ ] Verify `npx tsc --noEmit` passes with zero errors

### Suspense Boundaries (FE-030) — 4-6h

- [ ] Add `<Suspense>` boundaries to pages with loading.tsx (from DEBT-003)
- [ ] Add `<Suspense>` boundaries around dynamically imported components
- [ ] Ensure fallback UI matches loading.tsx skeleton

## Acceptance Criteria

- [ ] AC1: Global state management for auth/plan/quota — zero prop drilling for these values
- [ ] AC2: `conta/page.tsx` decomposed into 4 sub-routes, each < 300 lines
- [ ] AC3: Conta sub-routes have shared sidebar layout
- [ ] AC4: Zero `any` types in production files (`npx tsc --noEmit` clean)
- [ ] AC5: `<Suspense>` boundaries wrap dynamic imports and loading states
- [ ] AC6: All conta functionality preserved (profile edit, password change, plan view, data export)
- [ ] AC7: Zero regressions in frontend test suite (2700+ pass — post quarantine resolution)

## Tests Required

- Global state: verify state updates propagate (change plan, verify all consumers update)
- Conta sub-routes: render tests for each sub-route
- Conta navigation: tab switching between sub-routes preserves state
- Type safety: `npx tsc --noEmit` passes
- Suspense: loading fallback renders during async load

## Definition of Done

- [ ] All tasks complete
- [ ] Tests passing (frontend 2700+ / 0 fail)
- [ ] No regressions
- [ ] `npx tsc --noEmit` passes
- [ ] Visual verification of conta page (all sub-routes)
- [ ] Code reviewed
