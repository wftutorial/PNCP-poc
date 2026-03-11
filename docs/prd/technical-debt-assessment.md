# GTM Readiness Assessment — FINAL

**Project:** SmartLic | **Date:** 2026-03-10 | **Version:** 1.0
**Reviewed by:** @architect (Atlas), @data-engineer (Delta), @ux-design-expert (Uma), @qa (Quinn)
**Pricing target:** SmartLic Pro R$397/mo, Consultoria R$997/mo

---

## Executive Summary

SmartLic is architecturally ready for paying customers. The system handles failures gracefully with circuit breakers, two-level SWR cache, and SSE heartbeat resilience. Billing is well-integrated with Stripe (8 webhook event types, idempotency, signature verification, 3-day grace period). Auth is production-grade (JWT ES256+JWKS, RLS on all 32 tables). The frontend provides a polished search-to-pipeline experience with comprehensive error handling, retry logic, and graceful degradation.

The two RLS security vulnerabilities originally flagged as P0 blockers (cross-user access on `pipeline_items` and `search_results_cache`) were **already fixed in migration 027** (dated 2026-02-15). The migration drops the overly permissive policies and recreates them with `TO service_role`. Test coverage exists in `test_td001_rls_security.py` (7 tests validating migration SQL structure). However, **production state must be verified** via a `pg_policies` query to confirm migration 027 was applied successfully. If confirmed, there are zero P0 blockers.

**Recommendation:** Verify the two RLS fixes in production (10-minute task). If confirmed, proceed to launch with confidence. The remaining work is conversion optimization (product screenshot, testimonials, annual pricing default) and CI hardening (25 instances of `continue-on-error: true` across 8 workflows). All P1 items are achievable within 2 weeks.

---

## Overall GTM Readiness Score: 8.0 / 10 — GREEN: Proceed to Launch

| Dimension | Weight | Score | Status | Key Issue |
|-----------|--------|-------|--------|-----------|
| Security | 30% | 9.0/10 | GREEN | RLS fixed (migration 027). Verify in production. |
| Reliability | 25% | 8.0/10 | GREEN | Circuit breakers, SWR cache, SSE heartbeat. No graceful shutdown on deploy. |
| Conversion/UX | 20% | 7.0/10 | YELLOW-GREEN | No product screenshot on landing page. Testimonials component exists but not imported. |
| Scalability | 15% | 6.5/10 | YELLOW | Single-instance ceiling (~30 concurrent users). Per-worker L1 cache. |
| Observability | 10% | 8.0/10 | GREEN | 50+ Prometheus metrics, Sentry, OpenTelemetry, structured logging. Missing alerting rules inventory. |

**Weighted score:** (9.0 x 0.30) + (8.0 x 0.25) + (7.0 x 0.20) + (6.5 x 0.15) + (8.0 x 0.10) = **8.08 ~ 8.0/10**

*Score increased from DRAFT 7.5 to 8.0 because the DB specialist confirmed P1-002 (FK standardization), P1-007 (CHECK constraint), and P1-010 (retention jobs) were all already resolved, and the QA review identified that the P0 RLS fixes exist in migration 027.*

---

## P0 — GTM BLOCKERS

**None confirmed.** Migration 027 (`027_fix_plan_type_default_and_rls.sql`) contains the exact fixes for both original P0 items. Requires production verification.

### P0-VERIFY: Confirm Migration 027 Applied in Production

**Status:** VERIFY IN PRODUCTION (not a code blocker — a verification task)

**What:** Migration 027 fixes both RLS policy gaps (`pipeline_items` and `search_results_cache`) by adding `TO service_role` to the permissive policies. The deploy pipeline auto-applies migrations via `supabase db push --include-all`. If this migration ran successfully, both P0 issues are resolved.

**Verification query (run in Supabase SQL Editor):**
```sql
SELECT tablename, policyname, roles, cmd
FROM pg_policies
WHERE tablename IN ('pipeline_items', 'search_results_cache')
  AND policyname LIKE '%service%'
ORDER BY tablename, policyname;
```

**Expected result if fixed:** `roles` column shows `{service_role}` (not `{0}` which means all roles).

**Negative test (run as authenticated non-admin user via Supabase client):**
```sql
SELECT count(*) FROM pipeline_items;
-- Must return ONLY own items (0 for a user with no pipeline items)
```

