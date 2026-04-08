# SmartLic System Architecture Document

## Executive Summary

**SmartLic** is a sophisticated public procurement intelligence platform for Brazilian licitacoes (public bids). Built with **FastAPI** (Python backend) and **Next.js** (TypeScript frontend), it provides real-time search, AI-powered bid analysis, subscription billing, and comprehensive monitoring for procurement opportunities across PNCP, PCP v2, and ComprasGov sources.

**Project Type:** Brownfield Discovery Phase 1
**Last Updated:** 2026-04-08
**Auditor:** @architect (Aria)
**Technology Stack:** FastAPI + Next.js + Supabase + PostgreSQL + Redis + OpenAI + Stripe + Railway

---

## Table of Contents

1. [Tech Stack Overview](#tech-stack-overview)
2. [Backend Architecture](#backend-architecture)
3. [Frontend Architecture](#frontend-architecture)
4. [Data Pipeline & Search Engine](#data-pipeline--search-engine)
5. [API Routes & Endpoints](#api-routes--endpoints)
6. [Database Schema & RLS](#database-schema--rls)
7. [Authentication & Authorization](#authentication--authorization)
8. [Billing & Subscription Management](#billing--subscription-management)
9. [Background Jobs & Cron](#background-jobs--cron)
10. [Caching Strategy](#caching-strategy)
11. [External Integrations](#external-integrations)
12. [Monitoring & Observability](#monitoring--observability)
13. [Infrastructure & Deployment](#infrastructure--deployment)
14. [Security Posture](#security-posture)
15. [Configuration & Feature Flags](#configuration--feature-flags)
16. [Known Issues & Debt](#known-issues--debt)

---

## Tech Stack Overview

### Backend Dependencies (Python 3.12)

| Component | Version | Purpose |
|-----------|---------|---------|
| **FastAPI** | 0.129.0 | Async web framework |
| **Uvicorn** | 0.41.0 | ASGI server (NO uvloop -- fork-safe) |
| **Gunicorn** | 23.0.0 | Application server (single-worker mode only) |
| **Pydantic** | 2.12.5 | Data validation & settings |
| **Python-multipart** | >=0.0.22 | Path traversal fix (CVE-2026-24486) |
| **Httpx** | 0.28.1 | Async HTTP client |
| **Supabase** | 2.28.0 | PostgreSQL + Auth backend |
| **PyJWT** | >=2.12.0 | ES256/JWKS JWT validation |
| **BCrypt** | >=4.0.0 | TOTP MFA code hashing |
| **Stripe** | 11.4.1 | Payment processing |
| **Redis** | 5.3.1 | Caching & feature flags |
| **OpenAI** | 1.109.1 | GPT-4.1-nano LLM integration |
| **ReportLab** | 4.4.0 | PDF report generation |
| **Openpyxl** | 3.1.5 | Excel generation |
| **OpenTelemetry** | 1.25+ | Distributed tracing (HTTP only) |
| **Prometheus Client** | >=0.20.0 | Metrics exporter |
| **ARQ** | 0.26+ | Async job queue (Redis-backed) |
| **Sentry SDK** | >=2.0.0 | Error tracking |
| **Resend** | >=2.0.0 | Transactional email |
| **Google APIs** | 2.190.0 | Google Sheets integration |
| **PyYAML** | >=6.0 | Configuration loading |

### Frontend Dependencies (Node.js 20.11)

| Component | Version | Purpose |
|-----------|---------|---------|
| **Next.js** | 16.1.6 | React framework (App Router) |
| **React** | 18.3.1 | UI library |
| **TypeScript** | 5.9.3 | Type safety |
| **Tailwind CSS** | 3.4.19 | Utility-first styling |
| **Supabase JS** | 2.95.3 | Client SDK (auth + DB) |
| **SWR** | 2.4.1 | Client-side data fetching with SWR cache |
| **Zod** | 4.3.6 | Runtime validation |
| **React Hook Form** | 7.71.2 | Form state management |
| **Sentry/Nextjs** | 10.38.0 | Error tracking |
| **Mixpanel** | 2.74.0 | Analytics |
| **Lucide React** | 0.563.0 | Icon library |
| **Recharts** | 3.7.0 | Data visualization |
| **Framer Motion** | 12.33.0 | Animations |
| **DnD Kit** | 6.3.1+ | Drag-and-drop (pipeline) |

### Infrastructure

| Component | Purpose |
|-----------|---------|
| **PostgreSQL 17** | Supabase-managed database |
| **Redis** | Queue + cache layer |
| **Railway** | Deployment platform (web + worker + frontend) |
| **Docker** | Containerization (multi-stage builds) |

---

## Backend Architecture

### Directory Structure

```
backend/
+-- main.py                          # Entry point (thin facade, 31 LOC)
+-- startup/                         # App initialization
|   +-- app_factory.py              # FastAPI app creation
|   +-- lifespan.py                 # Startup/shutdown hooks
|   +-- middleware_setup.py         # CORS, logging, metrics
|   +-- routes.py                   # Route registration
|   +-- endpoints.py                # Root endpoints
|   +-- exception_handlers.py       # Custom error handling
|   +-- sentry.py                   # Sentry integration
+-- config/                          # Configuration system
|   +-- base.py                     # Logging, env validation
|   +-- features.py                 # Feature flags (100+ flags)
|   +-- pipeline.py                 # Search pipeline config
|   +-- pncp.py                     # PNCP client config
|   +-- cors.py                     # CORS policy
+-- routes/                          # 52 route modules (144 endpoints)
|   +-- search.py                   # POST /buscar (main search)
|   +-- search_sse.py              # GET /buscar-progress SSE stream
|   +-- search_state.py            # Async search state & results
|   +-- search_status.py           # Status, retry, cancel endpoints
|   +-- billing.py                 # Stripe checkout & plans
|   +-- user.py                    # Profile, preferences
|   +-- alerts.py                  # Smart alerts system
|   +-- analytics.py               # Usage analytics
|   +-- health.py                  # Health checks & readiness
|   +-- admin_*.py                 # Admin operations
|   +-- feature_flags.py           # Feature flag management
|   +-- ... (40+ more)
+-- schemas/                         # Pydantic models
+-- services/                        # Business logic
+-- search_pipeline.py               # 7-stage orchestrator
+-- search_context.py               # Intermediate state container
+-- pipeline/                        # Pipeline stages
|   +-- stages/
|   |   +-- validate.py            # Stage 1: Input validation
|   |   +-- prepare.py             # Stage 2: Sector/keywords
|   |   +-- execute.py             # Stage 3: Multi-source fetch
|   |   +-- filter_stage.py        # Stage 4: Keyword/rules filter
|   |   +-- enrich.py              # Stage 5: Data enrichment
|   |   +-- post_filter_llm.py    # Stage 6a: LLM refinement
|   |   +-- generate.py            # Stage 6b: Output generation
|   |   +-- persist.py             # Stage 7: DB persistence
|   +-- cache_manager.py           # Cache orchestration
|   +-- helpers.py                 # Pipeline utilities
|   +-- tracing.py                 # Span instrumentation
+-- ingestion/                       # ETL pipeline (PNCP data)
|   +-- crawler.py                 # Web scraper for PNCP
|   +-- transformer.py             # Data transformation
|   +-- loader.py                  # Bulk insert to pncp_raw_bids
|   +-- checkpoint.py              # Resume capability
|   +-- scheduler.py               # Cron scheduling
|   +-- config.py                  # Ingestion settings
+-- clients/                         # External API clients
|   +-- pncp/
|   |   +-- async_client.py       # Async PNCP API
|   |   +-- sync_client.py        # Sync PNCP API
|   |   +-- circuit_breaker.py    # Resilience pattern
|   |   +-- retry.py              # Exponential backoff
|   |   +-- adapter.py            # Response normalization
|   +-- portal_compras_client.py  # PCP v2 integration
|   +-- compras_gov_client.py     # ComprasGov v3 API
|   +-- sanctions.py              # Sanctions list checker
+-- cache/                           # Multi-tier caching
|   +-- manager.py                # Cache orchestration
|   +-- redis.py                  # Redis L2 cache
|   +-- memory.py                 # In-memory L1 cache
|   +-- supabase.py               # Supabase table cache
|   +-- swr.py                    # Stale-while-revalidate
+-- auth.py                          # JWT validation (ES256/JWKS)
+-- authorization.py                 # Role-based access control
+-- quota.py                         # Plan-based quotas (65KB)
+-- rate_limiter.py                 # Per-user rate limiting
+-- llm.py                           # OpenAI integration
+-- llm_arbiter.py                  # Classification orchestrator
+-- job_queue.py                     # ARQ facade + enqueue
+-- jobs/                            # Background job implementations
|   +-- queue/                      # Async job definitions
|   +-- cron/                       # Scheduled tasks
+-- metrics.py                       # Prometheus metrics (35KB)
+-- health.py                        # Health check endpoints
+-- excel.py                         # Excel report generation
+-- pdf_report.py                    # PDF report generation
+-- webhooks/                        # Stripe webhooks
+-- Dockerfile                       # Multi-stage build
```

### Core Modules Overview

#### `main.py` (31 LOC)
- Entry point for uvicorn/gunicorn
- Imports `startup/app_factory.py` to create the FastAPI instance
- Enables faulthandler for C extension crash diagnostics

#### `search_pipeline.py` (148 LOC)
- **7-stage orchestrator** for procurement search
- Uses state machine for async search (GTM-RESILIENCE-A04)
- Emits Prometheus metrics at each stage
- Supports queue mode (offload LLM/Excel to ARQ workers)

#### `auth.py` (150+ LOC)
- JWT validation with ES256/JWKS support (STORY-227)
- Two-tier cache: L1 in-memory (60s) + L2 Redis (5m)
- Local JWT validation (no API calls) with public key caching

#### `quota.py` (65+ KB)
- Plan-based usage quotas (STORY-203 SYS-M04)
- Atomic check-and-increment via PostgreSQL function
- Circuit breaker integration for Supabase unavailability (fail-open)

---

## Data Pipeline & Search Engine

### 3-Layer Architecture

```
+------------------------------------------------------------------+
| User Request (POST /buscar with filters)                          |
+-----------------------------+------------------------------------+
                              |
          +-------------------v------------------+
          |  Layer 1: Search Pipeline            |  (search_pipeline.py)
          |  +-- Validate request                |
          |  +-- Prepare keywords                |  7 Stages
          |  +-- Execute (multi-source)          |
          |  +-- Filter results                  |
          |  +-- Enrich data                     |
          |  +-- Generate output                 |
          |  +-- Persist to DB                   |
          +-------------------+------------------+
                              |
          +-------------------v------------------+
          |  Layer 2: Data Sources               |  (clients/)
          |  +-- PNCP (primary)                  |
          |  +-- PCP v2 (secondary)              |  Multi-source
          |  +-- ComprasGov v3 (tertiary)        |  parallel fetch
          |  +-- Datalake (fallback)             |
          +-------------------+------------------+
                              |
          +-------------------v------------------+
          |  Layer 3: Caching (SWR)              |  (cache/)
          |  +-- Supabase RLS table              |
          |  +-- Redis cluster                   |  3-tier cache
          |  +-- In-memory (local)               |
          |  +-- Stale-while-revalidate          |
          +--------------------------------------+
```

### Stage Details

| Stage | Module | Purpose | Output |
|-------|--------|---------|--------|
| 1. Validate | validate.py | Request validation, auth, quotas | `ctx.is_admin`, `ctx.quota_info` |
| 2. Prepare | prepare.py | Load sector keywords, parse terms | `ctx.sector`, `ctx.active_keywords` |
| 3. Execute | execute.py (58KB) | Parallel multi-source fetch | `ctx.licitacoes_raw`, `ctx.data_sources` |
| 4. Filter | filter_stage.py (20KB) | Keyword matching, exclusion rules | `ctx.licitacoes_filtradas`, `ctx.filter_stats` |
| 5. Enrich | enrich.py | Sanctions, status inference, CNAE | Enhanced licitacoes |
| 6a. LLM | post_filter_llm.py | Zero-match reclassification (batch) | Additional matches |
| 6b. Generate | generate.py (27KB) | Excel/PDF, API response | `ctx.response`, `ctx.excel_base64` |
| 7. Persist | persist.py | Save session, log analytics | `ctx.session_id` |

---

## API Routes & Endpoints

### Route Summary (~144 endpoints across 52 modules)

#### Core Search
```
POST   /buscar                              Search (main)
GET    /buscar-progress/{id}               Progress stream (SSE)
POST   /v1/search/{id}/status              Status & results
POST   /v1/search/{id}/cancel              Cancel search
POST   /v1/search/{id}/retry               Retry failed search
GET    /v1/search/{id}/results             Get results
POST   /v1/search/{id}/excel-download      Excel link
```

#### Billing & Subscription
```
GET    /plans                               List plans
POST   /checkout                            Create checkout session
GET    /subscription                        Current subscription
POST   /cancel-subscription                 Cancel subscription
GET    /invoices                            Invoice history
```

#### Authentication
```
POST   /auth/signup                         Email signup
POST   /auth/login                          Email login
POST   /auth/logout                         Logout
POST   /auth/refresh                        Refresh token
POST   /auth/google                         Google OAuth
POST   /auth/mfa/setup                      Setup TOTP
POST   /auth/mfa/verify                     Verify TOTP code
```

#### User & Profile
```
GET    /user/profile                        Get profile
PATCH  /user/profile                        Update profile
GET    /user/preferences                    Get preferences
POST   /user/feedback                       Submit feedback
GET    /user/quota                          Check quota usage
```

#### Alerts
```
POST   /alerts                              Create alert
GET    /alerts                              List alerts
PATCH  /alerts/{id}                         Update alert
DELETE /alerts/{id}                         Delete alert
POST   /alerts/{id}/test                    Test alert
```

#### Admin
```
GET    /admin/users                         List users
PATCH  /admin/users/{id}/quota              Set quota
POST   /admin/cache/clear                   Clear cache
POST   /admin/feature-flags/{flag}          Toggle feature flag
```

#### Health & Monitoring
```
GET    /health                              Health check
GET    /health/ready                        Readiness probe
GET    /health/live                         Liveness probe
GET    /metrics                             Prometheus metrics
```

---

## Authentication & Authorization

### JWT Flow

1. **Signup/Login** -> Supabase Auth issues JWT
2. **Token Format:** ES256 algorithm, public key cached from Supabase JWKS endpoint (5m TTL)
3. **Validation (auth.py):** L1 cache (in-memory, 60s) -> L2 cache (Redis, 5m) -> local validation with public key

### Role-Based Access Control

| Role | Permissions |
|------|-------------|
| **User (default)** | Search, alerts, profile |
| **Trial User** | 10 searches/month, basic features |
| **Premium** | Unlimited searches, all features |
| **Admin** | User management, feature flags, metrics |
| **Master** | System-wide operations |

---

## Billing & Subscription Management

### Plans & Pricing (STORY-277/360)

| Plan | Price | Billing Periods |
|------|-------|-----------------|
| **Free Trial** | R$0 | 14 dias |
| **SmartLic Pro** | R$397/mes | Mensal, Semestral (10%), Anual (25%) |
| **Consultoria** | R$997/mes | Mensal, Semestral (10%), Anual (20%) |

### Stripe Integration
- Webhook: `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`, `invoice.payment_failed`
- Atomic quota check via PostgreSQL function (prevents TOCTOU race conditions)
- 3-day grace period for subscription gaps

---

## Background Jobs & Cron

### ARQ Job Queue (Redis-backed)

| Job | Purpose |
|-----|---------|
| `search_job` | Execute full pipeline in background |
| `llm_summary_job` | Generate LLM summary asynchronously |
| `excel_generation_job` | Generate Excel file |
| `cache_refresh_job` | Update stale cache entries |
| `email_alerts_job` | Send saved search alerts |

### Cron Jobs

| Job | Interval | Purpose |
|-----|----------|---------|
| Alerts Runner | 5 min | Fetch matches, send notifications |
| Trial Sequence | 3 hours | Onboarding email sequence |
| Cache Cleanup | 1 hour | Remove expired entries |
| Cache Warmup | 6 hours | Pre-fetch top sectors |
| Reconciliation | 12 hours | Sync Stripe subscriptions |
| Health Canary | 5 min | Check PNCP API health |

---

## Caching Strategy

### Multi-Tier SWR Cache

```
Layer 3: Supabase     (cold, persistent -- search_cache table)
    | miss/expired
Layer 2: Redis        (warm, shared -- 24h TTL)
    | miss/expired
Layer 1: Memory       (hot, local -- 5m TTL)
    | miss
    -> Execute (fetch from APIs)
    -> Refresh all layers
```

### Fallback Strategy (GTM-RESILIENCE-A04)
1. Fresh cache -> Serve if <24h old
2. Stale cache -> Serve + background refresh
3. Fallback date range -> Try adjacent dates
4. Datalake -> Query `pncp_raw_bids` if all sources fail
5. Empty result -> Return 0 matches if all layers exhausted

---

## External Integrations

| Integration | Purpose | Client |
|-------------|---------|--------|
| **PNCP API** | Primary data source (public bids) | `clients/pncp/async_client.py` |
| **PCP v2** | Secondary source (Sao Paulo) | `clients/portal_compras_client.py` |
| **ComprasGov v3** | Tertiary source | `clients/compras_gov_client.py` |
| **OpenAI GPT-4.1-nano** | Classification + summaries | `llm.py`, `llm_arbiter.py` |
| **Stripe** | Billing + webhooks | `webhooks/stripe.py` |
| **Supabase Auth** | Email + Google OAuth + MFA | `auth.py` |
| **Google Sheets** | Export results to Drive | `google_sheets.py` |
| **Resend** | Transactional emails | `email_service.py` |
| **Sentry** | Error tracking | `startup/sentry.py` |

---

## Monitoring & Observability

### Prometheus Metrics

**Histograms (Latency):**
- `smartlic_search_duration_seconds` (sector, uf_count, cache_status)
- `smartlic_fetch_duration_seconds` (source)
- `smartlic_filter_duration_seconds` (mode)
- `smartlic_llm_latency_seconds` (model, phase)
- `smartlic_cache_get_latency_seconds` (layer, hit)

**Counters:**
- `smartlic_searches_total` (sector, result_status, search_mode)
- `smartlic_cache_hits_total` (level)
- `smartlic_http_requests_total` (method, path, status_code)
- `smartlic_auth_failures_total` (reason)
- `smartlic_quota_exceeded_total` (plan)

**Gauges:**
- `smartlic_active_searches`
- `smartlic_auth_cache_size`
- `smartlic_queue_length`
- `smartlic_worker_alive`

### Structured Logging
- JSON format in production, text in development
- User IDs masked with `log_sanitizer.mask_user_id()`
- No PII in logs

### OpenTelemetry Tracing
- FastAPI + httpx instrumentation
- OTLP HTTP exporter (NOT gRPC -- fork-safe)
- Per-stage spans in search pipeline

### Health Checks
- `GET /health/ready` (readiness: supabase, redis, queue)
- `GET /health/live` (liveness: uptime)
- `GET /health` (basic: version)
- Health Canary: 5-min PNCP API ping with circuit breaker

---

## Infrastructure & Deployment

### Docker (Multi-stage builds)

**Backend:** Python 3.12-slim, no uvloop (fork-safe), single-worker mode, non-root user (appuser)

**Frontend:** Node.js 20.11-alpine, standalone output, 512MB heap limit, non-root user (nextjs)

### Railway Configuration

**Backend:** Dockerfile build, `uvicorn main:app`, healthcheck at `/health`, 300s timeout, zero-downtime deploy (45s overlap, 120s drain)

**Frontend:** Dockerfile build, standalone Next.js server

### CI/CD (GitHub Actions)
- `deploy.yml`: Auto-deploy on push to main
- `backend-tests.yml`: pytest + coverage + lint + security scan
- `frontend-tests.yml`: jest + build + Lighthouse
- `e2e.yml`: Daily Playwright tests

### Deployment Topology

```
Internet
    |
    +-> Frontend (Railway) -- Next.js 16 standalone
    |
    +-> Backend (Railway) -- Uvicorn single-worker
    
Supabase (Managed) -- PostgreSQL + Auth + RLS
Redis (Railway) -- Cache + Queue
External APIs -- PNCP, PCP v2, ComprasGov, Stripe, OpenAI, Resend, Sentry
```

---

## Security Posture

### Authentication & Authorization
- Short-lived JWTs (60m) + refresh token rotation
- Atomic quota operations (prevent TOCTOU bypass)
- RLS policies enforce user isolation
- HTTPBearer auth on all protected routes

### Data Protection
- PII sanitization in logs
- Supabase PostgREST parameterization (no raw SQL)
- React escaping + CSP headers
- Secrets in Railway (not in code/env files)

### Infrastructure Security
- Non-root containers (UID 1001)
- Removed fork-unsafe C extensions (grpcio, httptools, uvloop)
- Dependabot + CVE scanning
- PCI-DSS compliance via Stripe (no card data stored)

### Fixed CVEs
- CVE-2026-24486 (Path Traversal) -- python-multipart >=0.0.22
- CVE-2026-26007, CVE-2026-34073 -- cryptography >=46.0.6
- CVE-2026-32597 (JWT header bypass) -- PyJWT >=2.12.0

---

## Configuration & Feature Flags

### Feature Flag System (100+ flags)
- Runtime-reloadable via database + 60s cache
- Categories: LLM/Classification, Data Sources, Cache, Search Pipeline, Billing/Trial
- Access: `get_feature_flag("FLAG_NAME")` in Python
- Admin toggle: `POST /admin/feature-flags/{flag}`

### Key Feature Flags
- `LLM_ARBITER_ENABLED`, `LLM_ZERO_MATCH_ENABLED` (AI classification)
- `DATALAKE_ENABLED`, `DATALAKE_QUERY_ENABLED` (data sources)
- `CACHE_WARMING_ENABLED`, `CACHE_REFRESH_ENABLED` (caching)
- `SEARCH_ASYNC_ENABLED` (async pipeline)
- `TRIAL_PAYWALL_ENABLED` (billing)

---

## Known Issues & Debt

### Critical Issues (Resolved)

| ID | Description |
|----|-------------|
| CRIT-SIGSEGV-v2 | Uvicorn single-worker mode (no forking) |
| CRIT-041 | Removed fork-unsafe C extensions |
| CRIT-033 | ARQ worker health detection + inline fallback |
| CRIT-072 | Async search deadline + time budget checks |

### Open Technical Debt

| ID | Priority | Description |
|----|----------|-------------|
| SYS-023 | Medium | Per-user Supabase tokens for user-scoped operations |
| DEBT-018 | Open | Cryptography fork-safe testing required |
| DEBT-325 | Open | USD/BRL exchange rate hardcoded (should be dynamic) |

---

## Architecture Decisions

### Why Single-Worker Uvicorn?
C extensions (cryptography, chardet) are fork-unsafe. In-memory state not shareable. Scaling via horizontal scaling (multiple Railway services).

### Why SWR Over Eager Refresh?
Fast response time (<50ms cache hit). Graceful degradation (stale > empty). Background refresh prevents thundering herd.

### Why Multiple Cache Layers?
L1 (5m): Worker-local, fastest. L2 (24h): Shared via Redis. L3 (persistent): Supabase, survives deploys.

### Why ARQ Over Celery?
Simpler API, Redis-only (no RabbitMQ), native asyncio, smaller image (Railway coldstart).

---

## Performance Metrics (Observed)

| Metric | Target | Actual |
|--------|--------|--------|
| Search Latency (p50) | <5s | 3-4s (cache hit) |
| Search Latency (p99) | <30s | 15-20s (multi-source) |
| Cache Hit Rate | >70% | 65-75% |
| Auth Cache Hit | >90% | 92-96% |
| PNCP API Availability | >95% | 94% |
| Cold Start | <30s | 10-15s |
| ARQ Job Processing | <60s | 45s avg |

---

**Document Generated:** 2026-04-08
**Architecture Phase:** Brownfield Discovery Phase 1 (Comprehensive)
**Deployment Platform:** Railway
**Database:** Supabase PostgreSQL
**Cache:** Redis
**Observability:** Prometheus + Sentry + OpenTelemetry
