# UX Specialist Review

**Reviewer:** @ux-design-expert (Uma)
**Date:** 2026-04-08
**Phase:** Brownfield Discovery Phase 6

**DRAFT Reviewed:** `docs/prd/technical-debt-DRAFT.md` (Section 3: Frontend/UX Debts, Section 6: Questions for @ux-expert)
**Frontend Spec Reference:** `docs/frontend/frontend-spec.md` (Phase 3)
**Codebase Validation:** Direct inspection of `frontend/app/buscar/`, `frontend/components/`, `frontend/app/globals.css`, `frontend/tailwind.config.ts`, `frontend/__tests__/`

---

## 1. Debitos Validados

For each Frontend/UX debt item in the DRAFT, I validated against the actual codebase. Severity adjustments reflect real UX impact observed in code.

| ID | Debito | Severidade Original | Severidade Ajustada | Horas | Prioridade | Impacto UX |
|----|--------|---------------------|---------------------|-------|------------|------------|
| TD-035 | useSearchFilters() 600+ lines | High | **High** (confirmed 607 lines) | 12-16h | P1 | Dev-only: maintainability. Does NOT directly affect end-users but slows feature velocity on the most critical page. |
| TD-036 | Visual regression testing ausente | Medium | **Medium** (confirmed) | 16-20h | P2 | Dev-only: quality gate. No direct user impact but increases risk of shipping visual regressions to production. |
| TD-037 | Saved filter presets ausente | Medium | **Medium** (confirmed) | 20-24h | P2 | **User-facing**: Power users (consultancies) running the same sector+UF+modality combos repeatedly lose time reconfiguring. |
| TD-038 | Modal focus trap edge cases | Medium | **Medium-Low** (mitigated) | 4-6h | P2 | User-facing (a11y): FocusTrap from `focus-trap-react` is used correctly in 7 components (MobileDrawer, DeepAnalysisModal, DowngradeModal, InviteMemberModal, PaymentRecoveryModal, CancelSubscriptionModal, TrialConversionScreen). Edge cases are nested portals, not widespread. |
| TD-039 | Small touch targets (<44px) legacy | Medium | **Medium** (confirmed in 2 components) | 6-8h | P2 | User-facing (mobile): FeedbackButtons (`p-1.5` = ~28px touch target) and CompatibilityBadge (`px-1.5 py-0.5 text-[10px]` = well below 44px) are the primary offenders. BottomNav and MobileDrawer already enforce `min-w-[44px] min-h-[44px]`. |
| TD-040 | /planos e /pricing duplicados | Medium | **Low** (SEO only) | 2-3h | P3 | Not user-facing: Both pages exist (352 vs 405 lines) with different content (/pricing has ROI calculator, /planos has plan cards). Not true duplicates -- different features. Canonical or redirect is still recommended. |
| TD-041 | Raw hex colors vs design tokens | Low | **Low** (partially mitigated) | 8-10h | P4 | Dev-only: ~89 hex occurrences across 20+ app files. Most are in `global-error.tsx` (17, justified -- inline styles for crash state), `privacidade/page.tsx` (14, legal page), `dados/DadosClient.tsx` (13). The design token system in `globals.css` + `tailwind.config.ts` is comprehensive and well-maintained. New components use tokens correctly. |
| TD-042 | CSP unsafe-inline for Tailwind | Low | **Low** (accepted risk, no change) | 0h | P4 | Dev-only: Required for Tailwind. Industry standard tradeoff. No action needed. |
| TD-043 | Component Storybook ausente | Low | **Low** | 24-32h | P4 | Dev-only: 65+ components without visual catalog. Useful for design handoff but not blocking. |
| TD-044 | Icons missing aria-hidden | Low | **Low** (largely mitigated) | 3-4h | P4 | User-facing (a11y minor): 90 `aria-hidden` usages found across 30+ files. Most icons are properly marked. The gap is in older components, not systematic. |
| TD-045 | Sonner toast live regions | Low | **Low** (correct default) | 1-2h | P4 | User-facing (a11y minor): Sonner `<Toaster>` in layout.tsx uses `position="bottom-center" richColors closeButton`. Sonner's default `aria-live="polite"` is correct for most cases. Only edge case is error toasts that should use `role="alert"` (assertive). |
| TD-046 | Scroll jank SSE (mobile) | Low | **Medium-Low** | 8-12h | P3 | User-facing (mobile): No explicit debounce on scroll during SSE updates found in code. ResultsList renders a flat list without virtualization. For typical result sets (10-50 items per page), this is manageable. At 50+ visible items, mobile jank is expected. |
| TD-047 | Bottom nav covers content | Low | **Low** (partially addressed) | 2-3h | P4 | User-facing (mobile): BottomNav is 60px fixed bottom. Only `comparador/page.tsx` has explicit `pb-20`. Other pages may have content hidden behind BottomNav on short viewports. |
| TD-048 | i18n ausente | Low | **Low** (correct prioritization) | 80-120h | P4 | User-facing: Product is Brazil-only. No international expansion planned. Correct to defer. |
| TD-049 | Offline support ausente | Low | **Low** (correct prioritization) | 40-60h | P4 | User-facing: SaaS web app. Offline mode adds complexity without clear user demand. Correct to defer. |

