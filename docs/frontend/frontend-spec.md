# SmartLic Frontend Specification & UX Audit

> Generated: 2026-03-10 | Brownfield Discovery Phase 3 (updated)
> Stack: Next.js 16.1.6 + React 18.3.1 + TypeScript 5.9.3 + Tailwind CSS 3.4.19

---

## 1. Architecture Overview

### Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Framework | Next.js (App Router) | 16.1.6 |
| UI Library | React | 18.3.1 |
| Language | TypeScript (strict) | 5.9.3 |
| Styling | Tailwind CSS + CSS Variables | 3.4.19 |
| State (server) | SWR | 2.4.1 |
| State (client) | React Context (4 providers) | -- |
| Forms | react-hook-form + zod | 7.71.2 + 4.3.6 |
| Auth | Supabase SSR (cookie-based) | 0.8.0 |
| Analytics | Mixpanel + Google Analytics + Clarity | -- |
| Error Tracking | Sentry | 10.38.0 |
| Icons | Lucide React (tree-shakeable) | 0.563.0 |
| Animations | Framer Motion | 12.33.0 |
| Charts | Recharts | 3.7.0 |
| DnD | @dnd-kit | 6.3.1 / 10.0.0 |
| Tours | Shepherd.js | 14.5.1 |
| Toasts | Sonner | 2.0.7 |
| Deployment | Railway (standalone output) | -- |

### Project Structure

```
frontend/                           # ~444 source files
  app/                              # Next.js App Router
    api/                            # 59 API proxy routes
    buscar/                         # Main search page (decomposed)
      components/                   # 36 search-specific + 8 sub-components
      hooks/                        # 9 search hooks (orchestration pattern)
      types/                        # searchPhase.ts, search-results.ts
      constants/                    # tour-steps.ts
    dashboard/                      # Analytics dashboard
      components/                   # 7 sub-components (stat cards, charts, etc.)
    pipeline/                       # Kanban board (6 files)
    conta/                          # Account settings (5 sub-routes)
    components/                     # App-level shared (46 files)
      landing/                      # 13 landing page sections
      ui/                           # GradientButton, Tooltip
    admin/                          # Admin pages (cache, emails, metrics, SLO, partners)
    blog/                           # Programmatic SEO (licitacoes, panorama)
    (protected)/                    # Route group with auth guard layout
    hooks/                          # useInView.ts (app-level)
    ...                             # 47 total page routes
  components/                       # Global shared (24 root + subdirectories)
    ui/                             # Button (CVA), Input, Label, Pagination, CurrencyInput
    billing/                        # PaymentFailedBanner, PaymentRecoveryModal, TrialPaywall, TrialUpsellCTA
    subscriptions/                  # PlanCard, PlanToggle, TrustSignals, DowngradeModal, AnnualBenefits, FeatureBadge
    auth/                           # MfaEnforcementBanner, MfaSetupWizard, TotpVerificationScreen
    blog/                           # BlogCTA, RelatedPages, SchemaMarkup
    reports/                        # PdfOptionsModal
    org/                            # InviteMemberModal
    account/                        # CancelSubscriptionModal
    layout/                         # MobileMenu
  hooks/                            # 28 custom React hooks
  contexts/                         # UserContext.tsx (single context)
  lib/                              # 37 utility/library files
    animations/                     # Framer Motion variants, easing, scroll
    constants/                      # sector-names, uf-names, stopwords
    copy/                           # ROI text, comparisons, value props
    schemas/                        # Zod form validation
    utils/                          # correlationId, dateDiffInDays
  __tests__/                        # 304 Jest test files
  e2e-tests/                        # 31 Playwright E2E specs
```

### Build & Runtime Configuration

| Setting | Value | File |
|---------|-------|------|
| Output | Standalone (Railway) | `next.config.js` |
| Build ID | Timestamp + random (force cache invalidation) | `next.config.js` |
| Strict mode | Enabled | `next.config.js` |
| Dark mode | `class` strategy | `tailwind.config.ts` |
| Path aliases | `@/*` -> project root | `tsconfig.json` |
| Sentry | Wrapped, source maps hidden, debug pruned | `next.config.js` |
| Bundle budget | 250 KB gzipped first-load JS | `.size-limit.js` |
| CSP | Enforcing with per-request nonce + strict-dynamic | `middleware.ts` |

### Static Asset Cache Headers

| Path | Cache-Control |
|------|---------------|
| `/_next/static/*` | `public, max-age=2592000, immutable` (30 days) |
| `/images/*` | `public, max-age=604800` (7 days) |
| `/fonts/*` | `public, max-age=31536000, immutable` (1 year) |

---

## 2. Page Inventory (47 Routes)

### Core Application Pages (Protected)

| Route | Purpose | Data Fetching | Key Features |
|-------|---------|---------------|-------------|
| `/buscar` | Main search (270 LOC, decomposed) | Client POST + SSE | Sector/UF filters, SSE progress, pull-to-refresh, keyboard shortcuts, tours, error boundary, cross-tab sync |
| `/dashboard` | User analytics | `useFetchWithBackoff` + `Promise.allSettled` | Stat cards, time-series chart, dimensions widget, profile completeness, CSV export |
| `/pipeline` | Opportunity kanban | SWR | Drag-and-drop (@dnd-kit, lazy-loaded), pipeline alerts, stage management, trial read-only mode |
| `/historico` | Search history | Client fetch | Session-based, restore previous searches, status badges |
| `/mensagens` | Messaging (feature-gated) | Client fetch | Conversations, reply, status management |
| `/alertas` | Alerts (feature-gated) | SWR hooks | Alert preferences, notification bell |
| `/conta` | Account hub (5 sub-routes) | -- | Sidebar layout with ErrorBoundary + Suspense |
| `/conta/perfil` | Profile editing | Client fetch | Profile context for AI recommendations |
| `/conta/seguranca` | Security settings | -- | Password change, MFA TOTP setup |
| `/conta/plano` | Plan management | SWR | Current plan, upgrade/downgrade, alert prefs |
| `/conta/equipe` | Team management | Client fetch | Member invitations (org feature) |
| `/conta/dados` | Data export/deletion | Client fetch | LGPD compliance, data portability |
| `/onboarding` | 3-step wizard | Client POST | CNAE + zod validation, UF selection, first-analysis auto-search |

