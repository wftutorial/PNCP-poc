# UX Specialist Review

**Reviewer:** @ux-design-expert (Pixel)
**Data:** 2026-03-10
**Fonte:** docs/prd/technical-debt-DRAFT.md (Section 3 + Appendix A/C), docs/frontend/frontend-spec.md
**Supersedes:** ux-specialist-review.md v3.0 (2026-03-09)
**Codebase Snapshot:** branch `main`, commit `f7db269f` (DEBT-111)

---

## Gate Status: VALIDATED

The reconciled DRAFT v2 (2026-03-10) already moved 7 resolved FE items to Appendix A. After verifying the actual codebase state of every remaining item, I confirm that the DRAFT is now **substantially accurate**. The remaining 15 frontend items plus 7 A11Y items plus 4 Appendix C items are real. I adjust severities, add hour estimates, assign GTM priorities, and identify 3 new findings below.

---

## Items Already Fixed (confirmed in Appendix A -- remove from active debt)

| ID | Fixed In | Evidence |
|----|----------|----------|
| FE-001 | DEBT-106 | `app/buscar/page.tsx` is 270 LOC (verified via `wc -l`). Decomposed into `useSearchOrchestration` + `BuscarModals` aggregator. |
| FE-002 | DEBT-105/106 | `next/dynamic` confirmed in 8 files: pipeline (dnd-kit), dashboard (Recharts x3), login (TOTP), buscar (SearchStateManager), blog (MDX). |
| FE-005 | DEBT-105 | `globals.css:331` has `@media (prefers-reduced-motion: reduce)` with blanket `animation-duration: 0.01ms !important`. Also `useInView.ts` checks preference. |
| FE-007 | DEBT-105 | `aria-live` present in 29 components (verified via grep: 51 occurrences across 29 files). Search flow fully covered. |
| FE-010 | DEBT-108 | `middleware.ts:45` uses `nonce-${nonce}` + `strict-dynamic`. Old `unsafe-inline`/`unsafe-eval` kept only as rollback comment. `style-src 'unsafe-inline'` remains (acceptable for Tailwind). |
| FE-012 | DEBT-111 | 0 `eslint-disable` in `app/buscar/`. 3 remaining in source files: `MunicipioFilter.tsx` (no-explicit-any), `OrgaoFilter.tsx` (no-explicit-any), `EnhancedLoadingProgress.tsx` (no-unused-vars). Plus several in test files. |
| FE-015 | DEBT-108 | `.size-limit.js` exists with 250KB gzipped budget, CI-enforced. |

These items are correctly in the Appendix. No action needed.

---

## Items Validated (STILL OPEN)

### From DRAFT Section 3 (remaining items)

