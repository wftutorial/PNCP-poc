# SmartLic Frontend Specification

**Version:** 2.0
**Date:** 2026-02-25
**Author:** @ux-design-expert (Phase 3 -- Brownfield Discovery)
**Framework:** Next.js 16 / React 18 / TypeScript 5.9 / Tailwind CSS 3.4
**Production URL:** https://smartlic.tech

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Technology Stack](#2-technology-stack)
3. [Design System](#3-design-system)
4. [Page Inventory](#4-page-inventory)
5. [Component Inventory](#5-component-inventory)
6. [Custom Hooks](#6-custom-hooks)
7. [API Integration](#7-api-integration)
8. [User Flows](#8-user-flows)
9. [Responsiveness](#9-responsiveness)
10. [Accessibility (a11y)](#10-accessibility-a11y)
11. [Performance](#11-performance)
12. [Testing](#12-testing)
13. [Security](#13-security)
14. [Technical Debt Inventory](#14-technical-debt-inventory)
15. [Remediation Roadmap](#15-remediation-roadmap)

---

## 1. Executive Summary

SmartLic is a government bid intelligence platform (licitacoes publicas) that automates discovery, analysis, and qualification of procurement opportunities for B2G companies. The frontend consists of **29 pages**, **100+ components** (across 4 component directories), **19 custom hooks**, **36 API proxy routes**, and a comprehensive design system built on CSS custom properties with dark/light theme support.

### Key Metrics

| Metric | Value |
|--------|-------|
| Total Pages | 29 (22 app pages + 4 SEO content + 2 blog + 1 auth callback) |
| Total Components | 100+ across 4 directories |
| Custom Hooks | 19 (16 global + 3 buscar-specific) |
| API Proxy Routes | 36 |
| Lib Utilities | 28 files |
| Unit Tests | 135 files, 2681+ passing |
| E2E Tests | 60 critical user flow tests |
| Dependencies (production) | 24 packages |
| Dependencies (dev) | 22 packages |

---

## 2. Technology Stack

### Core Framework

| Technology | Version | Purpose |
|-----------|---------|---------|
| Next.js | 16.1.6 | Full-stack React framework (App Router) |
| React | 18.3.1 | UI library |
| TypeScript | 5.9.3 | Type safety |
| Tailwind CSS | 3.4.19 | Utility-first CSS |

### UI Libraries

| Library | Version | Purpose |
|---------|---------|---------|
| Framer Motion | 12.33.0 | Animations (landing page, transitions) |
| Recharts | 3.7.0 | Dashboard charts (Bar, Line, Pie) |
| @dnd-kit/core | 6.3.1 | Pipeline drag-and-drop |
| @dnd-kit/sortable | 10.0.0 | Sortable pipeline columns |
| Shepherd.js | 14.5.1 | Interactive onboarding tours |
| Lucide React | 0.563.0 | Icon library (landing page only) |
| sonner | 2.0.7 | Toast notifications |
| react-day-picker | 9.13.0 | Date picker component |
| react-simple-pull-to-refresh | 1.3.4 | Mobile pull-to-refresh |
| nprogress | 0.2.0 | Page transition loading bar |

### Auth and Data

| Library | Version | Purpose |
|---------|---------|---------|
| @supabase/ssr | 0.8.0 | Server-side auth |
| @supabase/supabase-js | 2.95.3 | Client-side Supabase SDK |
| date-fns | 4.1.0 | Date manipulation |
| uuid | 13.0.0 | UUID generation |
| use-debounce | 10.1.0 | Input debouncing |

### Monitoring and Analytics

| Library | Version | Purpose |
|---------|---------|---------|
| @sentry/nextjs | 10.38.0 | Error tracking + source maps |
| mixpanel-browser | 2.74.0 | Product analytics |

### Testing

| Library | Version | Purpose |
|---------|---------|---------|
| Jest | 29.7.0 | Unit testing |
| @testing-library/react | 14.1.2 | Component testing |
| @playwright/test | 1.58.2 | E2E testing |
| @axe-core/playwright | 4.11.1 | Accessibility testing |

### Build and Dev

| Library | Version | Purpose |
|---------|---------|---------|
| @swc/jest | 0.2.29 | Fast test transforms |
| next-sitemap | 4.2.3 | Sitemap generation |
| @lhci/cli | 0.15.0 | Lighthouse CI |
| openapi-typescript | 7.13.0 | API type generation |
| @tailwindcss/typography | 0.5.19 | Prose styling (blog) |

---

## 3. Design System

### 3.1 Color Palette

The design system uses CSS custom properties (`:root` / `.dark`) with semantic naming. All colors have documented WCAG contrast ratios.

#### Canvas and Ink (Text)

| Token | Light | Dark | Contrast vs Canvas |
|-------|-------|------|--------------------|
| `--canvas` | `#ffffff` | `#121212` | Base |
| `--ink` | `#1e2d3b` | `#e8eaed` | 12.6:1 / 11.8:1 (AAA) |
| `--ink-secondary` | `#3d5975` | `#a8b4c0` | 5.5:1 / 7.2:1 (AA/AAA) |
| `--ink-muted` | `#6b7a8a` | `#6b7a8a` | 5.1:1 / 4.9:1 (AA) |
| `--ink-faint` | `#c0d2e5` | `#3a4555` | 1.9:1 / 2.1:1 (decorative) |

#### Brand Colors

| Token | Light | Dark | Purpose |
|-------|-------|------|---------|
| `--brand-navy` | `#0a1e3f` | `#0a1e3f` | Primary brand (14.8:1 AAA) |
| `--brand-blue` | `#116dff` | `#116dff` | Accent (4.8:1 AA) |
| `--brand-blue-hover` | `#0d5ad4` | `#0d5ad4` | Hover state (6.2:1 AA+) |
| `--brand-blue-subtle` | `#e8f0ff` | `rgba(17,109,255,0.12)` | Backgrounds |

#### Surface Hierarchy

| Token | Light | Dark | Purpose |
|-------|-------|------|---------|
| `--surface-0` | `#ffffff` | `#121212` | Base surface |
| `--surface-1` | `#f7f8fa` | `#1a1d22` | Elevated surface |
| `--surface-2` | `#f0f2f5` | `#242830` | Card backgrounds |
| `--surface-elevated` | `#ffffff` | `#1e2128` | Modals, dropdowns |

#### Semantic Colors

| Token | Light | Dark | Purpose |
|-------|-------|------|---------|
| `--success` | `#16a34a` | `#22c55e` | Success states |
| `--error` | `#dc2626` | `#f87171` | Error states |
| `--warning` | `#ca8a04` | `#facc15` | Warning states |

#### Gem Palette (GTM-006)

Translucent accent colors for badges and data visualization:

| Token | Purpose |
|-------|---------|
| `--gem-sapphire` | Blue accent (data source indicators) |
| `--gem-emerald` | Green accent (success metrics) |
| `--gem-amethyst` | Purple accent (premium features) |
| `--gem-ruby` | Red accent (alerts, urgency) |

### 3.2 Typography

Three font families loaded via Google Fonts with `display: swap`:

| Token | Font | Weight | Purpose |
|-------|------|--------|---------|
| `--font-body` | DM Sans | Regular (variable) | Body text, UI |
| `--font-display` | Fahkwang | 400-700 | Headings, hero text |
| `--font-data` | DM Mono | 400, 500 | Data, code, numbers |

#### Fluid Typography Scale (STORY-174)

| Token | Range | Usage |
|-------|-------|-------|
| `--text-hero` | 40-72px | Landing hero |
| `--text-h1` | 32-56px | Page headings |
| `--text-h2` | 24-40px | Section headings |
| `--text-h3` | 20-28px | Subsections |
| `--text-body-lg` | 18-20px | Body large |
| Base font | 14-16px | Standard body (via `clamp()`) |

### 3.3 Spacing System

4px base grid enforced via Tailwind defaults:

| Class | Value |
|-------|-------|
| `1` | 4px |
| `2` | 8px |
| `3` | 12px |
| `4` | 16px |
| `6` | 24px |
| `8` | 32px |
| `16` | 64px |

Section spacing (8pt grid):
- `--section-padding-sm`: 64px (mobile)
- `--section-padding-lg`: 96px (desktop)
- `--section-gap`: 128px (between sections)

### 3.4 Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| `input` | 4px | Form inputs |
| `button` | 6px | Buttons, CTAs |
| `card` | 8px | Cards, panels |
| `modal` | 12px | Modals, dialogs |

### 3.5 Shadows (Layered)

| Token | Usage |
|-------|-------|
| `sm` | Subtle elevation |
| `md` | Cards, dropdowns |
| `lg` | Floating panels |
| `xl` | Modals |
| `2xl` | Elevated content |
| `glow` | CTA hover glow |
| `glow-lg` | Hero CTA glow |
| `glass` | Glassmorphism |
| `gem-*` | Per-gem accent shadows |

### 3.6 Animations

#### Tailwind Keyframes

| Name | Duration | Easing | Usage |
|------|----------|--------|-------|
| `fade-in-up` | 0.4s | ease-out | List items, cards |
| `gradient` | 8s | linear infinite | Gradient backgrounds |
| `shimmer` | 2s | linear infinite | Skeleton loading |
| `float` | 3s | ease-in-out infinite | Decorative elements |
| `slide-up` | 0.6s | cubic-bezier | Modals, drawers |
| `scale-in` | 0.4s | cubic-bezier | Badges, tooltips |
| `slide-in-right` | 0.3s | ease-out | Side panels |
| `bounce-gentle` | 2s | ease-in-out infinite | Scroll indicator |

#### CSS Stagger System

Classes `.stagger-1` through `.stagger-5` with 50ms increments for list entrance animations.

#### Reduced Motion

Full `prefers-reduced-motion` support that disables all animations/transitions.

### 3.7 Glassmorphism (STORY-174)

| Token | Light | Dark |
|-------|-------|------|
| `--glass-bg` | `rgba(255,255,255,0.7)` | `rgba(26,29,34,0.7)` |
| `--glass-border` | `rgba(255,255,255,0.18)` | `rgba(255,255,255,0.12)` |
| `--glass-shadow` | `0 8px 32px rgba(31,38,135,0.07)` | `0 8px 32px rgba(0,0,0,0.3)` |

### 3.8 Icon System

Two icon systems are used:

1. **Inline SVG** (primary) -- Heroicons outline 24x24 for navigation, buttons, status indicators. Defined inline in components (Sidebar, BottomNav, LicitacaoCard).
2. **Lucide React** (landing page only) -- Used in HeroSection for decorative icons (Zap, Target, Globe, ChevronDown).

**Debt Note:** Icons are duplicated across Sidebar and BottomNav as separate inline SVG objects. No shared icon component library exists.

---

## 4. Page Inventory

### 4.1 Route Organization

```
frontend/app/
  layout.tsx              # Root layout (providers, navigation shell)
  page.tsx                # Landing page (/)
  globals.css             # Global styles + design tokens
  error.tsx               # Error boundary
  global-error.tsx        # Root error boundary (Sentry)
  not-found.tsx           # 404 page
  types.ts                # Shared type definitions
  api-types.generated.ts  # OpenAPI-generated types
  sitemap.ts              # Dynamic sitemap generation
  icon.png                # Favicon source

  (protected)/
    layout.tsx            # Auth guard + AppHeader + Breadcrumbs

  # Protected Pages (require auth):
  buscar/                 # Main search page
  dashboard/              # Analytics dashboard
  pipeline/               # Opportunity pipeline (Kanban)
  historico/              # Search history
  mensagens/              # Support messaging
  conta/                  # Account settings
  admin/                  # Admin panel
  admin/cache/            # Cache management
  onboarding/             # 3-step wizard

  # Public Pages (no auth):
  login/                  # Login with layout
  signup/                 # Registration with layout
  auth/callback/          # OAuth callback handler
  recuperar-senha/        # Password recovery
  redefinir-senha/        # Password reset
  planos/                 # Pricing page
  planos/obrigado/        # Thank-you (post-checkout)
  pricing/                # Marketing pricing
  features/               # Feature showcase
  ajuda/                  # Help center / FAQ
  termos/                 # Terms of service
  privacidade/            # Privacy policy
  sobre/                  # About / Methodology
  blog/                   # Blog listing
  blog/[slug]/            # Blog article (dynamic)

  # SEO Content Pages:
  como-avaliar-licitacao/
  como-evitar-prejuizo-licitacao/
  como-filtrar-editais/
  como-priorizar-oportunidades/
```

### 4.2 Detailed Page Inventory

| Route | Type | Auth | Layout | Key Components | Data Fetching |
|-------|------|------|--------|----------------|---------------|
| `/` | Landing | Public | None (own navbar) | 14 landing components, Footer | SSR (static) |
| `/login` | Auth | Public | Own layout | InstitutionalSidebar, AuthProvider | CSR |
| `/signup` | Auth | Public | Own layout | InstitutionalSidebar, AuthProvider | CSR |
| `/auth/callback` | Auth | Public | None | OAuth handler | CSR |
| `/recuperar-senha` | Auth | Public | None | Form | CSR |
| `/redefinir-senha` | Auth | Public | None | Form | CSR |
| `/onboarding` | Wizard | Protected | (protected) | 3-step wizard, RegionSelector | CSR |
| `/buscar` | Search | Protected | (protected) | SearchForm, SearchResults, 30 sub-components | CSR + SSE |
| `/dashboard` | Analytics | Protected | (protected) | Recharts (Bar, Line, Pie), ProfileCompletion | CSR + fetch |
| `/pipeline` | Kanban | Protected | (protected) | DndContext, PipelineColumn, PipelineCard | CSR + fetch |
| `/historico` | History | Protected | (protected) | Search session list, status badges | CSR + fetch |
| `/mensagens` | Messaging | Protected | (protected) | Conversation list/detail, reply form | CSR + fetch |
| `/conta` | Settings | Protected | (protected) | Profile editor, subscription management | CSR + fetch |
| `/admin` | Admin | Protected | (protected) | User table, plan management | CSR + fetch |
| `/admin/cache` | Admin | Protected | (protected) | Cache statistics | CSR + fetch |
| `/planos` | Pricing | Public | Own layout | PlanToggle, PlanCard, FAQ accordion | CSR + fetch |
| `/planos/obrigado` | Thank-you | Public | Planos layout | Confirmation message | CSR |
| `/pricing` | Marketing | Public | None | Feature comparison | SSR (static) |
| `/features` | Marketing | Public | None | Transformation narratives | SSR (static) |
| `/ajuda` | Help | Public | None | FAQ accordion, search | CSR |
| `/termos` | Legal | Public | None | Static content | SSR (static) |
| `/privacidade` | Legal | Public | None | Static content | SSR (static) |
| `/sobre` | About | Public | None | Methodology, Schema.org JSON-LD | SSR (static) |
| `/blog` | Blog | Public | None | Article grid, category filters | SSR (static) |
| `/blog/[slug]` | Article | Public | None | BlogArticleLayout, ContentPageLayout | SSR (static) |
| `/como-avaliar-licitacao` | SEO | Public | None | Content article | SSR (static) |
| `/como-evitar-prejuizo-licitacao` | SEO | Public | None | Content article | SSR (static) |
| `/como-filtrar-editais` | SEO | Public | None | Content article | SSR (static) |
| `/como-priorizar-oportunidades` | SEO | Public | None | Content article | SSR (static) |

### 4.3 Layout Hierarchy

```
RootLayout (app/layout.tsx)
  |-- GoogleAnalytics (head)
  |-- StructuredData (head)
  |-- Theme flash prevention script (head)
  |-- Skip-to-content link
  |-- AnalyticsProvider
  |   |-- AuthProvider
  |       |-- ThemeProvider
  |           |-- NProgressProvider
  |               |-- BackendStatusProvider
  |                   |-- SessionExpiredBanner
  |                   |-- PaymentFailedBanner
  |                   |-- NavigationShell (conditional)
  |                   |   |-- Sidebar (desktop, lg+)
  |                   |   |-- children
  |                   |   |-- BottomNav (mobile, <lg)
  |                   |-- Toaster (sonner, bottom-center)
  |                   |-- CookieConsentBanner

ProtectedLayout (app/(protected)/layout.tsx)
  |-- Auth guard (redirect to / if no session)
  |-- Onboarding redirect check
  |-- AppHeader
  |-- Breadcrumbs
  |-- children (max-w-7xl)
```

### 4.4 Server vs Client Components

| Pattern | Usage |
|---------|-------|
| `"use client"` | All pages except `/features`, `/sobre`, `/blog`, SEO content pages |
| Server Components | Features page, About page, Blog listing, Blog articles, SEO content |
| Suspense boundaries | Login (for `useSearchParams`), Buscar page |

**Debt Note:** All protected pages are fully client-rendered. No server component data fetching is used for authenticated pages, meaning every data load requires a client-side `fetch()` after hydration.

---

## 5. Component Inventory

### 5.1 Search Components (`app/buscar/components/`)

30 components dedicated to the search experience:

| Component | Purpose | Props Complexity | Reusable |
|-----------|---------|-----------------|----------|
| `SearchForm` | Main search form with UF selection, date range, sector, terms | Very High (40+ props) | No |
| `SearchResults` | Results container with loading, error, empty states | Very High (30+ props) | No |
| `FilterPanel` | Advanced filter controls (esfera, municipio, modalidade, valor) | High (14 props) | No |
| `UfProgressGrid` | Real-time UF fetch progress indicator | Medium | No |
| `CacheBanner` | Indicates cached results | Low | Yes |
| `DegradationBanner` | Shows partial/degraded data warning | Medium | Yes |
| `DataQualityBanner` | Unified data quality indicator | Medium | No |
| `ErrorDetail` | Detailed error display with retry | Medium | Yes |
| `ExpiredCacheBanner` | Expired cache warning | Low | Yes |
| `FeedbackButtons` | Thumbs up/down per bid result | Medium | Yes |
| `FilterRelaxedBanner` | Indicates filter relaxation | Low | Yes |
| `FilterStatsBreakdown` | Filter rejection reasons | Low | No |
| `FreshnessIndicator` | Cache freshness badge | Low | Yes |
| `LlmSourceBadge` | LLM vs fallback summary indicator | Low | Yes |
| `OperationalStateBanner` | System operational state | Low | Yes |
| `PartialResultsPrompt` | Prompt to accept partial results | Medium | No |
| `PartialTimeoutBanner` | Timeout partial results warning | Low | Yes |
| `RefreshBanner` | Stale data refresh prompt | Medium | No |
| `ReliabilityBadge` | Data reliability indicator | Low | Yes |
| `SearchErrorBanner` | Error banner for search | Medium | Yes |
| `SearchErrorBoundary` | React error boundary for search | Low | Yes |
| `SourcesUnavailable` | All sources down indicator | Low | Yes |
| `TruncationWarningBanner` | Results truncated warning | Low | Yes |
| `UfFailureDetail` | Per-UF failure details | Low | No |
| `ViabilityBadge` | Viability score badge (alta/media/baixa) | Medium | Yes |
| `ZeroResultsSuggestions` | Suggestions when no results | Low | No |
| `ActionLabel` | Action label component | Low | Yes |
| `CompatibilityBadge` | Compatibility percentage badge | Low | Yes |
| `CoverageBar` | Coverage percentage bar | Low | Yes |
| `DeepAnalysisModal` | On-demand deep bid analysis modal | High | No |

### 5.2 App Components (`app/components/`)

48 components for general app functionality:

| Component | Purpose | Reusable |
|-----------|---------|----------|
| **Auth and Session** | | |
| `AuthProvider` | Auth context (Supabase), session management | Core |
| `ThemeProvider` | Light/dark/system theme context | Core |
| `AnalyticsProvider` | Mixpanel analytics context | Core |
| `NProgressProvider` | Page transition progress bar | Core |
| `GoogleAnalytics` | GA4 script injection | Core |
| `StructuredData` | Schema.org JSON-LD | Core |
| `CookieConsentBanner` | LGPD/GDPR cookie consent | Core |
| `SessionExpiredBanner` | Session expired notification | Core |
| **Navigation** | | |
| `AppHeader` | Protected page header (logo, ThemeToggle, UserMenu) | Yes |
| `Breadcrumbs` | Auto-generated breadcrumbs | Yes |
| `ThemeToggle` | Theme switcher (light/system/dark) | Yes |
| `UserMenu` | User dropdown menu | Yes |
| `InstitutionalSidebar` | Auth page decorative sidebar | No |
| **Search Enhancement** | | |
| `SavedSearchesDropdown` | Load saved search configurations | No |
| `QuotaBadge` | Quota usage indicator | Yes |
| `QuotaCounter` | Quota remaining counter | Yes |
| `PlanBadge` | Current plan indicator | Yes |
| `AddToPipelineButton` | Add bid to pipeline from results | Yes |
| `LicitacaoCard` | Individual bid result card | Yes |
| `LicitacoesPreview` | Compact bid preview list | Yes |
| `LoadingResultsSkeleton` | Skeleton loading for results | Yes |
| `OrdenacaoSelect` | Sort order selector | Yes |
| `RegionSelector` | Region/UF multi-selector | Yes |
| `CustomSelect` | Custom styled select | Yes |
| `CustomDateInput` | Custom date input | Yes |
| `StatusBadge` | Bid status badge | Yes |
| `Countdown` | Countdown to bid deadline | Yes |
| `MessageBadge` | Unread message count badge | Yes |
| **Filters** | | |
| `EsferaFilter` | Government sphere filter | Yes |
| `MunicipioFilter` | Municipality filter | Yes |
| `ModalidadeFilter` (top-level) | Procurement modality filter | Yes |
| `StatusFilter` (top-level) | Bid status filter | Yes |
| `ValorFilter` (top-level) | Value range filter | Yes |
| `PaginacaoSelect` | Page size selector | Yes |
| `OrgaoFilter` | Organ filter | Yes |
| **Trial/Billing** | | |
| `UpgradeModal` | Plan upgrade prompt modal | No |
| `TrialConversionScreen` | Trial expiration conversion | No |
| `TrialExpiringBanner` | Trial expiring warning | Yes |
| `TrialCountdown` | Trial days remaining | Yes |
| `Dialog` | Generic dialog/modal component | Yes |
| **SEO/Marketing** | | |
| `Footer` | Site footer | Yes |
| `ComparisonTable` | SmartLic vs alternatives | No |
| `ValuePropSection` | Value proposition section | No |
| `BlogArticleLayout` | Blog article page layout | Yes |
| `ContentPageLayout` | SEO content page layout | Yes |
| `EmptyState` | Generic empty state | Yes |
| `LoadingProgress` | Basic loading progress | Yes |
| `ContextualTutorialTooltip` | Shepherd.js tutorial tooltip | Yes |

### 5.3 Landing Components (`app/components/landing/`)

13 components for the landing page:

| Component | Purpose | Key Libraries |
|-----------|---------|---------------|
| `LandingNavbar` | Public navigation bar | -- |
| `HeroSection` | Hero with gradient text, CTAs | Framer Motion, Lucide |
| `ProofOfValue` | Value proof section | Framer Motion |
| `AnalysisExamplesCarousel` | Analysis examples carousel | Framer Motion |
| `OpportunityCost` | Cost of inaction section | -- |
| `BeforeAfter` | Before/after comparison | -- |
| `DifferentialsGrid` | Feature differentials grid | -- |
| `HowItWorks` | How it works steps | -- |
| `StatsSection` | Platform statistics | -- |
| `DataSourcesSection` | Data sources explanation | -- |
| `SectorsGrid` | 15 sectors display grid | -- |
| `TrustCriteria` | Trust/credibility signals | -- |
| `FinalCTA` | Final call-to-action section | -- |

### 5.4 UI Components (`app/components/ui/`)

6 low-level reusable UI primitives:

| Component | Purpose |
|-----------|---------|
| `BentoGrid` | Grid layout for feature cards |
| `CategoryBadge` | Category label badge |
| `GlassCard` | Glassmorphism card |
| `GradientButton` | Gradient CTA button |
| `ScoreBar` | Score progress bar |
| `Tooltip` | Tooltip popover |

### 5.5 Top-Level Components (`components/`)

21 components at the top-level `components/` directory:

| Component | Purpose |
|-----------|---------|
| `NavigationShell` | Conditional sidebar/bottom-nav wrapper |
| `Sidebar` | Desktop sidebar navigation |
| `BottomNav` | Mobile bottom navigation |
| `MobileDrawer` | Mobile drawer overlay |
| `PageHeader` | Page title + description header |
| `EmptyState` | Generic empty state (separate from app/components) |
| `ErrorStateWithRetry` | Error display with retry button |
| `AuthLoadingScreen` | Full-screen auth loading |
| `EnhancedLoadingProgress` | 5-stage search loading with SSE |
| `LoadingProgress` | Basic loading indicator |
| `BackendStatusIndicator` | Backend health status display |
| `GoogleSheetsExportButton` | Google Sheets export |
| `ProfileCompletionPrompt` | Profile completion nudge |
| `ProfileProgressBar` | Profile completion progress |
| `ProfileCongratulations` | Profile complete celebration |
| `ModalidadeFilter` | Procurement modality filter |
| `StatusFilter` | Bid status filter |
| `ValorFilter` | Value range filter |

### 5.6 Subscription Components (`components/subscriptions/`)

7 components for subscription/billing UI:

| Component | Purpose |
|-----------|---------|
| `PlanCard` | Plan feature card |
| `PlanToggle` | Monthly/semiannual/annual toggle |
| `DowngradeModal` | Plan downgrade confirmation |
| `FeatureBadge` | Feature availability badge |
| `AnnualBenefits` | Annual plan benefits display |
| `TrustSignals` | Payment trust signals |

### 5.7 Pipeline Components (`app/pipeline/`)

4 components for the Kanban pipeline:

| Component | Purpose |
|-----------|---------|
| `PipelineColumn` | Kanban column container |
| `PipelineCard` | Draggable pipeline item card |
| `PipelineMobileTabs` | Mobile tab-based pipeline view |
| `types.ts` | Pipeline stage definitions |

### 5.8 Account and Billing Components

| Path | Component | Purpose |
|------|-----------|---------|
| `components/account/CancelSubscriptionModal` | Subscription cancellation flow |
| `components/billing/PaymentFailedBanner` | Payment failure notification |
| `components/layout/MobileMenu` | Mobile menu component |

---

## 6. Custom Hooks

### 6.1 Global Hooks (`hooks/`)

| Hook | Purpose | Dependencies |
|------|---------|-------------|
| `useAnalytics` | Mixpanel event tracking, UTM params | mixpanel-browser |
| `useFeatureFlags` | Feature flag evaluation | Backend API |
| `useFetchWithBackoff` | Fetch with exponential backoff retry | -- |
| `useIsMobile` | Media query for mobile detection | window.matchMedia |
| `useKeyboardShortcuts` | Keyboard shortcut registration | -- |
| `useNavigationGuard` | Prevent navigation during search | Next.js router |
| `useOnboarding` | Shepherd.js tour management | shepherd.js |
| `usePipeline` | Pipeline CRUD operations | Backend API |
| `usePlan` | Current plan info + capabilities | Backend API, localStorage |
| `useQuota` | Quota usage tracking | Backend API |
| `useSavedSearches` | Save/load search configurations | localStorage |
| `useSearchPolling` | Polling-based search status check | Backend API |
| `useSearchProgress` | SSE progress event types | -- |
| `useSearchSSE` | Server-Sent Events for search progress | EventSource API |
| `useServiceWorker` | Service worker registration | navigator.serviceWorker |
| `useUnreadCount` | Unread message count polling | Backend API |

### 6.2 Buscar-Specific Hooks (`app/buscar/hooks/`)

| Hook | Purpose | Complexity |
|------|---------|-----------|
| `useSearch` | Core search orchestration (submit, cancel, SSE, results) | Very High |
| `useSearchFilters` | Filter state management (UFs, dates, sectors, terms) | High |
| `useUfProgress` | Per-UF fetch progress tracking from SSE events | Medium |

### 6.3 Page-Level Hook (`app/hooks/`)

| Hook | Purpose |
|------|---------|
| `useInView` | Intersection Observer for viewport detection |

---

## 7. API Integration

### 7.1 API Proxy Routes (`app/api/`)

All backend API calls are proxied through Next.js route handlers for auth token refresh and error sanitization.

| Route | Methods | Backend Endpoint | Purpose |
|-------|---------|-----------------|---------|
| `/api/buscar` | POST | `/v1/buscar` | Search execution |
| `/api/buscar-progress` | GET (SSE) | `/v1/buscar-progress/{id}` | Real-time search progress |
| `/api/buscar-results/[searchId]` | GET | `/v1/search/{id}/status` | Async search result retrieval |
| `/api/search-status` | GET | `/v1/search/{id}/status` | Search status polling |
| `/api/search-history` | GET | `/v1/sessions` | Search session history |
| `/api/download` | GET | `/v1/download` | Excel file download |
| `/api/setores` | GET | `/v1/setores` | Sector list |
| `/api/analytics` | GET | `/v1/analytics/*` | Dashboard analytics |
| `/api/pipeline` | GET, POST, PATCH, DELETE | `/v1/pipeline` | Pipeline CRUD |
| `/api/feedback` | POST | `/v1/feedback` | Result feedback |
| `/api/me` | GET | `/v1/me` | User profile |
| `/api/me/export` | GET | `/v1/me/export` | Data export |
| `/api/trial-status` | GET | `/v1/trial-status` | Trial info |
| `/api/subscription-status` | GET | `/v1/subscription/status` | Subscription info |
| `/api/subscriptions/cancel` | POST | `/v1/subscriptions/cancel` | Cancel subscription |
| `/api/billing-portal` | POST | `/v1/billing-portal` | Stripe portal |
| `/api/first-analysis` | POST | `/v1/first-analysis` | Onboarding analysis |
| `/api/health` | GET | `/v1/health/cache` | Backend health |
| `/api/sessions` | GET | `/v1/sessions` | Search sessions |
| `/api/profile-completeness` | GET | `/v1/profile/completeness` | Profile completion |
| `/api/profile-context` | GET, PUT | `/v1/profile/context` | User profile context |
| `/api/change-password` | POST | `/v1/change-password` | Password change |
| `/api/messages/conversations` | GET, POST | `/v1/conversations` | Messaging |
| `/api/messages/conversations/[id]` | GET | `/v1/conversations/{id}` | Conversation detail |
| `/api/messages/conversations/[id]/reply` | POST | `/v1/conversations/{id}/reply` | Send reply |
| `/api/messages/conversations/[id]/status` | PATCH | `/v1/conversations/{id}/status` | Update status |
| `/api/messages/unread-count` | GET | `/v1/conversations/unread` | Unread count |
| `/api/export/google-sheets` | POST | `/v1/export/google-sheets` | Google Sheets export |
| `/api/bid-analysis/[bidId]` | GET | `/v1/bid-analysis/{bidId}` | Deep bid analysis |
| `/api/auth/login` | POST | Supabase Auth | Email login |
| `/api/auth/signup` | POST | Supabase Auth | Registration |
| `/api/auth/check-email` | POST | `/v1/auth/check-email` | Email validation |
| `/api/auth/check-phone` | POST | `/v1/auth/check-phone` | Phone validation |
| `/api/auth/resend-confirmation` | POST | Supabase Auth | Resend confirmation |
| `/api/auth/status` | GET | Supabase Auth | Auth status |
| `/api/admin/[...path]` | All | `/v1/admin/*` | Admin catch-all proxy |

### 7.2 Data Fetching Patterns

| Pattern | Usage | Example |
|---------|-------|---------|
| Client-side fetch with auth header | Protected data | Dashboard analytics, pipeline items |
| SSE (EventSource) | Real-time search progress | `useSearchSSE` hook |
| Polling | Search status, unread count | `useSearchPolling`, `useUnreadCount` |
| `useFetchWithBackoff` | Resilient data loading | Dashboard, pipeline |
| localStorage cache | Plan info, search config, feedback | `usePlan`, `useSavedSearches` |

### 7.3 Error Handling in API Calls

- `proxy-error-handler.ts`: Sanitizes backend errors for user-facing display
- `error-messages.ts`: Maps error codes to Portuguese user-friendly messages, categorizes auth errors
- `getUserFriendlyError()`: Universal error-to-message function
- `translateAuthError()`: Supabase auth error translation
- Contextual error messages based on HTTP status (429, 500, 502, 503, 524)
- Sentry integration for error capture

### 7.4 SSE Implementation

```
Frontend (buscar/page.tsx)
  |
  |-- POST /api/buscar (with search_id)
  |       |-- Proxies to backend POST /v1/buscar
  |       |-- Returns BuscaResult JSON
  |
  |-- GET /api/buscar-progress?search_id=xxx (SSE stream)
  |       |-- Proxies to backend GET /v1/buscar-progress/{id}
  |       |-- Events: fetching, filtering, llm, uf_progress,
  |       |           degraded, llm_ready, excel_ready, done
  |       |-- Uses undici with bodyTimeout: 0 for long streams
  |       |-- Retry on BodyTimeoutError (max 1 retry)
  |
  |-- useSearchSSE hook manages EventSource lifecycle
  |-- useSearchProgress normalizes SSE events
  |-- useUfProgress tracks per-UF progress
  |-- Graceful fallback: if SSE fails, time-based simulation
```

---

## 8. User Flows

### 8.1 Search Flow (Primary)

```
[User lands on /buscar]
        |
        v
[Auth check] ---> No session ---> [Redirect to /]
        |
        v (authenticated)
[Onboarding check] ---> Not completed ---> [Redirect to /onboarding]
        |
        v (onboarded)
[Search Form displayed]
  |-- Select sector (dropdown) or enter custom terms
  |-- Select UFs (region selector, multi-select)
  |-- Set date range (default: last 10 days)
  |-- Optional: Advanced filters (esfera, municipio, modalidade, valor)
  |-- Click "Buscar"
        |
        v
[Validation] ---> Errors ---> [Show inline validation messages]
        |
        v (valid)
[Generate search_id (UUID)]
  |-- Start SSE connection (GET /api/buscar-progress?search_id=xxx)
  |-- POST /api/buscar with search params + search_id
        |
        v
[Loading State]
  |-- EnhancedLoadingProgress (5 stages)
  |-- UfProgressGrid (per-UF real-time progress)
  |-- Cancel button available
  |-- SSE events update progress in real-time
  |-- Fallback: time-based simulation if SSE fails
        |
        v
[Results Received]
  |-- Summary card (AI or fallback)
  |-- Results list with LicitacaoCard components
  |   |-- ViabilityBadge (alta/media/baixa)
  |   |-- ReliabilityBadge
  |   |-- FeedbackButtons (thumbs up/down)
  |   |-- AddToPipelineButton
  |   |-- DeepAnalysisModal (on-demand)
  |-- Filter stats breakdown
  |-- Download Excel button
  |-- Google Sheets export
  |-- Sort order selector
        |
        v
[Banners (conditional)]
  |-- CacheBanner (if cached results)
  |-- DegradationBanner (if partial data)
  |-- PartialResultsPrompt (if some sources failed)
  |-- FilterRelaxedBanner (if filters were relaxed)
  |-- TruncationWarningBanner (if results truncated)
  |-- RefreshBanner (if background refresh available)
```

### 8.2 Authentication Flow

```
[User visits /login]
        |
        v
[Login Form]
  |-- Email + Password mode (default)
  |-- Magic Link mode (toggle)
  |-- Google OAuth button
  |-- "Esqueceu senha?" link ---> /recuperar-senha
  |-- "Criar conta" link ---> /signup
        |
        v (submit)
[Supabase Auth]
  |-- Success ---> Redirect to /buscar
  |-- Error ---> Show translated error message
  |-- Google OAuth ---> Redirect to Supabase OAuth flow
        |               |-- Callback: /auth/callback
        |               |-- Success: Redirect to /buscar
        |               |-- Error: Redirect to /login?error=xxx
        |
[Signup Flow]
  |-- Full name + Email + Password + Phone
  |-- Email validation (disposable check)
  |-- Phone validation (duplicate check)
  |-- Submit ---> Confirmation email sent
  |-- Confirmation screen with countdown
  |-- Resend confirmation option
```

### 8.3 Onboarding Flow

```
[User redirected to /onboarding (first login)]
        |
        v
[Step 1: CNAE Selection]
  |-- CNAE code input with autocomplete
  |-- Objective selection
  |-- Value range presets (R$50k - R$5M)
        |
        v
[Step 2: UF Selection]
  |-- Region-based UF selector
  |-- Multi-select with "select all" / "clear"
        |
        v
[Step 3: Confirmation]
  |-- Review selections
  |-- Submit profile context
  |-- Auto-trigger first search (/first-analysis)
  |-- Redirect to /buscar with onboarding results
```

### 8.4 Pipeline Flow

```
[User visits /pipeline]
        |
        v
[Kanban Board]
  |-- Columns: Descoberta -> Analise -> Proposta -> Acompanhamento -> Finalizada
  |-- Cards loaded from backend
  |-- Desktop: Drag-and-drop between columns (@dnd-kit)
  |-- Mobile: Tab-based view (PipelineMobileTabs)
        |
        v
[Card Actions]
  |-- Drag to new column ---> PATCH /api/pipeline (update stage)
  |-- Click card ---> View details
  |-- Delete card ---> DELETE /api/pipeline
  |-- Add from search results ---> AddToPipelineButton
        |
        v
[Trial Expired]
  |-- Read-only mode (no drag-and-drop)
  |-- Upgrade prompt
```

### 8.5 Billing Flow

```
[User visits /planos]
        |
        v
[Pricing Page]
  |-- PlanToggle: Monthly / Semiannual / Annual
  |-- Single plan: SmartLic Pro
  |-- Feature list (all enabled)
  |-- FAQ accordion
        |
        v
[Click "Assinar"]
  |-- POST /api/billing-portal or Stripe Checkout
  |-- Redirect to Stripe
  |-- Success: Redirect to /planos/obrigado
  |-- Cancel: Return to /planos
        |
        v
[Subscription Management]
  |-- /conta page: Current plan display
  |-- Billing portal button
  |-- Cancel subscription modal
  |-- PaymentFailedBanner (if payment failed)
```

---

## 9. Responsiveness

### 9.1 Breakpoint Strategy

Uses Tailwind's default breakpoints:

| Breakpoint | Min Width | Usage |
|-----------|-----------|-------|
| `sm` | 640px | Mobile landscape |
| `md` | 768px | Tablet |
| `lg` | 1024px | Desktop (navigation switch point) |
| `xl` | 1280px | Wide desktop |
| `2xl` | 1536px | Ultra-wide |

**Key Breakpoint: `lg` (1024px)** -- Navigation switches between:
- Desktop: Sidebar (left rail, collapsible)
- Mobile: BottomNav (fixed bottom bar with drawer)

### 9.2 Mobile-Specific Adaptations

| Feature | Desktop | Mobile |
|---------|---------|--------|
| Navigation | Sidebar (collapsible) | BottomNav + drawer |
| Pipeline | Kanban columns (drag-and-drop) | Tab-based view |
| Search form | Full width | Stacked, full-screen UF selector |
| Date picker | Native date input | React Day Picker calendar (44px cells) |
| Pull-to-refresh | Disabled (pointer-events: none) | Enabled with native-like feel |
| Touch targets | Standard | Minimum 44px (WCAG 2.5.8) |
| Results | Multi-column layout | Single column, stacked cards |

### 9.3 Viewport Configuration

```typescript
export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
};
```

### 9.4 Max Width Constraints

| Area | Max Width |
|------|-----------|
| Landing page | 1200px (`max-w-landing`) |
| Protected pages | 1280px (`max-w-7xl`) |
| Content pages | Variable (per section) |

---

## 10. Accessibility (a11y)

### 10.1 WCAG Compliance Status

| Criterion | Level | Status | Notes |
|-----------|-------|--------|-------|
| 1.1.1 Non-text Content | A | Partial | SVG icons have `aria-hidden="true"`, some missing `alt` |
| 1.4.3 Contrast (Minimum) | AA | Pass | All text colors documented with contrast ratios |
| 1.4.6 Enhanced Contrast | AAA | Partial | Primary text meets AAA, secondary meets AA |
| 2.1.1 Keyboard | A | Partial | Navigation and forms keyboard accessible |
| 2.4.1 Bypass Blocks | A | Pass | Skip-to-content link present |
| 2.4.7 Focus Visible | AA | Pass | 3px ring, WCAG 2.2 AAA compliant |
| 2.5.8 Target Size | AAA | Pass | All buttons minimum 44px |
| 3.1.1 Language | A | Pass | `lang="pt-BR"` |
| 4.1.2 Name, Role, Value | A | Partial | Many `aria-label` attributes, some gaps |

### 10.2 Implemented a11y Features

- **Skip-to-content link**: `<a href="#main-content" className="sr-only focus:not-sr-only">` in root layout
- **Focus indicators**: 3px solid ring with 2px offset (WCAG 2.2 Level AAA)
- **Touch targets**: Minimum 44px height on all buttons and inputs
- **Reduced motion**: `@media (prefers-reduced-motion: reduce)` disables all animations
- **Color contrast**: All text tokens documented with WCAG contrast ratios
- **ARIA labels**: Used on badges (ViabilityBadge, StatusBadge), navigation, buttons
- **Semantic HTML**: `<nav>`, `<main>`, `<section>` used appropriately
- **Dark mode**: Separate contrast verification for dark theme tokens
- **Focus ring in Shepherd.js**: Custom focus states for onboarding tour
- **Keyboard navigation**: @dnd-kit `KeyboardSensor` for pipeline, keyboard shortcut system

### 10.3 a11y Gaps

| Issue | Severity | Location |
|-------|----------|----------|
| Inline SVG icons inconsistently labeled | Medium | Sidebar, BottomNav, LicitacaoCard |
| Some icons have both `aria-hidden` and `role="img"` | Low | LicitacaoCard icon components |
| Date picker calendar may lack screen reader announcements | Medium | react-day-picker integration |
| Dropdown menus (feedback, filter) lack `role="menu"` | Medium | FeedbackButtons, FilterPanel |
| Toast notifications may not be announced | Medium | sonner Toaster |
| BottomNav drawer lacks focus trap | High | BottomNav drawer overlay |
| 404 page missing accented characters | Low | `not-found.tsx` |

---

## 11. Performance

### 11.1 Bundle Analysis

#### Production Dependencies (24 packages)

| Package | Est. Size (gzip) | Category |
|---------|----------|----------|
| `next` | ~90KB (framework, shared) | Core |
| `react` + `react-dom` | ~45KB | Core |
| `framer-motion` | ~30KB | Animation |
| `recharts` | ~40KB | Charts |
| `@dnd-kit/*` | ~15KB | Drag-and-drop |
| `@supabase/*` | ~20KB | Auth |
| `@sentry/nextjs` | ~30KB | Monitoring |
| `shepherd.js` | ~25KB | Onboarding |
| `lucide-react` | ~5KB (tree-shaken) | Icons |
| `date-fns` | ~8KB (tree-shaken) | Dates |
| `sonner` | ~5KB | Toasts |
| `mixpanel-browser` | ~15KB | Analytics |
| Others | ~10KB | Utilities |

**Estimated total client JS: ~340KB gzip** (approximate, depends on code splitting)

### 11.2 Code Splitting

| Strategy | Implementation |
|----------|---------------|
| Route-based splitting | Next.js automatic per-page code splitting |
| `output: 'standalone'` | Optimized production build |
| Dynamic imports | Not widely used (potential optimization) |
| `Suspense` boundaries | Used for search params parsing |

### 11.3 Image Optimization

- Next.js `<Image>` component used for optimized loading
- Remote pattern allowed: `static.wixstatic.com/media/**`
- Favicon: `/favicon.ico` (PNG source: `icon.png`)
- No CDN-based image optimization beyond Next.js built-in

### 11.4 SSR vs CSR Distribution

| Type | Pages | Percentage |
|------|-------|------------|
| Fully Client-Rendered (`"use client"`) | 21 | 72% |
| Server Components (static) | 8 | 28% |
| Hybrid (server + client) | 0 | 0% |

### 11.5 Caching Strategy

- **Build ID**: Unique per deploy (`timestamp-random`) for cache invalidation
- **localStorage caching**: Plan info (1hr TTL), saved searches, feedback state, theme preference
- **No `unstable_cache` or `revalidate`**: Server data fetching not used for protected pages
- **Sitemap**: Generated at build time via `next-sitemap`

### 11.6 Font Loading

All three fonts use `display: "swap"` for FOUT (Flash of Unstyled Text) over FOIT (Flash of Invisible Text).

### 11.7 Third-Party Scripts

| Script | Loading | Impact |
|--------|---------|--------|
| Google Analytics 4 | Head (with consent) | Medium |
| Mixpanel | Dynamic (AnalyticsProvider) | Medium |
| Stripe.js | CSP-allowed, loaded on demand | Low |
| Sentry | Bundled | Medium |

---

## 12. Testing

### 12.1 Unit Tests (Jest + Testing Library)

| Metric | Value |
|--------|-------|
| Test files | 135 |
| Passing tests | 2681+ |
| Coverage threshold | 50-55% (branches/functions/lines/statements) |
| Target threshold | 60% |
| Environment | jsdom |
| Transform | @swc/jest |
| Runner | jest-junit (CI) |

**Polyfills in `jest.setup.js`:**
- `crypto.randomUUID` (jsdom lacks it)
- `EventSource` (jsdom lacks SSE support)

**Path aliases:**
- `@/` maps to `app/`
- `@/components/` maps to `app/components/`
- `@/lib/` maps to `lib/`

### 12.2 E2E Tests (Playwright)

| Metric | Value |
|--------|-------|
| Test files | 60 critical flows |
| Browsers | Chromium Desktop (1280x720) + Mobile Safari (iPhone 13) |
| Timeout | 60s per test |
| Retries | 2 (CI only) |
| Artifacts | Screenshots on failure, video on retry, traces on retry |
| Reporter | HTML + list + JUnit (CI) |

### 12.3 Accessibility Testing

| Tool | Integration |
|------|------------|
| `@axe-core/playwright` | E2E accessibility checks |
| `@lhci/cli` | Lighthouse CI (performance + a11y audits) |

### 12.4 Quarantine System

Flaky tests are moved to `__tests__/quarantine/` and run separately via `npm run test:quarantine` with `--passWithNoTests`.

---

## 13. Security

### 13.1 Security Headers (next.config.js)

| Header | Value |
|--------|-------|
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `DENY` |
| `X-XSS-Protection` | `1; mode=block` |
| `Referrer-Policy` | `strict-origin-when-cross-origin` |
| `Permissions-Policy` | `camera=(), microphone=(), geolocation=()` |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` |
| `Content-Security-Policy` | Strict CSP with allow-list |

### 13.2 CSP Directives

| Directive | Allowed Sources |
|-----------|----------------|
| `default-src` | `'self'` |
| `script-src` | `'self' 'unsafe-inline' 'unsafe-eval'` + Stripe + Cloudflare |
| `style-src` | `'self' 'unsafe-inline'` |
| `connect-src` | `'self'` + Supabase + Stripe + Railway + Sentry + SmartLic + Mixpanel |
| `frame-src` | `'self'` + Stripe |
| `img-src` | `'self' data: https: blob:` |
| `font-src` | `'self' data:` |
| `object-src` | `'none'` |
| `base-uri` | `'self'` |

### 13.3 Auth Security

- Server-side token refresh via `getRefreshedToken()` in API proxies
- Auth header forwarding through proxy routes
- Session expiration detection and banner
- OAuth callback handler with error parameter parsing
- Admin role check via backend `/v1/me` endpoint

### 13.4 Source Map Protection

- Source maps hidden from client bundles (`hideSourceMaps: true`)
- Uploaded to Sentry for error debugging
- Sentry tunnel route (`/monitoring`) to bypass ad-blockers

---

## 14. Technical Debt Inventory

### 14.1 Critical Severity

| ID | Area | Description | Impact | Files |
|----|------|-------------|--------|-------|
| D-001 | Component Duplication | `EmptyState` exists in BOTH `app/components/EmptyState.tsx` AND `components/EmptyState.tsx` with slightly different APIs | Confusion, maintenance burden | 2 files |
| D-002 | Component Duplication | `LoadingProgress` exists in BOTH `app/components/LoadingProgress.tsx` AND `components/LoadingProgress.tsx` | Same component duplicated | 2 files |
| D-003 | Prop Drilling | `SearchForm` has 40+ props passed from the buscar page. No intermediate context or state management. | Extremely difficult to maintain, test, or refactor | `buscar/page.tsx`, `SearchForm.tsx` |
| D-004 | No Server Components for Data | All protected pages use `"use client"` with client-side fetch. No RSC data fetching. | Slower initial page load, waterfall requests, no streaming | All protected pages |

### 14.2 High Severity

| ID | Area | Description | Impact | Files |
|----|------|-------------|--------|-------|
| D-005 | Icon Duplication | SVG icons are duplicated as literal JSX objects in `Sidebar.tsx` and `BottomNav.tsx` (identical icons defined twice) | ~200 lines of duplicated SVGs | `Sidebar.tsx`, `BottomNav.tsx` |
| D-006 | Mixed Icon Systems | Landing page uses `lucide-react` while app pages use inline SVGs. No shared icon abstraction. | Inconsistent, larger bundle | Multiple files |
| D-007 | Inline Styles in global-error.tsx | `global-error.tsx` uses inline `style={{}}` objects instead of design system tokens | Falls outside design system, inconsistent look | `global-error.tsx` |
| D-008 | Missing Focus Trap | BottomNav drawer overlay lacks focus trap. Users can Tab out of the drawer. | a11y violation (WCAG 2.4.3) | `BottomNav.tsx` |
| D-009 | UF Constants Duplicated | `ALL_UFS` array is defined independently in `historico/page.tsx`, `conta/page.tsx`, `onboarding/page.tsx`, and `lib/constants/uf-names.ts` | Risk of inconsistency | 4+ files |
| D-010 | Component Directory Split | Components are split across 4 directories (`app/buscar/components/`, `app/components/`, `components/`, `app/components/ui/`) with no clear separation principle | Developer confusion on where to add new components | All component dirs |
| D-011 | ThemeProvider Duplicates CSS Variables | `ThemeProvider.tsx` manually sets CSS variables in JavaScript that are already defined in `globals.css` `:root` and `.dark` selectors | Dual source of truth for theme values, risk of drift | `ThemeProvider.tsx`, `globals.css` |
| D-012 | No State Management Library | Complex state (search, pipeline, auth, plan) is managed through hooks + prop drilling + localStorage. No centralized state management. | Hard to debug cross-component state, prop drilling | Multiple hooks and pages |

### 14.3 Medium Severity

| ID | Area | Description | Impact | Files |
|----|------|-------------|--------|-------|
| D-013 | Missing Type Safety | `AddToPipelineButton` uses `catch (err: any)` | Suppresses TypeScript safety | `AddToPipelineButton.tsx` |
| D-014 | Hardcoded Strings | Portuguese strings are hardcoded throughout (no i18n framework). Constants like `APP_NAME`, error messages duplicated. | Cannot localize, harder to change copy | All pages |
| D-015 | Custom Toast in FeedbackButtons | `FeedbackButtons` implements its own toast with manual `setTimeout` instead of using `sonner` which is already available | Inconsistent toast behavior | `FeedbackButtons.tsx` |
| D-016 | 404 Page Missing Accents | `not-found.tsx` has "Pagina nao encontrada" instead of "Pagina nao encontrada" (missing Portuguese accents) | Poor Portuguese quality | `not-found.tsx` |
| D-017 | Shepherd.js Uses Tailwind @apply in Global CSS | Shepherd theme styles use `@apply` directives in `globals.css` with hardcoded Tailwind classes (`bg-white dark:bg-gray-800`) instead of design system tokens | Bypasses design system | `globals.css` |
| D-018 | No Error Boundary per Page | Only search page has its own error boundary (`SearchErrorBoundary`). Other pages rely on the root `error.tsx`. | Coarse error recovery | Most pages |
| D-019 | Coverage Threshold Below Target | Current coverage thresholds (50-55%) are below the documented target (60%) | Technical debt acknowledged in config | `jest.config.js` |
| D-020 | No `dynamic()` Import Usage | Heavy libraries like Recharts, @dnd-kit, and Shepherd.js are not dynamically imported | Larger initial bundle for pages that don't need them | `dashboard/page.tsx`, `pipeline/page.tsx` |
| D-021 | Fetch Calls Without AbortController | Most page-level `useEffect` fetch calls do not use AbortController for cleanup | Potential memory leaks, race conditions | Multiple pages |
| D-022 | Inconsistent Date Display | Some pages use `date-fns`, others use manual `toLocaleDateString("pt-BR")` | Inconsistent date formatting | Multiple pages |

### 14.4 Low Severity

| ID | Area | Description | Impact | Files |
|----|------|-------------|--------|-------|
| D-023 | Legacy Theme Key Migration | `ThemeProvider` and root layout both have legacy `bidiq-theme` to `smartlic-theme` migration code | Dead code (migration should be complete) | `layout.tsx`, `ThemeProvider.tsx` |
| D-024 | Missing Viewport Meta | `not-found.tsx` does not have viewport configuration (though root layout does) | Minor SSR concern | `not-found.tsx` |
| D-025 | Unused `@types/js-yaml` | `@types/js-yaml` in devDependencies but `js-yaml` only used in one script | Unused dependency | `package.json` |
| D-026 | Mixed Tailwind and CSS Variable Usage | Some components use `bg-white dark:bg-gray-800` (Tailwind defaults) while others use `bg-[var(--surface-0)]` (design tokens) | Inconsistent approach | Shepherd styles, some older components |
| D-027 | Blog Font Override | Blog hero uses inline `style={{ fontFamily: "Georgia, ..." }}` instead of design system font tokens | Bypasses font system | `blog/page.tsx` |
| D-028 | `@types/uuid` in Dependencies | `@types/uuid` is in `dependencies` instead of `devDependencies` | Minor packaging issue | `package.json` |

---

## 15. Remediation Roadmap

### Phase 1: Quick Wins (1-2 sprints)

| Action | Debt IDs | Effort | Impact |
|--------|----------|--------|--------|
| Deduplicate `EmptyState` and `LoadingProgress` | D-001, D-002 | Small | High (reduces confusion) |
| Create shared icon component library | D-005, D-006 | Medium | High (eliminates 200+ duplicate lines) |
| Fix `not-found.tsx` accents | D-016 | Tiny | Low (quality) |
| Replace custom toast in FeedbackButtons with `sonner` | D-015 | Small | Medium (consistency) |
| Move `@types/uuid` to devDependencies | D-028 | Tiny | Low |
| Centralize UF constants | D-009 | Small | Medium (single source of truth) |
| Add focus trap to BottomNav drawer | D-008 | Small | High (a11y fix) |

### Phase 2: Architecture Improvements (3-5 sprints)

| Action | Debt IDs | Effort | Impact |
|--------|----------|--------|--------|
| Extract SearchForm state into a React Context | D-003, D-012 | Large | Critical (maintainability) |
| Add `dynamic()` imports for Recharts, @dnd-kit, Shepherd.js | D-020 | Medium | High (bundle size) |
| Consolidate component directories into clear hierarchy | D-010 | Large | High (DX) |
| Add per-page error boundaries | D-018 | Medium | Medium (error recovery) |
| Add AbortController to all useEffect fetch calls | D-021 | Medium | Medium (memory safety) |
| Standardize date formatting with shared utility | D-022 | Small | Medium (consistency) |
| Remove legacy theme migration code | D-023 | Tiny | Low (cleanup) |

### Phase 3: Strategic Improvements (6+ sprints)

| Action | Debt IDs | Effort | Impact |
|--------|----------|--------|--------|
| Migrate protected pages to RSC data fetching pattern | D-004 | Very Large | Critical (performance) |
| Resolve ThemeProvider / globals.css dual source of truth | D-011 | Medium | High (DX) |
| Replace Shepherd.js `@apply` with design system tokens | D-017, D-026 | Medium | Medium (design system purity) |
| Raise coverage thresholds to 60% target | D-019 | Ongoing | Medium (quality gate) |
| Extract Portuguese strings to i18n-ready constants | D-014 | Very Large | Low now, critical for multi-language |
| Implement proper state management (Zustand or Jotai) | D-012 | Very Large | High (maintainability) |

---

## Appendix A: File Count Summary

| Directory | Files | Purpose |
|-----------|-------|---------|
| `app/` (pages + layouts) | 35 | Pages, layouts, error boundaries |
| `app/buscar/components/` | 30 | Search-specific components |
| `app/buscar/hooks/` | 3 | Search-specific hooks |
| `app/components/` | 48 | General app components |
| `app/components/landing/` | 13 | Landing page sections |
| `app/components/ui/` | 6 | UI primitives |
| `app/api/` | 36 | API proxy routes |
| `app/hooks/` | 1 | Page-level hooks |
| `app/pipeline/` | 4 | Pipeline components |
| `components/` | 21 | Top-level shared components |
| `components/subscriptions/` | 7 | Subscription components |
| `components/billing/` | 1 | Billing components |
| `components/account/` | 1 | Account components |
| `components/layout/` | 1 | Layout components |
| `hooks/` | 16 | Global custom hooks |
| `lib/` | 28 | Utilities, constants, config |
| **Total** | **~251** | |

## Appendix B: Dependency Graph (Simplified)

```
Root Layout
  |-- AuthProvider (Supabase)
  |-- ThemeProvider (CSS vars)
  |-- AnalyticsProvider (Mixpanel)
  |-- NProgressProvider (nprogress)
  |-- BackendStatusProvider
  |-- NavigationShell
  |     |-- Sidebar (desktop, lg+)
  |     |-- BottomNav (mobile, <lg)
  |
  Protected Layout (route group)
  |   |-- AppHeader
  |   |-- Breadcrumbs
  |   |-- Page content
  |
  Public pages (no shell)
      |-- LandingNavbar
      |-- Page content
      |-- Footer
```

## Appendix C: Environment Variables (Frontend)

| Variable | Purpose | Required |
|----------|---------|----------|
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL | Yes |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase anon key | Yes |
| `NEXT_PUBLIC_BACKEND_URL` | Backend API URL | Yes |
| `NEXT_PUBLIC_APP_NAME` | App display name | No (default: SmartLic.tech) |
| `NEXT_PUBLIC_SITE_URL` | Canonical URL | No (default: https://smartlic.tech) |
| `NEXT_PUBLIC_MIXPANEL_TOKEN` | Mixpanel project token | No |
| `NEXT_PUBLIC_GA_MEASUREMENT_ID` | Google Analytics ID | No |
| `SENTRY_ORG` | Sentry organization | No |
| `SENTRY_PROJECT` | Sentry project | No |
| `SENTRY_AUTH_TOKEN` | Sentry auth token (build time) | No |

---

*Generated by @ux-design-expert as part of the SmartLic brownfield discovery workflow (Phase 3). This document should be updated when significant frontend changes are made.*
