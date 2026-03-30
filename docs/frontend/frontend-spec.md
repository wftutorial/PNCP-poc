# SmartLic Frontend Specification & UX Audit

**Data:** 2026-03-30 | **Versao:** 2.0 | **Autor:** @ux-design-expert (Uma) — Brownfield Discovery Phase 3
**Stack:** Next.js 16 + React 18 + TypeScript 5.9 + Tailwind CSS 3 + Framer Motion + Recharts + Supabase SSR + @dnd-kit + Shepherd.js

---

## 1. Overview

### 1.1 Arquitetura Geral

O frontend SmartLic e uma SPA (Single-Page Application) com SSR seletivo, construida sobre Next.js 16 App Router. A aplicacao segue o padrao de **shell navigation** onde paginas protegidas (autenticadas) recebem sidebar desktop + bottom nav mobile via `NavigationShell`, enquanto paginas publicas (landing, login, planos) sao renderizadas sem chrome de navegacao.

**Padrao de rendering:**
- **Server Components:** Paginas publicas de SEO (landing, features, pricing, blog, status, termos, privacidade)
- **Client Components ("use client"):** Todas as paginas protegidas e interativas (buscar, dashboard, pipeline, historico, conta, admin)
- **Nenhum Server Action:** O projeto nao usa `"use server"` — toda comunicacao com backend e via API proxy routes (`/app/api/*`)

### 1.2 Dependencias Principais

| Categoria | Pacote | Versao | Uso |
|-----------|--------|--------|-----|
| Framework | next | ^16.1.6 | App Router, SSR, API routes |
| UI | tailwindcss | ^3.4.19 | Design system |
| Animacao | framer-motion | ^12.33.0 | Transicoes, micro-interacoes |
| Graficos | recharts | ^3.7.0 | Dashboard charts |
| Drag & Drop | @dnd-kit/core | ^6.3.1 | Pipeline kanban |
| Onboarding | shepherd.js | ^14.5.1 | Tours guiados |
| State | swr | ^2.4.1 | Data fetching + cache |
| Auth | @supabase/ssr | ^0.8.0 | Auth SSR-safe |
| Forms | react-hook-form + zod | ^7.71/^4.3 | Validacao tipada |
| Icons | lucide-react | ^0.563.0 | Iconografia |
| Toasts | sonner | ^2.0.7 | Notificacoes |
| Analytics | mixpanel-browser | ^2.74.0 | Event tracking |
| Monitoring | @sentry/nextjs | ^10.38.0 | Error tracking |
| A11y | focus-trap-react | ^12.0.0 | Focus management em modais |
| Mobile | react-simple-pull-to-refresh | ^1.3.4 | Pull-to-refresh na busca |

### 1.3 Provider Hierarchy (layout.tsx)

```
<html lang="pt-BR">
  <body>
    <AnalyticsProvider>
      <AuthProvider>
        <SWRProvider>
          <UserProvider>
            <ThemeProvider>
              <NProgressProvider>
                <BackendStatusProvider>
                  <SessionExpiredBanner />
                  <PaymentFailedBanner />
                  <NavigationShell>
                    {children}
                  </NavigationShell>
                  <Toaster />
                  <CookieConsentBanner />
                </BackendStatusProvider>
              </NProgressProvider>
            </ThemeProvider>
          </UserProvider>
        </SWRProvider>
      </AuthProvider>
    </AnalyticsProvider>
  </body>
</html>
```

---

## 2. Page Inventory

### 2.1 Paginas Publicas (sem autenticacao)

#### `/` (Landing Page)
- **Proposito:** Conversao de visitantes, posicionamento de marca
- **Componentes:** LandingNavbar, HeroSection, OpportunityCost, BeforeAfter, HowItWorks, StatsSection, TestimonialSection, FinalCTA, Footer
- **State Management:** Nenhum — server component puro
- **API Dependencies:** Nenhuma
- **UX Patterns:** Scroll-based sections, fluid typography (clamp), gradient hero, glassmorphism cards, AnimateOnScroll

#### `/login`
- **Proposito:** Autenticacao (email/senha + Google OAuth + Magic Link + MFA/TOTP)
- **Componentes:** InstitutionalSidebar, LoginForm, TotpVerificationScreen (lazy-loaded)
- **State Management:** react-hook-form com zodResolver, useState para fluxo MFA
- **API Dependencies:** Supabase Auth (`signInWithPassword`, `signInWithOtp`, `signInWithOAuth`)
- **UX Patterns:** Split-screen (sidebar institucional + form), error categorization para analytics, redirect pos-login via searchParams

#### `/signup`
- **Proposito:** Criacao de conta com trial 14 dias
- **Componentes:** InstitutionalSidebar, SignupForm, SignupOAuth, SignupSuccess
- **State Management:** react-hook-form + zod, partner tracking via query params
- **API Dependencies:** Supabase Auth (`signUpWithEmail`, `signInWithGoogle`)
- **UX Patterns:** Password strength indicator, UTM param capture, success state com instrucoes de email

#### `/recuperar-senha` e `/redefinir-senha`
- **Proposito:** Fluxo de reset de senha
- **State Management:** Formulario controlado
- **API Dependencies:** Supabase Auth reset flow

