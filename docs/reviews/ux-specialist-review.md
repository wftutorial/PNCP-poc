# UX Specialist Review

**Reviewer:** @ux-design-expert
**Date:** 2026-02-25
**Input:** `docs/prd/technical-debt-DRAFT.md` (Phase 4), `docs/frontend/frontend-spec.md` (Phase 3)
**Scope:** Enterprise monetization readiness -- what UX issues would make an enterprise customer not trust the product enough to pay?

---

## Executive Assessment

SmartLic's frontend is surprisingly well-built for a POC at this stage. The design system (CSS custom properties, semantic tokens, dark/light themes, WCAG contrast ratios) is more mature than typical pre-revenue B2G products. The core search flow has production-hardened resilience patterns (SSE progress, graceful fallbacks, humanized error messages, cache banners). The billing flow is structurally complete (Stripe integration, plan cards, payment failed banner).

**The enterprise readiness gap is narrow but specific.** The 4 Tier 1 database items are the only true functional blockers. From a UX perspective, the primary risks to enterprise perception are: (1) raw `error.message` exposure in error boundaries, (2) missing Portuguese accents on the 404 page, (3) the `global-error.tsx` using inline styles outside the design system, and (4) inconsistent component duplication suggesting an unfinished product to developers who inspect the code. None of these are showstoppers for a paying enterprise user in normal operation -- they only surface during error states or edge cases.

**Bottom line:** Fix the 4 Tier 1 items, address the 5 UX-critical items below, and the product is enterprise-presentable for monetization.

---

## Tier Validation

### Frontend Items in Tier 1/2

| ID | Debito | Validated? | Severity Correct? | Enterprise Impact |
|----|--------|-----------|-------------------|-------------------|
| T1-04 | `trial_stats.py` references non-existent `user_pipeline` table | Yes | Correct (Tier 1) | Trial value display on pipeline page will error. Enterprise users evaluating during trial see a broken metric -- damages first impression. |
| T2-11 | BottomNav drawer lacks focus trap (D-008) | Yes | Correct (Tier 2) | Mobile a11y violation. Enterprise procurement officers increasingly use tablets/phones. WCAG compliance is a checkbox item for government-adjacent B2G buyers. However, the drawer is a secondary navigation element (the "More" menu), not a primary flow blocker. Tier 2 is appropriate. |

**Validation summary:** Both items are correctly tiered. No frontend items in Tier 1 need re-rating. T2-11 is the only frontend item in Tier 2 and it belongs there.

### Items to ESCALATE (Tier 3 to Tier 2)

| ID | Debito | Current Tier | Recommended | Reason |
|----|--------|-------------|-------------|--------|
| T3-F15 | 404 page missing Portuguese accents ("Pagina nao encontrada") | Tier 3 (Medium) | **Tier 2** | Enterprise users who mistype a URL see broken Portuguese. This is the kind of surface-level quality issue that signals "unfinished product" to a decision-maker. The fix is literally 2 strings. |
| T3-F07 | `global-error.tsx` uses inline styles instead of design system | Tier 3 (High) | **Tier 2** | When the root layout crashes (rare but possible), the error page renders with hardcoded `#f9fafb` background and `system-ui` font -- visually disconnected from the rest of the app. An enterprise user hitting this sees a different product. The fix is ~20 minutes to use design system tokens. |
| T3-F17 | Only search page has per-page error boundary | Tier 3 (Medium) | **Tier 2** | Pipeline (`/pipeline`) and Account (`/conta`) pages use the root `error.tsx` which displays raw `error.message` in a monospace font block. Enterprise users should never see `TypeError: Cannot read properties of undefined`. Currently, buscar, dashboard, and admin have custom error boundaries -- pipeline, historico, mensagens, and conta do not. Adding error boundaries for the 4 remaining protected pages takes ~2 hours and eliminates all raw error exposure. |
| T3-F14 | `FeedbackButtons` uses custom toast instead of `sonner` | Tier 3 (Medium) | Stays Tier 3 | Not impactful enough for enterprise perception. The custom toast works; it just looks slightly different. |
| T3-F21 | Inconsistent date display (mixed `date-fns` and `toLocaleDateString`) | Tier 3 (Medium) | Stays Tier 3 | Users unlikely to notice date formatting inconsistencies. Not an enterprise perception issue. |

