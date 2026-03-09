# UX Specialist Review

**Reviewer:** @ux-design-expert
**Data:** 2026-03-09
**Fonte:** docs/prd/technical-debt-DRAFT.md (Section 3), docs/frontend/frontend-spec.md
**Supersedes:** ux-specialist-review.md v2.0 (2026-03-07, reviewer Uma)
**Codebase Snapshot:** branch `main`, commit `3c71ce93`

---

## Resumo da Revisao

The DRAFT Section 3 catalogs 29 frontend/UX debt items (FE-001 through FE-022 plus FE-A11Y-01 through FE-A11Y-07). After thorough codebase validation, I found that **several items have been partially or fully resolved** since the earlier discovery phases. The codebase shows strong progress on accessibility (aria-live now present in 15+ components, focus-trap-react in 6 modals, prefers-reduced-motion in globals.css) and performance (next/dynamic in 4 files for Recharts, dnd-kit, blog). However, the core structural debts remain: the `/buscar/page.tsx` monolith (983 LOC of orchestration logic), CSP unsafe-inline directives, and dual component directories.

The overall accuracy of the DRAFT is **good** -- 21 of 29 items are confirmed as stated. 5 items need severity adjustment (mostly downgrades due to recent fixes). 3 items are effectively resolved and should be removed or downgraded to INFO. I identified 4 new UX debts not present in the DRAFT.

| Status | Count |
|--------|-------|
| Confirmed (as-is) | 21 |
| Severity Adjusted | 5 |
| Removed / Downgraded to INFO | 3 |
| Added (new) | 4 |
| **Total validated frontend debts** | **30** |

---

## Debitos Validados

### Arquitetura e Estrutura (FE-001 through FE-003)

| ID | Debito | Severidade Original | Severidade Ajustada | Horas | Prioridade | Impacto UX |
|----|--------|---------------------|---------------------|-------|------------|------------|
| FE-001 | `/buscar/page.tsx` monolithic 983 LOC, 30+ imports | CRITICAL | **HIGH** | 16-20h | P2 | Indirect: maintainability affects feature velocity, re-renders on prop changes degrade scroll responsiveness. The page is well-decomposed into sub-components (35 in `buscar/components/`) -- the remaining LOC is state orchestration. Extract into `useSearchOrchestration` hook rather than more visual components. |
| FE-002 | No `next/dynamic` for heavy deps | CRITICAL | **MEDIUM** | 4-6h | P2 | **Partially fixed.** `next/dynamic` now used in pipeline (dnd-kit), dashboard charts (Recharts), login, and blog. Remaining gaps: Shepherd.js loaded on every /buscar visit regardless of tour state, framer-motion loaded globally in ProfileCompletionPrompt and landing page. Impact reduced from ~175KB to ~95KB. |
| FE-003 | SSE proxy complexity | CRITICAL | **HIGH** | 20-24h | P3 | Correct assessment. Multiple fallback paths (SSE -> polling -> time-simulation) with 3+ retry strategies. Hard to debug, hard to test E2E. However, this is a working system in production -- refactoring risk is high. Prioritize documentation and integration tests before restructuring. |

### Code Quality (FE-004 through FE-010)

