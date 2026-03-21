# UX Specialist Review
**Reviewer:** @ux-design-expert (Uma)
**Date:** 2026-03-21
**Input:** docs/prd/technical-debt-DRAFT.md (Section 4 + Section 8)
**Method:** Code audit of actual frontend source + cross-reference with frontend-spec.md

---

## Debitos Validados

| ID | Debito | Sev. Original | Sev. Ajustada | Horas | Design Review? | Breaking? | Impacto UX |
|----|--------|---------------|---------------|-------|----------------|-----------|------------|
| DEBT-FE-001 | react-hook-form in devDependencies | HIGH | HIGH | 0.5 | No | No | None directly, but blocks reliable CI/CD |
| DEBT-FE-002 | SearchForm zero ARIA attributes | HIGH | **CRITICAL** | 3 | Yes | No | Core feature invisible to assistive tech; buscar is the #1 page |
| DEBT-FE-003 | Inconsistent form handling (useState vs react-hook-form) | MED | MED | 8 | No | No | Login form has no real-time validation feedback; inconsistent error UX across auth flows |
| DEBT-FE-004 | Framer Motion loaded globally (~50KB) | MED | MED | 6 | No | No | FCP penalty on every page load; users on mobile/slow connections affected |
| DEBT-FE-005 | 6 pages > 500 LOC without decomposition | MED | MED | 16 | No | No | Indirect: makes UX iteration slow; onboarding wizard (783 LOC) is highest priority |
| DEBT-FE-006 | Search hooks 3,287 LOC complexity | MED | **LOW** | 4 (docs) | No | No | Not user-facing; the decomposition is logical. Document it, do not refactor unless adding features |
| DEBT-FE-007 | Missing error boundaries (onboarding, signup, login, planos) | MED | **HIGH** | 3 | Yes | No | Errors on conversion-critical pages (signup, onboarding, planos) cause full-page crash with no recovery |
| DEBT-FE-008 | Skip-link broken on protected pages | MED | **HIGH** | 0.5 | No | No | Keyboard/SR users cannot skip nav on dashboard, pipeline, historico, conta. buscar has its own main-content id so it works there, but the (protected) layout does not. |
| DEBT-FE-009 | Blog TODO placeholders (60+) | LOW | LOW | 4 | No | No | No user-visible impact; internal links are missing but pages function |
| DEBT-FE-010 | No i18n infrastructure | LOW | LOW (accepted) | N/A | No | No | Intentional for pt-BR-only market. Not debt -- design choice |
| DEBT-FE-011 | Duplicate LoadingProgress + AddToPipelineButton | LOW | LOW | 2 | No | No | Developer confusion only; no UX impact |
| DEBT-FE-012 | Feature-gated pages still routable | LOW | **MED** | 2 | Yes | No | Users reaching /alertas or /mensagens via URL see API errors with no explanation. Especially bad if they land from a shared link. |
| DEBT-FE-013 | No skeleton loaders for 5 pages | LOW | LOW | 4 | No | No | Generic spinner is acceptable at current user volume; skeletons are a polish item |
| DEBT-FE-014 | EnhancedLoadingProgress 452 LOC | LOW | LOW | 4 | No | No | Not user-facing; only matters for maintainability |
| DEBT-FE-015 | BottomNav wrong Dashboard icon | LOW | LOW | 0.5 | No | No | Confirmed: line 48 uses icons.search for Dashboard instead of a dashboard icon. Minor visual inconsistency. |
| DEBT-FE-016 | Raw CSS var() instead of Tailwind classes | LOW | LOW | 4 | No | No | Developer ergonomics only; no UX difference |

### Also validated from System section:

| ID | Debito | Sev. Original | Sev. Ajustada | Horas | Impacto UX |
|----|--------|---------------|---------------|-------|------------|
| DEBT-SYS-008 | api-types.generated.ts 5,177 LOC bundle impact | HIGH | MED | 2 | Minimal if tree-shaken by Next.js; verify with bundle analyzer before acting |
| DEBT-SYS-015 | 58 API proxy routes, no factory | MED | LOW | 4 | Zero user impact; backend concern |
| DEBT-SYS-016 | onboarding + signup no decomposition | MED | MED | 4 | Slows UX iteration on first-time experience |

