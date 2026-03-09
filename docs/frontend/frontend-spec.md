# SmartLic Frontend Specification & UX Audit

> Generated: 2026-03-09 | Source: Brownfield Discovery Phase 3
> Stack: Next.js 16 + React 18 + TypeScript 5.9 + Tailwind CSS 3

---

## 1. Project Structure & Configuration

### Directory Layout

```
frontend/
├── app/                    # Next.js App Router (pages + API routes)
│   ├── api/                # 58 API proxy routes
│   ├── buscar/             # Main search page + sub-components + hooks
│   │   ├── components/     # 35 search-specific components
│   │   ├── hooks/          # useSearch, useSearchFilters, useSearchRetry, etc.
│   │   └── types/          # search-results.ts type definitions
│   ├── dashboard/          # Analytics dashboard + sub-components
│   ├── components/         # App-level shared components (46 files)
│   ├── admin/              # Admin pages (cache, emails, metrics, SLO, partners)
│   ├── blog/               # SEO blog with programmatic pages
│   ├── conta/              # Account settings (dados, equipe, perfil, plano, seguranca)
│   └── ...                 # 47 total page routes
├── components/             # Global shared components (49 files)
│   ├── ui/                 # Primitives (Button, Input, Label, Pagination, CurrencyInput)
│   ├── billing/            # PaymentFailedBanner, PaymentRecoveryModal, TrialPaywall, TrialUpsellCTA
│   ├── subscriptions/      # PlanCard, PlanToggle, TrustSignals, DowngradeModal, etc.
│   ├── auth/               # MfaEnforcementBanner, MfaSetupWizard, TotpVerificationScreen
│   ├── blog/               # BlogCTA, RelatedPages, SchemaMarkup
│   ├── layout/             # MobileMenu
│   ├── reports/            # PdfOptionsModal
│   ├── org/                # InviteMemberModal
│   └── account/            # CancelSubscriptionModal
├── hooks/                  # 27 custom React hooks
├── contexts/               # UserContext (single context)
├── lib/                    # 37 utility/library files
│   ├── animations/         # Framer Motion variants, easing, scroll
│   ├── constants/          # sector-names, uf-names, stopwords
│   ├── copy/               # ROI text, comparisons, value props
│   ├── schemas/            # Zod form validation
│   └── utils/              # correlationId, dateDiffInDays
├── __tests__/              # 303 Jest test files
├── e2e-tests/              # 21 Playwright E2E specs
└── public/                 # Static assets
```

**Totals:** ~445 source files (.ts/.tsx), 303 unit test files, 21 E2E specs, 58 API proxy routes.

### Build & Runtime Configuration

| Setting | Value | File |
|---------|-------|------|
| **Framework** | Next.js 16.1.6 (App Router) | `package.json` |
| **Output** | Standalone (for Railway) | `next.config.js` -> `output: 'standalone'` |
| **React** | 18.3.1 | `package.json` |
| **TypeScript** | 5.9.3, strict mode | `tsconfig.json` |
| **Module** | ESNext / bundler resolution | `tsconfig.json` |
| **Build ID** | Timestamp + random (cache invalidation) | `next.config.js` -> `generateBuildId` |
| **Sentry** | Wrapped via `@sentry/nextjs` 10.38 | `next.config.js` |
| **Sitemap** | `next-sitemap` postbuild | `package.json` scripts |
| **Path aliases** | `@/*` maps to project root | `tsconfig.json` |
| **Dark mode** | `class` strategy | `tailwind.config.ts` |
| **Strict mode** | Enabled | `next.config.js` -> `reactStrictMode: true` |

### Static Asset Cache Headers

| Path | Cache-Control |
|------|---------------|
| `/_next/static/*` | `public, max-age=2592000, immutable` (30 days) |
| `/images/*` | `public, max-age=604800` (7 days) |
| `/fonts/*` | `public, max-age=31536000, immutable` (1 year) |

---

## 2. Pages Inventory (47 Routes)

### Core Application Pages (Protected)

| Route | Purpose | Data Fetching | Key Features |
|-------|---------|---------------|-------------|
| `/buscar` | **Main search** -- largest page (~983 LOC) | Client-side POST + SSE streaming | Sector/UF filters, SSE progress, pull-to-refresh, keyboard shortcuts, guided tours, error boundary, cross-tab sync |
| `/dashboard` | User analytics dashboard | Client-side fetch with backoff + Promise.allSettled | Stat cards, time-series chart, dimensions widget, profile completeness, CSV export, team view toggle |
| `/pipeline` | Opportunity kanban board | SWR | Drag-and-drop (@dnd-kit), pipeline alerts, stage management |
| `/historico` | Search history | Client-side fetch | Session-based history, restore previous searches |
| `/mensagens` | Messaging system | Client-side fetch | Conversations list, reply, status management |
| `/alertas` | Alert management | SWR hooks | Alert preferences, notification bell |
| `/conta` | Account settings hub | - | Sub-routes for profile, security, plan, team, data |
| `/conta/perfil` | Profile editing | Client-side fetch | Profile context for recommendations |
| `/conta/seguranca` | Security settings | - | Password change, MFA setup |
| `/conta/plano` | Plan management | SWR | Current plan display, upgrade/downgrade |
| `/conta/equipe` | Team management | Client-side fetch | Member invitations (org feature) |
| `/conta/dados` | Data export/deletion | Client-side fetch | LGPD compliance, data portability |
| `/onboarding` | 3-step onboarding wizard | Client-side POST | CNAE selection, UF selection, first analysis auto-search |