**Rationale for escalations:** The 3 escalated items all share the same characteristic -- they are visible to enterprise users during normal or near-normal operation, they signal "unfinished" quality, and they each take under 2 hours to fix.

---

## Enterprise UX Blockers

These are the specific UX issues that would make an enterprise customer not trust the product enough to pay, ordered by severity:

### Blocker 1: Raw Error Messages Exposed to Users (CRITICAL)

**Location:** `app/error.tsx`, `app/buscar/error.tsx`, `app/dashboard/error.tsx`, `app/admin/error.tsx`

All 4 error boundary files render `error.message` directly in a monospace font block:

```tsx
{error.message && (
  <div className="mb-6 p-4 bg-surface-2 rounded-md text-left">
    <p className="text-sm text-ink-secondary font-mono break-words">
      {error.message}
    </p>
  </div>
)}
```

This means when a React error boundary catches an exception, the raw JavaScript error message (e.g., `TypeError: Cannot read properties of undefined (reading 'map')`) is displayed to users. The `getUserFriendlyError()` function in `lib/error-messages.ts` exists and handles this well -- but error boundaries do NOT use it. They display the raw `error.message` directly.

**Enterprise impact:** A procurement director seeing `TypeError: Cannot read properties of undefined` will immediately lose confidence in the platform's reliability. This is the single most damaging UX issue for enterprise perception.

**Fix:** Wrap `error.message` through `getUserFriendlyError()` before display, or conditionally hide the raw message in production (show only in development). Estimated effort: 1 hour across all 4 files.

### Blocker 2: 404 Page Missing Portuguese Accents

**Location:** `app/not-found.tsx`

The 404 page displays "Pagina nao encontrada" instead of "Pagina nao encontrada" and "A pagina que voce procura nao existe ou foi movida." -- missing proper accented characters. The architect's DRAFT correctly flags this as D-016 / T3-F15.

**Enterprise impact:** Low frequency (users rarely hit 404) but high signal. Missing accents in Portuguese is equivalent to a spelling error on an English-language enterprise product. It says "nobody proofread this."

**Fix:** Replace 2 strings with properly accented versions. Estimated effort: 5 minutes.

### Blocker 3: `global-error.tsx` Visually Disconnected from Product

**Location:** `app/global-error.tsx`

Uses inline styles (`backgroundColor: "#f9fafb"`, `fontFamily: "system-ui"`, `color: "#111827"`) instead of the design system. When triggered, it renders a white card with green button on light gray background -- no dark mode support, no brand fonts, no design tokens.

**Enterprise impact:** This page only appears when the root layout crashes (very rare). But when it does, it looks like a completely different product. The `error.tsx` (non-global) already uses the design system correctly -- the global error page should match.

**Note:** `global-error.tsx` cannot use Tailwind or CSS imports since the root layout has failed. However, it CAN use inline styles that match the design system values (e.g., `backgroundColor: "#ffffff"` for light, with a `<style>` tag for dark mode media query). Estimated effort: 30 minutes.

### Non-Blockers Confirmed

The following items were evaluated for enterprise impact and are confirmed as non-blocking for monetization:

- **T3-F01/F02 (Component duplication):** Internal code quality issue. Users never see duplicate EmptyState or LoadingProgress components -- they see one or the other. No enterprise perception impact.
- **T3-F03 (SearchForm 40+ props):** Developer experience issue only. The search form works correctly from a user perspective.
- **T3-F04 (No RSC for protected pages):** Performance impact but not a perception issue. Pages load in 1-3 seconds which is acceptable for B2G enterprise users.
- **T3-F11 (No state management library):** Internal architecture concern. Does not affect user experience.
- **T3-F13 (No i18n):** SmartLic targets Brazilian market only. Portuguese-only is correct for monetization.

---

## Quick Wins for Professional Appearance

These are low-effort changes that significantly improve enterprise perception, ranked by impact-per-hour:

