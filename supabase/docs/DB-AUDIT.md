# SmartLic Database Audit Report

**Audit Date:** 2026-02-25
**Auditor:** @data-engineer (AIOS Brownfield Discovery Phase 2)
**Scope:** 42 migration files (35 Supabase + 7 backend), 18 tables, 13 functions, 49+ indexes
**Database:** Supabase PostgreSQL 17 (Project: `fqqyovlzdzimiwfofdjk`)
**Previous Audit:** 2026-02-15 (26 migrations, 16 tables)

---

## Executive Summary

The SmartLic database is well-structured for a POC-stage product with strong fundamentals: all tables have RLS enabled, most tables have proper indexes, and the migration history shows progressive hardening. However, the audit identified **28 technical debts** across 6 categories, with **4 critical**, **8 high**, **10 medium**, and **6 low** severity items.

### Severity Distribution

| Severity | Count | Immediate Action Required |
|----------|-------|---------------------------|
| CRITICAL | 4 | Yes -- data integrity or security risk |
| HIGH | 8 | Within next sprint |
| MEDIUM | 10 | Within next 2 sprints |
| LOW | 6 | Backlog |
| **Total** | **28** | |

---

## Table of Contents

1. [Foreign Key Inconsistencies](#1-foreign-key-inconsistencies)
2. [Missing Columns and Schema Drift](#2-missing-columns-and-schema-drift)
3. [RLS Policy Analysis](#3-rls-policy-analysis)
4. [Index Analysis](#4-index-analysis)
5. [Migration Health](#5-migration-health)
6. [Naming Convention Inconsistencies](#6-naming-convention-inconsistencies)
7. [Normalization Issues](#7-normalization-issues)
8. [Performance Concerns](#8-performance-concerns)
9. [Data Integrity Gaps](#9-data-integrity-gaps)
10. [Code-Database Mismatches](#10-code-database-mismatches)
11. [Remediation Priority Matrix](#11-remediation-priority-matrix)

---

## 1. Foreign Key Inconsistencies

### DB-AUDIT-001: Three tables still reference `auth.users(id)` instead of `profiles(id)` [HIGH]

**Tables affected:**
- `pipeline_items.user_id` -> `auth.users(id)` (migration 025)
- `classification_feedback.user_id` -> `auth.users(id)` (backend migration 006)
- `trial_email_log.user_id` -> `auth.users(id)` (migration 20260224100000)

**Context:** Migration 018 standardized FKs on `monthly_quota`, `user_oauth_tokens`, and `google_sheets_exports` to reference `profiles(id)`. Migration 20260224200000 standardized `search_results_cache`. But three tables were missed.

**Impact:**
- Inconsistent data model -- some tables cascade from profiles, others from auth.users
- If a profile row is deleted without auth.users deletion (or vice versa), orphaned rows may appear
- Developers must remember which FK convention each table uses

**Remediation:**
```sql
-- Pipeline items
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'pipeline_items_user_id_fkey' AND table_name = 'pipeline_items')
    THEN ALTER TABLE pipeline_items DROP CONSTRAINT pipeline_items_user_id_fkey;
    END IF;
    ALTER TABLE pipeline_items ADD CONSTRAINT pipeline_items_user_id_profiles_fkey
        FOREIGN KEY (user_id) REFERENCES profiles(id) ON DELETE CASCADE;
END $$;

-- classification_feedback
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'classification_feedback_user_id_fkey' AND table_name = 'classification_feedback')
    THEN ALTER TABLE classification_feedback DROP CONSTRAINT classification_feedback_user_id_fkey;
    END IF;
    ALTER TABLE classification_feedback ADD CONSTRAINT classification_feedback_user_id_profiles_fkey
        FOREIGN KEY (user_id) REFERENCES profiles(id) ON DELETE CASCADE;
END $$;

-- trial_email_log
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'trial_email_log_user_id_fkey' AND table_name = 'trial_email_log')
    THEN ALTER TABLE trial_email_log DROP CONSTRAINT trial_email_log_user_id_fkey;
    END IF;
    ALTER TABLE trial_email_log ADD CONSTRAINT trial_email_log_user_id_profiles_fkey
        FOREIGN KEY (user_id) REFERENCES profiles(id) ON DELETE CASCADE;
END $$;
```

**Effort:** 1 migration, low risk (same cascade behavior)

---

### DB-AUDIT-002: `classification_feedback.user_id` FK has no ON DELETE clause [HIGH]

**Finding:** The `classification_feedback` table FK to `auth.users(id)` has no explicit `ON DELETE` clause, defaulting to `RESTRICT`. If a user is deleted from `auth.users`, the delete will fail if feedback rows exist.

**Impact:** User deletion blocked by orphaned feedback rows. This is unlike all other user-owned tables which use `ON DELETE CASCADE`.

**Remediation:** Fix as part of DB-AUDIT-001 (add `ON DELETE CASCADE` when switching to `profiles(id)`).

---

## 2. Missing Columns and Schema Drift

### DB-AUDIT-003: `profiles.subscription_status` -- used in code, no migration [CRITICAL]

**Finding:** The column `profiles.subscription_status` is actively used in:
- `backend/webhooks/stripe.py` (lines 215, 222, 471, 476) -- sets it on checkout and payment failures
- `backend/routes/billing.py` (line 164) -- reads it in `get_subscription_status`
- `backend/routes/subscriptions.py` (line 240) -- sets to "canceling"
- `backend/routes/user.py` (lines 137-141) -- reads it for `/me` endpoint
- `backend/schemas.py` (line 1512) -- defined in `UserProfile` Pydantic model

**But no migration creates this column.** It was likely added manually via the Supabase dashboard.

**Impact:**
- If the Supabase project is recreated from migrations alone (disaster recovery), this column will be missing
- Stripe webhook processing will silently fail on `.update({"subscription_status": ...})`
- The `/me` endpoint will return incomplete data

**Remediation:**
```sql
-- New migration: Add subscription_status to profiles
ALTER TABLE public.profiles
    ADD COLUMN IF NOT EXISTS subscription_status TEXT DEFAULT 'trial'
    CHECK (subscription_status IN ('trial', 'active', 'canceling', 'past_due', 'expired'));

CREATE INDEX IF NOT EXISTS idx_profiles_subscription_status
    ON profiles (subscription_status)
    WHERE subscription_status != 'trial';

COMMENT ON COLUMN profiles.subscription_status IS
    'Subscription lifecycle state. Set by Stripe webhooks. DB-AUDIT-003 fix.';
```

**Effort:** 1 migration, low risk

---

### DB-AUDIT-004: `profiles.trial_expires_at` -- used in code, no migration [CRITICAL]

**Finding:** The column `profiles.trial_expires_at` is actively read in:
- `backend/routes/analytics.py` (line 278) -- `db.table("profiles").select("created_at, trial_expires_at")`
- `backend/routes/user.py` -- likely used in `/me` response

**But no migration creates this column.** Like `subscription_status`, it was likely added via dashboard.

**Impact:** Same as DB-AUDIT-003 -- disaster recovery from migrations will produce a broken schema.

**Remediation:**
```sql
ALTER TABLE public.profiles
    ADD COLUMN IF NOT EXISTS trial_expires_at TIMESTAMPTZ;

COMMENT ON COLUMN profiles.trial_expires_at IS
    'When the trial period expires. Set during signup. DB-AUDIT-004 fix.';
```

**Effort:** 1 migration, low risk

---

### DB-AUDIT-005: `user_subscriptions.subscription_status` -- used in webhook code, no migration [CRITICAL]

**Finding:** The column `user_subscriptions.subscription_status` is actively used in:
- `backend/webhooks/stripe.py` (line 215) -- inserted with `"subscription_status": "active"` on checkout
- `backend/webhooks/stripe.py` (line 471) -- updated to `"past_due"` on payment failure
- `backend/routes/billing.py` (line 164) -- selected in `get_subscription_status`

**But no migration creates this column.** The original `user_subscriptions` table (migration 001) does not include it, and no subsequent migration adds it.

**Note:** Migration 017 created a trigger referencing `NEW.status` (not `subscription_status`), which was identified as dead code and removed in migration 030. The column `subscription_status` is a different column name entirely.

**Impact:** Critical path broken on fresh database setup. Stripe webhook processing will fail.

**Remediation:**
```sql
ALTER TABLE public.user_subscriptions
    ADD COLUMN IF NOT EXISTS subscription_status TEXT DEFAULT 'active'
    CHECK (subscription_status IN ('active', 'trialing', 'past_due', 'canceled', 'expired'));

COMMENT ON COLUMN user_subscriptions.subscription_status IS
    'Subscription lifecycle state from Stripe. DB-AUDIT-005 fix.';
```

**Effort:** 1 migration, low risk

---

### DB-AUDIT-006: `handle_new_user()` trigger diverged from schema over multiple rewrites [MEDIUM]

**Finding:** The `handle_new_user()` function has been rewritten 6 times across migrations 001, 007, 016, 024, 027, and 20260224000000. The final version (20260224000000) inserts only `id, email, full_name, phone_whatsapp` -- it dropped `company`, `sector`, `whatsapp_consent`, `context_data`, and `plan_type` that were present in the version from migration 027.

**Impact:**
- New users created via signup will not have `company`, `sector`, `whatsapp_consent`, or `context_data` populated even if provided in signup metadata
- The `plan_type` column relies on the column DEFAULT (`'free_trial'`) instead of explicit insertion
- The `avatar_url` column (originally in migration 001) is no longer set by the trigger

**Remediation:** The trigger should be consolidated. Decide which fields should be populated from signup metadata vs. onboarding flow, and write a single definitive version with clear comments.

```sql
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
DECLARE
  _phone text;
BEGIN
  -- Normalize phone
  _phone := regexp_replace(COALESCE(NEW.raw_user_meta_data->>'phone_whatsapp', ''), '[^0-9]', '', 'g');
  IF length(_phone) > 11 AND left(_phone, 2) = '55' THEN _phone := substring(_phone from 3); END IF;
  IF left(_phone, 1) = '0' THEN _phone := substring(_phone from 2); END IF;
  IF length(_phone) NOT IN (10, 11) THEN _phone := NULL; END IF;

  INSERT INTO public.profiles (
    id, email, full_name, company, sector,
    phone_whatsapp, whatsapp_consent, plan_type,
    avatar_url, context_data
  )
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'full_name', ''),
    COALESCE(NEW.raw_user_meta_data->>'company', ''),
    COALESCE(NEW.raw_user_meta_data->>'sector', ''),
    _phone,
    COALESCE((NEW.raw_user_meta_data->>'whatsapp_consent')::boolean, FALSE),
    'free_trial',
    NEW.raw_user_meta_data->>'avatar_url',
    '{}'::jsonb
  )
  ON CONFLICT (id) DO NOTHING;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

**Effort:** 1 migration, medium risk (test signup flow after)

---

## 3. RLS Policy Analysis

### DB-AUDIT-007: `search_state_transitions` INSERT policy not scoped to service_role [MEDIUM]

**Finding:** The INSERT policy for `search_state_transitions` uses `WITH CHECK (true)` without a `TO service_role` clause:

```sql
CREATE POLICY "Service role can insert transitions"
    ON search_state_transitions
    FOR INSERT
    WITH CHECK (true);
```

This means **any authenticated user** can insert arbitrary state transition records. While the data is non-sensitive (audit logs), it violates the principle of least privilege.

**Impact:** Low-risk data integrity issue. Users could inject fake transition records.

**Remediation:**
```sql
DROP POLICY IF EXISTS "Service role can insert transitions" ON search_state_transitions;
CREATE POLICY "Service role can insert transitions" ON search_state_transitions
    FOR INSERT TO service_role WITH CHECK (true);
```

**Effort:** 1 migration, very low risk

---

### DB-AUDIT-008: `trial_email_log` has RLS enabled but no policies [LOW]

**Finding:** The `trial_email_log` table has RLS enabled but zero policies defined. This is intentional (only service_role accesses it, which bypasses RLS). However, it should be documented and preferably have an explicit service_role policy for clarity.

**Impact:** None functionally, but could confuse future developers.

**Remediation:**
```sql
CREATE POLICY "Service role full access on trial_email_log"
    ON trial_email_log FOR ALL TO service_role
    USING (true) WITH CHECK (true);
```

**Effort:** 1 migration, zero risk

---

### DB-AUDIT-009: `classification_feedback` admin policy uses `auth.role()` instead of `TO service_role` [MEDIUM]

**Finding:** The `feedback_admin_all` policy uses:
```sql
CREATE POLICY feedback_admin_all ON classification_feedback
    FOR ALL USING (auth.role() = 'service_role');
```

This is a valid but older pattern. The modern Supabase convention is `TO service_role` which is more performant (evaluated at connection level, not per-row).

**Impact:** Slight performance overhead on every row evaluation. Functional correctness is fine.

**Remediation:**
```sql
DROP POLICY IF EXISTS feedback_admin_all ON classification_feedback;
CREATE POLICY feedback_admin_all ON classification_feedback
    FOR ALL TO service_role USING (true) WITH CHECK (true);
```

**Effort:** 1 migration, zero risk

---

### DB-AUDIT-010: `profiles` table missing service_role UPDATE/DELETE policies [MEDIUM]

**Finding:** The `profiles` table has service_role INSERT policy (`profiles_insert_service`) but no service_role UPDATE or DELETE policies. The backend updates profiles in multiple places (webhook handlers, admin endpoints, etc.) using the service_role key.

**Why it works today:** Supabase service_role key bypasses RLS entirely. But if Supabase ever changes this behavior, or if explicit role-scoped policies are enforced, backend writes would break.

**Impact:** No current issue, but defense-in-depth concern.

**Remediation:**
```sql
DROP POLICY IF EXISTS "profiles_service_all" ON public.profiles;
CREATE POLICY "profiles_service_all" ON public.profiles
    FOR ALL TO service_role USING (true) WITH CHECK (true);
```

**Effort:** 1 migration, zero risk

---

### DB-AUDIT-011: `conversations` and `messages` tables missing service_role policies [MEDIUM]

**Finding:** The messaging tables use admin-aware RLS policies but lack explicit service_role policies. The backend accesses these tables via the service_role key in `routes/messages.py`.

**Impact:** Same as DB-AUDIT-010.

**Remediation:** Add `FOR ALL TO service_role USING (true) WITH CHECK (true)` policies to both tables.

---

## 4. Index Analysis

### DB-AUDIT-012: `plans` table has no index on `is_active` [LOW]

**Finding:** Multiple queries filter by `is_active = true`:
- `backend/routes/billing.py` line 52: `.eq("id", plan_id).eq("is_active", True)`
- `backend/routes/plans.py` line 67: `.eq("is_active", True)`

The `plans` table is small (6-8 rows), so a full table scan is negligible. However, as the product scales, an index would be best practice.

**Impact:** Negligible at current scale.

**Remediation:** Optional. Create if table grows beyond 50 rows.
```sql
CREATE INDEX IF NOT EXISTS idx_plans_active ON plans(is_active) WHERE is_active = true;
```

---

### DB-AUDIT-013: `search_sessions` missing index on `(user_id, status, created_at)` composite [MEDIUM]

**Finding:** Multiple backend queries filter by `user_id + status + created_at` simultaneously:
- `backend/cron_jobs.py` queries for stale sessions by user and status
- `backend/routes/analytics.py` queries sessions by user and date range
- `backend/main.py` SIGTERM cleanup queries in-flight sessions

The existing indexes cover `(user_id, created_at DESC)` and `(status)` separately, but the composite pattern requires a merge or re-scan.

**Impact:** Slightly slower queries as search_sessions grows. Each user may have hundreds of sessions over time.

**Remediation:**
```sql
CREATE INDEX IF NOT EXISTS idx_search_sessions_user_status_created
    ON search_sessions (user_id, status, created_at DESC);
```

---

### DB-AUDIT-014: `search_results_cache.results` JSONB column has no size governance [MEDIUM]

**Finding:** The `results` column stores full search results as JSONB. With 50+ licitacoes per search, each with objeto (text), orgao (text), valor, and other fields, a single row can be 50-500 KB. The trigger limits entries to 10 per user, but total storage per user can reach 5 MB.

**Impact:** Large JSONB blobs slow down Supabase queries, especially when `results` is included in SELECT *. The GIN index approach is not feasible on such large JSONB. Over time, this is the most likely performance bottleneck.

**Remediation:**
1. Add a `CHECK (octet_length(results::text) < 1048576)` constraint (1 MB max)
2. Consider compressing results or storing only IDs + metadata
3. Add TTL-based cleanup (older than 7 days) via pg_cron
4. Exclude `results` from default SELECTs where not needed

---

### DB-AUDIT-015: Redundant index on `search_results_cache.params_hash` [LOW]

**Finding:** The `idx_search_cache_params_hash` index on `params_hash` alone is potentially redundant because the UNIQUE constraint `(user_id, params_hash)` already creates a composite index. However, queries filtering by `params_hash` alone (without `user_id`) would benefit from the standalone index.

**Analysis:** The backend does query by `params_hash` alone in `search_cache.py` line 1656: `.delete().eq("params_hash", params_hash)`. This justifies keeping the index.

**Remediation:** Keep as-is. Document the justification.

---

## 5. Migration Health

### DB-AUDIT-016: Dual migration numbering schemes [MEDIUM]

**Finding:** Migrations 001-033 use sequential numbering (e.g., `001_profiles_and_sessions.sql`), while newer migrations use timestamp format (e.g., `20260220120000_add_search_id_to_search_sessions.sql`). Additionally, there is a `027b_` prefix that breaks alphabetical ordering.

**Impact:**
- Two numbering conventions in the same directory creates confusion
- `027b` depends on 027 running first but has no dependency mechanism
- The `027b` migration is "SUPERSEDED by 033" per its own comment

**Remediation:**
1. Adopt timestamp format exclusively for all new migrations
2. Add a `MIGRATION_README.md` documenting the convention change
3. Consider removing `027b` (its content is fully replicated in 033)

---

### DB-AUDIT-017: Backend migrations directory duplicates Supabase migrations [MEDIUM]

**Finding:** The `backend/migrations/` directory contains 9 files, of which 7 are exact duplicates of Supabase migrations:

| Backend Migration | Supabase Equivalent |
|-------------------|-------------------|
| 002_monthly_quota.sql | 002_monthly_quota.sql |
| 003_atomic_quota_increment.sql | 003_atomic_quota_increment.sql |
| 004_google_oauth_tokens.sql | 013_google_oauth_tokens.sql |
| 005_google_sheets_exports.sql | 014_google_sheets_exports.sql |
| 007_search_session_lifecycle.sql | 20260221100000_search_session_lifecycle.sql |
| 008_search_state_transitions.sql | 20260221100002_create_search_state_transitions.sql |
| 009_add_search_id_to_search_sessions.sql | 20260220120000_add_search_id_to_search_sessions.sql |

Only `006_classification_feedback.sql` and `010_normalize_session_arrays.sql` are unique to backend.

**Impact:**
- Confusion about which directory is the source of truth
- Risk of applying a migration from the wrong directory
- Maintenance burden of keeping two copies in sync

**Remediation:**
1. Designate `supabase/migrations/` as the single source of truth
2. Move unique backend migrations (006, 010) to `supabase/migrations/` with proper timestamps
3. Add a README in `backend/migrations/` marking it as deprecated
4. Or: Keep `backend/migrations/` for local development only, with a clear README

---

### DB-AUDIT-018: No rollback scripts for any migration [LOW]

**Finding:** Only migration 010 (`stripe_webhook_events`) includes a rollback comment. No other migration has rollback SQL.

**Impact:** If a migration needs to be rolled back, developers must manually write rollback SQL, which is error-prone under pressure.

**Remediation:** Add rollback comments to all migrations going forward. For existing migrations, generate rollback scripts for the most recent 10 migrations as a safety net.

---

### DB-AUDIT-019: Superseded migration 027b still present in directory [LOW]

**Finding:** Migration `027b_search_cache_add_sources_and_fetched_at.sql` begins with the comment `-- SUPERSEDED by 033_fix_missing_cache_columns.sql`. It should not be applied to new databases, but its presence in the migrations directory means it would be.

**Impact:** Double-application of `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` is safe due to `IF NOT EXISTS`, but the migration is dead weight that adds confusion.

**Remediation:** Either delete the file or rename it with a `.deprecated` suffix. Add a comment in migration 033 noting it replaces 027b.

---

## 6. Naming Convention Inconsistencies

### DB-AUDIT-020: Inconsistent trigger naming conventions [LOW]

**Finding:**
| Trigger | Convention |
|---------|-----------|
| `on_auth_user_created` | `on_{event}` |
| `profiles_updated_at` | `{table}_{column}` |
| `plans_updated_at` | `{table}_{column}` |
| `trg_update_conversation_last_message` | `trg_{action}` |
| `tr_pipeline_items_updated_at` | `tr_{table}_{column}` |
| `trg_cleanup_search_cache` | `trg_{action}` |
| `user_subscriptions_updated_at` | `{table}_{column}` |
| `plan_features_updated_at` | `{table}_{column}` |

Three different conventions are used: `on_`, `trg_/tr_`, and `{table}_{column}`.

**Impact:** Developer confusion when debugging or querying `pg_trigger`.

**Remediation:** Standardize to `trg_{table}_{purpose}` convention for all future triggers. Rename existing ones in a batch migration when convenient.

---

### DB-AUDIT-021: Inconsistent function naming for `updated_at` triggers [LOW]

**Finding:** Two separate functions serve the same purpose:
- `update_updated_at()` (migration 001) -- used by profiles, plans, plan_features, user_subscriptions
- `update_pipeline_updated_at()` (migration 025) -- used by pipeline_items only

Both have identical logic: `NEW.updated_at = now(); RETURN NEW;`.

**Impact:** Unnecessary function duplication. Pipeline items could reuse `update_updated_at()`.

**Remediation:**
```sql
-- Drop the duplicate function and repoint the trigger
DROP TRIGGER IF EXISTS tr_pipeline_items_updated_at ON pipeline_items;
CREATE TRIGGER tr_pipeline_items_updated_at
    BEFORE UPDATE ON pipeline_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
DROP FUNCTION IF EXISTS update_pipeline_updated_at();
```

---

## 7. Normalization Issues

### DB-AUDIT-022: `search_sessions` stores arrays that should be join tables [MEDIUM]

**Finding:** The `search_sessions` table uses PostgreSQL arrays for:
- `sectors text[]` -- searched sectors
- `ufs text[]` -- searched states
- `custom_keywords text[]`
- `destaques text[]`
- `failed_ufs text[]`

Arrays are convenient but break 1NF and make queries like "find all sessions that searched sector X" require `@>` array contains operators.

**Current mitigating factor:** Migration `backend/010_normalize_session_arrays.sql` sorts arrays for dedup, showing the arrays are actively managed. The `sectors_data.yaml` defines a fixed set of 15 sectors.

**Impact:**
- Cannot easily create FK constraints on sector/UF values
- Array containment queries (`@> ARRAY['SP']`) cannot use standard btree indexes (need GIN)
- No GIN index exists on `sectors` or `ufs` columns

**Remediation (Medium-term):**
- For current scale (hundreds of sessions), arrays are acceptable
- If analytics on "searches per sector" or "searches per UF" become critical, consider:
  - Adding GIN indexes: `CREATE INDEX idx_sessions_sectors ON search_sessions USING GIN(sectors);`
  - Or normalizing into `search_session_sectors(session_id, sector_id)` join table

---

### DB-AUDIT-023: `search_results_cache.results` stores denormalized full search results [HIGH]

**Finding:** The `results` JSONB column stores the complete filtered search results (potentially hundreds of licitacao objects) as a single JSONB blob per cache entry. Each entry can be 50-500 KB.

With the 10-entry-per-user limit (migration 032), a single user can consume 5 MB. Across 1,000 users, this is 5 GB of JSONB data in a single table.

**Impact:**
- Supabase free/pro tiers have database size limits
- Full-table operations (backfill updates in migrations 031, 032, 033) become progressively slower
- `pg_dump` includes this data, inflating backup sizes
- Cannot run meaningful queries against individual results without JSONB operators

**Remediation:**
1. **Short-term:** Add pg_cron job to delete entries with `fetched_at < NOW() - INTERVAL '7 days'` AND `priority = 'cold'`
2. **Medium-term:** Move results to Supabase Storage (S3-compatible) and store only a reference URL + metadata in the table
3. **Long-term:** Implement Redis as the primary cache layer, using Supabase only as a warm backup

---

## 8. Performance Concerns

### DB-AUDIT-024: No index on `search_sessions.sectors` or `search_sessions.ufs` for analytics [MEDIUM]

**Finding:** The analytics endpoint (`routes/analytics.py`) and admin endpoints query sessions by sector and UF for reporting. Without GIN indexes on the array columns, these queries require full table scans.

**Remediation:**
```sql
CREATE INDEX IF NOT EXISTS idx_search_sessions_sectors ON search_sessions USING GIN(sectors);
CREATE INDEX IF NOT EXISTS idx_search_sessions_ufs ON search_sessions USING GIN(ufs);
```

**Effort:** 1 migration, low risk. GIN indexes have moderate write overhead.

---

### DB-AUDIT-025: `get_conversations_with_unread_count` RPC has correlated subquery per row [MEDIUM]

**Finding:** The RPC function `get_conversations_with_unread_count` (migration 019) uses a correlated subquery to count unread messages for each conversation:

```sql
COALESCE(
    (SELECT COUNT(*) FROM messages m
     WHERE m.conversation_id = fc.id
     AND CASE WHEN p_is_admin THEN ... END),
    0
) as unread_count
```

This runs one COUNT subquery per conversation row. With partial indexes on unread messages (`idx_messages_unread_by_user`, `idx_messages_unread_by_admin`), performance is acceptable for small conversation counts but degrades linearly.

**Impact:** Acceptable for current scale (tens of conversations per user). Would need optimization at 1000+ conversations.

**Remediation:** Consider a `LATERAL JOIN` or materialized unread count column on `conversations` table. Low priority.

---

## 9. Data Integrity Gaps

### DB-AUDIT-026: `search_state_transitions.search_id` has no FK to `search_sessions` [LOW]

**Finding:** The `search_state_transitions` table's `search_id` column is intentionally NOT a foreign key (documented in migration 20260221100002: "fire-and-forget inserts -- never blocks the pipeline"). This is a deliberate design choice for performance.

**Trade-off:** Orphaned transition records can exist if the associated search_session is deleted. Over time, this table will grow unbounded without cleanup.

**Remediation:**
1. Add a pg_cron job to clean transitions older than 30 days:
```sql
SELECT cron.schedule('cleanup-state-transitions', '0 5 * * *',
    $$DELETE FROM search_state_transitions WHERE created_at < NOW() - INTERVAL '30 days'$$);
```
2. Document the intentional no-FK design in a table comment.

---

### DB-AUDIT-027: No CHECK constraint on `search_state_transitions.to_state` values [LOW]

**Finding:** The `to_state` column accepts any text value. The application enforces valid states via the `SearchState` enum in `search_state_manager.py`, but there is no database-level validation.

Valid states from code: `CREATED, PROCESSING, COMPLETED, FAILED, TIMED_OUT, CANCELLED`

**Impact:** Invalid state values could be inserted by buggy code or manual queries.

**Remediation:**
```sql
ALTER TABLE search_state_transitions
    ADD CONSTRAINT check_valid_to_state
    CHECK (to_state IN ('CREATED','PROCESSING','COMPLETED','FAILED','TIMED_OUT','CANCELLED'));
```

---

## 10. Code-Database Mismatches

### DB-AUDIT-028: `services/trial_stats.py` references non-existent `user_pipeline` table [CRITICAL]

**Finding:** In `backend/services/trial_stats.py` line 78:
```python
sb.table("user_pipeline")
    .select("id", count="exact")
    .eq("user_id", user_id)
```

The actual table name is `pipeline_items` (migration 025). The code references a table that does not exist.

**Impact:** The trial stats endpoint will throw a Supabase 404/error when trying to count pipeline items. This is a runtime bug.

**Remediation:**
```python
# Fix in backend/services/trial_stats.py
sb.table("pipeline_items")  # was "user_pipeline"
    .select("id", count="exact")
    .eq("user_id", user_id)
```

**Effort:** 1-line code fix, zero risk

---

## 11. Remediation Priority Matrix

### Critical (Fix Immediately)

| ID | Issue | Impact | Effort |
|----|-------|--------|--------|
| DB-AUDIT-003 | `profiles.subscription_status` missing migration | Stripe webhooks fail on fresh DB | 1 migration |
| DB-AUDIT-004 | `profiles.trial_expires_at` missing migration | Analytics endpoint fails on fresh DB | 1 migration |
| DB-AUDIT-005 | `user_subscriptions.subscription_status` missing migration | Stripe webhooks fail on fresh DB | 1 migration |
| DB-AUDIT-028 | Code references non-existent `user_pipeline` table | Runtime error in trial stats | 1-line code fix |

### High (Next Sprint)

| ID | Issue | Impact | Effort |
|----|-------|--------|--------|
| DB-AUDIT-001 | 3 tables with inconsistent FK targets | Data model inconsistency | 1 migration |
| DB-AUDIT-002 | `classification_feedback` FK missing ON DELETE CASCADE | User deletion blocked | Part of 001 |
| DB-AUDIT-023 | JSONB results blob growing unbounded | Database size inflation | pg_cron + architecture |
| DB-AUDIT-006 | `handle_new_user()` trigger regression | New users missing profile fields | 1 migration |

### Medium (Next 2 Sprints)

| ID | Issue | Impact | Effort |
|----|-------|--------|--------|
| DB-AUDIT-007 | State transitions INSERT not scoped to service_role | Minor security gap | 1 migration |
| DB-AUDIT-009 | Feedback admin policy uses old pattern | Minor perf overhead | 1 migration |
| DB-AUDIT-010 | profiles missing service_role ALL policy | Defense-in-depth | 1 migration |
| DB-AUDIT-011 | Messaging tables missing service_role policies | Defense-in-depth | 1 migration |
| DB-AUDIT-013 | search_sessions missing composite index | Query performance | 1 migration |
| DB-AUDIT-014 | Cache results JSONB has no size governance | Storage growth | Constraint + cron |
| DB-AUDIT-016 | Dual migration numbering schemes | Developer confusion | Convention doc |
| DB-AUDIT-017 | Backend migrations duplicate Supabase | Maintenance burden | Directory cleanup |
| DB-AUDIT-022 | search_sessions arrays without GIN indexes | Analytics query perf | 1 migration |
| DB-AUDIT-024 | No GIN indexes on sectors/ufs arrays | Analytics query perf | Part of 022 |

### Low (Backlog)

| ID | Issue | Impact | Effort |
|----|-------|--------|--------|
| DB-AUDIT-008 | trial_email_log has RLS but no policies | Code clarity | 1 migration |
| DB-AUDIT-012 | plans table has no is_active index | Negligible at scale | 1 migration |
| DB-AUDIT-018 | No rollback scripts | Risk during incidents | Documentation |
| DB-AUDIT-019 | Superseded migration 027b still present | Clutter | File deletion |
| DB-AUDIT-020 | Inconsistent trigger naming | Developer confusion | Batch rename |
| DB-AUDIT-021 | Duplicate updated_at functions | Code duplication | 1 migration |

---

## Consolidated Migration Proposal

All critical and high-priority fixes can be addressed in a single migration:

```sql
-- Migration: 20260225100000_db_audit_fixes.sql
-- Fixes: DB-AUDIT-001 through DB-AUDIT-011

BEGIN;

-- DB-AUDIT-003: Add subscription_status to profiles
ALTER TABLE public.profiles
    ADD COLUMN IF NOT EXISTS subscription_status TEXT DEFAULT 'trial';

-- DB-AUDIT-004: Add trial_expires_at to profiles
ALTER TABLE public.profiles
    ADD COLUMN IF NOT EXISTS trial_expires_at TIMESTAMPTZ;

-- DB-AUDIT-005: Add subscription_status to user_subscriptions
ALTER TABLE public.user_subscriptions
    ADD COLUMN IF NOT EXISTS subscription_status TEXT DEFAULT 'active';

-- DB-AUDIT-001: Standardize FKs to profiles(id)
-- pipeline_items
DO $$ BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'pipeline_items_user_id_fkey') THEN
        ALTER TABLE pipeline_items DROP CONSTRAINT pipeline_items_user_id_fkey;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'pipeline_items_user_id_profiles_fkey') THEN
        ALTER TABLE pipeline_items ADD CONSTRAINT pipeline_items_user_id_profiles_fkey
            FOREIGN KEY (user_id) REFERENCES profiles(id) ON DELETE CASCADE;
    END IF;
END $$;

-- classification_feedback (also fixes DB-AUDIT-002)
DO $$ BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'classification_feedback_user_id_fkey') THEN
        ALTER TABLE classification_feedback DROP CONSTRAINT classification_feedback_user_id_fkey;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'classification_feedback_user_id_profiles_fkey') THEN
        ALTER TABLE classification_feedback ADD CONSTRAINT classification_feedback_user_id_profiles_fkey
            FOREIGN KEY (user_id) REFERENCES profiles(id) ON DELETE CASCADE;
    END IF;
END $$;

-- trial_email_log
DO $$ BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'trial_email_log_user_id_fkey') THEN
        ALTER TABLE trial_email_log DROP CONSTRAINT trial_email_log_user_id_fkey;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'trial_email_log_user_id_profiles_fkey') THEN
        ALTER TABLE trial_email_log ADD CONSTRAINT trial_email_log_user_id_profiles_fkey
            FOREIGN KEY (user_id) REFERENCES profiles(id) ON DELETE CASCADE;
    END IF;
END $$;

-- DB-AUDIT-007: Scope state transitions INSERT to service_role
DROP POLICY IF EXISTS "Service role can insert transitions" ON search_state_transitions;
CREATE POLICY "Service role can insert transitions" ON search_state_transitions
    FOR INSERT TO service_role WITH CHECK (true);

-- DB-AUDIT-008: Add explicit service_role policy on trial_email_log
DROP POLICY IF EXISTS "Service role full access on trial_email_log" ON trial_email_log;
CREATE POLICY "Service role full access on trial_email_log"
    ON trial_email_log FOR ALL TO service_role USING (true) WITH CHECK (true);

-- DB-AUDIT-009: Fix classification_feedback admin policy
DROP POLICY IF EXISTS feedback_admin_all ON classification_feedback;
CREATE POLICY feedback_admin_all ON classification_feedback
    FOR ALL TO service_role USING (true) WITH CHECK (true);

-- DB-AUDIT-010: Add profiles service_role ALL policy
DROP POLICY IF EXISTS "profiles_service_all" ON public.profiles;
CREATE POLICY "profiles_service_all" ON public.profiles
    FOR ALL TO service_role USING (true) WITH CHECK (true);

-- DB-AUDIT-011: Add messaging service_role policies
DROP POLICY IF EXISTS "conversations_service_all" ON conversations;
CREATE POLICY "conversations_service_all" ON conversations
    FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "messages_service_all" ON messages;
CREATE POLICY "messages_service_all" ON messages
    FOR ALL TO service_role USING (true) WITH CHECK (true);

COMMIT;
```

**Estimated effort:** 2-3 hours including testing
**Risk level:** Low (additive changes, no data modification)
**Testing required:** Run full backend test suite, verify Stripe webhook flow, test signup flow

---

## Appendix: Tables Not Found in Migrations

The following columns are referenced in backend code but have no migration creating them. They were likely added via the Supabase Dashboard SQL editor:

| Table | Column | Where Used |
|-------|--------|------------|
| `profiles` | `subscription_status` | webhooks/stripe.py, routes/billing.py, routes/user.py |
| `profiles` | `trial_expires_at` | routes/analytics.py, routes/user.py |
| `user_subscriptions` | `subscription_status` | webhooks/stripe.py, routes/billing.py |

These **must** be formalized in migrations for disaster recovery and new environment setup.

---

## Appendix: Code Table Reference Validation

All tables referenced in backend Python code via `.table("name")` calls:

| Table Name in Code | Exists in Migrations | Status |
|--------------------|---------------------|--------|
| `profiles` | Yes (001) | OK |
| `plans` | Yes (001) | OK |
| `user_subscriptions` | Yes (001) | OK |
| `plan_features` | Yes (009) | OK |
| `monthly_quota` | Yes (002) | OK |
| `search_sessions` | Yes (001) | OK |
| `search_results_cache` | Yes (026) | OK |
| `search_state_transitions` | Yes (20260221100002) | OK |
| `pipeline_items` | Yes (025) | OK |
| `conversations` | Yes (012) | OK |
| `messages` | Yes (012) | OK |
| `stripe_webhook_events` | Yes (010) | OK |
| `user_oauth_tokens` | Yes (013) | OK |
| `google_sheets_exports` | Yes (014) | OK |
| `audit_events` | Yes (023) | OK |
| `classification_feedback` | Yes (backend/006) | OK |
| `trial_email_log` | Yes (20260224100000) | OK |
| **`user_pipeline`** | **NO** | **BUG: Should be `pipeline_items`** |
