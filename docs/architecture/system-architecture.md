# System Architecture -- GTM Readiness Assessment

**Date:** 2026-03-10 | **Agent:** @architect (Atlas) | **Version:** 1.0
**Codebase snapshot:** commit `5efa4b13` (main)

---

## Executive Summary

SmartLic's backend is significantly more mature than a typical POC. The codebase demonstrates production-grade patterns across reliability (circuit breakers on all 3 data sources + Supabase, timeout chains, SWR caching), security (JWT with ES256+JWKS, RLS, Stripe webhook signature verification, log sanitization), and observability (Prometheus metrics, OpenTelemetry tracing, Sentry, structured JSON logging). The architecture reflects lessons learned from real production incidents (SIGSEGV crash loops, SSE heartbeat gaps, connection pool exhaustion), which is a strong signal of operational maturity.

However, there are structural risks for GTM. The system's complexity has outpaced its operational tooling: 90 database migrations, 199 source files (72K+ lines), 336 test files, and 50+ feature flags create a configuration surface area that could surprise operators. The reliance on government APIs (PNCP, PCP, ComprasGov) introduces an external reliability ceiling that no amount of internal hardening can fully compensate for -- the system correctly handles this via multi-level cache and graceful degradation, but customers will inevitably encounter "stale data" scenarios.

**Overall GTM Verdict: YELLOW -- Ready with caveats.** There are no hard blockers that prevent charging customers, but there are two areas that need tightening within the first 30 days: (1) the vulnerability scan in CI is non-blocking (`continue-on-error: true`), and (2) the lint/type-check gates are advisory only. For a B2G SaaS product handling procurement data, these should be enforced.

---

## Architecture Overview

```
                    +------------------+
                    |  smartlic.tech   |
                    |  (Next.js 16)    |
                    +--------+---------+
                             |
                     API Proxy (/api/*)
                             |
              +--------------v--------------+
              |     FastAPI Backend          |
              |     (Railway, 2 workers)     |
              |                              |
              |  +--------+  +----------+   |
              |  | Search |  | Billing  |   |
              |  | Pipe-  |  | (Stripe) |   |
              |  | line   |  +----------+   |
              |  +---+----+                 |
              |      |                      |
              |  +---v-----------+          |
              |  | Consolidation |          |
              |  | (3 sources)   |          |
              |  +--+---+---+---+          |
              |     |   |   |              |
              +-----|---|---|--+--+---------+
                    |   |   |  |  |
           +--------+  |  +--+ |  +--------+
           |        |  |     | |           |
      +----v---+ +-v--v-+ +-v-v---+ +-----v-----+
      | PNCP   | | PCP  | |Compras| | Supabase  |
      | API    | | v2   | |Gov v3 | | (Postgres)|
      +--------+ +------+ +-------+ +-----------+
                                      |    |
                               +------+    +------+
                               | Redis |   | ARQ  |
                               |(cache)|   |(jobs)|
                               +-------+   +------+
```

**Key Patterns:**
- 7-stage pipeline orchestrator (`SearchPipeline.run()`) with state machine transitions
- Per-source circuit breakers (PNCP, PCP, ComprasGov) + Supabase circuit breaker
- Two-level cache: L1 InMemory/Redis (4h) + L2 Supabase (24h) + L3 local file (emergency)
- SSE progress tracking via Redis Streams (cross-worker) with in-memory fallback
- ARQ background jobs for LLM summaries + Excel generation
- Timeout chain: Pipeline(110s) > Consolidation(100s) > PerSource(80s) > PerUF(30s) > PerModality(20s)
- Feature flags: 50+ runtime-reloadable flags with 60s TTL cache

---

## GTM Readiness Matrix

