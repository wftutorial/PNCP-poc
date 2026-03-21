# QA Review - Technical Debt Assessment

**Reviewer:** @qa (Quinn)
**Date:** 2026-03-21
**Input:** docs/prd/technical-debt-DRAFT.md + system-architecture.md + DB-AUDIT.md + frontend-spec.md
**Scope:** General quality review, gap analysis, test state assessment, gate decision

---

## Gate Status: APPROVED (with caveats)

The assessment is comprehensive, well-structured, and actionable. It correctly identifies 54 actionable debt items across 3 audits with consistent severity ratings, effort estimates, and a sound dependency-aware execution plan. The caveats below are improvements to track, not blockers.

---

## 1. Gaps Identificados

### 1.1 Areas Nao Cobertas

| Area | Status | Impact |
|------|--------|--------|
| **CI/CD debt** | Not audited | 17 GitHub Actions workflows exist but no audit of workflow health, redundancy, or gaps (e.g., `tests.yml` vs `backend-tests.yml` overlap) |
| **Dependency debt (backend)** | Not audited | `requirements.txt` has no pinned hashes, no `pip-audit` in CI. Python dependency vulnerabilities are unchecked beyond Dependabot. |
| **Dependency debt (frontend)** | Partially covered | DEBT-FE-001 (react-hook-form) noted, but no audit of outdated/vulnerable packages. `framer-motion 12.33.0` and `@sentry/nextjs 10.38.0` versions not validated. |
| **Observability/monitoring debt** | Not audited | Prometheus, OpenTelemetry, and Sentry are in the stack but no audit of metric coverage gaps, alert rules, or dashboard completeness. |
| **Documentation debt** | Minimally covered | DEBT-SYS-018 (stale backend docs) is LOW priority. No audit of API documentation (OpenAPI spec completeness), inline code comments, or developer onboarding docs. |
| **Infrastructure/IaC debt** | Not audited | Railway configuration is spread across `railway.toml`, `railway-worker.toml`, and env vars. No audit of infrastructure reproducibility. |
| **Secret management debt** | Not audited | 356 env vars mentioned but no audit of rotation policy, access scope, or whether secrets are properly scoped per service. |

### 1.2 Debitos Nao Identificados (QA-found)

| ID | Debt | Severity | Area | Evidence |
|----|------|----------|------|----------|
| **QA-DEBT-001** | `cron_jobs.py` (2,039 LOC) has ZERO test files | HIGH | Backend/Testing | `find backend/tests -name "*cron*"` returns nothing. This is a 2K LOC module running scheduled production tasks with no automated verification. |
| **QA-DEBT-002** | `supabase_client.py` (537 LOC, contains SupabaseCircuitBreaker) has ZERO test files | HIGH | Backend/Testing | The circuit breaker singleton is used by the entire backend. Tests mock it but never test it directly. |
| **QA-DEBT-003** | `search_state_manager.py` (544 LOC) has ZERO test files | MEDIUM | Backend/Testing | State machine for search lifecycle is untested. |
| **QA-DEBT-004** | `worker_lifecycle.py` (125 LOC) has ZERO test files | MEDIUM | Backend/Testing | ARQ worker startup/shutdown logic is untested. |
| **QA-DEBT-005** | 11 `filter_*.py` submodules have no individual test files | MEDIUM | Backend/Testing | `filter_basic.py`, `filter_density.py`, `filter_keywords.py`, `filter_recovery.py`, `filter_status.py`, `filter_uf.py`, `filter_utils.py`, `filter_value.py` -- all untested individually. Tests exist for `filter.py` (the monolith) but not for the decomposed submodules. This means DEBT-SYS-001 (filter decomposition) cannot verify correctness of individual submodules after refactoring. |
| **QA-DEBT-006** | `webhooks/` directory has no test file named `test_webhook_handler.py` -- coverage is via `test_stripe_webhook.py` and `test_payment_failed_webhook.py` which may not cover all 10+ event types | MEDIUM | Backend/Security | DEBT-SYS-007 identifies the webhook handler as 1,192 LOC. Need to verify all Stripe event types are tested. |
| **QA-DEBT-007** | Frontend pages with zero tests: `onboarding/`, `mensagens/`, `redefinir-senha/`, `ajuda/`, `features/` | MEDIUM | Frontend/Testing | Onboarding is the first protected experience (783 LOC) with no unit tests. |
| **QA-DEBT-008** | No backend `requirements.txt` lockfile with hashes | LOW | Backend/Security | `pip install -r requirements.txt` is vulnerable to supply chain attacks without hash verification. |
| **QA-DEBT-009** | Test-to-source LOC ratio discrepancy | INFO | Backend/Testing | DRAFT says 1.8x but the real concern is not the ratio -- it is that test coverage is unevenly distributed. Some modules have 10+ test files (filter, auth, cache) while others have zero. |