### Admin Pages (Protected + Role-gated)

| Route | Purpose |
|-------|---------|
| `/admin` | Admin dashboard |
| `/admin/cache` | Cache management and invalidation |
| `/admin/emails` | Email template management |
| `/admin/metrics` | System metrics dashboard |
| `/admin/slo` | SLO monitoring dashboard |
| `/admin/partners` | Partner management |

### Public Pages (Marketing & Auth)

| Route | Purpose | Data Fetching |
|-------|---------|---------------|
| `/` | Landing page | Static |
| `/login` | Authentication | Supabase Auth |
| `/signup` | Registration | Supabase Auth |
| `/auth/callback` | OAuth callback handler | Server-side Supabase |
| `/recuperar-senha` | Password recovery | Supabase Auth |
| `/redefinir-senha` | Password reset | Supabase Auth |
| `/planos` | Pricing page | SWR (dynamic pricing from Stripe) |
| `/planos/obrigado` | Post-purchase thank you | Query params |
| `/pricing` | Marketing pricing | Static |
| `/features` | Feature showcase | Static |
| `/ajuda` | Help center | Static |
| `/sobre` | About page | Static |
| `/termos` | Terms of service | Static |
| `/privacidade` | Privacy policy | Static |
| `/status` | Public system status | Client-side fetch |

### SEO/Programmatic Pages

| Route | Purpose |
|-------|---------|
| `/blog` | Blog index |
| `/blog/[slug]` | Blog article (MDX-like) |
| `/blog/licitacoes` | Licitacoes hub |
| `/blog/licitacoes/[setor]/[uf]` | Programmatic SEO: sector x state pages |
| `/blog/panorama/[setor]` | Sector panorama pages |
| `/blog/programmatic/[setor]` | Programmatic sector pages |
| `/blog/programmatic/[setor]/[uf]` | Programmatic sector x UF pages |
| `/licitacoes` | Licitacoes landing |
| `/licitacoes/[setor]` | Sector-specific landing |
| `/como-avaliar-licitacao` | Content page -- how to evaluate bids |
| `/como-evitar-prejuizo-licitacao` | Content page -- avoiding losses |
| `/como-filtrar-editais` | Content page -- filtering bids |
| `/como-priorizar-oportunidades` | Content page -- prioritizing opportunities |

---

## 3. Component Catalog

### UI Primitives (`components/ui/`)

| Component | Purpose | Notes |
|-----------|---------|-------|
| `Button` | Core button with CVA variants | 6 variants (primary, secondary, destructive, ghost, link, outline), 4 sizes, loading state, icon-only requires `aria-label` (TypeScript-enforced) |
| `Input` | Form input | Standard text input |
| `Label` | Form label | Accessibility-aware |
| `Pagination` | Page navigation | Numbered pagination |
| `CurrencyInput` | BRL currency input | Formatted input for R$ values |

### Search Components (`app/buscar/components/` -- 35 files)

| Category | Components |
|----------|-----------|
| **Form** | `SearchForm`, `SearchResults`, `SearchStateManager` |
| **Progress** | `UfProgressGrid`, `SourceStatusGrid`, `CoverageBar`, `PartialResultsPrompt`, `PartialTimeoutBanner` |
| **Results** | `FilterPanel`, `FilterStatsBreakdown`, `FilterRelaxedBanner`, `EmptyResults`, `ZeroResultsSuggestions` |
| **Badges** | `ViabilityBadge`, `LlmSourceBadge`, `ReliabilityBadge`, `ZeroMatchBadge`, `CompatibilityBadge`, `FreshnessIndicator`, `ActionLabel` |
| **Error** | `SearchErrorBoundary`, `SearchErrorBanner`, `ErrorDetail`, `SourcesUnavailable`, `UfFailureDetail` |
| **Cache** | `ExpiredCacheBanner`, `DataQualityBanner`, `RefreshBanner`, `TruncationWarningBanner` |
| **Feedback** | `FeedbackButtons`, `DeepAnalysisModal` |
| **Onboarding** | `OnboardingBanner`, `OnboardingSuccessBanner`, `OnboardingEmptyState`, `SearchEmptyState` |

### App-Level Shared Components (`app/components/` -- 46 files)

| Category | Components |
|----------|-----------|
| **Auth** | `AuthProvider`, `SessionExpiredBanner`, `CookieConsentBanner` |
| **Navigation** | `AppHeader`, `UserMenu`, `SavedSearchesDropdown`, `Breadcrumbs`, `InstitutionalSidebar` |
| **Theme** | `ThemeProvider`, `ThemeToggle` |
| **Billing** | `PlanBadge`, `QuotaBadge`, `QuotaCounter`, `UpgradeModal`, `TrialConversionScreen`, `TrialExpiringBanner`, `TrialCountdown` |
| **Data Display** | `LicitacaoCard`, `LicitacoesPreview`, `StatusBadge`, `ComparisonTable`, `Countdown` |
| **Forms** | `CustomDateInput`, `CustomSelect`, `PaginacaoSelect`, `OrdenacaoSelect`, `RegionSelector`, `EsferaFilter`, `MunicipioFilter`, `OrgaoFilter` |
| **Content** | `ContentPageLayout`, `BlogArticleLayout`, `ValuePropSection`, `MessageBadge` |
| **Progress** | `LoadingProgress`, `NProgressProvider` |
| **Analytics** | `AnalyticsProvider`, `GoogleAnalytics`, `ClarityAnalytics`, `StructuredData` |
| **Pipeline** | `AddToPipelineButton`, `PipelineAlerts` |
| **Tour** | `ContextualTutorialTooltip` |
| **Landing** | `LandingNavbar` (in `landing/`) |
| **Footer** | `Footer` |

