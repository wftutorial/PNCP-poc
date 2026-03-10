# SmartLic — System Architecture Documentation

**Project Stage:** POC Advanced (v0.5) in Production — Beta with trials, pre-revenue  
**Last Updated:** 2026-03-10
**Analysis Scope:** Brownfield discovery Phase 1 — Complete system documentation (updated with actual code analysis)

## Executive Summary

SmartLic is a **B2G SaaS platform** that automates procurement opportunity discovery and analysis across Brazilian government sources (PNCP, PCP v2, ComprasGov v3). The system employs a **multi-source pipeline** with AI classification, viability assessment, and opportunity pipeline management.

**Key Stats (verified 2026-03-10):**
- 192 backend Python files, 72,693 total LOC (Python 3.12, FastAPI 0.129)
- 28 frontend pages, 328 TS/TSX files (Next.js 16, React 18, TypeScript 5.9)
- 33 route modules in `backend/routes/`, 58 API proxy routes in `frontend/app/api/`
- 169 backend test files (5131+ passing), 135 frontend test files (2681+ passing)
- 3 data sources with per-source circuit breakers + bulkheads
- 88 Supabase migrations + 7 backend migrations
- 50+ defined feature flags
- 17 GitHub Actions workflows
- 27 custom hooks in `frontend/hooks/`
- Production monitoring via Prometheus, OpenTelemetry, Sentry

---

## 1. Technology Stack

### Backend
| Component | Technology | Version |
|-----------|-----------|---------|
| **Runtime** | Python | 3.12 |
| **Web Framework** | FastAPI | 0.129 |
| **ASGI Server** | Uvicorn + Gunicorn | 0.41.0 / 23.0.0 |
| **Request Validation** | Pydantic | 2.12.5 |
| **HTTP Client** | httpx (async), requests (sync fallback) | 0.28.1, 2.32.3 |
| **Database** | Supabase (PostgreSQL 17) | 2.28.0 |
| **Cache** | Redis (in-memory L1 + Redis L2) | 5.3.1 |
| **Job Queue** | ARQ | 0.26+ |
| **LLM** | OpenAI (GPT-4.1-nano) | 1.109.1 |
| **Auth** | Supabase Auth + JWT (ES256/HS256) | JWT 2.11.0 |
| **Billing** | Stripe | 11.4.1 |
| **Email** | Resend (transactional) | 2.0.0+ |
| **Exports** | Google Sheets API, openpyxl (Excel), reportlab (PDF) | Various |
| **Monitoring** | Prometheus, OpenTelemetry, Sentry | Latest stable |
| **Logging** | JSON-structured (python-json-logger) | 2.0.4+ |

### Frontend
| Component | Technology | Version |
|-----------|-----------|---------|
| **Framework** | Next.js | 16.1.6 |
| **React** | React | 18.3.1 |
| **Language** | TypeScript | 5.9 |
| **Styling** | Tailwind CSS 3 + Tailwind Merge | 3.x |
| **Auth** | Supabase SSR | 0.8.0 |
| **State Management** | SWR (Stale-While-Revalidate) + React Context | 2.4.1 |
| **Real-time Updates** | Server-Sent Events (SSE) | Native |
| **Charts** | Recharts | 3.7.0 |
| **Drag-Drop** | @dnd-kit (pipeline kanban) | 6.3.1+ |
| **Forms** | react-hook-form + Zod validation | 7.71.2, 4.3.6 |
| **Animations** | Framer Motion | 12.33.0 |
| **Onboarding** | Shepherd.js (guided tours) | 14.5.1 |
| **Analytics** | Sentry, Mixpanel | 10.38.0, 2.74.0 |
| **Testing** | Jest + @testing-library/react + Playwright | 29.7.0, Playwright 1.58.2 |

### Infrastructure
| Component | Technology | Status |
|-----------|-----------|--------|
| **Hosting** | Railway (web + worker + frontend) | Production |
| **Database** | Supabase Cloud (PostgreSQL 17) | Production |
| **Cache/Queue** | Redis (Upstash on Railway) | Production |
| **CI/CD** | GitHub Actions (17 workflows) | Production |
| **Secrets** | GitHub repo encrypted (SUPABASE_*, OPENAI_*, STRIPE_*, etc.) | Secure |
| **Monitoring** | Prometheus scrape, Sentry.io, OpenTelemetry export | Production |

---

## 2. Backend Architecture

### 2.1 High-Level Structure

```
backend/                                 # 192 Python files, 72,693 total LOC
├── main.py                              # App entry — thin wrapper (80 lines, DEBT-107)
├── config/                              # Configuration (decomposed from config.py)
│   ├── __init__.py                      # Re-export hub (all config symbols)
│   ├── base.py                          # Logging, env validation
│   ├── pncp.py                          # PNCP, PCP, ComprasGov source config
│   ├── features.py                      # Feature flags (50+ flags)
│   ├── pipeline.py                      # Cache, warmup, cron config
│   └── cors.py                          # CORS origins
├── startup/                             # Startup orchestration (9 files, DEBT-107)
│   ├── app_factory.py                   # FastAPI create_app()
│   ├── sentry.py                        # PII scrubbing, noise filtering, init
│   ├── lifespan.py                      # Startup/shutdown lifecycle
│   ├── middleware_setup.py              # CORS, custom & inline HTTP middlewares
│   ├── routes.py                        # Router imports & registration
│   ├── exception_handlers.py           # Validation + global exception handlers
│   ├── endpoints.py                     # /, /v1/setores
│   └── state.py                         # Shared process state
├── routes/                              # 33 route modules
│   ├── search.py                        # POST /buscar (2177 lines — LARGEST)
│   ├── alerts.py                        # Alert management (692 lines)
│   ├── user.py                          # Profile, auth state (674 lines)
│   ├── blog_stats.py                    # Blog analytics (603 lines)
│   ├── pipeline.py                      # Kanban CRUD (432 lines)
│   ├── messages.py                      # Messaging (395 lines)
│   ├── feature_flags.py                 # Runtime flags (388 lines)
│   ├── analytics.py                     # Usage dashboards (373 lines)
│   └── [25 more modules...]            # billing, mfa, organizations, etc.
├── clients/                             # Data source clients (8 files, 5019 LOC)
│   ├── base.py                          # SourceAdapter interface (413 lines)
│   ├── portal_transparencia_client.py   # Portal da Transparencia (938 lines)
│   ├── compras_gov_client.py            # ComprasGov v3 (838 lines)
│   ├── querido_diario_client.py         # Querido Diario (801 lines)
│   ├── qd_extraction.py                 # QD data extraction (710 lines)
│   ├── portal_compras_client.py         # PCP v2 (646 lines)
│   └── sanctions.py                     # Sanctions check (639 lines)
├── pipeline/                            # Search pipeline stages (13 files, 3530 LOC)
│   ├── stages/
│   │   ├── execute.py                   # Stage 3: Multi-source fetch (1186 lines)
│   │   ├── generate.py                  # Stage 6: Excel, SSE emit (531 lines)
│   │   ├── filter_stage.py              # Stage 4: Keyword + LLM filter (359 lines)
│   │   ├── validate.py                  # Stage 1: Input validation (212 lines)
│   │   ├── persist.py                   # Stage 7: Cache, audit (167 lines)
│   │   ├── prepare.py                   # Stage 2: State prep (144 lines)
│   │   └── enrich.py                    # Stage 5: Status, viability (115 lines)
│   ├── cache_manager.py                 # Two-level cache orchestration (345 lines)
│   ├── helpers.py                       # Pipeline utilities (246 lines)
│   ├── worker.py                        # Async worker setup (79 lines)
│   └── tracing.py                       # OpenTelemetry spans (53 lines)
├── search_pipeline.py                   # 7-stage orchestrator (169 lines)
├── pncp_client.py                       # PNCP API client (2580 lines — 2nd largest)
├── search_cache.py                      # Search result caching (2512 lines)
├── job_queue.py                         # ARQ background jobs (2189 lines)
├── filter.py                            # Keyword filter FACADE (2141 lines)
├── schemas.py                           # Pydantic models (2119 lines)
├── cron_jobs.py                         # Scheduled tasks (2039 lines)
├── quota.py                             # Billing quota enforcement (1622 lines)
├── llm_arbiter.py                       # LLM classification (1271 lines)
├── filter_keywords.py                   # Keyword matching core (1151 lines)
├── metrics.py                           # Prometheus metrics defs (1002 lines)
├── health.py                            # Health check logic (960 lines)
├── admin.py                             # Admin panel backend (957 lines)
├── consolidation.py                     # Multi-source dedup (917 lines)
├── pdf_report.py                        # PDF report generation (895 lines)
├── progress.py                          # SSE progress tracking (887 lines)
├── filter_density.py                    # Sector context scoring (367 lines)
├── filter_uf.py                         # UF filtering (303 lines)
├── filter_status.py                     # Status filtering (289 lines)
├── filter_value.py                      # Value range filtering (162 lines)
├── filter_stats.py                      # Filter performance tracking (249 lines)
├── auth.py                              # JWT validation + token cache (519 lines)
├── cache.py                             # Redis L1 + L2 abstraction
├── bid_analyzer.py                      # Per-bid intelligence (437 lines)
├── item_inspector.py                    # Deep item analysis (466 lines)
├── bulkhead.py                          # Concurrency isolation
└── tests/                               # 169 test files, 5131+ passing

Supabase Migrations: 88 files
Backend Migrations: 7 files
```