| Priority | Item | Effort | Impact | Details |
|----------|------|--------|--------|---------|
| 1 | Fix 404 accents (T3-F15) | 5 min | High | Two string replacements in `not-found.tsx`. Eliminates the most visible "unpolished" signal. |
| 2 | Filter `error.message` through `getUserFriendlyError()` in all error boundaries | 1 hr | Critical | Apply to `error.tsx`, `buscar/error.tsx`, `dashboard/error.tsx`, `admin/error.tsx`. The function already exists -- just import and use it. |
| 3 | Add error boundaries for pipeline, historico, mensagens, conta | 2 hr | High | Copy the pattern from `buscar/error.tsx` or `dashboard/error.tsx`. Each page gets a contextual error message instead of raw error. |
| 4 | Improve `global-error.tsx` to match brand | 30 min | Medium | Use inline styles that match the design system values. Add dark mode media query. Use brand color for the button. |
| 5 | Remove legacy `bidiq-theme` migration code (T3-F22) | 15 min | Low | Dead code in `ThemeProvider.tsx` and `layout.tsx`. Subtle signal of product maturity when code is inspected. |

---

## Effort Estimates

### UX-Critical Items (Required for Enterprise Monetization)

| ID | Item | Hours | Impact on Perception |
|----|------|-------|---------------------|
| NEW-1 | Filter `error.message` through `getUserFriendlyError()` in 4 error boundary files | 1.0 | Critical -- eliminates raw technical errors visible to users |
| T3-F15 | Fix 404 Portuguese accents | 0.1 | High -- eliminates visible spelling/accent errors |
| T3-F07 | Improve `global-error.tsx` brand alignment | 0.5 | Medium -- ensures error states match the product |
| T3-F17 | Add error boundaries for pipeline, historico, mensagens, conta | 2.0 | High -- ensures no raw errors on any page |
| T2-11 | Focus trap in BottomNav drawer | 1.5 | Medium -- WCAG compliance for mobile users |
| **Total** | | **5.1** | |

### UX Nice-to-Haves (Post-Monetization Sprint)

| ID | Item | Hours | Impact on Perception |
|----|------|-------|---------------------|
| T3-F01 | Deduplicate EmptyState component | 2.0 | Low (internal quality) |
| T3-F02 | Deduplicate LoadingProgress component | 1.5 | Low (internal quality) |
| T3-F14 | Replace custom toast with sonner in FeedbackButtons | 1.0 | Low (consistency) |
| T3-F05/F06 | Create shared icon component library | 4.0 | Low (DX improvement) |
| T3-F22 | Remove legacy bidiq-theme code | 0.25 | Low (cleanup) |
| T3-F08 | Centralize ALL_UFS constant | 1.0 | Low (internal quality) |

---

## Recommended Priority Order

For maximum enterprise perception improvement with minimal effort:

1. **Fix 404 accents** (5 min) -- Immediate quality signal improvement
2. **Filter error.message in all error boundaries** (1 hr) -- Eliminates the most damaging UX issue
3. **Add error boundaries for 4 remaining protected pages** (2 hr) -- Complete error handling coverage
4. **Improve global-error.tsx brand alignment** (30 min) -- Error states match the product
5. **Fix BottomNav focus trap** (1.5 hr) -- WCAG compliance for mobile
6. **(Tier 1 database fixes)** -- These are backend but have frontend UX impact on billing/trial display
7. **Remove legacy bidiq-theme code** (15 min) -- Clean code signal

Items 1-4 should be done in a single sprint (half-day of work). Item 5 can be done in parallel. The total investment is approximately 5 hours of frontend work to achieve enterprise-grade UX quality.

---

## Answers to Architect

### Question 1: Focus trap (T2-11) -- Is the BottomNav drawer used frequently enough on mobile to prioritize the a11y fix? What is the mobile traffic percentage?

The BottomNav drawer is the "More" menu that contains secondary navigation items (Dashboard, Account, Help). It is triggered by the fifth navigation tab on mobile. While I do not have exact mobile traffic percentages from Mixpanel, B2G enterprise users in Brazil increasingly use tablets and phones for initial review of procurement opportunities (especially decision-makers reviewing during travel or meetings).

**Recommendation:** The focus trap fix is correctly prioritized at Tier 2. It should be fixed within the next 2 sprints but is not a monetization blocker. The drawer is a secondary navigation element -- primary flows (search, pipeline, billing) do not depend on it. The fix involves adding a focus trap library (like `focus-trap-react`, ~3KB gzip) or a manual `keydown` handler to cycle focus within the drawer.

### Question 2: Component duplication (T3-F01, T3-F02) -- Which version should be canonical?