---

## 2. Riscos Cruzados

| Risco | Areas Afetadas | Probabilidade | Impacto | Mitigacao |
|-------|---------------|---------------|---------|-----------|
| **Billing status drift + untested webhook paths** | DEBT-DB-001 + DEBT-SYS-007 + QA-DEBT-006 | MEDIUM | CRITICAL | Paying users could lose access or free users could get paid features. Requires comprehensive webhook event type test matrix before any billing refactor. |
| **Backend restructuring breaks import paths** | DEBT-SYS-004 + DEBT-SYS-001 + DEBT-SYS-002 | HIGH (during Wave 3) | HIGH | 344 test files depend on current import paths. A single import change can cascade into dozens of test failures. Must snapshot test count before and after each restructuring step. |
| **Filter decomposition without submodule tests** | DEBT-SYS-001 + DEBT-SYS-012 + QA-DEBT-005 | HIGH | MEDIUM | The 11 `filter_*.py` submodules have no individual tests. Completing the filter decomposition (DEBT-SYS-001) without first adding submodule tests means regressions will be caught only by the monolith tests, which may not cover all edge cases in the submodules. |
| **Cron jobs untested + migration squash risk** | QA-DEBT-001 + DEBT-DB-008 | LOW | HIGH | `cron_jobs.py` orchestrates 15+ pg_cron retention jobs. If migration squash (DEBT-DB-008) alters cron job definitions, there are no tests to catch regressions. |
| **Circuit breaker untested + cache dependency** | QA-DEBT-002 + DEBT-SYS-006 | LOW | HIGH | `SupabaseCircuitBreaker` in `supabase_client.py` is a global singleton affecting every DB operation. If cache refactoring (DEBT-SYS-006) changes the interaction pattern, the breaker behavior is unverified. |
| **Frontend error boundaries missing on critical flows** | DEBT-FE-007 + QA-DEBT-007 | MEDIUM | MEDIUM | Onboarding has neither error boundaries nor unit tests. A runtime error during first-time user experience has no recovery path and no automated detection. |

---

## 3. Dependencias Validadas

### 3.1 Ordem Correta?

The proposed 4-wave execution order is **sound** with one correction needed:

**Wave 1 (Quick wins):** Correct. These are truly independent and low-risk. However, the DRAFT lists 18 quick wins at ~25h combined -- this is aggressive for a single sprint alongside feature work. Recommend splitting into 2 sub-waves:
- Wave 1a: Security quick wins (DEBT-DB-002 FK fix, DEBT-DB-006 RLS, DEBT-FE-008 skip-link, DEBT-FE-001 deps)
- Wave 1b: Maintainability quick wins (DEBT-SYS-013 ComprasGov, DEBT-SYS-008 types, remaining items)

**Wave 2 (Database hygiene):** Correct dependency chain. DEBT-DB-001 (subscription status) must precede DEBT-DB-008 (migration squash) because the squash should capture the resolved state.

**Wave 3 (Backend restructuring):** Correct but **must add a prerequisite**: create tests for untested modules (QA-DEBT-001 through QA-DEBT-005) BEFORE restructuring. Without these tests, restructuring is flying blind.

**Wave 4 (Frontend quality):** Correct and can genuinely run in parallel with Wave 3.

### 3.2 Bloqueios Potenciais

| Bloqueio | Afeta | Descricao |
|----------|-------|-----------|
| **No staging Stripe account** | DEBT-DB-009 (Stripe price IDs) | The DRAFT asks this question to @data-engineer. If no staging Stripe account exists, this item is blocked until one is created (1-2h setup on Stripe side). |
| **Test creation before restructuring** | Wave 3 (all) | Backend restructuring without first adding tests for `cron_jobs.py`, `supabase_client.py`, `search_state_manager.py`, and `filter_*.py` submodules is risky. Estimated blocker: 16-24h of test writing. |
| **CI workflow confusion** | Any parallel work | `tests.yml`, `backend-tests.yml`, and `backend-ci.yml` appear to overlap. Developers may not know which workflow gates their PR. Should be clarified before Wave 3 to avoid CI confusion during high-change periods. |

