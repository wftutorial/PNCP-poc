# QA Review - Technical Debt Assessment

**Reviewer:** @qa
**Data:** 2026-03-09
**Fontes:** technical-debt-DRAFT.md (Phase 4), db-specialist-review.md (Phase 5), ux-specialist-review.md (Phase 6)
**Codebase Snapshot:** branch `main`, commit `3c71ce93`
**Supersedes:** qa-review.md v2.0 (2026-03-07 by @qa Quinn) -- complete rewrite against new DRAFT ID scheme and specialist reviews

**Test Artifacts Reviewed:**
- Backend: 333 test files (170+ unit + 10 integration + fixtures/conftest), pyproject.toml config
- Frontend: 298 test files (__tests__/), jest.config.js
- E2E: 21 Playwright spec files (e2e-tests/) + 3 legacy specs (__tests__/e2e/)
- Manually inspected: test_auth.py, test_security_story210.py, test_filter_llm.py, test_full_pipeline_cascade.py, conftest.py (root + integration), sse-proxy-crit048.test.ts, search-flow.spec.ts, dialog-accessibility.spec.ts

---

## Gate Status: APPROVED (with conditions)

---

## Resumo Executivo

The technical debt assessment is **thorough and production-ready for planning**, with strong contributions from the three specialist phases. The DRAFT correctly identified 93 items across system, database, and frontend layers. The subsequent specialist reviews refined this to a more accurate picture: the DB review eliminated 10 already-resolved items and added 4 new ones; the UX review eliminated 3 resolved items and added 4 new ones. The net result is a validated catalog of approximately 80 active debt items with concrete file/line references, cross-validated severity ratings, and a well-mapped dependency graph.

The assessment quality is high in three dimensions: (1) each item has traceable evidence in the codebase, (2) the DB specialist review is exemplary -- every item was cross-referenced against 76 migration files and specific `billing.py` line numbers, and (3) the UX review correctly identified 3 false positives (FE-005 already fixed in globals.css, FE-007 aria-live present in 15+ components, FE-A11Y-04 focus-trap-react in 6 modals) that would have wasted sprint capacity.

However, my cross-cutting analysis reveals three gaps that must be addressed before execution: (a) the assessment lacks a **regression risk matrix** for P0/P1 fixes -- several touch auth, billing, and search pipeline code paths where a bad fix causes production outages; (b) there is **no baseline test execution report** to anchor the "5131+ backend / 2681+ frontend" claims against actual pass rates on the current commit; (c) the **Stripe billing pathway** has been under-analyzed relative to its business criticality -- webhook handler test files exist (3 files) but no end-to-end contract test verifies the checkout-to-plan_type sync flow.

---

## Gaps Identificados

### Areas Nao Cobertas

| Area | Descricao | Impacto |
|------|-----------|---------|
| **Billing/Stripe end-to-end** | The assessment focuses on DB-level billing debts (DB-013 legacy column) but does not audit the `routes/billing.py` -> `services/billing.py` -> Stripe webhook handler chain for correctness. Three test files exist (test_stripe_webhook.py, test_payment_failed_webhook.py, test_billing_period_update.py) but no integration test verifies the full checkout -> webhook -> profile.plan_type sync flow. | HIGH -- billing is revenue-critical |
| **Cron job reliability** | 22 test files reference cron_jobs but the assessment only mentions retention jobs (DB-010). No analysis of cron_jobs.py itself for error handling, retry logic, or overlap protection (what if a job takes longer than its schedule interval?). | MEDIUM -- silent failures in cron could cause data accumulation |
| **Redis failure modes** | The assessment covers circuit breakers and cache fallback but does not analyze what happens when Redis is completely unavailable at startup. The two-level cache (L1 InMemory + L2 Supabase) should degrade gracefully, but redis_pool.py and redis_client.py are not audited for debt. | MEDIUM -- Redis is a single point for rate limiting and state |
| **Email delivery reliability** | email_service.py and templates/emails/ are mentioned in the architecture but not audited for debt. Failed email delivery (Resend downtime) could silently drop trial reminders, password resets, and alert digests. | LOW -- non-blocking but affects user experience |
| **Worker process isolation** | The ARQ worker (`PROCESS_TYPE=worker` in start.sh) shares code with the web process. No analysis of whether worker-specific issues (memory leaks from long-running LLM jobs, ThreadPoolExecutor exhaustion) could affect stability. | MEDIUM -- worker crashes are silent to users |
| **API versioning debt** | SYS-025 mentions legacy non-/v1/ routes but the assessment does not catalog which routes are deprecated, which are active, and whether clients still use old routes. No deprecation telemetry exists. | LOW -- affects API contract clarity |

