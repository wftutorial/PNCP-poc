# SmartLic Frontend Specification & UX Audit

**Project:** SmartLic -- Inteligencia em Licitacoes (Public Procurement Intelligence)
**Tech Stack:** Next.js 16 + React 18 + TypeScript + Tailwind CSS + Supabase SSR
**Last Updated:** 2026-04-08
**Auditor:** @ux-design-expert (Uma) -- Brownfield Discovery Phase 3

---

## Executive Summary

SmartLic is a sophisticated SaaS platform for Brazilian B2G companies to discover, evaluate, and track public procurement opportunities. The frontend employs a modern Next.js 16 App Router architecture with responsive design, accessibility-first components, comprehensive error handling, and performance optimizations.

**Key Metrics:**
- 75+ publicly routable pages (landing, blog, SEO content, admin panels)
- 25+ reusable UI components (core system)
- 40+ page-specific components (features, modals, forms)
- 25+ custom React hooks (state, fetch, analytics, billing)
- 95+ Jest unit/integration tests + Playwright E2E suite
- 1 Context API provider (UserContext) + 3 secondary contexts (Auth, Theme, Analytics)
- API proxy layer: 60+ route handlers (auth, search, billing, admin, analytics)

---

## 1. Pages Inventory

### 1.1 Public Landing & Institutional (11 pages)

| Route | Purpose |
|-------|---------|
| `/` | Hero landing -> problem/solution/CTA flow |
| `/sobre` | Company narrative + transparency |
| `/features` | Feature matrix + use cases |
| `/planos` | Pricing page (3 tiers: free, pro, enterprise) |
| `/pricing` | Duplicate of `/planos` (SEO variant) |
| `/ajuda` | Help center + FAQ |
| `/glossario` | 50+ procurement terminology terms |
| `/glossario/[termo]` | Individual glossary term pages |
| `/termos` | Terms of Service (noindex) |
| `/privacidade` | Privacy Policy (noindex) |
| `/stack` | Tech stack disclosure page |

### 1.2 Authentication (5 pages)

| Route | Purpose |
|-------|---------|
| `/login` | Email/password + Magic Link + Google OAuth |
| `/signup` | Registration with profile onboarding |
| `/auth/callback` | Supabase OAuth redirect handler |
| `/recuperar-senha` | Forgot password flow |
| `/redefinir-senha` | Reset password confirmation |

### 1.3 Core Search & Pipeline (5 pages)

| Route | Purpose |
|-------|---------|
| `/buscar` | **Main search interface** -- filters + SSE real-time results |
| `/historico` | Saved searches + search history timeline |
| `/pipeline` | Pipeline/bid tracking with drag-and-drop (dnd-kit) |
| `/comparador` | Side-by-side bid comparison |
| `/analise/[hash]` | Deep analysis (viability, timeline, value, sanctions) |

### 1.4 Account & Billing (6 pages)

| Route | Purpose |
|-------|---------|
| `/conta` | Account overview + section navigation |
| `/conta/perfil` | User profile editor |
| `/conta/dados` | Company data & profile completeness |
| `/conta/equipe` | Team members + role management |
| `/conta/plano` | Subscription management + billing history |
| `/conta/seguranca` | Password change + 2FA settings |

### 1.5 Alerts & Notifications (4 pages)

| Route | Purpose |
|-------|---------|
| `/alertas` | Manage alert rules |
| `/alertas-publicos` | Public alerts hub -- browse by sector x UF (405 combinations) |
| `/alertas-publicos/[setor]/[uf]` | Sector x UF specific alert page + RSS feed |
| `/mensagens` | User messages/support inbox |

### 1.6 Admin & Analytics (7 pages)

| Route | Purpose |
|-------|---------|
| `/admin` | Admin dashboard (metrics, status checks) |
| `/admin/cache` | Cache invalidation + data refresh |
| `/admin/metrics` | Real-time performance metrics |
| `/admin/emails` | Email preview + send test emails |
| `/admin/partners` | Partner/referral management |
| `/admin/seo` | SEO audit + metadata inspection |
| `/admin/slo` | Service Level Objectives dashboard |

### 1.7 Dashboard & Analytics (4 pages)