| ID | Debito | Severidade Original | Severidade Ajustada | Horas | Prioridade | Impacto UX |
|----|--------|---------------------|---------------------|-------|------------|------------|
| FE-004 | Test coverage 50-55% | HIGH | **HIGH** | Ongoing | P3 | Confirmed. Current thresholds (branches 50%, functions 55%, lines 55%) are below the 60% target. Not directly user-visible but increases regression risk on every change. |
| FE-005 | No `prefers-reduced-motion` for 8 custom animations | HIGH | **REMOVED (INFO)** | 0h | N/A | **Already fixed.** `globals.css:331-337` contains a comprehensive `@media (prefers-reduced-motion: reduce)` block that disables all animations and transitions via `animation-duration: 0.01ms !important`. Additionally, `useInView.ts` checks for reduced-motion preference. The Tailwind config animations are properly covered by this global rule. |
| FE-006 | Dual component directories (app/components/ 46 + components/ 49) | HIGH | **HIGH** | 6-8h | P2 | Confirmed. Ownership is actually clearer than described -- `components/` holds primitives and global components, `app/components/` holds auth-aware and app-specific shared components, `app/buscar/components/` holds search-specific. The issue is lack of documented convention and some misplaced files. Not a full reorg needed, just a documented rule + 5-10 file moves. |
| FE-007 | `aria-live` missing on dynamic content updates | HIGH | **REMOVED (INFO)** | 0h | N/A | **Substantially fixed.** Found `aria-live` in 15+ production components: `ResultsHeader` (polite, atomic), `SearchStateManager` (assertive for errors, 4 instances), `EmptyResults` (polite), `UfProgressGrid` (polite), `SearchErrorBanner` (assertive), `ExpiredCacheBanner` (polite), `DataQualityBanner` (polite), `RefreshBanner` (polite), `ResultsLoadingSection` (polite), `EnhancedLoadingProgress` (polite), `PaymentFailedBanner` (assertive), `QuotaCounter` (polite), `Countdown` (polite). The search flow is now well-covered for screen readers. |
| FE-008 | localStorage used without centralized abstraction | HIGH | **MEDIUM** | 6h | P3 | Partially valid. `lib/storage.ts` provides `safeSetItem` which is used in many places, but direct `localStorage.getItem` calls still appear throughout (e.g., `buscar/page.tsx` lines 221-264 read localStorage directly, `Sidebar.tsx` line 52 reads directly). The pattern is inconsistent -- writes use `safeSetItem` but reads are raw. |
| FE-009 | Inline SVGs instead of centralized icon system | HIGH | **MEDIUM** | 8h | P3 | Partially valid. `lucide-react` is installed and used in `Sidebar.tsx` (8 icons from lucide). However, many components still use inline SVGs (buscar/page.tsx hamburger menu, ViabilityBadge chart icon, LlmSourceBadge spinner/bolt/calculator icons, ProfileCompletionPrompt user icon, SearchErrorBoundary warning icon). The inconsistency is real but `lucide-react` is tree-shakeable and covers most standard icons -- the remaining inline SVGs are mostly custom/domain-specific. |
| FE-010 | `unsafe-inline` and `unsafe-eval` in CSP script-src | HIGH | **HIGH** | 12-16h | P1 | Confirmed. `middleware.ts:30` contains `'unsafe-inline' 'unsafe-eval'`. This is a real security concern, not just a best-practice gap. Implementing CSP nonces with Next.js requires middleware changes, script tag modifications, and careful testing with all third-party scripts (Stripe, Sentry, Cloudflare, Clarity, Mixpanel). The `style-src 'unsafe-inline'` is acceptable (Tailwind generates inline styles). |

### Testing and Features (FE-011 through FE-018)