### Admin Pages (Protected + Role-gated)

| Route | Purpose |
|-------|---------|
| `/admin` | Admin dashboard |
| `/admin/cache` | Cache management |
| `/admin/emails` | Email templates |
| `/admin/metrics` | System metrics |
| `/admin/slo` | SLO monitoring |
| `/admin/partners` | Partner management |

### Public Pages (Marketing & Auth)

| Route | Purpose | Rendering |
|-------|---------|-----------|
| `/` | Landing page (6 sections) | Server component imports, client sections |
| `/login` | Auth (password + magic link + Google) | Client-side + Suspense |
| `/signup` | Registration | Client-side |
| `/auth/callback` | OAuth callback | Server-side Supabase |
| `/recuperar-senha` | Password recovery | Client-side |
| `/redefinir-senha` | Password reset | Client-side |
| `/planos` | Pricing (SmartLic Pro + Consultoria) | SWR (dynamic pricing from Stripe) |
| `/planos/obrigado` | Post-purchase thank you | Query params |
| `/pricing` | Marketing pricing | Static |
| `/features` | Feature showcase | Static |
| `/ajuda` | Help center (FAQ) | Static |
| `/sobre` | About page | Static |
| `/termos` | Terms of service | Static |
| `/privacidade` | Privacy policy | Static |
| `/status` | Public system status | Client fetch |

### SEO/Programmatic Pages (13 routes)

| Route Pattern | Purpose |
|---------------|---------|
| `/blog`, `/blog/[slug]` | Blog index + articles |
| `/blog/licitacoes`, `/blog/licitacoes/[setor]/[uf]` | Sector x state pages |
| `/blog/panorama/[setor]` | Sector panorama |
| `/blog/programmatic/[setor]`, `/blog/programmatic/[setor]/[uf]` | Programmatic SEO |
| `/licitacoes`, `/licitacoes/[setor]` | Sector landings |
| `/como-avaliar-licitacao`, `/como-evitar-prejuizo-licitacao`, `/como-filtrar-editais`, `/como-priorizar-oportunidades` | Content marketing |

---

## 3. Component Library

### UI Primitives (`components/ui/` -- 6 files)

| Component | Purpose | Notes |
|-----------|---------|-------|
| `Button` | Core CVA button | 6 variants (primary, secondary, destructive, ghost, link, outline), 4 sizes, loading state, icon-only requires `aria-label` (TypeScript-enforced) |
| `Input` | Form text input | Standard with styling |
| `Label` | Form label | Accessibility-aware |
| `Pagination` | Page navigation | Numbered pagination |
| `CurrencyInput` | BRL currency input | Formatted R$ input |
| `Button.examples.tsx` | Visual reference | Not a runtime component |

### Search Components (`app/buscar/components/` -- 44 files)

| Category | Components |
|----------|-----------|
| **Form** | `SearchForm` (props interface with 40+ fields), `FilterPanel`, `ModalidadeFilter`, `StatusFilter`, `ValorFilter` |
| **Results** | `SearchResults` (orchestrator), `ResultsHeader`, `ResultsToolbar`, `ResultsFilters`, `ResultCard`, `ResultsList`, `ResultsLoadingSection`, `ResultsFooter`, `ResultsPagination` |
| **Progress** | `EnhancedLoadingProgress`, `UfProgressGrid`, `SourceStatusGrid`, `CoverageBar`, `PartialResultsPrompt`, `PartialTimeoutBanner` |
| **State** | `SearchStateManager`, `SearchEmptyState`, `EmptyResults`, `ZeroResultsSuggestions` |
| **Badges** | `LlmSourceBadge`, `ReliabilityBadge`, `ZeroMatchBadge`, `FreshnessIndicator` |
| **Banners** | `SearchErrorBanner`, `RefreshBanner`, `FilterRelaxedBanner`, `ExpiredCacheBanner`, `DataQualityBanner`, `TruncationWarningBanner`, `OnboardingBanner`, `OnboardingSuccessBanner`, `OnboardingEmptyState` |
| **Error** | `SearchErrorBoundary` (class component, Sentry integration), `ErrorDetail`, `SourcesUnavailable`, `UfFailureDetail` |
| **Export** | `GoogleSheetsExportButton` |
| **Modals** | `BuscarModals` (aggregator for save/keyboard/upgrade/PDF/trial/payment modals) |

### App-Level Components (`app/components/` -- 46 files)

| Category | Components |
|----------|-----------|
| **Auth** | `AuthProvider` (Supabase context), `SessionExpiredBanner`, `CookieConsentBanner` |
| **Navigation** | `AppHeader`, `UserMenu`, `SavedSearchesDropdown`, `Breadcrumbs`, `InstitutionalSidebar` |
| **Theme** | `ThemeProvider` (light/dark/system), `ThemeToggle` |
| **Billing/Trial** | `PlanBadge`, `QuotaBadge`, `QuotaCounter`, `UpgradeModal`, `TrialConversionScreen`, `TrialExpiringBanner`, `TrialCountdown` |
| **Data Display** | `LicitacaoCard`, `LicitacoesPreview`, `StatusBadge`, `ComparisonTable`, `Countdown` |
| **Forms** | `CustomDateInput`, `CustomSelect`, `PaginacaoSelect`, `OrdenacaoSelect`, `RegionSelector`, `EsferaFilter`, `MunicipioFilter`, `OrgaoFilter` |
| **Content** | `ContentPageLayout`, `BlogArticleLayout`, `ValuePropSection`, `MessageBadge` |
| **Analytics** | `AnalyticsProvider`, `GoogleAnalytics`, `ClarityAnalytics`, `StructuredData` |
| **Landing** | 13 section components in `landing/` (HeroSection, OpportunityCost, BeforeAfter, HowItWorks, StatsSection, FinalCTA, etc.) |
| **Footer** | `Footer` |
| **Progress** | `LoadingProgress`, `NProgressProvider` |

