# UX Specialist Review

**Reviewer:** @ux-design-expert (Uma)
**Date:** 2026-03-07
**Documents Reviewed:** technical-debt-DRAFT.md v3.0 (2026-03-07), frontend-spec.md (Phase 3)
**Supersedes:** ux-specialist-review.md v1 (2026-03-04, reviewer Pixel)
**Codebase Snapshot:** branch `main`, commit `a1349fc2`

---

## Validation Summary

| Status | Count |
|--------|-------|
| Confirmed (as-is) | 23 |
| Severity Adjusted | 5 |
| Removed (false positive) | 1 |
| Added (new) | 6 |
| **Total validated frontend debts** | **35** |

---

## Debitos Validados

All 30 FE-xxx items from the DRAFT v3.0 were reviewed against the codebase. Line counts, component counts, and claims were verified via grep/glob.

### 4.1 Arquitetura e Estrutura (FE-001 through FE-007)

| ID | Debito | Original Sev | Adjusted Sev | Hours | UX Impact | Design Review? | Sprint |
|----|--------|-------------|-------------|-------|-----------|---------------|--------|
| FE-001 | Monolithic pages (conta 1420, alertas 1068, buscar 1057, dashboard 1037) | HIGH | **HIGH** | 20-28h | Performance + maintainability; re-renders on large pages degrade scroll/interaction responsiveness | Yes | Sprint 2 |
| FE-002 | Zero `loading.tsx` streaming (44 pages) | HIGH | **HIGH** | 16h | Directly user-visible: blank screen on every route transition until JS hydrates. Core Web Vitals (FCP, LCP) impacted. | No | Sprint 1 |
| FE-003 | No i18n framework (hardcoded PT) | HIGH | **LOW** | 40h | None for current users. Product is 100% BR, pre-revenue, no international plans. Domain terms (licitacao, edital, pregao) have no direct translations. Premature optimization. | No | Backlog |
| FE-004 | 23/44 pages `"use client"` excessively | HIGH | **MEDIUM** | 24h | Indirect: inflated JS bundle increases TTI on slow connections. However, most CSR pages require client interactivity (forms, real-time data). Only 3-5 pages (planos, historico, ajuda) are candidates for partial SSR. | No | Sprint 2 |
| FE-005 | 3 component directories without clear rule | HIGH | **MEDIUM** | 8h | Invisible to users but slows dev velocity. EmptyState duplication (FE-011) is a symptom. | No | Sprint 2 |
| FE-006 | No global state management | HIGH | **HIGH** | 16h | Indirect but critical: prop drilling causes stale data display when auth/plan/quota changes propagate slowly. Users may see incorrect plan badges or quota counts. | No | Sprint 2 |
| FE-007 | Inconsistent data fetching (SWR vs raw fetch vs fetchWithAuth) | HIGH | **HIGH** | 12h | Direct: no dedup means duplicate requests visible in slow network; no revalidation means stale data displayed; inconsistent error handling means some failures show nothing to user. | No | Sprint 2 |

### 4.2 Qualidade de Codigo (FE-008 through FE-015)