**EmptyState:**
- `components/EmptyState.tsx` (top-level): Generic empty state with icon, title, description, optional steps, CTA link. API: `{ icon, title, description, steps?, ctaLabel, ctaHref }`. Used on pipeline, historico, and other pages for "no data yet" scenarios.
- `app/components/EmptyState.tsx` (buscar-specific): Search-specific empty state with filter stats breakdown, rejection reasons, LLM zero-match info, and "adjust search" button. API: `{ onAdjustSearch?, rawCount?, stateCount?, filterStats?, sectorName? }`. Used only on the search page.

**Recommendation:** Keep BOTH but rename them. The buscar-specific one should be `SearchEmptyState` (it is fundamentally different). The generic one in `components/EmptyState.tsx` should be the canonical `EmptyState`. The confusion is naming, not duplication -- they serve different purposes.

**LoadingProgress:**
- `components/LoadingProgress.tsx`: Basic loading indicator (simple spinner + text).
- `app/components/LoadingProgress.tsx`: Similar basic loading indicator.

**Recommendation:** The `components/LoadingProgress.tsx` version should be canonical. Delete `app/components/LoadingProgress.tsx` and update imports. The `EnhancedLoadingProgress` component (search-specific, SSE-aware, 5-stage) remains separate -- it is a different component entirely.

### Question 3: SearchForm props (T3-F03) -- Recommended state management approach?

**Recommendation:** React Context, not Zustand/Jotai. Here is why:

The 40+ props on SearchForm fall into 3 categories:
1. **Search state** (UFs, dates, sector, terms, filters) -- ~15 props
2. **UI state** (loading, error, progress, expanded sections) -- ~10 props
3. **Callbacks** (onSearch, onCancel, onFilterChange, etc.) -- ~15 props

A `SearchContext` with `useReducer` would encapsulate categories 1 and 2. Callbacks in category 3 would be stable references via `useCallback` in the context provider. This eliminates prop drilling without adding a dependency.

Zustand/Jotai would be overkill -- the search state is page-scoped (only exists on `/buscar`), not app-global. React Context is the right tool for page-scoped shared state.

**Effort:** ~8-12 hours to extract SearchContext, update SearchForm, SearchResults, and the buscar page. This is a Phase 2 improvement, not needed for monetization.

### Question 4: Icon system (T3-F05, T3-F06) -- Standardize on Lucide or custom?

**Recommendation:** Standardize on Lucide React for all icons.

Rationale:
- Lucide is already a dependency (used on landing page).
- It provides all the icons currently used as inline SVGs (search, clipboard, clock, chat, user, etc.).
- Tree-shaking means only imported icons are bundled (~200 bytes per icon).
- Eliminates ~200 lines of duplicated SVG definitions in Sidebar and BottomNav.
- Provides consistent sizing, stroke width, and accessibility attributes.

**Do NOT create a custom icon component library** -- that is unnecessary abstraction for 15-20 icons. Simply replace inline SVGs with `import { Search, ClipboardList, Clock, ... } from 'lucide-react'` and pass `size` and `strokeWidth` props.

**Effort:** ~4 hours. This is a Phase 2 improvement.

### Question 5: Protected pages RSC (T3-F04) -- Near-term migration plan?

**Recommendation:** No. Do not migrate to RSC for protected pages in the near term.

Rationale:
1. **Auth complexity:** Protected pages require Supabase session tokens. RSC data fetching would need server-side token handling, which adds complexity to the auth flow.
2. **SSE dependency:** The search page relies heavily on client-side SSE for real-time progress. RSC does not help here.
3. **Risk:** Migrating 8+ protected pages to RSC hybrid is a significant refactor with risk of regressions.
4. **Marginal benefit:** Current CSR pages load in 1-3 seconds. Enterprise B2G users are accustomed to government portal performance. The improvement would be noticeable but not decisive for monetization.

**When to revisit:** After monetization is validated and user base grows beyond 50 concurrent users, RSC migration for the dashboard and historico pages (which are read-heavy and benefit most from server rendering) would be a good investment.

---

## Enterprise UX Readiness Score

