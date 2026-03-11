# QA Review -- GTM Readiness Assessment

**Date:** 2026-03-10 | **Agent:** @qa (Quinn) | **Gate Status:** APPROVED WITH CONDITIONS

---

## Review Summary

The GTM Readiness Assessment (technical-debt-DRAFT.md) is a well-structured document that consolidates findings from three specialist phases (architecture, database, frontend). The assessment correctly identifies the most critical risks and provides actionable remediation paths with effort estimates. The scoring methodology is transparent and the weighted formula is sound.

However, this review identified **one significant factual error** in the P0 classification, **one CI configuration gap worse than reported**, and **several cross-domain risks** that were underweighted. The assessment is fundamentally sound and can proceed to final review after addressing the conditions listed below.

---

## Assessment Completeness

| Area | Covered? | Quality | Gaps |
|------|----------|---------|------|
| System Architecture | Yes | Good | Comprehensive module-level analysis. Timeout chain documented. Missing: no mention of `faulthandler.enable()` startup or Railway restart behavior. |
| Database | Yes | Good | Thorough RLS audit of all 32 tables. **Critical gap: migration 027 already fixes P0-001/P0-002 but DB-AUDIT does not reference it (see Critical Gap CG-001).** |
| Frontend/UX | Yes | Good | 47 pages inventoried, 4 user journeys analyzed, component health assessed. Conversion optimization opportunities well-identified. |
| Security | Yes | Good | JWT ES256+JWKS, RLS, Stripe signature verification, CORS, log sanitization, rate limiting all covered. Missing: no OWASP Top 10 mapping. |
| Performance | Partial | Fair | Estimated baselines provided but no load test data. No p50/p95/p99 measurements. Cache hit ratios not measured. |
| Billing/Payments | Yes | Good | Stripe webhook chain well-documented. 8 event types, idempotency, signature verification, 3-day grace period all covered. |
| Auth/AuthZ | Yes | Good | Two-layer defense (RLS + backend middleware) correctly analyzed. Auth cache, MFA, OAuth all covered. |
| Observability | Yes | Good | 50+ Prometheus metrics, Sentry, OpenTelemetry, structured logging documented. Missing: no alerting rules inventory. |
| E2E Test Infrastructure | Partial | Fair | **E2E workflow uses Python 3.11 but project requires Python 3.12 (see Gap MG-001).** |
| API Contract Testing | Yes | Good | OpenAPI schema snapshot validation in CI is a strong pattern. |

---

## Gaps Identified

### Critical Gaps (must address before final assessment)

#### CG-001: P0-001/P0-002 May Already Be Fixed -- Assessment Contradicts Migration History

**Finding:** The DRAFT classifies `pipeline_items` and `search_results_cache` RLS policies as P0 GTM blockers. However, migration `027_fix_plan_type_default_and_rls.sql` **already contains the exact fix** -- it drops the overly permissive policies and recreates them with `TO service_role`.

**Evidence:**
- Migration 027, lines 58-67: `DROP POLICY IF EXISTS "Service role full access on pipeline_items"` followed by `CREATE POLICY ... TO service_role USING (true) WITH CHECK (true);`
- Migration 027, lines 76-84: Same pattern for `search_results_cache`
- Test file `test_td001_rls_security.py` validates this migration's SQL structure (4 tests, all pass)

**The DB-AUDIT (Phase 2) identifies the vulnerability in migration 025/026 but does not reference migration 027 which fixes it.** The DB-AUDIT mentions `027b` (search cache columns) but not `027` (RLS fix). This is a factual oversight.

**However,** the question remains: **was migration 027 applied in production?** The deploy workflow auto-applies via `supabase db push --include-all`, so it should be applied. But the assessment should verify production state, not just migration file content.

**Required action:** Before finalizing the assessment:
1. Run the verification query from migration 027 in production:
   ```sql
   SELECT policyname, roles, cmd, qual
   FROM pg_policies
   WHERE tablename IN ('pipeline_items', 'search_results_cache')
   ORDER BY tablename, policyname;
   ```