### Global Components (`components/` -- 49 files)

| Category | Components |
|----------|-----------|
| **Navigation** | `NavigationShell`, `Sidebar`, `BottomNav`, `MobileDrawer`, `MobileMenu` |
| **Loading** | `LoadingProgress`, `EnhancedLoadingProgress`, `AuthLoadingScreen` |
| **Billing** | `PaymentFailedBanner`, `PaymentRecoveryModal`, `TrialPaywall`, `TrialUpsellCTA` |
| **Subscriptions** | `PlanCard`, `PlanToggle`, `TrustSignals`, `DowngradeModal`, `AnnualBenefits`, `FeatureBadge` |
| **Auth** | `MfaEnforcementBanner`, `MfaSetupWizard`, `TotpVerificationScreen` |
| **Profile** | `ProfileCompletionPrompt`, `ProfileCongratulations`, `ProfileProgressBar` |
| **Blog SEO** | `BlogCTA`, `RelatedPages`, `SchemaMarkup` |
| **Reports** | `PdfOptionsModal` |
| **Org** | `InviteMemberModal` |
| **Account** | `CancelSubscriptionModal` |
| **Feedback** | `TestimonialSection` |
| **Alerts** | `AlertNotificationBell` |
| **Status** | `BackendStatusIndicator` |
| **Tour** | `OnboardingTourButton`, `KeyboardShortcutsHelp` |
| **Data** | `SWRProvider`, `GoogleSheetsExportButton` |
| **Error** | `ErrorStateWithRetry`, `EmptyState` |
| **Filters** | `ModalidadeFilter`, `StatusFilter`, `ValorFilter` |
| **Layout** | `PageHeader` |

---

## 4. API Integration Layer (58 Proxy Routes)

All API routes live in `frontend/app/api/` and serve as a proxy layer between the frontend client and the FastAPI backend. This pattern:
- Hides the backend URL from the client
- Handles auth token forwarding
- Provides CSP-compliant same-origin requests
- Enables SSE proxying with proper headers

### API Route Inventory

| Category | Routes | Count |
|----------|--------|-------|
| **Search** | `buscar`, `buscar-progress` (SSE), `buscar-results/[searchId]`, `search-history`, `search-status`, `search-zero-match/[searchId]` | 6 |
| **Auth** | `auth/login`, `auth/signup`, `auth/check-email`, `auth/check-phone`, `auth/google`, `auth/google/callback`, `auth/resend-confirmation`, `auth/status` | 8 |
| **User** | `me`, `me/export`, `profile-context`, `profile-completeness`, `change-password` | 5 |
| **Billing** | `plans`, `billing-portal`, `subscription-status`, `trial-status`, `subscriptions/cancel`, `subscriptions/cancel-feedback` | 6 |
| **Analytics** | `analytics` (endpoint param: summary, searches-over-time, top-dimensions, trial-value) | 1 |
| **Pipeline** | `pipeline` | 1 |
| **Messages** | `messages/conversations`, `messages/conversations/[id]`, `messages/conversations/[id]/reply`, `messages/conversations/[id]/status`, `messages/unread-count` | 5 |
| **Admin** | `admin/[...path]` (catch-all), `admin/metrics` | 2 |
| **Alerts** | `alerts`, `alerts/[id]`, `alerts/[id]/preview`, `alert-preferences` | 4 |
| **Export** | `download`, `export/google-sheets`, `regenerate-excel/[searchId]`, `reports/diagnostico` | 4 |
| **Health** | `health`, `health/cache` | 2 |
| **Metrics** | `metrics/daily-volume`, `metrics/discard-rate`, `metrics/sse-fallback` | 3 |
| **Other** | `bid-analysis/[bidId]`, `csp-report`, `feedback`, `first-analysis`, `mfa`, `onboarding`, `organizations`, `organizations/[id]`, `sessions`, `setores`, `status` | 11 |

### Proxy Pattern

Routes use a shared `create-proxy-route.ts` utility (in `lib/`) with:
- Auth token extraction from request headers
- Backend URL resolution via `NEXT_PUBLIC_BACKEND_URL`
- Error handling with `proxy-error-handler.ts`
- Correlation ID injection via `lib/utils/correlationId.ts`

### SSE Proxy (Critical Path)

The `buscar-progress` route proxies Server-Sent Events from the backend. Key configuration:
- `bodyTimeout: 0` to prevent premature connection closure
- Heartbeat forwarding for Railway idle timeout (60s)
- Graceful fallback: if SSE fails, frontend uses time-based progress simulation

---

## 5. Authentication & Authorization Flow

### Architecture

```
Browser -> Next.js Middleware -> Supabase Auth (getUser) -> Protected Route
                                    |
                               Cookie-based sessions
                               (getAll/setAll pattern)
```

