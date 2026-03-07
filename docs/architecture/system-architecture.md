# System Architecture -- SmartLic v0.5

**Version:** 5.0
**Date:** 2026-03-07
**Author:** @architect (Atlas) -- Brownfield Discovery Phase 1
**Status:** Comprehensive analysis of production codebase on `main` branch
**Previous version:** v4.0 (2026-03-04)

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Backend Architecture](#2-backend-architecture)
3. [Frontend Architecture](#3-frontend-architecture)
4. [Data Flow](#4-data-flow)
5. [Infrastructure](#5-infrastructure)
6. [Security](#6-security)
7. [Integrations](#7-integrations)
8. [Resilience Patterns](#8-resilience-patterns)
9. [Monitoring and Observability](#9-monitoring-and-observability)
10. [Technical Debt Inventory](#10-technical-debt-inventory)

---

## 1. System Overview

### 1.1 What SmartLic Does

SmartLic is a SaaS platform for automated government procurement opportunity discovery from Brazil's official data sources. It aggregates, classifies, and scores public bids (licitacoes) using AI-powered filtering and viability assessment, serving B2G companies and procurement consultancies.

### 1.2 Key Characteristics

| Attribute | Value |
|---|---|
| **Architecture Style** | Monolithic API + SPA with BFF (Backend-for-Frontend) proxy layer |
| **Stage** | POC avancado (v0.5) in production, beta with trials, pre-revenue |
| **Production URL** | https://smartlic.tech |
| **Primary Data Sources** | PNCP (priority 1), PCP v2 (priority 2), ComprasGov v3 (priority 3, currently offline) |
| **Revenue Model** | SmartLic Pro R$397/mo, R$357/mo (semiannual), R$297/mo (annual) + Consultoria tier |
| **AI Integration** | GPT-4.1-nano (classification + summaries via OpenAI SDK) |
| **Scale** | Dual-instance deployment (web + worker on Railway), Redis for distributed state |
| **Sectors** | 15 industry verticals with keyword-based classification (defined in `sectors_data.yaml`) |

### 1.3 Tech Stack

**Backend:** FastAPI 0.129, Python 3.12, Pydantic v2, httpx + requests, OpenAI SDK (GPT-4.1-nano), Supabase (PostgreSQL 17 + Auth + RLS), Redis 5.x (cache + circuit breaker + state + streams), ARQ (async job queue), Stripe (billing), Resend (email), Prometheus + OpenTelemetry + Sentry, openpyxl, ReportLab (PDF), PyYAML

**Frontend:** Next.js 16, React 18, TypeScript 5.9, Tailwind CSS 3, Framer Motion, Recharts, Supabase SSR (auth), Sentry, Mixpanel, @dnd-kit (pipeline), Shepherd.js (onboarding), Playwright (E2E)

**Infra:** Railway (web + worker + frontend), Supabase Cloud, Redis (Upstash/Railway), GitHub Actions (17 CI/CD workflows)

### 1.4 System Diagram

```
                                    External Data Sources
                                   +---------------------+
                                   | PNCP API (priority 1)|
                                   | PCP v2 API (priority 2)|
                                   | ComprasGov v3 (priority 3)|
                                   +----------+----------+
                                              |
  User Browser                                |
  +---------+                                 |
  |         |   HTTPS                         |
  |  React  +--------> +------------------+  |
  |  SPA    |          | Next.js 16        |  |    +------------------+
  |         |<--------+| (Railway Frontend)|  |    | OpenAI API       |
  +---------+  SSR +   | Port 8080         |  |    | GPT-4.1-nano     |
               HTML    +--------+---------+  |    +--------+---------+
                                |              |             |
                         API Proxy Routes      |             |
                         (/api/buscar, etc.)   |             |
                                |              |             |
                       +--------v---------+    |    +--------v---------+
                       | FastAPI Backend   +---+    |                  |
                       | (Railway Web)     +--------+ Supabase Cloud   |
                       | Port 8000         |        | PostgreSQL 17    |
                       | 2 Gunicorn Workers|        | Auth + RLS       |
                       +--------+---------+        | Storage           |
                                |                   +------------------+
                       +--------v---------+
                       | Redis             |
                       | (Upstash/Railway) |        +------------------+
                       | - Cache (SWR)     |        | Stripe           |
                       | - SSE Streams     |        | Payments         |
                       | - Circuit Breaker |        +------------------+
                       | - ARQ Job Queue   |
                       +--------+---------+        +------------------+
                                |                   | Resend           |
                       +--------v---------+        | Transactional    |
                       | ARQ Worker        |        | Email            |
                       | (Railway Worker)  +--------+------------------+
                       | LLM summaries     |
                       | Excel generation  |        +------------------+
                       | Email dispatch    |        | Sentry           |
                       +------------------+        | Error Tracking   |
                                                    +------------------+
```

### 1.5 Request Flow (Simplified)

```
Browser -> Next.js middleware (auth check)
        -> API route handler (/api/buscar/route.ts)
           -> getRefreshedToken() (Supabase SSR)
           -> fetch(BACKEND_URL/v1/buscar, { Authorization: Bearer ... })
              -> FastAPI require_auth (JWT validation)
              -> SearchPipeline.run() (7 stages)
              -> SSE progress via /buscar-progress/{search_id}
```

---

## 2. Backend Architecture

### 2.1 Module Inventory

The backend consists of 73+ Python modules organized across the root, `routes/`, `clients/`, `pipeline/`, `source_config/`, `utils/`, `services/`, and `webhooks/` packages.

#### Core Modules

| Category | Modules | Responsibility |
|----------|---------|----------------|
| **Entry** | `main.py`, `config.py`, `schemas.py` | App lifecycle, env config, Pydantic models |
| **Search Pipeline** | `search_pipeline.py`, `search_context.py`, `search_state_manager.py` | 7-stage search orchestration, typed context, state machine |
| **Consolidation** | `consolidation.py`, `bulkhead.py` | Multi-source parallel fetch, per-source concurrency isolation |
| **Data Sources** | `pncp_client.py` + `clients/portal_compras_client.py`, `clients/compras_gov_client.py`, `clients/base.py` | PNCP, PCP v2, ComprasGov v3 adapters |
| **Filtering** | `filter.py`, `filter_stats.py`, `term_parser.py`, `synonyms.py`, `status_inference.py`, `relevance.py` | Keyword matching, density scoring, term parsing |
| **AI/LLM** | `llm.py`, `llm_arbiter.py`, `viability.py` | Classification, summaries, viability assessment |
| **Cache** | `search_cache.py`, `cache.py`, `redis_pool.py`, `redis_client.py` (deprecated) | Three-level SWR cache (InMemory/Redis, Supabase, Local File) |
| **Auth** | `auth.py`, `authorization.py`, `oauth.py`, `quota.py` | JWT validation, role checks, plan quotas |
| **Billing** | `services/billing.py`, `webhooks/stripe.py` | Stripe subscription management, webhooks |
| **Jobs** | `job_queue.py`, `cron_jobs.py` | ARQ background processing, periodic tasks |
| **Progress** | `progress.py` | SSE via Redis Streams (or asyncio.Queue fallback) |
| **Monitoring** | `metrics.py`, `telemetry.py`, `health.py`, `audit.py` | Prometheus, OpenTelemetry, health checks |
| **Output** | `excel.py`, `pdf_report.py`, `report_generator.py`, `google_sheets.py`, `storage.py` | Excel, PDF, Google Sheets export |
| **Email** | `email_service.py` + `templates/emails/` | Transactional emails via Resend |
| **Sectors** | `sectors.py`, `sectors_data.yaml` | 15 sector definitions with keywords and exclusions |
| **Middleware** | `middleware.py` | CorrelationID, SecurityHeaders, Deprecation, RateLimit |
| **Logging** | `log_sanitizer.py` | PII masking (email, token, user ID, IP) |
| **Misc** | `lead_prospecting.py`, `lead_scorer.py`, `lead_deduplicator.py`, `contact_searcher.py`, `bid_analyzer.py`, `slo.py`, `business_hours.py`, `analytics_events.py`, `feedback_analyzer.py`, `schema_contract.py` | Lead gen (experimental), SLO, analytics |

#### Pipeline Sub-Package (`pipeline/`)

| Module | Responsibility |
|--------|---------------|
| `helpers.py` | `_build_pncp_link()`, `_calcular_urgencia()`, `_convert_to_licitacao_items()`, quota email helpers |
| `cache_manager.py` | Cache key computation, read/write/compose, SWR revalidation triggers |

#### Source Config (`source_config/`)

| Module | Responsibility |
|--------|---------------|
| `sources.py` | `SourceConfig` dataclass, enable/disable per source, health registry, env-based config |

#### Utilities (`utils/`)

| Module | Responsibility |
|--------|---------------|
| `cnae_mapping.py` | CNAE code to sector ID mapping (onboarding) |
| `date_parser.py` | Date parsing and formatting |
| `error_reporting.py` | Centralized Sentry/logging error emission |
| `ordenacao.py` | Result sorting logic |
| `disposable_emails.py` | Disposable email domain detection |
| `email_normalizer.py` | Email normalization for dedup |
| `phone_normalizer.py` | Phone number normalization |

### 2.2 Search Pipeline (Core Business Logic)

`search_pipeline.py` implements a 7-stage decomposition:

| Stage | Name | Key Operations |
|-------|------|----------------|
| 1 | ValidateRequest | JWT auth, quota check (`check_and_increment_quota_atomic`), plan resolution (is_admin, is_master) |
| 2 | PrepareSearch | Sector config from `sectors_data.yaml`, term parsing (`term_parser.py`), keyword/exclusion set assembly |
| 3 | ExecuteSearch | Cache lookup (L1/L2/L3), `ConsolidationService.fetch_all()` on miss, bulkhead isolation, SSE per-UF progress |
| 4 | FilterResults | UF check, value range, keyword density scoring, LLM zero-match classification, status/date validation |
| 5 | EnrichResults | Relevance scoring, viability assessment (4 factors, 0-100), sorting by relevance |
| 6 | GenerateOutput | Item conversion to `LicitacaoItem`, ARQ job enqueue (LLM summary + Excel), immediate fallback response |
| 7 | Persist | Session save to Supabase, cache write (L1+L2), `BuscaResponse` construction, SSE "complete" event |

**`SearchContext`** dataclass carries ~30 typed fields across all stages: input request, auth results, sector config, raw results, filter outputs, cache state, error tracking, truncation flags, coverage metadata.

**`SearchStateManager`** tracks lifecycle: `created -> processing -> completed | timed_out | error`. State transitions persisted to `search_state_transitions` table for observability.

### 2.3 Data Source Architecture

All sources implement the `SourceAdapter` ABC (`clients/base.py`) with unified contract: `fetch()`, `health_check()`, `close()`, plus `code` and `metadata` properties. Each source produces `UnifiedProcurement` dataclass instances that the consolidation layer deduplicates.

**PNCP (Priority 1)** -- `pncp_client.py` (1500+ lines):
- Dual implementation: `PNCPClient` (sync/requests) + async via `AsyncPNCPClient` (httpx)
- Per-modality fetching with 4 default competitive modalities
- Phased UF batching: `PNCP_BATCH_SIZE=5`, `PNCP_BATCH_DELAY_S=2.0s`
- Per-UF timeout: 30s normal, 15s degraded
- Per-modality timeout: 20s
- Circuit breaker: 15 failures threshold, 60s cooldown
- Max page size: 50 (API limit since Feb 2026)
- UFs ordered by population for degraded-mode priority
- `on_uf_complete` callback for per-UF SSE progress

**PCP v2 (Priority 2)** -- `clients/portal_compras_client.py`:
- Public API, no authentication required
- Fixed 10/page pagination with `pageCount`/`nextPage`
- Client-side UF filtering only (no server-side UF parameter)
- `valor_estimado=0.0` (v2 has no value data)
- Circuit breaker: 15 failures, 60s cooldown

**ComprasGov v3 (Priority 3)** -- `clients/compras_gov_client.py`:
- Dual-endpoint: legacy + Lei 14.133
- Currently **OFFLINE** since 2026-03-03 (JSON 404 on all endpoints)

**`consolidation.py`** -- `ConsolidationService`:
- Parallel fetch via `asyncio.gather` with per-source and global timeouts
- Priority-based deduplication (lower number wins, PNCP=1 over PCP=2)
- Early return when >=80% UFs responded after 80s elapsed
- Health-aware timeout adjustments for degraded sources
- `AllSourcesFailedError` for cascade failure signaling

**`bulkhead.py`** -- Per-source concurrency isolation:
- Each source gets an `asyncio.Semaphore` (configurable `max_concurrent`)
- `BulkheadAcquireTimeoutError` signals capacity exhaustion without triggering circuit breaker

### 2.4 Filtering and Classification Chain

Processing order (fail-fast, cheapest checks first):

```
Raw bids from all sources
  |
  v
1. UF check (fastest -- skip if bid not in requested UFs)
  |
  v
2. Value range check (sector-defined min/max from sectors_data.yaml)
  |
  v
3. Keyword matching (density scoring via filter.py)
  |  - >5% density -> "keyword" source (ACCEPT)
  |  - 2-5% density -> "llm_standard" (uncertain zone, send to LLM)
  |  - 1-2% density -> "llm_conservative" (uncertain zone, send to LLM)
  |
  v
4. LLM zero-match classification (for 0% keyword density)
  |  - GPT-4.1-nano YES/NO decision
  |  - Batch classification with ThreadPoolExecutor(max_workers=10)
  |  - Feature flag: LLM_ZERO_MATCH_ENABLED
  |  - Fallback: REJECT on LLM failure (zero noise philosophy)
  |
  v
5. Status/date validation
  |
  v
6. Viability assessment (post-filter, orthogonal to relevance)
   - 4 factors: Modalidade(30%), Timeline(25%), ValueFit(25%), Geography(20%)
   - Levels: Alta(>70), Media(40-70), Baixa(<40)
```

**`filter.py`** -- Keyword matching engine:
- Portuguese stopword removal (100+ stopwords in `STOPWORDS_PT`)
- Term validation (min length, no stopwords, no special chars)
- Density scoring with phrase matching
- Synonym expansion (feature flag `SYNONYM_MATCHING_ENABLED`)
- Per-sector exclusion term support

### 2.5 AI/LLM Integration

**`llm_arbiter.py`** -- GPT-4.1-nano classification:
- Two modes: "uncertain zone" (1-5% density) and "zero-match" (0% density)
- Structured output: `classe (SIM/NAO), confianca (0-100), evidencias, motivo_exclusao`
- Two-level arbiter cache: L1 in-memory `OrderedDict` (max 5000 entries, LRU) + L2 Redis hash (`smartlic:arbiter:` prefix, 1h TTL)
- Lazy OpenAI client initialization with 15s timeout (`_LLM_TIMEOUT`)
- Cost: ~R$0.00007 per structured classification
- Fallback: REJECT on any LLM failure

**`llm.py`** -- GPT-4.1-nano summary generation:
- `gerar_resumo()` -- Full LLM summary with `ResumoEstrategico` Pydantic schema (max 50 bids input)
- `gerar_resumo_fallback()` -- Deterministic fallback when LLM unavailable or timed out
- Dispatched as ARQ background job; immediate fallback response returned to user

**`viability.py`** -- Deterministic 4-factor viability scoring:
- `ViabilityAssessment` Pydantic model with `ViabilityFactors` breakdown
- Modality scoring dictionary maps procurement types to 0-100 scores
- `assess_batch()` for processing multiple bids in one call

### 2.6 Cache Architecture (Three-Level SWR)

```
Request arrives
  |
  v
L1: InMemoryCache / Redis (4h TTL) -- CACHE_FRESH_HOURS=4
  |-- HIT (fresh, 0-4h) -> serve immediately
  |-- MISS -> check L2
  v
L2: Supabase search_results_cache table (24h TTL) -- CACHE_STALE_HOURS=24
  |-- HIT (stale, 4-24h) -> serve + trigger SWR background revalidation
  |-- MISS -> check L3
  v
L3: Local file (/tmp/smartlic_cache, 24h TTL, emergency only)
  |-- HIT -> serve only if Supabase down
  |-- MISS -> fetch from live sources
```

**`search_cache.py`** (500+ lines):
- Cache key includes sector, UFs, `date_from`/`date_to` (STORY-306 correctness fix)
- Dual-read: exact key -> legacy key (thundering herd mitigation)
- SWR: max 3 concurrent background refreshes, 180s timeout
- Hot/Warm/Cold priority tiering (`CachePriority` enum, access frequency-based)
- Local cache: `LOCAL_CACHE_MAX_SIZE_MB=200`, eviction target 100MB

**`redis_pool.py`** -- Unified connection management:
- Async pool: `max_connections=50`, `socket_timeout=30s`, `socket_connect_timeout=10s`
- SSE-specific pool: `max_connections=10`, `socket_timeout=60s` (extended for XREAD)
- Sync pool: `max_connections=12` (for LLM arbiter in `ThreadPoolExecutor`)
- `InMemoryCache` LRU fallback: 10K max entries, TTL support, `OrderedDict`-based
- Prometheus metrics: `REDIS_AVAILABLE` gauge, `REDIS_FALLBACK_DURATION` gauge
- Fallback warning: periodic WARNING every 60s when in fallback mode > 5 minutes

### 2.7 Background Jobs (ARQ)

**`job_queue.py`**:
- Web process enqueues via `get_arq_pool()` -> `enqueue_job()`
- Worker process: `arq job_queue.WorkerSettings`
- Communication: SSE events via `ProgressTracker` (Redis Streams or in-memory fallback)
- Fallback: if Redis/ARQ unavailable, pipeline executes LLM/Excel inline
- Worker liveness check: 15s interval, cached health status

**`cron_jobs.py`** -- 10+ periodic background tasks (asyncio, started in lifespan):
- Cache cleanup (6h), session cleanup (stale >1h -> timeout, >7d -> delete)
- Cache refresh (4h, SWR proactive warming)
- Stripe reconciliation
- Health canary (PNCP/PCP periodic probes)
- Revenue share reports, sector stats, support SLA, daily volume, results cleanup

**`start.sh`** -- Entrypoint:
- `PROCESS_TYPE=web`: Gunicorn + Uvicorn workers (2 workers, 120s timeout, 75s keep-alive)
- `PROCESS_TYPE=worker`: ARQ worker with restart loop (max 10 restarts, 5s delay)
- `RUNNER=uvicorn`: Alternative single-process mode (no fork, no SIGSEGV risk)

### 2.8 API Routes (31 modules, 60+ endpoints)

| Module | Key Endpoints | Purpose |
|--------|--------------|---------|
| `search.py` | `POST /buscar`, `GET /buscar-progress/{id}` (SSE), `GET /v1/search/{id}/status` | Core search + SSE progress |
| `pipeline.py` | `POST/GET/PATCH/DELETE /pipeline`, `GET /pipeline/alerts` | Opportunity kanban |
| `billing.py` | `POST /checkout`, `POST /billing-portal` | Stripe checkout |
| `plans.py` | `GET /plans` | Plan listing with prices |
| `user.py` | `GET /me`, `PUT /profile/context`, `GET /trial-status` | User profile |
| `analytics.py` | `GET /summary`, `GET /searches-over-time`, `GET /trial-value` | Dashboard analytics |
| `feedback.py` | `POST/DELETE /feedback`, `GET /admin/feedback/patterns` | User feedback loop |
| `sessions.py` | `GET /sessions` | Search history |
| `messages.py` | `POST/GET /conversations`, `POST /{id}/reply`, `PATCH /{id}/status` | Messaging |
| `auth_oauth.py` | `GET /google`, `GET /google/callback`, `DELETE /google` | Google OAuth |
| `onboarding.py` | `POST /first-analysis` | Onboarding wizard |
| `alerts.py` | Alert CRUD + preview | Email alert subscriptions |
| `bid_analysis.py` | `GET /bid-analysis/{id}` | AI-powered deep bid analysis |
| `mfa.py` | TOTP enroll/verify + recovery codes | Multi-factor auth |
| `organizations.py` | Organization CRUD | Multi-user organizations |
| `partners.py` | Revenue share CRUD | Partner program |
| `reports.py` | PDF diagnostico | PDF report generation |
| `sectors_public.py` | Public sector listing | SEO landing pages |
| `slo.py` | SLO dashboard | Admin SLO metrics |
| `admin_trace.py` | `GET /search-trace/{search_id}` | Admin debugging |
| `health.py` | `GET /health/cache` | Admin cache inspection |
| `metrics_api.py` | `GET /metrics/discard-rate` | Filter analytics |
| `subscriptions.py` | `GET /subscription/status` | Subscription queries |
| `features.py` | Feature flags | Runtime flag management |
| `export_sheets.py` | Google Sheets export | Sheet integration |
| `emails.py` | Email preferences | Email management |
| `auth_email.py` | Email confirmation recovery | Auth recovery |
| `auth_check.py` | Email/phone availability | Registration checks |
| `trial_emails.py` | Trial email sequence | Trial reminders |
| `blog_stats.py` | Blog stats | Programmatic SEO |

All routers mounted twice: `/v1/<path>` (versioned) + `/<path>` (legacy, deprecated with `Sunset: 2026-06-01` header via `DeprecationMiddleware`).

---

## 3. Frontend Architecture

### 3.1 Pages and Routes

44 pages in `frontend/app/` (Next.js App Router):

| Route | Purpose |
|-------|---------|
| `/` | Landing page (marketing) |
| `/login`, `/signup` | Email/password + Google OAuth |
| `/auth/callback` | OAuth callback handler |
| `/recuperar-senha`, `/redefinir-senha` | Password reset flow |
| `/onboarding` | 3-step wizard (CNAE -> UFs -> Confirmation + auto-search) |
| `/buscar` | **Main search page** -- filters, SSE progress, results, viability badges |
| `/dashboard` | Analytics dashboard with Recharts charts |
| `/historico` | Search history list |
| `/pipeline` | Opportunity kanban (@dnd-kit drag-and-drop) |
| `/mensagens` | Messaging system |
| `/conta`, `/conta/seguranca`, `/conta/equipe` | Account settings, MFA, team |
| `/alertas` | Email alert preferences |
| `/planos`, `/planos/obrigado` | Pricing + thank you |
| `/pricing`, `/features` | Marketing pages |
| `/ajuda` | Help center |
| `/admin`, `/admin/cache`, `/admin/slo`, `/admin/metrics`, `/admin/emails`, `/admin/partners` | Admin dashboards |
| `/termos`, `/privacidade`, `/sobre` | Legal/about pages |
| `/status` | Public status page |
| `/blog`, `/blog/[slug]`, `/blog/programmatic/[setor]/[uf]`, `/blog/licitacoes/[setor]/[uf]`, `/blog/panorama/[setor]` | Blog with programmatic SEO |
| `/licitacoes`, `/licitacoes/[setor]` | SEO sector landing pages |
| `/como-avaliar-licitacao`, `/como-evitar-prejuizo-licitacao`, `/como-filtrar-editais`, `/como-priorizar-oportunidades` | SEO content pages |

### 3.2 Key Components

**Search Components** (`app/buscar/components/`, 31 files):
- `SearchForm.tsx` -- Main search form with UF selector, sector picker, date range
- `SearchResults.tsx` -- Results list with pagination and feedback buttons
- `FilterPanel.tsx` -- Advanced filters (status, modality, value range, esfera, municipio)
- `UfProgressGrid.tsx` -- Per-UF progress visualization during SSE
- `ErrorDetail.tsx` -- Structured error display (7 error codes mapped to Portuguese messages)
- `ViabilityBadge.tsx`, `LlmSourceBadge.tsx`, `ReliabilityBadge.tsx`, `CompatibilityBadge.tsx`, `ZeroMatchBadge.tsx` -- AI metadata badges
- `FeedbackButtons.tsx` -- Thumbs up/down per result
- `SourceStatusGrid.tsx`, `SourcesUnavailable.tsx` -- Multi-source transparency
- `RefreshBanner.tsx`, `ExpiredCacheBanner.tsx` -- Stale data indicators
- `PartialResultsPrompt.tsx`, `PartialTimeoutBanner.tsx` -- Degraded mode UX
- `SearchStateManager.tsx` -- Client-side state management for search lifecycle
- `SearchErrorBoundary.tsx` -- Error boundary with recovery UI
- `ZeroResultsSuggestions.tsx`, `EmptyResults.tsx` -- Empty state with actionable suggestions
- `CoverageBar.tsx`, `FilterStatsBreakdown.tsx`, `FilterRelaxedBanner.tsx` -- Filter transparency
- `FreshnessIndicator.tsx`, `DataQualityBanner.tsx`, `TruncationWarningBanner.tsx` -- Data quality signals
- `DeepAnalysisModal.tsx` -- AI-powered bid deep analysis modal

**Shared Components** (`components/`, 22+ files):
- `NavigationShell.tsx`, `Sidebar.tsx`, `BottomNav.tsx` -- App layout
- `BackendStatusIndicator.tsx` -- Backend health polling (30s, visibility-gated)
- `EnhancedLoadingProgress.tsx` -- Educational B2G carousel during search
- `ErrorStateWithRetry.tsx` -- Retry UI with exponential backoff
- `AlertNotificationBell.tsx` -- Alert notification badge
- `ProfileProgressBar.tsx`, `ProfileCompletionPrompt.tsx` -- Profile completion UX
- `MobileDrawer.tsx` -- Mobile navigation
- `SWRProvider.tsx` -- SWR global configuration
- `billing/PaymentRecoveryModal.tsx` -- Payment failure recovery
- `reports/PdfOptionsModal.tsx` -- PDF report options

### 3.3 Custom Hooks (20 hooks in `hooks/`)

| Hook | Purpose |
|------|---------|
| `useSearchSSE.ts` | Consolidated SSE hook: EventSource, reconnect backoff [1s,2s,4s], max 3 retries, Last-Event-ID replay, polling fallback |
| `useSearch.ts` (in buscar/hooks) | Search lifecycle: submit, SSE, retry (3 attempts with 10s/20s/30s countdown) |
| `useSearchFilters.ts` (in buscar/hooks) | Sector/UF/modality filter state with localStorage persistence |
| `usePlan.ts` | Current plan with localStorage cache (1h TTL) |
| `usePlans.ts` | Plan listing fetcher |
| `useQuota.ts` | Quota status and limits |
| `useTrialPhase.ts` | Trial phase detection (active/expiring/expired) |
| `usePipeline.ts` | Pipeline CRUD operations |
| `useSessions.ts` | Search history fetcher |
| `useFetchWithBackoff.ts` | Generic exponential backoff fetcher (2s->4s->8s->16s->30s cap, max 5 retries) |
| `useAnalytics.ts` | Mixpanel event tracking |
| `useFeatureFlags.ts` | Runtime feature flag checking |
| `useUserProfile.ts` | User profile state |
| `useSavedSearches.ts` | Saved search management |
| `useSearchPolling.ts` | Status polling fallback when SSE unavailable |
| `useNavigationGuard.ts` | Unsaved changes warning |
| `useKeyboardShortcuts.ts` | Keyboard shortcut registration |
| `useIsMobile.ts` | Responsive breakpoint detection |
| `useShepherdTour.ts` | Onboarding tour management |
| `useBroadcastChannel.ts` | Cross-tab search sync via BroadcastChannel API |
| `useServiceWorker.ts` | Service worker registration |
| `useUnreadCount.ts` | Unread message count |

### 3.4 API Proxy Pattern

58 API proxy routes in `frontend/app/api/` proxy requests to the backend:

```
Browser -> /api/buscar (Next.js route handler)
        -> getRefreshedToken() (Supabase SSR, server-side)
        -> fetch(BACKEND_URL/v1/buscar, { Authorization: Bearer <refreshed_token> })
        -> parse response, add error context
        -> return to browser
```

The proxy layer:
- Refreshes Supabase tokens server-side (`lib/serverAuth.ts`) to prevent expired token errors
- Translates backend error codes to Portuguese user messages (`lib/error-messages.ts`)
- Sanitizes error details via `lib/proxy-error-handler.ts` (never exposes stack traces)
- Adds `X-Request-ID` header for correlation
- SSE proxy uses `undici.Agent({ bodyTimeout: 0 })` to prevent timeout on long streams
- AbortController linked to `request.signal` for client disconnect cleanup
- Inactivity timeout (120s) on SSE reader loop via `Promise.race`

### 3.5 State Management

No global state library (Redux, Zustand). State managed via:

- **React hooks** -- Component-local state with `useState`/`useReducer`
- **Custom hooks** -- Domain-specific state (see table above)
- **Supabase SSR** -- Auth state via `@supabase/ssr` (cookie-based, server-side refresh)
- **localStorage** -- Plan cache (1hr TTL), filter preferences, theme, sector fallback, last search cache
- **BroadcastChannel** -- Cross-tab search result sync
- **URL search params** -- `?auto=true&search_id=xxx` for onboarding auto-search flow

### 3.6 SSE Progress Tracking

Dual-connection pattern:
1. `GET /api/buscar-progress?search_id={id}` -- SSE stream for real-time progress
2. `POST /api/buscar` -- JSON response with final results

```
Frontend                           Backend
  |                                  |
  |-- POST /buscar (search_id) ----->|  (starts pipeline)
  |-- GET /buscar-progress/{id} ---->|  (opens SSE stream)
  |                                  |
  |<-- SSE: connecting (10%) --------|
  |<-- SSE: fetching (30%) ----------|  (per-UF uf_status events)
  |<-- SSE: filtering (60%) ---------|
  |<-- SSE: complete (100%) ---------|
  |<-- SSE: llm_ready --------------|  (background job done)
  |<-- SSE: excel_ready -------------|  (background job done)
  |                                  |
  |<-- JSON response (final) --------|
```

**Backend** (`progress.py`):
- `ProgressTracker` per search operation with `ProgressEvent` dataclass
- Primary: Redis Streams (at-least-once delivery, replay from any point via `$` cursor)
- Fallback: In-memory `asyncio.Queue` when Redis unavailable
- Heartbeat: `: waiting\n\n` every 5s during tracker wait, `: heartbeat\n\n` every 15s
- Terminal stages (`complete`, `error`, `degraded`, `search_complete`) trigger 5-minute stream EXPIRE
- Last-Event-ID resumption support (replay list in Redis, max 200 events)

**Frontend** graceful fallback: if SSE connection fails after 3 retries, uses calibrated time-based simulation with educational carousel (`EnhancedLoadingProgress`).

---

## 4. Data Flow

### 4.1 End-to-End Search Request

```
1. User enters search criteria (sector, UFs, date range) on /buscar
   |
2. Frontend generates search_id (UUID), opens SSE to /buscar-progress/{id}
   |
3. POST /api/buscar (Next.js proxy) -> refreshes token -> POST /v1/buscar (FastAPI)
   |
4. Stage 1 -- ValidateRequest
   |  - JWT validation (auth.py, ES256+JWKS or HS256)
   |  - Quota check (quota.py check_and_increment_quota_atomic)
   |  - Plan resolution (is_admin, is_master, capabilities)
   |
5. Stage 2 -- PrepareSearch
   |  - Load sector config from sectors_data.yaml
   |  - Parse search terms (term_parser.py)
   |  - Build keyword sets (active_keywords, active_exclusions)
   |
6. Stage 3 -- ExecuteSearch
   |  - Check L1/L2/L3 cache (search_cache.py)
   |  - If cache MISS: ConsolidationService.fetch_all()
   |    - Parallel fetch from PNCP + PCP v2 (+ ComprasGov if online)
   |    - Bulkhead isolation per source (asyncio.Semaphore)
   |    - Circuit breaker checks before each source
   |    - Priority-based deduplication (PNCP=1 wins)
   |    - SSE progress events per UF
   |  - If cache HIT (stale): serve + trigger SWR background revalidation
   |
7. Stage 4 -- FilterResults
   |  - UF check -> Value range -> Keyword matching -> LLM zero-match -> Status validation
   |  - filter_stats tracking for each rejection reason
   |
8. Stage 5 -- EnrichResults
   |  - Relevance scoring per bid
   |  - Viability assessment (4 factors, 0-100 score)
   |  - Sort by relevance (descending)
   |
9. Stage 6 -- GenerateOutput
   |  - Convert to LicitacaoItem objects
   |  - Enqueue LLM summary job (ARQ, async)
   |  - Enqueue Excel generation job (ARQ, async)
   |  - Immediate response with gerar_resumo_fallback()
   |
10. Stage 7 -- Persist
    |  - Save search session to Supabase (search_sessions table)
    |  - Write results to cache (L1 Redis + L2 Supabase)
    |  - Build BuscaResponse with coverage metadata
    |  - SSE: "complete" event
    |
11. Background (ARQ worker):
    |  - LLM summary generated -> SSE: "llm_ready" event
    |  - Excel file generated + uploaded to Supabase Storage -> SSE: "excel_ready" event
    |
12. Frontend receives JSON response + SSE events
    - Renders results with viability badges, confidence indicators
    - Updates UI when llm_ready/excel_ready arrive
```

### 4.2 Timeout Chain (Strict Decreasing)

```
Railway Hard Timeout (300s)
  > Gunicorn Timeout (120s, env GUNICORN_TIMEOUT)
    > Pipeline Total (110s)
      > Consolidation Global (100s)
        > Per-Source (80s)
          > Per-UF (30s normal, 15s degraded)
            > Per-Modality (20s)
              > HTTP Request (10s)

SSE Chain: bodyTimeout(0) + heartbeat(15s) > Railway idle(60s)
           SSE inactivity timeout(120s)
```

Skip LLM after 90s elapsed, skip viability after 100s elapsed.

### 4.3 Billing Flow

```
User clicks "Assinar" -> POST /v1/checkout
  -> Create Stripe Checkout Session (hosted page)
  -> Redirect to Stripe
  -> User completes payment
  -> Stripe sends webhook: checkout.session.completed
  -> Backend: verify signature, check idempotency
  -> Update profiles.plan_type, user_subscriptions
  -> Invalidate plan status cache
  -> Redis feature cache invalidation
```

### 4.4 Email Alert Flow

```
Cron (periodic) -> Check alert_preferences for due alerts
  -> For each alert: run search pipeline (subset)
  -> Compare results vs previous run
  -> If new results: send email via Resend
  -> Log alert_runs for audit
```

---

## 5. Infrastructure

### 5.1 Railway Deployment

Three Railway services from the same codebase:

| Service | Process Type | Port | Resources |
|---------|-------------|------|-----------|
| `bidiq-backend` (web) | `PROCESS_TYPE=web` | 8000 | 1GB RAM, 2 Gunicorn workers |
| `bidiq-worker` | `PROCESS_TYPE=worker` | N/A | ARQ worker (LLM + Excel) |
| `bidiq-frontend` | Next.js standalone | 8080 | Node.js server |

**Dockerfile** (`backend/Dockerfile`):
- Base: `python:3.12-slim`
- `libjemalloc2` preloaded via `LD_PRELOAD` to reduce RSS fragmentation
- Aggressive removal of fork-unsafe C extensions: grpcio, httptools, uvloop
- Post-install verification step

**Gunicorn Configuration** (`start.sh` + `gunicorn_conf.py`):
- 2 workers (`WEB_CONCURRENCY=2`, reduced from 4 due to Railway 1GB OOM)
- Timeout: 120s (`GUNICORN_TIMEOUT`)
- Keep-alive: 75s (> Railway proxy 60s, prevents intermittent 502s)
- Max-requests: 1000 + jitter 50 (worker recycling for memory leak prevention)
- Graceful timeout: 30s
- Worker lifecycle hooks: `when_ready`, `post_worker_init` (SIGABRT handler + faulthandler), `worker_abort` (Sentry notification), `worker_exit` (crash diagnosis: SIGSEGV=-11, OOM=-9)
- JSON structured logging via `logconfig_dict` (redirects Gunicorn stderr -> stdout for Railway severity)

**Railway specifics:**
- Hard timeout: ~300s (5 minutes)
- Health check: `/health` with `healthcheckTimeout=300s`
- No container sleep (always running)
- Custom domain: `smartlic.tech` with `targetPort: 8080`

### 5.2 Redis Usage

| Usage | Key Pattern | TTL | Pool |
|-------|-------------|-----|------|
| Search cache | `smartlic:cache:{key}` | 4h (L1) | Async (50 conns) |
| LLM arbiter cache | `smartlic:arbiter:{hash}` | 1h | Sync (12 conns) |
| SSE Streams | `smartlic:progress:{search_id}` | 5min after terminal | SSE (10 conns, 60s timeout) |
| Rate limiting | `rate_limit:{user_id}:{minute}` | 60s | Async (50 conns) |
| Feature flags | `features:{user_id}` | 5min | Async (50 conns) |
| SSE replay list | `sse_events:{search_id}` | 10min | Async (50 conns) |
| Tracker metadata | `smartlic:tracker:{search_id}` | 5min | Async (50 conns) |

### 5.3 Supabase Configuration

**Database Tables** (73 migrations):
- `profiles` -- User profiles with `plan_type`, `is_admin`, `is_master`
- `search_sessions` -- Search history and analytics
- `search_results_cache` -- L2 cache persistence
- `search_results_store` -- Full result storage for async retrieval
- `pipeline_items` -- Kanban pipeline opportunities
- `user_subscriptions` -- Stripe subscription data
- `stripe_webhook_events` -- Idempotency tracking
- `plans`, `plan_features`, `plan_billing_periods` -- Plan definitions
- `messages`, `conversations` -- User messaging
- `alert_preferences`, `alert_runs` -- Email alerts
- `feedback` -- User feedback per result
- `audit_events` -- Security audit trail
- `trial_email_log` -- Trial email sequence tracking
- `mfa_recovery_codes` -- MFA recovery codes (bcrypt hashed)
- `organizations`, `org_members` -- Multi-user organizations
- `partners`, `revenue_share` -- Partner program
- `health_checks`, `incidents` -- SLO tracking
- `search_state_transitions` -- State machine audit

**RLS (Row-Level Security):** Enabled on all user-facing tables. Service role key bypasses RLS for backend operations. Key policies enforce `user_id = auth.uid()` for all CRUD.

**Auth:** Supabase Auth with email/password + Google OAuth. JWT rotation: ES256 (JWKS) or HS256.

### 5.4 CI/CD Pipelines

17 GitHub Actions workflows:

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `backend-tests.yml` | PR/push to main | Backend pytest (5774+ tests, zero-failure policy) |
| `frontend-tests.yml` | PR/push | Frontend Jest (2681+ tests) |
| `e2e.yml` | PR/push | Playwright E2E (60 tests) |
| `deploy.yml` | Push to main | Production deploy + migration auto-apply + smoke test |
| `staging-deploy.yml` | Push to staging | Staging deployment |
| `pr-validation.yml` | PR | PR validation checks |
| `migration-gate.yml` | PR (migrations) | Warning comment for pending migrations |
| `migration-check.yml` | Push to main + daily | Block if unapplied migrations |
| `backend-ci.yml` | Various | Backend CI checks |
| `codeql.yml` | Schedule | CodeQL security analysis |
| `cleanup.yml` | Schedule | Repository cleanup |
| `dependabot-auto-merge.yml` | Dependabot PR | Auto-merge minor/patch updates |
| `lighthouse.yml` | Manual | Lighthouse performance audit |
| `load-test.yml` | Manual | Locust load testing |
| `sync-sectors.yml` | Manual | Sector data sync |
| `tests.yml` | Various | Combined test runner |

**Deploy pipeline** (`deploy.yml`):
1. Detect changes (backend/frontend)
2. Deploy changed services to Railway
3. Auto-apply Supabase migrations (`supabase db push --include-all`)
4. Send `NOTIFY pgrst, 'reload schema'` for PostgREST cache refresh
5. Smoke test (verify no PGRST205 errors)

---

## 6. Security

### 6.1 Authentication Flow

```
Signup: Email/password -> Supabase Auth -> JWT (ES256 or HS256)
Login:  Email/password -> Supabase Auth -> JWT with sub, email, role, aud, exp
OAuth:  Google -> /auth/google -> Supabase OAuth -> /auth/callback -> JWT
MFA:    TOTP enrollment -> verify -> recovery codes (bcrypt hashed in DB)
```

**JWT Validation** (`auth.py`):
- Three-attempt key detection: JWKS endpoint (ES256) -> PEM key (ES256) -> HS256 symmetric
- `PyJWKClient` with 5-minute JWKS cache (lifespan=300)
- Token validation cache: SHA256(full token) key, 60s TTL (~95% auth API call reduction)
- `require_auth` FastAPI dependency returns `{ sub, email, role, aud, exp }`
- Bearer token passed via `Authorization` header

### 6.2 Authorization

**Role hierarchy:** admin > master > regular user
- `check_user_roles()` queries `profiles` table for `is_admin`, `plan_type`
- Admins automatically get master privileges
- Master users: unlimited quota, Excel export, full pipeline access
- Regular users: plan-based quotas and feature gating

**Row-Level Security (RLS):**
- Enabled on all user-facing Supabase tables
- Policies enforce `user_id = auth.uid()` for SELECT/INSERT/UPDATE/DELETE
- Backend uses service role key to bypass RLS for admin operations
- Webhook handlers operate with service role (no user context)

### 6.3 Rate Limiting

**Per-user rate limiting** (Redis token bucket + in-memory fallback):
- Search: `SEARCH_RATE_LIMIT_PER_MINUTE=10`
- Auth: `AUTH_RATE_LIMIT_PER_5MIN=5`
- Signup: `SIGNUP_RATE_LIMIT_PER_10MIN=3`
- SSE: `SSE_MAX_CONNECTIONS=3` per user, `SSE_RECONNECT_RATE_LIMIT=10` per 60s

**Per-IP rate limiting** (`RateLimitMiddleware`):
- `/health`: 60 req/min
- `/plans`: 30 req/min
- Stripe webhooks: exempt

### 6.4 Input Validation

**Backend (Pydantic v2):**
- `BuscaRequest` with field validators for dates, UFs, sector IDs
- UUID v4 pattern validation for all user/entity IDs
- `SAFE_SEARCH_PATTERN` regex for search terms (blocks `$` for command injection)
- `validate_uuid()` helper for route parameters
- Plan ID validation via `PLAN_ID_PATTERN`

**Frontend:**
- Form validation in components
- Type-safe API contracts via TypeScript interfaces
- URL parameter sanitization in proxy routes

### 6.5 Security Headers

`SecurityHeadersMiddleware` applies on all responses:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: camera=(), microphone=(), geolocation=()`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`
- `Cache-Control: no-store` on authenticated endpoints

### 6.6 CORS Configuration

`get_cors_origins()` in `config.py`:
- Development: `localhost:3000`, `127.0.0.1:3000`
- Production: auto-includes `smartlic.tech`, `www.smartlic.tech`, Railway hostnames
- Custom origins via `CORS_ORIGINS` env var (comma-separated)
- Wildcard `*` explicitly blocked with warning

### 6.7 Secrets and PII

- API keys in env vars only (never committed)
- `log_sanitizer.py` masks: emails (`***@domain`), tokens (`Bearer ***...`), user IDs (`u_***...`), IP addresses
- Sentry `before_send` callback scrubs PII from breadcrumbs, exceptions, user context, request headers
- Stripe webhook signature verification (`STRIPE_WEBHOOK_SECRET`)
- MFA recovery codes stored bcrypt-hashed
- `scrub_pii()` function in `main.py` for Sentry event sanitization

### 6.8 CSP Report Collection

Frontend has `/api/csp-report/route.ts` endpoint for collecting Content Security Policy violation reports.

---

## 7. Integrations

### 7.1 PNCP API (Primary Data Source)

| Attribute | Value |
|-----------|-------|
| **URL** | `https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao` |
| **Auth** | None (public API) |
| **Max page size** | 50 (reduced from 500, Feb 2026; >50 returns HTTP 400 silently) |
| **Default search period** | 10 days |
| **Modalities** | 4 competitive by default: Concorrencia Eletronica(4), Presencial(5), Pregao Eletronico(6), Presencial(7) |
| **Excluded modalities** | Inexigibilidade(9), Inaplicabilidade(14) -- pre-defined winners |
| **UF batching** | `PNCP_BATCH_SIZE=5`, `PNCP_BATCH_DELAY_S=2.0s` |
| **Circuit breaker** | 15 failures / 60s cooldown |
| **Retry** | Exponential backoff, HTTP 422 retryable (max 1 retry) |

### 7.2 PCP v2 API (Secondary)

| Attribute | Value |
|-----------|-------|
| **URL** | `https://compras.api.portaldecompraspublicas.com.br/v2/licitacao/processos` |
| **Auth** | None (fully public v2 API) |
| **Pagination** | Fixed 10/page, `pagina` param |
| **UF filtering** | Client-side only (no server-side param) |
| **Value data** | Not available (`valor_estimado=0.0`) |
| **Circuit breaker** | 15 failures / 60s cooldown |

### 7.3 ComprasGov v3 (Tertiary)

| Attribute | Value |
|-----------|-------|
| **URL** | `https://dadosabertos.compras.gov.br` |
| **Auth** | None (open government data) |
| **Status** | **OFFLINE** since 2026-03-03 (JSON 404) |
| **Endpoints** | Dual: legacy + Lei 14.133 |

### 7.4 OpenAI (GPT-4.1-nano)

| Usage | Module | Details |
|-------|--------|---------|
| Classification (arbiter) | `llm_arbiter.py` | Binary SIM/NAO or structured JSON, ~60ms, ~R$0.00007/call |
| Zero-match classification | `llm_arbiter.py` | Batch via `ThreadPoolExecutor(max_workers=10)`, ~1.5s/batch |
| Executive summary | `llm.py` | `gerar_resumo()`, max 50 bids input, ~2-5s |
| Deep bid analysis | `bid_analyzer.py` | Detailed single-bid analysis |
| **Timeout** | All | 15s (`_LLM_TIMEOUT`), 1 max retry |
| **Fallback** | All | REJECT on failure (classification), deterministic fallback (summary) |

### 7.5 Stripe

| Component | Detail |
|-----------|--------|
| **Checkout** | Hosted checkout sessions via `stripe.checkout.Session.create()` |
| **Webhooks** | 8 event types handled: `checkout.session.completed`, `.async_payment_succeeded/failed`, `customer.subscription.updated/deleted`, `invoice.payment_succeeded/failed/action_required` |
| **Idempotency** | `stripe_webhook_events` table prevents duplicate processing |
| **Proration** | Stripe handles automatically (`proration_behavior="create_prorations"`) |
| **Plans** | SmartLic Pro (monthly/semiannual/annual) + Consultoria tier |
| **Security** | Signature verification via `stripe.Webhook.construct_event()` |

### 7.6 Resend (Email)

| Attribute | Value |
|-----------|-------|
| **From** | `SmartLic <noreply@smartlic.tech>` |
| **Retry** | 3 retries with exponential backoff |
| **Delivery** | Fire-and-forget async (never blocks caller) |
| **Templates** | HTML templates in `templates/emails/` |
| **Free tier** | 1 domain limit (smartlic.tech) |

### 7.7 Supabase

- **Database:** PostgreSQL 17 with 73 migrations
- **Auth:** Email/password + Google OAuth, JWT (ES256/HS256)
- **Storage:** Excel file upload (search results)
- **RLS:** Enabled on all user-facing tables
- **Realtime:** Not used (SSE via custom implementation)

### 7.8 Google APIs

- **Google Sheets:** Export search results via `google-api-python-client`
- **Google OAuth:** Login via Supabase OAuth provider

---

## 8. Resilience Patterns

### 8.1 Circuit Breakers

| Circuit Breaker | Target | Threshold | Cooldown | Behavior When Open |
|-----------------|--------|-----------|----------|-------------------|
| PNCP | PNCP API | 15 failures | 60s | Skip source, serve from other sources + cache |
| PCP | PCP v2 API | 15 failures | 60s | Skip source |
| ComprasGov | ComprasGov v3 | 15 failures | 60s | Skip source |
| Supabase | Supabase client | Sliding window 10, 50% threshold | 60s, 3 trial calls | Fail-open: use cached plan, allow search, log for reconciliation |

**Supabase CB** (`supabase_client.py`):
- `SupabaseCircuitBreaker` with thread-safe `threading.Lock`
- Global singleton `supabase_cb` (must be reset between tests via conftest)
- `CircuitBreakerOpenError` exception for fast-fail signaling
- `sb_execute()` wrapper integrates CB with all Supabase operations
- Prometheus: `smartlic_supabase_cb_state` gauge + `smartlic_supabase_cb_transitions_total` counter

### 8.2 Two-Level Cache (SWR)

See section 2.6 for full cache architecture. Key resilience features:
- **Stale-While-Revalidate:** Serves stale data immediately while refreshing in background
- **Three-level fallback:** InMemory/Redis -> Supabase -> Local file
- **Hot/Warm/Cold priority:** Access frequency determines eviction order
- **Background revalidation:** Max 3 concurrent, 180s timeout
- **Recovery epoch:** Cache entries written before PNCP recovery are treated as stale

### 8.3 Graceful Degradation Cascade

```
All sources healthy -> Full results
  |
One source down -> Partial results from remaining sources + degradation banner
  |
All sources down -> Stale cache (if within 24h SWR window) + stale_cache banner
  |
No cache available -> Empty results with contextual suggestions (EmptyResults component)
```

**Frontend degradation signals:**
- `CacheBanner` (stale data indicator)
- `DegradationBanner` (partial source failure)
- `PartialResultsPrompt` (missing UFs)
- `SourcesUnavailable` (all sources down)
- `BackendStatusIndicator` (backend offline)
- Auto-retry: 3 attempts with 10s/20s/30s countdown timers

### 8.4 Bulkhead Pattern

`bulkhead.py` provides per-source concurrency isolation:
- Each data source gets its own `asyncio.Semaphore`
- One slow/overloaded source cannot exhaust connection pool for others
- `BulkheadAcquireTimeoutError` marks UF as "skipped" (not "error")
- Prometheus: `SOURCE_ACTIVE_REQUESTS`, `SOURCE_POOL_EXHAUSTED`, `SOURCE_SEMAPHORE_WAIT_SECONDS`

### 8.5 Connection Pool Management

| Pool | Type | Max Connections | Timeout | Purpose |
|------|------|-----------------|---------|---------|
| Redis async | `redis.asyncio` | 50 | 30s socket | General cache, rate limiting |
| Redis SSE | `redis.asyncio` | 10 | 60s socket | SSE XREAD (extended for latency spikes) |
| Redis sync | `redis.Redis` | 12 | 30s socket | LLM arbiter in ThreadPoolExecutor |
| Supabase httpx | `httpx.AsyncClient` | 50 conn / 20 keepalive | 30s total, 10s connect | Database operations |

### 8.6 Retry Strategies

| Component | Strategy | Max Retries | Backoff |
|-----------|----------|-------------|---------|
| PNCP API | Exponential with jitter | Per RetryConfig | `base * 2^attempt + random(0, base)` |
| LLM arbiter | Fixed | 1 | N/A (15s timeout) |
| Email (Resend) | Exponential | 3 | Increasing delay |
| ARQ worker | Restart loop | 10 | 5s fixed |
| Frontend search | Countdown timer | 3 | 10s, 20s, 30s |
| Frontend SSE | Exponential | 3 | 1s, 2s, 4s |
| Supabase `check_user_roles` | Fixed delay | 1 | 0.3s |

### 8.7 Fail-Open / Fail-Safe Decisions

| Scenario | Decision | Rationale |
|----------|----------|-----------|
| Supabase CB open during quota check | **Fail-open** (allow search) | Revenue protection: better to over-serve than block paying users |
| LLM failure during classification | **Fail-safe** (REJECT bid) | Zero noise philosophy: false negatives > false positives |
| Redis unavailable | **Degrade** to InMemoryCache | Search still works, just no cross-worker state sharing |
| ARQ worker unavailable | **Inline execution** | LLM/Excel generated in HTTP request cycle (slower but functional) |
| PNCP circuit breaker open | **Serve from cache + other sources** | Partial results > no results |

---

## 9. Monitoring and Observability

### 9.1 Prometheus Metrics

**`metrics.py`** exports 30+ metrics via `GET /metrics` (protected by `METRICS_TOKEN`):

| Category | Key Metrics |
|----------|-------------|
| **Search latency** | `smartlic_search_duration_seconds` (sector, uf_count, cache_status) |
| **Source latency** | `smartlic_fetch_duration_seconds` (source) |
| **LLM** | `smartlic_llm_call_duration_seconds`, `smartlic_llm_calls_total`, `smartlic_llm_tokens_total` |
| **Cache** | `smartlic_cache_hits_total` (level, freshness), `smartlic_cache_misses_total` |
| **Errors** | `smartlic_api_errors_total` (source, error_type), `smartlic_items_conversion_errors_total` |
| **Circuit breakers** | `smartlic_supabase_cb_state`, `smartlic_supabase_cb_transitions_total`, `CIRCUIT_BREAKER_STATE` |
| **Active** | `smartlic_active_searches`, `smartlic_http_responses_total` |
| **Filter** | `smartlic_filter_decisions_total` (stage, decision), `smartlic_filter_discard_rate` |
| **Pipeline state** | `smartlic_search_state_duration_seconds` (state) |
| **Bulkhead** | `BULKHEAD_ACQUIRE_TIMEOUT`, `SOURCE_ACTIVE_REQUESTS`, `SOURCE_POOL_EXHAUSTED` |
| **Redis** | `REDIS_AVAILABLE` gauge, `REDIS_FALLBACK_DURATION` gauge |
| **SSE** | `smartlic_sse_connection_errors_total` (error_type, phase) |

Graceful degradation: if `prometheus_client` not installed, all metrics become `_NoopMetric` (silent no-ops).

### 9.2 OpenTelemetry Distributed Tracing

**`telemetry.py`**:
- OTLP HTTP exporter (not gRPC, to avoid fork-unsafe C extensions)
- Auto-instrumentation: FastAPI + httpx
- Manual spans via `optional_span()` context manager for pipeline stages
- Sampling: 10% default (`OTEL_SAMPLING_RATE`)
- Health checks excluded from tracing (0% sample rate)
- Zero overhead when `OTEL_EXPORTER_OTLP_ENDPOINT` not set (no-op mode)
- Trace/span IDs injected into log records and SSE events

### 9.3 Sentry Error Tracking

**Backend** (`main.py`):
- `sentry-sdk[fastapi]` with `FastApiIntegration` + `StarletteIntegration`
- PII scrubbing via `scrub_pii()` callback (headers, user context, breadcrumbs, exception values)
- Transient error fingerprinting: httpx timeouts grouped under custom fingerprints, downgraded to "warning"
- Noise filtering: `CircuitBreakerOpenError`, PGRST205, PNCP 400 on page>1 all dropped
- Traces: 10% sampling, health checks excluded

**Frontend**:
- `@sentry/nextjs` with source maps
- CSP report endpoint (`/api/csp-report/route.ts`)

### 9.4 Structured Logging

**Production format:** JSON via `python-json-logger`:
```json
{"timestamp": "2026-03-07T12:00:00", "level": "INFO", "logger_name": "main", "message": "GET /buscar -> 200 (1234ms)", "request_id": "abc-123", "search_id": "def-456", "correlation_id": "ghi-789", "trace_id": "...", "span_id": "..."}
```

**Key features:**
- `CorrelationIDMiddleware` injects `request_id`, `search_id`, `correlation_id` into every log record
- `RequestIDFilter` logging filter ensures all records have correlation fields
- Gunicorn logs redirected from stderr to stdout via `logconfig_dict` (Railway classifies stderr as error)
- `log_sanitizer.py` provides: `mask_email()`, `mask_token()`, `mask_user_id()`, `mask_ip_address()`, `sanitize_dict()`, `sanitize_string()`

### 9.5 Health Endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /health` | Overall system health (always 200 for liveness), includes `ready` flag for startup gate |
| `GET /health/ready` | Readiness probe (returns 503 during startup) |
| `GET /v1/health/cache` | Admin: cache statistics and hit rates |
| `GET /sources/health` | Per-source availability status |
| Frontend `GET /api/health` | Frontend health proxy (always 200) |

---

## 10. Technical Debt Inventory

### 10.1 Architecture Debts

| ID | Severity | Issue | Location | Impact |
|----|----------|-------|----------|--------|
| TD-A01 | **High** | Routes mounted twice (versioned `/v1/` + legacy root) | `main.py` ~L710-778 | 61 `include_router` calls (33 versioned + 28 legacy). Doubles the route table. Sunset date 2026-06-01 set but no migration plan or frontend consumer uses legacy paths. |
| TD-A02 | **High** | `search_pipeline.py` is the new god module | `search_pipeline.py` (800+ lines) | After STORY-216 decomposition from main.py, absorbed all business logic. Each "stage" method is 50-100+ lines with nested try/catch. Should be further decomposed into stage classes. |
| TD-A03 | **High** | In-memory progress tracker not horizontally scalable | `progress.py` `_active_trackers` | Redis Streams mode exists but in-memory `asyncio.Queue` is the primary fallback. Two Railway web instances would have split progress state. |
| TD-A04 | **Medium** | 10+ background tasks in lifespan without lifecycle manager | `main.py` lifespan | Each task has manual create/cancel/await. No `TaskRegistry` abstraction. Adding/removing tasks requires touching 3+ locations. |
| TD-A05 | **Medium** | Dual HTTP client (sync + async) for PNCP | `pncp_client.py` | `PNCPClient` (sync/requests) and async httpx duplicate 1500+ lines of retry logic. Sync client used only as `asyncio.to_thread()` fallback. |
| TD-A06 | **Medium** | `main.py` still 820+ lines despite decomposition | `main.py` | Sentry init (100+ lines), exception handlers (80+ lines), middleware config, router registration (60+ lines), lifespan (200+ lines), health endpoints. Should extract Sentry config, exception handlers, and lifespan to separate modules. |
| TD-A07 | **Low** | Lead prospecting modules disconnected from main pipeline | `lead_prospecting.py`, `lead_scorer.py`, `lead_deduplicator.py`, `contact_searcher.py`, `cli_acha_leads.py` | 5 modules appear disconnected. Possibly dead code from feature exploration. |
| TD-A08 | **Low** | Frontend proxy route explosion | `frontend/app/api/` (58 routes) | Each backend endpoint gets a proxy route. No generic proxy pattern or API gateway abstraction. Adding a backend endpoint requires creating a new proxy file. |

### 10.2 Code Quality Issues

| ID | Severity | Issue | Location | Detail |
|----|----------|-------|----------|--------|
| TD-Q01 | **High** | `time.sleep(0.3)` in async context | `authorization.py:check_user_roles()` | Blocks the async event loop. Should be `await asyncio.sleep(0.3)`. |
| TD-Q02 | **Medium** | Global mutable singletons without cleanup | `auth.py:_token_cache`, `llm_arbiter.py:_arbiter_cache`, `filter.py:_filter_stats_tracker` | In-memory caches grow unbounded during long-running processes. LLM arbiter has LRU cap (5000) but auth cache and others do not. |
| TD-Q03 | **Medium** | Inconsistent error handling patterns | Various routes | Some routes return `JSONResponse` directly, others raise `HTTPException`. No consistent error response schema across all endpoints. |
| TD-Q04 | **Medium** | `config.py` is 500+ lines with mixed concerns | `config.py` | Contains: PNCP modality codes, retry config, CORS config, logging setup, feature flags, context vars, validation. Should split into `pncp_config.py`, `cors.py`, `feature_flags.py`. |
| TD-Q05 | **Low** | Hardcoded User-Agent references "BidIQ" | `pncp_client.py` | `"BidIQ/1.0 (procurement-search; contact@bidiq.com.br)"`. Misleading for API providers. |
| TD-Q06 | **Low** | Test files in backend root | `test_pncp_homologados_discovery.py`, `test_receita_federal_discovery.py`, `test_story_203_track2.py` | Test files outside `tests/` directory. Breaks convention. |
| TD-Q07 | **Low** | `pyproject.toml` references "bidiq-uniformes-backend" | `backend/pyproject.toml` | Old branding not updated. |

### 10.3 Missing Abstractions

| ID | Severity | Issue | Location | Recommendation |
|----|----------|-------|----------|----------------|
| TD-M01 | **Medium** | No background task lifecycle manager | `main.py` lifespan | Create a `TaskRegistry` class: register, start_all, stop_all, health_check. |
| TD-M02 | **Medium** | No API contract validation in CI | CI workflows | No CI step validates that frontend TypeScript types match backend OpenAPI schema. Drift detection only via snapshot diff (`openapi_schema.diff.json`). |
| TD-M03 | **Medium** | No feature flag UI for runtime toggling | `config.py` | 25+ flags loaded from env vars with 60s cache. Requires container restart or admin endpoint to change. Should have admin UI or Redis-backed runtime flags. |
| TD-M04 | **Low** | No pre-commit hooks | Repository root | No `.pre-commit-config.yaml`. Developers can commit code failing lint/type checks. |
| TD-M05 | **Low** | No backend linting enforcement in CI | `.github/workflows/` | `ruff` and `mypy` configured in `pyproject.toml` but not enforced in any CI workflow. |
| TD-M06 | **Low** | No generic API proxy abstraction on frontend | `frontend/app/api/` | Each endpoint has its own proxy file with boilerplate (token refresh, error handling). A shared `createProxyRoute()` utility would reduce 58 files to ~10. |

### 10.4 Scalability Concerns

| ID | Severity | Issue | Location | Impact |
|----|----------|-------|----------|--------|
| TD-S01 | **High** | Railway 1GB memory with 2 workers | `start.sh` | Each Gunicorn worker maintains in-memory caches (auth tokens, LLM decisions, plan capabilities, feature flags, filter stats). OOM kills observed historically. |
| TD-S02 | **High** | PNCP page size reduced to 50 | `pncp_client.py` | 10x more API calls vs previous 500/page. Health canary uses `tamanhoPagina=10` and cannot detect this limit change. |
| TD-S03 | **Medium** | In-memory auth token cache not shared across workers | `auth.py:_token_cache` | Each Gunicorn worker has its own cache. Not a correctness issue but wastes memory and causes duplicate Supabase Auth calls. |
| TD-S04 | **Medium** | No CDN for static assets | Infrastructure | Frontend served directly from Railway without edge caching. Images, JS bundles not CDN-accelerated. |
| TD-S05 | **Medium** | Single Supabase client singleton | `supabase_client.py` | `_supabase_client` is a module-level global. With Gunicorn workers (no --preload), each worker creates its own client. Pool configured for 50 connections but 2 workers = 100 potential connections against Supabase. |
| TD-S06 | **Low** | Search cache key does not include all filter parameters | `search_cache.py` | Cache key includes sector, UFs, dates but not status filter, modalidades, valor range, esferas. Different filter combinations share the same cache entry (filters applied post-cache). |

### 10.5 Security Observations

| ID | Severity | Issue | Location | Detail |
|----|----------|-------|----------|--------|
| TD-SEC01 | **Medium** | `unsafe-inline` and `unsafe-eval` likely in frontend CSP | `frontend/next.config.js` | Required by Next.js + Stripe.js but weakens Content Security Policy. Should evaluate nonce-based approach. |
| TD-SEC02 | **Medium** | Service role key for ALL backend DB operations | `supabase_client.py` | Backend bypasses RLS for all operations. Any backend vulnerability (SSRF, injection) exposes all user data. Consider per-user tokens for user-scoped operations. |
| TD-SEC03 | **Medium** | No webhook request timeout | `webhooks/stripe.py` | Long-running DB operations in webhook handler could block indefinitely. Stripe retries unacknowledged webhooks, potentially causing duplicate processing. |
| TD-SEC04 | **Low** | Excel temp files in frontend proxy | `frontend/app/api/buscar/route.ts` | Writes base64 Excel to `tmpdir()` as fallback. Not cleaned on crash, potential disk exhaustion. |
| TD-SEC05 | **Low** | Rate limiter in-memory store unbounded | `rate_limiter.py` | `_memory_store` has `MAX_MEMORY_STORE_SIZE=10_000` but cleanup only runs every 200 requests. Under heavy load, could accumulate stale entries. |
| TD-SEC06 | **Low** | `STRIPE_WEBHOOK_SECRET` not-set error only logged | `webhooks/stripe.py` | If secret is missing, `STRIPE_WEBHOOK_SECRET = None` and all webhook signature validations will fail at runtime. Should fail at startup. |

### 10.6 Testing Gaps

| ID | Severity | Issue | Detail |
|----|----------|-------|--------|
| TD-T01 | **Medium** | No integration tests against real APIs | All source clients tested with mocks only. No staging environment with real PNCP/PCP calls. API contract changes (like page size 500->50) can only be caught in production. |
| TD-T02 | **Medium** | E2E tests require production credentials | `e2e-tests/` use production Supabase/backend URLs. No isolated test environment. |
| TD-T03 | **Medium** | No load test in CI | `load-test.yml` exists but is manual-trigger only. No performance regression detection in PR pipeline. |
| TD-T04 | **Low** | Backend linting (`ruff`, `mypy`) not in CI gate | `ruff check .` and `mypy .` not enforced. Type errors can be merged. |
| TD-T05 | **Low** | Test pollution patterns documented but not prevented | `conftest.py` has autouse fixtures for `supabase_cb` reset, but `sys.modules` injection by ARQ tests still causes intermittent failures in isolation. |

### 10.7 Documentation Gaps

| ID | Severity | Issue | Detail |
|----|----------|-------|--------|
| TD-D01 | **Low** | No API documentation beyond auto-generated OpenAPI | API docs disabled in production (`ENVIRONMENT=production`). No public developer documentation. |
| TD-D02 | **Low** | Migration naming inconsistency | `supabase/migrations/` has mixed naming: `001_*` through `033_*` (sequential) + `20260220*` (timestamped). 73 total migrations. |
| TD-D03 | **Low** | No runbook for incident response | No documented procedures for: Supabase outage, Redis failure, PNCP API degradation, Railway OOM kills. Institutional knowledge in CLAUDE.md and MEMORY.md only. |
| TD-D04 | **Low** | `.env.example` may be stale | 25+ feature flags and config vars added incrementally. No automated check that `.env.example` contains all required vars. |

### 10.8 Dependency Concerns

| ID | Severity | Issue | Detail |
|----|----------|-------|--------|
| TD-DEP01 | **Medium** | `cryptography` pinned to 46.0.5 for fork-safety | Cannot upgrade without re-testing Gunicorn fork behavior. ES256/JWKS depends on this. |
| TD-DEP02 | **Medium** | `requests` library only used for sync PNCP fallback | `pncp_client.py` maintains a full sync `requests.Session` + `HTTPAdapter` + `urllib3.Retry` stack. If async client is reliable, `requests` can be removed (eliminating ~50KB of dependency). |
| TD-DEP03 | **Low** | `redis_client.py` deprecated but still importable | Shim module that redirects to `redis_pool`. Should be removed after confirming no imports remain. |
| TD-DEP04 | **Low** | `arq` not installed locally (mocked in tests via `sys.modules`) | Tests use `sys.modules["arq"] = MagicMock()`. Creates fragile test fixtures and masks real import errors. |

---

*End of System Architecture Document -- SmartLic v5.0*
*Generated 2026-03-07 by @architect (Atlas) during Brownfield Discovery Phase 1*