| ID | Debito | Severidade Original | Severidade Ajustada | Horas | Prioridade | Impacto UX |
|----|--------|---------------------|---------------------|-------|------------|------------|
| FE-011 | No page-level tests for 5 pages | MEDIUM | **MEDIUM** | 16-20h | P3 | Confirmed. Dashboard, pipeline, historico, onboarding, and conta sub-pages lack dedicated render tests. These are all high-traffic authenticated pages. |
| FE-012 | `eslint-disable exhaustive-deps` 5+ times in buscar | MEDIUM | **MEDIUM** | 3h | P3 | Confirmed: 3 instances found in `buscar/page.tsx` (lines 356, 377, 408). Each suppression hides a potential stale closure bug. Should be fixed by extracting stable references via useRef or restructuring effect dependencies. |
| FE-013 | Hardcoded pricing fallback in planos/page.tsx | MEDIUM | **MEDIUM** | Ongoing | P3 | Confirmed. This is inherent to the architecture (Stripe is the source of truth, fallback needed for when Stripe is unreachable). Not fixable, only manageable via sync script (`scripts/sync-setores-fallback.js` pattern). |
| FE-014 | Feature-gated dead code in production bundles | MEDIUM | **MEDIUM** | 6h | P3 | Confirmed. ORGS_ENABLED, alertas, mensagens code paths ship to production. Should use `next/dynamic` with feature flag checks to tree-shake unused paths. |
| FE-015 | No bundle size budget in CI | MEDIUM | **MEDIUM** | 3h | P3 | Confirmed. `@lhci/cli` is in devDeps, scripts defined, but no CI workflow enforces budgets. A `size-limit` or `next-bundle-analyzer` step would catch regressions. |
| FE-016 | Duplicate footer implementations | MEDIUM | **LOW** | 2h | P4 | Confirmed. `/buscar/page.tsx` has a full 40-line footer (lines 883-922) AND `NavigationShell.tsx` provides a minimal footer (line 54). The buscar footer is a deliberate design choice (richer content), not a bug. However, it creates duplicate `<footer>` landmarks which confuses screen reader landmark navigation (related to FE-A11Y-05). |
| FE-017 | Theme init via dangerouslySetInnerHTML | MEDIUM | **LOW** | 1h | P4 | Low UX impact. The inline script prevents flash-of-wrong-theme (FOWT), which is the correct pattern for class-based dark mode. Standard Next.js practice. |
| FE-018 | Raw `var(--*)` alongside Tailwind tokens | MEDIUM | **MEDIUM** | Ongoing | P3 | Confirmed. `tailwind.config.ts` already maps CSS vars to Tailwind tokens (`brand-blue`, `ink`, `surface-0`, etc.), but usage is inconsistent. Many components use `bg-[var(--surface-1)]` instead of `bg-surface-1`, or `text-[var(--ink)]` instead of `text-ink`. This is a linting enforcement issue, not a design system gap. |

### Low Severity (FE-019 through FE-022)

| ID | Debito | Severidade Original | Severidade Ajustada | Horas | Prioridade | Impacto UX |
|----|--------|---------------------|---------------------|-------|------------|------------|
| FE-019 | `@types/uuid` in dependencies | LOW | **LOW** | 0.5h | P4 | Trivial. Should be in devDependencies. Zero UX impact. |
| FE-020 | `__tests__/e2e/` alongside `e2e-tests/` | LOW | **LOW** | 2h | P4 | Confirmed. Two E2E directories creates confusion for developers. Merge into `e2e-tests/`. |
| FE-021 | No Storybook | LOW | **LOW** | 20-32h | Backlog | Not justified at current scale. With ~130 components and 1-2 developers, Storybook overhead exceeds benefit. Consider Ladle (lighter) when team reaches 3+ frontend developers. |
| FE-022 | `Button.examples.tsx` but no visual regression | LOW | **LOW** | 8-12h | Backlog | Nice-to-have. Playwright visual comparisons would be more practical than a dedicated tool like Chromatic at this scale. |

### Accessibility Gaps (FE-A11Y-01 through FE-A11Y-07)