| ID | Debito | Original Sev | Adjusted Sev | Hours | UX Impact | Design Review? | Sprint |
|----|--------|-------------|-------------|-------|-----------|---------------|--------|
| FE-008 | `any` types in 5+ production files | MEDIUM | **MEDIUM** | 2h | Indirect: type holes can lead to runtime errors visible to users. Verified 8 files with `: any` including pipeline, filters, analytics proxy. | No | Sprint 1 |
| FE-009 | Console statements in production | MEDIUM | **MEDIUM** | 1h | Indirect: log noise can mask real errors in Railway logs, delaying incident response. Users dont see console.log but suffer from slower debugging. | No | Sprint 1 |
| FE-010 | 28+ TODO/FIXME in blog content | MEDIUM | **LOW** | 8h | SEO impact only (internal linking incomplete). No UX impact for authenticated users. Blog is marketing, not core product. | No | Backlog |
| FE-011 | EmptyState duplicated in 2 locations | MEDIUM | **MEDIUM** | 1h | Risk of visual inconsistency if one copy is updated and the other is not. | Yes | Sprint 1 |
| FE-012 | Error boundary only in `/buscar` | MEDIUM | **HIGH** | 6h | Direct: dashboard, pipeline, historico, mensagens, alertas crash to root error page on any unhandled exception. Users lose all page context and must re-navigate. This is a resilience gap for the 5 most-used authenticated pages. | No | Sprint 1 |
| FE-013 | SearchErrorBoundary uses hardcoded red | MEDIUM | **MEDIUM** | 1h | Inconsistent with "blue/yellow, never red" error guideline in error-messages.ts. Verified: 9 red class references in SearchErrorBoundary.tsx. Creates anxiety-inducing error display. | Yes | Sprint 1 |
| FE-014 | No memoization in large pages | MEDIUM | **MEDIUM** | 4h | alertas has only 2 useMemo in 1068 lines; dashboard has 6 in 1037 lines. Complex filter/list UIs re-render unnecessarily causing jank on mid-range devices. | No | Sprint 2 |
| FE-015 | `nul` file in app directory | MEDIUM | **LOW** | 0.5h | Zero UX impact. Codebase hygiene only. Confirmed file exists at `frontend/app/nul`. | No | Sprint 1 |

### 4.3 Styling e Design System (FE-016 through FE-017)

| ID | Debito | Original Sev | Adjusted Sev | Hours | UX Impact | Design Review? | Sprint |
|----|--------|-------------|-------------|-------|-----------|---------------|--------|
| FE-016 | Mix CSS variables and raw Tailwind (~10 files) | MEDIUM | **MEDIUM** | 4h | Visual: some components use brand tokens, others use Tailwind defaults. Creates subtle color/spacing inconsistencies that undermine the "polished enterprise" feel needed for B2G buyers. | Yes | Sprint 2 |
| FE-017 | global-error.tsx uses wrong brand colors | MEDIUM | **MEDIUM** | 0.5h | Verified: `#2563eb`/`#1e3a5f` (Tailwind blue-600/dark navy) instead of `#116dff`/`#0a1e3f` (SmartLic tokens). Users who hit a root error see off-brand colors. Low frequency but jarring. | Yes | Sprint 1 |

### 4.4 Performance (FE-018 through FE-020)

| ID | Debito | Original Sev | Adjusted Sev | Hours | UX Impact | Design Review? | Sprint |
|----|--------|-------------|-------------|-------|-----------|---------------|--------|
| FE-018 | No `next/image` usage (only 4 files) | MEDIUM | **MEDIUM** | 8h | LCP impacted on image-heavy pages (landing, blog). Authenticated pages use mostly SVG icons (no impact). Prioritize landing page images for conversion. | No | Sprint 2 |
| FE-019 | No code splitting for Recharts (~50KB), @dnd-kit (~15KB), Shepherd.js (~25KB) | MEDIUM | **MEDIUM** | 4h | Verified: only 2 files use `next/dynamic` (login, blog slug). Dashboard loads Recharts eagerly. Pipeline loads @dnd-kit eagerly. Every search page loads Shepherd.js even for returning users who dismissed the tour. | No | Sprint 2 |
| FE-020 | 3 Google Fonts loaded globally | MEDIUM | **LOW** | 2h | DM Mono (data font) and Fahkwang (display font) used on few pages but loaded everywhere. Impact is ~50-100ms on slow 3G. Not a priority given target audience (enterprise, good connectivity). | No | Backlog |

### 4.5 Acessibilidade (FE-021 through FE-024)