### Global Components (`components/` -- 49 files across subdirectories)

| Category | Components |
|----------|-----------|
| **Navigation** | `NavigationShell` (auth-aware sidebar + bottom nav wrapper), `Sidebar` (collapsible, localStorage persistence), `BottomNav` (focus trap, Escape to close), `MobileDrawer` |
| **Loading** | `LoadingProgress`, `AuthLoadingScreen` |
| **Error** | `ErrorBoundary` (class component, Sentry), `ErrorStateWithRetry`, `EmptyState` |
| **Billing** | `PaymentFailedBanner`, `PaymentRecoveryModal`, `TrialPaywall`, `TrialUpsellCTA` |
| **Subscriptions** | `PlanCard`, `PlanToggle`, `TrustSignals`, `DowngradeModal`, `AnnualBenefits`, `FeatureBadge` |
| **Auth** | `MfaEnforcementBanner`, `MfaSetupWizard`, `TotpVerificationScreen` |
| **Profile** | `ProfileCompletionPrompt`, `ProfileCongratulations`, `ProfileProgressBar` |
| **Status** | `BackendStatusIndicator` (polling /api/health every 30s, visibility-gated) |
| **Tour** | `OnboardingTourButton`, `KeyboardShortcutsHelp` |
| **Misc** | `SWRProvider`, `TestimonialSection`, `AlertNotificationBell`, `ActionLabel`, `CompatibilityBadge`, `ViabilityBadge`, `DeepAnalysisModal`, `FeedbackButtons`, `PageHeader` |

### Component Dependency Graph (Key Paths)

```
layout.tsx
  -> AnalyticsProvider -> AuthProvider -> SWRProvider -> UserProvider
     -> ThemeProvider -> NProgressProvider -> BackendStatusProvider
        -> NavigationShell -> Sidebar (desktop) + BottomNav (mobile)
           -> {children}

/buscar/page.tsx
  -> useSearchOrchestration() (master hook)
     -> useSearchFilters() -> useSearch() -> useSearchSSE()
  -> SearchForm (40+ props)
  -> SearchResults -> ResultsHeader, ResultsToolbar, ResultsList
  -> BuscarModals (6 modal aggregator)

/pipeline/page.tsx
  -> usePipeline() (SWR)
  -> PipelineKanban (dynamic import) -> PipelineColumn -> PipelineCard

/dashboard/page.tsx
  -> useFetchWithBackoff()
  -> DashboardStatCards, DashboardTimeSeriesChart (dynamic), DashboardDimensionsWidget (dynamic)
```

---

## 4. Hooks & State Management

### Provider Hierarchy (root layout)

```tsx
<AnalyticsProvider>
  <AuthProvider>          // Supabase session, user, signOut, isAdmin, sessionExpired
    <SWRProvider>         // Global SWR config
      <UserProvider>      // Composes auth + plan + quota + trial into single context
        <ThemeProvider>   // Light/dark/system (localStorage)
          <NProgressProvider>  // Page transition loading bar
            <BackendStatusProvider>  // Online/offline/recovering polling
              {children}
            </BackendStatusProvider>
          </NProgressProvider>
        </ThemeProvider>
      </UserProvider>
    </SWRProvider>
  </AuthProvider>
</AnalyticsProvider>
```

### Custom Hooks (28 in `hooks/` + 9 in `app/buscar/hooks/` + 1 in `app/hooks/`)

#### Global Hooks (`hooks/`)

| Hook | Purpose | Data Pattern |
|------|---------|-------------|
| `usePlan` | Current user plan info | SWR |
| `usePlans` | All available plans (pricing from Stripe) | SWR |
| `useQuota` | Search quota tracking | SWR |
| `useTrialPhase` | Trial lifecycle phase | Derived from usePlan |
| `useAnalytics` | Mixpanel event tracking | Imperative |
| `useFeatureFlags` | Runtime feature toggles | localStorage + env vars |
| `useKeyboardShortcuts` | Global keyboard bindings | Event listeners |
| `useSearchSSE` | SSE event stream handling | EventSource + polling fallback |
| `useSearchPolling` | Fallback polling for search status | Interval-based fetch |
| `useFetchWithBackoff` | Retry with exponential backoff (2s->4s->8s->16s->30s cap) | Generic fetch wrapper |
| `useSavedSearches` | CRUD for saved searches | localStorage + API |
| `useSessions` | Session history | SWR |
| `usePipeline` | Pipeline CRUD | SWR |
| `useAlerts` | Alert management | SWR |
| `useAlertPreferences` | Alert preference CRUD | SWR |
| `useConversations` | Message conversations | SWR |
| `useUnreadCount` | Unread message count | SWR |
| `useIsMobile` | Responsive breakpoint (768px) | matchMedia listener |
| `useNavigationGuard` | Prevent accidental navigation during search | beforeunload |
| `useBroadcastChannel` | Cross-tab search result sync | BroadcastChannel API |
| `useShepherdTour` | Guided tour management | Shepherd.js |
| `useProfileCompleteness` | Profile completion percentage | SWR |
| `useProfileContext` | User profile context | SWR + localStorage cache |
| `useOrganization` | Organization/team membership | SWR |
| `usePublicMetrics` | Public system metrics | SWR |
| `useServiceWorker` | PWA service worker registration | Navigator API |
| `useUserProfile` | User profile data | SWR |