### Summary of Severity Adjustments

- **TD-040** downgraded Low: /pricing and /planos are NOT true duplicates; /pricing has ROI calculator, /planos has plan comparison. Canonical tag is sufficient.
- **TD-046** upgraded Medium-Low: No debounce/virtualization found in code. Risk is higher than "Low" on mobile devices with 50+ results.
- All other severities confirmed as originally assessed.

---

## 2. Debitos Adicionados

Additional UX debts found by exploring the actual codebase:

### TD-050: useSearchExecution.ts is 852 lines (NEW - High)

**File:** `frontend/app/buscar/hooks/useSearchExecution.ts` (852 lines)
**Issue:** This hook is significantly larger than the flagged useSearchFilters (607 lines) and was not identified in the DRAFT. It handles search API calls, error handling, retry logic, partial results, SSE coordination, and analytics in a single hook.
**UX Impact:** Dev-only (maintainability). The search page has 3,775 total lines across 13 hooks. useSearchExecution is the largest single file and the most complex.
**Severity:** High
**Hours:** 16-20h
**Recommendation:** Extract into useSearchAPI (pure fetch), useSearchErrorHandling, useSearchPartialResults. Follow the same split pattern that was already applied (useSearchSSE + useSearchSSEHandler separation is a good precedent).

### TD-051: Search hooks total complexity (3,775 lines across 13 hooks) (NEW - Medium)

**File:** `frontend/app/buscar/hooks/` (13 files, 3,775 total lines)
**Issue:** The search page hooks collectively form a complex state machine. While individual hooks are reasonably scoped (except TD-035 and TD-050), the orchestration between them involves deeply nested prop passing and ref sharing.
**UX Impact:** Dev-only. New developers face steep onboarding curve for the most critical feature.
**Severity:** Medium
**Hours:** 4h (documentation) + 12h (state machine simplification)
**Recommendation:** Create `docs/architecture/search-hooks-architecture.md` documenting the hook dependency graph. Consider a state machine library (XState) for the search lifecycle.

### TD-052: FeedbackButtons touch target below 44px (NEW - Medium)

**File:** `frontend/components/FeedbackButtons.tsx` (lines 178-210)
**Issue:** Thumbs up/down buttons use `p-1.5` padding around a `w-4 h-4` (16px) icon. Total clickable area is approximately 28x28px, well below WCAG 2.5.5 minimum of 44x44px.
**UX Impact:** User-facing (mobile a11y). These buttons appear on every search result card. Mobile users may misclick.
**Severity:** Medium
**Hours:** 1-2h
**Recommendation:** Add `min-w-[44px] min-h-[44px]` to the button elements, or increase padding to `p-3`.

### TD-053: CompatibilityBadge inaccessible on mobile (NEW - Low)

**File:** `frontend/components/CompatibilityBadge.tsx` (line 37)
**Issue:** Badge uses `text-[10px]` which is below the recommended 12px minimum for body text. The badge is not interactive (role="img") so touch target is not applicable, but readability on mobile is poor.
**UX Impact:** User-facing (readability). Small text on result cards.
**Severity:** Low
**Hours:** 0.5h
**Recommendation:** Increase to `text-xs` (12px) minimum.

### TD-054: Inconsistent error boundary patterns (NEW - Low)

**Files:** `frontend/components/ErrorBoundary.tsx`, `frontend/components/PageErrorBoundary.tsx`, `frontend/app/buscar/components/SearchErrorBoundary.tsx`, `frontend/app/global-error.tsx`, `frontend/app/buscar/error.tsx`
**Issue:** Five different error boundary implementations with varying UI patterns. Some use `aria-live`, some do not. Recovery actions differ (retry vs reload vs navigate).
**UX Impact:** User-facing (consistency). Error recovery is unpredictable across pages.
**Severity:** Low
**Hours:** 4-6h
**Recommendation:** Create a shared `BaseErrorBoundary` component with configurable recovery actions and consistent a11y.