### 2.2 Core Modules Deep Dive

#### **search_pipeline.py** — 7-Stage Orchestrator
**Lines:** <200 | **Responsibility:** Orchestrate multi-source search  
**Pattern:** State machine with pipeline stages

```python
# Pseudo-flow:
run() 
  → stage_validate()       # Input validation, quota check
  → stage_prepare()        # Load cache, prepare state
  → stage_execute()        # Multi-source fetch (parallel)
  → stage_filter()         # Keyword + LLM filtering
  → stage_enrich()         # Status inference, viability, summaries
  → stage_generate()       # Excel, PDF, Google Sheets
  → stage_persist()        # Cache, audit, cleanup
```

**Key Features:**
- OpenTelemetry tracing per stage
- Timeout chain validation at startup
- State machine tracking (7 states: VALIDATING, FETCHING, FILTERING, etc.)
- Active search counter (Prometheus gauge)
- Cache status tracking (hit/miss/stale)

**Critical Notes:**
- Each stage is in `pipeline/stages/` (decomposed per DEBT-015)
- Stage outputs validated with `validate_stage_outputs()`
- Time budget checks after filtering (early exit if over budget)
- All metrics exported for SLO tracking

---

#### **pncp_client.py** — Resilient HTTP Client
**Lines:** 2580 | **Responsibility:** Fetch from PNCP API
**Pattern:** Retry + circuit breaker + bulkhead
**DEBT NOTE:** Reads 14 env vars directly via `os.environ.get()` instead of using `config/` package

**Key Config (per CLAUDE.md):**
```python
# PNCP API Limits
PNCP_MAX_PAGE_SIZE = 50                 # Hard limit (reduced Feb 2026)
PNCP_BATCH_SIZE = 5                     # UF batching (GTM-FIX-031)
PNCP_BATCH_DELAY_S = 2.0               # Delay between batches

# Circuit Breaker (STORY-252, GTM-INFRA-001)
PNCP_CIRCUIT_BREAKER_THRESHOLD = 15    # Trips faster (was 50)
PNCP_CIRCUIT_BREAKER_COOLDOWN = 60s    # Was 120s

# Timeout Chain (strict decreasing validation)
PNCP_TIMEOUT_PER_MODALITY = 20s        # 4 modalities in parallel
PNCP_TIMEOUT_PER_UF = 30s              # >= 4 × 20s with margin
PNCP_TIMEOUT_PER_SOURCE = 180s         # Per-source total
CONSOLIDATION_TIMEOUT = 300s           # All sources combined
PIPELINE_TIMEOUT = 360s                # Entire pipeline
```

**Error Handling:**
- HTTP 422 is retryable (intermittent PNCP issue)
- Exponential backoff with jitter
- Circuit breaker: 15 failures → open for 60s
- **New in Feb 2026:** Reduced `tamanhoPagina` validation (API rejects >50)
- Redis-backed circuit breaker toggle (B-06 feature)

**Data Deduplication:**
- PNCP (priority 1) wins over PCP (priority 2)
- Dedup key: (id_licitacao, modalidade, setor_id)
- Merge-enrichment from lower-priority duplicates (HARDEN-006)

---

#### **filter.py** — Keyword Matching Engine (FACADE)
**Lines:** 2141 (facade) + 2521 (5 sub-modules) = 4662 total | **Responsibility:** Sector-based filtering
**Pattern:** Keyword density scoring + LLM arbiter fallback
**Structure:** Decomposed (DEBT-110 AC4) into `filter_keywords.py` (1151), `filter_density.py` (367),
`filter_status.py` (289), `filter_value.py` (162), `filter_uf.py` (303). Facade re-exports all symbols.

**Validation:**
```python
validate_terms(terms: list[str]) → {
    'valid': [...],      # Will be used
    'ignored': [...],    # Rejected
    'reasons': {...}     # Rejection motives
}
```

**Critical Invariant:** Terms NEVER in both `valid` AND `ignored` (asserts if violated)

**Filtering Pipeline (order matters):**
1. UF check (fastest)
2. Value range check
3. Keyword matching (density scoring: high/medium/low)
4. LLM zero-match classification (for 0% keyword density)
5. Status/date validation
6. Viability assessment (post-filter)

**Keyword Sources:**
- 15 sectors defined in `backend/sectors_data.yaml`
- Each sector has: keywords (main), keywords_excluir (exclusions), viability_value_range
- Lazy-load filter stats tracker (circular dependency prevention)

**Portuguese Stopwords:** 65+ common words stripped (prepositions, articles, etc.)

---

#### **llm_arbiter.py** — AI Classification
**Lines:** 1271 | **Responsibility:** False positive elimination + zero-match classification
**Pattern:** Structured output + dual-cache (L1 in-memory, L2 Redis)

**Models:**
- **gpt-4.1-nano** (default) — 33% cheaper than gpt-4o-mini
- Max tokens: 800 (DEBT-101 AC5: increased from 300 to prevent JSON truncation)
- Temperature: 0 (deterministic)
- Timeout: 5s (DEBT-103 AC1: reduced from 15s to 5s, still 5x p99)

**LLMClassification Schema (D-02 AC1):**
```python
class LLMClassification(BaseModel):
    classe: Literal["SIM", "NAO"]        # Final decision
    confianca: int                       # 0-100% confidence
    evidencias: list[str]                # Up to 3 citations from text
    motivo_exclusao: Optional[str]       # Why rejected (if NAO)
```

**Cache Strategy:**
- **L1:** In-memory OrderedDict, 5000 entries max (LRU eviction)
- **L2:** Redis with 1h TTL, MD5-hashed input keys
- Fallback: REJECT on LLM failure (zero-noise philosophy)

**Zero-Match Handling:**
- Items with 0% keyword density → GPT-4.1-nano YES/NO
- Batch processing: up to 30 items per call
- Per-future timeout: HARDEN-014 AC4

---

#### **consolidation.py** — Multi-Source Dedup
**Lines:** 917 | **Responsibility:** Fetch from 3 sources, merge, deduplicate
**Pattern:** Parallel fetch with per-source timeout + bulkhead isolation

**Sources (Priority Order):**
1. PNCP (priority 1, highest)
2. PCP v2 (priority 2)
3. ComprasGov v3 (priority 3)

**Consolidation Flow:**
```python
fetch_all_sources(context)
  → parallel: fetch_pncp(), fetch_pcp(), fetch_comprasgov()
  → merge results (PNCP wins on dedup key collision)
  → convert to legacy format
  → deduplicate by (id_licitacao, modalidade, setor_id)
  → enrich from lower-priority duplicates
  → return ConsolidationResult
```

**Timeout Chain:**
```
PerSource(180s) > PerUF(30s) > PerModality(20s) > HTTP(10s)
```

**Error Handling:**
- `AllSourcesFailedError` if all sources fail (503)
- Partial results on partial failure (graceful degradation)
- Status tracking: success, error, timeout, skipped, degraded

---

#### **auth.py** — JWT Token Validation
**Lines:** 519 | **Responsibility:** Validate Supabase JWT, cache tokens
**Pattern:** Local JWT decode + dual-cache (L1 memory, L2 Redis)

**Key Security Updates (STORY-210, STORY-227):**
- **CRIT-SIGSEGV:** faulthandler enabled at app startup
- **STORY-210 AC3:** Hash FULL token (SHA256) to prevent identity collision (CVSS 9.1)
- **STORY-227:** Support ES256 (Supabase JWT rotation Feb 2026) + HS256 backward compat
- **STORY-227:** JWKS endpoint + PEM key support with 5-min cache