### 3.3 Oportunidades de Paralelizacao

The DRAFT's Group A/B/C parallelization is correct. Additional parallelization opportunities:

- **DEBT-FE-002 (SearchForm ARIA) + DEBT-FE-008 (skip-link)**: Both are accessibility, but touch completely different files. Can be done simultaneously.
- **DEBT-SYS-011 (test audit) can start in Wave 1**: It is an analysis task, not a code change. Starting early provides data for Wave 3 planning.
- **QA-DEBT-001 through QA-DEBT-005 (missing tests)**: Can be written in parallel with Wave 1 and Wave 2, serving as the prerequisite for Wave 3.

---

## 4. Estado Atual dos Testes

### 4.1 Backend

| Metric | Value |
|--------|-------|
| Total test files | 344 (332 in tests/, 12 in fixtures/integration/snapshots) |
| Estimated tests | 7,332+ passing, 0 failures baseline |
| Test LOC | ~140,199 |
| Source LOC | ~77,364 |
| Test/source ratio | 1.81x |
| Files with skip/xfail markers | 10+ (checked: `test_admin`, `test_alerts`, `test_alert_matcher`, `test_background_revalidation`, `test_bulkhead`, `test_cache_correctness`, `test_cache_refresh`, integration tests) |
| Integration test directory | Yes (backend/tests/integration/) |
| Snapshot tests | Yes (backend/tests/snapshots/api_contracts/) |
| Conftest fixtures | Comprehensive (ARQ isolation, circuit breaker reset, async task cleanup, fast asyncio sleep) |

**Coverage gaps (modules with ZERO test files):**

| Module | LOC | Risk Level | Notes |
|--------|-----|------------|-------|
| `cron_jobs.py` | 2,039 | HIGH | Production scheduled tasks, untested |
| `supabase_client.py` | 537 | HIGH | Circuit breaker singleton, only mock-tested indirectly |
| `search_state_manager.py` | 544 | MEDIUM | Search lifecycle state machine |
| `worker_lifecycle.py` | 125 | MEDIUM | ARQ worker startup/shutdown |
| `filter_basic.py` through `filter_value.py` (8 files) | ~1,500 est. | MEDIUM | Decomposed filter submodules |
| `bid_analyzer.py` | unknown | LOW | Bid analysis logic |
| `business_hours.py` | unknown | LOW | Business hours utility |
| `exceptions.py` | unknown | LOW | Custom exception classes |
| `schema_contract.py` | unknown | LOW | Schema validation |
| `schemas_stats.py` | unknown | LOW | Schema statistics |
| `seed_users.py` | unknown | LOW | User seeding script |
| `search_context.py` | 137 | LOW | Search context object |

### 4.2 Frontend

| Metric | Value |
|--------|-------|
| Total test files | 306 |
| Estimated tests | 5,583+ passing, 3 pre-existing failures |
| Coverage threshold | 60% (CI gate) |
| jest.setup.js polyfills | `crypto.randomUUID`, `EventSource` |
| Module name mapper | `@/` -> `<rootDir>/` (documented pitfall) |

**Coverage gaps (pages with ZERO test files):**

| Page | LOC | Risk Level | Notes |
|------|-----|------------|-------|
| `onboarding/page.tsx` | 783 | HIGH | First protected user experience, no tests |
| `mensagens/page.tsx` | 547 | MEDIUM | Feature-gated but routable |
| `redefinir-senha/page.tsx` | ~150 | MEDIUM | Password reset flow |
| `ajuda/page.tsx` | ~300 | LOW | Help center |
| `features/page.tsx` | ~300 | LOW | Marketing page |
| 4 SEO content pages (`como-*`) | ~200 each | LOW | Static content |

### 4.3 E2E

| Metric | Value |
|--------|-------|
| Total spec files | 31 (+ helpers directory) |
| Estimated tests | ~60 |
| Framework | Playwright |
| Accessibility specs | 2 (axe-core based: `accessibility-audit.spec.ts`, `dialog-accessibility.spec.ts`) |

