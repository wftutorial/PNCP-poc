# SmartLic Database Audit Report

**Date:** 2026-03-21 | **Auditor:** @data-engineer (Delta)
**Scope:** All 85 Supabase migration files + 10 backend migration files + backend query patterns
**Rating:** CRITICAL (production risk) | HIGH (fix soon) | MEDIUM (improve when convenient) | LOW (nice to have)

---

## Executive Summary

The SmartLic database schema is **mature and well-maintained** for a POC-advanced (v0.5) product. After 85+ migrations, the schema has been through multiple hardening rounds (DEBT-001 through DEBT-120). Key strengths:

- All 27 tables have RLS enabled
- FK standardization to profiles(id) is complete (verified by DEBT-113 assertion)
- 15 pg_cron retention jobs cover all growing tables
- Service role policies consistently use `TO service_role` (no auth.role() patterns remain)
- Optimistic locking on pipeline_items and user_subscriptions

However, several structural debt items remain from rapid feature iteration, and the migration history itself introduces complexity. This audit identifies **19 debt items** across 6 categories.

---

## Category 1: Schema Design Issues

### DB-DEBT-001: profiles table has 20+ columns (wide table smell)
- **Severity:** MEDIUM
- **Description:** The profiles table serves as a catch-all for user data: auth fields, billing state (subscription_status, trial_expires_at, subscription_end_date), marketing preferences (whatsapp_consent, email_unsubscribed, marketing_emails_enabled), business context (context_data JSONB), and partner referral tracking. This violates SRP at the table level.
- **Impact:** Every profiles query pulls all columns. The handle_new_user() trigger must list all 10+ columns explicitly. Adding new user attributes further bloats the table.
- **Recommendation:** Consider extracting billing state into a dedicated `user_billing_state` view or materialized columns, and marketing preferences into `user_preferences`. For now, the profiles table works fine at POC scale.
- **Estimated effort:** 8-12 hours (including backend code changes)

### DB-DEBT-002: Dual subscription status tracking (profiles.subscription_status vs user_subscriptions.subscription_status)
- **Severity:** HIGH
- **Description:** Subscription status is stored in two places: `profiles.subscription_status` (CHECK: trial, active, canceling, past_due, expired) and `user_subscriptions.subscription_status` (CHECK: active, trialing, past_due, canceled, expired). The values are not identical (profiles uses "canceling" but user_subscriptions uses "canceled"; profiles uses "trial" but user_subscriptions uses "trialing"). The sync trigger (migration 017) was removed as dead code in migration 030.
- **Impact:** Status drift between the two columns. No trigger or application-level guarantee keeps them in sync. Billing decisions may use stale data from one source.
- **Recommendation:** Define one as the source of truth (user_subscriptions for Stripe-sourced state, profiles for app-visible state) and document the mapping. Add a CHECK constraint comment documenting the semantic difference, or unify the enum values.
- **Estimated effort:** 3-4 hours

### DB-DEBT-003: organizations.plan_type CHECK constraint is overly permissive
- **Severity:** LOW
- **Description:** The CHECK constraint on organizations.plan_type (added in DEBT-100) allows 13 different values including legacy ones (free, avulso, pack, monthly, annual). Organizations was only introduced for consultoria use cases and should only accept current plan types.
- **Impact:** No practical impact (organizations feature is not yet active in production), but it allows invalid data insertion.
- **Recommendation:** Tighten the CHECK to `('consultoria', 'smartlic_pro', 'master')` when the organizations feature ships.
- **Estimated effort:** 0.5 hours

### DB-DEBT-004: search_sessions has 24 columns (wide table)
- **Severity:** LOW
- **Description:** search_sessions combines search parameters (sectors, ufs, dates, keywords), search results (total_raw, total_filtered, valor_total, resumo_executivo), lifecycle state (status, error_message, pipeline_stage, duration_ms), and operational metadata (search_id, response_state, failed_ufs). This is a result of incremental additions across 4 migrations.
- **Impact:** Large row size. Historical queries that only need parameters or results still fetch lifecycle columns.
- **Recommendation:** Acceptable at current scale. If table grows past 1M rows, consider partitioning by created_at (range) or splitting results into a separate table.
- **Estimated effort:** 16+ hours (major refactor)