**Cache Strategy:**
```
L1: OrderedDict (60s TTL, max 1000 entries, LRU eviction)
L2: Redis (300s TTL, shared across Gunicorn workers)
```

**Token Validation:**
```python
# Key detection order:
1. JWKS endpoint (if configured)
2. PEM public key (SUPABASE_JWT_SECRET env)
3. HS256 symmetric secret (fallback)
```

**Audience Verification (AC7):** `verify_aud=True` (re-enabled after security review)

---

### 2.3 API Routes (33 Route Modules, 10,600 LOC)

| Module | Endpoints | Purpose |
|--------|-----------|---------|
| `search.py` | POST /buscar, GET /buscar-progress/{id} (SSE), POST /v1/search/{id}/retry | Main search pipeline |
| `pipeline.py` | CRUD /pipeline, GET /pipeline/alerts | Opportunity kanban |
| `billing.py` | GET /plans, POST /checkout, GET /billing-portal, GET /subscription/status | Stripe integration |
| `user.py` | GET /me, POST /change-password, GET /trial-status, PUT /profile/context | Profile mgmt |
| `analytics.py` | GET /summary, /searches-over-time, /top-dimensions, /trial-value | Usage analytics |
| `feedback.py` | POST/DELETE /feedback, GET /admin/feedback/patterns | User feedback |
| `health.py` | GET /health/cache, /sources/health | Cache + source health |
| `admin.py` | 30+ admin endpoints (user mgmt, feature flags, cache stats) | Admin dashboard |
| `sessions.py` | GET /sessions | Search history |
| `messages.py` | POST/GET /conversations, POST /{id}/reply | Messaging |
| `auth_oauth.py` | GET /google, /google/callback, DELETE /google | Google OAuth |
| `feature_flags.py` | GET/POST /v1/admin/feature-flags | Runtime flags |
| Others | export_sheets, onboarding, plans, emails, organizations, partners, sectors_public, reports, blog_stats, metrics_api, mfa, alerts, trial_emails, bid_analysis, slo, admin_trace | Additional services |

---

### 2.4 Database Schema (88 Supabase + 7 Backend Migrations)

**Key Tables:**

| Table | Purpose | Notes |
|-------|---------|-------|
| `profiles` | User accounts, trial, plan, quota | RLS per user |
| `plan_billing_periods` | Stripe subscription periods | Source of truth for billing |
| `search_sessions` | Search history + state | Cleanup after 14 days |
| `licitacoes_cache` | Cached search results | 24h TTL, SWR strategy |
| `llm_classifications` | LLM decision audit | STORY-179 AC3 |
| `stripe_webhook_events` | Webhook audit trail | Dedup via idempotency key |
| `google_oauth_tokens` | OAuth token storage | Encrypted |
| `google_sheets_exports` | Export history | STORY-180 tracking |
| `messages` | In-app messaging | STORY-282 |
| `organizations` | Multi-tenant support | ORGANIZATIONS_ENABLED flag |
| `alert_preferences` | Email alert settings | STORY-315 |
| `health_checks` | Canary results | STORY-316 tracking |

**RLS Policies:** All tables protected with `auth.uid()` checks (except admin-only tables)

---

### 2.5 Cron Jobs (7 Background Tasks)

| Cron Job | Schedule | Purpose | Files |
|----------|----------|---------|-------|
| **Session Cleanup** | Every 6 hours | Delete old search sessions (CRIT-011 AC7) | cron_jobs.py:100 |
| **Cache Warmup** | Startup + every 24h | Pre-warm cache for popular sector+UF combos (CRIT-055) | cron_jobs.py:443 |
| **Cache Refresh** | Every 24h (staggered) | Background SWR refresh of stale results | cron_jobs.py (cache refresh logic) |
| **Health Canary** | Every 5 minutes | Test PNCP, PCP, Supabase health (STORY-316) | cron_jobs.py:617 |
| **Trial Emails** | Daily at 08:00 BRT | Trial reminder sequence (STORY-310) | cron_jobs.py:897 |
| **Card Expiry Alerts** | Daily at 08:00 BRT | Pre-dunning warnings (STORY-309 AC4) | cron_jobs.py:770 |
| **Search Alerts** | Daily at 08:00 BRT | Daily digest for saved searches (STORY-315 AC8) | cron_jobs.py:909 |
| **Stripe Reconciliation** | Daily at 03:00 BRT | Sync Stripe ↔ DB subscriptions (STORY-314 AC5) | cron_jobs.py:1118 |

**Lock Mechanism:** Redis locks with 30min TTL prevent duplicate execution

---

### 2.6 Background Job Queue (ARQ)

**Purpose:** Offload long-running tasks (LLM summaries, Excel generation)  
**Config:** PROCESS_TYPE env var (web/worker)

| Job Type | Timeout | Purpose |
|----------|---------|---------|
| `gerar_resumo_job` | 60s | Generate LLM summary (fallback to sync if timeout) |
| `gerar_resumo_fallback` | Immediate | Quick summary for fast response |
| `excel_job` | 120s | Generate Excel file |
| `zero_match_batch_job` | Configurable | Batch LLM zero-match classification |

**SSE Events:** `llm_ready` / `excel_ready` notify frontend on completion

---

### 2.7 Two-Level Cache Architecture (SWR Pattern)

**L1: In-Memory Cache**
- 4h TTL (hot/warm/cold priority)
- OrderedDict with LRU eviction
- Per-process (Gunicorn worker-local)

**L2: Supabase Persistent**
- 24h TTL
- Shared across workers + restarts
- Fallback when L1 misses

**Cache Freshness States:**
```
Fresh (0-6h)       → Served immediately
Stale (6-24h)      → Served + background refresh
Expired (>24h)     → Not served, triggers fetch
```

**Key:** `search:{setor_id}:{ufs_hash}:{modalidades_hash}:{custom_terms_hash}`

---

### 2.8 Monitoring & Observability

#### **Prometheus Metrics (30+ metrics)**

```python
# Histograms (latency buckets)
smartlic_search_duration_seconds          # Total pipeline latency
smartlic_fetch_duration_seconds           # Per-source fetch time
smartlic_llm_call_duration_seconds        # LLM arbiter latency
smartlic_llm_zero_match_batch_duration_seconds
smartlic_search_state_duration_seconds    # Time per pipeline state

# Counters
smartlic_cache_hits_total                 # Cache hit count
smartlic_cache_misses_total               # Cache miss count
smartlic_searches_total                   # Search count (by sector, status)
smartlic_llm_calls_total                  # LLM call count
smartlic_filter_rejections_total          # Filter rejection count
smartlic_circuit_breaker_state            # CB status (open/half-open/closed)
smartlic_legacy_route_calls               # Deprecated route usage

# Gauges
smartlic_active_searches                  # Current in-flight searches
smartlic_auth_cache_size                  # Token cache entries
smartlic_arbiter_cache_size               # LLM arbiter cache entries
```

#### **OpenTelemetry Tracing**
- Per-stage spans (validate, prepare, execute, filter, enrich, generate, persist)
- Per-source spans (PNCP, PCP, ComprasGov)
- LLM call traces
- Database query spans

#### **Sentry Error Tracking**
- PII scrubbing (user IDs, emails masked)
- Noise filtering (transient errors ignored)
- Fingerprint heuristics (CRIT-codes grouped)

#### **Structured Logging**
- JSON format (python-json-logger)
- Correlation IDs (X-Request-ID)
- Sensitive field sanitization

---

## 3. Frontend Architecture

### 3.1 Directory Structure