| ID | Debito | Original Sev | Adjusted Sev | Hours | UX Impact | Design Review? | Sprint |
|----|--------|-------------|-------------|-------|-----------|---------------|--------|
| FE-021 | No `aria-live` for search results | LOW | **MEDIUM** | 2h | WCAG 4.1.3 violation. Screen reader users cannot perceive when search results appear or update. Search is the primary user flow. Verified: `aria-live` exists in 15 non-test files but NOT in search results or search count areas. | No | Sprint 1 |
| FE-022 | No focus trapping in modals | LOW | **MEDIUM** | 4h | WCAG 2.4.3 violation. Tab key escapes Dialog, DeepAnalysisModal, UpgradeModal, CancelSubscriptionModal. Verified: no `focus-trap` library installed, no custom focus trap implementation found. Keyboard-only users are blocked. | No | Sprint 1 |
| FE-023 | Viability indicators color-only | LOW | **MEDIUM** | 2h | WCAG 1.4.1 violation. ViabilityBadge uses green/yellow/red without secondary indicators. ~8% of male users have some form of color vision deficiency. | Yes | Sprint 2 |
| FE-024 | No keyboard shortcut documentation | LOW | **LOW** | 2h | Minor discoverability issue. `useKeyboardShortcuts` exists but no `?` help overlay. Low priority since shortcuts are convenience, not required. | No | Backlog |

### 4.6 Testes e Features Faltantes (FE-025 through FE-030)

| ID | Debito | Original Sev | Adjusted Sev | Hours | UX Impact | Design Review? | Sprint |
|----|--------|-------------|-------------|-------|-----------|---------------|--------|
| FE-025 | No tests for navigation (NavigationShell, Sidebar, BottomNav, MobileDrawer) | LOW | **LOW** | 8h | Indirect: navigation renders on every authenticated page. Regression here is high-blast-radius but low-probability (rarely changed). | No | Backlog |
| FE-026 | 14 quarantined tests (AuthProvider, ContaPage, LicitacaoCard) | LOW | **LOW** | 8h | Indirect: quarantined tests mean no regression protection for critical components. | No | Backlog |
| FE-027 | No PWA/offline support | LOW | **LOW** | 8h | B2G users are office-based with reliable connectivity. PWA is a nice-to-have, not a need. useServiceWorker hook exists but is not wired up. | No | Backlog |
| FE-028 | No structured form validation (no react-hook-form/zod) | LOW | **MEDIUM** | 16h | Direct: manual validation leads to inconsistent error messages, missing validation on edge cases, and no inline validation feedback. Affects signup, conta, onboarding, alertas forms. | Yes | Sprint 2 |
| FE-029 | `react-simple-pull-to-refresh` installed but not used | LOW | **REMOVED** | 0h | **FALSE POSITIVE.** Verified: `PullToRefresh` is imported and actively used in `buscar/page.tsx` (line 6, rendered at line 695). The library wraps the entire search results area for mobile pull-to-refresh. This is NOT a dead dependency. | N/A | N/A |
| FE-030 | No `<Suspense>` boundaries | LOW | **LOW** | 8h | Related to FE-002. Without Suspense, no streaming possible. However, Suspense without loading.tsx or async server components provides no benefit. Address as part of FE-002. | No | Sprint 2 |

---

## Debitos Adicionados

These UX-relevant debts were identified during codebase validation but are absent from the DRAFT v3.0.

