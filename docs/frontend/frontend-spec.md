# SmartLic Frontend Specification & UX Audit

**Date:** 2026-03-21
**Auditor:** @ux-design-expert (Uma) — Brownfield Discovery
**Stack:** Next.js 16.1, React 18.3, TypeScript 5.9, Tailwind CSS 3.4, Framer Motion 12
**Language:** pt-BR (user-facing), English (code/docs)

---

## 1. App Structure Overview

### 1.1 Directory Layout

```
frontend/
  app/                    # Next.js App Router (335 TS/TSX files, ~56,700 LOC)
    (protected)/          # Route group — auth guard, AppHeader, Breadcrumbs
    admin/                # Admin pages (dashboard, cache, emails, metrics, partners, SLO)
    ajuda/                # Help / FAQ
    alertas/              # Alert configuration (feature-gated)
    api/                  # 57 API proxy routes
    auth/                 # OAuth callback
    blog/                 # 30 editorial articles + programmatic SEO pages
    buscar/               # Core search page — 47 components, 9 hooks, 270 LOC page
    como-*/               # 4 SEO content pages
    components/           # App-level shared components (66 files)
    conta/                # Account settings (5 sub-pages: dados, equipe, perfil, plano, seguranca)
    dashboard/            # Analytics dashboard (10 component files)
    features/             # Features marketing page
    historico/            # Search history
    licitacoes/           # Programmatic SEO sector pages
    login/                # Login (502 LOC, password + magic link + MFA)
    mensagens/            # Messaging (feature-gated)
    onboarding/           # 3-step wizard (783 LOC)
    pipeline/             # Kanban opportunity pipeline (5 component files)
    planos/               # Pricing + thank-you page
    pricing/              # Alternative pricing route
    privacidade/          # Privacy policy
    recuperar-senha/      # Password recovery
    redefinir-senha/      # Password reset
    signup/               # Registration (703 LOC, react-hook-form + zod)
    sobre/                # About page
    status/               # Public status page (uptime chart, incidents)
    termos/               # Terms of service
  components/             # Global shared components (49 files)
  contexts/               # UserContext.tsx (unified auth+plan+quota+trial)
  hooks/                  # 27 global custom hooks
  lib/                    # 37 utility modules
  styles/                 # (empty — globals.css is in app/)
  __tests__/              # 306 unit test files
  e2e-tests/              # 31 Playwright spec files
```

### 1.2 Route Map (47 pages)

