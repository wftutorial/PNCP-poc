# QA Review - Technical Debt Assessment

**Reviewer:** @qa
**Date:** 2026-02-25
**Phase:** 7 (Brownfield Discovery QA Gate)
**Inputs:** `docs/prd/technical-debt-DRAFT.md`, `docs/reviews/db-specialist-review.md`, `docs/reviews/ux-specialist-review.md`, `docs/architecture/system-architecture.md`, `supabase/docs/DB-AUDIT.md`, `docs/frontend/frontend-spec.md`

---

## Gate Status: APPROVED

The assessment is complete enough to proceed to final consolidation and story creation. The DRAFT correctly identifies the 4 true blockers, both specialist reviews are thorough and well-evidenced, and the combined coverage addresses all core flows required for enterprise monetization. Specific conditions and gaps are documented below and must be incorporated into the final assessment.

---

## 1. Specialist Adjustments Validated

### DB Specialist (@data-engineer) Adjustments

| Adjustment | QA Verdict | Reasoning |
|------------|-----------|-----------|
| **T2-04 escalation** ("Consider Tier 1.5") | **AGREE -- Escalate to Tier 1** | Verified: migration `20260224000000` inserts only `id, email, full_name, phone_whatsapp`. Every new user signup since that migration silently drops `company`, `sector`, `whatsapp_consent`, `context_data`. Additionally lacks `ON CONFLICT (id) DO NOTHING` -- edge-case re-signup crashes auth entirely. This is not "stability" -- it is a functional regression on every new registration. Recommend Tier 1. |
| **T2-06 demotion** to Tier 3 | **AGREE** | Confirmed: `auth.role() = 'service_role'` pattern is functionally correct. Per-row evaluation overhead negligible for classification_feedback (low row count). Convention-only fix. |
| **T2-10 demotion** to Tier 3 | **AGREE** | Verified via code: `routes/analytics.py` fetches all sessions by `user_id` and aggregates in Python. No `@>` array containment queries exist at DB level. GIN indexes provide zero current benefit. |
| **T2-12 demotion** to Tier 3 | **AGREE** | Confirmed: `trial_email_log` is accessed only via service_role which bypasses RLS. Adding explicit policy is documentation, not functionality. |
| **T2-15 removal** (already fixed) | **AGREE** | Independently verified: `backend/quota.py` lines 1101, 1191, 1259 all use `await asyncio.sleep(0.3)`. The `time.sleep` debt no longer exists. Must be removed from DRAFT. |
| **MISSED-01** (`profiles.subscription_end_date`) | **AGREE -- Add to Tier 1** | Verified: `backend/routes/subscriptions.py` line 241 writes `subscription_end_date`. No migration creates it. Confirmed zero results in `supabase/migrations/`. Same pattern as T1-01. |
| **MISSED-02** (`profiles.email_unsubscribed` + `email_unsubscribed_at`) | **AGREE -- Add to Tier 1** | Verified: `backend/search_pipeline.py` line 79 SELECTs it, `backend/routes/emails.py` lines 147-148 UPDATEs both columns. No migration creates either. Confirmed zero results in `supabase/migrations/`. LGPD compliance column -- critical for enterprise. |
| **MISSED-03** (test masks T1-04 bug) | **AGREE** | Verified: `backend/tests/test_trial_usage_stats.py` lines 70, 79, 151, 188 all mock `user_pipeline`. Test fix must accompany T1-04 code fix. |
| **MISSED-04** (trigger lacks ON CONFLICT) | **AGREE -- Bundled with T2-04** | Covered by the proposed T2-04 fix which includes `ON CONFLICT (id) DO NOTHING`. |
| **CHECK constraints** for `subscription_status` columns | **AGREE** | DB-AUDIT.md proposed CHECK constraints that were omitted from DRAFT migration. Should be added for data integrity. Low risk -- values are already constrained in application code. |
| **Separate migration files** vs one consolidated | **AGREE** | Smaller blast radius is worth the extra files. Particularly: trigger rewrite (T2-04) must be deployed after missing columns exist. JSONB constraint (T2-03) needs production data verification first. |

### UX Specialist (@ux-design-expert) Adjustments