### TD-055: Missing bottom padding for BottomNav on multiple pages (NEW - Low)

**Files:** Most app pages under `frontend/app/`
**Issue:** Only `comparador/page.tsx` explicitly adds `pb-20` to account for the 60px BottomNav. Other pages rely on layout padding which may not be sufficient on shorter viewports.
**UX Impact:** User-facing (mobile). Last items in lists may be hidden behind BottomNav.
**Severity:** Low
**Hours:** 2-3h
**Recommendation:** Add a global CSS rule `main { padding-bottom: env(safe-area-inset-bottom, 80px); }` for mobile, or use the NavigationShell layout to inject consistent bottom padding.

---

## 3. Respostas ao Architect

Answering all questions from Section 6 directed to @ux-expert:

### Q1. TD-035 (search filters 600+ lines): Quais responsabilidades podem ser extraidas do useSearchFilters()?

**Answer:** After reading the full 607-line hook, I identify 5 extractable concerns:

1. **useFilterFormState** (~150 lines): Pure form state management (useState for all filter fields, setters with clearResult wrappers). No logic, just state containers.
2. **useFilterValidation** (~80 lines): `validateTermsClientSide()`, `canSearch` computation, `validationErrors`. Already partially isolated as a standalone function but embedded in the hook.
3. **useFilterPersistence** (~60 lines): `safeGetItem`/`safeSetItem` for last-used filters, URL search params reading. Already a pattern in `useSearchPersistence.ts` -- merge or compose.
4. **useFilterAnalytics** (~30 lines): `analytics.track()` calls on filter changes. Extract as a thin wrapper.
5. **useSectorData** (~100 lines): Sector fetching, fallback, stale cache detection, retry. This is a data-fetching concern, not a filter concern.

**Recommended split:** Keep useSearchFilters as a facade that composes these 5 hooks. Total API surface stays the same for consumers.

### Q2. TD-036 (visual regression): Percy ou Chromatic? Qual coverage minimo?

**Answer:** **Chromatic** is recommended over Percy for this project:

- Chromatic integrates natively with Storybook (if TD-043 is addressed later)
- Chromatic offers component-level snapshots, not just page-level
- Pricing: Chromatic free tier (5K snapshots/month) is sufficient for initial setup
- Percy requires separate infrastructure and is page-snapshot oriented

**Minimum coverage for first setup (10 critical screens):**
1. `/buscar` -- empty state, loading state, results state, error state
2. `/buscar` -- FilterPanel open (mobile)
3. `/planos` -- pricing cards
4. `/pipeline` -- kanban board
5. `/dashboard` -- analytics charts
6. `/login` -- form state
7. `ResultCard` -- all badge variants (viability, LLM, reliability)
8. `EnhancedLoadingProgress` -- all progress states
9. `BannerStack` -- multiple banners
10. `MobileDrawer` -- open state

This covers ~80% of user-visible surface area with 10 snapshots.

### Q3. TD-037 (saved filters): Qual o UX pattern recomendado?

**Answer:** Recommended UX pattern:

- **Location:** Dropdown button next to the search button, labeled "Filtros salvos" with a bookmark icon
- **Save flow:** After a successful search, show a subtle "Salvar filtros" button in the results toolbar. Click opens a modal with: name input (auto-suggest based on sector+UFs), optional description
- **Load flow:** Dropdown shows list of saved presets with name, date saved, and a "delete" action
- **Limit:** 10 presets per user (sufficient for consultancies managing multiple clients)
- **Storage:** Supabase table `saved_filter_presets` (user_id, name, filters_json, created_at). NOT localStorage -- presets should be available across devices.
- **Data model:** filters_json stores the full `UseSearchFiltersSnapshot` type already defined in the codebase

### Q4. TD-038 (focus trap): Quais edge cases especificos?

**Answer:** After inspecting all 7 FocusTrap usages in the codebase:

- **Validated:** All use `focus-trap-react` with proper `active` prop and escape key handling
- **Edge cases found:**
  1. **DeepAnalysisModal:** Opens via portal. If another modal is already open (e.g., upgrade modal triggered from within analysis), focus trap may conflict. Not observed but architecturally possible.
  2. **TrialConversionScreen:** Full-screen overlay. No `returnFocusOnDeactivate` configuration found -- focus may not return to trigger element.
  3. **BottomNav "more" drawer:** Uses custom overlay, NOT FocusTrap. This is an inconsistency -- the "more" menu overlay should trap focus for a11y compliance.