| Dimension | Status | Score | Key Issues | Blockers? |
|-----------|--------|-------|------------|-----------|
| **Reliability** | GREEN | 8/10 | Circuit breakers on all sources + Supabase. SWR cache absorbs failures. Timeout chain validated at startup. Time-budget skip for LLM after 90s. | No |
| **Scalability** | YELLOW | 6/10 | Single Railway instance (2 Gunicorn workers). MAX_CONCURRENT_SEARCHES=3. In-memory caches are per-worker. Redis needed for cross-worker state. | No blocker, but limits exist |
| **Security** | GREEN | 8/10 | JWT ES256+JWKS, RLS on all tables, Stripe signature verification, CORS no-wildcard in prod, log sanitization, MFA support, rate limiting. | No |
| **Observability** | GREEN | 8/10 | Prometheus (50+ metrics), OpenTelemetry traces, Sentry (PII scrubbed), structured JSON logging, request_id/search_id correlation, health canary. | No |
| **Data Pipeline** | YELLOW | 7/10 | ComprasGov v3 DOWN since 2026-03-03 (disabled). PNCP page size=50 limit detected. PCP v2 public, no auth. Multi-level cache handles outages. | No blocker, but 1/3 sources offline |
| **Billing** | GREEN | 8/10 | Stripe webhooks: 8 event types handled. Idempotency via DB. Signature verification. Profile sync on all events. 3-day grace period. Boleto/PIX support. | No |
| **API Contracts** | GREEN | 7/10 | OpenAPI schema snapshot validated in CI. Pydantic v2 for all request/response validation. Structured error codes. BUT: no API versioning beyond `/v1/` prefix. | No |
| **Performance** | YELLOW | 7/10 | Pipeline: <110s target. Cache hits: <2s. LLM: ~60ms/call (nano). BUT: full search with 27 UFs can be slow. No CDN. Railway 300s hard timeout. | No blocker |
| **Error Handling** | GREEN | 8/10 | SearchErrorCode enum (7 values). Graceful degradation banners (stale cache, partial results). Portuguese user-facing messages. SSE error events. | No |
| **Configuration** | YELLOW | 6/10 | 50+ feature flags. 90 migrations. Env var validation at startup in production. BUT: no config validation tool, easy to misconfigure. | No blocker |

---

## Critical Path Analysis

### GTM Blockers (Must Fix Before Charging)

**None identified.** The system is architecturally ready for paying customers. The failure modes are well-handled with graceful degradation rather than hard failures.

### High Priority (Fix within 30 days post-launch)

**H1. CI gates are advisory, not blocking (EFFORT: 2h)**
- `pip-audit` vulnerability scan: `continue-on-error: true` -- a HIGH CVE could ship to production
- `ruff check` linting: `continue-on-error: true`
- `mypy` type checking: `continue-on-error: true`
- **Impact:** A dependency vulnerability or type error could reach production undetected
- **Fix:** Remove `continue-on-error` and fix existing violations. At minimum, make pip-audit blocking for HIGH severity.

**H2. ComprasGov v3 API offline since 2026-03-03 (EFFORT: 1h investigation)**
- Master flag `COMPRASGOV_ENABLED=false` correctly set
- **Impact:** Data coverage reduced to 2/3 sources. Customers may miss opportunities posted only on ComprasGov.
- **Action:** Re-evaluate every 2 weeks. Consider adding a data coverage disclaimer to the product.

**H3. Single-instance scaling ceiling (EFFORT: 8-16h)**
- 2 Gunicorn workers, MAX_CONCURRENT_SEARCHES=3
- In-memory L1 cache is per-worker (not shared)
- In-memory auth token cache: per-worker OrderedDict (Redis L2 compensates)
- **Impact:** At ~100 concurrent users doing searches, the system would queue heavily. Estimated capacity: ~20-30 concurrent search users.
- **Fix:** Redis Streams for SSE already enables horizontal scaling. Add a second Railway service instance and validate cross-worker cache coherence.

**H4. No graceful shutdown for in-flight searches (EFFORT: 4h)**
- Railway deploys kill the process. In-flight searches return nothing.
- The lifespan handler marks sessions as timed out, but users see errors.
- **Impact:** Every deploy causes ~30s of search failures for active users.
- **Fix:** Implement SIGTERM handler that drains in-flight requests before exiting. Railway sends SIGTERM with configurable grace period.