| ID | Debito | Severidade | Hours | UX Impact | Design Review? | Sprint |
|----|--------|-----------|-------|-----------|---------------|--------|
| FE-031 | **Dashboard charts not mobile-optimized** -- Recharts Bar/Line/Pie have no mobile-specific layout. Labels overflow, touch targets are too small, charts lack horizontal scroll wrappers. Dashboard is the second most-visited authenticated page. | MEDIUM | 4-6h | Medium: mobile users see truncated/overlapping chart labels | Yes | Sprint 2 |
| FE-032 | **No shared Button component** -- At least 15 distinct button styling patterns across the codebase (inline Tailwind classes). Primary, secondary, ghost, destructive, icon-only variants are all ad-hoc. Most visible inconsistency for users. | HIGH | 4-6h | High: every page has buttons; inconsistency undermines trust | Yes | Sprint 1 |
| FE-033 | **No shared Input/Label component** -- Forms across signup, conta, onboarding, alertas use different input styling. Some use placeholder-as-label (WCAG 1.3.1 violation). | MEDIUM | 3-4h | Medium: forms feel different across pages | Yes | Sprint 2 |
| FE-034 | **Missing icon-only button aria-labels** -- Some icon buttons (sidebar collapse, filter toggles, close buttons) lack aria-label. Screen readers announce only "button" with no context. | HIGH | 1.5h | High: accessibility blocker for screen reader users | No | Sprint 1 |
| FE-035 | **No hook isolation tests for useSearch (1,510 lines)** -- Core search hook tested only indirectly through component tests. Decomposition (part of FE-001 resolution) without dedicated hook tests is high-risk for regressions. | MEDIUM | 8-12h | Medium: indirect, but regressions in search break the primary user flow | No | Sprint 2 |
| FE-036 | **Design tokens partially adopted** -- Mix of CSS custom properties (`var(--brand-blue)`), Tailwind theme tokens, and raw hex values (`#116dff`) across the codebase. No enforcement mechanism. | MEDIUM | 3-4h | Medium: subtle color inconsistencies across pages | Yes | Sprint 2 |

---

## Severity Adjustments

### FE-003 (i18n): HIGH -> LOW

**Justification:** SmartLic is 100% Brazilian market, pre-revenue, with no international expansion plans. The Portuguese strings are heavily domain-specific (licitacao, edital, pregao, CNPJ, modalidade) -- terms that have no direct equivalents in other languages. Spending 40h on i18n infrastructure delivers zero value to current users. If international expansion becomes viable, string extraction can be done mechanically with `react-i18next` tooling. The 40h is better invested in design system primitives (FE-032, FE-033) which have immediate visual impact.

### FE-012 (Error boundaries): MEDIUM -> HIGH

**Justification:** Only `/buscar` has a component-level error boundary. The other 5 most-used authenticated pages (dashboard, pipeline, historico, mensagens, alertas) fall through to the root `error.tsx`. When an unhandled exception occurs on these pages, users lose all page context (scroll position, form state, filter selections) and must re-navigate. For a data-heavy B2G application where users configure complex filters and manage pipelines, this context loss is severe. Adding `error.tsx` files to each route group is low-effort (6h) and high-impact.

### FE-021 (aria-live): LOW -> MEDIUM

**Justification:** Search is the primary user flow. Screen reader users receive no announcement when results load, when the count changes, or when errors occur. This is a WCAG 4.1.3 (Status Messages) AA violation. Given that SmartLic targets government-adjacent enterprises (B2G), accessibility compliance may be contractually required by some buyers. The fix is 2h and non-breaking.

### FE-022 (Focus trapping): LOW -> MEDIUM

**Justification:** Same reasoning as FE-021. Focus escaping modals is a WCAG 2.4.3 violation that prevents keyboard-only users from completing critical flows (plan upgrade, subscription cancellation, deep analysis). The fix involves adding a focus trap library (e.g., `focus-trap-react`) and wrapping each modal. 4h, non-breaking.

### FE-023 (Color-only indicators): LOW -> MEDIUM

**Justification:** ViabilityBadge is rendered on every search result card. Color-only indicators (green = alta, yellow = media, red = baixa) exclude the ~8% of male users with color vision deficiency. Adding text labels or icons alongside color is a 2h fix with meaningful inclusivity improvement. WCAG 1.4.1 (Use of Color) AA violation.

---

## Respostas ao Architect

### 1. Decomposicao de paginas (FE-001)

`conta/page.tsx` at 1,420 lines should be decomposed into sub-routes rather than just sub-components:

```
/conta              -> redirect to /conta/perfil
/conta/perfil       -> Profile editing (CNAE, UFs, porte, contact)
/conta/seguranca    -> Password change, MFA setup (already exists as separate page)
/conta/plano        -> Plan info, billing, cancellation
/conta/dados        -> GDPR export, account deletion
```

Use `conta/layout.tsx` for shared tab navigation. Each tab file stays under 400 lines.

