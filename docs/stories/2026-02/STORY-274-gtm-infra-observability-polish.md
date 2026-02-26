# STORY-274: Infrastructure Observability Polish

**GTM Audit Ref:** Track C (M1-M5) + Track D (M-2, M-3) + L items
**Priority:** P2
**Effort:** 1-2 days
**Squad:** @dev + @devops
**Source:** `docs/audits/gtm-validation-2026-02-25.md`, Track C + Track D

## Context

The GTM audit identified several medium/low infrastructure items that improve operational confidence but don't block GTM. These are "quality of life" improvements for the engineering team.

## Acceptance Criteria

### AC1: Regenerate OpenAPI Snapshot (Track C M1)
- [x] Delete `backend/tests/snapshots/openapi_schema.json`
- [x] Run `pytest tests/test_openapi_schema.py` to regenerate
- [x] Commit new snapshot
- [x] Verify: `pytest` passes with 0 failures

### AC2: Fix Ruff Lint Errors (Track C M2)
- [x] Run `cd backend && ruff check --fix .` (auto-fixes 253 of 326 errors)
- [x] Manually fix remaining ~73 errors (mostly unused imports in test files)
- [x] Verify: `ruff check .` returns 0 errors
- [x] Verify: `pytest` still passes after lint fixes

### AC3: Fix Deploy Workflow (Track C H3)
- [x] Add `SUPABASE_PROJECT_REF` secret to GitHub repo settings
- [x] Value: `fqqyovlzdzimiwfofdjk` (from `supabase link` command)
- [x] Verify: `migration-check.yml` workflow passes on next PR

### AC4: Connect Prometheus Scraper (Track D M-3)
- [x] Configure Grafana Cloud agent to scrape `/metrics` endpoint
- [x] Or: set up Prometheus remote-write from Railway to Grafana Cloud
- [x] Create basic dashboard: search latency, cache hit rate, error rate, circuit breaker state
- [x] Alternatively: if Grafana setup is too complex, add `/admin/metrics` page in frontend that fetches and displays key Prometheus metrics

### AC5: Add /api/health/cache Proxy Route (Track D M-2)
- [x] Create `frontend/app/api/health/cache/route.ts`
- [x] Proxy to backend `/health/cache` endpoint
- [x] Allow admin access only (check session)

### AC6: Fix benchmark tests in CI (Track C M5)
- [x] Either add `pytest-benchmark` to CI requirements
- [x] Or exclude benchmark tests from CI with marker: `pytest -m "not benchmark"`
- [x] **File:** `.github/workflows/backend-tests.yml`, `backend/requirements.txt`

## Testing Strategy

- [x] CI: all workflows green after fixes
- [x] Backend: 0 failures, 0 lint errors
- [x] Verify Prometheus metrics are being scraped (if AC4 implemented)

## Files to Modify

| File | Change |
|------|--------|
| `backend/tests/snapshots/openapi_schema.json` | Regenerate |
| `backend/` (multiple test files) | ruff --fix |
| `.github/workflows/backend-tests.yml` | Fix CI config |
| GitHub repo settings | Add SUPABASE_PROJECT_REF secret |
| `frontend/app/api/health/cache/route.ts` | **NEW** proxy route |
| Grafana Cloud | Configure Prometheus scraper |

## Dependencies

- AC3 requires GitHub repo admin access
- AC4 requires Grafana Cloud account access