| Route | Type | Auth | LOC | Notes |
|-------|------|------|-----|-------|
| `/` | Landing | Public | 35 | Server component, 7 sections |
| `/login` | Auth | Public | 502 | Password + magic link + TOTP MFA |
| `/signup` | Auth | Public | 703 | react-hook-form + zod validation |
| `/auth/callback` | Auth | Public | ~80 | OAuth/magic-link callback |
| `/recuperar-senha` | Auth | Public | ~120 | Password recovery |
| `/redefinir-senha` | Auth | Public | ~150 | Password reset |
| `/onboarding` | Wizard | Protected | 783 | 3-step (CNAE > UFs > Confirm) |
| `/buscar` | Core | Protected | 270 | Main search — SSE, filters, results |
| `/dashboard` | Analytics | Protected | 279 | Charts, stat cards, insights |
| `/pipeline` | Kanban | Protected | 376 | Drag-and-drop with @dnd-kit |
| `/historico` | History | Protected | 426 | Saved search sessions |
| `/conta` | Account | Protected | 22 | Tab router to 5 sub-pages |
| `/conta/dados` | Account | Protected | ~200 | Personal data |
| `/conta/perfil` | Account | Protected | ~250 | Profile (react-hook-form) |
| `/conta/plano` | Account | Protected | ~300 | Subscription management |
| `/conta/seguranca` | Account | Protected | ~200 | Password change, MFA |
| `/conta/equipe` | Account | Protected | ~250 | Team / organization |
| `/mensagens` | Messaging | Protected | 547 | Feature-gated |
| `/alertas` | Alerts | Protected | 222 | Feature-gated |
| `/planos` | Pricing | Public | 714 | Plan cards, billing periods |
| `/planos/obrigado` | Post-purchase | Protected | ~100 | Thank-you page |
| `/admin` | Admin | Protected | 764 | Admin dashboard |
| `/admin/cache` | Admin | Protected | ~200 | Cache management |
| `/admin/emails` | Admin | Protected | ~200 | Email management |
| `/admin/metrics` | Admin | Protected | ~200 | Prometheus metrics |
| `/admin/partners` | Admin | Protected | ~200 | Partner management |
| `/admin/slo` | Admin | Protected | ~200 | SLO monitoring |
| `/ajuda` | Help | Public | ~300 | FAQ with structured data |
| `/blog` | SEO | Public | ~200 | Blog index |
| `/blog/[slug]` | SEO | Public | ~150 | 30 article pages |
| `/blog/licitacoes` | SEO | Public | ~100 | Programmatic index |
| `/blog/licitacoes/[setor]/[uf]` | SEO | Public | ~100 | Programmatic pages |
| `/blog/panorama/[setor]` | SEO | Public | ~100 | Sector panorama |
| `/blog/programmatic/[setor]` | SEO | Public | ~100 | Programmatic sector |
| `/blog/programmatic/[setor]/[uf]` | SEO | Public | ~100 | Programmatic sector+UF |
| `/licitacoes` | SEO | Public | ~150 | Sector listing |
| `/licitacoes/[setor]` | SEO | Public | ~150 | Sector detail |
| `/features` | Marketing | Public | ~300 | Features page |
| `/pricing` | Marketing | Public | ~200 | Alternative pricing |
| `/sobre` | Institutional | Public | ~200 | About page |
| `/status` | Public | Public | ~200 | Status page with uptime |
| `/termos` | Legal | Public | ~100 | Terms of service |
| `/privacidade` | Legal | Public | ~100 | Privacy policy |
| `/como-avaliar-licitacao` | SEO | Public | ~200 | Content page |
| `/como-evitar-prejuizo-licitacao` | SEO | Public | ~200 | Content page |
| `/como-filtrar-editais` | SEO | Public | ~200 | Content page |
| `/como-priorizar-oportunidades` | SEO | Public | ~200 | Content page |

### 1.3 Layout Hierarchy

```
RootLayout (app/layout.tsx) — lang="pt-BR", fonts, providers
  ├── AnalyticsProvider (Mixpanel)
  │   └── AuthProvider (Supabase auth)
  │       └── SWRProvider (global SWR config)
  │           └── UserProvider (unified auth+plan+quota+trial context)
  │               └── ThemeProvider (dark/light mode)
  │                   └── NProgressProvider (route transition bar)
  │                       └── BackendStatusProvider (health polling)
  │                           ├── SessionExpiredBanner
  │                           ├── PaymentFailedBanner
  │                           └── NavigationShell (conditional sidebar/bottomnav)
  │                               └── {children}
  │
  ├── (protected)/layout.tsx — Auth guard, AppHeader, Breadcrumbs
  │   └── Suspense + loading.tsx skeleton
  │
  └── Per-route layouts: login, signup, ajuda, planos, dashboard, pipeline, historico, conta
```

### 1.4 Middleware

`middleware.ts` (274 LOC) handles:
- **CSP enforcement** with per-request nonce (DEBT-108 completed)
- **Route protection** — 8 protected route prefixes redirect to `/login` with reason codes
- **Canonical domain redirect** — `*.railway.app` -> `smartlic.tech` (301)
- **Security headers**: HSTS preload, X-Frame-Options DENY, COOP same-origin, X-DNS-Prefetch-Control off, Permissions-Policy
- **Auth validation**: Uses `supabase.auth.getUser()` (server-side, secure) not `getSession()`
- Distinguishes "never logged in" vs "session expired" via cookie inspection

---

## 2. Component Inventory

### 2.1 Component Count Summary

| Location | Files | Purpose |
|----------|-------|---------|
| `app/buscar/components/` | 47 | Search-specific (forms, filters, results, banners) |
| `app/components/` | 66 | App-level shared (auth, landing, UI primitives) |
| `app/components/landing/` | 13 | Landing page sections |
| `app/components/ui/` | 6 | UI primitives (Tooltip, BentoGrid, GlassCard, etc.) |
| `app/dashboard/components/` | 10 | Dashboard widgets |
| `app/pipeline/` | 4 | Pipeline kanban components |
| `app/alertas/components/` | 8 | Alert management |
| `app/status/components/` | 3 | Status page widgets |
| `components/` | 49 | Global shared (Button, Input, Sidebar, etc.) |
| `components/ui/` | 6 | Design system primitives |
| `components/billing/` | 4 | Billing UI |
| `components/auth/` | 3 | MFA components |
| `components/subscriptions/` | 6 | Plan cards, toggles |
| `components/blog/` | 3 | Blog components |
| **Total** | **~239** | |