#### Search Hooks (`app/buscar/hooks/`)

| Hook | Purpose |
|------|---------|
| `useSearchOrchestration` | Master hook composing all search state (auth, filters, trial, tours, modals) |
| `useSearch` | Search execution state machine |
| `useSearchExecution` | POST /buscar call + result handling |
| `useSearchFilters` | Filter state (sector, UFs, dates, terms, mode) with SWR sectors |
| `useSearchSSEHandler` | SSE event routing to state |
| `useSearchRetry` | Auto-retry with countdown timer |
| `useSearchExport` | Excel/PDF export logic |
| `useSearchPersistence` | Search state persistence (localStorage) |
| `useUfProgress` | Per-UF progress tracking from SSE events |

### localStorage Keys (observed)

| Key Pattern | Purpose |
|-------------|---------|
| `smartlic-theme` | Theme preference (light/dark/system) |
| `smartlic-has-searched` | First-search tracking |
| `smartlic-first-tip-dismissed` | First-use tooltip |
| `smartlic:buscar:filters-expanded` | Filter accordion state |
| `smartlic-sidebar-collapsed` | Sidebar collapse |
| `smartlic-onboarding-completed` | Onboarding wizard completed |
| `smartlic_tour_*_completed` | Per-tour completion |
| `smartlic_partner` | Partner referral slug |
| `smartlic-plan-cache` | Plan info cache (1hr TTL) |
| `smartlic-profile-context` | Cached profile context |

All reads/writes go through `lib/storage.ts` (`safeSetItem`, `safeGetItem`, `safeRemoveItem`) which wraps try/catch for private browsing mode.

---

## 5. API Integration Layer (59 Proxy Routes)

All API routes in `frontend/app/api/` proxy to the FastAPI backend. Pattern:
- Auth token forwarding from request headers
- Backend URL via `NEXT_PUBLIC_BACKEND_URL`
- Error normalization via `proxy-error-handler.ts`
- Correlation ID injection via `correlationId.ts`
- Shared factory: `create-proxy-route.ts`

### Route Categories

| Category | Routes | Count |
|----------|--------|-------|
| Search | buscar, buscar-progress (SSE), buscar-results/[searchId], search-history, search-status, search-zero-match/[searchId] | 6 |
| Auth | login, signup, check-email, check-phone, google, google/callback, resend-confirmation, status | 8 |
| User | me, me/export, profile-context, profile-completeness, change-password | 5 |
| Billing | plans, billing-portal, subscription-status, trial-status, subscriptions/cancel, subscriptions/cancel-feedback | 6 |
| Analytics | analytics (endpoint param: summary, searches-over-time, top-dimensions, trial-value) | 1 |
| Pipeline | pipeline | 1 |
| Messages | conversations, conversations/[id], [id]/reply, [id]/status, unread-count | 5 |
| Admin | admin/[...path] (catch-all), admin/metrics | 2 |
| Alerts | alerts, alerts/[id], alerts/[id]/preview, alert-preferences | 4 |
| Export | download, export/google-sheets, regenerate-excel/[searchId], reports/diagnostico | 4 |
| Health | health, health/cache | 2 |
| Metrics | metrics/daily-volume, metrics/discard-rate, metrics/sse-fallback | 3 |
| Other | bid-analysis/[bidId], csp-report, feedback, first-analysis, mfa, onboarding, organizations, organizations/[id], sessions, setores, status | 11 |

### SSE Proxy (Critical Path)

The `buscar-progress` route proxies Server-Sent Events from the backend:
- `undici.Agent({ bodyTimeout: 0 })` prevents premature closure
- AbortController linked to `request.signal` for client disconnect cleanup
- Heartbeat forwarding for Railway idle timeout (60s)
- Structured error logging: `{ error_type, search_id, elapsed_ms }`

---

## 6. Authentication & Authorization

### Flow

```
Browser -> Middleware (getUser) -> Protected Route
              |
         Cookie-based sessions (getAll/setAll pattern)
         Session expiry detection (cookie inspection)
         User headers injection (x-user-id, x-user-email)
```

### Middleware (`middleware.ts`)

1. Canonical domain redirect (*.railway.app -> smartlic.tech, 301)
2. CSP nonce generation (per-request, `crypto.randomUUID` -> base64)
3. Security headers injection (see below)
4. API passthrough (`/api/*` skip auth)
5. Public route allowlist (`/login`, `/signup`, `/planos`, `/auth/callback`)
6. Protected route auth check (server-side `getUser()`, not just `getSession()`)

### Security Headers

| Header | Value |
|--------|-------|
| Content-Security-Policy | Enforcing with nonce + strict-dynamic |
| X-Content-Type-Options | nosniff |
| X-Frame-Options | DENY |
| X-XSS-Protection | 1; mode=block |
| Referrer-Policy | strict-origin-when-cross-origin |
| Permissions-Policy | camera=(), microphone=(), geolocation=() |
| Strict-Transport-Security | max-age=31536000; includeSubDomains; preload |
| Cross-Origin-Opener-Policy | same-origin |
| X-DNS-Prefetch-Control | off |

### MFA Support

- `MfaEnforcementBanner` -- prompts admin/master users
- `MfaSetupWizard` -- TOTP enrollment flow
- `TotpVerificationScreen` -- code entry during login (lazy-loaded)

---

## 7. Design System

### Typography