#### `/auth/callback`
- **Proposito:** OAuth callback handler
- **UX Patterns:** Loading state enquanto processa token exchange

#### `/planos`
- **Proposito:** Pricing page com checkout Stripe
- **Componentes:** PlanStatusBanners, PlanProCard, PlanConsultoriaCard, PlanToggle, PlanFAQ, TestimonialSection
- **State Management:** usePlans (SWR), usePlan, billing period toggle (monthly/semiannual/annual)
- **API Dependencies:** `GET /api/plans`, `POST /api/checkout`, `GET /api/subscription-status`
- **UX Patterns:** Pricing toggle com desconto progressivo, fallback statico para precos, social proof com depoimentos

#### `/features`
- **Proposito:** Pagina de funcionalidades (transformation narratives)
- **Componentes:** LandingNavbar, FeaturesContent, Footer
- **UX Patterns:** "Sem SmartLic" vs "Com SmartLic" comparisons, hero gradient

#### `/pricing`
- **Proposito:** Marketing pricing page (alternativa a /planos)

#### `/ajuda`
- **Proposito:** Central de ajuda com FAQs
- **UX Patterns:** Accordion para perguntas, links para suporte

#### `/termos` e `/privacidade`
- **Proposito:** Paginas legais

#### `/status`
- **Proposito:** Status page publica do sistema
- **Componentes:** StatusContent (client), UptimeChart
- **API Dependencies:** `GET /api/status`
- **UX Patterns:** Server component shell + client-side data fetching, auto-refresh

#### `/blog`
- **Proposito:** Blog para SEO/content marketing
- **Componentes:** BlogCTA, RelatedPages, SchemaMarkup

#### Paginas SEO Programaticas
- `/como-avaliar-licitacao`, `/como-evitar-prejuizo-licitacao`, `/como-filtrar-editais`, `/como-priorizar-oportunidades`, `/licitacoes`, `/sobre`
- **Proposito:** SEO long-tail para captura organica

### 2.2 Paginas Protegidas (autenticadas)

#### `/buscar` (Principal)
- **Proposito:** Busca e analise de licitacoes — pagina core do produto
- **Componentes (42+):**
  - Header: SearchFormHeader, SearchFormActions, SearchCustomizePanel
  - Filtros: FilterPanel, ModalidadeFilter, ValorFilter, StatusFilter
  - Progresso: EnhancedLoadingProgress, ProgressAnimation, ProgressBar, ProgressSteps, UfProgressGrid
  - Resultados: SearchResults, ResultCard, ResultsList, ResultsHeader, ResultsToolbar, ResultsFilters, ResultsLoadingSection, ResultsFooter
  - Status/Banners: CacheBanner, DegradationBanner, PartialResultsPrompt, SourcesUnavailable, ErrorDetail, RefreshBanner, DataQualityBanner, FilterRelaxedBanner, ExpiredCacheBanner, TruncationWarningBanner, SearchErrorBanner
  - Badges: LlmSourceBadge, ViabilityBadge, ReliabilityBadge, ZeroMatchBadge, FreshnessIndicator, CoverageBar, CompatibilityBadge
  - Interacao: FeedbackButtons, GoogleSheetsExportButton, DeepAnalysisModal
  - Onboarding: OnboardingBanner, OnboardingEmptyState, OnboardingSuccessBanner, TourInviteBanner
  - Empty States: SearchEmptyState, EmptyResults, ZeroResultsSuggestions
  - Modais: BuscarModals (save dialog, keyboard help, upgrade modal, PDF options, trial conversion, payment recovery)
- **State Management:** `useSearchOrchestration` (mega-hook que orquestra):
  - `useSearchFilters` — setor, UFs, datas, modalidades, termos, status
  - `useSearch` — execucao da busca, SSE, resultados
  - `useSearchSSEHandler` — Server-Sent Events para progresso
  - `useSearchExport` — exportacao Excel/Google Sheets/PDF
  - `useSearchPersistence` — persistencia de estado entre sessoes
  - `useSearchRetry` — retry logica
  - `useUfProgress` — progresso por UF
  - `useShepherdTour` — tours guiados (search + results)
  - `useKeyboardShortcuts` — atalhos de teclado
  - `usePlan` / `useTrialPhase` — gating por plano
  - `useNavigationGuard` — prevencao de navegacao acidental durante busca
  - `useBroadcastChannel` — sincronizacao entre abas
- **API Dependencies:** `POST /api/buscar`, `GET /api/buscar-progress/{id}` (SSE), `GET /api/setores`, `GET /api/me`, `GET /api/trial-status`, `POST /api/feedback`, `GET /api/download`
- **UX Patterns:**
  - Pull-to-refresh mobile
  - SSE progress com fallback time-based
  - Sticky header com status do backend
  - Keyboard shortcuts (Ctrl+K para buscar, etc.)
  - Auto-scroll para area de progresso ao iniciar busca
  - Persistent search state via localStorage
  - Tour guiado para novos usuarios
  - Error boundary com recovery