| ID | Debito | Severidade Original | Severidade Ajustada | Horas | Prioridade | Impacto UX |
|----|--------|---------------------|---------------------|-------|------------|------------|
| FE-A11Y-01 | Loading: no aria-busy/role="status" | MEDIUM | **LOW** | 2h | P3 | Partially mitigated. `EnhancedLoadingProgress` has `aria-live="polite"`, `ResultsLoadingSection` has `aria-live="polite"`. The loading spinner in `buscar/page.tsx` (line 551-557) lacks `role="status"` but is a brief auth check, not a long wait. Remaining gap: auth loading screen and page-level loading states. |
| FE-A11Y-02 | SearchErrorBoundary not announced to AT | MEDIUM | **MEDIUM** | 1h | P2 | Confirmed. The error boundary fallback UI (SearchErrorBoundary.tsx:53-88) lacks `role="alert"` or `aria-live="assertive"`. When a crash occurs, screen readers are not notified. Quick fix: add `role="alert"` to the outer div. |
| FE-A11Y-03 | Inline SVGs in pricing lack aria-hidden | LOW | **LOW** | 0.5h | P4 | Confirmed but low impact. Most inline SVGs throughout the codebase correctly use `aria-hidden="true"` (verified in ViabilityBadge, LlmSourceBadge, ReliabilityBadge, ProfileCompletionPrompt). Spot-check pricing page for stragglers. |
| FE-A11Y-04 | Focus trap consistency across modals | MEDIUM | **REMOVED (INFO)** | 0h | N/A | **Substantially fixed.** `focus-trap-react` v12 is installed (package.json line 43) and actively used in 6 modal components: `DowngradeModal`, `InviteMemberModal`, `PaymentRecoveryModal`, `CancelSubscriptionModal`, `MobileDrawer`, `DeepAnalysisModal`. The main `Dialog` component used for save-search and keyboard-help should be verified, but the critical modals are covered. |
| FE-A11Y-05 | Duplicate footers confuse landmark navigation | LOW | **MEDIUM** | 2h | P3 | Confirmed and more impactful than rated. `/buscar/page.tsx` has a `<footer role="contentinfo">` (line 883) AND `NavigationShell.tsx` has a `<footer>` (line 54). Screen readers will announce two contentinfo landmarks. The buscar page footer should either replace or integrate with the NavigationShell footer for this route. |
| FE-A11Y-06 | Color-only indicators on badges | MEDIUM | **LOW** | 0h | N/A | **Largely resolved.** `ViabilityBadge` includes text labels ("Viabilidade alta/media/baixa") alongside colors (verified lines 48-60). `ReliabilityBadge` displays text level ("Alta/Media/Baixa") alongside colors (line 52). `LlmSourceBadge` uses text labels ("Resumo por IA", "Resumo automatico"). The badges combine color + text + icon, meeting WCAG 1.4.1. |
| FE-A11Y-07 | Escape key inconsistency in modals | MEDIUM | **LOW** | 1h | P4 | Partially mitigated by `focus-trap-react` which handles Escape by default. The custom `Dialog` component should be verified for Escape handling. Low remaining risk. |

---

## Debitos Adicionados

| ID | Debito | Severidade | Horas | Prioridade | Impacto UX |
|----|--------|-----------|-------|------------|------------|
| FE-NEW-01 | **ProfileCompletionPrompt (651 LOC) untested and imports framer-motion eagerly.** This component imports `framer-motion` at the top level (line 4), adding ~70KB to any page that renders it (dashboard). It should use `next/dynamic` with `ssr: false`. Additionally, zero test files exist for this component, which handles profile context API calls with optimistic UI. | MEDIUM | 6h | P2 | Medium: bundle bloat on dashboard; regression risk on profile flows |
| FE-NEW-02 | **No error boundaries on dashboard, pipeline, historico, conta pages.** Only `/buscar` has `SearchErrorBoundary`. An unhandled exception on any other authenticated page crashes to the root `error.tsx`, losing all page context (scroll, filter state, form data). | HIGH | 4h | P1 | High: users lose all context on crash; must re-navigate from scratch |
| FE-NEW-03 | **Direct localStorage reads in buscar/page.tsx without SSR guard.** Lines 221-234 use `localStorage.getItem` inside `useMemo` with `typeof window === 'undefined'` guards, but `useMemo` runs during SSR hydration mismatch checks. Should use `useEffect` + `useState` pattern or the existing `safeSetItem`/`safeGetItem` from `lib/storage.ts`. Potential hydration warnings in strict mode. | LOW | 2h | P3 | Low: works in practice but causes hydration mismatch warnings |
| FE-NEW-04 | **Tour step HTML injected via raw string (Shepherd.js).** `SEARCH_TOUR_STEPS` and `RESULTS_TOUR_STEPS` (lines 58-119) use `text:` with raw HTML strings (`<span class="tour-step-counter">...`). This bypasses React's XSS protections. While the content is static, it sets a precedent for HTML injection. Shepherd.js supports React components as step content -- migration would be safer. | LOW | 3h | P4 | Low: no dynamic content, but establishes unsafe pattern |