### Medium Priority (Fix within 90 days)

**M1. Feature flag explosion (50+ flags, EFFORT: 8h)**
- `_FEATURE_FLAG_REGISTRY` has 30+ entries
- `config/features.py` has 60+ variables
- No admin UI for flag management (only env vars + runtime reload endpoint)
- **Risk:** Misconfiguration is the most common production incident cause in complex systems.
- **Fix:** Build a feature flag dashboard (admin only). Categorize flags as "launch", "ops", "experiment", "deprecated".

**M2. Migration count growing rapidly (90 migrations, EFFORT: 4h)**
- 90 SQL migration files in `supabase/migrations/`
- Migration CI gate exists but only warns on PRs
- **Risk:** Migration apply time grows. One bad migration could cause downtime.
- **Fix:** Squash historical migrations into a baseline. Ensure migration gate blocks (not just warns) for production pushes.

**M3. No load testing baseline (EFFORT: 8h)**
- `load-test.yml` workflow exists but unclear if regularly run
- No documented capacity numbers
- **Risk:** Unknown breaking point for concurrent users
- **Fix:** Run load test, document p50/p95/p99 for key endpoints, set alerting thresholds.

**M4. ARQ worker liveness detection is cached (15s interval, EFFORT: 2h)**
- Worker health check has 15s cache (`_WORKER_CHECK_INTERVAL`)
- If worker dies, it takes up to 15s to detect and fallback to inline processing
- **Impact:** Background LLM/Excel jobs silently fail for up to 15s after worker crash
- **Fix:** Acceptable for now but document the behavior. Consider Redis health pub/sub.

**M5. OpenAI dependency is a single point of failure for classification (EFFORT: 4h)**
- `llm_arbiter.py` uses GPT-4.1-nano exclusively
- 5s timeout, 1 retry
- Fallback: REJECT on failure (zero noise philosophy) -- this is correct behavior
- **Risk:** If OpenAI has an outage, all zero-match classifications default to REJECT, reducing result quality
- **Fix:** Consider adding a simple local model fallback (e.g., keyword heuristic with lower confidence) for when OpenAI is unreachable.

### Low Priority (Technical Debt, No GTM Impact)

**L1.** `mypy` has `disallow_untyped_defs = false` -- some functions lack type hints
**L2.** Debug endpoint `/debug/pncp-test` exists in production (admin-gated, but still)
**L3.** `health.py:get_detailed_health()` uses `os.popen("python --version")` -- should use `sys.version`
**L4.** Local file cache TTL (24h) could accumulate disk usage on Railway (200MB cap exists but untested at scale)
**L5.** Auth cache dual-hash transition window (1 hour) still active on every deploy -- minor performance overhead

---

## Backend Module Health

| Module | Lines (est.) | Test Files | Health | GTM Risk |
|--------|-------------|------------|--------|----------|
| `search_pipeline.py` + `pipeline/stages/` | ~800 | 15+ | Excellent | LOW -- well-decomposed orchestrator |
| `consolidation.py` | ~400 | 10+ | Good | LOW -- handles all failure modes |
| `pncp_client.py` | ~600 | 20+ | Good | MEDIUM -- depends on PNCP API stability |
| `portal_compras_client.py` | ~300 | 5+ | Good | LOW |
| `filter.py` + `filter_*.py` (8 modules) | ~2000 | 30+ | Good | LOW -- well-decomposed facade |
| `llm_arbiter.py` | ~400 | 15+ | Good | MEDIUM -- OpenAI dependency |
| `search_cache.py` | ~500 | 10+ | Good | LOW -- 3-level fallback |
| `auth.py` | ~520 | 10+ | Excellent | LOW -- ES256+JWKS, L1+L2 cache |
| `authorization.py` | ~180 | 5+ | Good | LOW |
| `quota.py` | ~1500 | 15+ | Good | LOW -- atomic check+increment |
| `webhooks/stripe.py` | ~700 | 10+ | Good | LOW -- idempotent, signature-verified |
| `progress.py` | ~300 | 5+ | Good | LOW -- Redis Streams + fallback |
| `health.py` | ~960 | 5+ | Good | LOW -- comprehensive checks |
| `metrics.py` | ~200 | 3+ | Good | LOW -- graceful no-op if prometheus missing |
| `job_queue.py` | ~300 | 5+ | Good | LOW -- inline fallback on queue failure |
| `config/` (5 modules) | ~500 | 5+ | Good | MEDIUM -- large surface area |
| `supabase_client.py` | ~400 | 10+ | Good | LOW -- circuit breaker, pool management |
| `startup/` (7 modules) | ~600 | 5+ | Good | LOW -- clean app factory pattern |
| `routes/` (35 modules) | ~5000 | 50+ | Good | LOW |

