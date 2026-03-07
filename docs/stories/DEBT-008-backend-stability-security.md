# DEBT-008: Backend Stability & Security Quick Fixes

**Sprint:** 1
**Effort:** 19.5h
**Priority:** HIGH
**Agent:** @dev

## Context

Several backend issues affect stability and security. The Railway deployment runs at 1GB memory with 2 Gunicorn workers and has a history of OOM kills. The PNCP health canary uses `tamanhoPagina=10` and cannot detect the critical page size reduction from 500 to 50 (which already caused 10x more API calls). Stripe webhook handlers lack timeouts, risking indefinite blocking on long DB operations. The `STRIPE_WEBHOOK_SECRET` absence is only logged (not fail-at-startup), meaning payment processing could run without webhook verification. Additionally, naming inconsistencies (BidIQ vs SmartLic) persist in User-Agent headers and pyproject.toml.

## Scope

| ID | Debito | Horas |
|----|--------|-------|
| SYS-016 | Railway 1GB memory with 2 workers — OOM kills historical | 8h |
| SYS-017 | PNCP page size reduced to 50 — health canary uses 10, blind to change | 4h |
| SYS-024 | No timeout in Stripe webhook handler — long DB ops block indefinitely | 4h |
| SYS-027 | `STRIPE_WEBHOOK_SECRET` not-set only logged — should fail at startup | 1h |
| CROSS-004 | Naming inconsistency: BidIQ in User-Agent/pyproject vs SmartLic | 1h |
| SYS-013 | User-Agent hardcoded "BidIQ" in pncp_client.py | (bundled with CROSS-004) |
| SYS-015 | `pyproject.toml` references "bidiq-uniformes-backend" | 0.5h |

## Tasks

### Memory Optimization (SYS-016) — 8h

- [ ] Profile memory usage per worker: identify top consumers (in-memory caches, JSONB processing, LLM responses)
- [ ] Add memory usage Prometheus metric (`process_resident_memory_bytes` if not already)
- [ ] Implement memory limits for InMemoryCache (cap entries, not just TTL)
- [ ] Evaluate reducing to 1 worker + async (eliminates duplicate cache memory)
- [ ] Add OOM-kill detection and alerting
- [ ] Document Railway memory configuration and worker trade-offs

### PNCP Health Canary (SYS-017) — 4h

- [ ] Update health canary to test with `tamanhoPagina=50` (actual production limit)
- [ ] Add page size validation: if response with `tamanhoPagina=50` returns error, log alert
- [ ] Add metric `smartlic_pncp_page_size_limit` gauge (current known limit)
- [ ] Document the PNCP page size reduction history (500 -> 50, Feb 2026)

### Stripe Webhook Security (SYS-024, SYS-027) — 5h

- [ ] Add `asyncio.wait_for()` timeout (30s) around Stripe webhook DB operations (SYS-024)
- [ ] Add startup validation: if `STRIPE_WEBHOOK_SECRET` is None/empty, raise `SystemExit` (SYS-027)
- [ ] Log structured error with remediation steps before exit
- [ ] Update `.env.example` with clear documentation for `STRIPE_WEBHOOK_SECRET`

### Naming Cleanup (CROSS-004, SYS-013, SYS-015) — 1.5h

- [ ] Replace User-Agent "BidIQ" with "SmartLic" in `pncp_client.py` (SYS-013)
- [ ] Update `pyproject.toml` name from "bidiq-uniformes-backend" to "smartlic-backend" (SYS-015)
- [ ] Grep for any remaining "BidIQ" references in non-test, non-docs production code (CROSS-004)
- [ ] Fix any found references

## Acceptance Criteria

- [ ] AC1: Memory profiling data documented; InMemoryCache has entry count cap
- [ ] AC2: Health canary tests with `tamanhoPagina=50` (not 10)
- [ ] AC3: Stripe webhook handler has 30s timeout — long operations raise TimeoutError
- [ ] AC4: Application refuses to start if `STRIPE_WEBHOOK_SECRET` is not set
- [ ] AC5: Zero "BidIQ" strings in production code (excluding tests, docs, git history)
- [ ] AC6: `pyproject.toml` name is "smartlic-backend"
- [ ] AC7: Zero regressions in backend test suite (5774+ pass)

## Tests Required

- Startup test: verify `SystemExit` when `STRIPE_WEBHOOK_SECRET` is None
- Webhook timeout test: simulate slow DB op, verify timeout after 30s
- Health canary test: mock PNCP response with page size error
- Memory cap test: verify InMemoryCache evicts when entry limit reached
- Grep verification: no "BidIQ" in production code paths

## Definition of Done

- [ ] All tasks complete
- [ ] Tests passing (backend 5774+ / 0 fail)
- [ ] No regressions
- [ ] Memory profiling results documented in PR
- [ ] Code reviewed