### Debitos Nao Identificados

| ID | Debito | Severidade | Localizacao | Justificativa |
|----|--------|-----------|-------------|---------------|
| **QA-NEW-01** | Integration conftest.py lacks `_cleanup_pending_async_tasks` and `_isolate_arq_module` -- these are documented in CLAUDE.md as critical anti-hang fixtures. Root conftest.py has them but integration conftest uses ad-hoc warning suppression (`filterwarnings("ignore", message="coroutine.*was never awaited")`) instead. | MEDIUM | `backend/tests/integration/conftest.py` | Risk of test suite hangs in integration tests; suppressed warnings mask real async bugs |
| **QA-NEW-02** | `@axe-core/playwright` is installed as a devDependency but is not imported or used in ANY of the 21 E2E spec files. Zero automated accessibility assertions in E2E. The dialog-accessibility.spec.ts tests focus-trap behavior manually but does not run axe audits. | HIGH | `frontend/e2e-tests/` | Accessibility regressions will go undetected; the "resolved" a11y items (FE-005, FE-007, FE-A11Y-04) are verified by code inspection only |
| **QA-NEW-03** | No enforced contract/snapshot test for OpenAPI schema stability. `tests/snapshots/openapi_schema.json` and `openapi_schema.diff.json` exist, but the diff file shows as modified in git status right now, suggesting drift is actively happening without detection. | MEDIUM | `backend/tests/snapshots/` | Frontend/API consumer contract risk; breaking changes could ship undetected |
| **QA-NEW-04** | Backend coverage config uses global 70% threshold with broad source inclusion (`.`). No per-module minimum thresholds for critical modules (auth.py, billing.py, search_pipeline.py). A global 70% could mask 20% coverage on revenue-critical paths. | MEDIUM | `backend/pyproject.toml [tool.coverage]` | False sense of coverage adequacy |
| **QA-NEW-05** | Frontend jest.config.js enables `clearMocks`, `resetMocks`, AND `restoreMocks` simultaneously. `resetMocks` resets both state and implementation, which can conflict with global mocks set in `jest.setup.js`. This triple-enable is unusual and may cause intermittent test behavior. | LOW | `frontend/jest.config.js:118-124` | Test reliability risk |

---

## Riscos Cruzados

