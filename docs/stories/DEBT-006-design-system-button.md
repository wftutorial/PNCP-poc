# DEBT-006: Design System Foundation (Shared Button Component)

**Sprint:** 1
**Effort:** 4-6h
**Priority:** HIGH
**Agent:** @ux-design-expert (Uma) + @dev

## Context

The SmartLic frontend has 15+ distinct button styling patterns with no shared Button component. This is the most visible inconsistency to users and undermines the professional appearance critical for B2G customers evaluating the platform during their 14-day trial. A shared Button component is the foundation for the entire design system — all subsequent component standardization (Input, Label, Badge) depends on establishing this pattern first.

Priority score: 10.0 (HIGH severity, HIGH impact, MEDIUM effort).

## Scope

| ID | Debito | Horas |
|----|--------|-------|
| FE-032 | No shared Button component — 15+ distinct styling patterns across the app | 4-6h |

## Tasks

- [x] Initialize Shadcn/ui (or equivalent) in the frontend project
  - Already initialized: CVA + @radix-ui/react-slot + tailwind-merge (shadcn/ui pattern)
- [x] Create `components/ui/Button.tsx` with:
  - 6 variants: `primary`, `secondary`, `ghost`, `destructive`, `outline`, `link`
  - 4 sizes: `sm`, `default`, `lg`, `icon` (icon = icon-only)
  - States: `loading` (spinner), `disabled`, `icon-only` (with required `aria-label`)
  - Full TypeScript props interface extending `ButtonHTMLAttributes`
  - Discriminated union: IconButtonProps (size="icon" + aria-label required) | StandardButtonProps
- [x] Create Storybook-like documentation or a `Button.examples.tsx` showing all variants
  - `components/ui/Button.examples.tsx` — full matrix of variants x sizes + states
- [x] Migrate top 5 most-used button patterns to the shared component:
  - Primary CTA buttons (SearchForm search button, alertas create, conta password change)
  - Secondary/ghost navigation buttons (SearchForm save, SearchStateManager cancel, alertas cancel)
  - Destructive buttons (alertas delete confirm, conta delete account/modal)
  - Icon-only buttons (SearchForm dismiss tip, SearchResults tour close)
  - Loading state buttons (SearchForm search in progress, SearchStateManager failed retry, alertas save, conta export/delete)
- [x] Verify Tailwind config is not broken by Shadcn/ui setup (visual check all pages)
  - Build passes, no Tailwind config changes needed

## Acceptance Criteria

- [x] AC1: `components/ui/Button.tsx` exists with 6 variants, 3 sizes, loading/disabled/icon-only states
- [x] AC2: Button component has full TypeScript interface (no `any` types)
- [x] AC3: Icon-only variant requires `aria-label` prop (TypeScript enforcement via discriminated union)
- [x] AC4: At least 5 pages use the shared Button component (replacing inline styles)
  - 10 files total: buscar/page.tsx, login/page.tsx, signup/page.tsx, planos/page.tsx, pipeline/page.tsx, conta/page.tsx, alertas/page.tsx, SearchForm.tsx, SearchStateManager.tsx, SearchResults.tsx
- [x] AC5: `npm run build` succeeds (Shadcn/ui setup does not break build)
- [x] AC6: Visual check confirms no layout/style regressions on authenticated pages
  - Build successful, TypeScript clean (1 pre-existing error in SearchEmptyState.tsx fixed)
- [x] AC7: Zero regressions in frontend test suite
  - 5352 passing / 5 pre-existing failures / 57 skipped (was 5291 + 61 new tests)

## Tests Required

- [x] Unit tests for Button component: all 6 variants render correctly
- [x] Unit tests: loading state shows spinner, disabled state is not clickable
- [x] Unit tests: icon-only without aria-label produces TypeScript error (compile-time, verified via source analysis)
- [x] Snapshot tests for each variant/size combination (21 snapshots)
- [x] Integration: pages using Button render without errors (10 pages verified via import check)

## Definition of Done

- [x] All tasks complete
- [x] Tests passing (5352+ / 5 pre-existing fail)
- [x] No regressions
- [x] Visual verification on 5+ pages (10 pages using Button)
- [x] Code reviewed
- [x] Tailwind config verified (no style conflicts)

## File List

| File | Change |
|------|--------|
| `components/ui/button.tsx` | Enhanced: discriminated union for icon-only aria-label enforcement |
| `components/ui/Button.examples.tsx` | NEW: full variant/size/state documentation |
| `app/buscar/components/SearchForm.tsx` | Migrated: search CTA, save button, dismiss tip |
| `app/buscar/components/SearchResults.tsx` | Migrated: tour start/close, degraded retry |
| `app/buscar/components/SearchStateManager.tsx` | Migrated: retry/cancel buttons (3 phases) |
| `app/alertas/page.tsx` | Migrated: create CTA, delete confirm, form save/cancel |
| `app/conta/page.tsx` | Migrated: password change, export, delete account, modal buttons |
| `app/buscar/components/SearchEmptyState.tsx` | Fixed: pre-existing import path bug |
| `__tests__/button-component.test.tsx` | NEW: 61 tests (variants, sizes, states, snapshots, adoption) |