For `buscar/page.tsx` (1,057 lines): this page is already well-decomposed into sub-components (39 components in `app/buscar/components/`). The remaining 1,057 lines are orchestration logic (state wiring, SSE handling, conditional rendering). Further decomposition should focus on extracting the orchestration into a custom hook (`useSearchOrchestration`) rather than creating more visual components.

For `alertas/page.tsx` (1,068 lines): extract `AlertRuleEditor`, `AlertList`, `AlertPreview`, and `AlertPreferences` as separate components. The page should become a layout shell under 200 lines.

For `dashboard/page.tsx` (1,037 lines): extract each chart section (`SearchesOverTime`, `TopSectors`, `UfBreakdown`, `ValueDistribution`) into individual components. Use `React.lazy` for chart components since they import Recharts.

**No wireframes exist.** Infer component boundaries from the existing UI: each visual "card" or "section" on the page is a natural component boundary. The current layout is functional and should be preserved during decomposition.

### 2. loading.tsx streaming (FE-002)

Priority order for `loading.tsx` files:

1. **`/buscar`** (critical) -- Users wait the longest here (search takes 5-30s). A skeleton with search form + empty results grid gives immediate visual feedback.
2. **`/dashboard`** (data-heavy) -- 4 chart sections + stats cards. Show skeleton cards with shimmer animation.
3. **`/pipeline`** (interactive) -- Kanban columns skeleton. Users need to see the structure before drag targets.
4. **`/(protected)/layout.tsx`** -- A shared loading state for the auth check (currently shows a centered spinner via inline code).
5. **`/historico`** -- Simple list skeleton.

Recommended skeleton approach: use the existing `shimmer` Tailwind animation (already defined in tailwind.config.ts) with `bg-gray-200 dark:bg-gray-700 animate-shimmer` blocks matching the page layout. This is 2-3h per page, mostly copy-paste with layout adjustments.

### 3. Consolidacao de componentes (FE-005)

Agreed with the proposed rule:

- `components/` -- Shared/reusable primitives (Button, Input, Card, Badge, EmptyState, ErrorStateWithRetry, PageHeader). These have NO page-specific dependencies.
- `app/components/` -- App-wide providers, layouts, and composed components that depend on auth/plan/routing context (AuthProvider, ThemeProvider, AppHeader, UpgradeModal, TrialBanner).
- `app/buscar/components/` -- Search-feature-specific components (SearchForm, ResultCard, UfProgressGrid, FilterPanel). These depend on search types/hooks.

**Immediate action:** Delete `app/components/EmptyState.tsx` and keep `components/EmptyState.tsx` as canonical (it is the more general implementation). Update all imports.

### 4. Design tokens vs Tailwind raw (FE-016)

**Recommended: Extend Tailwind theme to map CSS custom properties.**

In `tailwind.config.ts`, add:

```ts
colors: {
  brand: {
    navy: 'var(--brand-navy)',
    blue: 'var(--brand-blue)',
  },
  surface: {
    0: 'var(--surface-0)',
    1: 'var(--surface-1)',
    2: 'var(--surface-2)',
  },
  ink: {
    DEFAULT: 'var(--ink)',
    secondary: 'var(--ink-secondary)',
    muted: 'var(--ink-muted)',
  },
  // ... semantic colors
}
```

This gives developers Tailwind utility syntax (`bg-brand-blue`, `text-ink-secondary`) that resolves to CSS custom properties at runtime. Benefits:
- Developers use familiar Tailwind syntax (no `bg-[var(--surface-1)]` awkwardness)
- Dark mode switches automatically via CSS variable overrides
- ESLint/IDE can validate class names
- Single source of truth for all color values
- Gradual migration: new code uses `bg-brand-blue`, old code keeps working

This approach reduces inconsistency risk more than pure CSS variables (which require remembering exact variable names) while being less work than a full design system migration.

### 5. Acessibilidade (FE-021/022/023) priority

**Priority order for WCAG AA compliance:**