2. If `roles` includes `{service_role}` for the "Service role full access" policies, P0-001/P0-002 are **already resolved** and should be reclassified to "Verified Fixed."
3. If `roles` is `{0}` (all roles), migration 027 was not applied and the P0 classification stands.

**Impact on assessment:** If both P0s are already fixed, the overall score should increase from 7.5 to ~8.0, and the "no hard blockers" statement in the executive summary is already correct without caveats.

---

#### CG-002: `continue-on-error: true` Problem Is Broader Than Reported

**Finding:** P1-001 flags `pip-audit` as non-blocking in `backend-tests.yml`. The actual scope is much larger:

| Workflow | Steps with `continue-on-error: true` | Risk |
|----------|---------------------------------------|------|
| `backend-tests.yml` | pip-audit, ruff, mypy (3 steps) | Reported in assessment |
| `frontend-tests.yml` | npm audit (1 step) | **NOT reported** -- frontend CVEs also non-blocking |
| `pr-validation.yml` | 8 steps with continue-on-error | **NOT reported** -- PR validation is almost entirely advisory |
| `staging-deploy.yml` | Tests AND coverage (2 steps) | **NOT reported** -- staging deploys skip test failures entirely |
| `deploy.yml` | 2 steps | Partially noted |
| `tests.yml` | 5 steps | **NOT reported** -- duplicate/legacy workflow? |
| `codeql.yml` | 1 step | Not reported |
| `load-test.yml` | 2 steps | Not reported |

Total: **25 instances** of `continue-on-error: true` across 8 workflows. The assessment only flags 3 in one workflow.

**Required action:** P1-001 should be expanded to cover all security-relevant `continue-on-error` usage, particularly:
- `frontend-tests.yml` npm audit (same risk class as pip-audit)
- `staging-deploy.yml` skipping test failures (defeats the purpose of staging)
- `pr-validation.yml` having 8 non-blocking steps (makes PR validation almost decorative)

---

### Minor Gaps (note but proceed)

#### MG-001: E2E Workflow Uses Python 3.11, Project Requires 3.12

The `e2e.yml` workflow specifies `python-version: '3.11'` while the backend requires Python 3.12 (`pyproject.toml: requires-python = ">=3.12"` and `backend-tests.yml` uses 3.12). This means E2E tests run against a different Python version than CI unit tests and production.

**Risk:** LOW -- the E2E tests exercise the frontend browser flows and the backend is started via uvicorn which is unlikely to have 3.11/3.12 behavioral differences. But it should be fixed for consistency.

#### MG-002: No Alerting Rules Inventory

The assessment documents 50+ Prometheus metrics but does not inventory which metrics have alerting rules, thresholds, or notification channels configured. For GTM, the question is not "do we collect metrics?" but "will we be notified before customers notice?"

#### MG-003: search_state_manager Does Not Write 'consolidating' or 'partial' to DB

P1-007 flags a potential CHECK constraint mismatch between `search_sessions.status` and the state manager. Grep analysis of `search_state_manager.py` shows **zero occurrences** of 'consolidating' or 'partial'. These terms appear in `pipeline/stages/execute.py` as `ctx.is_partial` (a boolean on the context object), not as a DB status value. This suggests P1-007 may be a non-issue.

**Required action:** Verify by reading the state manager's `_transition()` method to confirm it only writes CHECK-allowed values. If confirmed, downgrade P1-007 to "Verified Non-Issue."

#### MG-004: No Security Assessment of Debug Endpoint

P3-002 flags `/debug/pncp-test` as low priority. For a paid B2G product, any debug endpoint in production should be evaluated more carefully, even if admin-gated. The assessment does not analyze what data this endpoint exposes or whether the admin gate is sufficient.

#### MG-005: Backup Recovery Never Tested

P2-012 notes Supabase PITR is enabled but untested. For a product handling procurement intelligence data for paying customers, "we have backups but never tested restore" is arguably P1, not P2. A failed restore during an incident would be catastrophic for customer trust.

---

## Cross-Domain Risks