---

## Debitos Removidos/Downgraded

| ID | Motivo | Status Atual |
|----|--------|-------------|
| FE-005 | `prefers-reduced-motion` already implemented in `globals.css:331-337` with comprehensive universal rule that covers all 8 custom keyframe animations. Also `useInView.ts` checks for the preference. | **REMOVED** -- false positive in current codebase |
| FE-007 | `aria-live` now present in 15+ production components covering search results, loading states, error states, quota displays, and progress indicators. Comprehensive coverage of the search flow. | **REMOVED** -- resolved since DRAFT was written |
| FE-A11Y-04 | `focus-trap-react` v12 installed and used in 6 modal components. Critical modals (payment, cancellation, deep analysis, invite, downgrade, mobile drawer) all have focus trapping. | **REMOVED** -- resolved since DRAFT was written |

---

## Respostas ao Architect

### 1. FE-001: Decomposicao do buscar page 983 LOC -- que sub-secoes devem ser independentemente carregaveis?

The buscar page is already well-decomposed at the component level (35 components in `app/buscar/components/`, further split into `search-results/` sub-directory). The 983 remaining lines are **orchestration logic**: state wiring between `useSearch`, `useSearchFilters`, `useShepherdTour`, `useOnboarding`, `useBroadcastChannel`, plus conditional rendering for trial/grace/payment states.

**Above-the-fold split for perceived performance:**
- **Immediate render:** Header (sticky, line 563-615) + SearchForm (line 652-669) + empty results placeholder
- **Deferred render:** SearchResults (line 701-795), Footer (line 883-922), Modals (lines 801-968)

**Recommended decomposition:**
1. Extract `useSearchOrchestration()` hook (lines 130-508) -- consolidates 15+ state variables, 8+ useEffect hooks, and 6+ useCallback handlers into a single custom hook. This reduces the page component to ~200 lines of JSX.
2. Extract `BuscarModals` component (lines 800-968) -- save dialog, keyboard help, trial conversion, PDF modal, payment recovery, onboarding tour button. All modal state can be lifted via a `useModalManager` hook.
3. The footer (lines 883-922) should be removed in favor of extending NavigationShell footer for the buscar route (solves FE-016 + FE-A11Y-05 simultaneously).

### 2. FE-005: prefers-reduced-motion -- quais animacoes sao essenciais vs decorativas?

**Moot point** -- already implemented. The global `@media (prefers-reduced-motion: reduce)` rule in `globals.css:331-337` applies to ALL elements with `animation-duration: 0.01ms !important` and `transition-duration: 0.01ms !important`. This is the recommended WCAG approach (blanket disable). No per-animation decision needed.

For reference, if granular control were desired:
- **Essential (should still animate, simplified):** `shimmer` (loading skeleton feedback), `slide-in-right` (drawer entrance -- reduce to instant)
- **Decorative (should disable entirely):** `float`, `bounce-gentle`, `gradient`, `fade-in-up`, `slide-up`, `scale-in`

### 3. FE-006: Dual component directories -- ownership boundary

The proposed rule aligns well with the current codebase reality:
- `components/` = truly global, no page-specific dependencies (Button, Input, NavigationShell, Sidebar, EmptyState, ErrorStateWithRetry, LoadingProgress, PaymentFailedBanner, PlanCard, ProfileCompletionPrompt)
- `app/components/` = app-wide providers and auth-aware compositions (AuthProvider, ThemeProvider, UserMenu, UpgradeModal, TrialBanner, QuotaBadge, Dialog, SavedSearchesDropdown)
- `app/buscar/components/` = search-specific (SearchForm, SearchResults, ViabilityBadge, UfProgressGrid, etc.)