### 2.2 Design System Primitives (`components/ui/`)

| Component | Variants | A11y |
|-----------|----------|------|
| `Button` | 6 variants (primary, secondary, destructive, ghost, link, outline) x 4 sizes | Icon-only requires aria-label (TypeScript enforced), focus-visible ring, loading state spinner |
| `Input` | 3 sizes x 3 states (default, error, success) | aria-invalid, aria-describedby, error role="alert" |
| `Label` | Standard | htmlFor association |
| `Pagination` | Standard | aria-label |
| `CurrencyInput` | Standard | Formatted number input |
| `Tooltip` | Standard | Accessible tooltip |

### 2.3 Key Business Components

| Component | Location | Purpose |
|-----------|----------|---------|
| `SearchForm` | buscar/components | Search input orchestrator (125 LOC, delegates to 3 sub-components) |
| `SearchResults` | buscar/components | Results display with counters, badges (249 LOC) |
| `ResultCard` | buscar/components/search-results | Individual bid card (200 LOC) |
| `EnhancedLoadingProgress` | buscar/components | SSE progress with UF grid (452 LOC) |
| `FilterPanel` | buscar/components | Post-search result filtering (119 LOC) |
| `PipelineKanban` | pipeline/ | Drag-and-drop kanban board |
| `NavigationShell` | components/ | Conditional sidebar/bottom nav wrapper |
| `Sidebar` | components/ | Desktop left navigation (collapsible, persisted state) |
| `BottomNav` | components/ | Mobile bottom tab bar |

---

## 3. State Management

### 3.1 Context Providers (4 layers)

| Provider | Location | State |
|----------|----------|-------|
| `AuthProvider` | app/components/ | Supabase session, user, isAdmin, sessionExpired, signOut |
| `UserProvider` | contexts/ | Unified: auth + plan + quota + trial (DEBT-011 FE-006) |
| `ThemeProvider` | app/components/ | Dark/light mode with localStorage persistence |
| `BackendStatusProvider` | app/components/ | Backend health polling (30s, visibility-gated) |

### 3.2 Custom Hooks (27 global + 9 search-specific)

**Global hooks (`hooks/`):**

| Hook | Purpose | Data Source |
|------|---------|-------------|
| `usePlan` | Current user plan info with localStorage cache (1hr TTL) | `/api/subscription-status` |
| `useQuota` | Search quota remaining | `/api/me` |
| `useTrialPhase` | Trial days remaining, phase | Derived from plan |
| `usePipeline` | Pipeline CRUD | `/api/pipeline` |
| `useConversations` | Message threads | `/api/messages/conversations` |
| `useAlerts` | Alert CRUD | `/api/alerts` |
| `useAlertPreferences` | Alert notification prefs | `/api/alert-preferences` |
| `useOrganization` | Org/team management | `/api/organizations` |
| `useUserProfile` | User profile data | `/api/me` |
| `useProfileContext` | Profile context (sector, UFs) | `/api/profile-context` |
| `useProfileCompleteness` | Profile completion % | `/api/profile-completeness` |
| `useAnalytics` | Mixpanel event tracking | Mixpanel SDK |
| `useFeatureFlags` | Feature flag checks | Local config |
| `useKeyboardShortcuts` | Global keyboard shortcuts | Event listeners |
| `useIsMobile` | Responsive breakpoint | Window resize |
| `useNavigationGuard` | Prevent accidental navigation | beforeunload |
| `useSessions` | Session history | `/api/sessions` |
| `useSavedSearches` | Saved search management | localStorage |
| `useSearchPolling` | Async search status polling | `/api/search-status` |
| `useSearchSSE` | SSE connection management | EventSource |
| `useBroadcastChannel` | Cross-tab communication | BroadcastChannel API |
| `useFetchWithBackoff` | Exponential backoff fetch | Custom fetch |
| `useShepherdTour` | Product tour (Shepherd.js) | Local state |
| `useServiceWorker` | SW registration | ServiceWorker API |
| `usePublicMetrics` | Public landing page metrics | `/api/metrics/*` |
| `useUnreadCount` | Unread message count | `/api/messages/unread-count` |
| `usePlans` | All available plans | `/api/plans` |