| Risk | Systems Affected | Probability | Impact | Mitigation |
|------|-----------------|-------------|--------|------------|
| RLS fix not applied in production (CG-001) | DB + Backend + Frontend | MEDIUM | CRITICAL | Verify via pg_policies query. Deploy pipeline auto-applies, but 027's alphabetical sort position between 026 and 027b could cause issues. |
| Stripe webhook replay after schema migration | DB + Billing | LOW | HIGH | stripe_webhook_events has idempotency check (evt_ prefix). But if the events table is migrated mid-webhook-delivery, duplicate processing could occur. Stripe signature verification + idempotency key provide double protection. |
| Auth token cache invalidation on deploy | Backend + Frontend | MEDIUM | LOW | Per-worker L1 cache is lost on deploy. L2 Redis compensates. 75s Gunicorn keep-alive prevents connection reset during rolling deploy. Documented in assessment. |
| Frontend plan cache (localStorage 1hr) vs backend quota enforcement | Frontend + Backend + DB | LOW | MEDIUM | If Stripe downgrades a plan but localStorage cache shows old plan, user sees stale plan for up to 1 hour. The backend quota check is the real enforcement, so this is cosmetic. |
| E2E tests on Python 3.11 miss 3.12-specific issues | CI + Backend | LOW | LOW | Fix Python version in e2e.yml. |
| ComprasGov outage + PNCP rate limiting = degraded coverage | Backend + External APIs | MEDIUM | MEDIUM | With ComprasGov offline, only PNCP and PCP active. If PNCP rate-limits during peak, effective coverage drops to PCP-only. Circuit breakers handle this gracefully but customers see fewer results. |
| Migration 027b sort order ambiguity | DB | LOW | HIGH | `027b_*` sorts after `027_*` alphabetically, so this is correct. But adding future `027c_*` etc. creates fragile ordering. Timestamp-based naming eliminates this risk. |

---

## Test Coverage Analysis for GTM

### P0 Items Test Status

| P0 ID | Finding | Has Tests? | Test Quality | Needs |
|-------|---------|------------|--------------|-------|
| P0-001 | pipeline_items RLS cross-user access | YES | GOOD | `test_td001_rls_security.py` validates migration 027 SQL structure. 4 tests verify DROP+CREATE with TO service_role. **Missing: production verification query.** |
| P0-002 | search_results_cache RLS cross-user access | YES | GOOD | Same test file, 2 tests for search_results_cache section. **Missing: production verification query.** |

**Assessment:** If migration 027 was applied (likely, given auto-deploy), both P0s have been fixed AND tested. The tests are static SQL analysis, not live DB integration tests. A production verification query is the definitive confirmation.

### P1 Items Test Status

| P1 ID | Finding | Has Tests? | Test Quality | Needs |
|-------|---------|------------|--------------|-------|
| P1-001 | CI vulnerability scan non-blocking | N/A | N/A | This is a CI config issue, not a code issue. Fix is removing `continue-on-error: true`. No test needed beyond CI pipeline itself. |
| P1-002 | 5 tables FK to auth.users | YES | FAIR | `test_debt104_fk_standardization.py` exists. But the 5 affected tables (trial_email_log, mfa_recovery_codes, mfa_recovery_attempts, organization_members, organizations.owner_id) were created after FK standardization and may not be covered. Need to verify test scope. |
| P1-003 | search_results_store FK NOT VALID | NO | N/A | No automated test. Requires production SQL query. |
| P1-004 | No graceful shutdown | YES | FAIR | `test_harden_022_graceful_shutdown.py` exists but the feature may not be fully implemented. Need to verify test content. |
| P1-005 | Landing page no product screenshot | N/A | N/A | UX issue, not testable via unit tests. E2E `landing-page.spec.ts` exists but likely does not assert image presence. |
| P1-006 | Landing page missing testimonials | N/A | N/A | UX issue. Quick fix (import existing component). |
| P1-007 | search_sessions.status CHECK mismatch | LIKELY NON-ISSUE | N/A | Grep shows state manager does not write 'consolidating'/'partial' to DB. `test_search_sessions.py` and `test_search_state.py` exist. Verify state manager maps to allowed values. |
| P1-008 | ComprasGov offline, no communication | N/A | N/A | Product/UX issue. |
| P1-009 | Single-instance scaling ceiling | NO | N/A | `load-test.yml` workflow exists but no documented results. No capacity test assertions. |
| P1-010 | Missing retention on 4 tables | PARTIAL | FAIR | `test_debt009_database_rls_retention.py` tests some retention. Need to verify it covers health_checks, mfa_recovery_attempts, stripe_webhook_events, search_state_transitions. |
| P1-011 | Dashboard lacks insights | N/A | N/A | UX/feature issue. |