**If NOT applied:** Deploy migration 027 immediately. It is a tested, idempotent migration. Then re-verify.

**Test coverage:** `backend/tests/test_td001_rls_security.py` — 7 tests validate migration SQL structure (DROP + CREATE with TO service_role, idempotency patterns).

**Owner:** @devops | **Effort:** 10 minutes | **Deadline:** Before first paying customer

---

## P1 — HIGH PRIORITY (First 30 Days)

| ID | Finding | Domain | Effort | Owner | Specialist Notes |
|----|---------|--------|--------|-------|------------------|
| P1-001 | CI vulnerability scans non-blocking (25 instances across 8 workflows) | CI/CD | M (4-8h) | @devops | QA expanded scope: not 3 in 1 workflow but 25 across 8. Prioritize pip-audit + npm audit + staging tests. |
| P1-004 | No graceful shutdown for in-flight searches | Backend | M (4h) | @dev | Every deploy causes ~30s of search failures. SIGTERM handler with drain period needed. |
| P1-005 | Landing page has no product screenshot/video | Frontend | M (6h) | @ux + @dev | UX: single highest-ROI conversion improvement (+15-25% signup rate). Static annotated screenshot, not video. Week 1 Day 3-4. |
| P1-006 | Landing page missing testimonials section | Frontend | S (1h) | @dev | `TestimonialSection` component exists and is used on `/planos`. Single import + JSX line on landing page. |
| P1-008 | ComprasGov v3 offline — no customer communication | UX/PM | S (2h) | @pm | "2/3 fontes ativas" badge in search results header. |
| P1-009 | Single-instance scaling ceiling (~30 concurrent users) | Infra | L (8-16h) | @devops | Investigation + Redis SSE validation. Deferred to Week 2-3. |
| P1-011 | Dashboard lacks actionable insights | Frontend | M (8h) | @dev | Pipeline deadline alerts + "new opportunities since last search." Retention lever. |
| P1-012 | Annual plan not defaulted on pricing page | Frontend | S (15min) | @dev | Change `useState("monthly")` to `useState("annual")` in `/planos/page.tsx` line 92. +3-8% checkout conversion. |
| P1-013 | No WhatsApp/contact CTA on pricing page | Frontend | S (2h) | @dev | B2G buyers need human contact before R$397-997/mo commitment. Inline contact row below FAQ, not floating bubble. |

### P1 Detail

#### P1-001: CI Gates Advisory-Only (Expanded Scope)

**What:** 25 instances of `continue-on-error: true` across 8 GitHub Actions workflows. Security scans (pip-audit, npm audit), linting (ruff), type checking (mypy), and even staging tests are all non-blocking. A HIGH severity CVE could ship to production undetected.

**Full inventory:**

| Workflow | Count | Steps | Security-Relevant |
|----------|-------|-------|-------------------|
| `backend-tests.yml` | 3 | pip-audit, ruff, mypy | YES (pip-audit) |
| `frontend-tests.yml` | 1 | npm audit | YES |
| `pr-validation.yml` | 8 | Multiple validation steps | YES (makes PR validation decorative) |
| `staging-deploy.yml` | 2 | Tests + coverage (marked "TEMP") | YES (defeats staging purpose) |
| `tests.yml` | 5 | Multiple steps (legacy/duplicate?) | Unclear — relationship to `backend-tests.yml` unknown |
| `deploy.yml` | 2 | Post-deploy checks | MEDIUM |
| `backend-ci.yml` | 1 | 1 step | LOW |
| `codeql.yml` | 1 | CodeQL analysis | YES |
| `load-test.yml` | 2 | Test execution | LOW |

**Prioritized fix plan:**
1. **Day 1:** Remove `continue-on-error` from `pip-audit` (backend-tests.yml) and `npm audit` (frontend-tests.yml). Run audits locally first to clear existing findings.
2. **Day 2:** Remove `continue-on-error` from `staging-deploy.yml` test steps (marked "TEMP" for STORY-165 — that story shipped months ago).
3. **Week 2:** Audit `pr-validation.yml` — decide which of the 8 steps should be blocking. Make at least security-relevant steps blocking.
4. **Week 3:** Clarify `tests.yml` vs `backend-tests.yml` relationship. Remove duplicate if confirmed.