| ID | Status | Adjusted Severity | Hours | GTM Priority | UX Impact |
|----|--------|-------------------|-------|--------------|-----------|
| FE-003 | CONFIRMED | HIGH | 20-24h | POST-GTM | SSE proxy has 3 fallback paths (SSE, polling, time-simulation) with multiple retry strategies. Working in production. Refactoring risk is high -- document and test before restructuring. Not a GTM blocker because it works, just hard to maintain. |
| FE-004 | CONFIRMED | MEDIUM (was HIGH) | Ongoing | POST-GTM | Coverage thresholds at 50/55/55/55% (verified in jest.config.js). Target is 60%. For B2G users this has zero direct impact; it increases regression risk for developers. Not a GTM blocker. |
| FE-006 | CONFIRMED | MEDIUM (was HIGH) | 4-6h | GTM-RISK | Dual directories: `app/components/` (48 items), `components/` (34 items). The split is actually semi-logical (global primitives vs app-aware compositions) but undocumented. New developers will misplace files. Fix is documenting the convention + moving 3-4 misplaced files, not a full reorg. |
| FE-008 | PARTIALLY FIXED | LOW (was HIGH) | 3h | POST-GTM | Raw `localStorage` calls (141 occurrences) vs safe wrappers (133 occurrences). Most raw calls are in test files and `lib/storage.ts` itself. In source files, ~6 files still use raw `localStorage.getItem` directly (`useSearchFilters.ts`, `SearchResults.tsx`, `layout.tsx`, `GoogleAnalytics.tsx`, `ContextualTutorialTooltip.tsx`). Low UX impact since the safe wrappers handle the critical private-browsing case. |
| FE-009 | PARTIALLY FIXED | LOW (was HIGH) | 4h | POST-GTM | Lucide React is the standard icon library and is used throughout Sidebar, navigation, etc. Remaining inline SVGs are in `conta/layout.tsx` (5 nav icons, confirmed no `aria-hidden`) and a few domain-specific icons in badges. The `conta/layout.tsx` inline SVGs are the most visible gap -- 5 standard icons that should be Lucide. |
| FE-011 | CONFIRMED | MEDIUM | 12-16h | GTM-RISK | No page-level tests for dashboard, pipeline, historico, onboarding, conta. These are all high-traffic authenticated pages. At minimum, render-smoke tests should exist before GTM to catch import/SSR crashes. |
| FE-013 | CONFIRMED | LOW (was MEDIUM) | Ongoing | POST-GTM | Hardcoded pricing fallback is inherent to architecture. Managed via sync scripts. Not fixable, only manageable. |
| FE-014 | CONFIRMED | LOW (was MEDIUM) | 6h | POST-GTM | Feature-gated code (alertas, mensagens, organizations) ships in bundles. Bundle budget (250KB) is in place, so this is controlled. Not a GTM concern unless bundle grows past budget. |
| FE-016 | CONFIRMED | LOW (was MEDIUM) | 1.5h | POST-GTM | Documented as intentional per DEBT-111 AC9. Buscar has a richer footer with domain-specific links. Creates duplicate `<footer>` landmarks (a11y concern) but functional. |
| FE-017 | CONFIRMED | INFO (was MEDIUM) | 0h | N/A | Theme init via `dangerouslySetInnerHTML` is standard Next.js dark mode pattern. Uses nonce for CSP. Not a debt item. |
| FE-018 | CONFIRMED | LOW (was MEDIUM) | Ongoing | POST-GTM | Raw `var(--*)` usage alongside Tailwind tokens. 110 raw hex color occurrences across 20 TSX files (verified via grep). Cosmetic inconsistency, not a UX issue for end users. |
| FE-019 | CONFIRMED | INFO | 0.5h | POST-GTM | Trivial: `@types/uuid` in dependencies instead of devDependencies. |
| FE-020 | NO LONGER VALID | N/A | 0h | N/A | `__tests__/e2e/` directory does not exist (verified). Only `e2e-tests/` exists. This item should be removed. |
| FE-021 | CONFIRMED | LOW | 0h (defer) | POST-GTM | No Storybook. Not justified at current team size (1-2 FE devs). Revisit when team reaches 3+. |
| FE-022 | CONFIRMED | INFO | 0h (defer) | POST-GTM | `Button.examples.tsx` exists but no visual regression framework. Nice-to-have, not a GTM concern. |

### Accessibility Items (FE-A11Y-01 through FE-A11Y-07)

| ID | Status | Adjusted Severity | Hours | GTM Priority | UX Impact |
|----|--------|-------------------|-------|--------------|-----------|
| FE-A11Y-01 | PARTIALLY FIXED | LOW (was MEDIUM) | 1h | POST-GTM | Several loading components now have `role="status"` and `aria-busy`: `AuthLoadingScreen`, `dashboard/loading.tsx`, `buscar/loading.tsx`, `(protected)/loading.tsx`, `BackendStatusIndicator`. Remaining gaps are minor (login page spinner, some page-level loading states). |
| FE-A11Y-02 | CONFIRMED | MEDIUM | 0.5h | GTM-RISK | `SearchErrorBoundary.tsx:54` has `role="alert" aria-live="assertive"` on the fallback div. **This item is actually fixed.** Downgrade to REMOVED. |
| FE-A11Y-03 | CONFIRMED | LOW | 0.5h | POST-GTM | Inline SVGs in `conta/layout.tsx` (5 icons) lack `aria-hidden="true"`. Decorative icons should be hidden from AT. Quick fix. |
| FE-A11Y-04 | LARGELY FIXED | INFO | 0h | N/A | `focus-trap-react` is used in 5 modal components: `DeepAnalysisModal`, `InviteMemberModal`, `CancelSubscriptionModal`, `MobileDrawer`, `PaymentRecoveryModal`, `DowngradeModal`. Critical modals are covered. |
| FE-A11Y-05 | CONFIRMED | LOW (was LOW) | 1.5h | POST-GTM | Duplicate `<footer>` landmarks on buscar page. Real a11y issue but low practical impact for B2G users (unlikely to use landmark navigation). |
| FE-A11Y-06 | FIXED | N/A | 0h | N/A | Badges all include text labels alongside colors. `ViabilityBadge`, `ReliabilityBadge`, `LlmSourceBadge` all use triple-encoding (color + text + icon). Meets WCAG 1.4.1. Remove from debt list. |
| FE-A11Y-07 | LARGELY FIXED | INFO | 0h | N/A | `focus-trap-react` handles Escape by default in all modals using it. Remaining risk is minimal. |