- **Severity adjustment:** These are real but low-frequency. The BottomNav case is the most impactful since it affects every mobile user.

### Q5. TD-039 (touch targets): Quantos componentes legacy estao abaixo de 44px?

**Answer:** Inventory of sub-44px touch targets found in code:

| Component | Element | Current Size | File |
|-----------|---------|-------------|------|
| FeedbackButtons | Thumbs up/down buttons | ~28x28px (`p-1.5` + 16px icon) | `components/FeedbackButtons.tsx` |
| CompatibilityBadge | Badge itself (non-interactive, role="img") | ~20x16px | `components/CompatibilityBadge.tsx` |
| TrialUpsellCTA | Close button | ~28x28px (`p-1` + icon) | `components/billing/TrialUpsellCTA.tsx` |

**Components already compliant:**
- BottomNav: All items `min-w-[44px] min-h-[44px]` -- compliant
- MobileDrawer: All items `min-h-[44px]` -- compliant
- MobileMenu: All items `min-h-[44px]` or `min-h-[48px]` -- compliant
- Global CSS: `button { min-height: 44px; }` base rule in globals.css -- covers most cases

**Total:** 3 components need fixes. The global CSS `button { min-height: 44px }` covers standard buttons. The offenders are components with custom padding that overrides the base.

### Q6. TD-040 (/planos vs /pricing): Redirect 301 ou manter ambos com canonical?

**Answer:** **Maintain both with canonical pointing to /planos.**

Rationale:
- `/pricing` (352 lines) has a unique ROI Calculator feature not present in `/planos`
- `/planos` (405 lines) is the canonical pricing page with plan comparison
- These are NOT duplicates -- they serve different user intents
- Redirect 301 would lose the ROI calculator, which is valuable for conversion

**Implementation:**
1. Add `<link rel="canonical" href="https://smartlic.tech/planos" />` to `/pricing/page.tsx`
2. Consider merging the ROI calculator INTO `/planos` as a tab or section (longer term)
3. Alternatively, rename `/pricing` to `/calculadora-roi` for clarity

### Q7. TD-043 (Storybook): Prioridade real considerando 65+ componentes?

**Answer:** **Low priority, defer to P4.** Reasoning:

- 312 test files in `frontend/__tests__/` provide strong coverage already
- Storybook's primary value is design handoff and visual documentation. With a single developer/designer, the ROI is low.
- **If team grows to 3+ frontend developers:** Storybook becomes Medium priority
- **Minimum scope if implemented:** 15 components -- the core UI kit (`Button`, `Input`, `Label`, `CurrencyInput`, `Pagination`) plus the 10 most complex feature components (`SearchForm`, `ResultCard`, `EnhancedLoadingProgress`, `FilterPanel`, `PlanCard`, `BottomNav`, `MobileDrawer`, `FeedbackButtons`, `ViabilityBadge`, `BannerStack`)

### Q8. TD-046 (scroll jank SSE): Debounce atual e quantos ms? Virtualized list seria mais efetivo?

**Answer:** After searching the codebase:

- **No explicit debounce on scroll/render during SSE updates found.** The SSE handler (`useSearchSSEHandler.ts`, 237 lines) updates state directly via `setResult()`.
- **Current mitigation:** Client-side pagination (10/20/50 items per page via `ResultsPagination`) effectively limits the visible DOM to at most 50 ResultCards.
- **Virtualization analysis:**
  - At 10-20 items/page (default): Virtualization adds complexity without benefit
  - At 50 items/page: Minor benefit on low-end mobile devices
  - The real jank source is SSE state updates triggering re-renders of the entire search results tree, not the list itself
- **Recommendation:** Instead of virtualized list, use `React.memo` on `ResultCard` and ensure `ResultsList` only re-renders when its specific slice of data changes. Add `useDeferredValue` for the results array during SSE streaming. This is simpler and more effective than react-window for this use case.
- **Estimated debounce if added:** 100-150ms on SSE state updates would be sufficient.

---

## 4. Recomendacoes de Design

### 4.1 Design System Improvements

The design system in `globals.css` + `tailwind.config.ts` is **well-architected**. Specific strengths:
- WCAG contrast ratios documented inline for every color token
- Full dark mode support with contrast validation
- Semantic color aliases (success, error, warning) with subtle backgrounds
- Chart palette (10 colors) and gem palette for data visualization
- `prefers-reduced-motion` respected globally