**Acceptance criteria:**
- pip-audit and npm audit run blocking in CI. `--ignore-vuln` used for accepted known risks.
- staging-deploy runs tests blocking (TEMP markers removed).
- No false positives block legitimate PRs (verify by running audits locally before enabling).

**Files:** `.github/workflows/backend-tests.yml`, `frontend-tests.yml`, `staging-deploy.yml`, `pr-validation.yml`

---

#### P1-004: No Graceful Shutdown

Railway deploys send SIGTERM but the app does not drain in-flight requests. Active searches fail mid-progress during deploys.

**Fix:** Implement SIGTERM handler with configurable drain period (30s). Use Gunicorn `on_exit` hook or FastAPI lifespan events to await in-flight search completion.

**Acceptance criteria:**
- SIGTERM triggers drain behavior (new requests rejected with 503, in-flight requests complete).
- In-flight search either completes or returns partial results (not an error).
- Drain timeout is configurable via env var (default 30s).
- `test_harden_022_graceful_shutdown.py` validates behavior.

**Files:** `backend/main.py`, `backend/start.sh` (Gunicorn config)

---

#### P1-005: Landing Page Product Screenshot

The landing page has 6 sections (Hero, OpportunityCost, BeforeAfter, HowItWorks, Stats, CTA) but zero product visuals. B2G buyers are risk-averse and need to see what they are buying before creating an account.

**Design (from UX specialist):**
- Static annotated screenshot of `/buscar` results page (1280x800, cropped to filter panel + 3-4 result cards)
- 3 callout annotations: "Classificacao por IA", "Viabilidade 4 fatores", "Pipeline integrado"
- Desktop: right side of hero. Mobile: below headline, full-width.
- Use `next/image` with `priority={true}` for LCP.
- Dark mode: separate screenshot or CSS `filter` for automatic darkening.

**Acceptance criteria:**
- Hero section shows annotated product screenshot on desktop (50/50 layout) and mobile (stacked).
- Image uses `next/image` with `priority` and descriptive Portuguese `alt` text.
- Page still loads in <3s on 3G throttle.

**Files:** `frontend/app/(landing)/HeroSection.tsx`, `frontend/public/` (screenshot asset)

---

#### P1-012: Default Pricing to Annual Billing

Currently shows R$397/mo (monthly) first. Changing default to annual shows R$297/mo — a 25% lower anchor price.

**Fix:** `useState<BillingPeriod>("monthly")` to `useState<BillingPeriod>("annual")` in `/planos/page.tsx` line 92. Also verify `?billing=monthly` URL override still works for monthly-specific links.

**Acceptance criteria:**
- `/planos` loads with annual billing selected by default.
- `?billing=monthly` and `?billing=semiannual` URL params override the default.
- Existing tests pass.

**File:** `frontend/app/planos/page.tsx`

---

#### P1-013: WhatsApp/Contact CTA on Pricing Page

B2G buyers with budget authority often need to speak with a human before committing company money. The pricing page has zero direct contact options.

**Design (from UX specialist):** Inline contact row between FAQ and bottom CTA link (NOT a floating bubble — too casual for B2G price point).

```
[FAQ accordion]
--- divider ---
"Precisa de mais informacoes?"
[WhatsApp icon] Fale conosco   [Email icon] contato@smartlic.tech
--- divider ---
```

**Acceptance criteria:**
- Contact row visible below FAQ section on `/planos`.
- WhatsApp number from env var (not hardcoded).
- Mobile-responsive layout.

**File:** `frontend/app/planos/page.tsx`

---

## P2 — MEDIUM (90 Days)

