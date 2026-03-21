# CI/CD Workflow Documentation

Last updated: 2026-03-21

## PR Gates (required checks for merge to main)

| Workflow | File | Trigger | Purpose |
|----------|------|---------|---------|
| Backend Tests (PR Gate) | `backend-tests.yml` | PR to main, push to main | **Authoritative backend gate.** Runs pytest (70% coverage), per-module thresholds, pip-audit (blocking), OpenAPI schema snapshot, ruff lint (advisory), mypy (advisory). |
| Frontend Tests (PR Gate) | `frontend-tests.yml` | PR to main, push to main | **Authoritative frontend gate.** Runs Jest (coverage), TypeScript check, npm audit critical (blocking), bundle size budget. |
| PR Validation (Metadata + Security) | `pr-validation.yml` | PR to main/master | Validates PR title (conventional commits), body sections, secret detection (TruffleHog), Trivy CRITICAL scan. Supplementary to test gates. |

## Post-Merge (push to main)

| Workflow | File | Trigger | Purpose |
|----------|------|---------|---------|
| Deploy to Production (Railway) | `deploy.yml` | Push to main (backend/** or frontend/** paths), manual | Deploys backend and/or frontend to Railway, applies Supabase migrations, smoke tests, Slack notification. |
| Migration Check (Post-Merge Alert) | `migration-check.yml` | Push to main, daily schedule, manual | Blocks (exit 1) if unapplied migrations detected. Catches CRIT-039/CRIT-045 recurrence. |
| Tests (Full Matrix + Integration + E2E) | `tests.yml` | PR to main/master, push to main/master | Full cross-version matrix (Python 3.11+3.12), integration tests, E2E (Playwright). Complements single-version gates in backend-tests.yml/frontend-tests.yml. |

## Scheduled

| Workflow | File | Trigger | Purpose |
|----------|------|---------|---------|
| Cleanup (Scheduled Maintenance) | `cleanup.yml` | Weekly Sunday 00:00 UTC, manual | Deletes merged branches older than 30 days; deletes workflow runs older than 90 days (keeps 10 minimum). |
| CodeQL Security Scan | `codeql.yml` | Push to main, PR to main, weekly Monday 00:00 UTC, manual | Static analysis (Python + JS/TS), TruffleHog secret scan, dependency review on PRs. |
| Sync Sectors Fallback (Monthly) | `sync-sectors.yml` | Monthly 1st at 03:00 UTC, manual | Syncs SETORES_FALLBACK in frontend from backend /setores endpoint; creates PR if changed. |
| Load Testing (Locust) | `load-test.yml` | Weekly Sunday 02:00 UTC, manual, PR to main/master (backend paths) | Locust load test against local backend (50 users, 120s). Validates failure rate < 5%, P95 < 10s. |
| Lighthouse CI (Performance Audit) | `lighthouse.yml` | PR to main (frontend paths), push to main (frontend paths) | Lighthouse performance/accessibility/SEO audit; posts scores as PR comment. |

## Deployment

| Workflow | File | Trigger | Purpose |
|----------|------|---------|---------|
| Deploy to Production (Railway) | `deploy.yml` | Push to main, manual | Production deploy via Railway CLI. Includes migration auto-apply (CRIT-050). |
| Deploy to Staging | `staging-deploy.yml` | Push to develop/feature/**, PR to develop/feature/**, manual | Staging deploy via Railway. **NOTE: Staging environment not currently provisioned** (secrets RAILWAY_TOKEN_STAGING etc. not set). Scoped to develop/feature branches only. |

## PR Supplementary (non-blocking, informational)

| Workflow | File | Trigger | Purpose |
|----------|------|---------|---------|
| Migration Gate (PR Warning) | `migration-gate.yml` | PR touching supabase/migrations/** | Posts PR comment warning if migrations exist locally but not applied remotely. Non-blocking — deploy workflow auto-applies. Part of CRIT-050 three-layer defense. |
| handle_new_user Guard | `handle-new-user-guard.yml` | PR touching supabase/migrations/** | Posts PR comment warning if handle_new_user trigger function is modified (DEBT-002). Non-blocking. |
| E2E Tests (Playwright) | `e2e.yml` | PR/push to main (critical frontend/backend paths), manual | Standalone E2E Playwright tests on path-filtered files. Includes smoke test quality gate (GTM-QUAL-001 AC13). |
| Dependabot Auto-merge | `dependabot-auto-merge.yml` | PR to main from dependabot[bot] | Auto-merges patch/minor dependency updates; posts warning comment on major updates. |

## Notes

### Redundancy Analysis

**`backend-ci.yml` vs `backend-tests.yml`** — Overlapping. Both run on PR + push to main for backend changes, both run tests. `backend-tests.yml` is the authoritative gate (CRIT-038). `backend-ci.yml` additionally runs Trivy filesystem scan and pip-audit at the HIGH level. If runner minutes are a concern, consider merging Trivy into `backend-tests.yml` and disabling `backend-ci.yml`. For now, both run (additive, not contradictory).

**`tests.yml` E2E job vs `e2e.yml`** — The E2E job in `tests.yml` runs after unit tests pass (gated). `e2e.yml` runs standalone on path-triggered files. They serve different purposes: `tests.yml` ensures E2E only runs when unit tests are green; `e2e.yml` runs targeted E2E on critical file changes.

**`staging-deploy.yml` vs `deploy.yml`** — Staging environment is not provisioned. The staging workflow will fail silently if triggered (missing secrets). It has been scoped to develop/feature branches to avoid triggering on main PRs.

### PR Gate Identification

- **Backend PRs:** `backend-tests.yml` ("Backend Tests (PR Gate)") is the required check
- **Frontend PRs:** `frontend-tests.yml` ("Frontend Tests (PR Gate)") is the required check
- Both require 0 failures (CRIT-038 zero-failure policy)

### Recommendations

1. **Disable `backend-ci.yml`** if you want to reduce runner usage — its unique value (Trivy CRITICAL scan) could be merged into `backend-tests.yml`'s security scan step.
2. **Provision or remove staging** — `staging-deploy.yml` should either have its secrets configured or be fully disabled (renamed to `.yml.disabled`) to avoid confusion.
3. **Branch naming:** `cleanup.yml` now correctly targets `origin/main` (was `origin/master` — bug fixed in DEBT-CI-001).
4. **`codeql.yml`** uses `@v4` action and `@master` for TruffleHog — pin these to specific versions for supply chain security.
5. **`lighthouse.yml` PyYAML parse note:** PyYAML's scanner trips on `|` pipe characters in Markdown tables embedded in the JS template literal inside the `script:` block. This is a pre-existing quirk — GitHub Actions' own YAML parser handles it correctly. The file is valid for GitHub Actions; only PyYAML's stricter scanner rejects it.