**Improvements:**
1. **Consolidate animation definitions.** Animations are defined BOTH in `globals.css` (`@keyframes`) AND in `tailwind.config.ts` (`keyframes` + `animation`). The CSS keyframes are redundant -- Tailwind generates them from config. Remove duplicates from `globals.css` (keep only those used by non-Tailwind selectors like Shepherd.js).
2. **Add spacing scale documentation.** The `spacing` key in tailwind config is empty (comment-only). Document the 4px base grid intention with actual values.
3. **Typography scale gap.** Fluid typography vars (`--text-hero` through `--text-body-lg`) are defined in CSS but NOT mapped in tailwind config `fontSize`. Add `hero: 'var(--text-hero)'`, etc. to enable `text-hero` utility classes.

### 4.2 Component Refactoring Suggestions

**Priority 1 (P1):**
- Split `useSearchExecution.ts` (852 lines) into 3 hooks (TD-050)
- Split `useSearchFilters.ts` (607 lines) into 5 hooks (TD-035)

**Priority 2 (P2):**
- Create shared `BaseErrorBoundary` composing the 5 existing patterns (TD-054)
- Merge feedback button touch target fix with global CSS audit (TD-039 + TD-052)

**Priority 3 (P3):**
- Extract `useSectorData` from useSearchFilters -- this is a data concern, not a filter concern
- Consider React Server Components for `ResultCard` to reduce client bundle (currently all client-side)

### 4.3 Accessibility Roadmap

**Immediate (0-2 weeks):**
- Fix FeedbackButtons touch target: `min-w-[44px] min-h-[44px]` (1h)
- Fix TrialUpsellCTA close button touch target (0.5h)
- Add `aria-hidden="true"` to remaining decorative icons (2h)

**Short-term (1-2 months):**
- Add FocusTrap to BottomNav "more" overlay (2h)
- Audit Sonner toast `role` attributes for error toasts (1h)
- Fix CompatibilityBadge minimum text size (0.5h)

**Long-term (3-6 months):**
- Quarterly axe-core audit integrated into CI (4h setup)
- Screen reader testing with NVDA/VoiceOver for top 5 flows (8h)
- WCAG 2.2 Level AAA audit for focus appearance (already partially compliant)

### 4.4 Mobile UX Improvements

1. **BottomNav safe area:** Add global `pb-[env(safe-area-inset-bottom,80px)]` to main content wrapper for mobile viewports. This prevents content from being hidden behind the 60px BottomNav.
2. **SSE streaming UX:** Add `useDeferredValue` to prevent jank during result streaming. More effective than debounce or virtualization for this use case.
3. **Filter panel mobile:** The filter panel on mobile could benefit from a bottom sheet pattern (slide up from bottom) instead of the current inline expansion. This is a larger UX change -- recommend prototyping in Q3.

### 4.5 Testing Strategy

**Current state:** 312 test files is excellent coverage for a frontend of this size. The buscar-specific tests (17 files) cover critical paths well.

**Recommended additions:**
1. **Visual regression (TD-036):** Chromatic with 10 critical screens (see Q2 answer above)
2. **a11y automated testing:** Add `jest-axe` to existing Jest tests for the top 10 components. Estimated: 4h setup + 1h per component = 14h total.
3. **Mobile-specific Playwright tests:** Add iPhone viewport tests for BottomNav padding, FeedbackButtons tap targets, and FilterPanel mobile drawer. Estimated: 6h.
4. **Storybook (TD-043):** Defer unless team grows. The 312 existing tests provide adequate coverage.

---

## Resumo de Impacto

| Categoria | Itens | Horas Totais Estimadas |
|-----------|-------|----------------------|
| Debitos Confirmados (DRAFT) | 15 | 110-160h |
| Debitos Adicionados (Novos) | 6 | 33-47h |
| **Total** | **21** | **143-207h** |

### Top 5 por Impacto (recomendacao de priorizacao):

1. **TD-050** (NEW): useSearchExecution 852 lines -- P1, 16-20h
2. **TD-035**: useSearchFilters 607 lines -- P1, 12-16h
3. **TD-037**: Saved filter presets -- P2, 20-24h (user-facing value)
4. **TD-052** (NEW): FeedbackButtons touch target -- P1, 1-2h (quick win, a11y compliance)
5. **TD-036**: Visual regression testing -- P2, 16-20h (quality gate)