| ID | Finding | Domain | Effort | Owner |
|----|---------|--------|--------|-------|
| P2-001 | Feature flag explosion (50+ flags, no admin UI) | Backend | L (8h) | @dev |
| P2-002 | 90 migrations, mixed naming conventions | DB | M (4h) | @data-engineer |
| P2-003 | No load testing baseline | Infra | L (8h) | @devops |
| P2-004 | OpenAI single point of failure for classification | Backend | M (4h) | @dev |
| P2-005 | Minimal next/image usage (7 files) | Frontend | M (4h) | @dev |
| P2-006 | No bundle analyzer configured | Frontend | S (2h) | @dev |
| P2-007 | Prop drilling in SearchResults (40+ props) | Frontend | M (8h) | @dev |
| P2-008 | Missing updated_at on search_results_store | DB | S (2h) | @data-engineer |
| P2-009 | search_results_cache cleanup trigger fires per-insert | DB | S (2h) | @data-engineer |
| P2-010 | ARQ worker liveness detection cached (15s) | Backend | S (2h) | @dev |
| P2-011 | No staging environment verified | Infra | L (16h) | @devops |
| P2-012 | Backup recovery process undocumented (PITR untested) | Infra | M (4h) | @devops |
| P2-013 | 4 analytics tools loading (LGPD consent surface) | Frontend | S (2h) | @dev |
| P2-014 | user_subscriptions lacks explicit service_role policy | DB | S (0.5h) | @data-engineer |
| P2-015 | grpcio transitive dep removal is fragile | Backend | S (2h) | @devops |
| P2-016 | Consultoria plan CTA uses raw `<button>` instead of `<Button>` | Frontend | S (0.5h) | @dev |
| P2-017 | FinalCTA on landing page has no urgency signal | Frontend | S (2h) | @dev |
| P2-018 | E2E workflow uses Python 3.11 instead of 3.12 | CI | S (5min) | @devops |
| P2-019 | No alerting rules inventory for Prometheus metrics | Observability | M (4h) | @devops |

### P2 Notes

**P2-008 (updated_at):** DB specialist confirmed most tables are append-only. Only `search_results_store` benefits from `updated_at` (has `expires_at` updates). Other tables listed in the DRAFT are non-issues.

**P2-009 (cleanup trigger):** Mitigated by DEBT-017 short-circuit optimization (`IF entry_count <= 5 THEN RETURN NEW`). Bottleneck unlikely before 100K users.

**P2-012 (backup recovery):** QA recommends upgrading to P1. For a paid product, untested backups are a significant operational risk. A 4-hour PITR restore test to a scratch project would verify the assumption that backups work.

**P2-014 (user_subscriptions):** Upgraded from P3 by DB specialist. Currently works because Supabase service_role bypasses RLS by default, but this is implicit behavior. If someone enables `ALTER ROLE service_role SET row_security TO on`, all billing operations break silently. 4-line defensive fix.

**P2-018 (E2E Python):** One-line fix in `.github/workflows/e2e.yml`. Change `python-version: '3.11'` to `'3.12'`.

---

## P3 — LOW (Backlog)

| ID | Finding | Domain | Effort |
|----|---------|--------|--------|
| P3-001 | mypy `disallow_untyped_defs = false` | Backend | M |
| P3-002 | Debug endpoint `/debug/pncp-test` in production | Backend | S |
| P3-003 | `health.py` uses `os.popen("python --version")` | Backend | S |
| P3-004 | Local file cache TTL disk accumulation untested at scale | Backend | S |
| P3-005 | Auth cache dual-hash transition window on every deploy | Backend | S |
| P3-006 | Inconsistent DB naming conventions (indexes, policies) | DB | S |
| P3-007 | google_sheets_exports GIN index possibly unused | DB | S |
| P3-008 | CSS variable + Tailwind class mixing | Frontend | M |
| P3-009 | Landing page sections tightly coupled (inline styles) | Frontend | M |
| P3-010 | Heading hierarchy unaudited on individual pages | Frontend | S |
| P3-011 | search_results_store FK validation (verify-only) | DB | S (10min) |
| P3-012 | pipeline_items migration 025 has wrong initial FK target | DB | S (1h) |
| P3-013 | Orphan trigger function `update_pipeline_updated_at()` | DB | S (0.5h) |
| P3-014 | Onboarding skip button appears twice on steps 1-2 | Frontend | S (0.5h) |

### P3 Notes

**P3-011:** Migration `20260304100000` includes `VALIDATE CONSTRAINT` for this FK. Almost certainly valid. 10-minute production query to confirm: `SELECT conname, convalidated FROM pg_constraint WHERE conrelid = 'public.search_results_store'::regclass AND contype = 'f';`

**P3-012:** Migration 025 creates `pipeline_items` with `REFERENCES auth.users(id)`. Later migration `20260225120000` re-points to `profiles(id)`. On fresh installs where migrations run sequentially, this works but is fragile. Not a production issue.

---

## Quick Wins (Ship This Week)

Ordered by impact-to-effort ratio:

| # | Action | Effort | Impact | Files to Change |
|---|--------|--------|--------|-----------------|
| 1 | **P0-VERIFY: Confirm RLS fixes in production** | 10min | Closes last security question | Run SQL query in Supabase SQL Editor |
| 2 | **P1-012: Default pricing to annual** | 15min | +3-8% checkout conversion | `frontend/app/planos/page.tsx` line 92 |
| 3 | **P1-006: Add TestimonialSection to landing page** | 1h | +5-10% signup rate | `frontend/app/(landing)/page.tsx` (import + JSX) |
| 4 | **P2-018: Fix E2E Python version** | 5min | CI consistency | `.github/workflows/e2e.yml` line 48 |
| 5 | **P1-001 (partial): Make pip-audit + npm audit blocking** | 2h | Prevent CVEs shipping | `backend-tests.yml`, `frontend-tests.yml` |
| 6 | **P1-008: ComprasGov transparency badge** | 2h | Prevents support tickets | `frontend/app/buscar/` (search results header) |
| 7 | **P2-014: Add user_subscriptions service_role policy** | 0.5h | Defensive billing safety | New migration (4 lines SQL) |
| 8 | **P2-016: Fix Consultoria CTA button** | 0.5h | Consistent loading state | `frontend/app/planos/page.tsx` line ~604 |
| 9 | **P1-005: Product screenshot in hero** | 6h | +15-25% signup rate | `HeroSection.tsx`, `public/` |

---

## Resolved Items (Were in DRAFT, Now Closed)

| ID | Original Finding | Resolution | Evidence |
|----|-----------------|------------|---------|
| P1-002 | 5 tables have FKs to auth.users instead of profiles | All 5 tables already fixed in migrations `20260225120000` and `20260304100000` | DEBT-113 AC1 verification script passes. DB specialist confirmed via grep of all 86 migrations. |
| P1-003 | search_results_store FK possibly NOT VALID | Migration `20260304100000` includes `VALIDATE CONSTRAINT` statement. Downgraded to P3-011 (verify-only, 10min). | DB specialist: "If migration ran successfully, FK is validated." |
| P1-007 | search_sessions.status CHECK may reject 'consolidating'/'partial' | Non-issue. State manager has `status_map` that maps all internal states to CHECK-allowed values. 'consolidating'/'partial' never written to DB. | DB specialist verified `search_state_manager.py` lines 213-228. Grep: zero occurrences of 'consolidating'/'partial' in state manager. QA confirmed independently. |
| P1-010 | Missing retention on 4 operational tables | All 4 cron jobs already exist in migrations `022_retention_cleanup.sql` and `20260308310000_debt009_retention_pgcron_jobs.sql`. | DB specialist verified: `health_checks` (30d), `mfa_recovery_attempts` (30d), `search_state_transitions` (30d), `stripe_webhook_events` (90d). |
| CD-004 | Search state persistence vs status CHECK mismatch | Same as P1-007. State manager maps correctly. | Closed by DB specialist and confirmed by QA. |
| P0-001 | pipeline_items RLS cross-user access | Fixed in migration 027 (DROP + CREATE with TO service_role). Test coverage exists. Reclassified to P0-VERIFY. | `027_fix_plan_type_default_and_rls.sql` lines 57-67. `test_td001_rls_security.py` (7 tests). |
| P0-002 | search_results_cache RLS cross-user access | Fixed in migration 027 (same pattern). Reclassified to P0-VERIFY. | `027_fix_plan_type_default_and_rls.sql` lines 75-85. Same test file. |

---

## Cross-Domain Risk Matrix

| Risk | Probability | Impact | Mitigation | Owner |
|------|-------------|--------|------------|-------|
| Migration 027 not applied in production | LOW | CRITICAL | Verify via `pg_policies` query. Deploy pipeline auto-applies. If not applied, run `supabase db push --include-all`. | @devops |
| CVE ships via non-blocking CI | MEDIUM | HIGH | P1-001: make pip-audit/npm audit blocking. Run audits locally to clear existing findings first. | @devops |
| In-flight search fails during deploy | HIGH | MEDIUM | P1-004: implement SIGTERM graceful shutdown with drain period. Current impact: ~30s of failures per deploy. | @dev |
| ComprasGov + PNCP rate limiting = degraded coverage | MEDIUM | MEDIUM | Circuit breakers handle gracefully. P1-008 adds transparency. Users see fewer results but no errors. | @dev |
| Single-instance overload during trial campaign | MEDIUM | MEDIUM | P1-009: horizontal scaling investigation. Current ceiling ~30 concurrent users. | @devops |
| Stripe webhook during schema migration | LOW | HIGH | Idempotency key + signature verification provide double protection. No action needed. | — |
| Frontend localStorage plan cache stale (1hr TTL) | LOW | LOW | Backend quota is real enforcement. Cosmetic mismatch for up to 1hr after plan change. | — |
| Auth token cache lost on deploy | MEDIUM | LOW | L2 Redis compensates. 75s Gunicorn keep-alive prevents connection reset. | — |
| Untested backup restore | LOW | CRITICAL | P2-012: 4h PITR restore test to scratch project. Currently assumed, not verified. | @devops |