### DB-DEBT-005: pipeline_items.search_id is TEXT, search_sessions.search_id is UUID
- **Severity:** MEDIUM
- **Description:** pipeline_items.search_id was added as TEXT (DEBT-120), while search_sessions.search_id is UUID. This type mismatch prevents adding a proper FK constraint and causes implicit casts in join queries.
- **Impact:** No referential integrity between pipeline items and their originating search. Queries joining on search_id require explicit casting.
- **Recommendation:** Change pipeline_items.search_id to UUID, or document that it may contain non-UUID values from external sources.
- **Estimated effort:** 1-2 hours

---

## Category 2: Missing Indexes

### DB-DEBT-006: No index on conversations.user_id for RLS evaluation
- **Severity:** MEDIUM
- **Description:** The conversations table has `idx_conversations_user_id` created in migration 012. However, conversations RLS policy for users uses `auth.uid() = user_id` which benefits from this index. The index exists, so this is verified as NOT an issue. No action needed.
- **Status:** RESOLVED (verified present)

### DB-DEBT-007: No index on user_subscriptions for common billing query pattern
- **Severity:** MEDIUM
- **Description:** The billing code in `quota.py` and `billing.py` frequently queries `user_subscriptions WHERE user_id = X AND is_active = true ORDER BY created_at DESC LIMIT 1`. The existing `idx_user_subscriptions_active` covers `(user_id, is_active)` but does not include `created_at` for the ORDER BY.
- **Impact:** The ORDER BY created_at DESC requires a sort step after the index lookup. At current scale (low user count), this is negligible. At 10K+ active subscriptions, it could matter.
- **Recommendation:** Replace `idx_user_subscriptions_active` with `(user_id, is_active, created_at DESC) WHERE is_active = true`.
- **Estimated effort:** 0.5 hours

### DB-DEBT-008: No retention index on reconciliation_log
- **Severity:** LOW
- **Description:** reconciliation_log has `idx_reconciliation_log_run_at` for history queries but no pg_cron retention job. The table is admin-only and low-volume, so this is not urgent.
- **Impact:** Unbounded growth of reconciliation_log (though grows by at most ~30 rows/month).
- **Recommendation:** Add pg_cron job to clean entries older than 12 months.
- **Estimated effort:** 0.5 hours

---

## Category 3: RLS & Security

### DB-DEBT-009: trial_email_log has RLS enabled but NO policies
- **Severity:** MEDIUM
- **Description:** trial_email_log (migration 20260224100000) enables RLS but creates no policies at all. The comment says "service_role only (backend accesses via service key)" which is correct since service_role bypasses RLS. However, if any authenticated-role query accidentally targets this table, it will return empty results silently.
- **Impact:** No practical security risk (backend always uses service_role), but it violates the project pattern where every RLS-enabled table has an explicit `service_role_all` policy for clarity.
- **Recommendation:** Add `CREATE POLICY "service_role_all" ON trial_email_log FOR ALL TO service_role USING (true) WITH CHECK (true)` for consistency.
- **Estimated effort:** 0.5 hours

### DB-DEBT-010: handle_new_user() trigger runs as SECURITY DEFINER with phone uniqueness check
- **Severity:** MEDIUM
- **Description:** The handle_new_user() function (latest version from migration 20260225110000) runs as SECURITY DEFINER (bypasses RLS) and performs a `SELECT COUNT(*) FROM profiles WHERE phone_whatsapp = _phone` before insert. This SELECT-then-INSERT pattern has a TOCTOU race condition under concurrent signups with the same phone number.
- **Impact:** Two users could potentially sign up with the same phone number if requests arrive simultaneously. The partial UNIQUE index `idx_profiles_phone_whatsapp_unique` catches this at the constraint level, so the race condition would result in a constraint violation error (not silent duplicate).
- **Recommendation:** The UNIQUE index already provides the real safety net. The COUNT(*) check in the trigger is redundant defense-in-depth. Consider removing the check and relying solely on the UNIQUE constraint with proper error handling in the backend. The RAISE EXCEPTION currently masks the real constraint name.
- **Estimated effort:** 1 hour

