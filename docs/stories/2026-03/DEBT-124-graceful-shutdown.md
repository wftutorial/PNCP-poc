# DEBT-124: Graceful Shutdown / Zero-Downtime Deploys
**Priority:** P1
**Effort:** 4h
**Owner:** @dev
**Sprint:** Week 2

## Context

Railway deploys send SIGTERM but the SmartLic backend does not drain in-flight requests. Every deploy causes approximately 30 seconds of search failures as active searches are killed mid-progress. For paying customers at R$397-997/month, a search failing because of a routine deploy is unacceptable. This is a prerequisite for horizontal scaling (P1-009) -- scaling without graceful shutdown means more instances = more deploy-time failures.

## Acceptance Criteria

- [ ] AC1: SIGTERM triggers drain behavior -- new requests receive 503 Service Unavailable, in-flight requests are allowed to complete
- [ ] AC2: In-flight search either completes normally or returns partial results (never an unhandled error)
- [ ] AC3: Drain timeout is configurable via `GRACEFUL_SHUTDOWN_TIMEOUT` env var (default 30s)
- [ ] AC4: Gunicorn `on_exit` hook or FastAPI lifespan `shutdown` event implements the drain logic
- [ ] AC5: SSE connections are gracefully closed with a `shutdown` event type before termination
- [ ] AC6: Health endpoint returns 503 during drain phase (load balancer stops sending new requests)
- [ ] AC7: `test_harden_022_graceful_shutdown.py` validates drain behavior with at least 5 test cases

## Technical Notes

**Approach options (choose one):**

1. **FastAPI lifespan shutdown event** -- Set a global `shutting_down` flag. Middleware checks flag and returns 503 for new requests. `asyncio.sleep(drain_timeout)` before actual shutdown.

2. **Gunicorn `on_exit` hook** -- Configure in `start.sh` or `gunicorn.conf.py`. Gunicorn sends SIGTERM to workers with `graceful_timeout`. Workers finish current requests.

3. **Hybrid** -- FastAPI lifespan sets flag + Gunicorn graceful_timeout as safety net.

**Key considerations:**
- Railway sends SIGTERM, then SIGKILL after a configurable timeout (default 10s, can be increased)
- Gunicorn `graceful_timeout` (currently 180s via `GUNICORN_TIMEOUT`) controls how long workers get to finish
- Railway may need `RAILWAY_HEALTHCHECK_TIMEOUT` or deploy config adjustment
- The `progress.py` SSE tracker should emit a `shutdown` event so frontend can show "deploying, please retry"

**Files to investigate:**
- `backend/start.sh` -- Gunicorn startup configuration
- `backend/main.py` -- FastAPI lifespan events
- `backend/health.py` -- Health endpoint (must return 503 during drain)

## Test Requirements

- [ ] `test_harden_022_graceful_shutdown.py` with cases:
  - SIGTERM sets shutting_down flag
  - New requests get 503 during shutdown
  - In-flight request completes during drain
  - Health endpoint returns 503 during drain
  - Drain timeout is respected (configurable)
- [ ] Existing search tests still pass
- [ ] Existing health endpoint tests still pass

## Files to Modify

- `backend/main.py` -- Add shutdown lifespan event, middleware for 503 during drain
- `backend/start.sh` -- Gunicorn graceful_timeout configuration
- `backend/config.py` -- `GRACEFUL_SHUTDOWN_TIMEOUT` env var
- `backend/health.py` -- Return 503 during drain phase
- `backend/tests/test_harden_022_graceful_shutdown.py` -- New test file

## Definition of Done

- [ ] All ACs pass
- [ ] Tests pass (existing + new)
- [ ] No regressions in CI
- [ ] Code reviewed
- [ ] Deploy to Railway and verify no search failures during subsequent deploy