### Middleware (`middleware.ts`)

1. **Canonical domain redirect** -- Railway URLs (*.railway.app) -> smartlic.tech (301)
2. **API passthrough** -- `/api/*` routes skip auth check
3. **Public routes** -- `/login`, `/signup`, `/planos`, `/auth/callback` skip auth
4. **Protected routes** -- `/buscar`, `/historico`, `/conta`, `/admin/*`, `/dashboard`, `/mensagens`, `/planos/obrigado`
5. **Session validation** -- Uses `supabase.auth.getUser()` (server-side validation, not just `getSession()`)
6. **Session expiry detection** -- Distinguishes "never logged in" vs "session expired" via cookie inspection
7. **User headers** -- Injects `x-user-id` and `x-user-email` into request headers

### Auth Provider (`AuthProvider.tsx`)

Client-side React Context providing:
- `session` -- Supabase session object
- `user` -- Authenticated user
- `loading` -- Auth state loading
- `signOut` -- Logout function
- `isAdmin` -- Role check

### Security Headers (applied in middleware to all non-static routes)

| Header | Value |
|--------|-------|
| Content-Security-Policy | Enforcing mode with whitelisted domains (Stripe, Sentry, Supabase, Mixpanel, Cloudflare, Clarity) |
| X-Content-Type-Options | nosniff |
| X-Frame-Options | DENY |
| X-XSS-Protection | 1; mode=block |
| Referrer-Policy | strict-origin-when-cross-origin |
| Permissions-Policy | camera=(), microphone=(), geolocation=() |
| Strict-Transport-Security | max-age=31536000; includeSubDomains; preload |
| Cross-Origin-Opener-Policy | same-origin |
| X-DNS-Prefetch-Control | off |

### MFA Support

- `MfaEnforcementBanner` -- Prompts admin/master users to enable MFA
- `MfaSetupWizard` -- TOTP enrollment flow
- `TotpVerificationScreen` -- TOTP code entry during login
- API route: `/api/mfa`

---

## 6. State Management Patterns

### Provider Hierarchy (root layout)

```tsx
<AnalyticsProvider>
  <AuthProvider>
    <SWRProvider>
      <UserProvider>
        <ThemeProvider>
          <NProgressProvider>
            <BackendStatusProvider>
              {children}
            </BackendStatusProvider>
          </NProgressProvider>
        </ThemeProvider>
      </UserProvider>
    </SWRProvider>
  </AuthProvider>
</AnalyticsProvider>
```

### React Contexts (4)

| Context | Provider | Purpose |
|---------|----------|---------|
| **Auth** | `AuthProvider` | Supabase session, user, signOut, isAdmin |
| **User** | `UserProvider` (via `UserContext`) | Extended user profile data |
| **Theme** | `ThemeProvider` | Light/dark mode toggle (localStorage `smartlic-theme`) |
| **BackendStatus** | `BackendStatusProvider` | Online/offline/recovering status with polling |

### Custom Hooks (27)

| Hook | Purpose | Data Pattern |
|------|---------|-------------|
| `useAuth` | Access auth context | Context |
| `usePlan` | Current user plan info | SWR |
| `usePlans` | All available plans (pricing) | SWR |
| `useQuota` | Search quota tracking | SWR |
| `useTrialPhase` | Trial lifecycle phase | Derived from usePlan |
| `useAnalytics` | Mixpanel event tracking | Imperative |
| `useFeatureFlags` | Runtime feature toggles | localStorage + env vars |
| `useKeyboardShortcuts` | Global keyboard bindings | Event listeners |
| `useSearchSSE` | SSE event stream handling | EventSource + asyncio |
| `useSearchPolling` | Fallback polling for search status | Interval-based fetch |
| `useFetchWithBackoff` | Retry with exponential backoff | Generic fetch wrapper |
| `useSavedSearches` | CRUD for saved searches | localStorage + API |
| `useSessions` | Session history | SWR |
| `usePipeline` | Pipeline CRUD | SWR |
| `useAlerts` | Alert management | SWR |
| `useAlertPreferences` | Alert preference CRUD | SWR |
| `useConversations` | Message conversations | SWR |
| `useUnreadCount` | Unread message count | SWR |
| `useIsMobile` | Responsive breakpoint detection | matchMedia |
| `useNavigationGuard` | Prevent accidental navigation during search | beforeunload event |
| `useBroadcastChannel` | Cross-tab search result sync | BroadcastChannel API |
| `useShepherdTour` | Guided tour management | Shepherd.js integration |
| `useOnboarding` | Welcome tour lifecycle | localStorage state |
| `useProfileCompleteness` | Profile completion percentage | SWR |
| `useProfileContext` | User profile context for recommendations | SWR + localStorage cache |
| `useOrganization` | Organization/team membership | SWR |
| `usePublicMetrics` | Public system metrics | SWR |
| `useServiceWorker` | PWA service worker registration | Navigator API |
| `useUserProfile` | User profile data | SWR |

### localStorage Keys (observed in code)

