# STORY-271: Resolve All 5 Sentry Unresolved Issues

**GTM Audit Ref:** Sentry Live Audit (2026-02-25) + Track D (H-1, H-2, M-1)
**Priority:** P0
**Effort:** 1-2 days
**Squad:** @dev + @devops
**Source:** Sentry screenshot `gtm-audit/06-sentry-unresolved-issues.png`

## Context

The GTM validation squad captured 5 unresolved Sentry issues in production (as of 2026-02-25 23:25 UTC). These must be resolved or triaged before GTM to achieve the "0 unresolved Sentry issues" operational maturity gate.

## Current Issues

| # | Issue | Level | Events | Age | Root Cause |
|---|-------|-------|--------|-----|------------|
| 1 | **APIError** — FK violation `search_results_cache_user_id_profiles_fkey` | Error | 44 | 6d | Cache warming uses `WARMING_USER_ID=00000000-...` which doesn't exist in `profiles` table |
| 2 | **WORKER KILLED BY TIMEOUT** — pid=4, duration=-1s, `/v1/buscar` | Fatal | 1 | 9hr | Heavy search exceeded GUNICORN_TIMEOUT=115s |
| 3 | **WORKER TIMEOUT (pid:4)** — gunicorn.error | Fatal | 5 | 3d | Same root cause as #2 |
| 4 | **Worker SIGABRT (pid:4)** — gunicorn.error | Fatal | 5 | 3d | Gunicorn sends SIGABRT after timeout |
| 5 | **AllSourcesFailedError** — "PNCP: Early return (elapsed 80s)" | Error | 3 | 5d | All sources timed out during search |

## Acceptance Criteria

### AC1: Fix Cache Warming FK Violation (Issue #1 — 44 events)
- [ ] Insert a system profile row for `WARMING_USER_ID`:
  ```sql
  INSERT INTO profiles (id, full_name, plan_type, is_admin)
  VALUES ('00000000-0000-0000-0000-000000000000', 'System Cache Warmer', 'system', false)
  ON CONFLICT (id) DO NOTHING;
  ```
- [ ] Verify: cache warming saves to Supabase L2 without FK violation
- [ ] Resolve Sentry issue after deploy
- [ ] **File:** New migration in `supabase/migrations/`

### AC2: Fix Worker Timeout Root Cause (Issues #2, #3, #4)
- [ ] Investigate: which search queries trigger >115s execution?
- [ ] Verify `PNCP_TIMEOUT_PER_MODALITY` Railway env var: currently `120` (IGNORED, falls back to 20s safe default). Either remove or set to `20`.
- [ ] Verify early return is functioning: `EARLY_RETURN_TIME_S=80` + `EARLY_RETURN_THRESHOLD_PCT=0.8`
- [ ] If worker still times out: reduce `PIPELINE_TIMEOUT` from 110s to 100s (gives 15s buffer before GUNICORN_TIMEOUT=115s)
- [ ] Mark Sentry issues as resolved after fix
- [ ] **File:** `backend/config.py`, Railway env vars

### AC3: Reduce AllSourcesFailedError (Issue #5)
- [ ] Investigate: was this a transient PNCP outage or systematic?
- [ ] Verify PNCP health canary is working correctly (see AC4)
- [ ] Verify circuit breaker thresholds are appropriate (currently: 15 failures, 60s cooldown)
- [ ] If PNCP was down: confirm stale cache was served as fallback
- [ ] If stale cache was NOT served: investigate why SWR fallback didn't trigger
- [ ] Mark as resolved or downgrade to warning (expected behavior during outages)

### AC4: Fix PNCP Health Canary (Track D H-2)
- [ ] PNCP canary in `health.py` uses WRONG date format (`YYYY-MM-DD` instead of `yyyyMMdd`)
- [ ] PNCP canary is MISSING required `codigoModalidadeContratacao` parameter
- [ ] HTTP 400 is currently treated as "healthy" (because `< 500`)
- [ ] Fix: use `yyyyMMdd` format, add `codigoModalidadeContratacao=6`, check `< 400`
- [ ] **File:** `backend/health.py` (line ~143-153)

### AC5: Clean Up Stale Railway Env Var (Track D H-1)
- [ ] Remove or correct `PNCP_TIMEOUT_PER_MODALITY=120` on Railway
- [ ] Command: `railway variables set PNCP_TIMEOUT_PER_MODALITY=20` or `railway variables delete PNCP_TIMEOUT_PER_MODALITY`
- [ ] Verify startup log no longer shows "TIMEOUT MISCONFIGURATION" warning

### AC6: Sentry Zero Unresolved Gate
- [ ] After all fixes deployed: verify 0 unresolved issues in Sentry
- [ ] Monitor for 24h: no new Fatal/Error issues
- [ ] Screenshot Sentry dashboard as evidence

## Testing Strategy

- [ ] Unit test: cache warming with valid WARMING_USER_ID profile
- [ ] Unit test: PNCP health canary with correct params
- [ ] Unit test: pipeline timeout < GUNICORN_TIMEOUT
- [ ] Integration: run search, verify no worker timeout in Railway logs
- [ ] Monitor Sentry post-deploy for 24h

## Files to Modify

| File | Change |
|------|--------|
| `supabase/migrations/XXXXXXXX_warming_user_profile.sql` | **NEW** — Insert system profile |
| `backend/health.py` | Fix PNCP canary params + date format + status check |
| `backend/config.py` | Possibly reduce PIPELINE_TIMEOUT to 100s |
| Railway env vars | Fix/remove PNCP_TIMEOUT_PER_MODALITY |
| `backend/tests/` | Tests for canary fix |

## Dependencies

- AC1 requires `supabase db push` (DevOps)
- AC5 requires Railway CLI access