---

## Production Verification Checklist

Run these before declaring GTM-ready:

- [ ] **RLS policies (P0-VERIFY):**
  ```sql
  SELECT tablename, policyname, roles, cmd
  FROM pg_policies
  WHERE tablename IN ('pipeline_items', 'search_results_cache')
    AND policyname LIKE '%service%'
  ORDER BY tablename, policyname;
  ```
  Expected: `roles` contains `{service_role}`, NOT `{0}`.

- [ ] **FK validation (P3-011):**
  ```sql
  SELECT conname, convalidated
  FROM pg_constraint
  WHERE conrelid = 'public.search_results_store'::regclass AND contype = 'f';
  ```
  Expected: `convalidated = true`.

- [ ] **Retention cron jobs active:**
  ```sql
  SELECT jobname, schedule, command
  FROM cron.job
  WHERE jobname LIKE 'cleanup-%'
  ORDER BY jobname;
  ```
  Expected: 4+ cleanup jobs (health_checks, mfa_recovery_attempts, search_state_transitions, stripe_webhook_events).

- [ ] **Profile defaults correct:**
  ```sql
  SELECT column_default
  FROM information_schema.columns
  WHERE table_name = 'profiles' AND column_name = 'plan_type';
  ```
  Expected: `'free_trial'::text`.

- [ ] **Run pip-audit locally** (before making it blocking in CI):
  ```bash
  cd backend && pip-audit -r requirements.txt
  ```

- [ ] **Run npm audit locally** (before making it blocking in CI):
  ```bash
  cd frontend && npm audit --audit-level=high
  ```

- [ ] **Verify alerting exists for critical metrics:**
  - `smartlic_supabase_cb_state` (circuit breaker open)
  - `smartlic_sse_connection_errors_total` (SSE failures)
  - Response latency p99 > 10s
  - Error rate > 5%

---

## Sprint Plan

### Week 1: Quick Wins + Verification (Days 1-5)

| Day | Task | Owner | Effort |
|-----|------|-------|--------|
| 1 | P0-VERIFY: Run production verification queries | @devops | 10min |
| 1 | P1-012: Default pricing to annual billing | @dev | 15min |
| 1 | P1-006: Import TestimonialSection to landing page | @dev | 1h |
| 1 | P2-018: Fix E2E Python version (3.11 -> 3.12) | @devops | 5min |
| 1 | P2-014: Add user_subscriptions service_role policy | @data-engineer | 0.5h |
| 2 | P1-001 (phase 1): Make pip-audit + npm audit blocking | @devops | 2h |
| 2 | P1-008: ComprasGov transparency badge | @dev | 2h |
| 2 | P2-016: Fix Consultoria CTA button component | @dev | 0.5h |
| 3-4 | P1-005: Product screenshot in hero section | @ux + @dev | 6h |
| 5 | P1-013: WhatsApp/contact CTA on pricing page | @dev | 2h |

**Week 1 outcome:** RLS verified, conversion quick wins shipped (+20-35% signup improvement estimated), CI security scans blocking, data source transparency.

### Week 2-3: P1 High Priority (Days 6-15)

| Task | Owner | Effort |
|------|-------|--------|
| P1-004: SIGTERM graceful shutdown | @dev | 4h |
| P1-011: Dashboard actionable insights (pipeline deadline alerts + new opportunities) | @dev | 8h |
| P1-001 (phase 2): Audit pr-validation.yml and staging-deploy.yml continue-on-error | @devops | 4h |
| P1-009: Horizontal scaling investigation + Redis SSE validation | @devops | 16h |

**Week 2-3 outcome:** Zero-downtime deploys, dashboard retention lever, CI fully hardened, scaling ceiling understood.

