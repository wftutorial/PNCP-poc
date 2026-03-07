# DEBT-018: Infrastructure, Security & Observability

**Sprint:** Backlog
**Effort:** 86h
**Priority:** LOW
**Agent:** @devops (Gage) + @dev

## Context

Remaining infrastructure and observability debts that improve operational excellence and security posture. These include dead code cleanup, CDN setup, the critical service-role-key issue (SYS-023 — service role bypasses RLS for all operations), staging environment, API documentation, incident runbook, and feature flags runtime UI. While individually lower priority, collectively they represent significant operational maturity improvements.

**Note:** SYS-023 (service role key for all DB operations) is HIGH severity but deferred to Backlog due to 16h effort and complex implementation (requires per-user token architecture). It should be prioritized if security audit is required for B2G contracts.

## Scope

| ID | Debito | Horas |
|----|--------|-------|
| SYS-007 | Lead prospecting modules apparently dead code (5 modules) | 2h |
| SYS-008 | Frontend proxy route explosion (58 routes, no `createProxyRoute()` generic) | 12h |
| SYS-014 | Test files in backend root (outside `tests/`) | 1h |
| SYS-019 | No CDN for static assets — frontend served directly from Railway | 8h |
| SYS-020 | Singleton Supabase client — 2 workers x 50 pool = 100 potential connections | 4h |
| SYS-023 | Service role key for ALL DB operations — bypasses RLS entirely | 16h |
| SYS-025 | Excel temp files in frontend proxy not cleaned on crash | 2h |
| SYS-026 | Rate limiter in-memory store with infrequent cleanup (every 200 requests) | 2h |
| SYS-028 | `cryptography` pinned to 46.0.5 for fork-safety | 4h |
| SYS-029 | `requests` lib only used for sync PNCP fallback | 4h |
| SYS-030 | `redis_client.py` deprecated shim for `redis_pool` | 1h |
| SYS-032 | No integration tests against real APIs — contract changes detected only in production | 16h |
| SYS-033 | E2E tests use production credentials | 8h |
| SYS-036 | No API documentation beyond auto-generated OpenAPI (disabled in prod) | 8h |
| SYS-037 | `.env.example` potentially stale — 25+ flags without automated check | 2h |
| SYS-038 | No runbook for incident response — knowledge only in CLAUDE.md/MEMORY.md | 8h |
| CROSS-003 | Feature flags without runtime UI — 25+ flags in env vars, require container restart | 16h |
| SYS-021 | Cache key does not include all filter parameters | 4h |
| CROSS-006 | No staging environment — E2E uses production, no integration test isolation | 16h |

## Tasks

### Quick Wins (7h)

- [ ] Audit and remove dead lead prospecting modules (SYS-007)
- [ ] Move test files from backend root to `tests/` (SYS-014)
- [ ] Remove `redis_client.py` shim (SYS-030)
- [ ] Add crash cleanup for Excel temp files in frontend proxy (SYS-025)
- [ ] Improve rate limiter cleanup frequency (SYS-026)
- [ ] Add `.env.example` validation script (SYS-037)

### Infrastructure (40h)

- [ ] Create `createProxyRoute()` utility to reduce 58 proxy files (SYS-008)
- [ ] Set up CDN (Cloudflare or similar) for static assets (SYS-019)
- [ ] Configure Supabase connection pool limits per-worker (SYS-020)
- [ ] Review and fix cache key generation to include all filter parameters (SYS-021)
- [ ] Set up Supabase staging project + Railway staging service (CROSS-006)
- [ ] Create staging environment documentation

### Security (20h)

- [ ] Implement per-user Supabase tokens for user-scoped operations (SYS-023)
- [ ] Restrict service role to admin-only operations
- [ ] Evaluate `cryptography` upgrade path (SYS-028)
- [ ] Remove `requests` dependency after async PNCP client migration (SYS-029, depends on DEBT-015)

### Observability (24h)

- [ ] Create integration test suite against real APIs (PNCP, PCP) with mocked responses as fallback (SYS-032)
- [ ] Move E2E to staging environment (SYS-033, depends on CROSS-006)
- [ ] Enable and customize OpenAPI documentation for production (SYS-036)
- [ ] Create incident response runbook (SYS-038)
- [ ] Create feature flags admin UI or adopt LaunchDarkly/Unleash (CROSS-003)

## Acceptance Criteria

- [ ] AC1: Zero dead code modules in production
- [ ] AC2: Proxy route creation uses shared utility (< 20 lines per route)
- [ ] AC3: Static assets served via CDN with proper cache headers
- [ ] AC4: User-scoped DB operations use per-user tokens (not service role)
- [ ] AC5: Staging environment operational (Supabase + Railway)
- [ ] AC6: Integration tests exist for PNCP and PCP API contracts
- [ ] AC7: Incident response runbook documented
- [ ] AC8: Feature flags toggleable without container restart
- [ ] AC9: Zero regressions

## Tests Required

- Proxy utility: verify routes proxy correctly with shared function
- Per-user token: verify RLS enforcement (user A cannot see user B data)
- Integration tests: API contract validation against live endpoints
- CDN: verify cache headers and asset delivery

## Definition of Done

- [ ] All tasks complete
- [ ] Tests passing (backend 5900+ / frontend 2800+ / 0 fail)
- [ ] No regressions
- [ ] Staging environment documented and operational
- [ ] Runbook reviewed by team
- [ ] Code reviewed