| Adjustment | QA Verdict | Reasoning |
|------------|-----------|-----------|
| **T3-F15 escalation** to Tier 2 (404 accents) | **AGREE** | Verified: `frontend/app/not-found.tsx` line 19 reads "Pagina nao encontrada" -- missing accents on `a`, `~`, and other Portuguese characters. 5-minute fix. For a Brazilian B2G enterprise product, this is mandatory polish. |
| **T3-F07 escalation** to Tier 2 (global-error.tsx) | **AGREE** | Verified: `frontend/app/global-error.tsx` uses hardcoded `backgroundColor: "#f9fafb"`, `fontFamily: "system-ui"`, no dark mode support. Visually disconnected from rest of product. Rare trigger but high perception impact. |
| **T3-F17 escalation** to Tier 2 (error boundaries for 4 pages) | **AGREE** | Verified: only `buscar/error.tsx`, `dashboard/error.tsx`, `admin/error.tsx` exist. Missing: `/pipeline`, `/historico`, `/mensagens`, `/conta`. These pages fall through to root `error.tsx` which exposes raw `error.message` in monospace. |
| **NEW-1** (filter error.message through getUserFriendlyError) | **AGREE -- Add to Tier 2** | Verified: all 4 error boundary files render `{error.message}` directly. The `getUserFriendlyError()` function exists in `frontend/lib/error-messages.ts` and is already used in 27 files across the codebase -- but NOT in error boundaries. This is the single most impactful UX fix for enterprise perception. |
| **T3-F14 stays Tier 3** (custom toast in FeedbackButtons) | **AGREE** | Low perception impact. The custom toast works. |
| **T3-F21 stays Tier 3** (inconsistent dates) | **AGREE** | Users unlikely to notice formatting differences. |

---

## 2. Gaps Identified

### GAP-01: No Monitoring/Alerting for Migration Drift (Cross-Area)

**Missing from assessment:** There is no mechanism to detect when a column exists in production code but not in migrations. The 5 missing columns (T1-01, T1-02, T1-03, MISSED-01, MISSED-02) were all added via Supabase Dashboard. The `schema_contract.py` module validates schema at startup but was not assessed for completeness. Without a CI check or startup validation that compares code-referenced columns against migration-derived schema, this class of bug will recur every time someone adds a column via Dashboard.

**Recommendation:** Add as Tier 3 item -- create a CI step that runs `schema_contract.py` validation against a fresh-from-migrations database schema (can be done as a Docker compose step in CI).

### GAP-02: Stripe Webhook Idempotency Under Concurrent Delivery (Cross-Area)

**Missing from assessment:** While the DRAFT mentions `stripe_webhook_events` for event dedup, neither specialist assessed whether the webhook handler correctly handles concurrent delivery of the same event. Stripe can send the same webhook event multiple times within seconds. The `stripe_webhook_events` table has a UNIQUE constraint on `event_id`, but the code path in `webhooks/stripe.py` needs verification that it catches the unique violation gracefully rather than returning a 500 error (which causes Stripe to retry, creating a retry storm).

**Recommendation:** Add as Tier 3 item -- verify webhook idempotency under concurrent delivery. Not blocking for monetization (Stripe retries gracefully) but important for enterprise reliability.

### GAP-03: No Load Testing Results Referenced

**Missing from assessment:** The system architecture documents `locustfile.py` exists but no load testing results were referenced in any assessment document. For enterprise monetization, the core search flow should be validated under expected load (e.g., 10 concurrent searches). The Railway 120s hard timeout combined with multi-UF searches is the most likely production failure mode under load.

**Recommendation:** Add as Tier 3 item -- run locust test against staging before enterprise launch. Not blocking for initial monetization but needed before scaling.

### GAP-04: Email Delivery Verification

**Missing from assessment:** The email service (`email_service.py`) sends transactional emails via Resend for welcome, quota warnings, and trial reminders. The MISSED-02 finding (`email_unsubscribed` column missing from migrations) means the email opt-out flow has no migration backing. Beyond that, no specialist assessed whether Resend is properly configured with SPF/DKIM for the `smartlic.tech` domain. Enterprise customers receiving emails from an unverified domain may have them land in spam.

