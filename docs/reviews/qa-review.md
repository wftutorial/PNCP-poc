# QA Review - Technical Debt Assessment

**Reviewer:** @qa (Quinn)
**Date:** 2026-04-08
**Phase:** Brownfield Discovery Phase 7
**Version:** v4 (supersedes v3 from 2026-03-31)
**Documents Reviewed:** `docs/prd/technical-debt-DRAFT.md` (49 items TD-001 to TD-049), `docs/reviews/db-specialist-review.md` (Phase 5), `docs/reviews/ux-specialist-review.md` (Phase 6)
**Codebase Verification:** Verified transformer.py hash algorithm, search hooks line counts, backend file sizes, migration count, FeedbackButtons touch targets

---

## Gate Status: APPROVED WITH CONDITIONS

The assessment is thorough and actionable. Both specialist reviews added genuine value (severity recalibrations, 9 new items). However, 3 factual errors in the DRAFT and 4 coverage gaps must be addressed before the final document is published.

**Conditions for full APPROVED:**
1. Fix TD-007/008/009 phantom file references (see Section 3.1)
2. Add the 4 missing concerns from Section 3
3. Incorporate severity recalibrations from Section 2 into the final matrix

---

## 1. Assessment Completeness

| Area | Covered? | Items | Gaps |
|------|----------|-------|------|
| Backend/System debts | Yes | TD-001 to TD-018 | TD-007/008/009 reference nonexistent files (see Section 3.1) |
| Database debts | Yes, thoroughly | TD-019 to TD-034 + TD-NEW-001/002/003 | None significant after @data-engineer review |
| Frontend/UX debts | Yes, thoroughly | TD-035 to TD-049 + TD-050 to TD-055 | None significant after @ux-expert review |
| Cross-cutting concerns | Partially | Section 4 in DRAFT | Missing: rate limiting debt, dependency pinning (Section 3.3) |
| Security | Partially | TD-005, TD-022, TD-030, TD-042 | Missing: OWASP dependency scanning (Section 3.4) |
| Testing | Not covered as standalone | Mentioned in specialist reviews | Missing: backend test anti-patterns, flaky test tracking (Section 3.5) |

---

## 2. Severity Calibration

### 2.1 Specialist Agreement Analysis

Both specialists were consistent in methodology: code-verified, hours-estimated, and prioritized. No conflicts between @data-engineer and @ux-expert since their domains do not overlap.

### 2.2 Severity Adjustments Validated

All specialist recalibrations are justified and validated:

| ID | Original | @data-engineer | @ux-expert | QA Verdict | Rationale |
|----|----------|---------------|------------|------------|-----------|
| TD-021 | High | **Medium** | -- | **Medium** (agree) | Infrequent plan changes, CHECK and table are consistent today |
| TD-022 | High | **Low** | -- | **Low** (agree) | Verified: `transformer.py` line 34 uses `hashlib.sha256()`. DRAFT was factually wrong. |
| TD-027 | Medium | **Low** | -- | **Low** (agree) | Low volume table, 1-year retention is fine but not urgent |
| TD-028 | Medium | **Low** | -- | **Low** (agree) | Theoretical concern with minimal practical value |
| TD-030 | Medium | **Low** | -- | **Low** (agree) | Migration 20260404 already addressed most gaps |
| TD-033 | Low | **Medium** | -- | **Medium** (agree) | Ticking time bomb. Should be P0 action, not P1. |
| TD-034 | Low | **Medium** | -- | **Medium** (agree) | Paying beta users = data loss is business-ending |
| TD-040 | Medium | -- | **Low** | **Low** (agree) | Verified: pages have different content (ROI calc vs plan cards) |
| TD-046 | Low | -- | **Medium-Low** | **Medium-Low** (agree) | No debounce found in SSE handler code |

### 2.3 Items Potentially Under-Rated

| ID | Current | Recommended | Rationale |
|----|---------|-------------|-----------|
| TD-033 | Medium (adjusted) | **High / P0** | @data-engineer estimates DB may already exceed 500MB. Insert failures on ingestion = complete service outage for the core feature. This is not "medium" -- it is an operational time bomb. |
| TD-015 | Medium | **Medium-High** | Railway kills requests at 120s but Gunicorn expects 180s. This causes silent failures with NO error logging on the backend side. Users see 504 with no trace in Sentry. Combined with the async search pipeline (CRIT-072), long searches can silently die. |
| TD-011 | Medium | **Medium-High** | Single-worker with no auto-scaling means a single slow request blocks ALL concurrent requests. Combined with TD-015, this is a latency cliff under load. |