#### `/dashboard`
- **Proposito:** Analytics e insights do usuario
- **Componentes:** DashboardStatCards, DashboardTimeSeriesChart, DashboardDimensionsWidget, DashboardQuickLinks, InsightCards, DashboardProfileSection, DashboardErrorStates (FullPageError, RetryingState, LoadingSkeleton, NotAuthenticated, EmptyState, StaleBanner)
- **State Management:** useFetchWithBackoff (exponential retry), useDashboardDerivedData, useProfileCompleteness
- **API Dependencies:** `GET /api/analytics/summary`, `GET /api/analytics/searches-over-time`, `GET /api/analytics/top-dimensions`, `GET /api/profile-completeness`
- **UX Patterns:** Period toggle (week/month/year), stale data banners, loading skeleton, profile completion prompt

#### `/pipeline`
- **Proposito:** Kanban de oportunidades com drag-and-drop
- **Componentes:** PipelineKanban (dynamic import, SSR: false), ReadOnlyKanban, PipelineMobileTabs
- **State Management:** usePipeline, @dnd-kit/core + sortable
- **API Dependencies:** `GET/POST/PATCH/DELETE /api/pipeline`
- **UX Patterns:** Code-split kanban para bundle size, mobile tabs (nao kanban), tour guiado 3 passos, deadline alerts (borda vermelha)

#### `/historico`
- **Proposito:** Historico de buscas realizadas
- **Componentes:** Inline (sem decomposicao significativa), StatusBadges
- **State Management:** useSessions (SWR)
- **API Dependencies:** `GET /api/sessions`
- **UX Patterns:** Status badges com icones (nao apenas cor), paginacao, filtro por UF

#### `/conta` (redirect -> `/conta/perfil`)
- **Sub-rotas:** `/conta/perfil`, `/conta/plano`, `/conta/seguranca`, `/conta/dados`, `/conta/equipe`
- **Proposito:** Configuracoes de conta, plano, MFA, dados, equipe
- **UX Patterns:** Tab navigation via sub-routes, skeleton loading

#### `/admin`
- **Proposito:** Dashboard administrativo (apenas admin/master)
- **Componentes:** AdminUptimeWidget, AdminSourceHealth, AdminReconciliation, AdminSupportSLA, AdminUserTable, AdminCreateUser
- **State Management:** useState com fetch manual
- **API Dependencies:** `GET /api/admin/*`
- **UX Patterns:** Auth guard (isAdmin), tabela paginada, search de usuarios

#### `/mensagens`
- **Proposito:** Sistema de mensagens/tickets de suporte
- **Componentes:** ConversationList, ConversationDetail
- **State Management:** useConversations
- **API Dependencies:** `GET/POST /api/conversations`
- **UX Patterns:** Inbox com categorias, status icons (nao apenas cor — DEBT-FE-018 resolvido)

#### `/alertas` (Feature-gated)
- **Proposito:** Alertas por email para novas licitacoes
- **Estado atual:** Mostra ComingSoonPage (SHIP-002 AC9)
- **Componentes preparados:** AlertCard, AlertFormModal, AlertsEmptyState

#### `/onboarding`
- **Proposito:** Wizard 3 passos pos-signup (CNAE -> UFs + Valor -> Confirmacao)
- **Componentes:** OnboardingProgress, OnboardingStep1, OnboardingStep2, OnboardingStep3
- **State Management:** react-hook-form por step com zodResolver, useState para dados consolidados
- **API Dependencies:** `POST /api/first-analysis`, `PUT /api/profile-context`
- **UX Patterns:** Progress bar visual, auto-busca apos conclusao, touch-friendly sliders mobile

---

## 3. Component Architecture

### 3.1 Shared Components (`components/`)

| Componente | Uso | Notas |
|-----------|-----|-------|
| `Button` (ui/button.tsx) | Todo o app | CVA variants (primary, secondary, destructive, ghost, link, outline), sizes (sm, default, lg, icon). **Icon buttons exigem aria-label via TypeScript** |
| `Input` / `Label` | Forms | Primitivos estilizados |
| `EmptyState` | Pipeline, historico, dashboard | Padrao com icone + titulo + descricao + steps opcionais + CTA |
| `ErrorBoundary` | Todas as paginas | Class component com Sentry integration, retry + support link |
| `PageErrorBoundary` | Wrapping de paginas | Wrapper do ErrorBoundary por pagina |
| `ErrorStateWithRetry` | Erros de fetch | Compact/full modes, auto-retry com loading state |
| `AuthLoadingScreen` | Paginas protegidas | Skeleton layout (header + cards + list) com aria-busy |
| `NavigationShell` | Layout protegido | Sidebar desktop + BottomNav mobile, condicional por rota |
| `Sidebar` | Desktop nav | Collapsible, persiste estado em localStorage, past_due badge |
| `BottomNav` | Mobile nav | 4 itens principais + drawer "Mais" com focus trap |
| `MobileDrawer` | /buscar mobile | Menu off-canvas com focus-trap-react |
| `PageHeader` | Todas as protegidas | Titulo + breadcrumb padronizado |
| `ViabilityBadge` | Resultados de busca | Tooltip com breakdown 4 fatores, aria-label, tabIndex |
| `FeedbackButtons` | Resultados de busca | Like/dislike com feedback ao backend |
| `DeepAnalysisModal` | Resultados de busca | Analise detalhada com focus trap |

### 3.2 Skeleton Components (`components/skeletons/`)