**Recommendation:** Verify Resend domain configuration as part of pre-launch checklist. Not a code issue but an operational gap.

### GAP-05: Frontend LocalStorage Plan Cache Staleness (Cross-Area)

**Missing from assessment:** The CLAUDE.md mentions "Frontend localStorage plan cache (1hr TTL) prevents UI downgrades." The `usePlan` hook caches plan info in localStorage with a 1-hour TTL. If a Stripe webhook updates the backend plan but the frontend has a cached stale plan, the user sees their old plan for up to 1 hour. For enterprise billing, this could mean a user who just subscribed still sees "free_trial" in the UI. Neither specialist assessed this cache invalidation gap.

**Recommendation:** Add as Tier 3 item -- reduce localStorage plan cache TTL to 5 minutes, or add cache-busting after checkout redirect. Low severity (user can refresh) but surprising for enterprise.

---

## 3. Cross-Area Risk Matrix

| Risk | Areas Affected | Impact on Core | Mitigation |
|------|---------------|----------------|------------|
| **Missing DB columns + Backend code using them** (T1-01/02/03 + MISSED-01/02) | Database + Backend | On fresh DB: Stripe webhooks fail silently, `/me` returns incomplete data, analytics endpoint crashes, subscription cancel loses `end_date`, email unsubscribe writes to void. **In production today: functional** (columns exist via Dashboard). Risk is disaster recovery only. | Single migration with `ADD COLUMN IF NOT EXISTS` for all 5 columns. Zero risk -- idempotent. |
| **Trigger regression + Onboarding flow** (T2-04 + Frontend onboarding) | Database + Backend + Frontend | New users sign up, trigger creates profile with NULL `company`, `sector`, `context_data`. Onboarding page (`/onboarding/page.tsx` line 491) reads `context_data` -- gets NULL. User completes onboarding, data is written via API (not trigger). **Net effect:** Onboarding data collected POST-signup works; signup metadata is silently discarded. Users who filled company/sector on signup form see them missing on their profile. | T2-04 fix (trigger rewrite). Must test: email signup with metadata, Google OAuth signup, onboarding completion. |
| **Trigger regression + Trigger lacks ON CONFLICT + Edge-case re-signup** (T2-04 + MISSED-04) | Database + Auth | If user's auth.users row is recreated (e.g., after account deletion/recreation), the trigger's INSERT without ON CONFLICT throws a unique violation. This **blocks the user from signing up entirely** -- the Supabase auth INSERT fails. | T2-04 fix includes `ON CONFLICT (id) DO NOTHING`. |
| **RLS gaps + Enterprise customer data** (T2-05 + T2-07 + T2-08) | Database + Security | T2-05: Any authenticated user can inject fake state transition records (audit log pollution). T2-07/T2-08: service_role bypasses RLS so no current data exposure. **Real risk is low** -- service_role bypass means these are defense-in-depth. No actual data leakage path exists today. | Apply RLS policy fixes in Tier 2 migration. |
| **Raw error.message exposure + Error boundary gaps** (NEW-1 + T3-F17) | Frontend + UX | When any unhandled React error occurs on `/pipeline`, `/historico`, `/mensagens`, or `/conta`, user sees raw JavaScript error (e.g., `TypeError: Cannot read properties...`). On pages WITH error boundaries, the raw message is still shown in a monospace block. **Enterprise perception risk** -- decision-maker loses confidence. | Add error boundaries for 4 pages + filter error.message through `getUserFriendlyError()` in all existing boundaries. |
| **Trial stats runtime error + Frontend trial display** (T1-04) | Backend + Frontend | `services/trial_stats.py` line 78 queries non-existent `user_pipeline` table. Backend returns error. Frontend pipeline page's trial value metric shows error or empty. **Affects every trial user** trying to see their pipeline value. | 1-line code fix: `user_pipeline` -> `pipeline_items`. Also fix test file. |
| **FK to auth.users + User deletion** (T2-01/02) | Database | If admin deletes a user profile without deleting auth.users (or vice versa), `pipeline_items`, `classification_feedback`, and `trial_email_log` can have orphaned rows because FK points to wrong table. **Low probability** (current code always deletes via auth which cascades). | Repoint FKs to `profiles(id) ON DELETE CASCADE`. Check for orphaned data before applying. |