**Search-specific hooks (`app/buscar/hooks/`):**

| Hook | LOC | Purpose |
|------|-----|---------|
| `useSearchOrchestration` | 600 | Top-level orchestrator (trial, tour, keyboard, persistence) |
| `useSearchExecution` | 770 | Core search logic (API call, SSE, retry, error handling) |
| `useSearchFilters` | 600 | Sector fetch, UF state, date ranges, validation |
| `useSearch` | 398 | Composes execution + SSE + retry + export |
| `useSearchExport` | 304 | Excel download, Google Sheets export |
| `useSearchSSEHandler` | 229 | SSE event parsing and state updates |
| `useSearchPersistence` | 193 | localStorage save/restore of search state |
| `useSearchRetry` | 144 | Auto-retry with countdown timer |
| `useUfProgress` | 49 | Per-UF progress tracking from SSE |
| **Total** | **3,287** | |

### 3.3 Data Flow Patterns

- **SWR**: Global provider with `revalidateOnFocus: false`, `dedupingInterval: 5s`, `errorRetryCount: 3`
- **localStorage**: Safe wrappers (`safeSetItem/safeGetItem/safeRemoveItem`) with quota eviction. Used for theme, sidebar state, onboarding status, plan cache, saved searches, last search results, search state persistence
- **SSE**: Dual-connection pattern — `POST /buscar` (initiates search) + `GET /buscar-progress/{id}` (SSE stream for real-time UF progress)
- **BroadcastChannel**: Cross-tab auth state sync

---

## 4. API Layer

### 4.1 API Proxy Routes (57 routes)

All backend calls go through Next.js API routes in `app/api/` which:
- Forward Supabase auth tokens
- Add correlation IDs
- Handle error translation
- Rate-limit sensitive endpoints

**Key proxy routes:**

| Route | Methods | Backend Target |
|-------|---------|----------------|
| `/api/buscar` | POST | `/buscar` — main search |
| `/api/buscar-progress` | GET | `/buscar-progress/{id}` — SSE stream |
| `/api/buscar-results/[searchId]` | GET | `/v1/search/{id}/status` |
| `/api/pipeline` | GET, POST, PATCH, DELETE | `/pipeline` |
| `/api/analytics` | GET | Multiple analytics endpoints |
| `/api/subscription-status` | GET | `/subscription/status` |
| `/api/plans` | GET | `/plans` |
| `/api/download` | GET | Excel file download |
| `/api/feedback` | POST, DELETE | `/feedback` |
| `/api/alerts` | GET, POST | `/v1/alerts` |
| `/api/alerts/[id]` | PATCH, DELETE | `/v1/alerts/{id}` |
| `/api/messages/conversations` | GET, POST | Messaging endpoints |
| `/api/auth/*` | Various | Auth flows (login, signup, OAuth, MFA) |
| `/api/admin/[...path]` | Various | Admin wildcard proxy |
| `/api/health` | GET | Always 200 (frontend-only check) |
| `/api/csp-report` | POST | CSP violation collector |

### 4.2 SSE Handling

- **Backend**: `progress.py` uses `asyncio.Queue` per `search_id`
- **Frontend proxy**: `undici.Agent({ bodyTimeout: 0 })` to prevent timeout, AbortController for cleanup
- **Client**: `useSearchSSE` hook manages EventSource lifecycle, heartbeat monitoring
- **Fallback**: If SSE fails, `EnhancedLoadingProgress` uses time-based simulation
- **Events**: `uf_complete`, `llm_ready`, `excel_ready`, `search_complete`, `search_error`

---

## 5. Styling & Design System

### 5.1 Design Tokens

**globals.css** (615 LOC) defines a comprehensive CSS custom property system:

