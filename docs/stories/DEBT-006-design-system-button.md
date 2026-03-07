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

- [ ] Initialize Shadcn/ui (or equivalent) in the frontend project
- [ ] Create `components/ui/Button.tsx` with:
  - 6 variants: `primary`, `secondary`, `ghost`, `destructive`, `outline`, `link`
  - 3 sizes: `sm`, `md`, `lg`
  - States: `loading` (spinner), `disabled`, `icon-only` (with required `aria-label`)
  - Full TypeScript props interface extending `ButtonHTMLAttributes`
- [ ] Create Storybook-like documentation or a `Button.examples.tsx` showing all variants
- [ ] Migrate top 5 most-used button patterns to the shared component:
  - Primary CTA buttons (search, save, submit)
  - Secondary/ghost navigation buttons
  - Destructive buttons (delete, cancel subscription)
  - Icon-only buttons (sidebar toggle, close, filter)
  - Loading state buttons (search in progress)
- [ ] Verify Tailwind config is not broken by Shadcn/ui setup (visual check all pages)

## Acceptance Criteria

- [ ] AC1: `components/ui/Button.tsx` exists with 6 variants, 3 sizes, loading/disabled/icon-only states
- [ ] AC2: Button component has full TypeScript interface (no `any` types)
- [ ] AC3: Icon-only variant requires `aria-label` prop (TypeScript enforcement)
- [ ] AC4: At least 5 pages use the shared Button component (replacing inline styles)
- [ ] AC5: `npm run build` succeeds (Shadcn/ui setup does not break build)
- [ ] AC6: Visual check confirms no layout/style regressions on authenticated pages
- [ ] AC7: Zero regressions in frontend test suite

## Tests Required

- Unit tests for Button component: all 6 variants render correctly
- Unit tests: loading state shows spinner, disabled state is not clickable
- Unit tests: icon-only without aria-label produces TypeScript error (compile-time)
- Snapshot tests for each variant/size combination
- Integration: pages using Button render without errors

## Definition of Done

- [ ] All tasks complete
- [ ] Tests passing (frontend 2681+ / 0 fail)
- [ ] No regressions
- [ ] Visual verification on 5+ pages
- [ ] Code reviewed
- [ ] Tailwind config verified (no style conflicts)