---

## 4. Enterprise Readiness per Flow

| Flow | Ready After T1+T2 Fixes? | Remaining Risks | Test Coverage |
|------|--------------------------|-----------------|---------------|
| **Search (end-to-end)** | YES | In-memory `_active_trackers` limits to 1 web instance (T3-S03). Railway 120s timeout for large multi-UF searches. Both are accepted Tier 3 items. | 169 backend test files + 60 E2E tests + SSE progress tests. Search pipeline well-covered. |
| **Billing/Subscription** | YES | After T1-01, T1-03, MISSED-01: all Stripe webhook paths write to correct columns. `subscription_end_date` persisted on cancel. LocalStorage plan cache can show stale plan for up to 1hr (GAP-05, Tier 3). | Stripe webhook tests exist. Need manual verification of checkout -> webhook -> profile update flow post-migration. |
| **Auth + Onboarding** | YES | After T2-04: trigger populates all fields + ON CONFLICT guard. Signup metadata propagated. Google OAuth flow needs manual testing. | Auth tests exist. Must manually test: email signup with company/sector, Google OAuth, re-signup edge case. |
| **Pipeline (Kanban)** | YES | After T1-04: trial stats query fixed. Pipeline CRUD and drag-and-drop functional. Missing per-page error boundary (T3-F17, escalated to Tier 2). | Pipeline unit tests + DnD tests exist. Trial stats test needs update (MISSED-03). |
| **Reporting (Excel + AI summary)** | YES | No blocking or stability issues identified. ARQ background jobs handle LLM + Excel generation. Fallback summary works. | Excel generation tests exist. LLM mock tests exist. |
| **Dashboard/Analytics** | YES | After T1-02: `trial_expires_at` column exists for analytics queries. Dashboard has its own error boundary (good). Fully CSR with loading waterfall (accepted Tier 3). | Analytics endpoint tests exist. |

**Assessment:** All 6 core flows will be enterprise-ready after Tier 1 + Tier 2 fixes are applied. No flow has a remaining blocker after the proposed fixes.

---

## 5. Test Requirements for Tier 1

| ID | Item | Test Required | Acceptance Criteria | Regression Risks |
|----|------|--------------|---------------------|------------------|
| T1-01 | `profiles.subscription_status` migration | 1. Run migration on test DB. 2. Verify column exists with DEFAULT 'trial'. 3. Run `pytest tests/test_api_me.py` -- verify `/me` returns `subscription_status`. 4. Run `pytest tests/test_stripe_webhooks.py` -- verify webhook writes `subscription_status`. | Column exists after migration. All existing backend tests pass. `/me` endpoint returns `subscription_status` field. | Migration is `ADD COLUMN IF NOT EXISTS` -- zero regression risk on existing production. New CHECK constraint could reject unexpected values if code writes unlisted status. |
| T1-02 | `profiles.trial_expires_at` migration | 1. Run migration on test DB. 2. Verify column exists as TIMESTAMPTZ. 3. Run `pytest tests/ -k "analytics"` -- verify analytics endpoint reads `trial_expires_at`. | Column exists after migration. Analytics tests pass. | Zero regression risk (additive only). |
| T1-03 | `user_subscriptions.subscription_status` migration | 1. Run migration on test DB. 2. Verify column exists with DEFAULT 'active'. 3. Run `pytest tests/test_stripe_webhooks.py` -- verify checkout creates subscription with `subscription_status`. | Column exists. Stripe webhook test passes for checkout + payment failure. | Zero regression risk (additive only). |
| T1-04 | Fix `user_pipeline` -> `pipeline_items` | 1. Change `backend/services/trial_stats.py` line 78: `user_pipeline` -> `pipeline_items`. 2. Update `backend/tests/test_trial_usage_stats.py` lines 70, 79, 151, 188: change mock from `user_pipeline` to `pipeline_items`. 3. Run `pytest tests/test_trial_usage_stats.py -v`. 4. Run full backend suite. | All trial stats tests pass with correct table name. No test mocks `user_pipeline` anymore. | Low -- isolated to trial stats module. Ensure test mocks match production table name. |
| MISSED-01 | `profiles.subscription_end_date` migration | 1. Run migration. 2. Verify column exists as TIMESTAMPTZ. 3. Run `pytest tests/ -k "subscriptions"` -- verify cancel flow writes `subscription_end_date`. | Column exists. Subscription cancel test passes. | Zero regression risk (additive only). |
| MISSED-02 | `profiles.email_unsubscribed` + `email_unsubscribed_at` migration | 1. Run migration. 2. Verify `email_unsubscribed` exists as BOOLEAN DEFAULT FALSE. 3. Verify `email_unsubscribed_at` exists as TIMESTAMPTZ. 4. Run `pytest tests/test_email_triggers.py`. | Columns exist. Email tests pass. Pipeline SELECT of `email_unsubscribed` returns FALSE (not NULL) for existing users. | Existing profiles will have NULL for `email_unsubscribed` unless DEFAULT is applied. Must verify: does `ADD COLUMN ... DEFAULT FALSE` backfill existing rows? In PostgreSQL 11+, yes -- ADD COLUMN with DEFAULT does NOT rewrite the table but applies default on read. Safe. |