**Critical flows covered:**
- Search happy path, validation, errors, LLM fallback
- Authentication UX, signup consent
- Pipeline kanban, dashboard flows
- Billing checkout, plan display
- SSE failure modes
- Mobile viewport, theme
- Landing page, institutional pages
- SEO schema validation

**Missing E2E flows:**
- Onboarding wizard (3-step flow) -- no dedicated E2E spec
- Password reset flow -- no spec
- Admin sub-pages (emails, metrics, partners, SLO) -- only admin-users.spec.ts
- Account settings sub-pages -- no spec
- Trial expiration conversion flow -- no spec
- Error boundary behavior -- covered by `error-handling.spec.ts` but not for onboarding/signup specifically

### 4.4 CI/CD

| Workflow | Purpose | Trigger |
|----------|---------|---------|
| `backend-tests.yml` | Backend pytest | PR + push |
| `frontend-tests.yml` | Frontend jest | PR + push |
| `e2e.yml` | Playwright E2E | PR + push |
| `backend-ci.yml` | Backend CI (lint + type check?) | PR |
| `tests.yml` | Combined tests? | Unknown -- potential overlap with above |
| `deploy.yml` | Production deploy + migration push | Push to main |
| `staging-deploy.yml` | Staging deploy | Push to staging? |
| `migration-gate.yml` | PR warning for unapplied migrations | PR |
| `migration-check.yml` | Block on unapplied migrations | Push + schedule |
| `pr-validation.yml` | PR checks | PR |
| `codeql.yml` | CodeQL security scanning | Schedule + PR |
| `lighthouse.yml` | Lighthouse performance audit | Schedule? |
| `load-test.yml` | Load testing (Locust) | Manual? |
| `handle-new-user-guard.yml` | Guard against handle_new_user changes | PR |
| `sync-sectors.yml` | Sector fallback sync | Manual? |
| `cleanup.yml` | Cleanup | Schedule? |
| `dependabot-auto-merge.yml` | Auto-merge Dependabot PRs | Dependabot |

**CI/CD gaps:**
- `tests.yml` vs `backend-tests.yml` vs `backend-ci.yml` -- potential redundancy, unclear which is the gate
- No `pip-audit` or `npm audit` in CI pipeline
- No SAST beyond CodeQL (no Semgrep, Snyk, or similar)
- No dependency license audit
- `load-test.yml` trigger unclear -- should be part of pre-release checklist

---

## 5. Testes Requeridos para Resolucao

### Para os Top 10 Debitos

| Rank | Debt ID | Testes ANTES (regressao) | Testes DEPOIS (aceitacao) | Metrica |
|------|---------|--------------------------|---------------------------|---------|
| 1 | DEBT-SYS-003 (sync/async dual) | Verify `pncp_client.py` sync fallback works under current test suite. Add test for `asyncio.to_thread()` wrapper. | Verify only `httpx` is used. No `requests` import. Thread pool not needed. | Import audit: `grep -r "import requests" backend/` returns 0 |
| 2 | DEBT-SYS-002 (schemas monolith) | Snapshot all Pydantic model names and their field sets. Run `pytest --co -q` to baseline test count. | All models importable from new locations. Backward-compat re-exports from `schemas.py`. Zero test failures. | Test count unchanged, import paths updated |
| 3 | DEBT-SYS-001 (filter.py decomp) | **Create individual test files for all 8 `filter_*.py` submodules** (QA-DEBT-005). Baseline: `pytest -k test_filter` pass count. | Each submodule has dedicated test file. `filter.py` reduced below 500 LOC. All filter tests pass. | filter test count >= current, `wc -l filter.py` < 500 |
| 4 | DEBT-DB-001 (subscription status) | Add test verifying current profiles.subscription_status and user_subscriptions.subscription_status are both readable and usable by `quota.py`. | Single canonical source documented. Mapping test exists. Webhook sync verified. | `test_subscription_status_canonical.py` passes |
| 5 | DEBT-DB-002 (FK to auth.users) | Run full migration replay on fresh DB (in CI or local). Document current FK target. | Migration replay succeeds. FK points to profiles(id). `\d classification_feedback` shows correct FK. | Migration replay CI step passes |
| 6 | DEBT-FE-001 (react-hook-form deps) | `npm ls react-hook-form` shows current location. Build succeeds. | `react-hook-form` in dependencies (not devDependencies). Build succeeds. | `npm ls react-hook-form` shows dependencies |
| 7 | DEBT-FE-002 (SearchForm ARIA) | **Add axe-core test for /buscar page** (extend existing Playwright accessibility audit). Document current violations. | SearchForm has `role="search"`, `aria-label`. axe-core /buscar returns 0 critical violations. | axe-core violation count for /buscar = 0 critical |
| 8 | DEBT-FE-008 (skip-link broken) | Manual keyboard test: Tab on /buscar, verify skip link does NOT work. Document in test. | `id="main-content"` on protected layout `<main>`. Skip link navigates correctly on /buscar. | E2E test: `page.keyboard.press('Tab')` + verify focus target |
| 9 | DEBT-SYS-008 (api-types bundle) | Measure current bundle size: `npm run build` + check `.next/analyze` or `next build --debug`. | Tree-shaking verified. Bundle size reduced. | Bundle size delta (bytes) |
| 10 | DEBT-SYS-013 (ComprasGov dead) | Verify ComprasGov circuit breaker is currently OPEN (expected). Log current timeout consumption. | ComprasGov client disabled via feature flag or removed. No timeout budget consumed. Pipeline source count = 2 (PNCP + PCP). | `grep "compras_gov" backend/logs` shows no requests |