### DB-DEBT-011: classification_feedback FK may still reference auth.users on fresh installs
- **Severity:** HIGH
- **Description:** The classification_feedback table was first created in DEBT-002 bridge migration (20260308200000) with `REFERENCES auth.users(id)`. DEBT-113 (20260311100000) detects and fixes this at runtime using a DO block. However, the original CREATE TABLE statement still references auth.users. If DEBT-113 fails or is skipped, the FK is wrong.
- **Impact:** On a disaster-recovery full replay of migrations, classification_feedback could end up with an auth.users FK instead of profiles(id).
- **Recommendation:** Edit the DEBT-002 bridge migration CREATE TABLE to reference profiles(id) directly (safe since DEBT-113 handles the runtime case). Or create a new migration that unconditionally replaces the FK.
- **Estimated effort:** 1 hour

---

## Category 4: Migration Health

### DB-DEBT-012: 85 migration files with complex dependency chains
- **Severity:** MEDIUM
- **Description:** The migration history spans 85 files with two naming conventions: sequential (`001_` to `033_`) and timestamped (`20260220...` to `20260315...`). Several migrations supersede earlier ones (e.g., 033 supersedes 027b). The handle_new_user() function has been redefined in **7 different migrations** (001, 007, 016, 024, 027, 20260224000000, 20260225110000). Some migrations reference constraints/indexes created by earlier migrations by exact name, creating fragile coupling.
- **Impact:** Full replay from scratch is risky. A developer running migrations on a fresh DB may encounter errors if ordering assumptions are violated. Understanding the "current state" requires reading all 85 files.
- **Recommendation:** Create a "squash migration" that represents the current state of the schema as a single idempotent SQL file. Keep it as `000_squashed_baseline.sql` alongside the incremental migrations. This does NOT replace the existing migrations -- it serves as documentation and disaster recovery baseline.
- **Estimated effort:** 4-6 hours

### DB-DEBT-013: backend/migrations/ directory is fully redundant
- **Severity:** LOW
- **Description:** The 10 files in `backend/migrations/` are all covered by Supabase migrations (confirmed by DEBT-002 bridge migration). The backend directory still exists and could confuse developers about which migration set to use.
- **Impact:** No functional impact. Confusion risk only.
- **Recommendation:** Add a `backend/migrations/README.md` stating "DEPRECATED: All migrations consolidated into supabase/migrations/ as of DEBT-002 (2026-03-08). Do not add new files here." Or remove the directory entirely.
- **Estimated effort:** 0.5 hours

### DB-DEBT-014: Production Stripe price IDs hardcoded in migrations
- **Severity:** MEDIUM
- **Description:** Migrations 015, 029, 20260226120000, and 20260301300000 contain production Stripe price IDs (e.g., `price_1T54vN9FhmvPslGYgfTGIAzV`). Migration 021 documents this issue but no fix was implemented. Running these migrations against a staging/development environment will point to production Stripe prices.
- **Impact:** Development/staging environments could accidentally create real Stripe subscriptions with production prices. A developer would need to manually UPDATE the price IDs after running migrations.
- **Recommendation:** Move Stripe price IDs to environment variables or a separate configuration table. The plan_billing_periods table is already the source of truth -- seed it from env vars in a deployment script rather than hardcoding in migrations.
- **Estimated effort:** 3-4 hours

---

## Category 5: Data Integrity