---

## Debitos Removidos

| ID | Razao da Remocao |
|----|-----------------|
| (none) | All items validated as real problems. Some severity adjustments above, but no removals. |

---

## Debitos Adicionados

| ID | Debito | Severidade | Horas | Impacto UX | Justificativa |
|----|--------|-----------|-------|------------|---------------|
| DEBT-FE-017 | **Login form lacks aria-invalid and aria-describedby** | HIGH | 1.5 | Login is the #2 most visited page. Email and password inputs use raw `<input>` with no `aria-invalid`, no `aria-describedby` linking to error messages, and no programmatic association between the error banner and the field that caused it. Screen readers announce the error role="alert" banner but users cannot navigate to the offending field. | Verified: login/page.tsx lines 396-420 use plain `<input>` with no aria attributes. |
| DEBT-FE-018 | **Mensagens status badges are color-only** | MED | 1 | Status indicators (aberto=yellow, respondido=blue, resolvido=green) rely solely on background color. No icon, no screen-reader text, and the text label is visible but relies on color contrast of white-on-color which may fail WCAG 2.1 AA for small text. | Verified: mensagens/page.tsx STATUS_COLORS lines 32-36 use only bg color + white text. |
| DEBT-FE-019 | **Onboarding progress bar has no accessible semantics** | MED | 1 | The ProgressBar component (onboarding/page.tsx lines 76-97) renders colored divs with "X de Y" text but has no `role="progressbar"`, no `aria-valuenow`, and no `aria-label`. Screen readers see "1 de 3" as static text with no context. | Verified in code. |
| DEBT-FE-020 | **Login mode toggle lacks tab/keyboard semantics** | MED | 1 | The "Email + Senha" / "Magic Link" toggle (login/page.tsx lines 373-393) is two adjacent buttons with visual styling to indicate selection, but has no `role="tablist"`/`role="tab"`, no `aria-selected`, and no keyboard arrow navigation. Violates WCAG 4.1.2 Name/Role/Value. | Verified: raw `<button>` elements with conditional className only. |
| DEBT-FE-021 | **Planos page FAQ accordion has no ARIA disclosure pattern** | LOW | 1.5 | FAQ items on /planos use openFaq state toggle but lack `aria-expanded`, `aria-controls`, and `role="button"` on the trigger. Screen readers cannot determine which items are open/closed. | Verified: planos/page.tsx uses simple click toggling with no ARIA. |
| DEBT-FE-022 | **Protected layout main tag missing id="main-content"** | HIGH | 0.25 | This is the root cause behind DEBT-FE-008 (skip-link). The `(protected)/layout.tsx` line 87 has `<main className="...">` without `id="main-content"`. The buscar page works because it renders its own `<main id="main-content">` outside the protected layout. Dashboard, pipeline, historico, conta all fail. Fix here rather than per-page. | Trivially fixable: add id="main-content" to one line. |
| DEBT-FE-023 | **No focus management after search completes** | MED | 2 | After a search returns results, keyboard focus remains on the search button. Users must tab through the entire form again to reach results. There is no focus shift strategy. ResultsHeader has aria-live="polite" which announces the count, but the tab order is suboptimal for keyboard-only users. | Verified: SearchForm does not manage focus post-search. |
| DEBT-FE-024 | **Pricing page CTA button has no inline loading state** | LOW | 1 | The "Comecar agora" button on /planos sets checkoutLoading state but on mobile the full-page Stripe redirect overlay may take 2-3s to appear. During this gap, users might tap multiple times. The button itself does not show a spinner or disabled state inline -- only the overlay appears. | Verified: planos/page.tsx checkout flow. |

---

## Respostas ao Architect