### Key Billing Chain Test Coverage

| Component | Test Files | Coverage Quality |
|-----------|-----------|-----------------|
| Stripe webhooks | `test_stripe_webhook.py`, `test_payment_failed_webhook.py`, `test_webhook_rls_security.py`, `test_harden028_stripe_events_purge.py` | GOOD -- 4 test files covering webhook processing, payment failures, RLS, and event cleanup |
| Billing routes | `test_routes_subscriptions.py`, `test_billing_period_update.py`, `test_debt114_billing_legacy_cleanup.py` | GOOD -- subscription CRUD, period updates, legacy plan handling |
| Quota enforcement | `test_quota.py`, `test_quota_race_condition.py`, `test_revalidation_quota_cache.py` | GOOD -- atomic check+increment, race conditions, cache interaction |
| Pricing consistency | `test_story360_pricing_consistency.py` | GOOD -- plan/price alignment |
| Boleto/PIX | `test_story280_boleto_pix.py` | GOOD -- alternative payment methods |
| Reconciliation | `test_stripe_reconciliation.py`, `test_concurrency_safety.py` | GOOD |

**Billing verdict:** The billing chain has strong test coverage across webhook processing, quota enforcement, reconciliation, and edge cases. This is one of the best-tested areas of the codebase.

### Key Auth Chain Test Coverage

| Component | Test Files | Coverage Quality |
|-----------|-----------|-----------------|
| JWT validation | `test_auth.py`, `test_auth_es256.py`, `test_auth_cache.py` | EXCELLENT -- ES256+JWKS, caching, expiration |
| Authorization | `test_authorization.py`, `test_auth_401.py`, `test_auth_check.py` | GOOD |
| OAuth | `test_oauth.py`, `test_oauth_story224.py`, `test_routes_auth_oauth.py` | GOOD |
| Email auth | `test_auth_email.py` | GOOD |
| Auth cache | `test_debt014_auth_cache.py` | GOOD |

**Auth verdict:** Strong coverage. The auth chain is well-tested from JWT validation through to route-level authorization.

---

## Acceptance Criteria for Fixes

### P0-001 + P0-002: RLS Policy Fix (if not already applied)

- [x] Test: `test_td001_rls_security.py` -- 4 tests validate migration 027 SQL structure (ALREADY PASSING)
- [ ] Verification: Run `SELECT policyname, roles FROM pg_policies WHERE tablename IN ('pipeline_items', 'search_results_cache') AND policyname LIKE '%service%';` in production. Roles must show `{service_role}`, NOT `{0}`.
- [ ] Verification: As an authenticated non-admin user, `SELECT count(*) FROM pipeline_items` must return ONLY own items, not all items.
- [ ] Regression: All pipeline CRUD tests (`test_pipeline.py`, `test_pipeline_coverage.py`, `test_pipeline_resilience.py`) must continue passing.

### P1-001: Make CI Vulnerability Scans Blocking

- [ ] Test: CI workflow must fail (non-zero exit) when pip-audit finds HIGH+ vulnerability.
- [ ] Verification: Temporarily introduce a known-vulnerable package and confirm the workflow blocks.
- [ ] Scope expansion: Also remove `continue-on-error` from `frontend-tests.yml` npm audit.
- [ ] Regression: Ensure no false positives block legitimate PRs. Use `--ignore-vuln` for known accepted risks.

### P1-002: FK Standardization (5 tables)