1. **FE-022 Focus trapping in modals** (HIGH priority, 4h) -- This is a functional blocker. Keyboard-only users literally cannot complete flows that require modals (plan upgrade, subscription cancel, deep analysis). Install `focus-trap-react` and wrap Dialog, DeepAnalysisModal, UpgradeModal, CancelSubscriptionModal.

2. **FE-034 (new) Missing aria-labels on icon-only buttons** (HIGH priority, 1.5h) -- Screen reader users cannot navigate the sidebar or interact with icon-only actions. Quick fix: add `aria-label` to all `<button>` elements that contain only an icon/SVG.

3. **FE-021 aria-live for search results** (MEDIUM priority, 2h) -- Add `aria-live="polite"` to the results count area and `aria-live="assertive"` to error banners. Non-breaking change.

4. **FE-023 Color-only viability indicators** (MEDIUM priority, 2h) -- Add text labels (Alta/Media/Baixa) alongside the color indicators. Already partially present in some views.

**None are hard blockers for launch**, but FE-022 (focus trapping) would be the most likely to be flagged in an accessibility audit. For B2G contracts, some government entities require WCAG AA compliance, making these fixes strategic rather than merely ethical.

### 6. SWR vs fetch (FE-007)

**Recommended: Standardize on SWR.**

SWR is already installed (v2.4.1) and used in 5 hooks. The migration path:

**Phase 1 (immediate, 4h):** Migrate read-only endpoints that currently use raw `fetch()`:
- `useQuota` -> `useSWR('/api/subscription-status')`
- Analytics endpoints in dashboard -> `useSWR('/api/analytics?endpoint=...')`
- Profile data -> `useSWR('/api/me')`

**Phase 2 (after FE-006 state management, 8h):** Migrate mutation-heavy endpoints:
- Pipeline CRUD -> `useSWRMutation` for POST/PATCH/DELETE
- Feedback submission -> `useSWRMutation`
- Alert management -> `useSWRMutation`

**Leave alone:** The search POST + SSE flow. This is not a data fetching pattern -- it is a long-running operation with real-time progress updates. SSE hooks are purpose-built and should remain custom.

**Why not TanStack Query:** SWR is 4KB vs TanStack Query 13KB. SWR's stale-while-revalidate model mirrors the backend cache semantics. The team is small (1-2 devs) and SWR's simpler API has lower cognitive overhead. TanStack Query's advanced features (infinite queries, structural sharing, query cancellation) are not needed.

---

## Recomendacoes de Design

### Component Architecture Strategy

**Phase 1 -- Primitives (Sprint 1, 10-12h):**
1. Install shadcn/ui CLI and initialize with existing Tailwind config + CSS custom properties
2. Add `Button` component (6 variants: primary, secondary, ghost, destructive, outline, link; 3 sizes: sm, md, lg; states: loading, disabled, icon-only with required aria-label)
3. Add `Input` + `Label` components (with proper label association, error state, disabled state)
4. Consolidate EmptyState to single canonical version in `components/`

**Phase 2 -- Compositions (Sprint 2, 12-16h):**
1. Add `Card` component (with header, body, footer slots; hover state for clickable cards)
2. Add `Badge` component (variants: status, plan, viability, source; standardize the 7+ inline badge implementations)
3. Add `Dialog` component with built-in focus trapping (replaces current Dialog + adds WCAG compliance)
4. Add `Select` component (replaces custom filter selects)

**Phase 3 -- Page-specific (Sprint 3, 8-12h):**
1. `ResultCard` component using Card + Badge primitives
2. `FormField` wrapper combining Input + Label + error message + helper text
3. `DataTable` for admin pages

### SSR Migration Plan

The blog/SEO pages are already Server Components (confirmed: no `"use client"` in `/blog/*`, `/licitacoes/*`, `/como-*`). The remaining SSR opportunity is limited:

1. **Quick win (2h):** Add `generateStaticParams` to programmatic blog pages (`/blog/licitacoes/[setor]/[uf]`, `/blog/panorama/[setor]`, `/blog/programmatic/[setor]/[uf]`) for build-time generation. These pages have a finite set of 15 sectors x 27 UFs.