### DB-DEBT-015: No FK between search_state_transitions.search_id and search_sessions.search_id
- **Severity:** LOW
- **Description:** Documented in DEBT-017/DB-050: search_sessions.search_id is nullable and not UNIQUE (retries share IDs), so a FK constraint is impossible. Orphan cleanup relies on pg_cron retention (30 days for transitions, 12 months for sessions).
- **Impact:** Orphan transitions accumulate between the 30-day and 12-month cleanup windows. No data corruption risk, just unnecessary rows.
- **Recommendation:** Acceptable. The pg_cron retention job at 30 days handles cleanup adequately. Documented as intentional.
- **Estimated effort:** 0 hours (accepted)

### DB-DEBT-016: plans table has inactive/legacy rows that cannot be deleted
- **Severity:** LOW
- **Description:** The user_subscriptions.plan_id FK uses ON DELETE RESTRICT (documented as intentional in migration 022). This means legacy plans (free, pack_5, pack_10, pack_20, monthly, annual, consultor_agil, maquina, sala_guerra) cannot be deleted even though they are inactive. They will remain in the plans table forever.
- **Impact:** Plans table bloat (12 rows instead of 3). Any `SELECT * FROM plans` returns inactive plans that frontends must filter.
- **Recommendation:** Acceptable. The `is_active = false` filter works correctly. Adding a `WHERE is_active = true` to the public RLS SELECT policy would prevent inactive plans from being returned to anonymous/authenticated users.
- **Estimated effort:** 0.5 hours (if RLS filter added)

### DB-DEBT-017: No CHECK constraint on search_sessions.error_code
- **Severity:** LOW
- **Description:** The error_code column on search_sessions (added in 20260221100000) accepts any text. The COMMENT documents valid values (sources_unavailable, timeout, filter_error, llm_error, db_error, quota_exceeded, unknown) but there is no CHECK constraint enforcing them.
- **Impact:** Inconsistent error codes could be stored. Analytics queries that GROUP BY error_code may show unexpected values.
- **Recommendation:** Add CHECK constraint matching the documented values. Also add CHECK for response_state (live, cached, degraded, empty_failure) and pipeline_stage.
- **Estimated effort:** 1 hour

---

## Category 6: Performance Concerns

### DB-DEBT-018: JSONB columns without size governance on several tables
- **Severity:** MEDIUM
- **Description:** While search_results_cache and search_results_store have 2MB CHECK constraints on their JSONB results columns, other JSONB columns have no size limits: audit_events.details, stripe_webhook_events.payload, classification_feedback (no JSONB but bid_objeto is unbounded TEXT), alert_preferences (no JSONB issue), alerts.filters, and search_sessions.resumo_executivo (TEXT, could be very long from LLM output).
- **Impact:** A malicious or buggy API call could insert very large JSONB/TEXT values, causing storage bloat and slow queries.
- **Recommendation:** Add CHECK constraints on: stripe_webhook_events.payload (< 256KB), audit_events.details (< 64KB), alerts.filters (< 16KB). For search_sessions.resumo_executivo, add a 50KB limit. Backend validation is the primary defense but DB-level constraints provide defense-in-depth.
- **Estimated effort:** 2 hours

### DB-DEBT-019: pg_cron job scheduling collision at 4:00 UTC
- **Severity:** LOW
- **Description:** Two pg_cron jobs run at exactly 4:00 UTC daily: `cleanup-search-state-transitions` and `cleanup-expired-search-results`. The DEBT-009 migration intentionally staggers jobs by 5-minute intervals (4:00, 4:05, 4:10, etc.) but these two overlap.
- **Impact:** Simultaneous DELETE queries could cause brief I/O contention. At current data volumes this is negligible.
- **Recommendation:** Reschedule `cleanup-expired-search-results` to 3:55 UTC to avoid collision.
- **Estimated effort:** 0.5 hours

---

## Summary Table