| Font | CSS Variable | Usage | Preload |
|------|-------------|-------|---------|
| DM Sans | `--font-body` | Body text (primary) | Yes |
| Fahkwang | `--font-display` | Headings, display | No (non-critical) |
| DM Mono | `--font-data` | Data/code displays | No (non-critical) |

Fluid typography scale:
- Hero: `clamp(2.5rem, 5vw + 1rem, 4.5rem)` (40-72px)
- H1: `clamp(2rem, 4vw + 1rem, 3.5rem)` (32-56px)
- H2: `clamp(1.5rem, 3vw + 0.5rem, 2.5rem)` (24-40px)
- H3: `clamp(1.25rem, 2vw + 0.5rem, 1.75rem)` (20-28px)
- Body LG: `clamp(1.125rem, 1vw + 0.5rem, 1.25rem)` (18-20px)

### Color System (CSS Variables + Tailwind Mapping)

**Light Mode:**

| Token | Hex | WCAG vs Canvas |
|-------|-----|----------------|
| `ink` (primary text) | `#1e2d3b` | 12.6:1 AAA |
| `ink-secondary` | `#3d5975` | 5.5:1 AA |
| `ink-muted` | `#6b7a8a` | 5.1:1 AA |
| `brand-navy` | `#0a1e3f` | 14.8:1 AAA |
| `brand-blue` | `#116dff` | 4.8:1 AA |
| `brand-blue-hover` | `#0d5ad4` | 6.2:1 AA+ |
| `success` | `#16a34a` | 4.7:1 AA |
| `error` | `#dc2626` | 5.9:1 AA |
| `warning` | `#ca8a04` | 5.2:1 AA |

**Dark Mode:** Full override set in `.dark` class with independently verified WCAG ratios (e.g., `--ink: #e8eaed` at 11.8:1, `--ink-muted: #8494a7` at 6.2:1).

**Special Palettes:**
- Gem palette: sapphire, emerald, amethyst, ruby (translucent, with dark mode variants)
- Chart palette: 10 colors (`--chart-1` through `--chart-10`)
- Brand: WhatsApp green

### Semantic Aliases

| Tailwind Token | Maps To |
|----------------|---------|
| `primary` | `--brand-blue` |
| `secondary` | `--brand-navy` |
| `accent` | `--brand-blue-hover` |
| `success` / `error` / `warning` | Semantic colors |

### Spacing & Border Radius

- Spacing: 4px base grid (standard Tailwind units)
- `rounded-input` = 4px, `rounded-button` = 6px, `rounded-card` = 8px, `rounded-modal` = 12px

### Shadows (11 levels)

- Standard: `sm`, `md`, `lg`, `xl`, `2xl`
- Brand glow: `glow`, `glow-lg`
- Glass: `glass`
- Gem: `gem-sapphire`, `gem-emerald`, `gem-amethyst`, `gem-ruby`

### Animations (8 Custom Keyframes)

| Animation | Duration | Use Case |
|-----------|----------|----------|
| `fade-in-up` | 0.4s ease-out | Page transitions |
| `gradient` | 8s linear infinite | Background gradients |
| `shimmer` | 2s linear infinite | Loading skeletons |
| `float` | 3s ease-in-out infinite | Decorative floating |
| `slide-up` | 0.6s cubic-bezier | Section entrance |
| `scale-in` | 0.4s cubic-bezier | Modal entrance |
| `slide-in-right` | 0.3s ease-out | Drawer/panel |
| `bounce-gentle` | 2s ease-in-out infinite | Attention indicators |

All animations respect `prefers-reduced-motion: reduce` via global media query in `globals.css`.

### Premium Effects

- Glassmorphism: `--glass-bg`, `--glass-border`, `--glass-shadow`
- Gradients: `--gradient-brand`, `--gradient-hero-bg`, `--gradient-card`, `--gradient-text`
- Hover utilities: `.hover-lift` (translateY -8px), `.hover-glow`, `.hover-scale`
- Text gradient: `.text-gradient` (background-clip)
- Stagger delays: `.stagger-1` through `.stagger-5` (50ms increments)

---

## 8. Accessibility Audit

### Strengths (12 items)

1. **Skip navigation** -- WCAG 2.4.1 "Pular para conteudo principal" in root layout
2. **WCAG color contrast** -- All text tokens documented with contrast ratios; all pass AA minimum
3. **Dark mode** -- Full dark mode with independently verified WCAG contrast (SAB-003 fixes)
4. **Button aria-label** -- TypeScript enforces `aria-label` for `size="icon"` at compile time
5. **Focus ring** -- `:focus-visible` with 3px outline + 2px offset (WCAG 2.2 AAA, 2.4.13)
6. **Touch targets** -- `min-height: 44px` enforced globally on `<button>` and `<input>`
7. **Semantic HTML** -- `<main id="main-content">`, `<header>`, `<footer>`, `<nav aria-label="...">`
8. **`aria-live` regions** -- Present on 29 components (progress, banners, counters, error states)
9. **Error boundaries** -- `role="alert"` + `aria-live="assertive"` on crash recovery UI
10. **Reduced motion** -- `@media (prefers-reduced-motion: reduce)` zeroes all animation durations
11. **Focus trap** -- BottomNav drawer implements manual focus trap + Escape to close
12. **Playwright a11y** -- `@axe-core/playwright` in devDependencies, dedicated test files

### Remaining Gaps (7 items)