---

## 6. Test Requirements for Tier 2

| ID | Item | Test Required | Acceptance Criteria | Regression Risks |
|----|------|--------------|---------------------|------------------|
| T2-01/02 | FK standardization + ON DELETE CASCADE | 1. **Pre-check:** Query for orphaned `user_id` values in `pipeline_items`, `classification_feedback`, `trial_email_log` that have no matching `profiles.id`. 2. Apply migration. 3. Verify new FK constraints exist. 4. Test: delete a test user profile -> verify cascading deletion of pipeline_items, feedback, email_log. | Zero orphaned rows (or clean them before applying). FK constraints point to `profiles(id)`. CASCADE works on delete. | If orphaned data exists, FK creation fails. Must run orphan check before migration. Two-phase approach (`NOT VALID` then `VALIDATE`) recommended by DB specialist for large tables. |
| T2-03 | JSONB size constraint + pg_cron cleanup | 1. **Pre-check:** Run `SELECT max(octet_length(results::text)) FROM search_results_cache` on production. 2. If max < 1MB: add CHECK constraint. If max >= 1MB: clean or raise limit first. 3. Set up pg_cron cleanup job. 4. Verify: insert a 1.1MB JSONB blob -> fails. Insert a 500KB blob -> succeeds. | CHECK constraint active. pg_cron job scheduled. No existing data violates constraint. | CHECK constraint will reject inserts if search returns very large result sets. Must verify max current size before applying. This is data-dependent -- cannot be tested without production data. |
| T2-04 | `handle_new_user()` trigger rewrite | 1. Apply migration. 2. **Test email signup:** create user with `company`, `sector`, `whatsapp_consent` in metadata -> verify all fields propagated to `profiles`. 3. **Test Google OAuth signup:** create user via OAuth -> verify `full_name` and `avatar_url` propagated. 4. **Test ON CONFLICT:** attempt to create profile with existing `id` -> verify no error (DO NOTHING). 5. **Test phone normalization:** provide `+5511999998888` -> verify stored as `11999998888`. | All metadata fields present in profiles after signup. ON CONFLICT does not raise error. Phone normalization works correctly. | This replaces the production trigger. If the new trigger has a bug, ALL new signups fail. Must test thoroughly. Consider: deploy to staging first, test 3 signup methods (email, Google, magic link), then deploy to production. |
| T2-05 | State transitions INSERT policy scoping | 1. Apply migration. 2. Verify: authenticated user (not service_role) attempting INSERT into `search_state_transitions` -> rejected (RLS violation). 3. Verify: service_role INSERT still works. | Non-service-role INSERT rejected. Service_role INSERT succeeds. | If backend code somewhere uses anon/authenticated role (not service_role) to insert transitions, those inserts will break. Verify all insert paths use service_role. |
| T2-07 | Profiles service_role ALL policy | 1. Apply migration. 2. Verify policy exists. 3. Run backend tests that update/delete profiles. | Policy active. Existing tests pass. | Zero risk -- additive policy. service_role already bypasses RLS. |
| T2-08 | Conversations/messages service_role policies | 1. Apply migration. 2. Verify policies exist. 3. Run `pytest tests/ -k "messages"`. | Policies active. Message tests pass. | Zero risk -- additive. |
| T2-09 | Composite index on search_sessions | 1. Apply migration. 2. Verify index exists via `\d search_sessions`. 3. Run `EXPLAIN ANALYZE` on analytics query pattern. | Index exists. Query plans show index usage for `(user_id, status, created_at)` filters. | Index creation can briefly impact write performance. Deploy during low traffic. |
| T2-11 | BottomNav drawer focus trap | 1. Open mobile drawer. 2. Tab through all focusable elements -> verify focus cycles within drawer. 3. Press Escape -> verify drawer closes. 4. Verify: focus returns to trigger button after close. | Focus trapped within drawer. Escape closes drawer. Focus returns to trigger. | Ensure focus trap does not interfere with touch/swipe interactions on mobile. Test on actual mobile device or emulator. |
| T3-F15 (escalated) | 404 page Portuguese accents | 1. Navigate to `/nonexistent-page`. 2. Verify text reads "Pagina nao encontrada" with proper accents. | All Portuguese characters properly accented. | Zero regression risk -- string replacement only. |
| T3-F07 (escalated) | global-error.tsx brand alignment | 1. Trigger root layout error (can be simulated by temporarily throwing in root layout). 2. Verify: page uses brand colors, supports dark mode via media query, button matches brand-blue. | Visual match with rest of product in both light and dark mode. | Must ensure inline styles work without Tailwind/CSS imports (root layout has failed). |
| T3-F17 (escalated) | Error boundaries for 4 pages | 1. Add error boundaries to `/pipeline`, `/historico`, `/mensagens`, `/conta`. 2. For each: trigger an error (e.g., mock API failure). 3. Verify: user sees contextual Portuguese error message, NOT raw `error.message`. | Each page has its own error boundary. No raw error.message visible to users. | Copy existing pattern from `buscar/error.tsx`. Low risk. |
| NEW-1 (escalated) | Filter error.message through getUserFriendlyError | 1. In each of the 4 existing error boundary files, import and apply `getUserFriendlyError()`. 2. Trigger errors in each page. 3. Verify: displayed message is user-friendly Portuguese, NOT raw JavaScript error. | All error boundaries show friendly messages. `getUserFriendlyError` function covers common error types. | Must verify `getUserFriendlyError()` handles all error categories gracefully. Function already used in 27 files -- low risk of missing cases. |