- **Canvas & Ink**: 5-level text hierarchy (ink, ink-secondary, ink-muted, ink-faint) with documented WCAG contrast ratios
- **Brand**: Navy (#0a1e3f) + Blue (#116dff) + Hover + Subtle
- **Surfaces**: 4-level hierarchy (surface-0 through surface-elevated)
- **Semantic**: Success, Error, Warning with subtle backgrounds
- **Gem palette**: Sapphire, Emerald, Amethyst, Ruby (translucent accents)
- **Chart palette**: 10 colors for Recharts data visualization
- **Shadows**: 7 levels (sm through 2xl + glow variants)
- **Fluid typography**: clamp()-based (hero: 40-72px, h1: 32-56px, h2: 24-40px)

**Dark mode**: Full `:root` / `.dark` dual token system with recalculated contrast ratios.

### 5.2 Tailwind Configuration

`tailwind.config.ts` (158 LOC) extends defaults with:
- All CSS custom properties mapped to Tailwind classes
- Custom border-radius tokens: `input: 4px`, `button: 6px`, `card: 8px`, `modal: 12px`
- 3 font families: body (DM Sans), display (Fahkwang), data (DM Mono)
- 8 custom animations: fade-in-up, gradient, shimmer, float, slide-up, scale-in, slide-in-right, bounce-gentle
- `darkMode: "class"` — manual toggle with localStorage persistence
- `@tailwindcss/typography` plugin

### 5.3 Typography

| Font | Role | Weight | Preload |
|------|------|--------|---------|
| DM Sans | Body text | Variable | Yes |
| Fahkwang | Display headings | 400-700 | No (FE-020) |
| DM Mono | Data/code | 400-500 | No (FE-020) |

### 5.4 Animation Patterns

- **Framer Motion**: Used in 9 files (landing sections, carousels, comparison tables)
- **CSS animations**: 8 keyframe animations in Tailwind config
- **NProgress**: Route transition progress bar
- **Skeleton loaders**: Dedicated `loading.tsx` files for buscar, dashboard, pipeline, historico, protected layout

### 5.5 Responsive Design

- Mobile-first approach with Tailwind breakpoints (sm/md/lg/xl)
- `BottomNav` for mobile (visible `md:hidden`)
- `Sidebar` for desktop (visible `hidden md:block`)
- `MobileDrawer` for hamburger menu on search page
- `useIsMobile` hook for JavaScript-level breakpoint detection
- Minimum touch targets: `min-height: 44px` on buttons and form inputs (globals.css)
- `react-simple-pull-to-refresh` for mobile pull-to-refresh on search

---

## 6. Testing

### 6.1 Test Coverage

| Type | Files | Tests | Passing | Failing | Framework |
|------|-------|-------|---------|---------|-----------|
| Unit/Integration | 306 | ~5,583 | ~5,580 | ~3 pre-existing | Jest + Testing Library |
| E2E | 31 | ~60 | Varies | - | Playwright |
| Accessibility E2E | 2 | - | - | - | @axe-core/playwright |
| **Total** | **339** | | | | |

### 6.2 Test Patterns

- `jest.setup.js` polyfills: `crypto.randomUUID`, `EventSource` (jsdom lacks both)
- Mock strategies: Auth via `useAuth` mock, API via fetch mock, Supabase via client mock
- `@jest-environment node` for API route tests (provides Request global)
- Module name mapper: `@/` maps to `<rootDir>/` (NOT `<rootDir>/app/`)
- Coverage threshold: 60% (CI gate)

### 6.3 E2E Tests

31 Playwright specs covering:
- Happy path search flow, validation errors, error handling
- Authentication UX, signup consent
- Pipeline kanban, dashboard flows
- Landing page, institutional pages
- Billing checkout, plan display
- Mobile viewport, theme switching
- SSE failure modes, performance
- Accessibility audit (axe-core)
- SEO schema validation, CTA validation

---

## 7. Dependencies Analysis

### 7.1 Key Production Dependencies

| Package | Version | Purpose | Bundle Impact |
|---------|---------|---------|---------------|
| next | 16.1.6 | Framework | Core |
| react / react-dom | 18.3.1 | UI library | Core |
| @supabase/ssr + supabase-js | 0.8 / 2.95 | Auth + DB | Medium |
| swr | 2.4.1 | Data fetching | Small |
| framer-motion | 12.33.0 | Animations | **Large (~50KB)** |
| recharts | 3.7.0 | Charts | **Large (~80KB)** |
| @dnd-kit/* | 6.3/10.0/3.2 | Drag-and-drop | Medium |
| lucide-react | 0.563.0 | Icons (tree-shakeable) | Small per icon |
| shepherd.js | 14.5.1 | Product tour | Medium |
| zod | 4.3.6 | Schema validation | Small |
| date-fns | 4.1.0 | Date utils (tree-shakeable) | Small |
| sonner | 2.0.7 | Toast notifications | Small |
| mixpanel-browser | 2.74.0 | Analytics | Medium |
| @sentry/nextjs | 10.38.0 | Error monitoring | Medium |
| react-day-picker | 9.13.0 | Date picker | Small |
| react-simple-pull-to-refresh | 1.3.4 | Pull to refresh | Small |
| class-variance-authority | 0.7.1 | Variant styling | Tiny |
| clsx / tailwind-merge | 2.1/3.5 | Class merging | Tiny |
| focus-trap-react | 12.0.0 | Focus management | Small |
| nprogress | 0.2.0 | Route progress bar | Tiny |
| uuid | 13.0.0 | UUID generation | Tiny |
| use-debounce | 10.1.0 | Debounce hook | Tiny |

### 7.2 Observations

- **framer-motion** and **recharts** are the two heaviest dependencies. framer-motion is only used in 9 files (mostly landing page) but is loaded globally.
- **shepherd.js** is loaded for product tours but could be lazy-loaded.
- **react-hook-form** is in devDependencies (should be in dependencies since it is used in production pages: signup, onboarding, profile).

---

## 8. UX / Frontend Technical Debt

### FE-DEBT-001 — react-hook-form in devDependencies
- **Category:** Maintainability
- **Severity:** High
- **Description:** `react-hook-form` is listed under `devDependencies` in `package.json` but is imported and used in production pages (`signup/page.tsx`, `onboarding/page.tsx`, `conta/perfil/page.tsx`). This works only because `next build` bundles it regardless, but it is semantically wrong and could break in certain deployment scenarios.
- **Impact:** Potential build failures in strict dependency resolution environments.
- **Recommendation:** Move `react-hook-form` from devDependencies to dependencies.
- **Effort:** 0.5h

### FE-DEBT-002 — Inconsistent form handling patterns
- **Category:** Consistency
- **Severity:** Medium
- **Description:** Only 3 pages use `react-hook-form` + `zod`. The login page (502 LOC) uses raw `useState` for email/password with no schema validation. The recuperar-senha and redefinir-senha pages also use raw `useState`. Meanwhile signup and onboarding use proper form libraries.
- **Impact:** Inconsistent validation UX; login form lacks real-time validation feedback.
- **Recommendation:** Migrate remaining forms (login, recuperar-senha, redefinir-senha, conta/dados, conta/seguranca) to react-hook-form + zod. This was partially noted as STORY-203 FE-M03 (pending).
- **Effort:** 8h

### FE-DEBT-003 — SearchForm has zero ARIA attributes
- **Category:** Accessibility
- **Severity:** High
- **Description:** `SearchForm.tsx` (125 LOC) contains no `aria-*` attributes. It delegates to sub-components, but the form wrapper itself lacks `role="search"`, `aria-label`, or `aria-live` regions for announcing results. The search input and sector selector have no programmatic labels visible to screen readers in the composed form context.
- **Impact:** Screen reader users cannot identify the search form purpose or receive search result announcements.
- **Recommendation:** Add `role="search"` to the form container, `aria-label="Buscar licitacoes"`, and `aria-live="polite"` on the results count area.
- **Effort:** 3h

### FE-DEBT-004 — Framer Motion loaded globally, used in 9 files
- **Category:** Performance
- **Severity:** Medium
- **Description:** `framer-motion` (~50KB gzipped) is a production dependency loaded in the global bundle. It is only used in 9 files, primarily landing page sections and a few app components. Pages that never animate (buscar, dashboard, pipeline, historico) still pay the bundle cost.
- **Impact:** Increased initial bundle size for all pages by ~50KB.
- **Recommendation:** Lazy-load framer-motion via `dynamic()` or use CSS animations (already defined in Tailwind config) for simpler animations. Consider `next/dynamic` with `ssr: false` for landing page sections.
- **Effort:** 6h

### FE-DEBT-005 — Large monolithic page files
- **Category:** Maintainability
- **Severity:** Medium
- **Description:** Several page files exceed 500 LOC: `onboarding/page.tsx` (783), `admin/page.tsx` (764), `planos/page.tsx` (714), `signup/page.tsx` (703), `mensagens/page.tsx` (547), `login/page.tsx` (502). These pages mix layout, state management, and business logic in a single file.
- **Impact:** Difficult to maintain, test, and review. Higher cognitive load for developers.
- **Recommendation:** Extract sub-components and hooks. For example, onboarding could have `OnboardingStep1.tsx`, `OnboardingStep2.tsx`, `OnboardingStep3.tsx` + `useOnboardingForm.ts`.
- **Effort:** 16h

### FE-DEBT-006 — Search hooks complexity (3,287 LOC in 9 hooks)
- **Category:** Maintainability
- **Severity:** Medium
- **Description:** The search functionality is split across 9 hooks totaling 3,287 LOC. `useSearchExecution` alone is 770 LOC and `useSearchOrchestration` is 600 LOC. While the decomposition is logical, the deep hook composition tree makes debugging and testing difficult.
- **Impact:** High onboarding cost for new developers; difficult to trace state flow.
- **Recommendation:** Document the hook dependency graph. Consider a state machine approach (XState) for the search lifecycle instead of scattered useState across 9 hooks.
- **Effort:** 24h (refactor) or 4h (documentation)

### FE-DEBT-007 — Blog TODO placeholders (60+ instances)
- **Category:** Consistency
- **Severity:** Low
- **Description:** All 30 blog articles contain identical TODO comments: `{/* TODO: Link para pagina programatica de setor -- MKT-003 */}` and `{/* TODO: Link para pagina programatica de cidade -- MKT-005 */}`. These are rendered as empty JSX but indicate incomplete internal linking.
- **Impact:** Missing internal links reduce SEO value and user navigation in blog content.
- **Recommendation:** Implement the programmatic page linking or remove TODOs if pages already exist at `/blog/programmatic/[setor]`.
- **Effort:** 4h

### FE-DEBT-008 — Missing error boundaries on some protected pages
- **Category:** UX
- **Severity:** Medium
- **Description:** Error boundaries (`error.tsx`) exist for: admin, alertas, buscar, conta, dashboard, historico, mensagens, pipeline, and root. However, the following protected pages lack dedicated error boundaries: onboarding, planos/obrigado, signup, login. The root error boundary catches these, but it loses the navigation context.
- **Impact:** Errors on onboarding or signup result in a full-page error with no navigation, potentially losing the user.
- **Recommendation:** Add `error.tsx` to onboarding/, signup/, and login/ directories with appropriate recovery actions.
- **Effort:** 3h

### FE-DEBT-009 — No i18n/l10n infrastructure
- **Category:** Consistency
- **Severity:** Low
- **Description:** All user-facing strings are hardcoded in Portuguese throughout the codebase. There is no i18n library (next-intl, react-i18next) or string extraction pattern. The `lang="pt-BR"` is set correctly in the root layout.
- **Impact:** Internationalization would require touching every file. Not critical for current pt-BR-only market.
- **Recommendation:** Accept as intentional for current market. If internationalization is needed, adopt `next-intl` and extract strings incrementally.
- **Effort:** 80h+ (full i18n)

### FE-DEBT-010 — Duplicate LoadingProgress components
- **Category:** Consistency
- **Severity:** Low
- **Description:** Two LoadingProgress components exist: `app/components/LoadingProgress.tsx` (app-level) and `components/LoadingProgress.tsx` (global). Similarly, `AddToPipelineButton` exists in both `app/components/` and `components/`. This creates confusion about which to import.
- **Impact:** Developer confusion, potential inconsistency if one is updated but not the other.
- **Recommendation:** Audit for actual usage, consolidate duplicates, and establish a clear convention (app/components for page-specific, components/ for truly shared).
- **Effort:** 2h

### FE-DEBT-011 — Missing skip-link target on some pages
- **Category:** Accessibility
- **Severity:** Medium
- **Description:** The root layout includes a "Pular para conteudo principal" skip link targeting `#main-content`. The landing page has `<main id="main-content">`, but the `(protected)/layout.tsx` uses `<main>` without an `id`. This means the skip link does not work on any protected page.
- **Impact:** Keyboard/screen reader users cannot bypass navigation on the most-used pages (buscar, dashboard, pipeline).
- **Recommendation:** Add `id="main-content"` to the `<main>` tag in `(protected)/layout.tsx`.
- **Effort:** 0.5h