### Appendix C Items (new findings from re-analysis)

| ID | Status | Adjusted Severity | Hours | GTM Priority | UX Impact |
|----|--------|-------------------|-------|--------------|-----------|
| ARCH-006 | CONFIRMED | MEDIUM | 8h | GTM-RISK | `SearchForm.tsx` (687 LOC) and `DataQualityBanner.tsx` (661 LOC) are the largest remaining components after the buscar page decomposition. SearchForm accepts 40+ props -- a sign it should be split into sub-components (form header, filter sections, action buttons). DataQualityBanner at 661 LOC is surprisingly large for a banner and likely contains complex logic that should be extracted. |
| FE-TD-004 | CONFIRMED | MEDIUM | Ongoing | GTM-RISK | Same as FE-004. Coverage 50-55%, target 60%. |
| FE-TD-006 | CONFIRMED | MEDIUM | 4-6h | GTM-RISK | Same as FE-006. Dual component directories. |
| FE-TD-008 | CONFIRMED | LOW | 6h | POST-GTM | 110 raw hex color occurrences across 20 TSX files. Should use Tailwind tokens. Not user-visible. |
| FE-TD-023 | CONFIRMED | MEDIUM | 4h | GTM-RISK | Framer Motion imported in 13 files including authenticated page components (`GlassCard`, `ScoreBar`, `GradientButton`, `ProfileCompletionPrompt`, `ProfileCongratulations`). These pull ~70KB into dashboard and other authenticated page bundles. Should wrap in `next/dynamic` or extract motion-dependent components to dynamic imports. |
| A11Y-001 | CONFIRMED | LOW | 0.5h | POST-GTM | Same as FE-A11Y-03. Inline SVGs without `aria-hidden`. |
| A11Y-002 | FIXED | N/A | 0h | N/A | Same as FE-A11Y-06. Color-only indicators resolved. |

---

## Additional Items to Remove from Debt List

| ID | Reason | Evidence |
|----|--------|----------|
| FE-020 | `__tests__/e2e/` directory does not exist | `ls` returns empty; only `e2e-tests/` exists |
| FE-A11Y-02 | SearchErrorBoundary already has `role="alert" aria-live="assertive"` | Verified in SearchErrorBoundary.tsx:54 |
| FE-A11Y-04 | `focus-trap-react` used in 5+ modals | Package.json + 5 modal files confirmed |
| FE-A11Y-06 | All badges have text labels | ViabilityBadge, ReliabilityBadge, LlmSourceBadge verified |
| FE-A11Y-07 | Escape handled by focus-trap-react | Default behavior in library |
| A11Y-002 | Duplicate of FE-A11Y-06, already fixed | Same evidence |
| FE-017 | Not a debt item | Standard dark mode FOWT prevention pattern with CSP nonce |

---

## New UX Findings

| ID | Finding | Severity | Hours | GTM Priority | UX Impact |
|----|---------|----------|-------|--------------|-----------|
| FE-NEW-01 | **Framer Motion in authenticated page bundles.** `GlassCard`, `ScoreBar`, `GradientButton`, `ProfileCompletionPrompt`, `ProfileCongratulations` all statically import `framer-motion`. These are used on `/dashboard` and other authenticated pages. Since the landing page is the only page that benefits from framer-motion animations, authenticated pages pay ~70KB for minor hover/entrance effects that could use CSS transitions instead. | MEDIUM | 6h | GTM-RISK | ~70KB unnecessary JS on authenticated pages. Dashboard perceived load time affected. |
| FE-NEW-02 | **`conta/layout.tsx` inline SVGs without `aria-hidden`.** The 5 navigation icons (user, shield, credit-card, database, users) are all inline SVGs without `aria-hidden="true"`. Screen readers will attempt to describe these decorative path elements. Also, these are standard icons available in Lucide React. | LOW | 1h | POST-GTM | Minor a11y issue. Screen readers read SVG paths. |
| FE-NEW-03 | **No error boundaries on dashboard, pipeline, historico pages.** Only `/buscar` has `SearchErrorBoundary`. The root `error.tsx` catches crashes on other pages but loses all page context (scroll position, filter state, form data). For B2G users working through a pipeline of opportunities, losing pipeline state on a transient error is disruptive. | HIGH | 4h | GTM-BLOCKER | Users lose all in-progress work on unhandled exception. Recovery requires full page reload and re-navigation. |