- [ ] Test: Migration creates FKs to `profiles(id)` with ON DELETE CASCADE (or RESTRICT for organizations.owner_id).
- [ ] Verification: `SELECT conname, confrelid::regclass FROM pg_constraint WHERE conrelid IN ('trial_email_log'::regclass, 'mfa_recovery_codes'::regclass, 'mfa_recovery_attempts'::regclass, 'organization_members'::regclass, 'organizations'::regclass) AND contype = 'f';` must show `profiles` as target.
- [ ] Test: Delete a test user from profiles and verify CASCADE propagation to all 5 tables.
- [ ] Regression: `test_lgpd.py` must continue passing. Add cascade verification test.

### P1-004: Graceful Shutdown

- [ ] Test: `test_harden_022_graceful_shutdown.py` must verify SIGTERM triggers drain behavior.
- [ ] Test: Add test that in-flight search completes after SIGTERM before process exit.
- [ ] Verification: Deploy to staging, start a search, trigger redeploy, verify search completes or returns partial results (not error).
- [ ] Regression: No impact on normal startup/shutdown cycle.

### P1-007: search_sessions.status CHECK (likely non-issue)

- [ ] Verification: Confirm `search_state_manager.py` `_transition()` method only writes values in `('created', 'processing', 'completed', 'failed', 'timed_out', 'cancelled')`.
- [ ] If confirmed: Close as non-issue. Remove from P1 list.
- [ ] If state manager writes 'consolidating'/'partial': Add those values to CHECK constraint via migration.

### P1-010: Missing Retention Policies

- [ ] Test: Verify pg_cron jobs exist for health_checks (30d), mfa_recovery_attempts (90d), stripe_webhook_events (90d), search_state_transitions (12mo).
- [ ] Verification: After cron jobs run, tables should not contain rows older than their retention period.
- [ ] Regression: Ensure cron jobs do not interfere with active operations (e.g., do not delete in-flight search state transitions).

---

## CI/CD Pipeline Assessment

### Strengths
- **17 GitHub Actions workflows** -- comprehensive coverage of tests, deployment, migrations, security, E2E
- **Three-layer migration defense** -- PR warning, push alert, auto-apply on deploy. This is excellent.
- **OpenAPI schema snapshot validation** -- prevents accidental API contract drift. Strong pattern.
- **Backend zero-failure gate** -- tests must pass with 0 failures for merge.
- **Per-module coverage thresholds** -- `check_module_coverage.py` prevents coverage regression.
- **Bundle size budget** -- `size-limit` in frontend CI prevents JS bloat.
- **TypeScript check blocking** -- `tsc --noEmit` in frontend CI prevents type errors from shipping.

### Weaknesses
- **25 instances of `continue-on-error: true`** across 8 workflows -- security scans, linting, type checking, and even staging tests are all advisory. This creates a false sense of CI rigor.
- **E2E Python version mismatch** -- 3.11 vs 3.12. Should match production.
- **No staging environment verification** -- `staging-deploy.yml` exists but skips test failures (continue-on-error on tests AND coverage).
- **Load test workflow unclear execution** -- `load-test.yml` exists but no evidence of regular execution or baseline documentation.
- **Duplicate/legacy workflows** -- Both `backend-tests.yml` and `tests.yml` exist. The relationship between them is unclear.

### Pipeline Readiness Verdict

The pipeline is **adequate for safe, fast P0/P1 fixes**. The test gates are strict (zero failures), coverage thresholds are enforced, and API contract drift is detected. The main risk is that security scans are non-blocking, meaning a fix for one issue could inadvertently introduce a vulnerable dependency without detection.

**Recommendation:** Fix P1-001 (make pip-audit/npm audit blocking) BEFORE deploying other fixes to ensure the fix pipeline itself is secure.

---

## Regression Risk

### When fixing P0-001/P0-002 (RLS):
- **LOW risk** if migration 027 already applied (no change needed).
- If new migration needed: Risk is that dropping and recreating policies could cause a brief window where the policy does not exist. Use a single transaction (`BEGIN;...COMMIT;`) to make the swap atomic. Test that pipeline CRUD still works after the fix.

### When fixing P1-001 (CI gates):
- **MEDIUM risk** -- making pip-audit blocking may immediately fail CI if any current dependency has a known vulnerability. Run `pip-audit -r requirements.txt` locally first and address any findings before removing `continue-on-error`.