| Flow | Score | Key Issues | Monetization Ready? |
|------|-------|-----------|-------------------|
| **Search** | 4/5 | Excellent loading states (5-stage SSE progress), resilient error handling, humanized messages. Only gap: root `error.tsx` shows raw error.message if error boundary catches unexpected exception. | Yes (after error.message filtering) |
| **Pipeline** | 3.5/5 | Kanban works well. Mobile tab view is thoughtful. T1-04 breaks trial value display. No per-page error boundary. | Yes (after T1-04 fix + error boundary) |
| **Billing** | 4/5 | PlanCard is polished. PaymentFailedBanner is well-designed (persistent, non-dismissable, with action button). Stripe portal integration works. Only concern: T1-01/T1-03 database columns missing from migrations (disaster recovery scenario, not day-to-day). | Yes (after T1-01/T1-03 migration) |
| **Dashboard** | 3.5/5 | Has its own error boundary (good). Uses Recharts for visualization. Profile completion prompt adds value. Gap: fully CSR with loading waterfall. | Yes |
| **Onboarding** | 4/5 | Clean 3-step wizard. Region selector is intuitive. Auto-triggers first search. T2-04 (handle_new_user trigger) may cause missing profile fields -- but this is a backend issue, not a UX issue. | Yes |
| **Error States** | 3/5 | `error.tsx` and page-specific error boundaries exist for search, dashboard, admin. But 4 protected pages lack them. Raw error.message exposed. `global-error.tsx` is off-brand. | Needs work (5 hours) |
| **404 Page** | 2.5/5 | Design is clean (uses design system tokens correctly). But missing Portuguese accents is unacceptable for a Portuguese-language enterprise product. | Needs 5-minute fix |
| **Loading States** | 4.5/5 | EnhancedLoadingProgress is best-in-class for this type of product. 5-stage progress, SSE real-time, overtime messaging, degraded state handling, cancel button. AuthLoadingScreen and skeletons are adequate. | Yes |
| **Mobile** | 3.5/5 | Responsive design is solid. Pipeline has mobile tab view. BottomNav works. Gap: focus trap missing on drawer overlay (a11y). | Yes (T2-11 is non-blocking for launch) |

**Overall Enterprise UX Readiness: 3.7/5**

To reach 4.2/5 (enterprise-presentable): fix the 5 UX-critical items listed above (~5 hours of work).

---

## Summary of Frontend Actions for Enterprise Monetization

### Must-Do (Before First Enterprise Customer)

| # | Action | Effort | Owner |
|---|--------|--------|-------|
| 1 | Fix 404 Portuguese accents | 5 min | Frontend dev |
| 2 | Filter `error.message` through `getUserFriendlyError()` in all 4 error boundary files | 1 hr | Frontend dev |
| 3 | Add error boundaries for `/pipeline`, `/historico`, `/mensagens`, `/conta` | 2 hr | Frontend dev |
| 4 | Improve `global-error.tsx` inline styles to match brand | 30 min | Frontend dev |
| 5 | Fix BottomNav drawer focus trap (T2-11) | 1.5 hr | Frontend dev |

### Should-Do (Within 2 Sprints Post-Launch)

| # | Action | Effort | Owner |
|---|--------|--------|-------|
| 6 | Deduplicate/rename EmptyState components | 2 hr | Frontend dev |
| 7 | Deduplicate LoadingProgress components | 1.5 hr | Frontend dev |
| 8 | Create shared icon library (Lucide migration) | 4 hr | Frontend dev |
| 9 | Centralize ALL_UFS constant | 1 hr | Frontend dev |
| 10 | Remove legacy bidiq-theme migration code | 15 min | Frontend dev |

### Defer (Backlog)

| # | Action | Effort | Trigger |
|---|--------|--------|---------|
| 11 | Extract SearchContext from SearchForm 40+ props | 8-12 hr | When search page needs significant feature additions |
| 12 | Add `dynamic()` imports for Recharts, @dnd-kit, Shepherd.js | 3 hr | When bundle size becomes a measured bottleneck |
| 13 | Migrate protected pages to RSC | 40+ hr | When user base exceeds 50 concurrent users |
| 14 | Implement state management library (Zustand) | 20+ hr | When cross-page state sharing is needed |
| 15 | i18n framework | 40+ hr | When multi-language is a business requirement |

---

*Generated by @ux-design-expert as part of SmartLic Brownfield Discovery Phase 6.*
*Cross-references: technical-debt-DRAFT.md (Phase 4), frontend-spec.md (Phase 3).*