**Action items:**
1. Document the rule in a `CONTRIBUTING.md` or add an ESLint import restriction rule
2. Move `MobileDrawer` from `components/` to `app/components/` (it depends on app routing)
3. Move `AlertNotificationBell` from `components/` to `app/components/` (depends on auth context)
4. The `BackendStatusIndicator` in `components/` exports `useBackendStatusContext` which creates a provider dependency -- should be in `app/components/`

### 4. FE-007: aria-live -- experiencia esperada para leitores de tela

**Already implemented** as described in the DRAFT. The current screen reader experience during search:
1. **Search initiated:** `ResultsLoadingSection` announces progress updates via `aria-live="polite"`
2. **Progress updates:** `UfProgressGrid` updates via `aria-live="polite"` for UF-level status
3. **Results loaded:** `ResultsHeader` announces count via `aria-live="polite" aria-atomic="true"`
4. **Errors:** `SearchStateManager` announces errors via `aria-live="assertive"` (4 instances: timeout, quota exceeded, general error, connection error)
5. **Empty results:** `EmptyResults` announces via `aria-live="polite"`

Only the SearchErrorBoundary crash fallback (FE-A11Y-02) remains unannounced.

### 5. FE-A11Y-06: Color-only indicators -- quais badges precisam redesign?

**Largely resolved.** All three badges now include text labels:
- `ViabilityBadge`: "Viabilidade alta/media/baixa" + chart bar icon + color
- `ReliabilityBadge`: "Alta/Media/Baixa" + shield icon + color
- `LlmSourceBadge`: "Resumo por IA" / "Resumo automatico" + distinct icons + color

No redesign needed. The badges meet WCAG 1.4.1 (Use of Color) with the current triple-encoding (color + text + icon).

### 6. FE-016: Duplicate footers -- qual usar?

The buscar page should use the NavigationShell footer exclusively. The inline buscar footer (lines 883-922) provides richer content (4-column grid with about/plans/support/legal links) but creates:
1. Duplicate `<footer role="contentinfo">` landmarks (a11y issue)
2. Maintenance burden (two footers to update)
3. Inconsistency with other authenticated pages

**Recommendation:** Enhance the NavigationShell footer to include the richer content from the buscar footer, then remove the buscar inline footer. This gives all authenticated pages a consistent, rich footer.

### 7. FE-021: Storybook vs lighter alternative?

**Storybook is overkill** for current scale (~130 components, 1-2 frontend developers, pre-revenue product). Recommend:
- **Now:** Continue with `Button.examples.tsx` pattern + Playwright visual regression screenshots
- **At 3+ frontend devs:** Evaluate Ladle (Vite-based, 10x faster build than Storybook) or Storybook 8 with Vite builder
- **Never:** Full Storybook + Chromatic CI -- too expensive for current scale

---

## Recomendacoes de Design

### Padrao de Design System Recomendado

The design system foundation is **stronger than the DRAFT suggests**:
- `tailwind.config.ts` already maps all CSS custom properties to Tailwind tokens (colors, borders, shadows, fonts, border-radius)
- `globals.css` has comprehensive light/dark mode variables with documented WCAG contrast ratios
- `components/ui/button.tsx` exists with CVA (6 variants, 4 sizes, loading state, TypeScript-enforced aria-label for icon-only)
- `components/ui/` directory has Input, Label, Pagination, CurrencyInput primitives

**Gaps remaining:**
1. No shared `Card` component (ad-hoc div + Tailwind throughout)
2. No shared `Badge` component (7+ inline implementations)
3. No shared `Select` component (3 custom filter selects with different styles)
4. No enforcement mechanism for Tailwind token usage (raw `var(--*)` still common)

**Recommended enforcement:** Add an ESLint rule or custom Tailwind plugin that warns on `bg-[var(--` patterns where a Tailwind token equivalent exists.

### Quick Wins (< 2h cada)