```
frontend/app/
├── layout.tsx                           # Root layout (providers, fonts, metadata)
├── page.tsx                             # Landing page
├── (auth)/
│   ├── login/page.tsx
│   ├── signup/page.tsx
│   ├── auth/callback/page.tsx           # OAuth callback
│   └── [reset, recovery, mfa]
├── buscar/                              # MAIN SEARCH PAGE
│   ├── page.tsx                         # Search container (700+ lines)
│   ├── hooks/
│   │   ├── useSearch.ts                 # Search API + SSE integration
│   │   ├── useSearchFilters.ts          # Filter state
│   │   └── useKeyboardShortcuts.ts      # Keyboard navigation
│   ├── components/
│   │   ├── SearchForm.tsx               # Input form
│   │   ├── SearchResults.tsx            # Results grid/table
│   │   ├── FilterPanel.tsx              # Sidebar filters
│   │   ├── UfProgressGrid.tsx           # UF status tracker
│   │   ├── SearchErrorBoundary.tsx
│   │   ├── OnboardingBanner.tsx
│   │   └── [8+ more components]
│   └── types/
│       └── search-results.ts            # Type definitions
├── dashboard/page.tsx                   # Analytics dashboard
├── historico/page.tsx                   # Search history
├── pipeline/page.tsx                    # Kanban board (@dnd-kit)
├── planos/page.tsx                      # Pricing page
├── conta/page.tsx                       # Account settings
├── admin/page.tsx                       # Admin dashboard
├── components/                          # Global components (40+ files)
│   ├── AuthProvider.tsx                 # Auth context
│   ├── ThemeProvider.tsx                # Dark mode
│   ├── SWRProvider.tsx                  # SWR cache config
│   ├── LoadingProgress.tsx              # Progress bar
│   ├── CacheBanner.tsx                  # Cache status indicator
│   ├── DegradationBanner.tsx            # Source degradation alert
│   ├── PartialResultsPrompt.tsx         # Partial data notice
│   ├── PlanCard.tsx                     # Subscription UI
│   ├── CookieConsentBanner.tsx
│   ├── SessionExpiredBanner.tsx
│   └── [30+ more components]
├── contexts/
│   └── UserContext.tsx                  # User data context
├── hooks/                               # 20+ custom hooks
│   ├── useAuth.ts
│   ├── usePlan.ts
│   ├── useTrialPhase.ts
│   ├── useAnalytics.ts
│   ├── useOnboarding.ts
│   └── [more hooks]
├── api/                                 # API route handlers (proxies)
│   ├── buscar/route.ts                  # POST → /v1/buscar
│   ├── download/route.ts                # Export handling
│   ├── analytics/route.ts
│   └── [10+ more routes]
├── lib/
│   ├── config.ts
│   ├── storage.ts                       # localStorage utilities
│   ├── utils/
│   │   ├── dateDiffInDays.ts
│   │   ├── formatCurrency.ts
│   │   └── [utility functions]
│   └── supabase-client.ts              # Supabase client (SSR)
├── __tests__/                           # Jest test files (135+ files)
├── e2e-tests/                           # Playwright tests (60 critical flows)
└── public/                              # Static assets, fonts

Key Config Files:
├── next.config.ts                       # Next.js config
├── tailwind.config.ts                   # Tailwind theme
├── jest.config.js                       # Jest setup
├── playwright.config.ts                 # E2E config
├── tsconfig.json                        # TypeScript strict mode
├── package.json                         # 61 deps, 20+ dev deps
└── .env.example
```

### 3.2 Main Search Page Data Flow

**URL:** `/buscar`  
**Component:** `frontend/app/buscar/page.tsx` (700+ lines)

```
User Input
  ↓
SearchForm.tsx (filters: setor, ufs, modalidades, valor, status, custom_terms)
  ↓
useSearch.ts Hook:
  ├─ POST /api/buscar → /v1/buscar (202 Accepted)
  ├─ GET /api/buscar-progress/{id} (SSE EventSource)
  └─ Emit events: searching, filtering, enriching, generating, complete
  ↓
SearchResults.tsx:
  ├─ Display progress in real-time
  ├─ Show partial results as they arrive
  ├─ Render LlmSourceBadge (keyword/llm/zero-match classification)
  ├─ Render ViabilityBadge (4-factor score)
  └─ Show cache status (fresh/stale/expired)
```

### 3.3 Key Frontend Hooks (27 custom hooks, 3,691 LOC)

| Hook | Lines | Purpose |
|------|-------|---------|
| `useSearchSSE.ts` | 769 | SSE + polling search progress (largest hook) |
| `useFetchWithBackoff.ts` | 251 | Exponential backoff fetcher (2s-30s cap, max 5 retries) |
| `usePipeline.ts` | 222 | Kanban pipeline state + drag-drop |
| `useFeatureFlags.ts` | 170 | Runtime feature flag system |
| `useShepherdTour.ts` | 162 | Guided onboarding tours |
| `useSearchPolling.ts` | 155 | Search status polling fallback |
| `useSavedSearches.ts` | 148 | Saved search persistence |
| `useAnalytics.ts` | 139 | Mixpanel/Sentry event tracking |
| `useUserProfile.ts` | 112 | User profile data + mutations |
| `useKeyboardShortcuts.ts` | 105 | Keyboard shortcut bindings |
| `useBroadcastChannel.ts` | 93 | Cross-tab state sync |
| `usePlan.ts` | 86 | Subscription status, quota check |
| `useOrganization.ts` | 86 | Multi-tenant org context |
| `useQuota.ts` | 75 | Plan quota tracking |
| `usePublicMetrics.ts` | 68 | Public metrics display |
| `useAlerts.ts` | 66 | Alert preferences |
| `useNavigationGuard.ts` | 63 | Unsaved changes warning |
| `useTrialPhase.ts` | -- | Trial countdown, paywall logic |
| `useIsMobile.ts` | -- | Responsive breakpoint detection |
| `useServiceWorker.ts` | -- | PWA service worker registration |

### 3.4 API Proxy Endpoints (58 routes in frontend/app/api/)

Key proxies (full list: 58 route.ts files across auth, billing, search, admin, etc.):