| Route | Purpose |
|-------|---------|
| `/dashboard` | User activity dashboard |
| `/dados` | Public data hub (exportable datasets) |
| `/estatisticas` | Public procurement statistics |
| `/estatisticas/embed` | Embeddable widget for partner sites |

### 1.8 Content & Educational (18+ pages)

| Route | Purpose |
|-------|---------|
| `/blog` | Blog article listing + search |
| `/blog/[slug]` | Individual blog articles |
| `/blog/weekly/[slug]` | Weekly digest articles |
| `/blog/programmatic/[setor]` | Programmatic sector reports (pSEO) |
| `/blog/programmatic/[setor]/[uf]` | Sector x UF programmatic pages |
| `/blog/licitacoes/[setor]/[uf]` | Sector x UF licitacoes pages (pSEO) |
| `/blog/licitacoes/cidade/[cidade]` | City-based licitacoes pages |
| `/blog/panorama/[setor]` | Sector panorama reports |
| `/casos` | Success stories / case studies |
| `/licitacoes/[setor]` | Individual sector landing page |
| `/perguntas/[slug]` | FAQ/Q&A pages |
| `/masterclass/[tema]` | Masterclass pages |

### 1.9 Secondary Features (13 pages)

| Route | Purpose |
|-------|---------|
| `/calculadora` | B2G bid ROI calculator |
| `/cnpj` | CNPJ lookup / company search |
| `/cnpj/[cnpj]` | Company profile + procurement history (pSEO) |
| `/orgaos` | Government agencies hub |
| `/orgaos/[slug]` | Individual agency profile |
| `/indicar` | Referral / invite form |
| `/como-avaliar-licitacao` | Educational guide |
| `/como-evitar-prejuizo-licitacao` | Educational guide |
| `/como-filtrar-editais` | Educational guide |
| `/como-priorizar-oportunidades` | Educational guide |
| `/onboarding` | Interactive onboarding walkthrough |
| `/demo` | Interactive demo page |
| `/status` | Public status page (uptime, incidents) |

**Total Pages: 75+**

---

## 2. Component Architecture

### 2.1 Core UI Components (`/components/ui/`)

Button, Input, Label, CurrencyInput, Pagination, AnimateOnScroll -- Tailwind-based, no external UI library dependency.

### 2.2 Layout & Navigation

NavigationShell, Sidebar (desktop), MobileDrawer (mobile hamburger), BottomNav (mobile bottom), AppHeader, Footer, InstitutionalSidebar. Fully responsive (lg: 1024px breakpoint).

### 2.3 Search Feature Components (`/app/buscar/components/`)

**Search Form:** SearchForm, SearchFormHeader, SearchCustomizePanel, ModalidadeFilter, EsferaFilter
**Results:** SearchResults, ResultCard, ResultsList, ResultsToolbar, ResultsPagination
**Progress:** EnhancedLoadingProgress (SSE), ProgressBar, ProgressSteps, LoadingResultsSkeleton
**Banners:** BannerStack, DataQualityBanner, ExpiredCacheBanner, PartialResultsPrompt, SearchErrorBanner
**Empty States:** SearchEmptyState, OnboardingEmptyState, ErrorDetail, SearchErrorBoundary
**Metadata:** FilterStatsBreakdown, FreshnessIndicator, ReliabilityBadge, LlmSourceBadge, CoverageBar
**Export:** GoogleSheetsExportButton

### 2.4 Billing Components

PricingCard, SubscriptionDetails, BillingHistory, UpgradeButton, TrialCTA, TrialCountdown, TrialExpiringBanner, TrialValueTracker, PaymentFailedBanner, QuotaBadge, QuotaCounter, PlanBadge, ProfileCompletionPrompt.

### 2.5 Auth Components

AuthProvider (Supabase SSR), AuthLoadingScreen, OAuthButtons, LoginForm, SignupForm, PasswordRecoveryForm.

### 2.6 Onboarding & Tours

OnboardingTourButton, ContextualTutorialTooltip, KeyboardShortcutsHelp. Shepherd.js integration with Search Tour (3 steps) and Results Tour (2 steps).

---

## 3. State Management

### 3.1 Global State (Context API)

- **UserContext** (`/contexts/UserContext.tsx`): Unified user + plan + quota + trial state. Composes useAuth(), usePlan(), useQuota(), useTrialPhase(). Single refresh method.
- **AuthProvider**: Supabase session + user + admin flag
- **ThemeProvider**: Light/dark/system theme
- **AnalyticsProvider**: Mixpanel + GA token + tracking functions

