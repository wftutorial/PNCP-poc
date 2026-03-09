# SmartLic Database Audit Report

**Audit Date:** 2026-03-09
**Auditor:** @data-engineer (AIOS Brownfield Discovery Phase 2)
**Scope:** 76 migration files (66 Supabase + 10 backend), 27+ tables, 13+ functions, 70+ indexes
**Severity Scale:** CRITICAL > HIGH > MEDIUM > LOW > INFO

---

## Table of Contents

1. [Summary Dashboard](#summary-dashboard)
2. [CRITICAL Issues](#critical-issues)
3. [HIGH Issues](#high-issues)
4. [MEDIUM Issues](#medium-issues)
5. [LOW Issues](#low-issues)
6. [INFO / Recommendations](#info--recommendations)

---

## Summary Dashboard

| Severity | Count | Status |
|----------|-------|--------|
| CRITICAL | 2 | Needs immediate attention |
| HIGH | 8 | Should fix in next sprint |
| MEDIUM | 12 | Plan for upcoming release |
| LOW | 9 | Address when convenient |
| INFO | 6 | Best-practice recommendations |
| **Total** | **37** | |

### Previously Fixed Issues (for reference)

These were identified in earlier audits and resolved in recent DEBT migrations:

| ID | Issue | Fixed In |
|----|-------|----------|
| DB-013 | `partner_referrals.referred_user_id` NOT NULL vs ON DELETE SET NULL | `20260308100000_debt001` |
| DB-038 | Wrong table names in index migration | `20260308100000_debt001` |
| DB-012 | Duplicate `updated_at` trigger functions | `20260308100000_debt001` |
| DB-001 | `classification_feedback` auth.role() pattern | `20260308300000_debt009` |
| DB-002 | `health_checks/incidents` missing service_role policies | `20260308300000_debt009` |
| DB-014 | `plans.stripe_price_id` deprecated column | `20260309100000_debt017` (documented) |
| DB-034 | Cache cleanup trigger performance | `20260309100000_debt017` (short-circuit added) |
| DB-035 | Conversations correlated subquery | `20260309100000_debt017` (LEFT JOIN LATERAL) |

---

## CRITICAL Issues

### CRIT-01: FK Target Inconsistency — `auth.users` vs `profiles`

**Tables affected:** 12 of 27 tables reference user IDs

Some tables reference `auth.users(id)` directly, while others reference `profiles(id)`. Both work in practice because `profiles.id` = `auth.users.id`, but this creates an inconsistent contract:

| FK Target | Tables |
|-----------|--------|
| `auth.users(id)` | `monthly_quota`, `user_oauth_tokens`, `google_sheets_exports`, `classification_feedback`, `search_results_cache`, `search_results_store`, `pipeline_items`, `organizations`, `organization_members`, `trial_email_log`, `partner_referrals` |
| `profiles(id)` | `user_subscriptions`, `search_sessions`, `conversations`, `messages`, `alert_preferences`, `alerts` |

**Risk:** If `profiles` row creation fails (e.g., `handle_new_user()` trigger error), tables referencing `profiles(id)` will reject inserts while tables referencing `auth.users(id)` will succeed, causing partial state.

**Impact:** Data integrity risk during edge-case signup failures. Tables referencing `profiles(id)` with `ON DELETE CASCADE` will cascade differently than tables referencing `auth.users(id)`.

**Fix:** Standardize all user FKs to either `auth.users(id)` (safer, since auth.users is the source of truth) or `profiles(id)` (more consistent with app-layer expectations). Migration `20260304100000_fk_standardization_to_profiles.sql` and `20260225120000_standardize_fks_to_profiles.sql` attempted partial standardization but did not complete it.

**Effort:** Medium (requires careful migration with FK recreation)

---

### CRIT-02: `search_results_store` Missing ON DELETE CASCADE

The `search_results_store.user_id` FK references `auth.users(id)` without `ON DELETE CASCADE`:

```sql
user_id UUID NOT NULL REFERENCES auth.users(id)  -- no ON DELETE behavior specified
```

If a user account is deleted, their search results store entries will block the deletion (FK violation) or remain as orphaned rows depending on Supabase's handling.

**Impact:** User account deletion may fail or leave orphaned data.

**Fix:**
```sql
ALTER TABLE search_results_store
  DROP CONSTRAINT search_results_store_user_id_fkey,
  ADD CONSTRAINT search_results_store_user_id_fkey
    FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;
```

**Effort:** Low (single ALTER TABLE)

---

## HIGH Issues

### HIGH-01: `classification_feedback` Missing ON DELETE CASCADE

`classification_feedback.user_id` references `auth.users(id)` without cascade behavior:

```sql
user_id UUID NOT NULL REFERENCES auth.users(id)  -- no ON DELETE specified
```

**Impact:** Same as CRIT-02 -- user deletion blocked or orphaned feedback rows.

**Fix:** Add `ON DELETE CASCADE` to the FK constraint.

---

### HIGH-02: Duplicate/Redundant `updated_at` Trigger Functions

Despite DEBT-001 consolidating triggers to `set_updated_at()`, three tables still use their own dedicated trigger functions:

| Table | Function | Should Use |
|-------|----------|------------|
| `pipeline_items` | `update_pipeline_updated_at()` | `set_updated_at()` |
| `alert_preferences` | `update_alert_preferences_updated_at()` | `set_updated_at()` |
| `alerts` | `update_alerts_updated_at()` | `set_updated_at()` |

All three functions are identical (`NEW.updated_at = now(); RETURN NEW;`).

**Impact:** Code duplication. 4 identical functions exist when 1 would suffice.

**Fix:** Migrate triggers to use `set_updated_at()`, then drop the 3 redundant functions.

**Effort:** Low

---

### HIGH-03: `search_state_transitions` No FK Constraint

`search_state_transitions.search_id` has no FK to `search_sessions.search_id`. This is documented (DEBT-017/DB-050) as intentional because `search_sessions.search_id` is nullable and not unique. However, this means orphaned transition records can accumulate indefinitely.

**Impact:** Table grows unbounded for searches that never create a session record. No retention cleanup exists.

**Fix:** Add a pg_cron retention job to delete transitions older than 90 days:
```sql
SELECT cron.schedule('cleanup-old-transitions', '0 3 * * *',
  $$DELETE FROM search_state_transitions WHERE created_at < NOW() - INTERVAL '90 days'$$);
```

**Effort:** Low

---

### HIGH-04: `alert_preferences` Service Role Policy Uses `auth.role()`

The service role policy uses the older `auth.role() = 'service_role'` pattern instead of the standardized `TO service_role` pattern:

```sql
CREATE POLICY "Service role full access to alert preferences"
  ON alert_preferences FOR ALL
  USING (auth.role() = 'service_role');  -- OLD pattern
```

The `auth.role()` approach evaluates per-row and is less efficient. The DEBT-009 migration standardized `classification_feedback`, `health_checks`, and `incidents` but missed `alert_preferences`.

**Impact:** Minor performance cost on every query. Inconsistent with project convention.

**Fix:**
```sql
DROP POLICY "Service role full access to alert preferences" ON alert_preferences;
CREATE POLICY "service_role_all" ON alert_preferences
  FOR ALL TO service_role USING (true) WITH CHECK (true);
```

---

### HIGH-05: `organizations` and `organization_members` Service Role Uses `auth.role()`

Same issue as HIGH-04. Both tables use the old `auth.role() = 'service_role'` pattern:

```sql
-- organizations
USING (auth.role() = 'service_role');
-- organization_members
USING (auth.role() = 'service_role');
```

**Fix:** Replace with `TO service_role` pattern for both tables.

---

### HIGH-06: `partners` and `partner_referrals` Service Role Uses `auth.role()`

Same pattern issue:

```sql
CREATE POLICY partners_service_role ON partners
  FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY partner_referrals_service_role ON partner_referrals
  FOR ALL USING (auth.role() = 'service_role');
```

**Note:** Migration `20260304200000_rls_standardize_service_role.sql` may have addressed this. Verify in production.

---

### HIGH-07: `search_results_store` Service Role Uses `auth.role()`

```sql
CREATE POLICY "Service role full access" ON search_results_store
  FOR ALL USING (auth.role() = 'service_role');
```

**Fix:** Standardize to `TO service_role` pattern.

---

### HIGH-08: `health_checks` and `incidents` Missing Retention Jobs

Both tables accumulate data indefinitely:
- `health_checks`: Comment says "30-day retention" but no pg_cron job exists
- `incidents`: No retention policy documented

**Impact:** Unbounded table growth in production.

**Fix:** Add pg_cron jobs:
```sql
SELECT cron.schedule('cleanup-old-health-checks', '0 3 * * *',
  $$DELETE FROM health_checks WHERE checked_at < NOW() - INTERVAL '30 days'$$);

SELECT cron.schedule('cleanup-old-incidents', '0 3 1 * *',
  $$DELETE FROM incidents WHERE status = 'resolved' AND resolved_at < NOW() - INTERVAL '90 days'$$);
```

---

## MEDIUM Issues

### MED-01: Redundant Indexes

Several tables have redundant indexes that waste storage and slow writes:

| Table | Redundant Index | Covered By |
|-------|----------------|------------|
| `alert_preferences` | `idx_alert_preferences_user_id` | `alert_preferences_user_id_unique` (UNIQUE constraint) |
| `search_results_store` | `idx_search_results_store_user_id` | `idx_search_results_user` (same column) |
| `search_sessions` | `idx_search_sessions_user_id` | `idx_search_sessions_user` (same column) |
| `partners` | `idx_partners_slug` | UNIQUE constraint on `slug` |

**Impact:** Extra write overhead and storage for no query benefit.

**Fix:**
```sql
DROP INDEX IF EXISTS idx_alert_preferences_user_id;
DROP INDEX IF EXISTS idx_search_results_store_user_id;
DROP INDEX IF EXISTS idx_search_sessions_user_id;
DROP INDEX IF EXISTS idx_partners_slug;
```

---

### MED-02: `conversations` Missing Composite Index for Admin Inbox

Admin inbox queries filter by `status` + order by `last_message_at DESC`. Individual indexes exist but a composite would be more efficient:

**Fix:**
```sql
CREATE INDEX idx_conversations_status_last_msg ON conversations(status, last_message_at DESC);
```

---

### MED-03: `plans.stripe_price_id` Legacy Column Still In Use

The column is marked DEPRECATED (DEBT-017/DB-014) via SQL COMMENT, but `billing.py` still uses it as a fallback. This creates confusion about which column is authoritative.

**Impact:** Risk of stale data if the deprecated column falls out of sync with `stripe_price_id_monthly`.

**Fix:** Update `billing.py` to exclusively use `stripe_price_id_monthly` / `plan_billing_periods.stripe_price_id`, then DROP the legacy column.

---

### MED-04: `search_sessions.status` CHECK Constraint Mismatch

The CHECK constraint allows `cancelled` but the DEBT-017 comment documents valid transitions using `cancelled` (with double-l). However, the actual CHECK values include both patterns:
- CHECK: `created, processing, completed, failed, timed_out, cancelled`
- Status column added in `20260221100000` uses `consolidating` and `partial` in transition comments but these are NOT in the CHECK

**Impact:** State transitions documented in DEBT-017 comment include states (`consolidating`, `partial`) not allowed by the CHECK constraint.

**Fix:** Either add `consolidating` and `partial` to the CHECK constraint or update documentation to match actual constraint values.

---

### MED-05: `monthly_quota.user_id` References `auth.users` Not `profiles`

This table references `auth.users(id)` directly while logically it should follow the same pattern as other user tables. The `increment_quota_atomic()` function also uses `auth.users` reference.

**Impact:** Inconsistency (part of CRIT-01). No functional bug but breaks convention.

---

### MED-06: Missing `updated_at` on Several Tables

These tables lack `updated_at` columns, making change tracking impossible:

| Table | Issue |
|-------|-------|
| `search_state_transitions` | Append-only, so acceptable |
| `classification_feedback` | Has `created_at` only -- feedback cannot be edited? But UPDATE policy exists |
| `stripe_webhook_events` | Append-only, so acceptable |
| `trial_email_log` | Append-only, so acceptable |
| `alert_sent_items` | Append-only, so acceptable |
| `health_checks` | Append-only, so acceptable |
| `incidents` | Mutable (resolved_at updated) but no `updated_at` |
| `partners` | Mutable (status changes) but no `updated_at` |

**Fix (for mutable tables):**
```sql
ALTER TABLE incidents ADD COLUMN updated_at TIMESTAMPTZ DEFAULT now();
ALTER TABLE partners ADD COLUMN updated_at TIMESTAMPTZ DEFAULT now();
```

---

### MED-07: `search_results_cache` Duplicate Size Constraints

Two CHECK constraints enforce the same 2MB limit:
1. `chk_results_max_size` from `20260225150000_jsonb_storage_governance.sql`: `octet_length(results::text) <= 2097152`
2. (Potentially) the same constraint re-added in `20260304110000_search_results_store_hardening.sql` on `search_results_store`

For `search_results_cache`, only one CHECK should exist. Verify in production that there is no duplicate.

---

### MED-08: `partner_referrals` Missing ON DELETE CASCADE on `partner_id`

```sql
partner_id UUID NOT NULL REFERENCES partners(id)  -- no ON DELETE specified
```

If a partner is deleted, referral records will block the deletion.

**Fix:** Add `ON DELETE CASCADE` or `ON DELETE SET NULL` depending on business rules.

---

### MED-09: Naming Convention Inconsistencies

Trigger and function names follow multiple patterns:

| Pattern | Examples |
|---------|----------|
| `tr_` prefix | `tr_pipeline_items_updated_at`, `tr_organizations_updated_at` |
| `trg_` prefix | `trg_update_conversation_last_message`, `trg_cleanup_search_cache` |
| `trigger_` prefix | `trigger_alerts_updated_at`, `trigger_alert_preferences_updated_at` |
| No prefix | `profiles_updated_at`, `plans_updated_at` |

DEBT-017/DB-020 documented the naming convention but it was not retroactively applied.

**Fix:** Standardize to a single prefix (`trg_` is most common in the codebase). Low priority since names don't affect functionality.

---

### MED-10: `google_sheets_exports` Using `last_updated_at` Instead of `updated_at`

Every other table uses `updated_at` but this table uses `last_updated_at`. No `set_updated_at()` trigger is attached.

**Impact:** Inconsistent naming. Column must be updated manually by application code.

**Fix:** Rename to `updated_at` and add trigger, or document the exception.

---

### MED-11: `organizations.plan_type` Has No CHECK Constraint

The column defaults to `'consultoria'` but accepts any text value. Should be constrained to valid plan types.

**Fix:**
```sql
ALTER TABLE organizations ADD CONSTRAINT chk_organizations_plan_type
  CHECK (plan_type IN ('consultoria', 'smartlic_pro', 'master'));
```

---

### MED-12: `pipeline_items` Service Role Policy Originally Overly Permissive

Migration 025 created the policy as `FOR ALL USING (true)` without `TO service_role`, allowing any authenticated user to bypass per-operation policies. This was **fixed in migration 027**, but the pattern should be verified in production.

---

## LOW Issues

### LOW-01: `user_oauth_tokens.provider` Overly Broad CHECK

The CHECK allows `google, microsoft, dropbox` but only Google is implemented. Dead values in constraint.

**Impact:** No functional issue, but misleading schema documentation.

**Fix:** Tighten to `CHECK (provider = 'google')` and expand when needed.

---

### LOW-02: `audit_events` No Index on `details` JSONB

If future queries need to filter by `details` content (e.g., event subtype), a GIN index would be needed.

**Impact:** None currently. Future-proofing concern only.

---

### LOW-03: `search_results_cache` Has 8 Indexes

The table has accumulated indexes across 5+ migrations:
- `idx_search_cache_user`
- `idx_search_cache_params_hash`
- `idx_search_cache_global_hash`
- `idx_search_cache_degraded`
- `idx_search_cache_priority`
- `idx_search_cache_fetched_at`
- Plus UNIQUE constraint index and PK

**Impact:** Write amplification on INSERT/UPDATE. The cleanup trigger fires on every INSERT, compounding the overhead.

**Fix:** Profile actual query patterns and remove unused indexes. `idx_search_cache_params_hash` may be redundant with the UNIQUE index on `(user_id, params_hash)`.

---

### LOW-04: `search_sessions` Accumulating Without Retention

No retention policy exists for old search sessions. Over time, this table will grow unbounded.

**Fix:** Add pg_cron job to archive or delete sessions older than 12 months (matching `audit_events` retention):
```sql
SELECT cron.schedule('cleanup-old-sessions', '0 4 2 * *',
  $$DELETE FROM search_sessions WHERE created_at < NOW() - INTERVAL '12 months'$$);
```

---

### LOW-05: `classification_feedback` Accumulating Without Retention

Same unbounded growth concern. No cleanup strategy documented.

---

### LOW-06: `conversations` and `messages` No Retention Policy

Support conversations accumulate indefinitely. Consider archiving resolved conversations older than 24 months.

---

### LOW-07: `alert_sent_items` Missing Retention

Dedup records accumulate for every alert sent. Over time with many active alerts, this table will grow significantly.

**Fix:** Add retention (e.g., 90 days) since items older than alert re-check window are no longer needed for dedup:
```sql
SELECT cron.schedule('cleanup-old-alert-sent-items', '0 5 * * 0',
  $$DELETE FROM alert_sent_items WHERE sent_at < NOW() - INTERVAL '90 days'$$);
```

---

### LOW-08: `stripe_webhook_events` No Automated Retention

Comment in migration says "Keep events for 90 days for compliance/debugging" but no pg_cron job was created.

**Fix:**
```sql
SELECT cron.schedule('cleanup-old-webhook-events', '0 4 * * *',
  $$DELETE FROM stripe_webhook_events WHERE processed_at < NOW() - INTERVAL '90 days'$$);
```

---

### LOW-09: `pipeline_items` Missing `search_id` Reference

Pipeline items snapshot bid data but don't link back to the search session that found them. This makes it impossible to trace which search led to a pipeline addition.

**Fix:** Consider adding an optional `search_id UUID` column.

---

## INFO / Recommendations

### INFO-01: Consolidate Backend Migrations

The `backend/migrations/` directory is now fully redundant after DEBT-002 bridge migration. Consider:
- Adding a `DEPRECATED` notice to `backend/migrations/README.md`
- Preventing CI from running backend migrations independently
- Eventually removing the directory

### INFO-02: Schema Versioning

No schema version table exists. Consider adding a `schema_version` table to track which migrations have been applied and when, independent of Supabase's internal tracking.

### INFO-03: Backup Strategy Documentation

No backup strategy is documented in the schema. Supabase provides automatic daily backups, but:
- Point-in-time recovery window should be documented
- Backup verification process should be established
- Cross-region backup should be considered for disaster recovery

### INFO-04: Connection Pooling

The schema does not account for connection pooling. With Railway backend + Supabase, connections should go through Supabase's built-in pgbouncer (port 6543) for transaction-mode pooling. Verify this is configured correctly.

### INFO-05: Consider Partitioning for High-Volume Tables

Tables that will grow significantly over time are candidates for partitioning:
- `search_state_transitions` (by `created_at` range)
- `audit_events` (by `timestamp` range)
- `alert_sent_items` (by `sent_at` range)

This is premature at current scale but should be planned when any table exceeds 10M rows.

### INFO-06: JSONB Column Schema Validation

Several tables use JSONB columns without database-level schema validation:
- `profiles.context_data`
- `alerts.filters`
- `search_results_cache.results`
- `search_results_cache.search_params`
- `health_checks.sources_json`
- `health_checks.components_json`

Application-level validation (Pydantic) handles this, but consider adding PostgreSQL CHECK constraints for critical JSONB fields if data corruption becomes a concern.

---

## Action Priority Matrix

### Immediate (This Sprint)

| ID | Issue | Effort | Impact |
|----|-------|--------|--------|
| CRIT-02 | `search_results_store` missing ON DELETE CASCADE | Low | Blocks user deletion |
| HIGH-01 | `classification_feedback` missing ON DELETE CASCADE | Low | Blocks user deletion |
| HIGH-03 | `search_state_transitions` retention job | Low | Unbounded growth |
| HIGH-08 | `health_checks`/`incidents` retention jobs | Low | Unbounded growth |
| LOW-08 | `stripe_webhook_events` retention job | Low | Unbounded growth |

### Next Sprint

| ID | Issue | Effort | Impact |
|----|-------|--------|--------|
| HIGH-04/05/06/07 | Standardize `auth.role()` to `TO service_role` | Low | Consistency + perf |
| HIGH-02 | Consolidate trigger functions | Low | Code cleanliness |
| MED-01 | Drop redundant indexes | Low | Write performance |
| MED-08 | `partner_referrals.partner_id` ON DELETE | Low | Data integrity |

### Planned

| ID | Issue | Effort | Impact |
|----|-------|--------|--------|
| CRIT-01 | FK target standardization | Medium | Architecture consistency |
| MED-03 | Remove `plans.stripe_price_id` legacy column | Medium | Code clarity |
| MED-04 | `search_sessions.status` CHECK alignment | Low | Documentation accuracy |
| MED-09 | Naming convention standardization | Low | Readability |
| MED-10 | `google_sheets_exports.last_updated_at` rename | Low | Convention |
| MED-11 | `organizations.plan_type` CHECK | Low | Data integrity |

### Low Priority / Future

| ID | Issue | Effort | Impact |
|----|-------|--------|--------|
| LOW-01 to LOW-09 | Various | Low-Medium | Maintenance |
| INFO-01 to INFO-06 | Recommendations | Varies | Best practices |