---

## 7. Regression Risks

### High Regression Risk

| Change | What Could Break | Mitigation |
|--------|-----------------|------------|
| **T2-04 trigger rewrite** | If new trigger has syntax error or incorrect field mapping, ALL new user signups fail silently (profile not created) or loudly (auth INSERT fails). | Deploy to staging first. Test 3 signup methods. Keep rollback SQL ready: `CREATE OR REPLACE FUNCTION` with the current production version. |
| **T2-01/02 FK repointing** | If orphaned data exists in `pipeline_items`, `classification_feedback`, or `trial_email_log`, the new FK constraint creation fails and the entire migration transaction rolls back. | Run orphan data check BEFORE migration. Use `NOT VALID` + `VALIDATE` two-phase approach for safety. |
| **T2-03 JSONB CHECK constraint** | If any existing `search_results_cache` row exceeds the CHECK limit, the constraint cannot be added. Future large searches that produce >1MB results will fail to cache. | Query production for max JSONB size before applying. Consider 2MB limit instead of 1MB. Add application-level truncation before INSERT. |

### Medium Regression Risk

| Change | What Could Break | Mitigation |
|--------|-----------------|------------|
| **T2-05 INSERT policy scoping** | If any backend code path inserts state transitions using a non-service-role connection, those inserts will fail with RLS violation. | Grep codebase for all `search_state_transitions` INSERT paths. Verify all use `get_supabase()` (which returns service_role client). |
| **NEW-1 error.message filtering** | If `getUserFriendlyError()` returns an empty string or generic message for a specific error type, the user gets less information than before (though friendlier). | Review `getUserFriendlyError()` mapping for completeness. Add a development-mode toggle to show raw error alongside friendly message. |
| **CHECK constraints on subscription_status** | If code ever writes a status value not in the CHECK list, the DB write fails silently (Supabase may swallow the error) or raises an error. | Review all code paths that SET `subscription_status` to ensure values match CHECK list. Currently: `trial`, `active`, `canceling`, `past_due`, `expired` for profiles; `active`, `trialing`, `past_due`, `canceled`, `expired` for user_subscriptions. |