**Total backend:** ~199 source files, ~72,700 lines, ~336 test files

---

## Dependency Audit

| Dependency | Version | Risk | Notes |
|------------|---------|------|-------|
| `fastapi` | 0.129.0 | LOW | Stable, well-maintained |
| `uvicorn[standard]` | 0.41.0 | LOW | Re-enabled after SIGSEGV fix. uvloop not on Windows. |
| `pydantic` | 2.12.5 | LOW | v2, email validation included |
| `httpx` | 0.28.1 | LOW | Modern async HTTP client |
| `openai` | 1.109.1 | LOW | Pinned, GPT-4.1-nano |
| `supabase` | 2.28.0 | MEDIUM | Supabase Python SDK still maturing |
| `stripe` | 11.4.1 | LOW | Mature, well-documented |
| `redis` | 5.3.1 | LOW | Stable |
| `cryptography` | >=46.0.5,<47 | MEDIUM | CVE-2026-26007 patched. Fork-safety with Gunicorn requires testing on major upgrades. |
| `google-api-python-client` | 2.190.0 | LOW | Google Sheets export |
| `sentry-sdk` | >=2.0.0 | LOW | Error tracking |
| `prometheus_client` | >=0.20.0 | LOW | Metrics |
| `arq` | >=0.26,<1.0 | MEDIUM | No runtime reconnection (issue #386). Community standard is restart wrapper. |
| `opentelemetry-*` | >=1.25 | MEDIUM | grpcio transitive dep is fork-unsafe. Dockerfile explicitly removes it. |
| `python-multipart` | >=0.0.22 | LOW | CVE-2026-24486 patched |
| `PyJWT` | 2.11.0 | LOW | ES256+JWKS support |
| `reportlab` | 4.4.0 | LOW | Pure Python, no C extensions |

**Key concern:** The `opentelemetry` stack pulls transitive dependencies that can be fork-unsafe with Gunicorn. The Dockerfile mitigates this with explicit `pip uninstall -y grpcio grpcio-status`, but this is fragile -- any dependency update could re-introduce it.

---

## Performance Baseline

| Operation | Target | Actual (estimated) | Notes |
|-----------|--------|-------------------|-------|
| Search (cache hit) | <2s | ~500ms-2s | L1 InMemory is instant; L2 Supabase adds ~200ms |
| Search (cache miss, single UF) | <30s | 10-30s | Depends on PNCP response time |
| Search (cache miss, all 27 UFs) | <110s | 30-110s | Batched (5 UFs/batch, 2s delay) |
| LLM classification | <100ms | ~60ms | GPT-4.1-nano, 5s timeout |
| Auth token validation | <10ms | <5ms (L1 hit) | SHA256 hash + OrderedDict lookup |
| Health check | <1s | ~200ms | Redis ping + Supabase query |
| Stripe webhook | <30s | <5s | Timeout guard at 30s |
| SSE heartbeat | 15s interval | 15s | Prevents Railway idle timeout (60s) |

**Scaling limits (estimated):**
- Concurrent search users before degradation: ~20-30 (2 workers, 3 max concurrent searches)
- Auth cache capacity: 1000 entries per worker (2000 total)
- Redis connection pool: 25 per worker (50 total)
- Supabase connection pool: 25 per worker (50 total)

---

## CI/CD Assessment

**Strengths:**
- 17 GitHub Actions workflows covering tests, deployment, migrations, security scanning, E2E
- Three-layer migration defense (PR warning, push alert, auto-apply on deploy)
- OpenAPI schema snapshot validation prevents accidental API contract drift
- Backend test gate: zero failures required for merge
- Coverage threshold: 70% (enforced in CI)
- Per-module coverage thresholds (`check_module_coverage.py`)

**Weaknesses:**
- Vulnerability scan (`pip-audit`): non-blocking (`continue-on-error: true`)
- Lint (`ruff`): non-blocking
- Type check (`mypy`): non-blocking
- Load test workflow exists but unclear execution frequency
- No staging environment for pre-production validation (staging-deploy.yml exists but needs verification)

---

## Recommendations (Top 5 Prioritized)

1. **Make pip-audit blocking in CI** (H1, 2h effort). This is the single most impactful security improvement. A HIGH CVE shipping to production could damage customer trust immediately at launch.

2. **Document and communicate capacity limits** (H3 + M3, 4h effort). Before launch, run the load test workflow and document the breaking point. Set Prometheus alerts at 80% of capacity. Be honest with early customers about concurrent search limits.

3. **Add SIGTERM drain handler for zero-downtime deploys** (H4, 4h effort). Every deploy causes a brief outage for active search users. Implementing graceful shutdown with a 30s drain period prevents the worst user experience (search suddenly fails mid-progress).

4. **Triage feature flags** (M1, 8h effort). Categorize the 50+ flags into "permanent" vs "temporary" vs "deprecated". Remove flags for features that are proven stable. This reduces the blast radius of misconfiguration.

5. **ComprasGov v3 contingency plan** (H2, 1h effort). Document the data coverage impact for customers. If the API remains down for 30+ days, consider removing it from the UI entirely rather than showing a disabled source that erodes trust.

---

## Appendix: Key File Reference

| Category | Path | Purpose |
|----------|------|---------|
| App entry | `backend/main.py` | App factory, debug endpoint |
| App factory | `backend/startup/app_factory.py` | FastAPI create_app() |
| Config | `backend/config/{base,features,pipeline,pncp,cors}.py` | All configuration |
| Pipeline | `backend/search_pipeline.py` + `backend/pipeline/stages/` | 7-stage orchestrator |
| Consolidation | `backend/consolidation.py` | Multi-source fetch + dedup |
| PNCP client | `backend/pncp_client.py` | Circuit breaker, retry, batching |
| Filter engine | `backend/filter.py` + `backend/filter_*.py` (8 files) | Keyword + LLM filtering |
| LLM | `backend/llm_arbiter.py` | GPT-4.1-nano classification |
| Cache | `backend/search_cache.py` | 3-level SWR cache |
| Auth | `backend/auth.py` | JWT ES256+JWKS, L1+L2 token cache |
| Quota | `backend/quota.py` | Plan-based quota enforcement |
| Billing | `backend/webhooks/stripe.py` | 8 Stripe event types |
| Progress | `backend/progress.py` | SSE via Redis Streams |
| Health | `backend/health.py` | System + source health checks |
| Metrics | `backend/metrics.py` | 50+ Prometheus metrics |
| Jobs | `backend/job_queue.py` | ARQ background LLM+Excel |
| Supabase | `backend/supabase_client.py` | Circuit breaker, pool mgmt |
| Middleware | `backend/startup/middleware_setup.py` | CORS, rate limit, security headers |
| CI | `.github/workflows/backend-tests.yml` | Test + schema + security gate |
| Migrations | `supabase/migrations/` (90 files) | Database schema |