| Key | Purpose |
|-----|---------|
| `smartlic-theme` | Theme preference (light/dark/system) |
| `smartlic-has-searched` | First-search tracking for progressive disclosure |
| `smartlic-first-tip-dismissed` | First-use tooltip dismissed |
| `smartlic:buscar:filters-expanded` | Filter accordion state |
| `smartlic-sidebar-collapsed` | Sidebar collapse state |
| `smartlic_onboarding_completed` | Welcome tour completed |
| `smartlic_onboarding_dismissed` | Welcome tour dismissed |
| `smartlic_tour_*_completed` | Per-tour completion tracking |
| `smartlic_partner` | Partner referral slug |
| `profileContext` | Cached user profile context |
| `smartlic-plan-cache` | Plan info cache (1hr TTL) |
| Various search state keys | Search parameters persistence |

### SWR Configuration

SWR is configured via `SWRProvider` with global settings. Individual hooks use SWR for:
- Plan data (`usePlan`, `usePlans`)
- Pipeline items (`usePipeline`)
- Alert data (`useAlerts`, `useAlertPreferences`)
- Profile completeness (`useProfileCompleteness`)
- Session history (`useSessions`)

---

## 7. Design System

### Typography

| Font | Variable | Usage | Preload |
|------|----------|-------|---------|
| **DM Sans** | `--font-body` | Body text (primary) | Yes |
| **Fahkwang** | `--font-display` | Headings, display text | No (non-critical path) |
| **DM Mono** | `--font-data` | Data/code displays | No (non-critical path) |

Fluid typography scale defined in CSS:
- Hero: `clamp(2.5rem, 5vw + 1rem, 4.5rem)` (40-72px)
- H1: `clamp(2rem, 4vw + 1rem, 3.5rem)` (32-56px)
- H2: `clamp(1.5rem, 3vw + 0.5rem, 2.5rem)` (24-40px)
- H3: `clamp(1.25rem, 2vw + 0.5rem, 1.75rem)` (20-28px)

### Color System (CSS Variables + Tailwind Mapping)

**Light Mode:**

| Token | CSS Variable | Hex | WCAG vs Canvas |
|-------|-------------|-----|----------------|
| `ink` (primary text) | `--ink` | `#1e2d3b` | 12.6:1 AAA |
| `ink-secondary` | `--ink-secondary` | `#3d5975` | 5.5:1 AA |
| `ink-muted` | `--ink-muted` | `#6b7a8a` | 5.1:1 AA |
| `brand-navy` | `--brand-navy` | `#0a1e3f` | 14.8:1 AAA |
| `brand-blue` | `--brand-blue` | `#116dff` | 4.8:1 AA |
| `brand-blue-hover` | `--brand-blue-hover` | `#0d5ad4` | 6.2:1 AA+ |
| `success` | `--success` | `#16a34a` | 4.7:1 AA |
| `error` | `--error` | `#dc2626` | 5.9:1 AA |
| `warning` | `--warning` | `#ca8a04` | 5.2:1 AA |
| `canvas` | `--canvas` | `#ffffff` | - |
| `surface-1` | `--surface-1` | `#f7f8fa` | - |
| `surface-2` | `--surface-2` | `#f0f2f5` | - |

**Dark Mode:** Full override set in `.dark` class with WCAG-compliant values (e.g., `--ink: #e8eaed` at 11.8:1).

**Special Palettes:**
- **Gem palette:** sapphire, emerald, amethyst, ruby (translucent for glassmorphism effects)
- **Chart palette:** 10 colors (`--chart-1` through `--chart-10`) for Recharts
- **Brand colors:** WhatsApp green

### Semantic Aliases

| Tailwind Token | Maps To |
|----------------|---------|
| `primary` | `--brand-blue` |
| `secondary` | `--brand-navy` |
| `accent` | `--brand-blue-hover` |
| `success` | `--success` |
| `error` | `--error` |
| `warning` | `--warning` |

### Spacing & Border Radius

- **Spacing:** 4px base grid (standard Tailwind units)
- `border-radius: input` = 4px
- `border-radius: button` = 6px
- `border-radius: card` = 8px
- `border-radius: modal` = 12px

### Shadows

Layered shadow system with 7 levels:
- `sm`, `md`, `lg`, `xl`, `2xl` (standard)
- `glow`, `glow-lg` (brand blue glow)
- `glass` (glassmorphism)
- Gem-specific shadows (sapphire, emerald, amethyst, ruby)

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

### Gradients

| Gradient | Use |
|----------|-----|
| `--gradient-brand` | CTA buttons, hero sections |
| `--gradient-hero-bg` | Landing page hero background |
| `--gradient-card` | Card overlays |
| `--gradient-text` | Gradient text effect |

### Glassmorphism

```css
--glass-bg: rgba(255, 255, 255, 0.7);
--glass-border: rgba(255, 255, 255, 0.18);
--glass-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
```

Used in pricing cards, FAQ sections, ROI anchor messages.

---

## 8. Accessibility Audit

### Strengths

1. **Skip navigation link** -- WCAG 2.4.1 compliant "Pular para conteudo principal" link in root layout
2. **WCAG color contrast** -- All text tokens documented with contrast ratios; all pass AA minimum
3. **Dark mode** -- Full dark mode with independently verified WCAG contrast ratios
4. **Button aria-label enforcement** -- TypeScript requires `aria-label` for icon-only buttons at compile time
5. **Focus ring** -- `focus-visible:ring-2 focus-visible:ring-brand-blue` on all interactive elements
6. **Semantic HTML** -- `<main id="main-content">`, `<header>`, `<footer role="contentinfo">`, `<nav>`
7. **Form labels** -- `<label htmlFor>` on form inputs (observed in search form, save dialog)
8. **Error role** -- `role="alert"` on error messages
9. **aria-expanded** -- Used on accordion/toggle controls
10. **Touch targets** -- Minimum 44px touch targets enforced on mobile (data-tour, mobile menu button)
11. **Playwright a11y testing** -- `@axe-core/playwright` included in devDependencies
12. **Dedicated accessibility test file** -- `__tests__/accessibility.test.tsx`