| ID | Severity | Category | Description | Effort |
|----|----------|----------|-------------|--------|
| DB-DEBT-001 | MEDIUM | Schema | profiles table too wide (20+ columns) | 8-12h |
| DB-DEBT-002 | HIGH | Schema | Dual subscription_status tracking | 3-4h |
| DB-DEBT-003 | LOW | Schema | organizations.plan_type overly permissive | 0.5h |
| DB-DEBT-004 | LOW | Schema | search_sessions too wide (24 columns) | 16+h |
| DB-DEBT-005 | MEDIUM | Schema | pipeline_items.search_id TEXT vs UUID type mismatch | 1-2h |
| DB-DEBT-007 | MEDIUM | Indexes | user_subscriptions missing created_at in active index | 0.5h |
| DB-DEBT-008 | LOW | Indexes | reconciliation_log no retention job | 0.5h |
| DB-DEBT-009 | MEDIUM | Security | trial_email_log RLS has no explicit policies | 0.5h |
| DB-DEBT-010 | MEDIUM | Security | handle_new_user TOCTOU race on phone check | 1h |
| DB-DEBT-011 | HIGH | Security | classification_feedback FK to auth.users on fresh install | 1h |
| DB-DEBT-012 | MEDIUM | Migrations | 85 migrations need squash baseline | 4-6h |
| DB-DEBT-013 | LOW | Migrations | backend/migrations/ fully redundant | 0.5h |
| DB-DEBT-014 | MEDIUM | Migrations | Stripe price IDs hardcoded in migrations | 3-4h |
| DB-DEBT-015 | LOW | Integrity | No FK on search_state_transitions.search_id | 0h |
| DB-DEBT-016 | LOW | Integrity | Legacy plans cannot be deleted | 0.5h |
| DB-DEBT-017 | LOW | Integrity | No CHECK on search_sessions.error_code | 1h |
| DB-DEBT-018 | MEDIUM | Performance | JSONB columns without size governance | 2h |
| DB-DEBT-019 | LOW | Performance | pg_cron scheduling collision at 4:00 UTC | 0.5h |

---

## Priority Recommendations

### Immediate (this sprint)
1. **DB-DEBT-002** (HIGH) -- Document or unify subscription_status semantics
2. **DB-DEBT-011** (HIGH) -- Fix classification_feedback FK for fresh installs

### Next sprint
3. **DB-DEBT-005** (MEDIUM) -- Fix pipeline_items.search_id type to UUID
4. **DB-DEBT-009** (MEDIUM) -- Add explicit service_role policy to trial_email_log
5. **DB-DEBT-014** (MEDIUM) -- Extract Stripe price IDs from migrations

### Backlog
6. **DB-DEBT-012** (MEDIUM) -- Create squash baseline migration
7. **DB-DEBT-018** (MEDIUM) -- Add JSONB size constraints
8. **DB-DEBT-007** (MEDIUM) -- Optimize user_subscriptions index
9. All LOW items

---

## Positive Findings

The following areas are **well-implemented** and deserve recognition:

1. **RLS coverage is 100%** -- All 27 public tables have RLS enabled with appropriate policies
2. **Service role standardization is complete** -- No `auth.role()` patterns remain (verified by DEBT-113 assertion)
3. **FK standardization to profiles(id)** -- All user_id FKs point to profiles(id) instead of auth.users(id)
4. **Comprehensive retention policies** -- 15 pg_cron jobs cover all growing tables with appropriate retention windows
5. **2MB JSONB constraints** -- Applied to the two highest-volume JSONB tables (search_results_cache, search_results_store)
6. **Optimistic locking** -- pipeline_items.version and user_subscriptions.version prevent lost updates
7. **Atomic quota operations** -- Three RPC functions (check_and_increment_quota, increment_quota_atomic, increment_quota_fallback_atomic) prevent race conditions
8. **Trigger consolidation** -- Single canonical `set_updated_at()` function used by 13+ tables (cleanup completed in DEBT-001)
9. **Audit trail** -- SHA-256 hashed PII in audit_events meets LGPD/GDPR requirements
10. **System account security** -- Cache warmer account banned until 2099, empty password, is_admin=false
