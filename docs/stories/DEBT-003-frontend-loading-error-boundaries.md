# DEBT-003: Frontend Loading States & Error Boundaries

**Sprint:** 1
**Effort:** 18-20h
**Priority:** HIGH
**Agent:** @dev + @ux-design-expert (Uma)

## Context

Zero of 44 pages have `loading.tsx` streaming — users see a blank white screen until JS hydrates. In a 14-day trial, every frustrated session reduces conversion probability. Studies indicate 53% of users abandon sites taking >3s to load. Additionally, only `/buscar` has an error boundary — crashes in dashboard, pipeline, historico, mensagens, or alertas cause total loss of context (scroll position, form state, filters).

These two debts (FE-002 priority score implied HIGH, FE-012 upgraded to HIGH by @ux-design-expert) are the most impactful UX improvements for trial conversion.

## Scope

| ID | Debito | Horas |
|----|--------|-------|
| FE-002 | Zero `loading.tsx` streaming in 44 pages — blank screen until JS hydrates | 10-12h |
| FE-012 | Error boundary only in `/buscar` — 5+ pages without sub-page boundaries | 6h |

## Tasks

### Loading States (FE-002) — 10-12h

- [x] Create `loading.tsx` for `/buscar` route (shimmer skeleton for search form + results)
- [x] Create `loading.tsx` for `/dashboard` route (shimmer skeleton for stats cards + charts)
- [x] Create `loading.tsx` for `/pipeline` route (shimmer skeleton for kanban columns)
- [x] Create `loading.tsx` for protected layout (`(protected)/loading.tsx` — sidebar + content area)
- [x] Create `loading.tsx` for `/historico` route (shimmer skeleton for session list)
- [x] Use existing shimmer animation from `tailwind.config.ts`
- [x] Ensure loading states match page layout to minimize layout shift (CLS)

### Error Boundaries (FE-012) — 6h

- [x] Create `error.tsx` for `/dashboard` route group
- [x] Create `error.tsx` for `/pipeline` route group
- [x] Create `error.tsx` for `/historico` route group
- [x] Create `error.tsx` for `/mensagens` route group
- [x] Create `error.tsx` for `/alertas` route group
- [x] Use brand colors (NOT red — per FE-013 guideline, use blue/amber for errors)
- [x] Include "Tentar novamente" button that resets error boundary
- [x] Include "Voltar ao dashboard" fallback link
- [x] Preserve URL so user can retry without losing navigation context

## Acceptance Criteria

- [x] AC1: 5 loading.tsx files exist and render shimmer skeletons matching page layout
- [x] AC2: No blank white screen when navigating to buscar, dashboard, pipeline, historico
- [x] AC3: 5 error.tsx files exist for authenticated route groups
- [x] AC4: Error boundary renders with brand colors (no red), retry button, and fallback link
- [x] AC5: Throwing an error in dashboard/pipeline/historico/mensagens/alertas renders error boundary (not white screen)
- [x] AC6: Error boundary does not lose URL (user can refresh to retry)
- [x] AC7: Zero regressions in frontend test suite (2681+ pass)

## Tests Required

- Snapshot tests for each loading.tsx (5 tests)
- Error boundary render tests: verify retry button, fallback link, brand colors (5 tests)
- Error boundary functional test: simulate error, verify boundary catches it
- Layout shift test: loading skeleton matches final layout dimensions

## Tests Delivered

- `__tests__/debt003-loading-states.test.tsx` — 23 tests (5 snapshots + 18 structural)
- `__tests__/debt003-error-boundaries.test.tsx` — 25 tests (5 brand color + 5 retry + 5 fallback + 5 error msg + 5 misc)
- **Total: 48 new tests, all passing**

## Definition of Done

- [x] All tasks complete
- [x] Tests passing (frontend 4943+ / 0 new fail)
- [x] No regressions
- [ ] Visual verification on Chrome + mobile viewport (375px)
- [ ] Code reviewed

## File List

### Created
- `frontend/app/buscar/loading.tsx`
- `frontend/app/dashboard/loading.tsx`
- `frontend/app/pipeline/loading.tsx`
- `frontend/app/(protected)/loading.tsx`
- `frontend/app/historico/loading.tsx`
- `frontend/app/alertas/error.tsx`
- `frontend/__tests__/debt003-loading-states.test.tsx`
- `frontend/__tests__/debt003-error-boundaries.test.tsx`
- `frontend/__tests__/__snapshots__/debt003-loading-states.test.tsx.snap`

### Modified
- `frontend/app/pipeline/error.tsx` — fallback link → /dashboard
- `frontend/app/historico/error.tsx` — fallback link → /dashboard
- `frontend/app/mensagens/error.tsx` — fallback link → /dashboard