### 2.4 Items Potentially Over-Rated

| ID | Current | Recommended | Rationale |
|----|---------|-------------|-----------|
| TD-035 | High | **Medium** | 607 lines is large but the hook is well-structured internally (the UX review confirms 5 clean extraction points). It works correctly and has tests. Refactoring is a maintainability improvement, not a defect. |
| TD-050 | High (new) | **Medium-High** | Same reasoning as TD-035. 852 lines is large but functional. The distinction between "code smell" and "debt" matters for prioritization. |

---

## 3. Gaps Identificados

### 3.1 CRITICAL: Phantom File References in DRAFT

The DRAFT lists these backend debts with specific file names:

| ID | DRAFT Claims | Actual File | Status |
|----|-------------|-------------|--------|
| TD-007 | `Execute.py` oversized (58KB) | **Does not exist** in `backend/` | INVALID |
| TD-008 | `Generate.py` oversized (27KB) | **Does not exist** in `backend/` | INVALID |
| TD-009 | `Filter_stage.py` oversized (20KB) | **Does not exist** in `backend/` | INVALID |

**Actual oversized backend files (verified via `wc -l`):**

| File | Lines | Concern |
|------|-------|---------|
| `backend/quota.py` | 1,660 | Quota logic, plan enforcement, atomic operations |
| `backend/consolidation.py` | 1,394 | Multi-source result consolidation |
| `backend/llm_arbiter.py` | 1,362 | LLM classification pipeline |
| `backend/routes/search.py` | 784 | Search endpoint handlers |
| `backend/routes/user.py` | 715 | User profile routes |
| `backend/routes/blog_stats.py` | 704 | Blog analytics |

TD-010 correctly identifies `quota.py` as oversized (though states 65KB+, actual is 1,660 lines / ~55KB). TD-007/008/009 must be **replaced** with debts referencing the actual files above, or **removed** if the referenced files were refactored/renamed since the architecture doc was written.

**Action required:** Correct or remove TD-007, TD-008, TD-009. Replace with actual oversized file debts.

### 3.2 Missing: Test Infrastructure Debt

Neither the DRAFT nor specialists cover testing debt:

- **5,131+ backend tests with 30s global timeout:** The `pyproject.toml` timeout and the Anti-Hang Rules in CLAUDE.md suggest past incidents with hanging tests. No tracking mechanism for flaky tests exists.
- **No mutation testing:** High line coverage (70% threshold) does not guarantee test quality. Mutation testing would reveal weak assertions.
- **Test execution time on Windows:** The `run_tests_safe.py` subprocess isolation script exists specifically because the standard `pytest` runner hangs on Windows. This is a development velocity debt.
- **Frontend: 2,681+ tests but no a11y testing in CI:** jest-axe is not integrated (noted by @ux-expert but not captured as a formal debt item).

**Proposed:** TD-056 (Medium, P2): Integrate jest-axe into frontend CI for top 10 components. TD-057 (Low, P3): Add flaky test tracking/quarantine mechanism for backend.

### 3.3 Missing: Dependency Management Debt

- **No `pip-audit` or `safety` in CI:** Backend dependencies are not scanned for known vulnerabilities.
- **No `npm audit` gate in CI:** Frontend dependencies not scanned.
- **requirements.txt uses loose pinning:** Many entries use `>=` without upper bounds, risking breaking changes on fresh installs.

**Proposed:** TD-058 (Medium, P2): Add dependency vulnerability scanning to CI (pip-audit + npm audit).

### 3.4 Missing: Security Scanning Debt

- **No SAST/DAST in CI:** No static or dynamic application security testing.
- **No secret scanning:** Beyond `.env` gitignore, no automated detection of accidentally committed secrets.
- **TD-005 (per-user tokens) lacks a concrete attack scenario:** The DRAFT says "risk of privilege escalation if RPC doesn't validate auth.uid()" but does not inventory which RPCs are vulnerable. This needs a targeted audit.

**Proposed:** TD-059 (Medium, P1): Audit all Supabase RPCs for auth.uid() validation gaps. TD-060 (Low, P3): Add GitHub secret scanning + SAST to CI.

### 3.5 Missing: Monitoring/Alerting Gaps

- **No alerting on ingestion failures:** If the daily crawl fails, there is no PagerDuty/Slack notification. The `ingestion_runs` table logs failures but nobody is watching.
- **No SLO alerting:** SLO targets exist (PNCP 95%, cache 70%) but no alerts fire when breached.
- **TD-NEW-003 (datalake cache observability)** was correctly identified by @data-engineer but the same gap exists for the L1 InMemoryCache and L2 Supabase cache.