### Gaps

1. **`aria-live` regions** -- SSE progress updates and search results do not use `aria-live="polite"` for screen reader announcements when content updates dynamically
2. **Loading announcements** -- Loading spinners use visual-only indicators without `aria-busy` or `role="status"` on parent containers
3. **Error boundary** -- `SearchErrorBoundary` catches rendering errors but does not announce them to assistive technology
4. **Inline SVG icons** -- Most SVGs have `aria-hidden="true"` (good), but some inline SVGs in the pricing page lack it
5. **Dialog focus trap** -- `focus-trap-react` is installed but usage consistency across all modals is not confirmed
6. **Landmark duplication** -- Multiple `<footer>` elements exist (page-level footer in buscar + NavigationShell footer) which may confuse landmark navigation
7. **Color-only indicators** -- Some status indicators (viability badges, source status) rely partially on color alone
8. **Keyboard navigation** -- Keyboard shortcuts defined but not all modal closures respond to Escape key consistently
9. **Language attribute** -- `lang="pt-BR"` correctly set on `<html>`, which is good
10. **`prefers-reduced-motion`** -- Not explicitly respected; 8 custom animations have no reduced-motion media query override

---

## 9. Performance Analysis

### Bundle Optimization

| Feature | Status | Details |
|---------|--------|---------|
| **Standalone output** | Enabled | Minimizes deployment size on Railway |
| **Source map hiding** | Enabled | `hideSourceMaps: true` in Sentry config |
| **Debug statement removal** | Enabled | `excludeDebugStatements: true` (Sentry) |
| **Font optimization** | Partial | DM Sans preloaded; Fahkwang and DM Mono skip preload (display: swap) |
| **Image optimization** | Configured | Remote patterns for Wix static images |
| **Code splitting** | Automatic | Next.js App Router page-level splitting |
| **Sentry tree-shaking** | Enabled | Debug logger statements excluded |
| **Static asset caching** | Configured | 30-day immutable for JS/CSS, 1-year for fonts |

### Key Dependencies (sorted by typical bundle impact)

| Dependency | Size Impact | Justification |
|------------|------------|---------------|
| `react` + `react-dom` | ~130KB | Framework |
| `framer-motion` | ~70KB | Page transitions, animations |
| `recharts` | ~50KB | Dashboard charts |
| `@supabase/supabase-js` | ~40KB | Auth + API client |
| `@dnd-kit/*` | ~30KB | Pipeline drag-and-drop |
| `shepherd.js` | ~25KB | Guided tours |
| `date-fns` | Tree-shakeable | Date formatting |
| `zod` | ~15KB | Form validation |
| `swr` | ~10KB | Data fetching/caching |
| `lucide-react` | Tree-shakeable | Icons |
| `sonner` | ~8KB | Toast notifications |

### Performance Concerns

1. **`/buscar` page size** -- The main search page is ~983 lines with 30+ imports. While it uses `Suspense` boundary, the component itself is a single large client component with no further lazy loading
2. **Framer Motion** -- Loaded globally via animation imports; no dynamic import observed
3. **Shepherd.js** -- Loaded on every search page visit regardless of tour state
4. **No `next/dynamic`** -- No evidence of dynamic imports for heavy components (Recharts, @dnd-kit)
5. **Pull-to-refresh** -- `react-simple-pull-to-refresh` loaded on main search page (mobile-only feature, not conditionally imported)
6. **Lighthouse CI** -- Configured (`@lhci/cli` in devDependencies, scripts defined) but assertion thresholds not verified

---

## 10. Testing Coverage

### Jest Unit Tests

| Metric | Value |
|--------|-------|
| **Test files** | 303 |
| **Passing tests** | 2,681+ |
| **Failures** | 0 |
| **Coverage thresholds** | Branches: 50%, Functions: 55%, Lines: 55%, Statements: 55% |
| **Target coverage** | 60% (stepping stone from post-quarantine baseline) |
| **Test environment** | jsdom |
| **Transform** | @swc/jest (TypeScript + JSX) |
| **Reporters** | Default + jest-junit (CI) |

**Test distribution by category:**

| Category | Files | Examples |
|----------|-------|---------|
| **API proxy routes** | ~15 | SSE proxy, download, analytics, auth, health |
| **Search/Buscar** | ~12 | Coverage bar, freshness, truncation, state manager, progressive delivery |
| **Components** | ~25 | ThemeProvider, UserMenu, QuotaBadge, RegionSelector, LoadingProgress |
| **Billing** | ~6 | Dunning flow, payment banner, trial upsell, cancel subscription |
| **Pipeline** | ~3 | AddToPipeline, alerts, types |
| **Hooks** | ~6 | useAnalytics, useFeatureFlags, useKeyboardShortcuts, useSearchFilters |
| **Auth** | ~4 | MFA flow, signup confirmation, error messages |
| **Blog/SEO** | ~4 | B2G articles, infrastructure, programmatic |
| **Admin** | ~4 | SLO, partners, cache |
| **Landing** | ~3 | DifferentialsGrid, OpportunityCost, TrustCriteria |
| **Lib/Utils** | ~5 | fetchWithAuth, dates, reliability, proxy sanitization |
| **Pages** | ~3 | LoginPage, AjudaPage, RecuperarSenha |