| Risco | Areas Afetadas | Probabilidade | Impacto | Mitigacao |
|-------|---------------|:---:|:---:|-----------|
| **DB-001 FK migration breaks auth flow** | Database + Backend Auth + User Registration | Media | CRITICAL | DB-001 touches 4 remaining tables including `monthly_quota` (used by every authenticated search). Migrating FK from auth.users to profiles requires zero-downtime approach: NOT VALID + VALIDATE pattern (as DB review recommends). Run orphan detection query BEFORE migration. Have rollback migration ready. |
| **SYS-004 token hash fix invalidates cached sessions** | Backend Auth + All Authenticated Routes + Frontend | Alta | HIGH | Changing the hash function for the token cache means all cached auth tokens become cache misses simultaneously. This causes a thundering herd on JWT verification. Mitigate: (1) deploy during low-traffic window (Brazilian time 2-4 AM), (2) monitor p99 latency post-deploy, (3) consider dual-hash lookup (old + new) for 1h transition period. |
| **FE-010 CSP nonce breaks third-party scripts** | Frontend + Stripe Checkout + Sentry + Mixpanel + Cloudflare | Alta | CRITICAL | Removing `unsafe-inline`/`unsafe-eval` and implementing nonces will break any third-party script that injects inline code. Must test every third-party integration individually. Deploy behind feature flag first. Rollback plan: revert CSP header only (single middleware line). |
| **FE-001 buscar refactor introduces state bugs** | Frontend Search + SSE + Filters + Pipeline Integration | Media | HIGH | Extracting `useSearchOrchestration` from 983 LOC changes how 15+ state variables interact. Any stale closure or missing dependency in the extracted hook could break search. Mitigate: (1) comprehensive E2E test pass before AND after, (2) extract incrementally (one hook per PR), (3) A/B test on staging. |
| **SYS-002 LLM token fix changes classification behavior** | Backend LLM + Search Results Quality + User Trust | Media | HIGH | Increasing MAX_TOKENS from 300 fixes JSON truncation but may change classification outcomes (LLM generates longer, potentially different responses). Mitigate: run golden sample tests before and after, compare classification acceptance rates. |
| **Retention jobs delete debugging evidence** | Database + Observability + Customer Support | Baixa | MEDIUM | Retention jobs for search_state_transitions (30d), health_checks (30d), incidents (90d) could delete debugging evidence for in-progress investigations. Mitigate: retention jobs should check for open incidents before purging related records. |

---

## Validacao de Dependencias

### Ordem de Resolucao

The DRAFT's proposed order (P0 -> P1 -> P2 -> P3 -> P4) is **correct in principle** but needs four adjustments:

**Adjustment 1: DB-NEW-01 and DB-NEW-04 must precede DB-001 completion.**
The DB review correctly identifies that FK validation state in production is unknown. Running the diagnostic SQL queries is a zero-risk prerequisite that should happen BEFORE any FK migration work. This is currently in the DB review's "Phase 1: Verification" which is correct.

**Adjustment 2: SYS-004 (token hash) should be fixed BEFORE SYS-005 (ES256/JWKS).**
The DRAFT has both at P0/P1 but does not enforce order. SYS-004 is a live security vulnerability (CVSS 9.1) with a 0.5d fix. SYS-005 is a 1d enhancement. Fix the vulnerability first.

**Adjustment 3: FE-010 (CSP nonces) should move from P1 to P2.**
The UX review correctly estimates 12-16h for this item (the DRAFT says 1-2d). CSP nonce implementation with 5+ third-party scripts is complex and high-regression-risk. It should not be in the same sprint as the P0 security fixes. The current `unsafe-inline`/`unsafe-eval` is a real concern but not an immediate exploitation risk (it is defense-in-depth, not the primary auth barrier).

**Adjustment 4: DB-NEW-03 should join Batch B (Retention).**
The DB review identifies `search_results_store` as having unbounded growth with an `expires_at` column but no cleanup job. This is a 0.5h quick win that directly impacts storage billing.

### Bloqueios Potenciais

| Bloqueio | Items Afetados | Mitigacao |
|----------|---------------|-----------|
| **Production SQL access required** | DB-NEW-01, DB-NEW-04, DB-025 | The DB review provides exact queries. Requires Supabase dashboard/CLI access. Block until queries are run. |
| **Stripe test mode limitations** | DB-013 (billing migration) | Dropping `plans.stripe_price_id` requires verifying no Stripe webhook handler reads it. Test with Stripe CLI webhook forwarding in staging. |
| **Railway deploy window** | SYS-001 (uvicorn fix), SYS-004 (token hash) | Both require backend redeploy. SYS-004 causes cache invalidation thundering herd. Schedule for low-traffic window. |
| **Next.js build verification** | FE-001, FE-002, FE-010 | Major frontend refactors require full build verification. Measure current build time before starting. |
| **PNCP API rate limits** | SYS-003 (page size fix) | Testing the page size fix requires live PNCP API calls. Use the health canary test pattern (tamanhoPagina=10) to verify without hitting rate limits. |

---

## Testes Requeridos

### Testes Pre-Resolucao (baseline)

Before fixing ANY debt items, establish these baselines:

1. **Backend full suite pass rate:** Run `python scripts/run_tests_safe.py` and record pass/fail/skip counts. The claimed 5131+ should be verified on current commit.
2. **Frontend full suite pass rate:** Run `npm test` and record pass/fail/skip counts. The claimed 2681+ should be verified.
3. **E2E full suite pass rate:** Run `npm run test:e2e` and record results. Note any flaky tests.
4. **Backend coverage report:** Run `pytest --cov` and save per-module coverage breakdown. Identify modules below 50%.
5. **Frontend coverage report:** Run `npm run test:coverage` and save. Identify pages/hooks below 40%.
6. **Production FK state:** Run the 5 diagnostic SQL queries from db-specialist-review.md Section "Validacao Pendente em Producao".
7. **Bundle size baseline:** Run `npx next build` and record chunk sizes. This becomes the regression baseline for FE-001/FE-002.
8. **LLM classification golden samples:** Run `pytest -k test_golden_samples` and save results. This is the baseline for SYS-002.

### Testes Pos-Resolucao (por debito)

| ID Debito | Testes Necessarios | Tipo |
|-----------|-------------------|------|
| SYS-001 | Verify uvicorn starts with `[standard]` extra on Linux container. Test faulthandler disabled. Deploy to Railway staging and verify no SIGSEGV. | integration + manual |
| SYS-002 | Run golden_samples test. Compare classification rates before/after. Verify JSON parse success rate >99% with new MAX_TOKENS. Add test for MAX_TOKENS=300 truncation scenario. | unit + integration |
| SYS-003 | Test PNCP client with tamanhoPagina=50 (success) and tamanhoPagina=51 (must fail gracefully). Add canary test with real API. | unit + integration |
| SYS-004 | test_security_story210.py already covers collision detection (verified: test_different_tokens_produce_different_cache_keys, test_prefix_only_hash_would_collide, test_auth_cache_uses_full_token_hash). Add test: two concurrent requests with different tokens must not cross-pollinate. | unit |
| SYS-005 | test_auth_es256.py exists. Verify backward compatibility: HS256 tokens still work after ES256 support added. Test JWKS key rotation with 2 active keys. | unit + integration |
| SYS-010 | Test LLM call with artificial 16s delay -- must timeout at 15s. Test ThreadPoolExecutor does not deadlock under 10 concurrent timeouts. | unit |
| SYS-012 | Test LRU cache eviction at 5000 entries. Test that evicted entries do not cause classification regressions. | unit |
| DB-001 (4 remaining) | After migration: run FK diagnostic query, verify all 4 tables reference profiles(id). Test user deletion cascade through all dependent tables. Run orphan detection query pre-migration. | integration + manual SQL |
| DB-NEW-01 | Run `SELECT convalidated FROM pg_constraint WHERE conname = 'search_results_store_user_id_fkey'` in production. If NOT validated, run VALIDATE CONSTRAINT. | manual SQL |
| DB-NEW-03 | After creating pg_cron job: verify expired rows are deleted within 24h. Test that active (non-expired) rows are preserved. Monitor storage size for 1 week. | manual SQL |
| DB-013 | Phase 1: modify billing.py, deploy, monitor for 1 week that zero queries hit legacy column. Phase 2: DROP column only after monitoring confirms. | integration + monitoring |
| FE-001 | Full E2E search flow must pass (search-flow.spec.ts). Verify all 35 buscar sub-components render correctly. Test SSE progress, filter state, save dialog, keyboard shortcuts. Bundle size must not increase. | e2e + unit + performance |
| FE-002 | Measure bundle size before/after. Verify Recharts, dnd-kit, Shepherd.js, framer-motion are code-split. Test that dynamic imports load correctly. Measure LCP before/after. | unit + performance |
| FE-010 | Test all third-party scripts load with nonce-based CSP: Stripe.js, Sentry SDK, Mixpanel, Clarity, Cloudflare. Test theme init script and dark mode toggle still work. | e2e + manual |
| FE-NEW-02 | Add error boundary to dashboard, pipeline, historico, conta. Test that an error in a child component is caught and displays fallback UI with recovery action. | unit + e2e |