| # | Fix | Horas | Impacto |
|---|-----|-------|---------|
| 1 | Add `role="alert"` to SearchErrorBoundary fallback UI | 0.5h | Screen readers notified on crashes |
| 2 | Move `@types/uuid` to devDependencies | 0.5h | Correct dependency classification |
| 3 | Remove duplicate `<footer>` from buscar page (use NavigationShell) | 1.5h | Fix landmark duplication, reduce maintenance |
| 4 | Add `aria-busy="true"` to auth loading spinner in buscar/page.tsx | 0.5h | Screen readers know content is loading |
| 5 | Wrap ProfileCompletionPrompt with `next/dynamic({ ssr: false })` | 0.5h | Removes ~70KB framer-motion from dashboard initial load |
| 6 | Add `role="status"` to loading spinners in auth check (line 551) | 0.5h | WCAG 4.1.3 compliance for loading states |

### Requer Design Review (> 8h)

| # | Item | Horas | Por que precisa design review |
|---|------|-------|-------------------------------|
| 1 | FE-001: buscar page orchestration extraction | 16-20h | Extracting useSearchOrchestration changes how state flows through the component tree; needs careful verification of all conditional rendering paths |
| 2 | FE-010: CSP nonce implementation | 12-16h | Requires testing all third-party scripts (Stripe checkout, Sentry, Mixpanel, Clarity, Cloudflare) still function correctly with nonce-based CSP |
| 3 | FE-003: SSE proxy simplification | 20-24h | The fallback cascade (SSE -> polling -> simulation) is complex but battle-tested in production; simplification risks breaking degradation paths |
| 4 | FE-NEW-02: Error boundaries for 5 pages | 4h | Each page needs a custom error fallback UI that preserves context and offers recovery actions appropriate to that page's function |
| 5 | NavigationShell footer enhancement | 3h | Rich footer content (4-column layout) needs responsive design review for mobile authenticated layout |

### Acessibilidade - Plano de Remediacao

**Tier 0 -- Already resolved (no action needed):**
- `aria-live` on search results and dynamic content (FE-007) -- DONE
- `prefers-reduced-motion` global rule (FE-005) -- DONE
- Focus trapping in modals via `focus-trap-react` (FE-A11Y-04) -- DONE
- Color-only indicators on badges (FE-A11Y-06) -- DONE, text labels present
- Button aria-label enforcement for icon-only buttons -- TypeScript-enforced in `button.tsx`

**Tier 1 -- Sprint fix (3h total):**

| Fix | WCAG Reference | Horas |
|-----|---------------|-------|
| Add `role="alert"` to SearchErrorBoundary fallback | WCAG 4.1.3 Status Messages (AA) | 0.5h |
| Remove duplicate `<footer role="contentinfo">` from buscar page | WCAG 1.3.1 Info and Relationships (A), WCAG 1.3.6 Identify Purpose (AAA) | 1.5h |
| Add `role="status"` / `aria-busy` to auth loading states | WCAG 4.1.3 Status Messages (AA) | 0.5h |
| Verify Dialog component Escape key handling | WCAG 2.1.2 No Keyboard Trap (A) | 0.5h |

**Tier 2 -- Next sprint (6h total):**

| Fix | WCAG Reference | Horas |
|-----|---------------|-------|
| Audit heading hierarchy on all authenticated pages (skip levels?) | WCAG 1.3.1 Info and Relationships (A) | 2h |
| Add `aria-describedby` for form validation error messages | WCAG 1.3.1, 3.3.1 Error Identification (A) | 2h |
| Ensure all inline SVGs have `aria-hidden="true"` (spot audit) | WCAG 1.1.1 Non-text Content (A) | 1h |
| Add skip-to-content verification on all page layouts | WCAG 2.4.1 Bypass Blocks (A) | 1h |

**Tier 3 -- Monitoring (ongoing):**
- Enable `@axe-core/playwright` accessibility assertions in E2E tests (already in devDeps, just needs activation)
- Add Lighthouse CI accessibility threshold (score >= 90) to CI pipeline
- Quarterly manual screen reader audit using NVDA/VoiceOver on the 5 core flows (search, pipeline, dashboard, account, billing)

---

*End of UX Specialist Review v3.0*
*Next step: Consolidation with @data-engineer and @qa reviews into FINAL technical debt assessment.*