| Componente | Pagina |
|-----------|--------|
| `AdminPageSkeleton` | /admin |
| `ContaPageSkeleton` | /conta/* |
| `PlanosPageSkeleton` | /planos |

### 3.3 Billing Components

| Componente | Uso |
|-----------|-----|
| `PaymentFailedBanner` | Global (layout) — banner para pagamento falho |
| `PaymentRecoveryModal` | /buscar — modal de recuperacao de pagamento |
| `TrialPaywall` | Gate de funcionalidades para trial expirado |
| `TrialUpsellCTA` | Dashboard, pipeline — upsell apos trial |
| `PlanCard` / `PlanToggle` | /planos — cards de planos |
| `CancelSubscriptionModal` | /conta — cancelamento com focus trap |
| `DowngradeModal` | /conta — downgrade com focus trap |

### 3.4 Search Components (`app/buscar/components/`)

42+ componentes decompostos em categorias:
- **Form:** SearchFormHeader, SearchFormActions, SearchCustomizePanel
- **Results:** ResultCard, ResultsList, ResultsHeader, ResultsToolbar, ResultsFilters, ResultsFooter
- **Progress:** EnhancedLoadingProgress, ProgressAnimation, ProgressBar, ProgressSteps, UfProgressGrid
- **Banners (12):** CacheBanner, DataQualityBanner, FilterRelaxedBanner, ExpiredCacheBanner, TruncationWarningBanner, PartialResultsPrompt, PartialTimeoutBanner, RefreshBanner, SourcesUnavailable, UfFailureDetail, SearchErrorBanner, OnboardingBanner
- **Badges (6):** LlmSourceBadge, ReliabilityBadge, FreshnessIndicator, CoverageBar, ZeroMatchBadge, ViabilityBadge

---

## 4. Design System Analysis

### 4.1 Cores & Tema

**Semantic Token System** via CSS custom properties em `:root` + `.dark`:

| Token | Light | Dark | Uso |
|-------|-------|------|-----|
| `--canvas` | #ffffff | #121212 | Background principal |
| `--ink` | #1e2d3b | #e8eaed | Texto primario |
| `--ink-secondary` | #3d5975 | #a8b4c0 | Texto secundario |
| `--ink-muted` | #6b7a8a | #8494a7 | Texto terciario |
| `--brand-navy` | #0a1e3f | #0a1e3f | Cor primaria |
| `--brand-blue` | #116dff | #116dff | Cor de accent |
| `--success` | #16a34a | #16a34a | Sucesso |
| `--error` | #dc2626 | #dc2626 | Erro |
| `--warning` | #ca8a04 | #ca8a04 | Aviso |

**Paleta especial:** Gem palette (sapphire, emerald, amethyst, ruby) para elementos decorativos e sombras tematicas.

**Chart palette:** 10 cores dedicadas (`--chart-1` a `--chart-10`) para consistencia em graficos Recharts.

**Contraste WCAG documentado:** Cada token tem comentario inline com ratio de contraste (ex: `--ink` vs `--canvas`: 12.6:1 AAA).

### 4.2 Tipografia

| Papel | Font | Variavel | Uso |
|-------|------|----------|-----|
| Body | DM Sans | `--font-body` | Texto corrido, UI geral |
| Display | Fahkwang | `--font-display` | Headings, titulos (preload: false) |
| Data | DM Mono | `--font-data` | Numeros, codigo, dados tabulares |

**Fluid Typography:** Landing page usa `clamp()` para responsive sizing:
- Hero: 40-72px
- H1: 32-56px
- H2: 24-40px
- H3: 20-28px
- Body LG: 18-20px

### 4.3 Espacamento

Base grid de 4px (Tailwind default). Border radius definidos semanticamente:
- `input`: 4px
- `button`: 6px
- `card`: 8px
- `modal`: 12px

### 4.4 Sombras

Sistema de 8 niveis: sm, md, lg, xl, 2xl, glow, glow-lg, glass. Sombras gem-* tematicas para elementos decorativos.

### 4.5 Animacoes

**Tailwind keyframes (7):** fade-in-up, gradient, shimmer, float, slide-up, scale-in, slide-in-right, bounce-gentle.

**Framer Motion:** Usado extensivamente na landing page (stagger animations, scroll-triggered, variants system). Modulo dedicado em `lib/animations/` com easing presets, framer variants, e scroll animations.

### 4.6 Dark Mode

Implementado via `class` strategy (Tailwind `darkMode: "class"`). Toggle manual com fallback para system preference. Tema persistido em localStorage (`smartlic-theme`). Script inline no `<head>` previne flash of unstyled content (FOUC).

---

## 5. State Management

### 5.1 Client State

| Mecanismo | Uso |
|-----------|-----|
| `useState` / `useReducer` | Estado local de componentes |
| `localStorage` | Tema, sidebar collapsed, search state persistence, plan cache (1h TTL), last search cache |
| `BroadcastChannel` | Sincronizacao entre abas do navegador (useBroadcastChannel) |
| `react-hook-form + zod` | Formularios validados (login, signup, onboarding, alertas) |

### 5.2 Server State (SWR/fetch)

| Hook | Dados | Revalidacao |
|------|-------|-------------|
| `usePlan` | Plan info + capabilities | SWR com localStorage fallback ("fail to last known plan") |
| `usePlans` | Lista de planos disponiveis | SWR |
| `useSessions` | Historico de buscas | SWR |
| `usePipeline` | Pipeline kanban items | SWR com mutate otimista |
| `useConversations` | Mensagens/tickets | SWR |
| `useAlerts` | Alertas configurados | SWR |
| `useProfileCompleteness` | % completude do perfil | SWR |
| `usePublicMetrics` | Metricas publicas | SWR |
| `useFetchWithBackoff` | Dashboard data | Fetch com exponential backoff |
| `useQuota` | Quota de buscas | SWR |

### 5.3 Auth State (Supabase SSR)

- `AuthProvider` gerencia sessao, loading, user, isAdmin, isMaster
- `useAuth()` hook exposto para todos os componentes
- Tokens gerenciados pelo `@supabase/ssr` (cookie-based)
- `SessionExpiredBanner` exibido globalmente quando sessao expira
- Redirect automatico para `/` em paginas protegidas se nao autenticado

### 5.4 Cache Strategy

- **Plan cache:** localStorage com 1h TTL (previne UI downgrades em erros de rede)
- **Search state:** localStorage para persistencia entre navegacoes
- **Last search cache:** Cached result da ultima busca para re-exibicao rapida
- **Saved searches:** localStorage para buscas salvas pelo usuario
- **Partial results cache:** Cache de resultados parciais durante busca SSE

---

## 6. UX Assessment

### 6.1 Onboarding Flow

**Qualidade: BOA**

- Wizard 3 passos com progress bar visual
- Step 1: CNAE + objetivo (react-hook-form + zod validation)
- Step 2: UFs + faixa de valor (touch-friendly sliders, min-h-[44px] tap targets)
- Step 3: Confirmacao + auto-busca
- Apos conclusao: auto-redirect para /buscar com resultados pre-carregados
- Tour guiado via Shepherd.js na primeira visita a /buscar (search tour + results tour)
- Banner de convite para tour em resultados (TourInviteBanner com auto-dismiss)

### 6.2 Search Experience

**Qualidade: EXCELENTE (feature principal, muito investimento)**

- Orchestration via mega-hook (`useSearchOrchestration`) que compoe 9+ sub-hooks
- SSE progress tracking com feedback granular por UF (UfProgressGrid)
- Fallback time-based quando SSE falha
- Pull-to-refresh mobile
- Persistent search state entre sessoes
- Keyboard shortcuts (Ctrl+K)
- Navigation guard durante busca ativa
- 12 banners contextuais para diferentes estados de dados (partial, cached, degraded, etc.)
- 6 badges informativos (viability, reliability, LLM source, coverage, freshness, zero-match)
- Feedback buttons por resultado (like/dislike)
- Export Excel/Google Sheets/PDF
- Auto-scroll para area de progresso ao iniciar busca
- BroadcastChannel para sincronizar resultados entre abas

### 6.3 Pipeline Management

**Qualidade: BOA**

- Kanban com drag-and-drop (@dnd-kit)
- Code-split para bundle size (dynamic import, SSR: false)
- Mobile: tabs ao inves de kanban (responsivo)
- Tour guiado 3 passos
- Deadline alerts visuais (borda vermelha)
- Read-only mode para planos restritos

### 6.4 Error Handling UX

**Qualidade: MUITO BOA**

- `error.tsx` global com Sentry reporting + analytics tracking
- `global-error.tsx` para erros de layout
- `not-found.tsx` customizado (404)
- `ErrorBoundary` reusavel com retry + suporte + detalhes tecnicos expandiveis
- `PageErrorBoundary` wrapper por pagina
- `ErrorStateWithRetry` para erros de fetch (compact + full modes)
- `SearchErrorBoundary` especifico para busca
- User-friendly error messages via `getUserFriendlyError()` e `translateAuthError()`
- Login error categorization para analytics (wrong_creds, not_registered, rate_limited, network)

### 6.5 Loading States

**Qualidade: BOA**

- `AuthLoadingScreen` unificado com skeleton layout (header + cards + list)
- Skeletons dedicados por pagina (Admin, Conta, Planos)
- `animate-pulse` usado extensivamente (101 ocorrencias em 20+ arquivos)
- Pipeline: skeleton cards durante load do dynamic import
- Busca: EnhancedLoadingProgress com steps visuais e animacao dedicada
- NProgress bar global para navegacao entre paginas
- Loading spinners em botoes (Button component suporta `loading` prop)

### 6.6 Empty States

**Qualidade: BOA**

- `EmptyState` reusavel com icone + titulo + descricao + steps opcionais + CTA
- `SearchEmptyState` / `EmptyResults` especificos para busca
- `OnboardingEmptyState` para zero resultados apos auto-busca
- `ZeroResultsSuggestions` com sugestoes contextuais
- `DashboardEmptyState` para dashboard sem dados
- `AlertsEmptyState` para alertas
- `ComingSoonPage` para features gated

### 6.7 Mobile Responsiveness

**Qualidade: BOA**

- Navigation: Sidebar desktop -> BottomNav mobile (4 itens + drawer "Mais")
- Buscar: Header mobile com hamburger menu, pull-to-refresh, drawer off-canvas
- Pipeline: Tabs mobile ao inves de kanban
- Touch targets: min-h-[44px] / min-w-[44px] em botoes criticos (53 ocorrencias)
- Viewport meta: `width=device-width, initialScale=1` configurado
- Hook `useIsMobile` para adaptacoes condicionais
- Fluid typography na landing page
- Breakpoints Tailwind: sm (640px), md (768px), lg (1024px)

---

## 7. Accessibility Audit

### 7.1 WCAG Compliance Level

**Estimativa: AA parcial (com gaps)**

O projeto demonstra esforco consciente de acessibilidade, mas tem lacunas em areas especificas.

### 7.2 Pontos Positivos

- **Skip navigation link:** `<a href="#main-content">Pular para conteudo principal</a>` no layout.tsx (WCAG 2.4.1)
- **lang="pt-BR":** Definido no `<html>` (WCAG 3.1.1)
- **Focus visible:** Ring customizado via `focus-visible:ring-2 focus-visible:ring-brand-blue` no Button
- **Focus trap:** `focus-trap-react` em 6 modais criticos (MobileDrawer, DeepAnalysisModal, CancelSubscriptionModal, DowngradeModal, InviteMemberModal, PaymentRecoveryModal)
- **aria-hidden em icones decorativos:** Consistente em Sidebar, BottomNav, ErrorBoundary, ViabilityBadge
- **role="alert"** em estados de erro (ErrorBoundary, ErrorStateWithRetry)
- **role="status" + aria-busy:** Em AuthLoadingScreen
- **aria-label em icon buttons:** Enforced via TypeScript no Button component (size="icon" exige aria-label)
- **WCAG color contrast documentado:** Cada token CSS tem comentario com ratio de contraste
- **Icones + cor para status:** DEBT-FE-018 resolvido em mensagens (nao apenas cor para status)
- **84+ usos de aria-label/aria-live/role em 30+ arquivos**

### 7.3 Lacunas Identificadas

| ID | Issue | Severidade | WCAG Criterio |
|----|-------|-----------|---------------|
| A11Y-001 | Muitos SVG icons inline sem `role="img"` ou `aria-label` (apenas `aria-hidden`) — OK para decorativos, mas alguns carregam informacao | Media | 1.1.1 Non-text Content |
| A11Y-002 | `ViabilityBadge` usa `title` (tooltip) para informacao critica (breakdown de fatores) — title nao e acessivel em mobile/touch | Alta | 1.1.1 / 4.1.2 |
| A11Y-003 | `SearchForm` usa `role="search"` corretamente, mas nao ha landmarks consistentes em todas as paginas (falta `role="main"` em algumas) | Media | 1.3.1 / 2.4.1 |
| A11Y-004 | Banners de status na busca (12 tipos) nao usam consistentemente `role="alert"` ou `aria-live` | Media | 4.1.3 Status Messages |
| A11Y-005 | Dark mode: `--brand-blue` (#116dff) vs `--canvas` dark (#121212) = ~4.5:1 — borderline AA para texto pequeno | Baixa | 1.4.3 Contrast |
| A11Y-006 | Focus order em `BuscarModals` — multiplos modais potencialmente sobrepostos podem confundir focus management | Baixa | 2.4.3 Focus Order |
| A11Y-007 | BottomNav drawer de "Mais" opcoes usa focus trap, mas overlay de fundo nao recebe `aria-hidden="true"` explicitamente no content abaixo | Baixa | 2.4.3 |
| A11Y-008 | Formularios de busca nao possuem `aria-describedby` para instructions/hints em todos os campos | Media | 1.3.1 / 3.3.2 |

### 7.4 Keyboard Navigation

- Sidebar: Tab navigation entre itens, atalhos de teclado globais via `useKeyboardShortcuts`
- Busca: Keyboard shortcuts documentados e acessiveis via modal (footer link)
- Modais: Focus trap funcional em 6 modais
- BottomNav: Focus trap no drawer "Mais", focusable selector configurado

### 7.5 Screen Reader Support

- Loading states: `role="status" + aria-busy` em AuthLoadingScreen
- Erros: `role="alert" + aria-live="assertive"` em ErrorBoundary
- Badges: `aria-label` em ViabilityBadge, CompatibilityBadge
- **Gap:** Resultados de busca nao anunciam dinamicamente numero de resultados encontrados via aria-live

---

## 8. Performance Assessment

### 8.1 Bundle Size

- **Pipeline kanban:** Dynamic import (`next/dynamic`, SSR: false) — @dnd-kit nao carregado em paginas que nao usam
- **TotpVerificationScreen:** Dynamic import em /login (nao carrega supabase em module level)
- **SearchStateManager:** Dynamic import em SearchResults
- **size-limit configurado:** Verificacao de bundle size no package.json
- **Lighthouse CI:** `@lhci/cli` configurado para coleta e assertacao

### 8.2 Image Optimization

- `next/image` configurado com remote patterns (Wix)
- Favicon: `/favicon.ico`
- OG Image: `/api/og` (server-generated)

### 8.3 Code Splitting

- App Router code-splits automaticamente por rota
- Dynamic imports estrategicos para componentes pesados (kanban, MFA)
- Sentry tree-shaking (`bundleSizeOptimizations.excludeDebugStatements`)
- Fonts: Fahkwang e DM Mono com `preload: false` (nao bloqueiam rendering)

### 8.4 SSR vs CSR

| Tipo | Paginas |
|------|---------|
| **Server Component** | Landing, features, status, blog, termos, privacidade, SEO pages |
| **Client Component** | Buscar, dashboard, pipeline, historico, conta, admin, mensagens, alertas, login, signup, onboarding, planos |

### 8.5 Caching

- Static assets: `Cache-Control: public, max-age=2592000, immutable` (_next/static)
- Images: `Cache-Control: public, max-age=604800`
- Fonts: `Cache-Control: public, max-age=31536000, immutable`
- Build ID unico por deploy (previne stale bundles)
- Standalone output para Railway

---

## 9. Technical Debt

| ID | Issue | Severidade | Impacto UX | Esforco |
|----|-------|-----------|------------|---------|
| DEBT-012 | Uso de raw hex values em alguns componentes ao inves de tokens semanticos (documentado no tailwind.config.ts) | Baixa | Inconsistencia visual | Medio |
| DEBT-011 | /conta e redirect puro para /conta/perfil (sem layout de tabs na pagina raiz) | Baixa | Flash de redirect | Baixo |
| DEBT-105 | Duplicacao de footers — NavigationShell footer + buscar footer customizado | Baixa | Confusao de landmarks | Baixo |
| DEBT-108 | RootLayout async para ler nonce de CSP (complexidade desnecessaria se middleware sempre presente) | Baixa | Nenhum | Baixo |
| DEBT-FE-012 | Feature gates hardcoded (apenas `alertas` gated) — sem feature flag service | Media | Nenhum | Medio |
| TD-001 | `useSearchOrchestration` e mega-hook com 200+ linhas, dificil de manter/testar | Alta | Risco de regressao | Alto |
| TD-002 | 12 banners na pagina de busca — excesso de informacao para usuario medio | Media | Cognitive overload | Medio |
| TD-003 | `admin/page.tsx` usa useState + fetch manual ao inves de SWR (inconsistente com resto do app) | Media | Stale data risk | Medio |
| TD-004 | SVGs inline em multiplos componentes (MobileDrawer, BottomNav, ErrorStates) ao inves de icon library unificada | Baixa | Bundle size | Medio |
| TD-005 | Tipo `any` potencialmente presente em API proxy routes | Media | Type safety | Medio |
| TD-006 | SEO pages programaticas (/como-*) podem ter conteudo duplicado/thin | Baixa | SEO penalty | Baixo |
| TD-007 | SearchResults.tsx re-exporta tipos para backward compatibility — indica refactor incompleto | Baixa | Nenhum | Baixo |
| TD-008 | `ViabilityBadge` usa `title` attr para dados criticos — inacessivel em mobile | Alta | A11y gap | Baixo |
| TD-009 | Nenhum `aria-live` region para anunciar resultados de busca dinamicamente | Media | A11y gap | Baixo |

---

## 10. Recommendations

### 10.1 Critical

1. **TD-008 + A11Y-002: Substituir `title` em ViabilityBadge por tooltip acessivel** — Usar Radix Tooltip ou popover customizado que funciona em mobile/touch e e acessivel via keyboard. O breakdown de fatores de viabilidade e informacao critica para decisao do usuario e nao deve depender de hover.

2. **TD-009 + A11Y-004: Adicionar `aria-live` region para resultados de busca** — Quando a busca retorna, anunciar "X oportunidades encontradas" via `aria-live="polite"` para screen readers. Aplicar `role="alert"` ou `role="status"` consistentemente nos 12 banners da busca.

3. **TD-001: Decompor `useSearchOrchestration`** — Este mega-hook orquestra 9+ sub-hooks, estado de trial, modais, tours, e mais. Considerar extrair:
   - `useSearchModals` (save, keyboard, upgrade, PDF, trial, payment recovery)
   - `useSearchTours` (search tour + results tour)
   - `useTrialOrchestration` (trial days, expired state, conversion modal)

### 10.2 High Priority

4. **TD-002: Audit de banners na busca** — 12 banners e excessivo. Consolidar em um sistema de notificacoes stacked com prioridade. Banner de maior prioridade (erro) deve suprimir banners de menor prioridade (cache, freshness). Testar com usuarios reais quais banners adicionam valor.

5. **TD-003: Migrar /admin para SWR** — Consistencia com resto do app. SWR resolve stale data, exponential backoff, e revalidation automaticamente.

6. **A11Y-003: Garantir landmarks consistentes** — Verificar que todas as paginas protegidas tem `<main>` (ou `role="main"`), `<nav>`, e `<footer>` marcados corretamente. A pagina `/buscar` usa `<main id="buscar-content">` — garantir padrao em todas.

7. **A11Y-008: Adicionar `aria-describedby` em campos de busca** — Hints como "Selecione um setor para iniciar" e "Minimo 3 caracteres" devem estar linkados via aria-describedby aos respectivos inputs.

### 10.3 Nice-to-Have

8. **TD-004: Consolidar SVGs inline** — Migrar SVGs restantes de MobileDrawer, BottomNav, etc. para lucide-react (ja e dependencia). Reduz duplicacao e facilita manutencao.

9. **DEBT-012: Finalizar migracao para tokens semanticos** — Eliminar raw hex/var() em favor de classes Tailwind (text-ink, bg-canvas, etc.). O tailwind.config.ts ja mapeia esses tokens.

10. **Adicionar testes de acessibilidade automatizados** — O projeto ja tem `@axe-core/playwright` como devDependency mas nao ha evidencia de uso sistematico nos E2E tests. Integrar `axe-core` em testes criticos (busca, resultados, pipeline).

11. **Considerar prefers-reduced-motion** — As animacoes Framer Motion e CSS nao verificam `prefers-reduced-motion` de forma sistematica. Adicionar media query para desabilitar animacoes para usuarios com sensibilidade.

12. **Otimizar chart palette para daltonismo** — As 10 cores de chart dependem de hue para diferenciar series. Considerar patterns/shapes adicionais ou validar com simulador de daltonismo.

---

## Apendice A: API Proxy Routes

27 proxy routes em `frontend/app/api/` que encaminham requests para o backend com auth token:

| Route | Backend Endpoint |
|-------|-----------------|
| `/api/buscar` | `POST /buscar` |
| `/api/buscar-progress` | `GET /buscar-progress/{id}` (SSE) |
| `/api/analytics` | `GET /analytics/*` |
| `/api/pipeline` | `GET/POST/PATCH/DELETE /pipeline` |
| `/api/plans` | `GET /plans` |
| `/api/me` | `GET /me` |
| `/api/sessions` | `GET /sessions` |
| `/api/feedback` | `POST/DELETE /feedback` |
| `/api/download` | `GET /download` |
| `/api/trial-status` | `GET /trial-status` |
| `/api/subscription-status` | `GET /subscription-status` |
| `/api/billing-portal` | `POST /billing-portal` |
| `/api/onboarding` | `POST /first-analysis` |
| `/api/profile-context` | `PUT/GET /profile/context` |
| `/api/profile-completeness` | `GET /profile/completeness` |
| `/api/setores` | `GET /setores` |
| `/api/health` | `GET /health` |
| `/api/status` | `GET /health/status` |
| `/api/search-status` | `GET /v1/search/{id}/status` |
| `/api/search-cancel` | `POST /v1/search/{id}/cancel` |
| `/api/change-password` | `POST /change-password` |
| `/api/alert-preferences` | `GET/POST /alert-preferences` |
| `/api/alerts` | `GET /alerts` |
| `/api/organizations` | `GET/POST /organizations` |
| `/api/mfa` | `POST /mfa/*` |
| `/api/csp-report` | `POST /csp-report` |
| `/api/first-analysis` | `POST /first-analysis` |

---

## Apendice B: Hooks Inventory

### Global Hooks (`hooks/`)

| Hook | Funcao |
|------|--------|
| `useAnalytics` | Mixpanel event tracking + UTM params |
| `useAuth` | Sessao, login, signup, logout (via AuthProvider) |
| `usePlan` | Plan info com SWR + localStorage fallback |
| `usePlans` | Lista de planos disponiveis |
| `useQuota` | Quota de buscas restante |
| `useTrialPhase` | Fase do trial (active, expiring, expired) |
| `usePipeline` | CRUD pipeline com SWR |
| `useSessions` | Historico de buscas |
| `useConversations` | Mensagens/tickets |
| `useAlerts` | Alertas configurados |
| `useAlertPreferences` | Preferencias de alertas |
| `useIsMobile` | Deteccao de mobile viewport |
| `useKeyboardShortcuts` | Keyboard shortcut registry |
| `useShepherdTour` | Tours guiados Shepherd.js |
| `useNavigationGuard` | Prevencao de navegacao acidental |
| `useBroadcastChannel` | Sincronizacao entre abas |
| `useFetchWithBackoff` | Fetch com exponential backoff |
| `useProfileCompleteness` | % de completude do perfil |
| `useProfileContext` | Contexto de perfil (onboarding data) |
| `useUserProfile` | Dados de usuario |
| `useSearchSSE` | Server-Sent Events para busca |
| `useSearchPolling` | Polling fallback para SSE |
| `useSavedSearches` | Buscas salvas |
| `useServiceWorker` | Service worker registration |
| `useUnreadCount` | Contagem de mensagens nao lidas |
| `usePublicMetrics` | Metricas publicas |
| `useOrganization` | Dados de organizacao (multi-tenant) |

### Search Hooks (`app/buscar/hooks/`)

| Hook | Funcao |
|------|--------|
| `useSearchOrchestration` | Mega-hook que compoe todos os sub-hooks de busca |
| `useSearch` | Core search execution + result state |
| `useSearchExecution` | Logica de execucao (POST + SSE) |
| `useSearchSSEHandler` | Processamento de eventos SSE |
| `useSearchFilters` | Estado de filtros (setor, UFs, datas, etc.) |
| `useSearchExport` | Export Excel/Sheets/PDF |
| `useSearchPersistence` | Persistencia de estado em localStorage |
| `useSearchRetry` | Logica de retry |
| `useUfProgress` | Progresso por UF individual |