### Metricas de Qualidade

| Metrica | Baseline Atual | Target Pos-Debt | Prazo |
|---------|:---:|:---:|:---:|
| Backend test pass rate | 5131+ (claimed, unverified) | 100% (0 failures) | Continuous |
| Backend coverage (global) | 70% threshold | 70% global + 60% minimum per critical module (auth, billing, search_pipeline, filter) | P3 |
| Frontend test pass rate | 2681+ (claimed, unverified) | 100% (0 failures) | Continuous |
| Frontend coverage (branches) | 50% | 60% | P3 (FE-004) |
| Frontend coverage (lines) | 55% | 65% | P3 |
| E2E pass rate | Unknown (21 specs) | >95% (allow 1 flaky) | Continuous |
| E2E accessibility audits | 0 specs use axe-core | 5 core flows with axe assertions | P2 (QA-NEW-02) |
| Bundle size (JS first load) | Unknown (measure baseline) | <250KB gzipped | P2 (FE-002) |
| LLM JSON parse success rate | ~70-80% (SYS-002 implies 20-30% truncation) | >99% | P0 |
| Search p95 latency | Unknown | <5s for 5 UFs | Continuous |

---

## Analise de Cobertura de Testes Atual

### Backend

**Structure:** 333 Python files in `backend/tests/`, organized as:
- Root level: ~170 unit test files covering individual modules
- `tests/integration/`: 10 files for cross-module pipeline tests (cascade failure, concurrent searches, SSE independence, queue fallback, Supabase outage, canary tests)
- `tests/fixtures/`: Shared response fixtures (pncp_responses.py)
- `tests/snapshots/`: OpenAPI schema snapshot (drift detected -- diff.json is modified in git status)

**Patterns verified (good):**
- Auth tests (test_auth.py) correctly use `_token_cache.clear()` in autouse fixtures to prevent cache poisoning between tests
- LLM tests (test_filter_llm.py) correctly mock at `llm_arbiter._get_client` level per CLAUDE.md guidelines
- Integration tests (test_full_pipeline_cascade.py) correctly disable multi-source via monkeypatch and bypass InMemoryCache via patch
- Security tests (test_security_story210.py) include both positive (collision detection) and negative (bug demonstration) assertions -- a strong testing pattern
- Stripe webhook tests cover 3 angles: RLS security (test_webhook_rls_security.py), payment failure handling (test_payment_failed_webhook.py), and event processing (test_stripe_webhook.py)
- pytest-timeout configured at 30s global with thread method (Windows-compatible)

**Patterns of concern:**
- Root conftest.py is minimal (80 lines of basic mock fixtures). The `_cleanup_pending_async_tasks` and `_isolate_arq_module` fixtures documented in CLAUDE.md as critical autouse fixtures were not found in the root conftest during this inspection -- they may be in a different conftest or were not yet implemented.
- Integration conftest.py uses `warnings.filterwarnings("ignore", message="coroutine.*was never awaited")` to suppress async warnings rather than fixing the underlying fire-and-forget issues. This masks real bugs.
- No dedicated test for `search_pipeline.py` orchestration as a whole (only `test_search_pipeline_filter_enrich.py` for the filter+enrich stage)
- No dedicated test for `consolidation.py` merge logic (SYS-011 merge-enrichment debt has zero test coverage)
- No test for `progress.py` SSE event queue as a standalone module (tested indirectly through integration only)
- No dedicated route-level test for `routes/billing.py` (billing is tested via webhook and subscription route tests only)
- `pyproject.toml` coverage omits `tests/*` but measures all other files from `.` -- no per-module minimum enforcement

### Frontend