2. **Medium effort (8h):** Convert `/planos` to hybrid: server component for pricing table (data from Stripe), client component only for the toggle and checkout button. Reduces JS sent to client.

3. **Not recommended now:** Converting `/historico`, `/alertas`, or `/dashboard` to server components. These pages have heavy client interactivity (filters, real-time updates, mutations) that would require significant refactoring for minimal bundle savings.

### Design System Roadmap

| Week | Deliverable | Hours |
|------|------------|-------|
| Week 1 | shadcn/ui init + Button + Tailwind theme token mapping | 8h |
| Week 2 | Input/Label + EmptyState consolidation + replace in 3 high-traffic pages | 6h |
| Week 3 | Badge + Card + replace in search results | 6h |
| Week 4 | Dialog with focus trap + replace all modals | 6h |
| Week 5 | Select + FormField wrapper | 4h |
| Week 6 | Audit and replace remaining raw Tailwind with design tokens | 4h |

**Total: ~34h over 6 weeks.** This is not a big-bang rewrite -- each week produces a usable primitive that is immediately adopted in high-traffic pages.

### Accessibility Remediation Plan

**Tier 0 -- Legal Risk (Sprint 1, 5.5h):**
- FE-034: Add aria-labels to all icon-only buttons (1.5h)
- FE-022: Install focus-trap-react, wrap all 4+ modals (4h)

**Tier 1 -- WCAG AA Compliance (Sprint 1-2, 6h):**
- FE-021: Add aria-live regions to search results area (2h)
- FE-023: Add text labels alongside color indicators on ViabilityBadge (2h)
- FE-033 (Input/Label): Ensure all form inputs have associated labels, not just placeholders (2h, combined with design system work)

**Tier 2 -- Enhancement (Sprint 3+, 6h):**
- Add aria-labels to SVG icons in sidebar (0.5h)
- Audit heading hierarchy on authenticated pages (2h)
- Add form validation announcements via aria-describedby (2h)
- Document keyboard shortcuts via `?` help overlay (1.5h)

**Tier 3 -- Monitoring (ongoing):**
- Enable Lighthouse CI accessibility audit in CI pipeline (part of existing `@lhci/cli` setup)
- Add `@axe-core/playwright` checks to E2E tests (already in devDeps)

---

## Resolution Roadmap

### Sprint 1 (Week 1-2) -- Critical and Quick Wins

| # | ID | Debito | Hours | Justification |
|---|-----|--------|-------|---------------|
| 1 | FE-002 | Add `loading.tsx` to top 5 routes | 10-12h | Most impactful UX improvement: eliminates blank screen on navigation |
| 2 | FE-012 | Add error boundaries to 5 authenticated pages | 6h | Prevents full context loss on unhandled exceptions |
| 3 | FE-032 | Shared Button component (shadcn/ui) | 4-6h | Foundation for all future component work; most visible inconsistency |
| 4 | FE-034 | Add aria-labels to icon-only buttons | 1.5h | Accessibility quick win; legal risk reduction |
| 5 | FE-022 | Focus trapping in modals | 4h | WCAG 2.4.3 compliance; keyboard users unblocked |
| 6 | FE-021 | aria-live for search results | 2h | WCAG 4.1.3 compliance; screen reader users |
| 7 | FE-017 | Fix global-error.tsx brand colors | 0.5h | 5-minute fix with disproportionate brand impact |
| 8 | FE-013 | Fix SearchErrorBoundary red -> blue/yellow | 1h | Aligns with error-messages.ts guidelines |
| 9 | FE-015 | Delete `frontend/app/nul` | 0.5h | Trivial cleanup |
| 10 | FE-009 | Remove console statements from production pages | 1h | Log hygiene |
| 11 | FE-011 | Consolidate EmptyState (delete duplicate) | 1h | Remove confusion |

**Sprint 1 total: ~32-36h**

### Sprint 2 (Week 3-4) -- High Priority Structural