### FE-DEBT-012 — Feature-gated pages still routable
- **Category:** UX
- **Severity:** Low
- **Description:** `/alertas` and `/mensagens` are feature-gated (SHIP-002 AC9) — hidden from navigation but still accessible via direct URL. The pages render but API calls return 404, showing error states without explanation.
- **Impact:** Users who discover these URLs see broken pages with no context about why.
- **Recommendation:** Add a feature-gate wrapper component that shows "Em breve" (Coming soon) message when feature flags are off.
- **Effort:** 2h

### FE-DEBT-013 — No skeleton loaders for some pages
- **Category:** UX
- **Severity:** Low
- **Description:** Loading skeletons exist for buscar, dashboard, pipeline, historico, and the protected layout. Pages without dedicated skeletons: admin (all sub-pages), conta, alertas, mensagens, planos. These show a generic spinner.
- **Impact:** Perceived performance is worse on pages without content-shaped skeletons.
- **Recommendation:** Add `loading.tsx` with content-shaped skeletons for admin, conta, and planos pages.
- **Effort:** 4h

### FE-DEBT-014 — EnhancedLoadingProgress is 452 LOC
- **Category:** Maintainability
- **Severity:** Low
- **Description:** `EnhancedLoadingProgress.tsx` (452 LOC) is the largest single component. It handles SSE progress visualization, UF grid, phase transitions, and fallback simulation all in one file.
- **Impact:** Difficult to test and maintain individual behaviors.
- **Recommendation:** Extract sub-components: `ProgressPhaseIndicator`, `UfProgressMap`, `FallbackSimulation`.
- **Effort:** 4h