### When fixing P1-002 (FK standardization):
- **MEDIUM risk** -- changing FK targets from `auth.users(id)` to `profiles(id)` requires that all affected rows have matching `profiles` entries. If any orphan rows exist (user deleted from profiles but not from these tables), the FK creation will fail. Run a pre-check query: `SELECT count(*) FROM trial_email_log t LEFT JOIN profiles p ON t.user_id = p.id WHERE p.id IS NULL;`

### When fixing P1-004 (graceful shutdown):
- **LOW risk** -- additive change (adding SIGTERM handler). Does not modify existing request handling. Main risk is the drain timeout being too long and delaying deploys.

---

## Recommendations

1. **Verify P0-001/P0-002 production state immediately.** Run the pg_policies query in production. This single query determines whether the assessment's top-priority blockers are already resolved. If migration 027 was applied, reclassify both P0s as "Verified Fixed" and adjust the overall score to 8.0.

2. **Expand P1-001 scope to all security-relevant `continue-on-error` usage.** The problem is 25 instances across 8 workflows, not 3 in one workflow. Prioritize: pip-audit (backend), npm audit (frontend), staging-deploy test skip. Leave linting/type-check as advisory for now but with a 30-day deadline to fix violations and make them blocking.

3. **Verify P1-007 is a non-issue.** Grep evidence strongly suggests the state manager does not write 'consolidating'/'partial' to the database. A 10-minute code review of `_transition()` in `search_state_manager.py` can close this item.

4. **Fix E2E Python version (MG-001).** Change `python-version: '3.11'` to `'3.12'` in `.github/workflows/e2e.yml`. One-line fix.

5. **Consider upgrading P2-012 (backup recovery) to P1.** For a paid product, untested backups are a significant operational risk. A 4-hour exercise to test Supabase PITR restore to a scratch project would provide confidence that is currently assumed but not verified.

6. **Add production verification queries to the assessment.** The DRAFT provides remediation SQL but the definitive production state checks should be listed as "Day 0" tasks before any fix work begins.

7. **Document alerting rules.** The assessment covers metrics collection but not alerting. Before GTM, confirm that at least these metrics have alerts: `smartlic_supabase_cb_state` (circuit breaker open), `smartlic_sse_connection_errors_total` (SSE failures), response latency p99 > 10s, error rate > 5%.

---

## Quality Gate Decision

**Status:** APPROVED WITH CONDITIONS

**Conditions:**

1. **MUST verify P0-001/P0-002 production state** before finalizing the DRAFT. If migration 027 is applied, reclassify as "Verified Fixed." If not applied, the P0 classification stands and the fix migration must be deployed immediately.

2. **MUST expand P1-001 scope** in the DRAFT to reflect the true extent of `continue-on-error` usage (25 instances across 8 workflows, not 3 in 1 workflow).

3. **SHOULD verify P1-007** via code review of `search_state_manager.py` to either confirm non-issue or confirm the CHECK constraint needs updating.

4. **SHOULD fix E2E Python version** mismatch (3.11 -> 3.12) before the assessment is finalized, as it undermines E2E test validity.

**Rationale:**

The assessment is thorough, well-structured, and identifies the right priority areas. The scoring methodology is transparent and the weighted formula produces a defensible result. The sprint planning suggestions are realistic with appropriate effort estimates.

The two conditions that must be met before final assessment are:
- CG-001 (P0 production state) could change the assessment's headline message from "fix 2 RLS policies before launch" to "already fixed, proceed to launch." This is a material difference for sprint planning.
- CG-002 (CI scope) is a factual accuracy issue. The assessment should reflect the true extent of the problem to ensure the fix addresses all security-relevant workflows, not just one.

The remaining conditions (P1-007 verification, E2E Python version) are lower risk and can be addressed during the first sprint without blocking the assessment's finalization.

**Overall assessment quality: 8/10.** Solid analysis with clear actionable findings. The main issue is the migration 027 oversight in the DB-AUDIT, which propagated into the DRAFT's P0 classification. This type of cross-phase information gap is expected in multi-agent assessments and is exactly what the QA review phase is designed to catch.