---

## Answers to Architect Questions

### 1. FE-001: Which sub-sections of the search page should be independently loadable?

**Moot -- already decomposed.** The buscar page is now 270 LOC (DEBT-106). The decomposition created `useSearchOrchestration` hook + `BuscarModals` aggregator. The remaining code is JSX composition of well-separated components.

However, the next decomposition targets should be the **sub-components** that are now the largest files:
- `SearchForm.tsx` (687 LOC, 40+ props) -- split into `SearchFormHeader`, `SearchFilterAccordion`, `SearchFormActions`
- `DataQualityBanner.tsx` (661 LOC) -- extract rule logic into a `useDataQualityRules` hook, keep the banner as a thin presenter

**Above-the-fold split for perceived performance:** The SearchForm (sticky header) + empty state should render immediately. SearchResults and all banners/modals can be deferred until data arrives. This is already the natural behavior since results are fetched asynchronously.

### 2. FE-005: Which animations are essential vs decorative?

**Already resolved.** The global `@media (prefers-reduced-motion: reduce)` in `globals.css:331` applies a blanket `animation-duration: 0.01ms !important` to all elements. No per-animation decision is needed.

For the record, the classification would be:
- **Essential (should simplify, not remove):** `shimmer` (loading skeleton feedback provides visual continuity)
- **Decorative (disable entirely):** `float`, `bounce-gentle`, `gradient`, `fade-in-up`, `slide-up`, `scale-in`, `slide-in-right`

### 3. FE-006: Component directory ownership boundary

The proposed rule is correct and aligns with the existing organic structure:
- `components/` = truly global primitives used by 3+ pages (Button, Input, NavigationShell, Sidebar, ErrorBoundary, LoadingProgress)
- `app/components/` = app-aware shared components (AuthProvider, ThemeProvider, UpgradeModal, QuotaBadge, Footer, landing sections)
- `app/{page}/components/` = page-local (buscar components, dashboard components, pipeline components)

**Concrete actions:**
1. Document this rule in the project (CONTRIBUTING.md or a code comment in each directory)
2. Move `BackendStatusIndicator` from `components/` to `app/components/` (it exports a context provider, so it is app-aware)
3. Move `AlertNotificationBell` from `components/` to `app/components/` (depends on auth context)
4. Add an ESLint `no-restricted-imports` rule to prevent page-local components from being imported outside their page directory

### 4. FE-007: Expected screen reader experience during search

**Already implemented.** The current flow:
1. Search button pressed: button gets `aria-busy="true"`
2. Loading phase: `EnhancedLoadingProgress` announces via `aria-live="polite"` with percentage
3. Per-UF progress: `UfProgressGrid` updates via `aria-live="polite"`
4. Results loaded: `ResultsHeader` announces count via `aria-live="polite" aria-atomic="true"`
5. Errors: `SearchStateManager` announces via `aria-live="assertive"` (4 distinct error types)
6. Empty results: `EmptyResults` announces via `aria-live="polite"`
7. Crash: `SearchErrorBoundary` announces via `role="alert" aria-live="assertive"`

**Recommendation:** Only announce the final result count and errors. Intermediate progress updates via `aria-live="polite"` are fine -- "polite" means they queue and do not interrupt, so the screen reader user gets the count when the reader finishes its current utterance.

### 5. FE-A11Y-06: Which badges need redesign?

**None.** All three badge types already use triple-encoding:
- `ViabilityBadge`: color (green/yellow/red) + text label ("alta/media/baixa") + chart icon
- `ReliabilityBadge`: color + text level + shield icon
- `LlmSourceBadge`: color + descriptive text + distinct icon per source type

This meets WCAG 1.4.1 (Use of Color). Remove this item from the debt list.

### 6. FE-016: Should buscar use NavigationShell footer exclusively?

**Yes, long-term.** The buscar-specific footer (with domain links like "Sobre", "Planos", "Suporte", "Termos") provides value but creates duplicate `<footer>` landmarks. The recommended approach:
1. Enhance the NavigationShell footer to accept optional "rich content" props
2. Each page can pass page-specific footer links if needed
3. Only one `<footer>` element renders per page

However, this is documented as intentional (DEBT-111 AC9) and has low practical impact. Classify as POST-GTM.

### 7. FE-021: Storybook vs lighter alternative?

**Neither, for now.** At the current scale (~130 components, 1-2 FE developers, pre-revenue), the overhead of any component documentation tool exceeds the benefit. The `Button.examples.tsx` pattern is sufficient.