### Q1: DEBT-FE-002 (SearchForm ARIA) -- aria-live placement and priority vs skip-link

**aria-live placement:** The `ResultsHeader` component already has `aria-live="polite" aria-atomic="true"` (search-results/ResultsHeader.tsx line 25), which announces the result count on completion. This is correct and sufficient for result announcements. What is missing is `role="search"` on the SearchForm wrapper and an `aria-label` on it. I would NOT add a page-level aria-live -- the component-level one is better scoped.

**Priority vs skip-link (DEBT-FE-008):** Fix skip-link FIRST. It is a 15-minute fix (add `id="main-content"` to `(protected)/layout.tsx` line 87) and unblocks keyboard navigation on every protected page. The SearchForm ARIA work is more involved (3h) and benefits a narrower audience. Both should be in Sprint Imediato, but skip-link is a prerequisite for meaningful keyboard testing.

### Q2: DEBT-FE-003 (form consistency) -- UX improvement or deferred debt?

**Prioritize as UX improvement, but sequence it after accessibility fixes.** The login form is the second most visited page. Raw useState means: (a) no real-time validation (users only see errors on submit), (b) no `aria-invalid` integration (accessibility gap), (c) inconsistent error presentation vs signup which has field-level errors. However, this is an 8h effort that does not block revenue or cause crashes. Ship it in Proximo Sprint, not Sprint Imediato.

### Q3: DEBT-FE-004 (Framer Motion) -- Would removal degrade perceived UX?

**No, with caveats.** The landing page (public, non-authenticated) is where framer-motion delivers the most value: entrance animations on hero, feature cards, testimonials. On authenticated pages (buscar, dashboard, pipeline), framer-motion is not used -- those pages already rely on CSS animations from Tailwind config (`animate-fade-in-up`, `animate-shimmer`). The correct strategy is:

1. Keep framer-motion for `app/page.tsx` and landing sections (lazy-load via `next/dynamic`)
2. Replace any framer-motion usage in authenticated pages with CSS animations
3. This preserves the premium feel on the marketing site while saving ~50KB on the app shell

Estimated impact: LCP improvement of 100-200ms on mobile for authenticated pages.

### Q4: DEBT-FE-005 (large pages) -- Which page benefits most from decomposition?

**Onboarding (783 LOC), then Planos (714 LOC).** Reasoning:

1. **Onboarding** is the first protected experience. It is a 3-step wizard with form validation, CNAE autocomplete, region selection, and value presets -- all in one file. Decomposing into `StepOne.tsx`, `StepTwo.tsx`, `StepThree.tsx` + `useOnboardingState.ts` enables individual step testing and faster UX iteration. The step components are already defined as functions inside the file -- just extract them.
2. **Planos** (714 LOC) is the conversion page. It mixes pricing logic, FAQ accordion, status banners, checkout flow, and billing portal. Decomposing into `PricingCard.tsx`, `FaqAccordion.tsx`, `UserStatusBanner.tsx` enables A/B testing of pricing layouts.
3. **Login** (502 LOC) is third priority -- it has multiple modes (password, magic link, MFA) that map well to sub-components.
4. **Admin** (764 LOC) is lowest priority -- it is used by 1-2 people.

### Q5: DEBT-FE-012 (feature-gated pages) -- "Em breve" design

**Use a distinctive "Coming soon" design, NOT the generic EmptyState.** Reasoning:

- Generic EmptyState implies "you have no data yet" -- wrong message for a feature that does not exist
- The design should include: (a) feature name + 1-sentence description, (b) an illustration or icon, (c) optional email notification signup ("Avise-me quando disponivel"), (d) a link back to the main app
- Do NOT include a waitlist -- too heavy for 2 feature-gated pages. A simple "we will notify you" toggle that writes to the user's profile is sufficient and can be implemented in < 2h
- Match the overall brand (navy/blue palette, rounded cards) but make it visually distinct from error states

### Q6: DEBT-FE-013 (skeleton loaders) -- Worst perceived loading

