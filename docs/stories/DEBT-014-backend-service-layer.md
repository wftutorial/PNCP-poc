# DEBT-014: Backend Service Layer & Lifecycle

**Sprint:** 2
**Effort:** 19h
**Priority:** MEDIUM
**Agent:** @architect (Atlas) + @dev

## Context

The backend has structural issues that affect maintainability and scalability preparation. Legacy routes are mounted in duplicate (versioned `/v1/` + legacy root) with 33 `include_router` statements creating ~61 route mounts — but removal requires usage data first. Background tasks in lifespan are managed ad-hoc (10+ tasks with manual create/cancel/await). Global mutable singletons lack proper cleanup (auth cache unbounded, LLM arbiter has LRU(5000)). Auth token cache is per-worker (not shared between Gunicorn workers). CSP uses `unsafe-inline`/`unsafe-eval` required by Next.js + Stripe.js.

## Scope

| ID | Debito | Horas |
|----|--------|-------|
| SYS-001 | Dual route mounts (versioned + legacy) — 33 statements, ~61 mounts, sunset 2026-06-01 | 4h |
| SYS-006 | 10+ background tasks in lifespan without lifecycle manager | 4h |
| SYS-010 | Global mutable singletons without cleanup (auth cache unbounded, LLM arbiter LRU(5000)) | 3h |
| SYS-018 | Auth token cache in-memory not shared between Gunicorn workers | 4h |
| SYS-022 | `unsafe-inline`/`unsafe-eval` in CSP frontend — required by Next.js + Stripe.js | 4h |

## Tasks

### Legacy Route Deprecation (SYS-001) — 4h

- [ ] Add Prometheus counter `smartlic_legacy_route_hits_total` (labels: path, method)
- [ ] Instrument all legacy (non-`/v1/`) route mounts with deprecation counter
- [ ] Plan sunset: after 2+ weeks of data, identify routes with zero hits for removal
- [ ] Document route migration guide for any external consumers
- [ ] Do NOT remove routes yet — this sprint is data collection only

### Task Lifecycle Manager (SYS-006) — 4h

- [ ] Create `TaskRegistry` class to manage background task lifecycle
- [ ] Register all 10+ lifespan tasks with TaskRegistry (name, create, cancel, health check)
- [ ] Implement centralized startup/shutdown sequence
- [ ] Add health endpoint for background task status
- [ ] Reduce lifespan boilerplate (single registry.start_all / registry.stop_all)

### Bounded Caches (SYS-010) — 3h

- [ ] Add TTL to `auth.py:_token_cache` (currently unbounded dict)
- [ ] Add max entry limit to auth cache (evict LRU when exceeded)
- [ ] Review `filter.py:_filter_stats_tracker` — add cleanup schedule
- [ ] Verify `llm_arbiter.py:_arbiter_cache` LRU(5000) is appropriate for current scale
- [ ] Add metrics for cache hit/miss rates

### Shared Auth Cache (SYS-018) — 4h

- [ ] Migrate auth token cache to Redis (shared between Gunicorn workers)
- [ ] Use short TTL (5 minutes) to balance freshness vs Redis calls
- [ ] Fallback to in-memory if Redis unavailable (resilience pattern)
- [ ] Verify no auth regressions with multi-worker setup

### CSP Investigation (SYS-022) — 4h

- [ ] Research nonce-based CSP compatible with Next.js 16
- [ ] Research Stripe.js CSP requirements (official docs)
- [ ] Test nonce-based CSP in development environment
- [ ] Document findings and compatibility constraints
- [ ] If feasible, implement nonce-based CSP; if not, document as accepted risk with mitigation plan

## Acceptance Criteria

- [ ] AC1: Deprecation counter metric exists for all legacy route mounts
- [ ] AC2: TaskRegistry manages all background tasks (centralized start/stop)
- [ ] AC3: Auth cache has TTL and max entry limit (no unbounded growth)
- [ ] AC4: Auth token cache shared via Redis between workers
- [ ] AC5: CSP investigation documented with clear recommendation
- [ ] AC6: Zero regressions in backend test suite (5774+ pass)

## Tests Required

- Deprecation counter: verify metric increments on legacy route hit
- TaskRegistry: start all, stop all, health check for each task
- Auth cache: TTL expiration test, max entries eviction test
- Redis auth cache: verify cross-worker cache hit (integration test)
- CSP: if implemented, verify Stripe checkout still works

## Definition of Done

- [ ] All tasks complete
- [ ] Tests passing (backend 5774+ / 0 fail)
- [ ] No regressions
- [ ] Route usage data collection active (2+ weeks before removal)
- [ ] CSP investigation documented
- [ ] Code reviewed