**Structure:** 298 test files in `frontend/__tests__/`, organized across:
- `api/`: 12 files testing API proxy routes (health, SSE, download, auth, analytics, alerts)
- `buscar/`: 7 files testing search sub-components (coverage-bar, freshness, truncation, data-quality, empty-failure, progressive-delivery, search-state-manager)
- `components/`: 20+ files testing shared components (ThemeProvider, UserMenu, QuotaBadge, RegionSelector, LoadingProgress, Footer, etc.)
- `hooks/`: 4 files testing custom hooks (useAnalytics, useFeatureFlags, useKeyboardShortcuts, useSearchFilters)
- `pages/`: 2 files only (LoginPage, AjudaPage)
- `pipeline/`: 3 files (AddToPipelineButton, PipelineAlerts, pipeline-types)
- `billing/`: 3 files (dunning-flow, payment-failed-banner, trial-upsell-cta)
- `auth/`: 2 files (mfa-flow, signup-confirmation)

**Patterns verified (good):**
- SSE proxy tests (sse-proxy-crit048.test.ts) correctly test retry behavior with ReadableStream mocking and call count assertions
- Component tests use `@testing-library/react` with proper render/query patterns
- jest.config.js correctly ignores E2E directories and test utilities via `testPathIgnorePatterns`
- Coverage thresholds are explicitly documented as "stepping stone toward 60%"
- `@swc/jest` transform for fast test compilation

**Patterns of concern:**
- Only 2 page-level tests (LoginPage, AjudaPage) out of 22 pages. Missing: dashboard, pipeline, historico, onboarding, conta, planos, buscar (as full page). Confirmed by FE-011.
- `clearMocks` + `resetMocks` + `restoreMocks` all true simultaneously in jest.config.js. This triple-reset is aggressive -- `resetMocks` resets both state AND implementation, which can conflict with global mocks set in `jest.setup.js`. Typically only `clearMocks` or `resetMocks` is used, not both.
- 3 legacy E2E specs in `__tests__/e2e/` alongside 21 in `e2e-tests/` (confirmed FE-020 -- two E2E locations)
- No snapshot tests for any component -- relies entirely on behavioral assertions (acceptable for this project size but limits regression detection for visual components)

### E2E

**Structure:** 21 Playwright spec files in `frontend/e2e-tests/` + 3 helper files:
- **Core flows:** search-flow, auth-ux, signup-consent, saved-searches
- **Error handling:** error-handling, failure-scenarios, empty-state
- **Accessibility:** dialog-accessibility (focus trap, Escape key -- manually tests WCAG 2.4.3)
- **Performance:** performance.spec.ts
- **Marketing/SEO:** 5 marketing validation specs (CTA, rich results, schema, GSC indexation)
- **Infrastructure:** crit072-async-search, smoke-gtm-root-cause
- **Admin:** admin-users.spec.ts
- **Page Object pattern** used consistently (SearchPage in helpers/page-objects.ts)

**Critical gaps:**
- **Zero axe-core usage** despite `@axe-core/playwright` being in package.json devDependencies. None of the 21 specs import or run automated accessibility audits. WCAG compliance is manually verified by code inspection only.
- **No billing/checkout E2E test.** The Stripe checkout flow, subscription management, and plan change flows are untested end-to-end. Plan display page has a spec (plan-display.spec.ts) but it tests rendering only, not the checkout flow.
- **No pipeline (kanban) E2E test.** The drag-and-drop pipeline is a core product feature with zero E2E coverage.
- **No SSE failure mode E2E test.** The SSE fallback cascade (SSE -> polling -> time-simulation) is unit-tested (3 sse-proxy test files) but not E2E-tested with real browser behavior.
- **No mobile viewport E2E test.** All specs appear to run at default viewport. Mobile-specific components (BottomNav, MobileDrawer) are untested in E2E context despite having unit tests.
- **No dashboard or historico E2E test.** Two of the highest-traffic authenticated pages have zero E2E coverage.

---

## Parecer Final

### Veredicto: APPROVED (com condicoes)

The technical debt assessment is comprehensive enough to proceed to planning. The three-phase brownfield discovery (system, database, frontend) followed by two specialist reviews has produced a validated, prioritized catalog of ~80 active debt items with concrete resolution paths.