### FE-DEBT-015 — BottomNav uses wrong icon for Dashboard
- **Category:** UX
- **Severity:** Low
- **Description:** In `BottomNav.tsx` line 48, the Dashboard item uses `icons.search` instead of a dashboard-specific icon (should be `LayoutDashboard` like in Sidebar).
- **Impact:** Visual inconsistency between mobile bottom nav and desktop sidebar.
- **Recommendation:** Change Dashboard icon to `LayoutDashboard` in MAIN_ITEMS.
- **Effort:** 0.5h

### FE-DEBT-016 — Raw CSS variable usage in some components
- **Category:** Consistency
- **Severity:** Low
- **Description:** Some components use raw CSS variables (`text-[var(--ink-secondary)]`, `bg-[var(--surface-0)]`) instead of the Tailwind semantic classes (`text-ink-secondary`, `bg-surface-0`). DEBT-012 in tailwind.config.ts notes this as a known issue. The buscar/page.tsx header alone has 6 instances of `var(--...)` in className.
- **Impact:** Inconsistent styling approach, harder to search/refactor, no Tailwind intellisense.
- **Recommendation:** Replace `text-[var(--ink-secondary)]` with `text-ink-secondary` across all components. Use a codemod or search-and-replace.
- **Effort:** 4h

---