---

## 6. Respostas ao Architect (Section 8 Questions)

### Q1: DEBT-SYS-011 (test LOC ratio) -- Should we audit for test duplication before refactoring?

**Yes, but with a narrow scope.** A full test duplication audit (8h per the DRAFT) is not blocking. Instead, I recommend a targeted approach:

1. Before Wave 3 restructuring, run `pytest --co -q | wc -l` to baseline the exact test count (currently 7,332+).
2. After each restructuring step (e.g., after `filter.py` decomposition), re-run and compare. The count must be >= baseline.
3. If test count drops, investigate whether tests were lost or legitimately consolidated.
4. For test duplication specifically, the concern is over-specified tests (testing implementation details like exact mock call counts). These should be identified and relaxed during the restructuring itself, not in a separate pass.

**Bottom line:** Baseline the count, validate after each step. Do not invest 8h in a pre-audit.

### Q2: Regression risk for Wave 3 -- What testing strategy?

**Recommended strategy (3-layer defense):**

1. **Pre-restructuring baseline**: `pytest --co -q | wc -l` (test discovery count) + `python scripts/run_tests_safe.py --parallel 4` (full pass count). Record both numbers.
2. **Per-step validation**: After each structural change (e.g., moving `filter.py` into `filter/` package), run the full suite. Zero tolerance for new failures. Use `git stash` to revert if failures appear and investigate before proceeding.
3. **Import path guard**: After Wave 3 completes, add a CI check that verifies no `from filter import X` (old path) remains in non-test code. This prevents regression from new code using old paths.

**Do NOT batch restructuring.** Each DEBT-SYS item in Wave 3 should be a separate PR with its own test validation.

### Q3: Quick wins -- batch into PRs or ship individually?

**Batch into 3 thematic PRs:**

- **PR 1 (Security/a11y):** DEBT-DB-002 FK, DEBT-DB-006 RLS, DEBT-FE-008 skip-link, DEBT-FE-001 deps, DEBT-DB-005 index (~5 items, ~3h)
- **PR 2 (Backend cleanup):** DEBT-SYS-003 sync/async, DEBT-SYS-013 ComprasGov, DEBT-DB-007 TOCTOU (~3 items, ~7h)
- **PR 3 (Frontend polish):** DEBT-FE-002 ARIA, DEBT-FE-015 icon, DEBT-SYS-008 types, DEBT-FE-007 error boundaries (~4 items, ~7h)

This avoids 18 individual PRs (review fatigue) while keeping each PR thematically coherent and independently revertible.

### Q4: DEBT-FE-007 (error boundaries) -- Do E2E tests cover error scenarios?

**Partially.** `error-handling.spec.ts` and `failure-scenarios.spec.ts` exist but focus on search errors and API failures. There is **no E2E spec** that:
- Triggers a React rendering error on the onboarding page
- Verifies the error boundary catches it
- Verifies a recovery action (e.g., "Tentar novamente" button) works

**Recommendation:** When adding error boundaries (DEBT-FE-007), also add 1 E2E test per page that injects a rendering error (e.g., mock a hook to throw) and verifies the error boundary renders. This is 1-2h additional effort on top of the 3h estimate.