| ID | Issue | Severity | Location |
|----|-------|----------|----------|
| A11Y-001 | Inline SVG icons: some in `planos/page.tsx` and `conta/layout.tsx` lack `aria-hidden="true"` | Medium | Various |
| A11Y-002 | Color-only indicators: viability badges and source status partially rely on color alone | Medium | Badges |
| A11Y-003 | Landmark duplication: buscar page has its own `<footer aria-label>` + NavigationShell footer (intentional per DEBT-111, but may confuse landmark navigation) | Low | `/buscar` |
| A11Y-004 | `focus-trap-react` is installed but not uniformly used across all modal implementations (some use manual focus trap, some use the library) | Low | Modals |
| A11Y-005 | Loading spinners in some pages use visual-only indicators without `role="status"` on the spinner container | Low | Login, auth callback |
| A11Y-006 | `useIsMobile` hook initializes `isMobile` to `false` -- brief flash of desktop layout on mobile before hydration | Low | Global |
| A11Y-007 | No explicit `aria-sort` on sortable table columns in admin pages | Low | Admin |

### WCAG 2.1 Compliance Summary

| Level | Status |
|-------|--------|
| A (Perceivable) | Pass -- text alternatives, time-based media N/A, adaptable, distinguishable |
| A (Operable) | Pass -- keyboard accessible, skip nav, no seizures, touch targets |
| A (Understandable) | Pass -- readable (lang="pt-BR"), predictable, input assistance |
| AA (Perceivable) | Pass -- contrast ratios documented and verified |
| AA (Operable) | Pass -- focus visible (3px, AAA-level), no keyboard traps |
| AAA (partial) | Focus appearance meets 2.4.13 |

---

## 9. Performance Audit

### Bundle Optimization Status

| Feature | Status | Details |
|---------|--------|---------|
| Standalone output | Enabled | Minimizes deployment size |
| Source map hiding | Enabled | `hideSourceMaps: true` |
| Debug statement pruning | Enabled | Sentry `excludeDebugStatements` |
| Font optimization | Good | DM Sans preloaded; Fahkwang + DM Mono deferred |
| Code splitting (pages) | Automatic | App Router page-level |
| Bundle budget | 250 KB gzipped | `.size-limit.js`, CI-enforced |
| CSP nonce | Enabled | Removes `'unsafe-inline'` / `'unsafe-eval'` |

### Dynamic Imports (Code Splitting)

| Component | Page | Why |
|-----------|------|-----|
| `PipelineKanban` / `ReadOnlyKanban` | `/pipeline` | @dnd-kit is heavy (~30KB), SSR disabled |
| `SearchStateManager` | `/buscar` | Progressive loading of state UI |
| `DashboardTimeSeriesChart` | `/dashboard` | Recharts (~50KB) |
| `DashboardDimensionsWidget` | `/dashboard` | Recharts charts |
| `DashboardProfileSection` | `/dashboard` | Profile completion UI |
| `TotpVerificationScreen` | `/login` | MFA verification (rare path) |
| Blog MDX renderer | `/blog/[slug]` | Content rendering |

### Key Dependencies (Bundle Impact)

| Dependency | Approximate Size | Notes |
|------------|-----------------|-------|
| `react` + `react-dom` | ~130KB | Framework |
| `framer-motion` | ~70KB | Used primarily on landing page |
| `recharts` | ~50KB | Dashboard only (dynamically imported) |
| `@supabase/supabase-js` | ~40KB | Auth + API |
| `@dnd-kit/*` | ~30KB | Pipeline only (dynamically imported) |
| `shepherd.js` | ~25KB | Tours |
| `@sentry/nextjs` | ~20KB | Error tracking (tree-shaken) |
| `zod` | ~15KB | Form validation |
| `swr` | ~10KB | Data fetching |
| `sonner` | ~8KB | Toasts |
| `date-fns` | Tree-shakeable | Date formatting |
| `lucide-react` | Tree-shakeable | Icons (named imports) |

### Performance Concerns

| ID | Concern | Severity | Notes |
|----|---------|----------|-------|
| PERF-001 | Framer Motion loaded globally via animation imports (landing sections are not dynamic imports) | Medium | Could save ~70KB for non-landing pages |
| PERF-002 | Shepherd.js loaded on every search page visit regardless of tour state | Low | Could conditionally import |
| PERF-003 | `react-simple-pull-to-refresh` loaded on search page (mobile-only feature, not conditionally imported) | Low | Small package |
| PERF-004 | Feature-gated code (alertas, mensagens, organizations) still in production bundles | Low | Feature-gated at runtime, not build-time |
| PERF-005 | `useIsMobile` causes hydration mismatch (server: false, client: depends on viewport) | Low | Brief flash on mobile |

---

## 10. UX Patterns

### Loading States

| Pattern | Usage | Implementation |
|---------|-------|---------------|
| Full-page spinner | Auth loading, page transitions | `AuthLoadingScreen`, inline spinner divs |
| Skeleton loading | Pipeline, dashboard, account | `animate-pulse` divs matching content shape |
| Progress bar | Page transitions | NProgress (top-of-page bar, brand-blue) |
| SSE progress | Search execution | `EnhancedLoadingProgress` with per-UF grid, percentage, stage labels |
| Pull-to-refresh | Mobile search refresh | `react-simple-pull-to-refresh` (mobile only via CSS) |

### Error States

| Pattern | Component | Features |
|---------|-----------|----------|
| Error boundary (page-level) | `ErrorBoundary` | Sentry reporting, retry button, support link, error details expandable |
| Error boundary (search) | `SearchErrorBoundary` | Search-specific recovery |
| Error boundary (route-level) | `error.tsx` files (9 pages) | Next.js error handling |
| Fetch error with retry | `ErrorStateWithRetry` | Retry button, error message |
| Backend offline | `BackendStatusIndicator` | Red/green dot, polling |
| Structured search error | `ErrorDetail` | 7-field error display (code, correlation_id, search_id, etc.) |

### Empty States

| Context | Component | Features |
|---------|-----------|----------|
| No search results | `EmptyResults`, `ZeroResultsSuggestions` | Suggestions to broaden search |
| First visit (no search) | `SearchEmptyState` | Welcome message, sector suggestions |
| Empty pipeline | `EmptyState` | Generic with icon, message, CTA |
| No history | `EmptyState` | Generic pattern |