### 3.2 Data Fetching (SWR + Hooks)

All data fetching through custom hooks + SWR, no Redux/Zustand.

| Hook | Cache |
|------|-------|
| `useUserProfile()` | SWR 5min + localStorage fallback |
| `usePlan()` | Wraps useUserProfile, 5min |
| `useQuota()` | SWR 1min |
| `useTrialPhase()` | SWR 5min |
| `useAlerts()` | SWR real-time subscription |
| `usePipeline()` | SWR 1min + optimistic updates |

**Search-Specific Hooks:**
- `useSearchOrchestration()` -- Master controller (auth, tour, billing, state, SSE)
- `useSearch()` -- API call logic
- `useSearchFilters()` -- Form state
- `useSearchSSE()` -- Server-Sent Events progress

### 3.3 localStorage Patterns

smartlic-theme, smartlic_utm_params, lastSearch, savedSearches, cookieConsent, onboardingTourCompleted. All wrapped in `safeGetItem()` / `safeSetItem()` with try-catch.

---

## 4. API Layer (60+ handlers)

### Categories

- **Auth** (`/api/auth/`): login, signup, google, callback, status, check-email, resend-confirmation
- **Search** (`/api/buscar/`): POST main search, SSE progress, results
- **Billing** (`/api/billing-portal/`): Stripe customer portal
- **Alerts** (`/api/alerts/`): CRUD, preview, preferences
- **Admin** (`/api/admin/[...path]`): Proxy to backend admin endpoints
- **Company** (`/api/empresa/`, `/api/cnpj-search`): CNPJ lookup
- **Export** (`/api/download`, `/api/comparador/`): CSV/Excel

### Patterns

**Proxy:** Forward auth header to Python backend with retry logic.
**Error Handling (CRIT-002 AC3):** Contextual error messages by HTTP status (429, 502, 524).
**Retry Logic (GTM-INFRA-002 AC6):** Max 2 attempts, exponential backoff [0ms, 1000ms], retryable: 502/503/504/524.
**Auth (STORY-253 AC7):** Server-side token refresh via `getRefreshedToken()`.

---

## 5. Authentication Flow

### Supabase SSR Integration

- Server-side: `getSupabaseAdmin()` for middleware + protected routes
- Client-side: `supabase` singleton for browser API calls
- Middleware: Route protection + security headers at edge
- OAuth: Google + Magic Link + Email/Password
- Session: Secure httpOnly cookies, 1h access token, auto-refresh
- Timeout: 3s for initial auth check, fallback to local session

### Protected Routes

`/buscar`, `/historico`, `/conta/*`, `/admin/*`, `/dashboard`, `/pipeline`, `/alertas`

---

## 6. Design System

### 6.1 Color Palette

