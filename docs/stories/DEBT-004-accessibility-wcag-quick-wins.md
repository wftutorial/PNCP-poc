# DEBT-004: Accessibility Quick Wins (WCAG AA)

**Sprint:** 1
**Effort:** 7.5h
**Priority:** HIGH
**Agent:** @ux-design-expert (Uma)

## Context

Four WCAG AA violations were identified, three of which are quick wins addressable in Sprint 1. Government contracts (B2G) increasingly require accessibility compliance. Non-compliance risks disqualification from procurement processes. The violations affect screen reader users, keyboard-only users, and users with color vision deficiency (~8% of males).

FE-023 (color-only indicators) is deferred to Sprint 2 (DEBT-012) as it requires design changes to the ViabilityBadge component.

## Scope

| ID | Debito | WCAG | Horas |
|----|--------|------|-------|
| FE-034 | Missing `aria-label` on icon-only buttons — screen readers announce "button" with no context | 1.3.1, 4.1.2 | 1.5h |
| FE-022 | No focus trapping in modals (Dialog, DeepAnalysis, Upgrade, Cancel) — keyboard users trapped or escape modals | 2.4.3 | 4h |
| FE-021 | No `aria-live` for search results — screen readers not notified of dynamic content updates | 4.1.3 | 2h |

## Tasks

### Icon Button Labels (FE-034) — 1.5h

- [ ] Audit all `<button>` elements with only icon/SVG children (Sidebar collapse, filter toggles, close buttons, etc.)
- [ ] Add `aria-label` with descriptive text to each icon-only button
- [ ] Verify no duplicate aria-labels on the same page

### Focus Trapping (FE-022) — 4h

- [ ] Install `focus-trap-react` package
- [ ] Wrap Dialog/Modal components with `<FocusTrap>`
- [ ] Wrap DeepAnalysis modal with `<FocusTrap>`
- [ ] Wrap Upgrade/CancelSubscription modals with `<FocusTrap>`
- [ ] Verify Escape key closes modal and returns focus to trigger element
- [ ] Test tab cycling stays within modal when open

### Search Results Announcements (FE-021) — 2h

- [ ] Add `aria-live="polite"` region for search result count ("X resultados encontrados")
- [ ] Add `aria-live="assertive"` for search errors
- [ ] Ensure loading state changes are announced ("Buscando..." -> "X resultados")
- [ ] Verify announcements work with NVDA/VoiceOver

## Acceptance Criteria

- [ ] AC1: Zero icon-only buttons without `aria-label` (axe audit passes)
- [ ] AC2: All modals trap focus — Tab key cycles within modal, not behind it
- [ ] AC3: Escape key closes modals and returns focus to the trigger element
- [ ] AC4: Screen reader announces search result count after search completes
- [ ] AC5: Screen reader announces search errors via `aria-live="assertive"`
- [ ] AC6: `focus-trap-react` is in `package.json` dependencies
- [ ] AC7: Zero regressions in frontend test suite

## Tests Required

- Axe accessibility audit: zero violations for aria-label on buttons
- Focus trap test: open modal, tab through all focusable elements, verify focus stays inside
- Focus trap test: close modal, verify focus returns to trigger
- aria-live test: verify search results update triggers screen reader announcement
- Integration test: search flow with accessibility assertions

## Definition of Done

- [ ] All tasks complete
- [ ] axe-core audit passes for all authenticated pages
- [ ] Tests passing (frontend 2681+ / 0 fail)
- [ ] No regressions
- [ ] Manual keyboard navigation test on buscar page
- [ ] Code reviewed