**Proposed:** TD-061 (Medium, P1): Add alerting for ingestion pipeline failures (Slack webhook or Sentry alert rule).

---

## 4. Riscos Cruzados

Cross-area risks where debts compound:

| Risco | Areas Afetadas | Severidade | Mitigacao |
|-------|---------------|------------|-----------|
| **DB storage exhaustion cascade:** TD-033 (FREE tier) + TD-020 (soft-delete bloat) + TD-025/026/027 (no retention) = storage fills, ingestion fails, search returns stale data, users see empty results | DB, Backend, Frontend | **Critical** | Upgrade Supabase tier (TD-033) FIRST, then add retention crons |
| **Silent request death:** TD-015 (Railway 120s kills) + TD-011 (single worker blocks) + TD-004 (async deadline) = long searches die silently, no Sentry trace, user sees generic 504 | Backend, Infra, Frontend | **High** | Align timeouts (TD-015), add Railway timeout detection middleware |
| **Search page maintainability cliff:** TD-035 (607 lines) + TD-050 (852 lines) + TD-051 (3,775 total) = any search feature change requires understanding 3,775 lines of interconnected hooks | Frontend | **Medium** | Refactor in planned order: useSearchExecution first, then useSearchFilters |
| **Security audit readiness:** TD-005 (service_role usage) + TD-030 (incomplete RLS docs) + TD-059 (no RPC audit) = cannot pass a security audit | Backend, DB, Security | **Medium** | RPC audit (TD-059) first, then document (TD-030), then migrate tokens (TD-005) |
| **Data loss without recovery:** TD-034 (no PITR/backup) + TD-033 (FREE tier) = if Supabase has an incident, no independent recovery path exists | DB, Infra | **High** | Supabase Pro upgrade enables PITR. Add pg_dump to S3 as independent backup. |
| **Mobile UX degradation:** TD-046 (SSE jank) + TD-052 (touch targets) + TD-047 (BottomNav covers content) + TD-055 (missing padding) = mobile experience is materially worse than desktop | Frontend, UX | **Medium** | Bundle mobile fixes into a single sprint (4-6h total) |

---

## 5. Dependencias Validadas

### 5.1 Resolution Order Review

The @data-engineer proposed a dependency graph. I validate and extend it:

```
PHASE 1 - Immediate (Week 1-2, no dependencies):
  TD-033 Supabase Pro upgrade -----> unblocks TD-034 (PITR)
  TD-019 composite index ----------> ship independently
  TD-025/026/027 + TD-NEW-001 ----> retention crons (bundle in 1 migration)
  TD-022 COMMENT fix --------------> ship with retention crons
  TD-052 FeedbackButtons touch ----> ship independently (1h)

PHASE 2 - Foundation (Week 3-6):
  TD-034 weekly pg_dump to S3 -----> requires TD-033 (Pro tier for larger DB)
  TD-020 + TD-NEW-002 investigate -> must precede TD-016 (squash)
  TD-021 plan_type FK migration ---> must precede TD-016 (squash)
  TD-029 alert cron async ---------> independent, backend-only
  TD-061 ingestion alerting -------> independent, infra-only
  TD-059 RPC auth.uid() audit -----> informs TD-005 scope

PHASE 3 - Refactoring (Week 7-12):
  TD-050 useSearchExecution split -> before TD-035 (shared patterns)
  TD-035 useSearchFilters split ---> after TD-050 (reuse extraction patterns)
  TD-037 saved filter presets -----> after TD-035 (cleaner hook surface)
  Backend file splits -------------> after correcting TD-007/008/009 references

PHASE 4 - Quality & Tooling (Week 12-20):
  TD-016 migration squash ---------> AFTER all Phase 1-2 migrations are merged
  TD-036 visual regression --------> can parallel with Phase 3
  TD-058 dependency scanning ------> independent, CI-only
  TD-056 jest-axe integration -----> independent, CI-only

PHASE 5 - Backlog (ongoing):
  TD-043 Storybook, TD-048 i18n, TD-049 offline -- defer
```

### 5.2 Sequence Validation

- **No circular dependencies detected.** The graph is a DAG.
- **TD-033 must be FIRST.** It is the single highest-risk item (potential imminent storage failure) and unblocks TD-034.
- **TD-016 (migration squash) must be LAST** among DB changes. All quick-win migrations must be merged before squashing, otherwise the squash captures an intermediate state.
- **Frontend refactoring (TD-050/035) can run in parallel** with DB Phase 2 work -- no cross-domain dependencies.

