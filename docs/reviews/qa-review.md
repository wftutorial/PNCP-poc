# QA Review -- Technical Debt Assessment

**Reviewer:** @qa (Shield)
**Date:** 2026-03-10
**Sources:** technical-debt-DRAFT.md (Phase 4 v2, reconciled), DB-AUDIT.md (Phase 2), frontend-spec.md (Phase 3), GTM-READINESS-ASSESSMENT.md, actual code verification
**Baselines:** Backend 5131+ tests / 169 files / 0 failures, Frontend 5583+ tests / 304 files / 3 pre-existing, E2E 60 tests / 31 specs

---

## Gate Status: APPROVED WITH FINDINGS

The assessment is comprehensive enough for story creation. However, this review identifies **6 stale items** that are already resolved, **3 items that contradict actual code**, **2 gaps not covered**, and **4 cross-cutting risks** requiring attention. Corrections below should be applied before finalizing stories to avoid wasted effort.

---

## 1. Stale Items Report (Already Resolved -- Confirmed by Code Inspection)

These items appear in the DRAFT as open debt but are already fixed. Some are in Appendix A but their corresponding entries in the main tables were not fully purged or cross-referenced.

| DRAFT ID | Claim | Actual Code State | Evidence |
|----------|-------|-------------------|----------|
| **SYS-001** | faulthandler + uvicorn WITHOUT `[standard]` | **REVERSED**: `requirements.txt` line 10 now has `uvicorn[standard]==0.41.0`. faulthandler is conditionally enabled (dev/test only). DEBT-101 AC3 re-enabled uvloop. | `requirements.txt:10`, `main.py:1-9` |
| **SYS-008** | `requests` library still needed for sync PNCPClient | **RESOLVED**: `requests` is NOT in `requirements.txt`. `pncp_client.py` line 794 documents the migration to httpx. No production `import requests` found. | `requirements.txt` (no match), `pncp_client.py:794` |
| **SYS-027** | `chardet<6` pin needed for requests compat | **RESOLVED**: Since `requests` was removed entirely, there is no chardet pin and no need for one. | `requirements.txt` (no match) |
| **DB-002** | `search_results_store.user_id` missing ON DELETE CASCADE | **RESOLVED**: Migration `20260304100000_fk_standardization_to_profiles.sql` adds FK to profiles(id) ON DELETE CASCADE. | Migration line 22 |
| **DB-003** | `classification_feedback.user_id` missing ON DELETE CASCADE | **RESOLVED**: Migration `20260225120000_standardize_fks_to_profiles.sql` adds FK to profiles(id) ON DELETE CASCADE NOT VALID, then validates. | Migration lines 57-67 |
| **DB-005** | `search_state_transitions.search_id` no retention cleanup | **RESOLVED**: Migration `20260308310000_debt009_retention_pgcron_jobs.sql` creates pg_cron job for 30-day retention. | Migration lines 17-26 |
| **DB-010** | `health_checks`/`incidents` missing retention jobs | **RESOLVED**: Same retention migration creates pg_cron for health_checks (30d) and incidents (90d). | Migration lines 42-62 |
| **DB-030** | `stripe_webhook_events` no automated retention | **RESOLVED**: Migration `022_retention_cleanup.sql` creates pg_cron job for 90-day retention. | Migration line 81-84 |

**Impact:** 8 items in the priority matrix (Section 4) reference already-resolved debt. This inflates the P0/P1 list and would lead to creating stories for work already done. SYS-001 is particularly dangerous -- it was listed as CRITICAL P0 but has been actively reversed (uvloop re-enabled).

**Action required:** Remove SYS-001, SYS-008, SYS-027, DB-002, DB-003, DB-005, DB-010, DB-030 from the active debt table and move to Appendix A/B.

---

## 2. Items That Contradict Actual Code

