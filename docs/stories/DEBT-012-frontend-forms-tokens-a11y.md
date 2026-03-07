# DEBT-012: Frontend Forms, Tokens & Accessibility

**Sprint:** 2
**Effort:** 14-16h
**Priority:** MEDIUM
**Agent:** @ux-design-expert (Uma) + @dev

## Context

Forms across SmartLic use inconsistent styling and manual validation leading to different error messages for the same errors. Some forms use placeholder-as-label (WCAG 1.3.1 violation). Design tokens are partially adopted — a mix of CSS custom properties, Tailwind theme tokens, and raw hex values without enforcement. The viability indicator uses color-only encoding (WCAG 1.4.1 violation affecting ~8% of male users with color vision deficiency).

This story depends on DEBT-006 (Button component) being complete for consistent design system patterns.

## Scope

| ID | Debito | Horas |
|----|--------|-------|
| FE-033 | No shared Input/Label component — forms with different styling, placeholder-as-label in some | 3-4h |
| FE-036 | Design tokens partially adopted — mix of CSS vars, Tailwind tokens, and raw hex values | 3-4h |
| FE-028 | No structured form validation — no react-hook-form/zod, manual validation with inconsistent messages | 8h |
| FE-023 | Viability indicators use color-only encoding (WCAG 1.4.1 violation) | 2h |

## Tasks

### Shared Input/Label Components (FE-033) — 3-4h

- [ ] Create `components/ui/Input.tsx` with consistent styling, error state, disabled state
- [ ] Create `components/ui/Label.tsx` with proper `htmlFor` association
- [ ] Ensure no placeholder-as-label pattern (all inputs have visible labels)
- [ ] Migrate top 3 forms to use shared components (signup, conta, onboarding)

### Design Tokens (FE-036) — 3-4h

- [ ] Extend `tailwind.config.ts` theme with CSS custom properties: `bg-brand-primary` -> `var(--brand-primary)`
- [ ] Define token mapping: primary (#116dff), secondary (#0a1e3f), accent, success, warning, error
- [ ] Replace raw hex values in 10+ files with Tailwind theme tokens
- [ ] Add ESLint rule or comment convention to discourage raw hex values

### Form Validation (FE-028) — 8h

- [ ] Install `react-hook-form` and `zod` packages
- [ ] Create Zod schemas for top 3 forms: signup, conta/perfil, onboarding
- [ ] Integrate `react-hook-form` with `zod` resolver
- [ ] Implement inline error feedback (real-time validation, not submit-only)
- [ ] Standardize error messages (consistent Portuguese copy for all validations)
- [ ] Ensure form state preservation on error (no data loss)

### Viability Accessibility (FE-023) — 2h

- [ ] Add text labels alongside color indicators in ViabilityBadge: "Alta", "Media", "Baixa"
- [ ] Ensure text is visible (not sr-only) for all users
- [ ] Maintain existing color coding as supplementary (not sole) indicator
- [ ] Update any tooltips to include text description

## Acceptance Criteria

- [ ] AC1: `components/ui/Input.tsx` and `components/ui/Label.tsx` exist and are used in 3+ forms
- [ ] AC2: Zero placeholder-as-label patterns (all inputs have visible `<Label>`)
- [ ] AC3: Tailwind theme extended with brand tokens; zero raw hex values in migrated files
- [ ] AC4: 3 forms use react-hook-form + zod with inline error feedback
- [ ] AC5: ViabilityBadge shows text labels ("Alta"/"Media"/"Baixa") alongside color
- [ ] AC6: WCAG 1.4.1 compliance: information not conveyed by color alone
- [ ] AC7: Zero regressions in frontend test suite

## Tests Required

- Input/Label: render tests for all states (default, error, disabled, focused)
- Form validation: zod schema validation tests for each form
- Form validation: inline error display on invalid input
- ViabilityBadge: verify text labels render for all viability levels
- Accessibility: axe audit passes for forms and viability indicators

## Definition of Done

- [ ] All tasks complete
- [ ] Tests passing (frontend 2700+ / 0 fail)
- [ ] No regressions
- [ ] axe accessibility audit passes for forms
- [ ] Visual verification of forms and viability badges
- [ ] Code reviewed
