# Frontend Specification & Audit -- SmartLic v0.5

> Generated: 2026-03-07 | Phase 3 Brownfield Discovery by @ux-design-expert (Uma)
> Codebase snapshot: branch `main`, commit `a1349fc2`

---

## Table of Contents

1. [Overview](#1-overview)
2. [Page Inventory](#2-page-inventory)
3. [Component Catalog](#3-component-catalog)
4. [State Management](#4-state-management)
5. [API Integration](#5-api-integration)
6. [Authentication Flow](#6-authentication-flow)
7. [Styling Architecture](#7-styling-architecture)
8. [Animation / Interaction](#8-animation--interaction)
9. [Accessibility Audit](#9-accessibility-audit)
10. [Performance Analysis](#10-performance-analysis)
11. [Error Handling](#11-error-handling)
12. [Testing Coverage](#12-testing-coverage)
13. [Technical Debt Inventory](#13-technical-debt-inventory)

---

## 1. Overview

### Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Framework | Next.js | 16.1.6 |
| UI Library | React | 18.3.1 |
| Language | TypeScript | 5.9.3 |
| Styling | Tailwind CSS | 3.4.19 |
| Animation | Framer Motion | 12.33.0 |
| Charts | Recharts | 3.7.0 |
| Auth | Supabase SSR | 0.8.0 |
| Data Fetching | SWR | 2.4.1 |
| Drag-and-Drop | @dnd-kit | 6.3.1 / 10.0.0 |
| Onboarding Tours | Shepherd.js | 14.5.1 |
| Analytics | Mixpanel | 2.74.0 |
| Error Tracking | Sentry | 10.38.0 |
| Toasts | Sonner | 2.0.7 |
| Icons | Lucide React | 0.563.0 |
| Date Picker | react-day-picker | 9.13.0 |
| UI Primitives | Radix UI (react-slot) | 1.2.4 |

### Build & Deploy

- **Output:** `standalone` (Node.js server, not static export)
- **Hosting:** Railway (port 8080)
- **Build:** `next build --webpack` + `next-sitemap` + standalone copy
- **CI:** GitHub Actions (`frontend-tests.yml`, `e2e.yml`)

### Quantitative Summary

| Metric | Count |
|--------|-------|
| Pages (page.tsx) | 44 |
| Layouts (layout.tsx) | 6 |
| API proxy routes | 58 |
| Shared components (`components/`) | 43 |
| App components (`app/components/`) | 62 |
| Search-specific components (`app/buscar/components/`) | 39 |
| Custom hooks (`hooks/` + `app/buscar/hooks/`) | 29 |
| Lib utilities | 35 |
| Unit/Integration tests | 292 files |
| E2E tests (Playwright) | 21 spec files |

---

## 2. Page Inventory

### Public Pages (no auth required)

| Route | Purpose | Rendering | Lines |
|-------|---------|-----------|-------|
| `/` | Landing page (redirects to content page) | Server | 33 |
| `/login` | Email/password + Google OAuth + magic link | Client | 501 |
| `/signup` | Registration with CNAE, sector, phone fields | Client | ~500 |
| `/recuperar-senha` | Password recovery request | Client | -- |
| `/redefinir-senha` | Password reset form | Client | -- |
| `/auth/callback` | OAuth / magic link callback handler | Client | -- |
| `/planos` | Pricing page (SmartLic Pro plans) | Client | 672 |
| `/planos/obrigado` | Post-purchase thank you | Client | -- |
| `/pricing` | Marketing pricing page | Server | -- |
| `/features` | Feature showcase page | Server | -- |
| `/sobre` | About / institutional page | Server | -- |
| `/ajuda` | Help center with FAQ sections | Client | -- |
| `/termos` | Terms of service | Server | -- |
| `/privacidade` | Privacy policy | Server | -- |
| `/status` | System status / health dashboard | Client | -- |
| `/licitacoes` | Programmatic SEO hub for sectors | Server | -- |
| `/licitacoes/[setor]` | Per-sector programmatic page | Server | -- |
| `/blog` | Blog listing page | Server | -- |
| `/blog/[slug]` | Individual blog article (dynamic import) | Server | -- |
| `/blog/licitacoes` | Blog sub-hub for bids | Server | -- |
| `/blog/licitacoes/[setor]/[uf]` | Programmatic blog pages | Server | -- |
| `/blog/panorama/[setor]` | Sector panorama pages | Server | -- |
| `/blog/programmatic/[setor]` | Programmatic SEO pages | Server | -- |
| `/blog/programmatic/[setor]/[uf]` | Per-UF programmatic pages | Server | -- |
| `/como-avaliar-licitacao` | SEO content page | Server | -- |
| `/como-evitar-prejuizo-licitacao` | SEO content page | Server | -- |
| `/como-filtrar-editais` | SEO content page | Server | -- |
| `/como-priorizar-oportunidades` | SEO content page | Server | -- |

### Protected Pages (auth required via middleware)

| Route | Purpose | Lines | Key Components |
|-------|---------|-------|----------------|
| `/buscar` | **Main search page** -- filters, SSE progress, results | 1,057 | SearchForm, SearchResults, UfProgressGrid, FilterPanel, many banners |
| `/dashboard` | Analytics dashboard with charts | 1,037 | Recharts, sector/UF breakdowns, skeletons |
| `/historico` | Search history with re-run capability | 423 | History list, date grouping |
| `/pipeline` | Kanban board for opportunity tracking | 481 | @dnd-kit, drag-and-drop columns |
| `/mensagens` | In-app messaging / support chat | 568 | Conversation list, message thread |
| `/conta` | Account settings (profile, plan, data export) | 1,420 | Many form sections, plan management |
| `/conta/equipe` | Team management page | -- | InviteMemberModal |
| `/conta/seguranca` | Security settings (MFA, password) | -- | MfaSetupWizard, TotpVerificationScreen |
| `/alertas` | Bid alert configuration | 1,068 | Alert rules, preferences |
| `/onboarding` | 3-step wizard (CNAE -> UFs -> Confirmation) | 689 | Step flow, auto-search trigger |
| `/admin` | Admin dashboard (users, metrics, searches) | 764 | Data tables, admin-only |
| `/admin/cache` | Cache management dashboard | -- | Cache stats, eviction controls |
| `/admin/emails` | Email template management | -- | Template editor |
| `/admin/metrics` | Prometheus metrics dashboard | -- | Metric charts |
| `/admin/slo` | SLO monitoring dashboard | -- | SLO targets, error budgets |
| `/admin/partners` | Partner management | -- | Partner list, invite |

### Route Group Layout

- `(protected)/layout.tsx` -- Auth guard, AppHeader, Breadcrumbs, max-width container
  - Redirects unauthenticated users to `/`
  - Redirects first-time users to `/onboarding` (checks profile context)
  - Shows loading spinner during auth check

---

## 3. Component Catalog

### Shared Components (`components/`)

| Component | Purpose | Used In |
|-----------|---------|---------|
| `NavigationShell` | Responsive nav wrapper (Sidebar + BottomNav) | Root layout |
| `Sidebar` | Desktop sidebar navigation | NavigationShell |
| `BottomNav` | Mobile bottom navigation bar | NavigationShell |
| `MobileDrawer` | Mobile slide-out drawer | NavigationShell |
| `BackendStatusIndicator` | Health polling indicator (green/red dot) | Root layout (provider) |
| `SWRProvider` | Global SWR configuration | Root layout |
| `EmptyState` | Generic empty state display | Multiple pages |
| `ErrorStateWithRetry` | Error display with retry button | Multiple pages |
| `PageHeader` | Standardized page header with title + actions | Multiple pages |
| `LoadingProgress` | Simple progress bar | Search flow |
| `EnhancedLoadingProgress` | Animated multi-step progress | Search flow |
| `AuthLoadingScreen` | Full-screen auth loading spinner | Auth flow |
| `ProfileProgressBar` | Profile completion progress | Dashboard |
| `ProfileCompletionPrompt` | Prompt to complete profile | Dashboard |
| `ProfileCongratulations` | Profile completion celebration (Framer Motion) | Dashboard |
| `AlertNotificationBell` | Alert notification icon with badge | AppHeader |
| `OnboardingTourButton` | Shepherd.js tour trigger | AppHeader |
| `GoogleSheetsExportButton` | Google Sheets export action | Search results |
| `ValorFilter` | Value range filter component | Search form |
| `StatusFilter` | Bid status filter | Search form |
| `ModalidadeFilter` | Procurement modality filter | Search form |
| `TestimonialSection` | Customer testimonials | Landing page |

### Subscription/Billing Components (`components/subscriptions/`, `components/billing/`)

| Component | Purpose |
|-----------|---------|
| `PlanCard` | Plan display card with pricing |
| `PlanToggle` | Monthly/semiannual/annual toggle |
| `FeatureBadge` | Plan feature indicator |
| `AnnualBenefits` | Annual plan savings display |
| `DowngradeModal` | Plan downgrade confirmation |
| `TrustSignals` | Trust badges (security, support) |
| `PaymentFailedBanner` | Global payment failure notification |
| `PaymentRecoveryModal` | Payment recovery flow |
| `CancelSubscriptionModal` | Cancellation with feedback |
| `TrialPaywall` | Trial limit paywall gate |
| `TrialUpsellCTA` | Trial-to-paid conversion CTA |

### Search Components (`app/buscar/components/`)

| Component | Purpose |
|-----------|---------|
| `SearchForm` | Main search form (sector, UFs, dates, terms) |
| `SearchResults` | Results container with pagination |
| `FilterPanel` | Post-search filter sidebar |
| `SearchErrorBoundary` | Class-based error boundary for search area |
| `SearchErrorBanner` | Error message banner with retry |
| `SearchStateManager` | Visual state manager (Framer Motion) |
| `UfProgressGrid` | Per-UF progress visualization during search |
| `ResultCard` | Individual bid result card |
| `ResultsHeader` | Results count + sort controls |
| `ResultsToolbar` | Actions toolbar (export, filter toggle) |
| `ResultsFilters` | Active filter chips |
| `ResultsPagination` | Page navigation |
| `ResultsList` | Scrollable results list |
| `ResultsLoadingSection` | Skeleton loading state for results |
| `ResultsFooter` | Results summary footer |
| `ViabilityBadge` | Viability score badge (alta/media/baixa) |
| `ReliabilityBadge` | Data reliability indicator |
| `CompatibilityBadge` | AI compatibility score |
| `LlmSourceBadge` | How relevance was determined (keyword/LLM) |
| `ZeroMatchBadge` | Zero-match classification indicator |
| `FeedbackButtons` | Thumbs up/down feedback on results |
| `FreshnessIndicator` | Cache freshness display |
| `CoverageBar` | Data coverage percentage bar |
| `ErrorDetail` | Structured error display (7 fields) |
| `EmptyResults` | Zero results with suggestions |
| `DataQualityBanner` | Data quality warning banner |
| `PartialResultsPrompt` | Partial results notification |
| `PartialTimeoutBanner` | Timeout with partial data |
| `TruncationWarningBanner` | Results truncation warning |
| `FilterRelaxedBanner` | Filter relaxation notification |
| `FilterStatsBreakdown` | Filter rejection reasons |
| `SourceStatusGrid` | Per-source status display |
| `SourcesUnavailable` | All sources down notification |
| `RefreshBanner` | Cache-first with live fetch running |
| `ExpiredCacheBanner` | Stale cache warning |
| `UfFailureDetail` | Failed UF details |
| `ZeroResultsSuggestions` | Suggestions when no results |
| `ActionLabel` | Recommended action label |
| `DeepAnalysisModal` | On-demand deep AI analysis |

### App-Level Components (`app/components/`)

| Component | Purpose |
|-----------|---------|
| `AuthProvider` | React context for Supabase auth state |
| `ThemeProvider` | Dark/light mode context |
| `AnalyticsProvider` | Mixpanel analytics context |
| `NProgressProvider` | Route transition progress bar |
| `AppHeader` | Authenticated page header |
| `Breadcrumbs` | Breadcrumb navigation |
| `UserMenu` | User dropdown menu |
| `MessageBadge` | Unread messages indicator |
| `QuotaBadge` | Search quota display |
| `QuotaCounter` | Detailed quota counter |
| `PlanBadge` | Current plan indicator |
| `Footer` | Site footer |
| `SessionExpiredBanner` | Session expiration notification |
| `CookieConsentBanner` | LGPD cookie consent |
| `TrialConversionScreen` | Full-screen trial expiry conversion |
| `TrialExpiringBanner` | Trial expiring warning (day 6+) |
| `TrialCountdown` | Color-coded trial countdown badge |
| `UpgradeModal` | Plan upgrade prompt |
| `Countdown` | Generic countdown timer |
| `Dialog` | Modal dialog wrapper |
| `ComparisonTable` | Feature comparison table |
| `SavedSearchesDropdown` | Saved searches quick access |
| `AddToPipelineButton` | Add bid to pipeline action |
| `StatusBadge` | Bid status indicator |
| `LicitacaoCard` | Bid card for preview/landing pages |
| `LicitacoesPreview` | Bid preview list |
| `GoogleAnalytics` | GA4 script injection |
| `ClarityAnalytics` | Microsoft Clarity injection |
| `StructuredData` | Schema.org JSON-LD |
| `ContentPageLayout` | Institutional page layout |
| `BlogArticleLayout` | Blog article layout |
| `InstitutionalSidebar` | Sidebar for institutional pages |
| `ContextualTutorialTooltip` | In-context help tooltips |
| `ValuePropSection` | Value proposition section |

### Landing Page Components (`app/components/landing/`)

| Component | Purpose |
|-----------|---------|
| `HeroSection` | Landing page hero with CTA |
| `LandingNavbar` | Public-facing navigation bar |
| `HowItWorks` | 3-step process explanation |
| `DifferentialsGrid` | Feature differentials display |
| `TrustCriteria` | Trust signals section |
| `ProofOfValue` | Social proof section |
| `AnalysisExamplesCarousel` | Example analysis carousel |
| `SectorsGrid` | Supported sectors grid |
| `DataSourcesSection` | Data sources display |
| `StatsSection` | Platform statistics |
| `OpportunityCost` | Cost of not using SmartLic |
| `BeforeAfter` | Before/after comparison |
| `FinalCTA` | Bottom CTA section |

### UI Primitives (`components/ui/`, `app/components/ui/`)

| Component | Purpose |
|-----------|---------|
| `button.tsx` | CVA-based button with variants |
| `Pagination` | Page navigation component |
| `CurrencyInput` | Brazilian currency (R$) input |
| `GradientButton` | Gradient-styled button |
| `Tooltip` | Hover tooltip component |
| `CategoryBadge` | Category indicator badge |
| `ScoreBar` | Score visualization bar |
| `GlassCard` | Glassmorphism card |
| `BentoGrid` | Bento grid layout |

---

## 4. State Management

### Patterns Used

1. **React Context** (3 contexts):
   - `AuthContext` -- User session, admin status, auth methods
   - `ThemeContext` -- Dark/light mode with localStorage persistence
   - `TutorialContext` -- Contextual tutorial tooltip state

2. **SWR (5 hooks with SWR)**:
   - `usePlans` -- Plan list fetching
   - `usePipeline` -- Pipeline data with mutations
   - `useSessions` -- Session history
   - `useTrialPhase` -- Trial status
   - `useUserProfile` -- User profile data

3. **Custom Hooks (component-local state)**:
   - `useSearch` -- Core search state machine (loading, results, error, retries)
   - `useSearchSSE` / `useSearchSSEHandler` -- SSE connection management
   - `useSearchFilters` -- Sector list fetching with SWR + localStorage fallback
   - `useSearchRetry` -- Auto-retry with exponential backoff
   - `useSearchExport` -- Excel/sheets export state
   - `useSearchExecution` -- Search execution orchestration
   - `useSearchPersistence` -- Search state persistence to localStorage
   - `useUfProgress` -- Per-UF progress tracking during search
   - `useFetchWithBackoff` -- Generic fetch with exponential backoff
   - `useSearchPolling` -- Polling for async search results
   - `usePlan` -- Single plan info with backoff
   - `useQuota` -- Quota usage tracking
   - `useAnalytics` -- Mixpanel event tracking
   - `useIsMobile` -- Media query hook (768px breakpoint)
   - `useKeyboardShortcuts` -- Keyboard shortcut handling
   - `useNavigationGuard` -- Unsaved changes protection
   - `useFeatureFlags` -- Runtime feature flag evaluation
   - `useSavedSearches` -- Saved search CRUD
   - `useOnboarding` -- Onboarding state management
   - `useShepherdTour` -- Shepherd.js tour integration
   - `useServiceWorker` -- Service worker registration
   - `useUnreadCount` -- Unread message count
   - `useBroadcastChannel` -- Cross-tab search sync

4. **localStorage Keys** (heavily used):
   - `smartlic-theme` -- Theme preference
   - `smartlic-onboarding-completed` -- Onboarding flag
   - `smartlic-profile-context` -- Cached profile context
   - `smartlic_last_search` -- Last search results cache (24h)
   - `search_partial_*` -- Partial search results (30min TTL)
   - `smartlic_plan_cache` -- Plan cache (1hr TTL)
   - `smartlic-saved-searches` -- Saved search list
   - `smartlic-cookie-consent` -- LGPD consent
   - `smartlic-tutorial-*` -- Tutorial completion state
   - `safeSetItem()` wrapper handles QuotaExceededError with eviction

5. **No Global Store** -- No Redux, Zustand, or Jotai. State is distributed across context providers and local component state.

---

## 5. API Integration

### Proxy Architecture

All API calls from the browser go through Next.js API routes (`app/api/`) which proxy to the FastAPI backend at `NEXT_PUBLIC_BACKEND_URL`. This pattern:
- Hides backend URL from client
- Adds auth headers server-side
- Enables response transformation
- Provides CORS-free communication

### API Proxy Routes (58 total)

| Proxy Route | Backend Endpoint | Methods |
|-------------|-----------------|---------|
| `/api/buscar` | `POST /buscar` | POST |
| `/api/buscar-progress` | `GET /buscar-progress/{search_id}` (SSE) | GET |
| `/api/buscar-results/[searchId]` | `GET /v1/search/{id}/status` | GET |
| `/api/search-status` | `GET /v1/search/{id}/status` | GET |
| `/api/search-zero-match/[searchId]` | Zero-match results endpoint | GET |
| `/api/download` | Excel file download | GET |
| `/api/regenerate-excel/[searchId]` | Excel regeneration | POST |
| `/api/analytics` | Multiple analytics endpoints | GET |
| `/api/pipeline` | Pipeline CRUD | GET/POST/PATCH/DELETE |
| `/api/plans` | Plan listing | GET |
| `/api/subscription-status` | Subscription info | GET |
| `/api/billing-portal` | Stripe portal session | POST |
| `/api/trial-status` | Trial phase info | GET |
| `/api/feedback` | Feedback submission | POST/DELETE |
| `/api/sessions` | Search sessions | GET |
| `/api/search-history` | Search history | GET |
| `/api/me` | User profile | GET |
| `/api/me/export` | GDPR data export | GET |
| `/api/change-password` | Password change | POST |
| `/api/profile-context` | Profile context | GET/PUT |
| `/api/profile-completeness` | Profile completion score | GET |
| `/api/setores` | Sector list | GET |
| `/api/messages/*` | Messaging CRUD | Multiple |
| `/api/first-analysis` | Onboarding first analysis | POST |
| `/api/onboarding` | Onboarding state | GET/POST |
| `/api/health` | Health check (always 200) | GET |
| `/api/health/cache` | Cache health | GET |
| `/api/admin/[...path]` | Admin catch-all proxy | Multiple |
| `/api/admin/metrics` | Metrics endpoint | GET |
| `/api/auth/*` | Auth endpoints (login, signup, google, check-email, check-phone) | Multiple |
| `/api/mfa` | MFA setup/verify | Multiple |
| `/api/alerts/*` | Alert CRUD | Multiple |
| `/api/alert-preferences` | Alert preferences | GET/PUT |
| `/api/organizations/*` | Org management | Multiple |
| `/api/subscriptions/*` | Cancel, cancel-feedback | POST |
| `/api/export/google-sheets` | Google Sheets export | POST |
| `/api/bid-analysis/[bidId]` | Deep bid analysis | GET |
| `/api/status` | System status | GET |
| `/api/csp-report` | CSP violation reports | POST |
| `/api/metrics/*` | Frontend metrics (discard-rate, sse-fallback, daily-volume) | POST |
| `/api/reports/diagnostico` | Diagnostic report | POST |
| `/api/og` | Open Graph image generation | GET |

### Data Fetching Patterns

1. **Direct fetch** -- Most pages use `fetch()` with manual token management
2. **fetchWithAuth()** -- Auto-retry on 401 with token refresh
3. **SWR hooks** -- 5 hooks using SWR for caching + revalidation
4. **SSE** -- Search progress via `EventSource` with heartbeat
5. **Polling** -- Async search status polling via `useSearchPolling`

### Type Safety

- API types auto-generated from backend OpenAPI schema via `openapi-typescript`
- `app/api-types.generated.ts` provides `components["schemas"]` types
- `app/types.ts` re-exports + extends with frontend-specific fields
- Command: `npm run generate:api-types`

---

## 6. Authentication Flow

### Architecture

1. **Supabase SSR** (`@supabase/ssr`) with PKCE flow
2. **Browser client** -- Lazy singleton via Proxy in `lib/supabase.ts`
3. **Server client** -- `lib/supabase-server.ts` + `lib/serverAuth.ts`
4. **Middleware** (`middleware.ts`) -- Route protection + security headers

### Auth Methods

- Email/password sign in (`signInWithPassword`)
- Email/password sign up (`signUp` with metadata: full_name, company, sector, phone)
- Magic link (`signInWithOtp`)
- Google OAuth (`signInWithOAuth` with `prompt: consent`)

### Route Protection

**Protected routes** (middleware-enforced):
`/buscar`, `/historico`, `/conta`, `/admin/*`, `/dashboard`, `/mensagens`, `/planos/obrigado`

**Public routes** (explicitly allowed):
`/login`, `/signup`, `/planos`, `/auth/callback`

### Session Management

- `AuthProvider` context wraps entire app
- Initial auth: `getUser()` (server-validated) with 10s timeout fallback to `getSession()`
- Proactive refresh: 10-minute interval
- `sessionExpired` state triggers `SessionExpiredBanner`
- `fetchWithAuth()` auto-retries on 401 with token refresh
- Redirect to `/login?reason=session_expired` on unrecoverable 401
- `isMountedRef` prevents setState-after-unmount race conditions

### Security Headers (middleware)

- Content-Security-Policy (enforcing)
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- HSTS with preload
- Cross-Origin-Opener-Policy: same-origin
- Permissions-Policy: camera=(), microphone=(), geolocation=()
- CSP violation reporting to `/api/csp-report`

---

## 7. Styling Architecture

### Design System

Built on CSS custom properties (design tokens) with Tailwind utility classes.

**Color Palette:**
- Brand: `--brand-navy` (#0a1e3f), `--brand-blue` (#116dff)
- Surfaces: `--surface-0` (base), `--surface-1` (elevated), `--surface-2` (cards)
- Ink: `--ink` (primary text), `--ink-secondary`, `--ink-muted`, `--ink-faint`
- Semantic: `--success`, `--error`, `--warning` (with `-subtle` variants)
- Gem palette: sapphire, emerald, amethyst, ruby (translucent accents)

**Typography:**
- Body: DM Sans (variable: `--font-body`)
- Display: Fahkwang (variable: `--font-display`)
- Data: DM Mono (variable: `--font-data`)
- Fluid scale: clamp() for hero, h1-h3, body-lg

**Shadows:** Layered system (sm through 2xl) + glow + glass

**Border Radius:** input (4px), button (6px), card (8px), modal (12px)

**Spacing:** 4px base grid documented in config (but Tailwind default spacing is not overridden -- this is a debt item)

### Dark Mode

- Strategy: `class` (not `media`)
- Toggle via `ThemeProvider` context
- Persisted to `smartlic-theme` localStorage
- Anti-FOUC: inline script in `<head>` reads localStorage before render
- Full dark palette with documented WCAG contrast ratios
- `global-error.tsx` uses `prefers-color-scheme` media query (can't load Tailwind when root layout fails)

### Responsive Design

- Breakpoints: Tailwind defaults (`sm: 640px`, `md: 768px`, `lg: 1024px`, `xl: 1280px`)
- Mobile detection: `useIsMobile()` hook (768px breakpoint)
- Mobile-specific components: `BottomNav`, `MobileDrawer`, `MobileMenu`
- Touch targets: CSS forces `min-height: 44px` on buttons and inputs
- Body font size: `clamp(14px, 1vw + 10px, 16px)`

### Glassmorphism Effects

- Glass background: `rgba(255, 255, 255, 0.7)` + backdrop blur
- `GlassCard` component for premium feel
- Dark mode adjustments for glass effects

---

## 8. Animation / Interaction

### Framer Motion Usage

Only 3 files use Framer Motion directly:
1. `ProfileCompletionPrompt.tsx` -- Entrance animation
2. `ProfileCongratulations.tsx` -- Celebration animation
3. `SearchStateManager.tsx` -- Search state transitions

### CSS Animations (Tailwind keyframes)

| Animation | Use Case |
|-----------|----------|
| `fade-in-up` | Staggered entrance for cards/sections |
| `gradient` | Background gradient animation (hero) |
| `shimmer` | Loading skeleton shimmer |
| `float` | Floating elements (decorative) |
| `slide-up` | Section entrance on scroll |
| `scale-in` | Modal/dialog entrance |
| `slide-in-right` | Drawer entrance |
| `bounce-gentle` | Scroll indicator bounce |

### Animation Library (`lib/animations/`)

- `framerVariants.ts` -- Reusable Framer Motion variant presets
- `scrollAnimations.ts` -- Scroll-triggered animations
- `easing.ts` -- Shared easing curves
- `index.ts` -- Barrel export

### Route Transitions

- NProgress (nprogress) for route change progress bar
- `NProgressProvider` wraps app with route change detection

### Loading States

- `LoadingProgress` -- Simple progress bar
- `EnhancedLoadingProgress` -- Multi-step with step names and ARIA
- `LoadingResultsSkeleton` -- Search results skeleton
- `ResultsLoadingSection` -- Results area skeleton
- Auth loading: Centered spinner (protected layout)
- Dashboard: Inline skeleton components

---

## 9. Accessibility Audit

### Strengths

1. **Skip Navigation** -- "Pular para conteudo principal" skip link in root layout
2. **Focus Indicators** -- 3px solid outline (WCAG 2.2 AAA compliant, 2.4.13)
3. **Touch Targets** -- CSS enforces `min-height: 44px` on buttons/inputs
4. **Color Contrast** -- WCAG ratios documented in CSS variables (all AA or better)
5. **ARIA Usage** -- 127 ARIA attributes across 30+ components
6. **Language** -- `lang="pt-BR"` on html element
7. **Font Display** -- `display: swap` on all Google Fonts
8. **Semantic HTML** -- `<main>`, `<nav>`, `<header>` used in layouts
9. **Dark Mode Contrast** -- Dark palette has documented contrast ratios
10. **E2E Accessibility Tests** -- `dialog-accessibility.spec.ts`, `@axe-core/playwright` in devDeps

### Weaknesses / Violations

1. **No `alt` text on images** -- `next/image` is barely used (only 4 files), most images are SVGs or icons without `alt`
2. **Missing `aria-label` on icon-only buttons** -- Some icon buttons (LlmSourceBadge, ZeroMatchBadge) may lack labels
3. **No `loading.tsx` files** -- Zero Next.js streaming loading states; all loading is client-side
4. **Keyboard navigation gaps** -- No visible focus trapping in modals (Dialog component)
5. **Color-only indicators** -- Some badges rely on color alone (ViabilityBadge green/yellow/red)
6. **Screen reader support** -- Limited `aria-live` regions for dynamic content (search progress, toasts)
7. **Form validation announcements** -- Error messages may not be announced to screen readers
8. **Search results announcements** -- No `aria-live="polite"` for result count changes

---

## 10. Performance Analysis

### Strengths

1. **Standalone output** -- Tree-shaken Node.js server
2. **Google Fonts with `display: swap`** -- No render blocking
3. **SWR deduplication** -- 5s dedup interval prevents duplicate requests
4. **Lazy Supabase client** -- Proxy pattern avoids initialization at import time
5. **Dynamic blog imports** -- `next/dynamic` for blog article content
6. **Sentry tunnel route** -- `/monitoring` rewrite bypasses ad blockers

### Concerns

1. **No `loading.tsx` streaming** -- All 44 pages lack Next.js streaming boundaries, causing full page loads
2. **Large page components** -- `conta/page.tsx` (1,420 lines), `buscar/page.tsx` (1,057 lines), `alertas/page.tsx` (1,068 lines), `dashboard/page.tsx` (1,037 lines) -- these monolithic components likely have unnecessary re-renders
3. **No `next/image` usage** -- Only 4 files import `next/image`; no image optimization
4. **No `React.lazy` / `dynamic()` for app components** -- Only 2 non-test files use `dynamic()` (login page, blog slug)
5. **Recharts full import** -- No evidence of tree-shaking Recharts components
6. **23 client-side pages** -- Many pages that could be server components are `"use client"` (e.g., `/planos` could be partially server)
7. **No route prefetching strategy** -- No `<Link prefetch>` optimization visible
8. **Bundle includes 3 Google Fonts** -- DM Sans, Fahkwang, DM Mono all loaded globally
9. **Sentry SDK** -- `@sentry/nextjs` 10.38 adds significant bundle weight
10. **No `useMemo`/`useCallback` in some large pages** -- While `buscar/page.tsx` has 15 usages, some large pages like `alertas` have only 2

---

## 11. Error Handling

### Error Boundaries

| Boundary | Scope | Implementation |
|----------|-------|---------------|
| `global-error.tsx` | Root layout crashes | Inline styles (can't use Tailwind), Sentry capture |
| `error.tsx` | Page-level errors | Tailwind-styled, Sentry capture, analytics tracking |
| `SearchErrorBoundary` | Search results area only | Class component, Sentry capture, retry + reset |
| `admin/error.tsx` | Admin section errors | Admin-specific error handling |

### Error Message System

- `lib/error-messages.ts` -- Central error translation layer
  - `getUserFriendlyError()` -- Maps technical errors to Portuguese
  - `translateAuthError()` -- Supabase auth error translations
  - `getRetryMessage()` -- Contextual retry messages
  - `isTransientError()` -- Classifies recoverable vs permanent errors
  - `getHumanizedError()` -- Error + action suggestion + tone (blue/yellow, never red)
  - `ERROR_CODE_MESSAGES` -- Backend error code to message mapping
  - 35+ error patterns mapped

### Retry Mechanisms

1. **useSearchRetry** -- Auto-retry with [10s, 20s, 30s] countdown, max 3 attempts
2. **useFetchWithBackoff** -- Exponential backoff (2s->4s->8s->16s->30s cap), max 5 retries
3. **SWR built-in** -- 3 error retries with exponential backoff
4. **fetchWithAuth** -- Single 401 retry with token refresh

### User Feedback Components

- `SearchErrorBanner` -- Error display with retry for search
- `ErrorStateWithRetry` -- Generic error with retry button
- `PartialResultsPrompt` -- Partial success notification
- `SourcesUnavailable` -- All sources failed
- `BackendStatusIndicator` -- Backend health polling with visual indicator
- `SessionExpiredBanner` -- Session expiration notification
- `PaymentFailedBanner` -- Payment failure notification
- Sonner toasts for transient notifications

---

## 12. Testing Coverage

### Unit/Integration Tests (Jest + React Testing Library)

- **292 test files** in `frontend/__tests__/`
- **2,681+ passing tests** (0 failures baseline)
- **Quarantine folder** -- 14 flaky tests isolated in `__tests__/quarantine/`

**Test Categories:**
| Category | Files | Description |
|----------|-------|-------------|
| Component tests | ~80 | Individual component rendering + interaction |
| Hook tests | ~15 | Custom hook behavior |
| API route tests | ~12 | Proxy route handling |
| Page tests | ~10 | Full page rendering |
| Utility tests | ~15 | lib/ function tests |
| Integration tests | ~20 | Multi-component flows |
| Accessibility tests | 1 | Dedicated a11y test file |
| Polish/UX tests | ~10 | Visual consistency tests |
| E2E-style tests (Jest) | 4 | `__tests__/e2e/` (not Playwright) |

**Test Setup:**
- `jest.setup.js` polyfills: `crypto.randomUUID`, `EventSource` (jsdom lacks both)
- `@jest-environment jsdom` (default), `@jest-environment node` for API route tests
- Coverage threshold: 60% (CI gate)

### E2E Tests (Playwright)

- **21 spec files** in `frontend/e2e-tests/`
- Key flows: search, auth, theme, saved searches, empty state, error handling, admin, signup consent, dialog accessibility, performance, plan display, landing page
- Helpers in `e2e-tests/helpers/`
- CI: `.github/workflows/e2e.yml`
- `@axe-core/playwright` available for automated accessibility testing

### Coverage Gaps

1. No tests for: `NavigationShell`, `Sidebar`, `BottomNav`, `MobileDrawer` (critical navigation)
2. No tests for: `CookieConsentBanner`, `StructuredData`, `GoogleAnalytics`, `ClarityAnalytics`
3. No tests for: Most `landing/` components (only 3 of 13 tested)
4. No tests for: `app/api/buscar-progress/route.ts` (SSE proxy)
5. No tests for: Blog pages and programmatic SEO pages
6. No tests for: `/admin/*` pages (except admin-cache)
7. No tests for: `/conta/equipe`, `/conta/seguranca` pages
8. No tests for: `MfaSetupWizard`, `TotpVerificationScreen`
9. Lighthouse CI configured (`@lhci/cli`) but unclear if regularly run

---

## 13. Technical Debt Inventory

### TD-HIGH: Architecture / Structural Issues

| ID | Issue | Impact | Files |
|----|-------|--------|-------|
| **TD-H01** | **Monolithic page components** -- 4 pages exceed 1,000 lines: `conta/page.tsx` (1,420), `alertas/page.tsx` (1,068), `buscar/page.tsx` (1,057), `dashboard/page.tsx` (1,037). These violate single-responsibility and cause unnecessary re-renders. | Performance, maintainability | 4 pages |
| **TD-H02** | **No `loading.tsx` streaming** -- Zero Next.js streaming loading files across all 44 pages. Every page transition shows nothing until JS hydrates. | UX, perceived performance | All routes |
| **TD-H03** | **No i18n framework** -- All user-facing strings are hardcoded Portuguese. No translation system. Future localization would require touching every file. | Scalability | ~100+ files |
| **TD-H04** | **Excessive client-side pages** -- 23 of 44 pages use `"use client"`. Many (planos, historico, alertas) could partially or fully run as server components, reducing client JS. | Bundle size, TTI | 23 pages |
| **TD-H05** | **Dual component directories** -- Components split across `components/`, `app/components/`, `app/buscar/components/` with no clear separation rule. Some overlap (e.g., EmptyState exists in both `components/` and `app/components/`). | Developer confusion | 3 directories |
| **TD-H06** | **No global state management** -- Complex state coordination (auth + plan + quota + search + pipeline) relies on prop drilling and context composition. Works now but will not scale. | Scalability | Multiple pages |
| **TD-H07** | **Inconsistent data fetching** -- Some hooks use SWR, most use raw `fetch()`, some use `fetchWithAuth()`. No unified pattern. | Consistency, error handling | ~30 files |

### TD-MEDIUM: Code Quality Issues

| ID | Issue | Impact | Files |
|----|-------|--------|-------|
| **TD-M01** | **`any` types in production code** -- 4 files use `: any` (buscar route.ts, GoogleAnalytics, MunicipioFilter, OrgaoFilter). `getUserFriendlyError()` accepts `any` parameter. | Type safety | 5 files |
| **TD-M02** | **Console statements in production** -- `buscar/page.tsx` and `auth/callback/page.tsx` have console.log/warn/error calls in page components. `AuthProvider` has debug console.log for Google OAuth. | Log noise | 3+ files |
| **TD-M03** | **28+ TODO/FIXME in blog content** -- All blog articles have identical TODO comments for unimplemented programmatic page links. | Incomplete feature | 14+ blog files |
| **TD-M04** | **Duplicate EmptyState components** -- `components/EmptyState.tsx` and `app/components/EmptyState.tsx` -- unclear which is canonical. | Confusion | 2 files |
| **TD-M05** | **Inconsistent error boundary coverage** -- Only `/buscar` has a component-level error boundary. Dashboard, pipeline, historico, mensagens, alertas have no boundaries below the page level. | Resilience | 5+ pages |
| **TD-M06** | **SearchErrorBoundary uses hardcoded red** -- Uses `bg-red-50`, `text-red-600` etc. instead of CSS variables, contradicting the "blue/yellow only, never red" UX guideline in `error-messages.ts`. | UX inconsistency | 1 file |
| **TD-M07** | **No memoization in some large pages** -- `alertas/page.tsx` (1,068 lines) has only 2 `useMemo`/`useCallback`, risking re-render of complex filter/list UI. | Performance | 2-3 pages |
| **TD-M08** | **`nul` file in app directory** -- `frontend/app/nul` exists (Windows artifact from `> /dev/null` typo). Harmless but messy. | Codebase hygiene | 1 file |

### TD-MEDIUM: Styling Inconsistencies

| ID | Issue | Impact | Files |
|----|-------|--------|-------|
| **TD-S01** | **Mixed CSS variable and raw value usage** -- Some components use `bg-[var(--surface-1)]` (design system), others use raw Tailwind (`bg-red-50`, `text-gray-500`). `SearchErrorBoundary` and `global-error.tsx` use hardcoded colors. | Visual consistency | ~10 files |
| **TD-S02** | **Global-error.tsx color drift** -- Uses different brand colors (`#2563eb`, `#1e3a5f`) than the design system (`#116dff`, `#0a1e3f`). These are Tailwind defaults, not SmartLic tokens. | Brand inconsistency | 1 file |
| **TD-S03** | **Tailwind spacing config empty** -- `tailwind.config.ts` has a comment about "4px base" but no actual spacing overrides, so default Tailwind spacing (which is 4px-based anyway) is used. Config comment is misleading. | Documentation | 1 file |
| **TD-S04** | **Limited responsive testing in Tailwind** -- Only ~20 files actively use responsive breakpoints (`sm:`, `md:`, etc.). Many components may not be mobile-optimized. | Mobile experience | ~24 untested files |

### TD-MEDIUM: Performance Anti-Patterns

| ID | Issue | Impact | Files |
|----|-------|--------|-------|
| **TD-P01** | **No `next/image` usage** -- Only 4 files reference `next/image` (2 are test files). No image optimization, no lazy loading of images, no responsive sizing. | Core Web Vitals (LCP) | All pages with images |
| **TD-P02** | **No code splitting for heavy components** -- Recharts, @dnd-kit, shepherd.js loaded eagerly on their respective pages. No `dynamic()` for these. | Bundle size | 3-4 pages |
| **TD-P03** | **3 Google Fonts loaded globally** -- DM Sans, Fahkwang, and DM Mono loaded for ALL pages even though DM Mono (data font) and Fahkwang (display font) are used on few pages. | Font loading time | Root layout |
| **TD-P04** | **No route-level code splitting** -- SSR standalone builds include all pages. No `dynamic(() => import())` for rarely-accessed admin pages. | Initial bundle | Admin pages |

### TD-LOW: Missing Features / Polish

| ID | Issue | Impact | Files |
|----|-------|--------|-------|
| **TD-L01** | **No `aria-live` for search results** -- Search result count and status changes not announced to screen readers. | Accessibility | buscar/page.tsx |
| **TD-L02** | **No focus trapping in modals** -- Dialog, DeepAnalysisModal, UpgradeModal, CancelSubscriptionModal lack focus trap. Tab key can reach elements behind the modal. | Accessibility | 4+ modals |
| **TD-L03** | **Color-only viability indicators** -- ViabilityBadge uses green/yellow/red without secondary indicators (icon or pattern) for colorblind users. | Accessibility | 1 component |
| **TD-L04** | **No keyboard shortcut documentation** -- `useKeyboardShortcuts` exists but no visible help (e.g., `?` to show shortcuts). | Discoverability | 1 hook |
| **TD-L05** | **Missing test coverage for navigation** -- `NavigationShell`, `Sidebar`, `BottomNav`, `MobileDrawer` have zero tests despite being rendered on every authenticated page. | Test coverage | 4 components |
| **TD-L06** | **Quarantine tests not resolved** -- 14 tests in `__tests__/quarantine/` are bypassed. These include AuthProvider, AnalyticsProvider, LicitacaoCard, ContaPage -- important components. | Test confidence | 14 test files |
| **TD-L07** | **No PWA / offline support** -- `useServiceWorker` hook exists but unclear if service worker is actually registered. No manifest.json visible. | Offline capability | 1 hook |
| **TD-L08** | **Blog programmatic links are TODOs** -- 28 TODO comments in blog content for unimplemented internal links (MKT-003, MKT-005). SEO internal linking incomplete. | SEO value | 14 blog files |
| **TD-L09** | **No structured form validation** -- Forms use manual validation. No react-hook-form or zod integration (identified as pending in FE-M03). | DX, user experience | Multiple forms |
| **TD-L10** | **Stale `react-simple-pull-to-refresh`** -- Installed as dependency but no usage found in codebase. Dead dependency. | Bundle bloat | package.json |
| **TD-L11** | **No `<Suspense>` boundaries** -- Beyond the lack of `loading.tsx`, there are no explicit `<Suspense>` boundaries for data-dependent sections. | Streaming, UX | All pages |

### TD Summary by Priority

| Priority | Count | Key Items |
|----------|-------|-----------|
| HIGH | 7 | Monolithic pages, no streaming, no i18n, excessive CSR, dual component dirs, no global state, inconsistent fetching |
| MEDIUM | 12 | `any` types, console noise, duplicate components, missing error boundaries, style inconsistencies, no image optimization, font bloat |
| LOW | 11 | A11y gaps, missing tests, quarantine tests, PWA gaps, dead deps, no form validation lib |
| **Total** | **30** | |

---

## Appendix A: File Size Heatmap (Top 10 Largest Pages)

| File | Lines | Recommendation |
|------|-------|---------------|
| `conta/page.tsx` | 1,420 | Split into sub-components (ProfileSection, PlanSection, DataSection) |
| `alertas/page.tsx` | 1,068 | Extract AlertRuleEditor, AlertList, AlertPreview |
| `buscar/page.tsx` | 1,057 | Already well-decomposed into sub-components; remaining logic is orchestration |
| `dashboard/page.tsx` | 1,037 | Extract chart sections into individual components |
| `admin/page.tsx` | 764 | Extract admin data tables |
| `onboarding/page.tsx` | 689 | Extract step components (already partially done) |
| `planos/page.tsx` | 672 | Extract PricingTable, FAQSection |
| `mensagens/page.tsx` | 568 | Extract ConversationList, MessageThread |
| `login/page.tsx` | 501 | Reasonable size but has OAuth debug logging |
| `pipeline/page.tsx` | 481 | Reasonable size |

## Appendix B: Dependency Audit

| Dependency | Status | Notes |
|-----------|--------|-------|
| `next` 16.1.6 | Current | App Router, standalone |
| `react` 18.3.1 | Current | Not yet React 19 |
| `framer-motion` 12.33.0 | Current | Only 3 files use it -- consider removing for CSS-only animations |
| `@sentry/nextjs` 10.38.0 | Current | Significant bundle impact |
| `shepherd.js` 14.5.1 | Current | Only used in onboarding tour |
| `swr` 2.4.1 | Current | Only 5 hooks use it -- consider standardizing all fetching |
| `recharts` 3.7.0 | Current | Only in dashboard -- could be dynamically imported |
| `@dnd-kit/*` | Current | Only in pipeline page |
| `react-simple-pull-to-refresh` | Unused | No imports found -- candidate for removal |
| `nprogress` 0.2.0 | Legacy | Consider native View Transitions API |
| `sonner` 2.0.7 | Current | Toast notifications |
| `mixpanel-browser` 2.74.0 | Current | Analytics (9 pages tracked) |

---

*End of Frontend Specification & Audit*