### 5.3 Parallelization Opportunities

| Track A (DB/Infra) | Track B (Frontend) | Track C (Security/CI) |
|--------------------|--------------------|-----------------------|
| TD-033 Pro upgrade | TD-052 touch targets | TD-059 RPC audit |
| TD-019 composite index | TD-050 hook split | TD-058 dep scanning |
| TD-025/026/027 retention | TD-035 hook split | TD-061 alerting |
| TD-034 pg_dump backup | TD-037 saved presets | TD-060 secret scanning |
| TD-020 bloat cleanup | TD-036 visual regression | |

Three parallel tracks can execute simultaneously if staffed.

---

## 6. Testes Requeridos

For each debt resolution phase, the testing requirements:

### Phase 1 (Quick Wins)

| TD | Test Type | Specific Tests |
|----|-----------|---------------|
| TD-033 | Manual validation | Run `pg_database_size()` before/after upgrade. Verify ingestion runs successfully post-upgrade. |
| TD-019 | Integration test | Run `EXPLAIN ANALYZE` on `search_datalake` RPC before/after index. Verify Index Scan (not BitmapAnd). Target: 50-70% latency reduction. |
| TD-025/026/027 | Unit test (SQL) | Verify cron jobs schedule correctly. Insert old rows, trigger cron, verify deletion. |
| TD-052 | E2E (Playwright) | Mobile viewport test: verify FeedbackButtons tap target >= 44x44px. |

### Phase 2 (Foundation)

| TD | Test Type | Specific Tests |
|----|-----------|---------------|
| TD-034 | Manual + automated | Restore pg_dump to staging. Verify data integrity. Time the restore (validate RTO). |
| TD-021 | Integration test | Insert profile with invalid plan_type -- verify FK violation. Run existing billing tests to ensure no regression. |
| TD-020 | Integration test | Seed rows with `is_active=false`, run cleanup, verify deletion. Run `search_datalake` to ensure no active rows affected. |
| TD-029 | Unit test | Mock 100 alerts, verify asyncio.gather processes all with correct concurrency limit. Verify error isolation (one failure does not kill batch). |
| TD-059 | Security audit | For each RPC, verify `auth.uid()` is checked. Document findings. |

### Phase 3 (Refactoring)

| TD | Test Type | Specific Tests |
|----|-----------|---------------|
| TD-050 | Unit + integration | All existing `useSearchExecution` tests must pass after split. No new functionality -- pure refactor. Run full frontend test suite (`npm test`). |
| TD-035 | Unit + integration | Same as TD-050. All existing `useSearchFilters` tests must pass. |
| TD-037 | Unit + E2E | New tests: save preset, load preset, delete preset, limit enforcement (max 10). E2E: full save/load flow on /buscar. |

### Phase 4 (Quality & Tooling)

| TD | Test Type | Specific Tests |
|----|-----------|---------------|
| TD-016 | Full regression | After squash: fresh `supabase db push` on empty database. Verify all tables, indexes, RPCs, RLS policies match production schema. Run full backend test suite. |
| TD-036 | CI integration | Chromatic snapshots for 10 screens. Verify baseline is green. Run on PR to catch regressions. |
| TD-058 | CI integration | `pip-audit` and `npm audit` run in CI. Verify they report known vulnerabilities (if any). |

---

## 7. Metricas de Sucesso

### Performance Benchmarks

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| `search_datalake` RPC latency (p50) | Unknown (needs baseline) | 50-70% reduction after TD-019 | `EXPLAIN ANALYZE` before/after |
| PNCP API availability | 94% | >= 95% | Prometheus `smartlic_pncp_health_*` |
| Cache hit rate | 65-75% | >= 75% sustained | Prometheus `smartlic_cache_hit_rate` |
| DB size | ~500MB (estimate) | Monitored, < 80% of tier limit | `pg_database_size()` weekly |
| Search page hooks total lines | 3,775 | < 2,500 after refactoring | `wc -l frontend/app/buscar/hooks/*.ts` |

### Coverage Thresholds

| Area | Current | Target | Gate |
|------|---------|--------|------|
| Backend test coverage | >= 70% (CI gate) | Maintain >= 70% | `pytest --cov` |
| Frontend test coverage | >= 60% (CI gate) | Maintain >= 60% | `npm run test:coverage` |
| a11y automated coverage | 0% | >= 80% of top 10 components | jest-axe after TD-056 |
| Visual regression coverage | 0% | 10 critical screens | Chromatic after TD-036 |
| Dependency vulnerability scan | Not in CI | 0 high/critical findings | pip-audit + npm audit after TD-058 |