**Recommended timeline:**
- **Now:** Continue `*.examples.tsx` pattern for key primitives. Use Playwright visual regression screenshots in E2E tests.
- **3+ frontend developers:** Evaluate Ladle (Vite-based, fast, minimal config) or Storybook 8 with Vite builder.
- **5+ developers or design system consumption by external teams:** Full Storybook + Chromatic CI.

---

## GTM Priority Summary

### GTM-BLOCKER (must fix before paid users)

| ID | Item | Hours |
|----|------|-------|
| FE-NEW-03 | Error boundaries on dashboard, pipeline, historico pages | 4h |

**Total: 4h**

Rationale: A paying B2G user working through their opportunity pipeline who hits an unhandled exception loses all state and must re-navigate. This is unacceptable for a paid product. Wrap each authenticated page in an error boundary with contextual recovery.

### GTM-RISK (fix within 30 days of launch)

| ID | Item | Hours |
|----|------|-------|
| FE-006 / FE-TD-006 | Document component directory convention + move 3-4 files | 4-6h |
| FE-011 | Add render-smoke tests for dashboard, pipeline, historico, onboarding, conta | 12-16h |
| FE-TD-023 / FE-NEW-01 | Dynamic-import or CSS-ify framer-motion on authenticated pages | 4-6h |
| ARCH-006 | Split SearchForm.tsx (687 LOC) into sub-components | 6-8h |

**Total: 26-36h**

Rationale: These items affect either developer velocity (directory convention, test coverage) or user-perceived performance (framer-motion bundle, SearchForm maintainability). None will cause data loss or security issues, but they increase the risk of regressions during the rapid iteration period after GTM launch.

### POST-GTM (fix incrementally)

All remaining items: FE-003, FE-004, FE-008, FE-009, FE-013, FE-014, FE-016, FE-018, FE-019, FE-021, FE-022, FE-TD-008, FE-A11Y-01, FE-A11Y-03, FE-A11Y-05, FE-NEW-02.

---

## Design Recommendations

### 1. Error Boundary Strategy for Authenticated Pages

Each authenticated page should have a lightweight error boundary that:
- Preserves the navigation shell (sidebar/bottom nav remain functional)
- Shows a contextual error message ("Erro ao carregar o pipeline")
- Offers a "Tentar novamente" button that resets the error boundary
- Reports to Sentry with page context
- Does NOT clear any localStorage/SWR cache

Implementation: Create a generic `PageErrorBoundary` component in `components/` that wraps page content, not the layout.

### 2. Framer Motion Isolation

Instead of removing framer-motion entirely from authenticated pages (which would remove subtle polish), isolate it:
1. Replace `GlassCard`, `ScoreBar`, `GradientButton` hover effects with CSS `transition` + `transform` (identical visual result, zero JS)
2. Keep `motion.div` usage only in `SearchStateManager` (already dynamically imported) and landing page components
3. `ProfileCompletionPrompt` and `ProfileCongratulations` entrance animations can use CSS `@keyframes fade-in-up` (already defined in globals.css)

This reduces framer-motion to landing-page-only, saving ~70KB on authenticated page bundles.

### 3. SearchForm Decomposition

`SearchForm.tsx` at 687 LOC with 40+ props is the next decomposition target after the successful buscar page split. Recommended structure:

```
SearchForm (container, ~100 LOC)
  -> SearchFormHeader (sector select, search terms input)
  -> SearchFilterPanel (UF selector, date range, value range, modalidade)
  -> SearchFormActions (search button, saved searches dropdown, keyboard shortcut hint)
```

Each sub-component receives only its relevant props, reducing the prop-drilling surface.

### 4. Hex Color Cleanup

110 raw hex colors across 20 files. Most are in:
- `signup/page.tsx` (10 occurrences) -- social button colors
- `privacidade/page.tsx` (14 occurrences) -- legal page styling
- `ThemeProvider.tsx` (29 occurrences) -- theme definition (appropriate use)
- `login/page.tsx` (5 occurrences) -- social button colors

Action: The ThemeProvider occurrences are correct (they define the CSS variables). For remaining files, replace with `var(--*)` references or Tailwind tokens. The social button colors (Google blue, GitHub black) are inherently hardcoded and can stay as hex in a constants file.

---

*End of UX Specialist Review v4.0*
*Reviewer: @ux-design-expert (Pixel), Phase 6 Brownfield Discovery*
*Next step: Consolidation with @data-engineer (Phase 5) and @qa (Phase 7) reviews into FINAL assessment*