### Week 4-8: P2 Medium Priority

| Task | Owner | Effort |
|------|-------|--------|
| P2-001: Feature flag triage + categorization | @dev | 8h |
| P2-003: Load testing baseline | @devops | 8h |
| P2-004: Local model fallback for OpenAI outages | @dev | 4h |
| P2-005: next/image infrastructure (after P1-005 ships) | @dev | 4h |
| P2-011: Staging environment verification | @devops | 16h |
| P2-012: Backup recovery runbook + PITR test | @devops | 4h |
| P2-007: SearchResults context provider refactor | @dev | 8h |
| P2-019: Alerting rules for critical metrics | @devops | 4h |

**Week 4-8 outcome:** Operational confidence for sustained growth. Known capacity limits. Recovery procedures tested.

---

## Acceptance Criteria Summary

### P0-VERIFY (RLS production state)
- [ ] `pg_policies` query returns `{service_role}` for both tables
- [ ] Authenticated non-admin user can only see own pipeline items
- [ ] All pipeline CRUD tests pass (`test_pipeline.py`, `test_pipeline_coverage.py`, `test_pipeline_resilience.py`)

### P1-001 (CI hardening)
- [ ] pip-audit fails CI on HIGH+ vulnerability
- [ ] npm audit fails CI on HIGH+ vulnerability
- [ ] staging-deploy.yml runs tests blocking (TEMP markers removed)
- [ ] No false positives block legitimate PRs (`--ignore-vuln` for accepted risks)

### P1-004 (graceful shutdown)
- [ ] SIGTERM triggers drain (new requests 503, in-flight complete)
- [ ] Drain timeout configurable via env var (default 30s)
- [ ] `test_harden_022_graceful_shutdown.py` passes

### P1-005 (product screenshot)
- [ ] Hero shows annotated screenshot on desktop (50/50 layout) and mobile (stacked)
- [ ] `next/image` with `priority` and Portuguese `alt` text
- [ ] Page loads in <3s on 3G throttle

### P1-012 (annual default)
- [ ] `/planos` loads with annual billing selected
- [ ] `?billing=monthly` URL param overrides to monthly
- [ ] Existing tests pass

---

## Appendix: Specialist Review Summary

**DB Specialist (@data-engineer):** "The database is in better shape than the DRAFT suggests. The DEBT-001 through DEBT-120 hardening campaign resolved most of the issues flagged as open. The only genuine data exposure risk is P0-001/P0-002, which is a 10-line fix." Confirmed 4 items already resolved (P1-002, P1-007, P1-010, CD-004). Upgraded P3-011 to P2. Provided ready-to-deploy migration SQL.

**UX Specialist (@ux-design-expert):** "The product's core search-to-pipeline loop is polished, error handling is best-in-class for the market segment, and the billing integration is clean." Elevated P1-005 (product screenshot) to P0-adjacent urgency. Upgraded P2-014 (annual default) to P1 (15-minute fix). Added WhatsApp CTA (P1-013) and Consultoria button fix (P2-016). Provided detailed design specs for hero screenshot layout.

**QA (@qa):** "APPROVED WITH CONDITIONS. Solid analysis with clear actionable findings." Identified critical gap: migration 027 already fixes P0-001/P0-002 (missed by DB audit). Expanded P1-001 scope from 3 to 25 `continue-on-error` instances. Flagged E2E Python 3.11/3.12 mismatch. Provided comprehensive test coverage analysis for billing chain (strong) and auth chain (strong). Recommended production verification queries as Day 0 tasks.

---

## Appendix: Dependency Map

```
P0-VERIFY (RLS production check)
  |
  v (if not applied)
Deploy migration 027 immediately
  |
  v (verified)
P1-001 (CI hardening) ─── ship BEFORE other fixes to ensure fix pipeline is secure
  |
  v
P1-004 (graceful shutdown) ──> P1-009 (horizontal scaling) — scaling without shutdown = more deploy failures
  |
P1-005 (product screenshot) ──> P2-005 (next/image infra) — needs image optimization before adding many visuals
  |
P2-011 (staging env) ──> P2-012 (backup testing) — staging is where you test recovery
```

---

*Document generated by @architect (Atlas) incorporating feedback from @data-engineer (Delta), @ux-design-expert (Uma), and @qa (Quinn). Phase 8 of Brownfield Discovery workflow.*