### Security Scan Results

| Check | Current | Target |
|-------|---------|--------|
| RPCs with auth.uid() validation | Unknown | 100% of user-scoped RPCs (after TD-059) |
| Dependencies with known CVEs | Unknown | 0 high/critical (after TD-058) |
| Secrets in git history | Unknown | 0 (after TD-060) |

---

## 8. Parecer Final

### Summary Statistics

| Category | DRAFT | After Specialist Reviews | After QA Review |
|----------|-------|--------------------------|-----------------|
| Total debt items | 49 (TD-001 to TD-049) | 55 (+ TD-NEW-001/002/003 from DB, + TD-050/051/052/053/054/055 from UX) | 61 (+ TD-056 to TD-061 proposed by QA) |
| Critical/Resolved (monitoring) | 4 | 4 | 4 |
| High severity | 8 | 6 (2 downgraded) | 6 |
| Medium severity | 16 | 18 (2 upgraded, adjustments) | 20 |
| Low severity | 21 | 27 | 31 |
| Invalid items | 0 | 0 | 3 (TD-007/008/009 reference nonexistent files) |

### Critical Path

The absolutely critical sequence that must execute in order:

1. **TD-033** -- Upgrade Supabase to Pro tier (0.5h, budget decision). Blocks everything at scale.
2. **TD-019** -- Composite index on pncp_raw_bids (1h). Immediate query performance gain.
3. **TD-025/026/027 + TD-NEW-001** -- Retention crons (1.5h). Prevents unbounded table growth.
4. **TD-034** -- Weekly pg_dump to S3 (2h). Independent backup path.
5. **TD-059** -- RPC auth.uid() audit (4h). Security posture baseline.

Total critical path: ~9h of focused work.

### Estimated Total Effort

| Phase | Items | Hours | Timeline |
|-------|-------|-------|----------|
| Phase 1 (Quick Wins) | 8 | 6-8h | Week 1-2 |
| Phase 2 (Foundation) | 7 | 14-18h | Week 3-6 |
| Phase 3 (Refactoring) | 5 | 52-68h | Week 7-12 |
| Phase 4 (Quality/Tooling) | 6 | 28-36h | Week 12-20 |
| Phase 5 (Backlog) | ~20 | 150-250h | Ongoing |
| **Active total (Phases 1-4)** | **26** | **100-130h** | **~20 weeks** |

### Risk Assessment

| Risk Level | Count | Action |
|------------|-------|--------|
| Immediate operational risk | 2 (TD-033 storage, TD-034 no backup) | Execute this week |
| Security gap | 3 (TD-005, TD-059, TD-058) | Plan for Phase 2 |
| Maintainability drag | 8 (oversized files/hooks) | Phase 3, non-urgent |
| Accepted/deferred | ~20 | Backlog, revisit quarterly |

### GO/NO-GO Recommendation for Phase 8

**GO** -- with the following conditions:

| # | Condition | Source | Blocking? |
|---|-----------|--------|-----------|
| 1 | Fix TD-007/008/009 phantom file references. Replace with actual oversized files: `quota.py` (1,660 lines), `consolidation.py` (1,394 lines), `llm_arbiter.py` (1,362 lines). | QA verification | YES |
| 2 | Upgrade TD-033 to P0. Supabase FREE tier storage limit is an imminent operational risk. | QA + DB specialist | YES |
| 3 | Add 6 QA-proposed items (TD-056 to TD-061) to the final matrix, or explicitly document why excluded. | QA review | NO (advisory) |
| 4 | Incorporate all specialist severity recalibrations into the final priority matrix. The DRAFT matrix is stale. | Both specialists | YES |

The assessment is comprehensive, well-structured, and actionable. The specialist reviews added substantial value -- particularly @data-engineer's finding that TD-022 (MD5) was factually incorrect and @ux-expert's discovery of TD-050 (an 852-line hook larger than the one flagged in the DRAFT). The debt inventory, once corrected per the conditions above, provides a solid foundation for Phase 8 sprint planning.

---

*Review completed 2026-04-08 by @qa (Quinn) as Phase 7 of Brownfield Discovery.*
*Previous version: v3 (2026-03-31) reviewed the earlier 63-item numbering scheme.*
*Next: Phase 8 -- Final Technical Debt Assessment (incorporate all review feedback, publish final document).*