## 9. Security

### 9.1 Implemented

- CSP enforcement with per-request nonce (DEBT-108 completed)
- HSTS preload with 1-year max-age
- X-Frame-Options DENY (clickjacking prevention)
- COOP same-origin (Spectre mitigation)
- Auth via `getUser()` not `getSession()` (server-validated)
- Supabase RLS on all tables
- API proxy pattern (backend URL not exposed to client)
- CSP violation reporting to `/api/csp-report`
- Rate limiting on auth endpoints
- Cookie consent banner (LGPD compliance)

### 9.2 Accepted Risks

- `style-src 'unsafe-inline'` — required by Tailwind/Next.js runtime styles (DEBT-116)
- localStorage used for non-sensitive caching (plan info, theme, search state)

---

## 10. Summary Metrics

| Metric | Value |
|--------|-------|
| Total pages | 47 |
| Total components | ~239 |
| Total hooks | 36 (27 global + 9 search) |
| API proxy routes | 57 |
| Unit test files | 306 |
| E2E test files | 31 |
| Blog articles | 30 |
| App TSX/TS files | 335 |
| App total LOC | ~56,700 |
| globals.css LOC | 615 |
| Design tokens (CSS vars) | ~80 |
| Custom animations | 8 |
| Technical debt items | 16 |
| Critical debt | 0 |
| High severity debt | 2 (FE-DEBT-001, FE-DEBT-003) |
| Medium severity debt | 6 |
| Low severity debt | 8 |
| Estimated total fix effort | ~157h |