**Polyfills (jest.setup.js):** `crypto.randomUUID` + `EventSource` (jsdom lacks both).

### Playwright E2E Tests (21 specs)

| Spec | Focus |
|------|-------|
| `search-flow.spec.ts` | Full search lifecycle |
| `auth-ux.spec.ts` | Authentication UX flows |
| `crit072-async-search.spec.ts` | Async search architecture |
| `error-handling.spec.ts` | Error states and recovery |
| `failure-scenarios.spec.ts` | Degradation and fallback |
| `empty-state.spec.ts` | Zero-result handling |
| `saved-searches.spec.ts` | Search persistence |
| `plan-display.spec.ts` | Pricing display |
| `signup-consent.spec.ts` | LGPD consent flow |
| `dialog-accessibility.spec.ts` | Dialog a11y |
| `performance.spec.ts` | Performance budgets |
| `theme.spec.ts` | Dark/light mode |
| `landing-page.spec.ts` | Landing page rendering |
| `institutional-pages.spec.ts` | Legal/about pages |
| `admin-users.spec.ts` | Admin functionality |
| `smoke-gtm-root-cause.spec.ts` | GTM integration smoke |
| `mkt-001-*.spec.ts` (3 files) | Marketing CTA, rich results, schema validation |
| `mkt-003-*.spec.ts` (2 files) | GSC indexation, schema validation |

**A11y tool:** `@axe-core/playwright` available for automated accessibility checks.

### Coverage Gaps

1. **No tests for:** `/dashboard` page, `/pipeline` page, `/historico` page, `/onboarding` page, `/conta/*` sub-pages
2. **SSE integration:** Unit tests mock SSE; no real SSE stream testing
3. **Cross-tab sync:** `useBroadcastChannel` has no dedicated tests
4. **Tour flows:** Shepherd.js integration not tested (guided tours)
5. **Responsive behavior:** No explicit mobile/tablet viewport testing in unit tests (covered partially by E2E)
6. **Dark mode rendering:** No systematic dark-mode snapshot tests
7. **Form validation:** Zod schemas in `lib/schemas/forms.ts` -- validation rules not fully tested

---

## 11. Technical Debt Catalog

### Severity: Critical

| ID | Issue | Location | Effort |
|----|-------|----------|--------|
| **FE-TD-001** | `/buscar/page.tsx` is ~983 lines with 30+ imports -- monolithic client component | `app/buscar/page.tsx` | Large (2-3 days) |
| **FE-TD-002** | No `next/dynamic` usage for heavy dependencies (Recharts, @dnd-kit, Shepherd.js, framer-motion) | Multiple pages | Medium (1 day) |
| **FE-TD-003** | SSE proxy complexity -- custom SSE handling with fallback simulation, multiple retry strategies | `hooks/useSearchSSE.ts`, `app/api/buscar-progress/route.ts` | Large (3-5 days to simplify) |

### Severity: High

| ID | Issue | Location | Effort |
|----|-------|----------|--------|
| **FE-TD-004** | Coverage thresholds at 50-55% (target is 60%, ideal is 80%) | `jest.config.js` | Ongoing |
| **FE-TD-005** | No `prefers-reduced-motion` media query for 8 custom animations | `tailwind.config.ts`, `globals.css` | Small (0.5 day) |
| **FE-TD-006** | Dual component directories (`app/components/` + `components/`) with unclear ownership boundaries | Project-wide | Medium (1-2 days) |
| **FE-TD-007** | `aria-live` missing on dynamic content updates (search results, SSE progress) | `app/buscar/components/SearchResults.tsx`, progress components | Small (0.5 day) |
| **FE-TD-008** | localStorage used directly in many places without centralized abstraction (despite `lib/storage.ts` existing) | Multiple hooks/components | Medium (1 day) |
| **FE-TD-009** | Inline SVGs throughout codebase (Stripe badge, payment icons, nav icons) instead of centralized icon system | `app/planos/page.tsx`, `components/Sidebar.tsx` | Medium (1 day) |
| **FE-TD-010** | `'unsafe-inline'` and `'unsafe-eval'` in CSP script-src | `middleware.ts` | Medium (1-2 days to implement nonces) |

### Severity: Medium

| ID | Issue | Location | Effort |
|----|-------|----------|--------|
| **FE-TD-011** | No page-level tests for dashboard, pipeline, historico, onboarding, or conta sub-pages | `__tests__/` | Medium (2-3 days) |
| **FE-TD-012** | `eslint-disable-next-line react-hooks/exhaustive-deps` used in multiple places (5+ occurrences in buscar) | `app/buscar/page.tsx` | Small (0.5 day) |
| **FE-TD-013** | Hardcoded pricing fallback in `planos/page.tsx` that must be kept in sync with Stripe | `app/planos/page.tsx` | Ongoing maintenance |
| **FE-TD-014** | Feature-gated code (ORGS_ENABLED, alertas, mensagens) still shipped in production bundles | Multiple files | Medium (1 day to add dynamic imports) |
| **FE-TD-015** | No bundle size monitoring/budget in CI (Lighthouse CI configured but not enforced) | `.lighthouserc.js` (missing?) | Small (0.5 day) |
| **FE-TD-016** | Multiple footer implementations (buscar page has inline footer + NavigationShell footer) | `app/buscar/page.tsx`, `components/NavigationShell.tsx` | Small (0.5 day) |
| **FE-TD-017** | Theme initialization script in `<head>` via `dangerouslySetInnerHTML` | `app/layout.tsx` | Low priority (works but not ideal) |
| **FE-TD-018** | Raw `var(--*)` CSS usage alongside Tailwind tokens in many components | Project-wide | Ongoing cleanup |