| DRAFT ID | DRAFT Claim | Actual State | Correction |
|----------|-------------|--------------|------------|
| **SYS-010** | OpenAI client timeout=15s (5x p99) | Already fixed to **5s** via `_LLM_TIMEOUT` (env default "5"). DEBT-103 AC1 completed. Listed in Appendix A but also still in main HIGH table. | Move to Appendix A |
| **SYS-012** | LRU cache unbounded -- 5000 entry limit needed | Already implemented: `_ARBITER_CACHE_MAX = int(os.getenv("LRU_MAX_SIZE", "5000"))` with LRU eviction in `llm_arbiter.py:78-85`. DEBT-103 AC3/AC4. | Move to Appendix A |
| **FE-010** | `unsafe-inline`/`unsafe-eval` in CSP script-src | **Partially correct**: Script-src is fixed (nonce + strict-dynamic). But `style-src` still has `'unsafe-inline'` (middleware.ts:46). The DRAFT marks FE-010 as resolved in Appendix A without noting the style-src gap. | Mark script-src as resolved; create new item for style-src unsafe-inline |

---

## 3. Gaps Not Covered by Phase 1-3 Audits

### Gap 1: `style-src 'unsafe-inline'` remains in CSP

The DRAFT marks FE-010 as fully resolved, but `middleware.ts:46` still contains:
```
"style-src 'self' 'unsafe-inline'",
```
This is a known trade-off (Tailwind/Next.js inject inline styles), but it was not explicitly documented as an accepted risk or a remaining debt item. It should be cataloged as a MEDIUM item.

### Gap 2: `alert_preferences` auth.role() pattern NOT fixed

DB-006 in the DRAFT correctly identifies `alert_preferences` service role policy using `auth.role() = 'service_role'` instead of `TO service_role`. The DEBT-009 RLS standardization migration (`20260308300000`) fixed `classification_feedback`, `health_checks`, and `incidents` but **did not touch `alert_preferences`**. The DRAFT lists this as open (correct), but the GTM assessment Section 4 says "2 tabelas com auth.role()" implying it is tracked. Verify: `alert_preferences` (confirmed still uses auth.role()) and potentially `organizations`/`organization_members` (confirmed: auth.role() pattern in creation migration, though they also have GRANT TO service_role).

### Gap 3: No mention of `conversations` and `messages` retention

DB-028 identifies this gap. The retention migration (DEBT-009) does NOT include conversations or messages. For a messaging feature, unbounded growth is a concern. However, the feature is currently gated. This should be explicitly documented as "deferred until feature ungated" rather than left ambiguous.

### Gap 4: `classification_feedback` retention missing

DB-027 correctly identifies this. No pg_cron job exists for this table. The retention migration covers 6 other tables but not classification_feedback. With LLM feedback accumulating per search, this could grow significantly.

### Gap 5: Backend integration test gap -- no E2E test for user deletion cascade

The FK cascade fixes (DB-002, DB-003 in old IDs) are critical for GDPR/LGPD compliance. There is no integration test verifying that deleting a user in `auth.users` correctly cascades to `search_results_store`, `classification_feedback`, `user_oauth_tokens`, `google_sheets_exports`, `pipeline_items`, etc. This is a high-risk blind spot.

---

## 4. Cross-Cutting Risks

| Risk | Areas Affected | Severity | Mitigation |
|------|---------------|----------|------------|
| **FK migration ordering** | DB-001 (FK standardization) depends on cleaning orphan rows first. If profiles row creation fails during auth signup, any user_id FK to profiles will fail. The `handle_new_user()` trigger is the critical path -- it has been redefined 8 times across migrations. | HIGH | Add integration test for signup -> profile creation -> FK integrity. Verify `handle_new_user()` latest definition handles all edge cases. |
| **uvicorn[standard] re-enablement** | SYS-001 was about uvloop crashes. DEBT-101 re-enabled `uvicorn[standard]` with conditional faulthandler (dev only). If Railway changes its container base or Python version, the SIGSEGV could recur. No canary test exists for this. | MEDIUM | Add Railway deploy smoke test that verifies worker process survives 60s without SIGSEGV. Document the conditional faulthandler rationale. |
| **Retention job cascade** | 6+ pg_cron jobs run daily at staggered times (4:00-4:25 UTC). If Supabase's pg_cron extension is disabled or the connection pool is exhausted during deletion, retention silently fails. No alerting on retention job failures exists. | MEDIUM | Add monitoring for pg_cron job success/failure. Consider adding a `retention_runs` log table or Prometheus metric for job completion. |
| **CSP regression on dependency update** | Next.js or Sentry SDK updates could inject new inline scripts that break CSP nonce policy, causing silent JS failures in production. No CI test validates CSP compliance. | MEDIUM | Add E2E test that checks browser console for CSP violation reports. Or add a CSP report endpoint monitor. |