### Form Patterns

| Pattern | Implementation |
|---------|---------------|
| Login/Signup | Inline form with error messages, password toggle, magic link option |
| Onboarding | 3-step wizard with progress bar, zod validation, react-hook-form |
| Search filters | Accordion-style collapsible filter panel |
| Region selector | Map-like UF multi-select with region toggles |
| Date input | Custom date input with react-day-picker calendar modal |
| Save dialog | Modal with text input for search name |

### Navigation Patterns

| Context | Desktop | Mobile |
|---------|---------|--------|
| App navigation | Collapsible sidebar (localStorage state) | Bottom nav (4 items + "Mais" drawer) |
| Account settings | Vertical sidebar nav | Horizontal scroll tabs |
| Page transitions | NProgress loading bar | Same |
| Auth guard | Redirect to `/login` | Same |
| First-time user | Redirect to `/onboarding` | Same |

### Feedback Mechanisms

| Pattern | Component/Tool |
|---------|---------------|
| Toast notifications | Sonner (`bottom-center`, richColors, closeButton) |
| Auto-retry with countdown | `useSearchRetry` (circular SVG countdown, 10s/20s/30s) |
| Backend status | `BackendStatusIndicator` (polling, red/green) |
| Trial countdown | `TrialCountdown` (color-coded badge) |
| Profile completion | `ProfileProgressBar` (percentage bar) |
| Onboarding tour | Shepherd.js (3 tours: welcome, search, results, pipeline) |
| Keyboard shortcuts | `?` key opens help modal |

---

## 11. Testing Coverage

### Jest Unit Tests

| Metric | Value |
|--------|-------|
| Test files | 304 |
| Passing tests | 5,583+ |
| Failures | 3 (pre-existing) |
| Coverage thresholds | Branches: 50%, Functions: 55%, Lines: 55%, Statements: 55% |
| Target | 60%+ (DEBT-111) |
| Environment | jsdom with polyfills (crypto.randomUUID + EventSource) |
| Transform | @swc/jest |

### Playwright E2E Tests

| Metric | Value |
|--------|-------|
| Spec files | 31 |
| Total tests | ~60 |
| A11y tool | @axe-core/playwright |
| Coverage | Search flow, auth, errors, accessibility, performance, theme, landing, admin |

### Error Handling Coverage

| Pattern | error.tsx | loading.tsx | ErrorBoundary |
|---------|-----------|-------------|---------------|
| `/buscar` | Yes | Yes | Yes (SearchErrorBoundary) |
| `/dashboard` | Yes | Yes | No |
| `/pipeline` | Yes | Yes | No |
| `/historico` | Yes | Yes | No |
| `/conta` | Yes | -- | Yes (ErrorBoundary wrapper) |
| `/admin` | Yes | -- | No |
| `/alertas` | Yes | -- | No |
| `/mensagens` | Yes | -- | No |
| Root | Yes (`error.tsx` + `global-error.tsx`) | -- | -- |

---

## 12. Technical Debt Catalog

### Resolved Since Last Audit (2026-03-09)

| ID | Issue | Resolution |
|----|-------|------------|
| FE-TD-001 | `/buscar/page.tsx` ~983 lines monolithic | **RESOLVED** -- DEBT-106 decomposed to 270 LOC + `useSearchOrchestration` hook + `BuscarModals` aggregator |
| FE-TD-002 | No `next/dynamic` for heavy deps | **RESOLVED** -- DEBT-105/106 added dynamic imports for Recharts, @dnd-kit, SearchStateManager, TotpVerificationScreen |
| FE-TD-005 | No `prefers-reduced-motion` | **RESOLVED** -- DEBT-105 added global media query in `globals.css` |
| FE-TD-007 | `aria-live` missing | **RESOLVED** -- DEBT-105 added `aria-live` to 29 components |
| FE-TD-010 | `unsafe-inline`/`unsafe-eval` in CSP | **RESOLVED** -- DEBT-108 implemented CSP nonce + strict-dynamic |
| FE-TD-012 | eslint-disable exhaustive-deps in buscar | **RESOLVED** -- 0 occurrences in `app/buscar/`, 3 remaining in other files |
| FE-TD-015 | No bundle size monitoring | **RESOLVED** -- DEBT-108 added `.size-limit.js` (250KB budget, CI-enforced) |

### Remaining Debt

#### Severity: High

| ID | Issue | Location | Effort |
|----|-------|----------|--------|
| FE-TD-004 | Coverage thresholds at 50-55% (target 60%, ideal 80%) | `jest.config.js` | Ongoing |
| FE-TD-006 | Dual component directories (`app/components/` 46 files + `components/` 49 files) with unclear ownership | Project-wide | Medium (1-2 days) |
| FE-TD-008 | ~96 raw hex color occurrences in TSX files (should use Tailwind tokens or CSS vars) | 19 files across app/ | Medium (1 day) |
| FE-TD-009 | Inline SVGs in `conta/layout.tsx` instead of Lucide icons or centralized system | `app/conta/layout.tsx` | Small (0.5 day) |
| FE-TD-023 | Framer Motion not dynamically imported -- loaded globally even for non-landing pages | Landing page sections, `lib/animations/` | Medium (1 day) |

#### Severity: Medium