| # | ID | Debito | Hours | Justification |
|---|-----|--------|-------|---------------|
| 12 | FE-001 | Decompose conta/page.tsx into sub-routes | 8-10h | Largest page; enables per-tab testing and loading |
| 13 | FE-006 | Adopt SWR for read-only endpoints (Phase 1) | 8h | Eliminates stale data + duplicate requests |
| 14 | FE-033 | Shared Input/Label component | 3-4h | Form consistency across pages |
| 15 | FE-036 | Extend Tailwind theme with CSS custom properties | 3-4h | Enforcement mechanism for design tokens |
| 16 | FE-023 | Add text labels to ViabilityBadge | 2h | WCAG 1.4.1 compliance |
| 17 | FE-019 | Dynamic imports for Recharts, @dnd-kit, Shepherd.js | 4h | Bundle size reduction for initial load |
| 18 | FE-014 | Add memoization to alertas and dashboard pages | 4h | Reduce re-render jank |
| 19 | FE-031 | Mobile-optimize dashboard charts | 4-6h | Second most-visited page |
| 20 | FE-028 | React-hook-form + zod for top 3 forms | 8h | Structured validation for signup, conta, onboarding |
| 21 | FE-008 | Fix `any` types in 8 production files | 2h | Type safety |

**Sprint 2 total: ~46-52h**

### Backlog (Month 2+) -- Medium/Low Priority

| ID | Debito | Hours | Notes |
|----|--------|-------|-------|
| FE-001 (remaining) | Decompose alertas, dashboard pages | 12-18h | After conta proves the pattern |
| FE-004 | Reduce CSR on 3-5 candidate pages | 12-16h | Depends on FE-006 completion |
| FE-005 | Enforce component directory conventions | 4h | Document rule + eslint import restriction |
| FE-007 (Phase 2) | SWR for mutation endpoints | 8h | After Phase 1 SWR adoption |
| FE-010 | Implement blog programmatic links | 8h | SEO value only |
| FE-018 | Adopt next/image on landing/blog pages | 8h | LCP improvement for marketing pages |
| FE-020 | Lazy-load Fahkwang and DM Mono fonts | 2h | Minor perf win |
| FE-024 | Keyboard shortcut help overlay | 2h | Nice-to-have |
| FE-025 | Navigation component tests | 8h | After component structure stabilizes |
| FE-026 | Resolve 14 quarantined tests | 8h | Debug and re-enable or delete |
| FE-027 | PWA/offline investigation | 8h | Only if user demand emerges |
| FE-030 | Add Suspense boundaries (with FE-002) | 8h | After loading.tsx proves the pattern |
| FE-003 | i18n framework | 40h | Only if international expansion is planned |
| FE-035 | useSearch hook isolation tests | 8-12h | Before major search refactoring |

**Backlog total: ~130-160h**

---

## Cross-Cutting Items Affecting UX

From Section 5 of the DRAFT, these cross-cutting debts have direct UX implications:

| ID | Debito | UX Impact | Recommendation |
|----|--------|-----------|---------------|
| CROSS-002 | No API contract validation in CI | Frontend types can diverge from backend, causing silent breakage (undefined fields, wrong types). Users see broken pages with no error message. | HIGH priority. Add `openapi-diff` step to CI that fails on breaking changes. |
| CROSS-004 | Naming inconsistency (BidIQ vs SmartLic) | If "BidIQ" leaks into user-visible text (unlikely but possible via error messages), it confuses users. | LOW priority but quick fix. |
| SYS-008 | Frontend proxy route explosion (58 routes) | Indirect: each new backend endpoint requires a new proxy file, slowing feature delivery. No UX impact per se but increases time-to-user for new features. | MEDIUM priority. Create `createProxyRoute()` utility to reduce boilerplate. |
| SYS-019 | No CDN for static assets | Direct: users in remote regions (Norte/Nordeste Brazil) experience slower page loads. Railway serves from a single region. | MEDIUM priority for conversion optimization. |

---

*End of UX Specialist Review v2.0*
*Next step: Consolidation with @data-engineer and @qa reviews into FINAL technical debt assessment.*