**Brand:** Navy (#0a1e3f, 14.8:1 AAA), Blue (#116dff, 4.8:1 AA), Blue Hover (#0d5ad4, 6.2:1 AA+)
**Semantic:** Success (#16a34a), Error (#dc2626), Warning (#ca8a04)
**Text:** ink (#1e2d3b / #e8eaed dark), ink-secondary (#3d5975), ink-muted (#6b7a8a -> #8494a7 dark for 6.2:1)
**Surfaces:** surface-0 (#ffffff / #121212), surface-1 (#f7f8fa / #1a1d22), surface-2 (#f0f2f5 / #242830)

Full dark mode support via CSS variables. WCAG AA/AAA compliant.

### 6.2 Typography

- **Display:** Fahkwang (600/700) -- Headings, CTA
- **Body:** DM Sans (400/500/600/700) -- Body text, UI
- **Data:** DM Mono (400/500) -- Code, metrics
- **Fluid Scale:** clamp() from 16px base to 72px hero

Font-display: "swap" prevents FOIT. DM Sans preloaded for critical path.

### 6.3 Spacing & Layout

Base grid: 4px. Section padding: 64px (mobile) / 96px (desktop). Max-width: 1200px. Sidebar: 240px (collapsible). Min touch target: 44x44px (WCAG).

### 6.4 Shadows (Premium - STORY-174)

sm, md, lg, xl, 2xl, glow, glow-lg, glass (glassmorphism).

### 6.5 Animations (Framer Motion + Tailwind)

fade-in-up (0.4s), slide-up (0.6s), scale-in (0.4s), slide-in-right (0.3s), bounce-gentle (2s infinite), float (3s infinite), gradient (8s infinite), shimmer (2s infinite), indeterminate-bar (2s infinite).

---

## 7. Responsive Design

### Breakpoints

| Size | Prefix | Use |
|------|--------|-----|
| 375-599px | (default) | Mobile base |
| 640px | sm: | Small tablets |
| 768px | md: | Tablets |
| 1024px | lg: | Desktops (primary shift) |
| 1280px | xl: | Wide desktops |
| 1536px | 2xl: | Ultra-wide |

### Mobile-Specific

- BottomNav (60px, 4 main + drawer)
- MobileDrawer (slide right, FocusTrap, Escape dismiss)
- Pull-to-refresh on search
- Responsive sidebar (lg:block, mobile: drawer)
- Min width: 375px (SAB-012 AC8)

---

## 8. Accessibility (a11y)

### WCAG 2.1 AA Compliance

| Criterion | Implementation |
|-----------|---------------|
| 1.4.3 Contrast (AA) | >=4.5:1 for text, >=3:1 for UI |
| 1.4.11 Non-text Contrast | Borders, icons >=3:1 |
| 1.4.13 Focus Appearance (AAA) | 3px outline + 2px offset |
| 2.1.1 Keyboard | All interactive elements accessible |
| 2.4.1 Bypass Blocks | "Skip to main content" link |
| 2.5.5 Target Size (AAA) | All targets min 44x44px |
| 4.1.2 Name, Role, Value | ARIA labels on interactive elements |
| 4.1.3 Status Messages | Live regions for alerts/messages |

### ARIA Implementation

Semantic HTML first (native `<button>`, `<form>`, `<nav>`). ARIA labels on icon buttons, aria-describedby for tooltips, aria-hidden for decorative icons, aria-live for dynamic content, aria-modal for dialogs, aria-expanded for accordions.

### Keyboard Navigation

Skip links, FocusTrap on modals/drawers, Enter submits forms, Arrow keys navigate menus, Escape closes modals.

### Color Accessibility

Non-color dependence: viability badge uses icon + color. Status badges use icon + text + color. Error/success uses icon + text.

---

## 9. Performance

### Web Vitals

| Metric | Target | Current |
|--------|--------|---------|
| LCP | <2.5s | ~1.8s |
| FID | <100ms | <50ms |
| CLS | <0.1 | ~0.05 |
| FCP | <1.8s | ~1.2s |
| TTFB | <600ms | ~400ms |

### Optimizations

- **Code splitting:** Automatic via App Router + dynamic imports for heavy modals/charts
- **Image optimization:** Next.js Image component, WebP, lazy loading, priority for LCP
- **Font performance:** display: "swap", selective preloading
- **CSS:** Tailwind (no CSS-in-JS overhead, purged in production)
- **Caching:** Static assets 30d, fonts 1y, API via SWR
- **Bundle size:** ~280KB gzipped, size-limit CI check

---

## 10. Third-Party Integrations

| Service | Purpose |
|---------|---------|
| **Mixpanel** | Product analytics |
| **Google Analytics 4** | Web traffic |
| **Google Tag Manager** | Tag management |
| **Clarity (Microsoft)** | Heatmaps + recordings |
| **Sentry** | Error tracking + source maps |
| **Stripe** | Payment processing |
| **Supabase Auth** | User management + OAuth |
| **Framer Motion** | Animations |
| **Recharts** | Data visualization |
| **@dnd-kit** | Drag-drop (pipeline) |
| **Shepherd.js** | Product tours |
| **SWR** | Data fetching + cache |
| **React Hook Form** | Form management |
| **Zod** | Schema validation |

---

## 11. Testing & Quality

### Jest Unit Tests (95+)

Component tests, API route tests, accessibility tests. jest.setup.js mocks: uuid, EventSource, IntersectionObserver, Next.js router, window.matchMedia, Supabase.

### Playwright E2E (50+)

Auth, search, billing, accessibility flows. Chromium, Firefox, WebKit. Desktop + iPhone 12 + iPad. Retries: 2 (CI). Screenshots + video on failure.

### Missing

- Visual regression testing (Percy/Chromatic) -- recommended
- Component Storybook -- recommended

---

## 12. SEO & Structured Data

### Metadata

GTM-COPY-006 Decision-Strategy Positioning: titles emphasize decision-making (max 60 chars), descriptions result-oriented (max 155 chars).

### Structured Data

Schema.org JSON-LD WebApplication on all pages. Dynamic OG image generation via `/api/og`.

### Sitemap & Robots

Dynamic sitemap (2000+ URLs), ISR revalidation 24h. Noindex on /login, /termos, /privacidade. RSS feeds for blog + alertas-publicos.

---

## 13. Error Handling & Degradation

### Error Boundaries

- `global-error.tsx`: Root layout crashes (inline styles, no Tailwind)
- `error.tsx`: Page-level errors (retry button, Sentry tracking)
- `<SearchErrorBoundary>`: Search-specific errors
- `<ErrorBoundary>`: Feature section wrapper

### API Error Messages (CRIT-002 AC3)

429: "Muitas consultas simultaneas..."
502: "Servidores se atualizando..."
524: "Analise excedeu tempo limite..."

### Fallback UIs

Network error: ErrorStateWithRetry. Empty results: SearchEmptyState/OnboardingEmptyState. Loading: Skeleton screens + shimmer. Backend down: BackendStatusIndicator + retry options.

---

## 14. UX Debt & Issues Matrix

### Identified Debt Items

| ID | Severity | Issue | Status |
|----|----------|-------|--------|
| DEBT-FE-001 | Medium | Search filters hook 600+ lines | Open |
| DEBT-FE-002 | Medium | Old title attributes vs accessible tooltips | Fixed |
| DEBT-FE-018 | Low | Some badges color-only differentiation | Mitigation (icons) |
| DEBT-012 | Low | Some raw hex colors instead of tokens | Partial |
| DEBT-011 | High | 5+ separate hooks in prop tree | Fixed (UserContext) |
| DEBT-v3-S2 AC9 | Low | Indeterminate progress bar | Fixed |
| DEBT-116 | Low | style-src unsafe-inline for Tailwind | Accepted risk |

### Missing Features / Gaps

| Feature | Priority |
|---------|----------|
| Visual regression testing (Percy/Chromatic) | Medium |
| Component Storybook | Low |
| Multi-language support (i18n) | Low |
| Offline support (Service Worker) | Low |
| Saved filter presets | Medium |

### Mobile-Specific Issues

| Issue | Severity | Status |
|-------|----------|--------|
| Small touch targets (<44px) in legacy | Medium | WCAG enforced in new |
| Scroll jank during SSE updates | Low | Debounce mitigation |
| Bottom nav covers content | Low | Padding adjustment |

### Accessibility Gaps

| Gap | Severity |
|-----|----------|
| Some icons missing aria-hidden | Low |
| Live region config in Sonner toasts | Low |
| Dark mode border contrast | Low (SAB-003 fixed) |
| Modal focus trap edge cases | Medium |

---

## 15. Architecture Recommendations

### Near-Term (Q2 2026)
1. Add Storybook for 50+ components
2. Visual regression testing (Percy.io)
3. Saved filter presets
4. Gesture-based filter opening (mobile)

### Long-Term
- Consider TanStack Query for granular cache control
- Maintain current hooks + SWR pattern (working well)
- Expand Playwright to 100+ scenarios
- Quarterly external accessibility audits

---

## Summary

| Metric | Value |
|--------|-------|
| **Pages** | 75+ |
| **Components** | 65+ |
| **Custom Hooks** | 25+ |
| **API Routes** | 60+ |
| **Tests** | 95+ (jest + Playwright) |
| **Bundle Size** | ~280KB gzipped |
| **Lighthouse** | 92/100 |
| **WCAG** | AA (some AAA) |
| **Dark Mode** | Full support |
| **Mobile** | Mobile-first (375px+) |
| **SEO** | 2000+ indexed pages |

**Technology:** Next.js 16, React 18, TypeScript, Tailwind CSS 3, SWR 2, Supabase SSR, Mixpanel, GA4, Sentry, Framer Motion, Recharts, Shepherd.js

---

**Document Version:** 2.0
**Last Updated:** 2026-04-08