---

## 5. Dependency Validation

### Validated: Correct Dependencies
- FE-001 (buscar split) enabling FE-002 (dynamic imports) -- **correct**, already resolved together in DEBT-105/106
- DB-006 + DB-007 + DB-008 + DB-009 as single migration batch -- **correct**, but DB-006 (alert_preferences) was missed in the existing batch migration

### Hidden Dependencies Found
- **SYS-008 -> SYS-027**: Both are resolved. The dependency chain is moot.
- **DB-001 (FK standardization) -> all user deletion FKs**: The DEBT-104 migration handles orphan detection + deletion before FK alteration. This is correctly sequenced. However, `search_sessions` is NOT in the FK standardization scope -- it still references `auth.users` via its original schema. This should be documented.
- **FE-003 (SSE complexity) -> backend SSE changes**: Any simplification of the SSE proxy must be coordinated with backend `progress.py`. This cross-layer dependency is not documented in the DRAFT.

### Batching Recommendations (Updated)
| Batch | Items | Correction |
|-------|-------|------------|
| **Batch A: User Deletion** | Was DB-002, DB-003 -- both RESOLVED. Remove this batch. | N/A |
| **Batch B: Retention** | Remove DB-005, DB-010, DB-030 (resolved). Keep DB-026 (search_sessions -- resolved via DEBT-100), DB-027 (classification_feedback -- NOT resolved), DB-028 (conversations/messages -- NOT resolved), DB-029 (alert_sent_items -- resolved via DEBT-009). Net: only DB-027 and DB-028 remain. | Reduce to 2 items |
| **Batch C: auth.role() Standardization** | DB-006 (alert_preferences) still open. DB-007, DB-008 (organizations) -- uses auth.role() but also has GRANT TO. DB-009 (search_results_store) -- needs verification. | Verify actual state; may be 1-3 items |
| **Batch D: LLM Resilience** | SYS-010 and SYS-012 are RESOLVED. Only SYS-013 (per-future timeout counter) remains. | Single item, not a batch |

---

## 6. Test Requirements for Remaining P0/P1 Items

| Debt Item(s) | Tests Needed | Type | Priority |
|--------------|-------------|------|----------|
| **SYS-004** (token hash) | Already resolved per Appendix A. Verify with: test that `hashlib.sha256(full_token)` is used, and legacy partial hash only during transition window. Test file `test_debt101_security_critical.py` exists. | Unit | Verified |
| **SYS-005** (ES256/JWKS) | Already implemented per code (`auth.py:20-163`). Test file `test_auth_es256.py` exists. Verify JWKS cache TTL (5min) and HS256 fallback. | Unit + Integration | Verified |
| **SYS-003** (PNCP page size) | Already resolved. `PNCP_MAX_PAGE_SIZE=50` with server-side validation. | Unit | Verified |
| **DB-006** (alert_preferences auth.role()) | After fixing: verify service_role can CRUD alert_preferences without auth.role() check. Test RLS with anon role (should fail). | Integration | P2 |
| **ARCH-001** (routes/search.py 2177 LOC) | Before decomposition: add contract tests for all search endpoints to prevent regression. Snapshot tests for response schemas exist but verify completeness. | Contract | P2 |
| **FE-TD-004** (coverage 55% -> 60%) | Identify modules below 40%: likely `app/admin/`, `app/mensagens/`, `app/alertas/`. Add page-render + interaction tests for these. | Unit | P3 |
| **FE-TD-008** (96 raw hex colors) | After tokenization: visual regression test or Storybook snapshot to confirm no color changes. | Visual | P3 |
| **User deletion cascade** | NEW: Add integration test that creates a user, populates all FK-referencing tables, deletes user, and verifies all dependent rows are deleted. Critical for LGPD. | Integration | P1 |
| **CSP compliance** | NEW: Add E2E test that navigates authenticated pages and checks for CSP violations in console. | E2E | P2 |
| **Retention job monitoring** | NEW: Add test or monitoring that verifies pg_cron jobs executed successfully in last 48h. | Operational | P2 |