**Planos has the worst perceived loading.** Here is the ranking:

1. **Planos** -- Users arrive with purchase intent. The page fetches plan data from the API, and during that time shows a generic spinner instead of price cards. This creates anxiety ("is the price going to change?") and reduces conversion confidence. A skeleton showing card shapes with shimmer would anchor expectations.
2. **Conta/plano** -- Users checking their subscription see a spinner before their plan details load. Again, billing context where loading feels longer.
3. **Admin** -- Only admins see this. Lowest priority.
4. **Alertas/mensagens** -- Feature-gated, so skeleton loaders are premature before the feature ships.

Given the small user base, I would only add skeletons for Planos now (1h effort) and defer the rest.

---

## Recomendacoes de Design

### Design System

**Status: Solid foundation, no formal system needed yet.** The codebase has:
- 6 Button variants with accessibility enforcement (icon-only requires aria-label)
- Input component with error/success states and ARIA bindings
- Comprehensive CSS custom property system (80+ tokens) with dark mode
- Tailwind config with semantic classes mapped to tokens

**Recommendation:** Do NOT invest in a formal design system (Storybook, documentation site) until the team grows past 3 frontend developers. The current approach (shared `components/ui/` with TypeScript enforcement) is sufficient. The main gap is not the system itself but inconsistent usage -- some components use the system (`components/ui/button`), others use raw HTML with inline styles. The DEBT-FE-016 (raw CSS vars) fix will close the biggest consistency gap.

**When to formalize:** When you hire a second frontend developer, create a minimal Storybook with the 6 existing UI primitives. Budget: 16h.

### Accessibility Roadmap

Priority order for WCAG 2.1 AA compliance:

1. **Sprint Imediato (this week):**
   - DEBT-FE-022: Add `id="main-content"` to protected layout (0.25h) -- unblocks all keyboard nav
   - DEBT-FE-008: Already covered by FE-022 (same fix)
   - DEBT-FE-002: Add `role="search"` + `aria-label` to SearchForm wrapper (3h)
   - DEBT-FE-017: Add `aria-invalid` + `aria-describedby` to login form (1.5h)

2. **Proximo Sprint (next 2 weeks):**
   - DEBT-FE-023: Focus management after search completes (2h)
   - DEBT-FE-019: Onboarding progress bar semantics (1h)
   - DEBT-FE-020: Login mode toggle tab semantics (1h)
   - DEBT-FE-018: Mensagens color-only status badges (1h)

3. **Backlog:**
   - DEBT-FE-021: Planos FAQ accordion ARIA (1.5h)
   - Extend axe-core Playwright specs to cover search page and login page
   - Manual screen reader testing (VoiceOver + NVDA) on the 3 critical flows: signup > onboarding > first search

**Total a11y effort:** ~12.25h across 3 sprints.

### Mobile Strategy

**Current state: Good.** Evidence:
- Mobile-first Tailwind breakpoints used consistently
- `BottomNav` for mobile with abbreviated labels for 375px viewport
- `min-height: 44px` enforced on buttons and inputs via globals.css
- `MobileDrawer` for hamburger menu
- `PullToRefresh` for mobile refresh on search
- `useIsMobile` hook for JS-level breakpoint detection

**Gaps:**
1. **BottomNav icon bug** (DEBT-FE-015) -- trivial fix
2. **Planos page on mobile** -- the pricing cards stack vertically but the billing period toggle (PlanToggle) could benefit from larger touch targets. Currently uses `text-xs` and `py-1.5` which may be borderline at 375px.
3. **Onboarding region selection** -- 27 UF checkboxes in a grid on mobile may be difficult to tap accurately. Consider region-level toggles (already implemented as REGIONS constant) with UF drill-down.

**Recommendation:** No major mobile changes needed. Fix the BottomNav icon and audit the PlanToggle touch targets (1h combined).

---

## Recomendacoes de Prioridade

### Sprint Imediato (this week, ~10.75h)