### Low Regression Risk

| Change | What Could Break | Mitigation |
|--------|-----------------|------------|
| T1-01/02/03 + MISSED-01/02 (column additions) | Nothing -- `ADD COLUMN IF NOT EXISTS` is idempotent and additive. | Standard migration testing. |
| T1-04 (table name fix) | Nothing if test is also updated -- but if test still mocks `user_pipeline`, it passes falsely. | Update test file simultaneously. Run with `-v` to verify correct table name in mock. |
| T2-07/08/09/12 (policies and indexes) | Nothing -- all additive. DROP POLICY IF EXISTS + CREATE POLICY is idempotent. | Standard migration testing. |
| T3-F15 (404 accents) | Nothing -- 2 string replacements. | Visual inspection. |

---

## 8. Consolidated Tier Summary (Post-Review)

### Final Tier 1 (BLOCKING) -- 7 items

| ID | Item | Area | Source |
|----|------|------|--------|
| T1-01 | `profiles.subscription_status` missing migration | DB | Original DRAFT |
| T1-02 | `profiles.trial_expires_at` missing migration | DB | Original DRAFT |
| T1-03 | `user_subscriptions.subscription_status` missing migration | DB | Original DRAFT |
| T1-04 | `trial_stats.py` references `user_pipeline` instead of `pipeline_items` + test fix | Backend | Original DRAFT |
| T1-05 (was MISSED-01) | `profiles.subscription_end_date` missing migration | DB | DB specialist review |
| T1-06 (was MISSED-02) | `profiles.email_unsubscribed` + `email_unsubscribed_at` missing migration | DB | DB specialist review |
| T1-07 (was T2-04) | `handle_new_user()` trigger regression -- drops 6 fields + no ON CONFLICT | DB | Escalated from Tier 2 |

### Final Tier 2 (STABILITY) -- 14 items

| ID | Item | Area | Source |
|----|------|------|--------|
| T2-01 | FK standardization to `profiles(id)` ON DELETE CASCADE (3 tables) | DB | Original DRAFT |
| T2-02 | `classification_feedback` FK ON DELETE CASCADE (bundled with T2-01) | DB | Original DRAFT |
| T2-03 | JSONB `results` blob size governance + pg_cron cleanup | DB | Original DRAFT |
| T2-05 | `search_state_transitions` INSERT policy scoping | DB | Original DRAFT |
| T2-07 | `profiles` service_role ALL policy | DB | Original DRAFT |
| T2-08 | `conversations`/`messages` service_role policies | DB | Original DRAFT |
| T2-09 | `search_sessions` composite index | DB | Original DRAFT |
| T2-11 | BottomNav drawer focus trap | Frontend | Original DRAFT |
| T2-13 | Dockerfile Python 3.11 vs pyproject.toml 3.12 mismatch | Backend | Original DRAFT |
| T2-14 | Hardcoded "BidIQ" User-Agent | Backend | Original DRAFT |
| T2-16 (was T3-F15) | 404 page missing Portuguese accents | Frontend | Escalated by UX specialist |
| T2-17 (was T3-F07) | `global-error.tsx` inline styles not matching brand | Frontend | Escalated by UX specialist |
| T2-18 (was T3-F17) | Missing error boundaries for pipeline, historico, mensagens, conta | Frontend | Escalated by UX specialist |
| T2-19 (was NEW-1) | Filter `error.message` through `getUserFriendlyError()` in all error boundaries | Frontend | Identified by UX specialist |

### Removed from Tier 2