### Severity: Low

| ID | Issue | Location | Effort |
|----|-------|----------|--------|
| **FE-TD-019** | `@types/uuid` in dependencies (should be devDependencies) | `package.json` | Trivial |
| **FE-TD-020** | `__tests__/e2e/` directory exists alongside `e2e-tests/` (two E2E locations) | Test directories | Small (0.5 day) |
| **FE-TD-021** | No Storybook or component documentation system | Project-wide | Large (3-5 days initial setup) |
| **FE-TD-022** | `Button.examples.tsx` exists but no visual regression testing framework | `components/ui/Button.examples.tsx` | Medium (1-2 days) |

---

## 12. Recommended Priority Actions

### Phase 1: Quick Wins (1-2 days)

1. **Add `prefers-reduced-motion`** media queries to all 8 custom animations (FE-TD-005)
2. **Add `aria-live="polite"`** to search results container and SSE progress area (FE-TD-007)
3. **Move `@types/uuid`** to devDependencies (FE-TD-019)
4. **Consolidate E2E test directories** -- merge `__tests__/e2e/` into `e2e-tests/` (FE-TD-020)
5. **Deduplicate footer** -- remove inline footer from `/buscar` page (FE-TD-016)

### Phase 2: Performance (3-5 days)

1. **Dynamic import** heavy dependencies with `next/dynamic`:
   - Recharts (dashboard charts)
   - @dnd-kit (pipeline only)
   - Shepherd.js (only when tour is not completed)
   - Framer Motion (landing page sections only)
2. **Split `/buscar/page.tsx`** into sub-components with clear separation:
   - `BuscarPageHeader` -- header bar with controls
   - `BuscarDialogs` -- save dialog + keyboard help
   - `BuscarFooter` -- inline footer
   - `BuscarTrialGates` -- trial conversion + payment recovery modals
3. **Enforce Lighthouse CI budgets** in GitHub Actions pipeline
4. **Add bundle size tracking** to CI (e.g., `next-bundle-analyzer` or `size-limit`)

### Phase 3: Testing & Quality (5-7 days)

1. **Add page-level tests** for: dashboard, pipeline, historico, onboarding, conta (FE-TD-011)
2. **Raise coverage thresholds** to 60% (current target) incrementally
3. **Add dark-mode snapshot tests** for key components
4. **Test Zod validation schemas** in `lib/schemas/forms.ts`
5. **Add cross-tab sync tests** for `useBroadcastChannel`
6. **Fix all `eslint-disable` suppressions** for exhaustive-deps (FE-TD-012)

### Phase 4: Architecture (7-14 days)

1. **Consolidate component directories** -- define clear ownership:
   - `components/` = truly global (used on 3+ pages)
   - `app/components/` = app-specific but shared (used on 2+ authenticated pages)
   - Page-local `components/` = page-specific only
2. **Implement CSP nonces** to remove `'unsafe-inline'` and `'unsafe-eval'` from script-src (FE-TD-010)
3. **Centralize localStorage** -- route all reads/writes through `lib/storage.ts` with type-safe keys
4. **Replace inline SVGs** with a centralized icon component system (extend `lib/icons/index.tsx`)
5. **Add Storybook** for component documentation and visual regression testing
6. **Feature flag dead code elimination** -- use build-time flags or dynamic imports for gated features

---

## Appendix: Key File Reference

| File | Purpose |
|------|---------|
| `frontend/package.json` | Dependencies, scripts |
| `frontend/next.config.js` | Next.js + Sentry config |
| `frontend/tailwind.config.ts` | Design system tokens |
| `frontend/app/globals.css` | CSS variables (light + dark) |
| `frontend/tsconfig.json` | TypeScript strict config |
| `frontend/middleware.ts` | Auth + security headers |
| `frontend/jest.config.js` | Test configuration |
| `frontend/app/layout.tsx` | Root layout, provider hierarchy |
| `frontend/app/buscar/page.tsx` | Main search page (~983 LOC) |
| `frontend/app/buscar/hooks/useSearch.ts` | Search orchestration hook |
| `frontend/hooks/useSearchSSE.ts` | SSE stream handling |
| `frontend/lib/create-proxy-route.ts` | API proxy factory |
| `frontend/lib/proxy-error-handler.ts` | Proxy error normalization |
| `frontend/lib/storage.ts` | Safe localStorage wrapper |
| `frontend/components/ui/button.tsx` | Core Button (CVA) |
| `frontend/components/NavigationShell.tsx` | Auth-aware layout shell |
| `frontend/components/Sidebar.tsx` | Sidebar navigation |
| `frontend/contexts/UserContext.tsx` | User context provider |