| Priority | ID | Debito | Horas | Justificativa |
|----------|-----|--------|-------|---------------|
| 1 | DEBT-FE-001 | react-hook-form to dependencies | 0.5 | Blocks CI reliability |
| 2 | DEBT-FE-022 | Add id="main-content" to protected layout | 0.25 | Fixes skip-link for ALL protected pages |
| 3 | DEBT-FE-002 | SearchForm role="search" + aria-label | 3 | Core page invisible to screen readers |
| 4 | DEBT-FE-017 | Login form aria-invalid + aria-describedby | 1.5 | #2 most visited page, zero a11y on form errors |
| 5 | DEBT-FE-015 | BottomNav Dashboard icon fix | 0.5 | Trivial, visual consistency |
| 6 | DEBT-FE-007 | Error boundaries for onboarding/signup/login/planos | 3 | Conversion-critical pages crash without recovery |
| 7 | DEBT-FE-012 | Feature-gated "Em breve" component | 2 | Users see broken state on direct URL access |

### Proximo Sprint (next 2 weeks, ~18h)

| Priority | ID | Debito | Horas | Justificativa |
|----------|-----|--------|-------|---------------|
| 1 | DEBT-FE-003 | Migrate login/reset forms to react-hook-form + zod | 8 | Consistent validation UX across all auth flows |
| 2 | DEBT-FE-023 | Focus management post-search | 2 | Keyboard UX on #1 page |
| 3 | DEBT-FE-019 | Onboarding progress bar a11y | 1 | First protected experience |
| 4 | DEBT-FE-020 | Login mode toggle tab semantics | 1 | WCAG 4.1.2 compliance |
| 5 | DEBT-FE-004 | Lazy-load Framer Motion for landing only | 6 | ~50KB bundle reduction on app pages |

### Backlog (prioritize when adding features)

| ID | Debito | Horas | Trigger |
|----|--------|-------|---------|
| DEBT-FE-005 | Page decomposition (onboarding, planos, login) | 16 | When iterating on onboarding or pricing UX |
| DEBT-FE-006 | Search hooks documentation | 4 | When onboarding a new developer |
| DEBT-FE-013 | Skeleton loader for planos | 1 | When optimizing conversion funnel |
| DEBT-FE-018 | Mensagens color-only badges | 1 | When un-gating mensagens feature |
| DEBT-FE-021 | Planos FAQ accordion ARIA | 1.5 | When iterating on pricing page |
| DEBT-FE-016 | Replace raw CSS vars with Tailwind classes | 4 | When doing any large-scale styling pass |
| DEBT-FE-014 | EnhancedLoadingProgress decomposition | 4 | When modifying search progress UX |
| DEBT-FE-024 | Planos checkout button inline loading | 1 | When optimizing conversion |
| DEBT-FE-009 | Blog TODO placeholder cleanup | 4 | When investing in SEO |
| DEBT-FE-010 | i18n infrastructure | 80+ | Only if expanding to non-PT markets |
| DEBT-FE-011 | Duplicate component consolidation | 2 | During any component cleanup pass |

---

## Metricas de Validacao

| Metric | Value |
|--------|-------|
| Items confirmados sem alteracao | 9/16 |
| Items com severidade ajustada | 5 (FE-002 HIGH->CRIT, FE-006 MED->LOW, FE-007 MED->HIGH, FE-008 MED->HIGH, FE-012 LOW->MED) |
| Items removidos | 0 |
| Items adicionados | 8 (FE-017 through FE-024) |
| Esforco total original (DRAFT) | ~62h (FE items only) |
| Esforco total revisado | ~73.5h (includes 8 new items at 11.25h) |
| Quick wins (< 1h) | 3 items: FE-001 (0.5h), FE-022 (0.25h), FE-015 (0.5h) |
| Sprint Imediato total | ~10.75h |
| Proximo Sprint total | ~18h |
| Backlog total | ~44.75h |

---

*Review completed 2026-03-21 by @ux-design-expert (Uma). All findings verified against actual source code.*