The assessment is particularly strong in:
1. **Database layer** -- the DB review is exemplary, with every item cross-referenced against 76 migration files, 10 items correctly identified as already resolved, and production SQL verification queries provided ready to execute
2. **Security items** -- SYS-004 (token collision CVSS 9.1), SYS-005 (JWT rotation), FE-010 (CSP) are correctly identified and prioritized
3. **Dependency mapping** -- the batch groupings (A-F) and dependency chains are practical and reduce context-switching
4. **UX false-positive detection** -- the UX review's identification of 3 items that were already fixed (FE-005, FE-007, FE-A11Y-04) prevents wasted sprint capacity

### Condicoes para APPROVED

The following 5 conditions must be met before execution begins:

**Condition 1 (MUST): Run production SQL diagnostics.**
DB-NEW-01 (FK validation state) and DB-NEW-04 (search_results_cache FK target) require production queries from the DB review. Results may change the scope of DB-001. The 5 queries are provided in db-specialist-review.md and should be executed immediately.

**Condition 2 (MUST): Establish test baselines.**
Run backend and frontend full suites on the current commit, record pass/fail counts, and generate coverage reports. These become the regression baselines for all debt fixes. The claimed "5131+ backend / 2681+ frontend" numbers are from documentation, not a verified test run.

**Condition 3 (MUST): Move FE-010 (CSP nonces) from P1 to P2.**
The regression risk is too high for a P1 sprint that also includes P0 security fixes. CSP nonce implementation with 5+ third-party scripts (Stripe.js, Sentry, Mixpanel, Clarity, Cloudflare) needs a dedicated effort with thorough integration testing. The current `unsafe-inline`/`unsafe-eval` is defense-in-depth, not the primary auth barrier.

**Condition 4 (SHOULD): Add DB-NEW-03 to Batch B (Retention).**
The `search_results_store` cleanup job is a 0.5h quick win with direct storage billing impact. It has an `expires_at` column but no pg_cron cleanup.

**Condition 5 (SHOULD): Create regression test plan for P0 items.**
Each P0 fix (SYS-004, SYS-002, SYS-001, DB-002/DB-003 removed by DB review) must have a documented rollback plan and a specific test that validates the fix. SYS-004 in particular needs a thundering-herd mitigation strategy since it invalidates all cached auth tokens.

### Riscos Aceitos

The following risks are acknowledged but accepted for planning purposes:

1. **Test suite counts are unverified.** The "5131+ backend / 2681+ frontend" numbers are from CLAUDE.md documentation, not a live test run on the current commit. If the actual pass rate is lower, debt prioritization may need adjustment. Mitigated by Condition 2.

2. **No load/stress testing baseline.** The assessment does not include performance benchmarks. Items like SYS-010 (OpenAI timeout), SYS-014 (per-UF timeout), and SYS-015 (UF batching) are estimated based on code analysis, not measured production latency data.

3. **Third-party API instability.** PNCP API behavior changes (SYS-003) and Stripe API updates could invalidate assumptions. External dependencies are inherently unstable.

4. **Incomplete automated accessibility audit.** Despite the UX review's thorough code-level analysis, no automated accessibility testing exists in E2E (QA-NEW-02). The "resolved" a11y items are verified by code inspection, not automated assertion. `@axe-core/playwright` is installed but unused.

5. **Worker process not audited.** The ARQ worker runs the same codebase but is excluded from the debt assessment. Memory leaks or ThreadPoolExecutor exhaustion in long-running LLM jobs could cause silent failures not covered by this analysis.

6. **OpenAPI schema drift is active.** The `openapi_schema.diff.json` file is modified in git status right now (QA-NEW-03), meaning API contract drift is happening without CI detection. This does not block planning but should be addressed early.

---

*QA Review completed by @qa -- AIOS Brownfield Discovery Phase 7*
*Methodology: Cross-reference of DRAFT items against specialist reviews, manual inspection of 10+ test files across backend/frontend/E2E, structural analysis of 333 backend + 298 frontend + 21 E2E test files, gap identification through grep/glob of test coverage patterns, verification of anti-hang fixtures and mock patterns against CLAUDE.md guidelines.*
*Verdict: APPROVED with 5 conditions (3 MUST, 2 SHOULD). Ready for planning after conditions are met.*