| Route | Backend Endpoint | Purpose |
|-------|-----------------|---------|
| `/api/buscar` | POST /buscar | Proxy search request |
| `/api/buscar-progress` | GET /buscar-progress/{id} | SSE stream proxy |
| `/api/buscar-results/[searchId]` | GET /buscar-results/{id} | Fetch completed results |
| `/api/download` | POST /export/excel | Export generation |
| `/api/analytics` | GET /analytics/* | Dashboard data |
| `/api/admin/[...path]` | GET /admin/* | Admin operations (catch-all) |
| `/api/feedback` | POST /feedback | User feedback |
| `/api/trial-status` | GET /trial-status | Trial countdown |
| `/api/me` | GET /me | Current user |
| `/api/plans` | GET /plans | Pricing data |
| `/api/pipeline` | CRUD /pipeline | Kanban state |
| `/api/sessions` | GET /sessions | Search history |
| `/api/alerts` | CRUD /alerts | Alert preferences |
| `/api/messages/*` | CRUD /conversations | Messaging |
| `/api/organizations/*` | CRUD /organizations | Multi-tenant |
| `/api/auth/*` | Auth endpoints | Login, signup, OAuth, MFA |
| `/api/bid-analysis/[bidId]` | GET /bid-analysis/{id} | Per-bid intelligence |
| `/api/reports/diagnostico` | POST /reports/diagnostico | PDF diagnostic report |

### 3.5 Component Hierarchy

```
RootLayout
├─ ThemeProvider (dark mode)
├─ AuthProvider (JWT, user context)
├─ SWRProvider (cache config)
├─ NProgressProvider (progress bar)
├─ AnalyticsProvider (Mixpanel/Sentry)
├─ BackendStatusProvider (source health)
├─ UserProvider (user data context)
├─ NavigationShell
│  ├─ Sidebar (nav links)
│  ├─ BottomNav (mobile)
│  └─ Main Content
└─ Toast (Sonner notifications)
   └─ Dialog stack
```

### 3.6 State Management

**SWR (Stale-While-Revalidate):**
- Auto-revalidation on window focus
- Dedupe parallel requests
- 1hr localStorage cache (fallback)
- Config: `dedupingInterval=60s`, `focusThrottleInterval=30s`

**React Context:**
- `UserContext`: User data, profile, plan
- `AuthProvider`: JWT token, session state
- `BackendStatusContext`: Source health, degradation alerts

**LocalStorage:**
- Last search (STORY-170)
- Theme preference
- Onboarding completion
- Keyboard shortcut hints

---

## 4. Data Flow — End-to-End

### 4.1 Search Pipeline (7 Stages)

```
User POST /buscar { setor_id, ufs, data_inicial, data_final, ... }
  ↓
STAGE 1: VALIDATE
├─ Check JWT token + quota
├─ Validate input params
└─ Emit: "validating"
  ↓
STAGE 2: PREPARE
├─ Load cache (check for fresh/stale)
├─ Parse custom search terms
├─ Initialize search context
└─ Emit: "preparing" (via SSE)
  ↓
STAGE 3: EXECUTE (Multi-Source, Parallel)
├─ Fetch PNCP:
│  ├─ Batch UFs (size=5, delay=2s)
│  ├─ Per-UF timeout: 30s
│  ├─ Per-modality timeout: 20s
│  └─ Circuit breaker: 15 failures → 60s cooldown
├─ Fetch PCP v2 (fallback):
│  ├─ Same UF batching
│  └─ No value data (sempre 0.0)
├─ Fetch ComprasGov v3 (fallback):
│  ├─ Dual endpoint (legacy + Lei 14.133)
│  └─ Client-side UF filtering
└─ Consolidation timeout: 300s
└─ Result: deduplicated licitacoes_raw
  ↓
STAGE 4: FILTER
├─ UF checks (fastest)
├─ Value range checks
├─ Keyword density scoring:
│  ├─ High (>5%): "keyword" source
│  ├─ Medium (2-5%): "llm_standard"
│  ├─ Low (1-2%): "llm_conservative"
│  └─ Zero (0%): "llm_zero_match" (LLM-only)
├─ LLM arbiter for uncertain/zero items:
│  ├─ Model: gpt-4.1-nano
│  ├─ Input: title + description
│  ├─ Output: SIM/NAO + confidence
│  └─ Cache: L1 (5000 entries) + L2 (Redis, 1h TTL)
├─ Status/date validation
└─ Result: licitacoes_filtradas (reduced set)
  ↓
STAGE 5: ENRICH
├─ Status inference (open/closing/closed)
├─ Viability assessment (4 factors):
│  ├─ Modalidade: 30% weight
│  ├─ Timeline: 25% weight
│  ├─ Valor fit: 25% weight
│  └─ Geography: 20% weight
├─ LLM summaries (ARQ background job):
│  ├─ Fallback: sync gerar_resumo_fallback()
│  └─ SSE event: "llm_ready" on completion
└─ Result: enriched licitacoes with scores
  ↓
STAGE 6: GENERATE
├─ Sort results (by viability + date)
├─ Excel generation (ARQ background job):
│  ├─ Columns: ID, título, viabilidade, setor, UF, valor, etc.
│  ├─ Styling: header color, number formatting
│  └─ SSE event: "excel_ready" on completion
├─ Google Sheets export (STORY-180):
│  └─ OAuth flow, append to shared sheet
├─ PDF report (STORY-325):
│  └─ Summary + top opportunities
└─ Result: export files ready for download
  ↓
STAGE 7: PERSIST
├─ Save to cache (L1 + L2):
│  ├─ L1: 4h TTL, OrderedDict
│  └─ L2: Supabase, 24h TTL
├─ Audit log (STORY-226 AC18):
│  ├─ Write search_sessions record
│  ├─ Log via Sentry, JSON stdout
│  └─ Include: user_id, setor_id, result_count, latency
├─ Cleanup (cancel pending tasks, close SSE)
└─ Emit: "complete" (final SSE event)
  ↓
Response to Frontend:
{
  search_id: UUID,
  total_raw: int,
  total_filtered: int,
  licitacoes: [BuscaResult, ...],
  cache_status: "hit" | "miss" | "stale",
  sources_summary: { pncp: {...}, pcp: {...}, comprasgov: {...} },
  latency_ms: int,
  excel_url: str (if generated),
  pdf_url: str (if generated),
}
```

### 4.2 SSE Progress Tracking

**Endpoint:** `GET /v1/buscar-progress/{search_id}` (EventSource)

```
Search ID links SSE stream to initial POST request
  ↓
Frontend: new EventSource('/buscar-progress/{id}')
  ↓
Backend: asyncio.Queue-based tracker (in-memory)
  ↓
Events emitted:
  → "searching"       (executing stage)
  → "filtering"       (filtering stage)
  → "enriching"       (enriching stage)
  → "generating"      (generating stage)
  → "llm_ready"       (LLM summary completed)
  → "excel_ready"     (Excel exported)
  → "complete"        (final, contains full response)
  ↓
Frontend: graceful fallback if SSE fails
  ├─ Use time-based simulation (assume 10s per stage)
  └─ Final poll for results (GET /v1/search/{id}/status)
```

---

## 5. Security Architecture

### 5.1 Authentication & Authorization

**Auth Flow:**
1. **Supabase Auth** — Email/password or OAuth (Google)
2. **JWT Validation** — Local decode (no Supabase API call)
   - Algorithm: ES256 (preferred) or HS256 (legacy)
   - Verification: JWKS endpoint OR PEM public key OR symmetric secret
   - Audience check: enabled (STORY-227 AC7)
   - Token cache: L1 (60s, 1000 entries) + L2 (Redis, 5min)

**MFA (STORY-317 AC2/AC3):**
- Sensitive endpoints require `aal: "aal2"` (Authenticator Assurance Level)
- TOTP (Time-based One-Time Password) support
- Recovery codes with bcrypt hashing

**Row-Level Security (RLS):**
- All user tables protected with `auth.uid()` checks
- Service role used for background jobs (cron, ARQ)
- User-scoped Supabase tokens (SYS-023)

### 5.2 Input Validation

**Backend:**
- Pydantic v2 with strict mode
- Email validation (RFC 5322)
- Date range validation
- UF/modalidade enum validation
- Custom term validation (min 4 chars, stopword removal)
- CRIT validation (reject invalid input before processing)

**Frontend:**
- react-hook-form + Zod validation
- HTML5 form validation
- Sanitization of user input in logs

### 5.3 Secrets Management

**Env Vars (Never Committed):**
```
OPENAI_API_KEY           # GPT-4.1-nano access
SUPABASE_URL             # Database + Auth
SUPABASE_ANON_KEY        # Client-side key (RLS gated)
SUPABASE_SERVICE_ROLE    # Backend-only (cron, ARQ)
STRIPE_SECRET_KEY        # Billing
STRIPE_WEBHOOK_SECRET    # Webhook verification
RESEND_API_KEY           # Email service
GOOGLE_CLIENT_ID         # OAuth
GOOGLE_CLIENT_SECRET     # OAuth
JWT_SECRET (legacy)      # HS256 symmetric key (for tests)
SUPABASE_JWT_SECRET      # JWKS fallback
```

**Storage:**
- GitHub repo (encrypted)
- Railway environment variables
- Not in logs (sanitized via log_sanitizer.py)

### 5.4 CORS & Rate Limiting

**CORS:**
```python
allowed_origins = [
    "https://smartlic.tech",
    "https://www.smartlic.tech",
    "http://localhost:3000",          # Dev
    "http://localhost:3001",           # Alt dev
]
# Configurable via CORS_ORIGINS env var
```

**Rate Limiting:**
- Redis token bucket (quota.py)
- Per-user quota: 100 searches/month (free), 500 (pro)
- Per-IP rate limit: 10 req/s (configurable)
- RateLimitMiddleware: 429 response when exceeded

### 5.5 SQL Injection Prevention

**Pattern:** Supabase ORM + parameterized queries (not raw SQL in user-facing code)

**Safe Patterns:**
```python
# ✓ SAFE: Parameterized query
user = await supabase.table("profiles").select("*").eq("id", user_id).single()

# ✗ UNSAFE: String interpolation (not found in codebase)
# query = f"SELECT * FROM profiles WHERE id = '{user_id}'"
```

### 5.6 CSRF Protection

**Strategy:** Supabase Auth handles CSRF (cookies + SameSite)  
**Frontend:** No manual CSRF tokens (rely on Auth framework)

### 5.7 Data Encryption

**At Rest:**
- Supabase: TLS 1.3 + AES-256 encryption (managed)
- Google OAuth tokens: encrypted in DB (STORY-204)
- Passwords: bcrypt (cost 12)

**In Transit:**
- All HTTPS
- HTTP/2 or HTTP/3

---

## 6. Infrastructure & DevOps

### 6.1 Deployment (Railway)

**Services:**
```
Railway Project: SmartLic
├─ Backend Service (web)
│  ├─ Command: gunicorn main:app -k uvicorn.workers.UvicornWorker -w 2 --timeout 180
│  ├─ Port: 8000
│  ├─ Memory: 2GB (auto-scaled)
│  └─ Processes: 2 Gunicorn workers (no preload, per startup/lifespan)
├─ Worker Service (background jobs)
│  ├─ Command: python -m arq backend.job_queue.settings
│  ├─ Workers: 1-2 (configurable)
│  └─ Purpose: LLM summaries, Excel generation, Stripe reconciliation
└─ Frontend Service (Next.js)
   ├─ Command: node .next/standalone/server.js
   ├─ Port: 3000
   └─ Memory: 1GB
```

**Environment Variables:**
```
ENVIRONMENT=production
PORT=8000
DATABASE_URL=postgresql://...
SUPABASE_URL=https://...
OPENAI_API_KEY=sk-...
STRIPE_SECRET_KEY=sk_live_...
# 50+ more config vars
```

### 6.2 CI/CD Workflows (17 GitHub Actions)

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `backend-tests.yml` | PR + push | Run pytest (169 files, 5131+ tests) |
| `frontend-tests.yml` | PR + push | Run Jest (135 files) |
| `backend-ci.yml` | PR + push | Backend CI (lint, type check, test) |
| `tests.yml` | PR + push | Combined test orchestration |
| `e2e.yml` | PR + push | Playwright tests (60 critical flows) |
| `migration-gate.yml` | PR touch `supabase/migrations/` | Warn of pending migrations |
| `migration-check.yml` | Push to main, daily | Block if unapplied migrations |
| `deploy.yml` | Push to main | Deploy to Railway + auto-apply migrations |
| `staging-deploy.yml` | Manual trigger | Deploy to staging environment |
| `lighthouse.yml` | PR + daily | Performance audit |
| `load-test.yml` | Manual trigger | Locust load test |
| `codeql.yml` | PR + schedule | Security scanning |
| `pr-validation.yml` | PR | Type check, lint, schema validation |
| `sync-sectors.yml` | Schedule | Sync sector definitions |
| `cleanup.yml` | Schedule | Resource cleanup |
| `dependabot-auto-merge.yml` | Dependabot PR | Auto-merge safe dep updates |
| `handle-new-user-guard.yml` | Webhook | New user onboarding guard |

### 6.3 Database Migrations (CRIT-050)

**Three-Layer Defense Against Unapplied Migrations:**

1. **PR Warning** (`migration-gate.yml`)
   - Lists pending migrations
   - Posts WARNING comment (non-blocking)

2. **Push Alert** (`migration-check.yml`)
   - Runs on push to main + daily schedule
   - Blocks (exit 1) if unapplied migrations detected

3. **Auto-Apply on Deploy** (`deploy.yml`)
   - After backend deploys, runs `supabase db push --include-all`
   - Sends `NOTIFY pgrst, 'reload schema'` for PostgREST cache refresh
   - Verifies no PGRST205 errors via smoke test
   - Marks deploy as DEGRADED if push fails (does NOT rollback)

**Migration Files:**
- Supabase: `/supabase/migrations/` (88 files, numbered sequentially)
- Backend: `/backend/migrations/` (7 files, local schema changes)

---

## 7. Technical Debt Inventory

*Updated 2026-03-10 with verified code analysis. Items marked RESOLVED have been fixed
but remain documented for reference. Active items are sorted by severity.*

### Critical Issues (SEVERITY: CRITICAL)

| ID | Category | Location | Issue | Impact | Est. Effort | Debt Type |
|---|----------|----------|-------|--------|-------------|-----------|
| **CRIT-SIGSEGV** | Reliability | `main.py:1-9`, `requirements.txt:10` | RESOLVED: faulthandler disabled in prod, uvicorn[standard] re-enabled | Was: process crashes on Railway | -- | Reliability |
| **CRIT-038** | Reliability | `llm_arbiter.py:68` | RESOLVED: LLM_STRUCTURED_MAX_TOKENS increased to 800 (DEBT-101 AC5) | Was: JSON truncation in 20-30% of calls | -- | Reliability |
| **CRIT-050** | Reliability | `.github/workflows/` | Three-layer migration defense (warning + block + auto-apply) | Prevents unapplied migrations in production | 1d | Reliability |
| **CRIT-PNCP-PAGESIZE** | Reliability | `pncp_client.py` | PNCP API reduced max tamanhoPagina from 500 → 50 (Feb 2026) | Silent HTTP 400 on oversized requests | 1d | Compatibility |
| **STORY-210 AC3** | Security | `auth.py:306` | Hash FULL token (SHA256) not just payload | Token identity collision (CVSS 9.1) | 0.5d | Security |
| **STORY-227** | Security | `auth.py:20` | ES256/JWKS support + HS256 backward compat | JWT signing algorithm rotation (Feb 2026) | 1d | Security |

### High-Priority Issues (SEVERITY: HIGH)

| ID | Category | Location | Issue | Impact | Est. Effort | Debt Type |
|---|----------|----------|-------|--------|-------------|-----------|
| **DEBT-015 SYS-005** | Maintainability | `main.py:7`, `startup/` | Monolith decomposition (extracted Sentry, lifespan, state to 3 modules) | Easier to test, lower coupling | 2d | Maintainability |
| **DEBT-017** | Performance | `backend/migrations/` | DB long-term optimization (18 items) | Index bloat, N+1 queries | 3d | Performance |
| **DEBT-018 SYS-029** | Maintainability | `pncp_client.py`, `requirements.txt:19` | requests still needed for sync PNCPClient fallback | Should fully migrate to httpx (AsyncPNCPClient in progress) | 2d | Maintainability |
| **DEBT-016** | Maintainability | `frontend/app/` | Frontend advanced refactoring (8 items) | Component reusability, test coverage | 2d | Maintainability |
| **HARDEN-001** | Performance | `llm_arbiter.py:35` | OpenAI client timeout = 15s (5× p99) | Prevents thread starvation on LLM hangs | 0.5d | Performance |
| **HARDEN-006** | Correctness | `consolidation.py:760` | Merge-enrichment from lower-priority duplicates | Data completeness across sources | 1d | Correctness |
| **HARDEN-009** | Performance | `llm_arbiter.py:74` | LRU cache with 5000 entry limit | Unbounded memory growth prevention | 0.5d | Performance |
| **HARDEN-014 AC4** | Reliability | `llm_arbiter.py:123` | Per-future timeout counter for LLM batch classification | Timeout metrics tracking | 0.5d | Observability |
| **GTM-FIX-029 AC1/AC5** | Performance | `pncp_client.py:87-92` | Per-UF timeout (30s) + degraded mode (15s) | Prevent timeout cascades under load | 0.5d | Performance |
| **GTM-FIX-031** | Performance | `pncp_client.py:96` | Phased UF batching (size=5, delay=2s) | Reduce PNCP API pressure | 0.5d | Performance |

### Medium-Priority Issues (SEVERITY: MEDIUM)

| ID | Category | Location | Issue | Impact | Est. Effort | Debt Type |
|---|----------|----------|-------|--------|-------------|-----------|
| **STORY-171** | Maintainability | `filter.py:17` | Feature flag caching with lazy import | Circular dependency prevention | 1d | Maintainability |
| **STORY-248 AC9** | Correctness | `filter.py:22` | Lazy-load filter stats tracker | Prevents circular imports at module load | 0.5d | Correctness |
| **STORY-252** | Reliability | `pncp_client.py:38-103` | Circuit breaker pattern (15 failures → 60s cooldown) | Faster recovery from degradation | 1d | Reliability |
| **STORY-291** | Reliability | `authorization.py:39,91` | CB integration (when Supabase CB open, skip retries) | Prevent cascading failures | 0.5d | Reliability |
| **STORY-293** | Maintainability | `search_cache.py` | Cache fallback banner + stale banner logic | User awareness of data freshness | 1d | Maintainability |
| **STORY-294 AC3** | Performance | `llm_arbiter.py:90` | Redis L2 cache for cross-worker LLM sharing | Reduce redundant LLM calls | 0.5d | Performance |
| **STORY-303** | Reliability | `requirements.txt:55` | cryptography pin >=46.0.5,<47.0.0 (fork-safe with Gunicorn preload) | Prevent SIGSEGV on upgrades | 1d | Reliability |
| **STORY-316** | Observability | `cron_jobs.py:617` | Health canary (every 5 min) | Source health tracking | 0.5d | Observability |
| **STORY-317** | Security | `auth.py:384,434` | MFA (aal2) requirement + TOTP + recovery codes | Multi-factor authentication | 2d | Security |
| **TD-004** | Maintainability | `main.py:217` | Legacy route tracking (non-/v1/ paths) | Identify deprecated endpoints | 0.5d | Maintainability |
| **FE-020** | Performance | `frontend/app/layout.tsx:31` | Font preload optimization (skip display fonts to avoid blocking critical path) | Faster LCP | 0.5d | Performance |
| **CHARDET-PIN** | Reliability | `requirements.txt:26` | chardet<6 pin (requests<=2.32.5 incompatible with chardet 6.0.0) | Remove once requests>=2.33.0 ships | 0.5d | Reliability |
| **PYTEST-TIMEOUT-WINDOWS** | Reliability | `pytest.ini` or `pyproject.toml` | timeout_method="thread" (signal-based fails on Windows) | Windows dev compatibility | 0.5d | Reliability |

### New Findings from Code Analysis (2026-03-10)

| ID | Severity | Category | Location | Issue | Impact | Est. Effort |
|---|----------|----------|----------|-------|--------|-------------|
| **ARCH-001** | HIGH | Maintainability | `routes/search.py` (2177 lines) | Largest route module by far -- buscar_licitacoes endpoint, SSE generator, state machine wiring all in one file | Hard to test, hard to review, merge conflicts | 2d |
| **ARCH-002** | HIGH | Maintainability | `search_pipeline.py` (17 noqa:F401 imports) | Re-exports 17+ symbols solely for backward test compatibility. Tests patch `search_pipeline.X` instead of actual module | Test fragility, import coupling | 1d |
| **ARCH-003** | MEDIUM | Config Hygiene | `pncp_client.py` (14 `os.environ.get()` calls) | Circuit breaker, timeout, batch config read directly instead of via `config/` package | Config scattered across modules | 1d |
| **ARCH-004** | MEDIUM | Dead Code | `config.py.bak`, `config_legacy.py.bak` in backend/ | Backup files from decomposition left in repo | Confusing, repo clutter | 0.5h |
| **ARCH-005** | MEDIUM | Maintainability | `filter.py` (2141-line facade) | Facade that re-exports from 5 sub-modules -- the facade itself contains `aplicar_todos_filtros` (main orchestrator) plus ThreadPoolExecutor, random, uuid imports | Split orchestrator from re-exports | 1d |
| **ARCH-006** | LOW | Frontend | `SearchForm.tsx` (687 lines) | Largest frontend component -- handles sector select, UF multi-select, date range, value range, modalidade, status, and custom terms in one component | Should decompose into sub-form components | 1.5d |
| **ARCH-007** | LOW | Frontend | `DataQualityBanner.tsx` (661 lines) | Very large presentational component for a banner | Review for decomposition | 0.5d |
| **ARCH-008** | LOW | Frontend | `useSearchSSE.ts` (769 lines) | Complex SSE hook with retry logic, polling fallback, terminal guards -- well-documented but large | Consider splitting into SSE + polling hooks | 1d |
| **ARCH-009** | LOW | Observability | 30 TODO/FIXME/HACK comments across backend | Scattered improvement notes not tracked in issue tracker | Audit and convert to issues or remove | 0.5d |

### Low-Priority Issues (SEVERITY: LOW)

| ID | Category | Location | Issue | Impact | Est. Effort | Debt Type |
|---|----------|----------|-------|--------|-------------|-----------|
| **STORY-226 AC8** | Maintainability | `authorization.py:172` | Backward-compatible aliases for quota functions | Old imports still work | 0.5d | Maintainability |
| **STORY-266** | Maintainability | `cron_jobs.py:736` | Trial reminder emails (legacy, replaced by STORY-310 sequence) | Dead code, remove | 0.5d | Code Quality |
| **SYS-023** | Correctness | `database.py:12` | Per-user Supabase tokens for user-scoped operations | Should be verified in all routes | 1d | Security |
| **SYS-036** | Security | `main.py:13,91-167` | OpenAPI docs protected by DOCS_ACCESS_TOKEN in production | Hardened API docs access | 0.5d | Security |
| **VALIDATE-TERMS-INVARIANT** | Correctness | `filter.py:68,138` | Terms NEVER in both `valid` AND `ignored` (critical invariant, asserts on violation) | Data quality guarantee | 0.5d | Correctness |

---

## 8. Testing Strategy

### Backend Testing (5131+ Tests, 169 Files)

**Test Location:** `/backend/tests/`

**Framework:** pytest + pytest-asyncio + pytest-timeout (30s default)

**Test Categories:**

| Category | Files | Tests | Coverage Target |
|----------|-------|-------|-----------------|
| Unit tests | 80 | 2500+ | 90% (critical modules) |
| Integration tests | 30 | 1500+ | 85% (API contracts, cache) |
| Circuit breaker tests | 15 | 200+ | 100% (fault handling) |
| LLM/classification tests | 20 | 300+ | 90% (mock OpenAI) |
| Auth tests | 15 | 400+ | 95% (security critical) |
| Cache tests | 10 | 200+ | 95% (two-level cache) |
| Migration tests | 5 | 100+ | 100% (DB schema) |
| Quota tests | 8 | 150+ | 95% (billing) |
| E2E tests | 6 | 80+ | N/A (smoke tests) |

**Key Test Patterns:**

```python
# Auth: Use app.dependency_overrides[require_auth]
app.dependency_overrides[require_auth] = lambda: {"id": "test-user"}

# Cache: Patch supabase_client.get_supabase (not search_cache.get_supabase)
@patch("supabase_client.get_supabase")

# Config: Use @patch("config.FLAG_NAME", False)
@patch("config.LLM_ARBITER_ENABLED", False)

# LLM: Mock at @patch("llm_arbiter._get_client")
@patch("llm_arbiter._get_client")

# ARQ: conftest fixture _isolate_arq_module handles cleanup
# (never do raw sys.modules["arq"] = ... without cleanup)

# Anti-Hang Rules:
# - Use @pytest.mark.asyncio for async tests
# - Every test has 30s timeout (@pytest.mark.timeout(60) for slow tests)
# - NEVER use asyncio.get_event_loop().run_until_complete()
# - NEVER use sys.modules manipulation without cleanup
```

**Test Execution:**
```bash
# Safe suite (Windows-compatible, subprocess isolation per file)
python scripts/run_tests_safe.py
python scripts/run_tests_safe.py --parallel 4

# Direct (Linux CI with signal-based timeout)
pytest --timeout=30 -q

# Specific file
pytest -k "test_search_pipeline"
```

---

### Frontend Testing (2681+ Tests, 135 Files)

**Framework:** Jest 29.7.0 + @testing-library/react 14.1.2 + Playwright 1.58.2

**Polyfills:** `jest.setup.js` provides:
- `crypto.randomUUID()`
- `EventSource` (jsdom lacks both)

**Test Coverage Target:** 60% (enforced in CI)

**E2E Tests:** 60 critical user flows (Playwright)
- Search page (filters, SSE progress, results)
- Onboarding (CNAE selection, UF selection, confirmation)
- Billing (plan selection, checkout flow)
- Auth (login, signup, OAuth, password recovery)
- Pipeline (kanban drag-drop, item edit)

---

## 9. Performance Optimization

### 9.1 Backend Latency Targets

| Operation | Target | Current | Status |
|-----------|--------|---------|--------|
| Search (cache hit) | <500ms | ~400ms | ✓ |
| Search (3-source, 5 UFs) | <15s | ~8-12s | ✓ |
| LLM classification per item | <100ms | ~60ms (with cache) | ✓ |
| Excel generation | <30s | ~15-20s | ✓ |
| PDF generation | <20s | ~8-12s | ✓ |

### 9.2 Frontend Metrics (Lighthouse)

**Targets:**
- Largest Contentful Paint (LCP): <2.5s
- First Input Delay (FID): <100ms
- Cumulative Layout Shift (CLS): <0.1

**Optimizations:**
- Font preload strategy (FE-020): skip display fonts
- Code splitting per route
- Image optimization (next/image)
- CSS-in-JS: Tailwind (zero-JS overhead)

### 9.3 Cache Warming

**Strategy (CRIT-055):**
- Startup: Pre-warm top 20 sector+UF combos (configurable)
- Periodic: Re-warm every 24h (staggered by sector)
- Post-deploy: Auto-warm top-N searches

**Config:**
```
WARMUP_ENABLED=true
WARMUP_UFS=["SP", "RJ", "MG", ...]        # Priority UFs
WARMUP_SECTORS=["construcao", "ti", ...]  # Top sectors
WARMUP_STARTUP_DELAY_SECONDS=30
WARMUP_PERIODIC_INTERVAL_HOURS=24
WARMUP_RATE_LIMIT_RPS=5                   # Prevent API overload
```

---

## 10. Monitoring & SLOs

### 10.1 Service Level Objectives (STORY-299)

| Metric | Target | Window |
|--------|--------|--------|
| **Availability** | 99.5% | 30-day |
| **Search Latency (p99)** | <30s | Per-search |
| **Cache Hit Rate** | >70% | Daily |
| **Source Health (PNCP)** | >95% success | Daily |
| **Error Rate** | <0.5% | Daily |

### 10.2 Prometheus Dashboards

**Key Metrics:**
- Request rate (qps, status codes)
- Search duration (by sector, UF count)
- Cache hit/miss ratio
- Circuit breaker state (open/closed)
- LLM call latency + cost
- Database query latency
- Queue depth (ARQ jobs)

### 10.3 Sentry Integration

**PII Scrubbing:**
- User IDs → `[user-id]`
- Emails → `[email]`
- Tokens → `[token]`
- Custom patterns in `startup/sentry.py`

**Noise Filtering:**
- Transient errors (rate-limit, timeout) sampled
- Network errors grouped by signature
- Fingerprint heuristics (CRIT-codes grouped together)

---

## 11. Key Architectural Decisions

| Decision | Rationale | Trade-off |
|----------|-----------|-----------|
| **Multi-source dedup** | Maximize coverage, avoid false negatives | Higher latency (parallel fetch) |
| **LLM arbiter** | Eliminate false positives, reduce user effort | Cost (~R$0.00007/call) + latency |
| **SWR cache** | Balance freshness + latency (serve stale while revalidating) | Potential stale data (mitigated by 24h TTL) |
| **AsyncPNCPClient (in progress)** | Use httpx instead of requests | Sync fallback still exists (DEBT-018) |
| **Two-level cache (L1 + L2)** | Per-worker speed (L1) + cross-restart persistence (L2) | Complexity, cache coherency challenges |
| **Circuit breaker per source** | Isolate failures, fast recovery | Overhead, tuning required |
| **ARQ background jobs** | Don't block search response on Excel/PDF | Complexity, eventual consistency |
| **Railway deployment** | Managed infrastructure, auto-scaling | Vendor lock-in, limited control |
| **Supabase Auth + RLS** | Managed auth, built-in security | Less flexible (no custom auth logic) |

---

## 12. Known Limitations & Future Work

### Current Limitations

1. **AsyncPNCPClient Migration (DEBT-018)**
   - requests library still required for sync fallback
   - Migration to pure httpx (async) in progress
   - Effort: 2d

2. **Search Filter Complexity (filter.py 177KB)**
   - Large monolithic file, hard to test
   - Should refactor into smaller modules
   - Effort: 2d

3. **Frontend Component Fragmentation**
   - Some components duplicated (loading states, error boundaries)
   - Opportunity for design system
   - Effort: 2d

4. **Database Query Performance**
   - Some N+1 patterns in analytics queries
   - Missing indexes on frequently-joined tables
   - Effort: 1d

5. **LLM Cost Optimization**
   - Currently using gpt-4.1-nano (R$0.00007/call)
   - Could use cheaper models for low-stakes classifications
   - Effort: 1d

### Roadmap (Suggested)

1. **Complete AsyncPNCPClient migration** (Q2 2026)
   - Remove requests dependency
   - Performance improvement expected

2. **Database optimization** (Q2 2026)
   - Index tuning
   - Query optimization

3. **Frontend design system** (Q3 2026)
   - Component library
   - Consistency & reusability

4. **Mobile app** (Q4 2026)
   - React Native (share business logic)
   - iOS + Android native UX

---

## 13. File Count & Metrics Summary (verified 2026-03-10)

| Metric | Count |
|--------|-------|
| **Backend Python Files** | 192 |
| **Backend Total LOC** | 72,693 |
| **Backend Route Modules** | 33 (10,600 LOC) |
| **Backend Test Files** | 169 |
| **Backend Total Tests** | 5131+ |
| **Frontend Pages** | 28 |
| **Frontend TS/TSX Files** | 328 |
| **Frontend Buscar Components** | 44 (7,574 LOC) |
| **Frontend Custom Hooks** | 27 (3,691 LOC) |
| **Frontend API Proxy Routes** | 58 |
| **Frontend Test Files** | 135 |
| **Frontend E2E Tests** | 60 |
| **Database Migrations** | 88 (Supabase) + 7 (backend) |
| **Feature Flags** | 50+ |
| **Cron Jobs** | 7+ |
| **Background Job Types** | 4+ |
| **Pipeline Stage Modules** | 13 (3,530 LOC) |
| **Client Modules** | 8 (5,019 LOC) |
| **Prometheus Metrics** | 30+ |
| **Monitoring Channels** | Prometheus, OTel, Sentry |
| **GitHub Workflows** | 17 |
| **Dependencies (Backend)** | 40+ pinned packages |
| **Dependencies (Frontend)** | 31 + 20 dev deps |
| **Database Tables** | 20+ (with RLS policies) |
| **Supabase Functions** | 5+ (RPC helpers) |

---

## 14. Questions for Specialists

### For @data-engineer

1. **88 migrations and counting** -- Is there a migration squash strategy? At what point do we consolidate old migrations into a baseline?
2. **Cache key correctness (STORY-306)** -- The cache key now includes date_from/date_to. Has this been validated with production cache hit rates? Are there orphaned cache entries from the old key format?
3. **search_sessions table cleanup** -- Cron runs every 6h deleting old sessions. What is the table growth rate? Do we need partitioning?
4. **Redis memory usage** -- Progress tracker uses Redis Streams with 5-min TTL. With 2 Gunicorn workers and concurrent searches, what is peak Redis memory?
5. **LLM classification audit trail** -- `llm_classifications` table stores every LLM decision. Growth rate? Retention policy?

### For @ux-design-expert

1. **SearchForm.tsx (687 lines)** -- This is a monolithic form component handling sector, UFs, dates, value range, modalidade, status, and custom terms. Should it be decomposed into sub-form sections with their own validation?
2. **DataQualityBanner.tsx (661 lines)** -- This banner component is unusually large for a notification element. What is driving the complexity? Can banners be standardized?
3. **44 components in `/buscar/components/`** -- Is the search page over-componentized? Are users overwhelmed by the number of banners (CacheBanner, DegradationBanner, PartialResultsPrompt, PartialTimeoutBanner, FilterRelaxedBanner, RefreshBanner, ExpiredCacheBanner, SearchErrorBanner, OnboardingBanner, OnboardingSuccessBanner, DataQualityBanner, TruncationWarningBanner)?
4. **28 frontend pages** -- Are all pages actively used? Blog content pages (como-avaliar-licitacao, como-evitar-prejuizo, etc.) may have low traffic.
5. **Mobile experience** -- `useIsMobile.ts` hook exists but no dedicated mobile views. Is responsive design sufficient or do mobile users need a distinct experience?

### For @dev (Priority Actions)

1. **ARCH-001**: `routes/search.py` at 2177 lines needs decomposition. Suggested: extract SSE generator, state machine wiring, and retry logic into separate modules.
2. **ARCH-002**: Clean up 17 `noqa:F401` re-exports in `search_pipeline.py`. Update tests to patch actual source modules instead.
3. **ARCH-003**: Move 14 `os.environ.get()` calls from `pncp_client.py` into `config/pncp.py`.
4. **ARCH-004**: Delete `config.py.bak` and `config_legacy.py.bak`.

---

## 15. Conclusion

SmartLic is a **well-architected, production-grade SaaS platform** with:

- Resilient multi-source pipeline with circuit breakers, bulkheads, and graceful degradation
- Intelligent filtering combining keywords + LLM classification + viability assessment
- Comprehensive monitoring (Prometheus, OTel, Sentry)
- Strong security (JWT + RLS + MFA + input validation + CORS)
- Extensive test coverage (5131 backend + 2681 frontend tests)
- Type-safe (Pydantic v2 backend, TypeScript 5.9 frontend)
- Scalable infrastructure (Railway, Redis, ARQ background jobs)

**Technical Debt Summary:** 6 critical (4 RESOLVED), 8 high, 13 medium, 5 low, plus 9 newly identified from this analysis (ARCH-001 through ARCH-009).

**Top Risk Areas:** LLM cost scaling, PNCP API reliability (50-page limit), cache coherency across workers.

**Recommended Next Actions (priority order):**
1. Decompose `routes/search.py` (2177 lines) -- highest-impact maintainability win
2. Clean up test coupling via `search_pipeline.py` re-exports
3. Consolidate env var reads into `config/` package
4. Database migration squash strategy
5. Frontend component audit (banner consolidation)

---

**Documentation compiled via comprehensive codebase analysis. 192 Python files (72,693 LOC), 328 TS/TSX files, 88 migrations, 17 CI workflows verified against actual source code on 2026-03-10.**