| ID | Issue | Location | Effort |
|----|-------|----------|--------|
| FE-TD-011 | Limited page-level tests (dashboard, pipeline, historico, onboarding, conta) | `__tests__/` | Medium (2-3 days) |
| FE-TD-013 | Hardcoded pricing fallback must stay in sync with Stripe | `app/planos/page.tsx` | Ongoing |
| FE-TD-014 | Feature-gated code (alertas, mensagens, organizations) shipped in production bundles | Multiple files | Medium (1 day) |
| FE-TD-016 | Dual footer: buscar page intentional `<footer aria-label="Links uteis da busca">` + NavigationShell minimal footer | `app/buscar/page.tsx` | Documented intentional (DEBT-111 AC9) |
| FE-TD-017 | Theme init script via `dangerouslySetInnerHTML` in layout (works, uses nonce) | `app/layout.tsx` | Low priority |
| FE-TD-018 | Mixed raw `var(--*)` + Tailwind token usage in many components | Project-wide | Ongoing |
| FE-TD-024 | 3 remaining `eslint-disable` in `MunicipioFilter`, `OrgaoFilter`, `EnhancedLoadingProgress` | 3 files | Small |

#### Severity: Low

| ID | Issue | Location | Effort |
|----|-------|----------|--------|
| FE-TD-019 | `@types/uuid` in dependencies (should be devDependencies) | `package.json` | Trivial |
| FE-TD-021 | No Storybook or component documentation | Project-wide | Large (3-5 days) |
| FE-TD-022 | `Button.examples.tsx` exists but no visual regression testing | `components/ui/` | Medium |
| FE-TD-025 | `useIsMobile` SSR mismatch (initializes to false) | `hooks/useIsMobile.ts` | Small |

---

## 13. Recommended Priority Actions

### Phase 1: Quick Wins (1-2 days)

1. Replace inline SVGs in `conta/layout.tsx` with Lucide icons (FE-TD-009)
2. Move `@types/uuid` to devDependencies (FE-TD-019)
3. Fix 3 remaining eslint-disable suppressions (FE-TD-024)
4. Add `aria-hidden="true"` to decorative SVGs in planos page (A11Y-001)

### Phase 2: Performance (2-3 days)

1. Dynamic import Framer Motion for landing page only (FE-TD-023) -- save ~70KB for authenticated pages
2. Conditionally import Shepherd.js only when tour is not completed
3. Audit and replace raw hex colors with Tailwind tokens (FE-TD-008)

### Phase 3: Testing (5-7 days)

1. Add page-level tests for dashboard, pipeline, historico, onboarding, conta (FE-TD-011)
2. Raise coverage thresholds to 60% (FE-TD-004)
3. Add dark-mode rendering tests for key components
4. Test Zod validation schemas in `lib/schemas/forms.ts`

### Phase 4: Architecture (7-14 days)

1. Consolidate component directories with clear ownership rules (FE-TD-006):
   - `components/` = truly global (3+ pages)
   - `app/components/` = app-specific shared (2+ authenticated pages)
   - Page-local = page-specific only
2. Add Storybook for component documentation (FE-TD-021)
3. Implement build-time feature flag elimination for gated features (FE-TD-014)

---

## 14. Questions for @architect

1. **Component directory consolidation** -- Should we enforce a strict ownership rule (components used on 3+ pages go to `components/`, 2 pages to `app/components/`, 1 page stays local)? Or is the current organic structure acceptable?

2. **Framer Motion scope** -- The animation library is imported globally. Should we restrict it to the landing page via dynamic imports, or does the animation system (page transitions, entrance effects) justify global inclusion?

3. **Feature-gated code** -- Alertas and Mensagens are feature-gated at runtime but still in the bundle. Should we move them behind `next/dynamic` with an enable check, or accept the bundle cost for faster re-enablement?

4. **SWR vs server components** -- Several pages (dashboard, pipeline, historico) are fully client-side. With Next.js 16 RSC maturity, should any data fetching move to server components?

5. **Dual footer pattern** -- The buscar page intentionally has its own rich footer (links, keyboard shortcuts) alongside NavigationShell's minimal footer. Is this the right long-term pattern, or should all pages share a single footer?

6. **Organization feature scope** -- The team/org feature (`useOrganization`, `InviteMemberModal`, `/conta/equipe`) appears partially implemented. Is this shipping soon, or should it be fully feature-gated?

---

## Appendix: Key File Reference

| File | Purpose |
|------|---------|
| `frontend/package.json` | Dependencies, scripts, engines |
| `frontend/next.config.js` | Next.js + Sentry + standalone output |
| `frontend/tailwind.config.ts` | Design system tokens, custom colors/shadows/animations |
| `frontend/app/globals.css` | CSS variables (light + dark), keyframes, Shepherd/NProgress styles |
| `frontend/tsconfig.json` | TypeScript strict config, path aliases |
| `frontend/middleware.ts` | Auth guard, CSP nonce, security headers |
| `frontend/.size-limit.js` | Bundle budget (250KB gzipped) |
| `frontend/jest.config.js` | Test config, module name mapper |
| `frontend/app/layout.tsx` | Root layout, provider hierarchy, fonts |
| `frontend/app/buscar/page.tsx` | Main search page (270 LOC, decomposed) |
| `frontend/app/buscar/hooks/useSearchOrchestration.ts` | Master search orchestration hook |
| `frontend/hooks/useSearchSSE.ts` | SSE stream handling with reconnection |
| `frontend/hooks/useFetchWithBackoff.ts` | Exponential backoff fetch hook |
| `frontend/lib/create-proxy-route.ts` | API proxy factory |
| `frontend/lib/storage.ts` | Safe localStorage wrapper |
| `frontend/components/ui/button.tsx` | Core Button (CVA, 6 variants) |
| `frontend/components/NavigationShell.tsx` | Auth-aware layout shell |
| `frontend/components/Sidebar.tsx` | Desktop sidebar navigation |
| `frontend/components/BottomNav.tsx` | Mobile bottom navigation |
| `frontend/contexts/UserContext.tsx` | Unified user context |