### Q5: Accessibility testing -- axe-core E2E or manual screen reader?

**Both, in phases:**

1. **Phase 1 (automated, immediate):** Extend existing `accessibility-audit.spec.ts` to include `/buscar` and all protected pages. axe-core catches ~57% of WCAG 2.1 AA issues automatically. This validates DEBT-FE-002 and DEBT-FE-008. Effort: 2h.
2. **Phase 2 (manual, next sprint):** Manual NVDA/VoiceOver testing on `/buscar` and `/onboarding`. axe-core cannot verify that `aria-live` announcements are actually spoken, or that the search flow is comprehensible via screen reader. Effort: 4h.

For the DRAFT's current scope, Phase 1 (automated) is sufficient. Phase 2 should be done before claiming WCAG compliance.

---

## 7. Parecer Final

### Pontos Fortes do Assessment

1. **Consistent ID scheme and severity ratings.** All 54 items have unique IDs, severity, effort, and area. The renumbering from source audits to DRAFT IDs is clean (though the mapping should be documented -- see caveats).
2. **Dependency analysis is actionable.** The dependency chains in Section 6 correctly identify that `DEBT-SYS-004` (package grouping) is the gateway to Wave 3, and that `DEBT-DB-001` must precede `DEBT-DB-008`.
3. **Cross-cutting risk matrix in Section 7 is well-reasoned.** The billing integrity risk (DEBT-DB-001 + DEBT-SYS-007 + DEBT-SYS-009) is correctly identified as the highest-impact compound risk.
4. **Quick wins are genuinely quick.** The 18 items marked "Quick Win" are all verifiable small changes. The effort estimates are realistic.
5. **Questions for specialists (Section 8) are specific and decision-forcing.** Each question presents concrete options rather than open-ended asks.

### Pontos de Atencao

1. **ID mapping between source audits and DRAFT is not documented.** The DRAFT renumbers DB-DEBT-002 (dual subscription) to DEBT-DB-001, and DB-DEBT-001 (profiles wide) to DEBT-DB-003. Without a mapping table, cross-referencing between the DRAFT and the source audits is error-prone. Recommend adding an appendix.
2. **Test coverage gaps are the biggest unaddressed risk.** The DRAFT identifies DEBT-SYS-011 (test LOC ratio) as MEDIUM but misses that several critical production modules have ZERO test files. This is not about ratio -- it is about blind spots. `cron_jobs.py` (2,039 LOC) and `supabase_client.py` (537 LOC with the circuit breaker) are production-critical and untested.
3. **Wave 3 prerequisite is missing.** The execution plan goes directly to backend restructuring without requiring test creation for untested modules first. This should be a hard prerequisite.
4. **CI/CD debt is absent.** With 17 workflows, some potentially overlapping (`tests.yml` vs `backend-tests.yml` vs `backend-ci.yml`), this is a non-trivial source of developer confusion and CI cost.
5. **Observability debt is absent.** At POC stage this is acceptable, but as the product moves to revenue, metric coverage gaps and alert rule completeness become important.
6. **The DRAFT says "55 total" but lists 54 unique IDs.** The count includes 1 resolved item (DB-DEBT-006). The executive summary should say "55 identified, 54 actionable, 1 resolved" for clarity.

### Recomendacoes

1. **Add an ID mapping appendix** to the DRAFT (source audit ID -> DRAFT ID) to enable traceability.
2. **Elevate test coverage gaps to a new section** (or add QA-DEBT-001 through QA-DEBT-005 as new items). These are not captured in any of the 3 source audits and represent the highest risk during debt resolution.
3. **Add "Wave 0: Test safety net"** before Wave 3. Estimated 16-24h to create tests for `cron_jobs.py`, `supabase_client.py`, `search_state_manager.py`, and `filter_*.py` submodules.
4. **Consider a CI/CD mini-audit** (2-4h) to clarify workflow overlap and identify which workflow is the actual PR gate.
5. **Track the 3 pre-existing frontend test failures** -- these should be fixed or documented as accepted before starting frontend debt work (Wave 4) to maintain a clean baseline.
6. **The effort total (~297-325h) is realistic** for the identified items. With the additional test creation work (Wave 0), expect ~320-350h total.

---

*Review completed 2026-03-21 by @qa (Quinn). Gate status: APPROVED. The assessment is ready for sprint planning with the caveats above tracked as follow-up items.*