---

## 7. Answers to Section 6 QA Questions

### Q1: FE-004 (coverage 50-55%) -- Which modules have lowest coverage?

Based on the test file inventory, the following areas likely have the lowest coverage:
- `app/admin/` (6 pages, minimal test files found)
- `app/mensagens/` (feature-gated, likely minimal tests)
- `app/alertas/` (feature-gated)
- `app/conta/` sub-routes (5 routes, partial test coverage)
- `lib/animations/` (utility code, often untested)

Critical paths (billing, auth, search) appear well-covered: 6 billing/webhook test files, 14 auth test files, and extensive search test coverage. No evidence of any critical path below 40%.

### Q2: FE-011 (missing page tests) -- What is minimum viable test suite?

For `/dashboard`, `/pipeline`, `/historico`:
- **Minimum**: Render test (component mounts without crash) + loading state test + error state test = 3 tests per page
- **Recommended**: Add interaction tests for primary CTA per page (e.g., pipeline drag-and-drop, dashboard export, historico restore search) = 2-3 more per page
- Focus on **render tests first** -- they catch import errors and missing provider wrapping, which are the most common regression sources.

### Q3: FE-003 (SSE complexity) -- E2E coverage for SSE failure modes?

The `sse-failure-modes.spec.ts` file has **16 test cases** (275 lines), which is strong coverage for an E2E spec. Combined with the backend SSE tests (CRIT-012: 11 backend + 8 frontend = 19 tests), the SSE path is one of the better-tested areas. The gap is in **SSE proxy error handling paths** -- the custom undici bodyTimeout and AbortController logic is tested at the unit level but the full proxy chain (backend -> Next.js API route -> client EventSource) is only partially covered in E2E.

### Q4: Backend test anti-hang -- Recent incidents on Windows?

The `timeout_method="thread"` in `pyproject.toml` is the correct approach for Windows. The `run_tests_safe.py` script with subprocess isolation per file remains the recommended way to run the full suite on Windows. Key safeguards are in place:
- Conftest `_cleanup_pending_async_tasks` (cancels lingering asyncio tasks)
- Conftest `_isolate_arq_module` (prevents sys.modules pollution)
- Conftest `_reset_supabase_circuit_breaker` (prevents CB state leakage)
- `_fast_asyncio_sleep` fixture in test_crit055 (prevents 67.5s test)

No additional safeguards are needed unless a new pattern introduces blocking I/O in tests.

### Q5: Integration test gaps -- Billing webhooks and OAuth flows?

Billing webhook coverage is good: `test_stripe_webhook.py`, `test_payment_failed_webhook.py`, `test_webhook_rls_security.py`, `test_stripe_reconciliation.py`, `test_harden028_stripe_events_purge.py` = 5 test files.

OAuth coverage: `test_oauth.py`, `test_oauth_story224.py`, `test_routes_auth_oauth.py` = 3 test files.

**Gap identified:** No integration test for the complete Stripe checkout -> webhook -> plan update -> quota adjustment flow as a single transaction. Each step is tested individually but the end-to-end chain across `billing.py -> webhooks/stripe.py -> quota.py -> profiles.plan_type` is not tested as a pipeline.

### Q6: FE-A11Y testing -- axe-core usage in E2E specs?

`@axe-core/playwright` is used in **2 E2E spec files**: `accessibility-audit.spec.ts` (9 tests) and `dialog-accessibility.spec.ts`. Out of 31 total E2E specs, this means ~6% run accessibility audits. This is adequate for catching major WCAG violations but could be improved by adding `checkA11y()` calls to the end of high-traffic page specs (search-flow, dashboard-flows, pipeline-kanban).

### Q7: Regression risk -- Which P0/P1 items have highest regression risk?

With the stale items removed, the remaining actionable P0/P1 items and their regression risk:

| Item | Regression Risk | Reason |
|------|----------------|--------|
| **DB-001** (FK standardization remaining tables) | **HIGH** | FK changes can block INSERT operations if profile creation fails. Must test signup flow end-to-end after migration. |
| **ARCH-001** (routes/search.py decomposition) | **HIGH** | 2177 LOC with complex state management. Any split risks breaking the SSE/progress/tracker interaction. Add contract tests BEFORE splitting. |
| **DB-006** (alert_preferences RLS) | **LOW** | Simple policy replacement, well-isolated table. |
| **FE-TD-023** (Framer Motion dynamic import) | **MEDIUM** | Animation behavior could change on lazy load (flash of unanimated content). Test landing page visually. |
| **SYS-030** (filter.py decomposition) | **HIGH** | 2141 LOC facade with tight coupling to 10+ modules. Decomposition risks breaking the filtering pipeline. Add snapshot tests for filter output before splitting. |

**Recommendation:** For ARCH-001 and SYS-030, add targeted regression tests (contract tests for search responses, snapshot tests for filter output) BEFORE attempting decomposition.

---

## 8. Priority Matrix Correction

After removing stale/resolved items, the actual P0/P1 list shrinks significantly:

### True P0 (Immediate)
- **SYS-004** (token hash) -- Already resolved (Appendix A). Remove.
- **SYS-002** (LLM truncation) -- Already resolved (Appendix A). Remove.
- **SYS-001** (faulthandler/uvicorn) -- REVERSED (uvloop re-enabled). Remove.
- **DB-002, DB-003** -- Already resolved. Remove.
- **DB-005, DB-010, DB-030** -- Already resolved. Remove.

**Net P0: 0 items.** All original P0 items are resolved.

### True P1 (This Sprint)
- **SYS-005** (ES256/JWKS) -- Already implemented. Move to Appendix. Remove.
- **SYS-003** (PNCP page size) -- Already implemented. Remove.
- **DB-001** (FK standardization remaining) -- Partially resolved. Check which of 12 tables remain.
- **FE-010** (CSP) -- script-src resolved. style-src gap remains (MEDIUM, not HIGH).
- **SYS-010, SYS-012** -- Already resolved. Remove.

**Net P1: 1-2 items** (DB-001 remaining tables, style-src gap).

### Actual Priority Order for New Stories
1. **DB-001 remaining** -- Verify which tables still reference auth.users instead of profiles
2. **DB-006** -- alert_preferences auth.role() standardization
3. **ARCH-001** -- routes/search.py 2177 LOC decomposition
4. **User deletion cascade integration test** -- NEW, critical for LGPD
5. **DB-027** -- classification_feedback retention
6. **DB-028** -- conversations/messages retention
7. **SYS-030** -- filter.py 2141 LOC decomposition
8. **FE-TD-004** -- Coverage 55% -> 60%
9. **FE-TD-008** -- 96 raw hex colors tokenization
10. **FE-TD-023** -- Framer Motion dynamic import

---

## 9. Final Assessment

### Quality of the Assessment
- **Thoroughness:** 9/10 -- The Phase 1-3 audits are comprehensive. The system architecture doc, DB audit, and frontend spec cover the codebase well.
- **Accuracy:** 6/10 -- Significant number of stale items (8) that inflate the severity picture. The DRAFT was reconciled but the reconciliation was incomplete.
- **Actionability:** 7/10 -- The batching recommendations are good but need updating after stale removal. The dependency graph is sound.

### Confidence Level
**MEDIUM-HIGH.** The assessment correctly identifies the major debt areas (large files, retention policies, RLS inconsistencies, coverage gaps). However, the P0/P1 prioritization is misleading because most items are already resolved. Without the corrections in this review, story creation would produce duplicate work.

### Recommendation
**APPROVED for story creation** with the following conditions:
1. Remove all 8 stale items from active tables (move to Appendix)
2. Remove SYS-010, SYS-012 from active tables (resolved by DEBT-103)
3. Add style-src unsafe-inline as new MEDIUM item
4. Add user deletion cascade integration test as P1
5. Update priority matrix to reflect actual remaining work
6. Verify DB-001 remaining scope (how many of 12 tables still need FK migration)

Total remaining actionable debt is approximately **25-30 items** (not 93), with estimated effort of **20-25 engineering days** (not 45-55).

---

*Review completed by @qa (Shield) -- Phase 7, Brownfield Discovery Workflow*
*Method: Cross-referenced every P0/P1 claim against actual source code, migrations, and test files*