| ID | Item | Reason |
|----|------|--------|
| T2-04 | `handle_new_user()` trigger | **Escalated to Tier 1** (T1-07) -- affects every new signup |
| T2-06 | `classification_feedback` admin policy convention | **Demoted to Tier 3** -- functional, convention only |
| T2-10 | GIN indexes on sectors/ufs arrays | **Demoted to Tier 3** -- no current DB-level array queries |
| T2-12 | `trial_email_log` explicit service_role policy | **Demoted to Tier 3** -- zero functional impact |
| T2-15 | `time.sleep(0.3)` in quota.py | **Removed** -- already fixed in codebase |

---

## 9. Execution Order Recommendation

### Phase 1: Immediate (Day 1 morning) -- ~2 hours

1. **Migration A:** All missing columns (T1-01 + T1-02 + T1-03 + T1-05 + T1-06)
   - Single migration: `ADD COLUMN IF NOT EXISTS` for 5 columns with CHECK constraints
   - Zero risk, idempotent
2. **Code fix B:** T1-04 + MISSED-03 (parallel with Migration A)
   - Fix `trial_stats.py` + `test_trial_usage_stats.py`
3. **Validation:** Full `pytest` run

### Phase 2: Critical trigger fix (Day 1 afternoon) -- ~2 hours

4. **Migration C:** T1-07 (`handle_new_user()` trigger rewrite)
   - Depends on Phase 1 (new columns must exist before trigger references them)
   - Requires manual signup testing (email, OAuth, re-signup edge case)

### Phase 3: Stability database (Day 2) -- ~4 hours

5. **Migration D:** T2-01/02 (FK standardization) -- after orphan data check
6. **Migration E:** T2-05 + T2-07 + T2-08 (RLS policies)
7. **Migration F:** T2-09 (composite index)
8. **Migration G:** T2-03 (JSONB governance) -- after production data size check

### Phase 4: Stability code (Day 2-3) -- ~6 hours

9. T2-13 (Dockerfile Python version alignment)
10. T2-14 (User-Agent string fix)
11. T2-16 (404 accents -- 5 minutes)
12. T2-17 (global-error.tsx brand alignment -- 30 minutes)
13. T2-18 (error boundaries for 4 pages -- 2 hours)
14. T2-19 (getUserFriendlyError in all error boundaries -- 1 hour)
15. T2-11 (BottomNav focus trap -- 1.5 hours)

**Total estimated effort:** ~14 hours (~2 working days) for all Tier 1 + Tier 2 items including testing.

---

## 10. Final Verdict

### APPROVED

**Rationale:** The technical debt assessment is comprehensive and actionable. The three assessment documents (DRAFT, DB specialist review, UX specialist review) together cover all 6 core flows required for enterprise monetization. The specialist reviews caught real issues (5 additional missing columns, 1 already-fixed item, correct tier adjustments) and provided actionable guidance.

**Conditions for proceeding to final assessment + story creation:**

1. **Incorporate all specialist adjustments validated above** into the final assessment document
2. **Expand Tier 1** to 7 items (adding MISSED-01, MISSED-02, escalating T2-04)
3. **Remove T2-15** (already fixed)
4. **Add the 5 gaps identified** (GAP-01 through GAP-05) as Tier 3 items in the backlog
5. **Add the 4 UX escalations** (T3-F15, T3-F07, T3-F17, NEW-1) to Tier 2
6. **Include CHECK constraints** for `subscription_status` columns as recommended by DB specialist
7. **Include test requirements** from Section 5 and 6 of this review as acceptance criteria in the stories
8. **Include regression risks** from Section 7 as warnings in relevant stories

**What is NOT blocking approval:**
- GAP-01 through GAP-05 are operational concerns, not assessment gaps. They are correctly Tier 3.
- Load testing (GAP-03) is important but does not block story creation.
- Stripe concurrent webhook handling (GAP-02) is edge-case behavior that does not block monetization.

**Bottom line:** The assessment identifies the right problems at the right severity levels. The combined Tier 1 + Tier 2 fixes (7 + 14 = 21 items) are achievable in 2 working days and will make SmartLic enterprise-ready for monetization across all 6 core flows. Proceed to final assessment consolidation and story creation.

---

*Reviewed by @qa during Phase 7 of SmartLic Brownfield Discovery.*
*Methodology: Independent verification of all specialist claims against source code, cross-area risk analysis, enterprise readiness assessment per core flow.*
