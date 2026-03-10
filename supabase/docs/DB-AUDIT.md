# Database Audit Report

**Audit Date:** 2026-03-10
**Auditor:** @data-engineer (AIOS Brownfield Discovery Phase 2)
**Scope:** 57 migration files (47 Supabase + 10 backend), 21 tables, 17 functions, 60+ indexes, Redis cache layer

---

## 1. Schema Health

### Tables Inventory

| # | Table | Columns | Indexes | RLS | Triggers | Issues |
|---|-------|---------|---------|-----|----------|--------|
| 1 | profiles | 18 | 7 | 5 policies | 1 (updated_at) | OK |
| 2 | plans | 13 | 0 | 1 policy | 1 (updated_at) | No index on is_active |
| 3 | plan_billing_periods | 7 | 0 | 2 policies | 0 | No index, low volume OK |
| 4 | plan_features | 8 | 1 | 1 policy | 1 (updated_at) | OK |
| 5 | user_subscriptions | 14 | 5 | 2 policies | 1 (updated_at) | OK |
| 6 | monthly_quota | 6 | 1 | 2 policies | 0 | No updated_at trigger |
| 7 | search_sessions | 24 | 6 | 3 policies | 0 | No updated_at, missing DELETE policy |
| 8 | search_results_cache | 19 | 6 | 2 policies | 1 (cleanup) | OK |
| 9 | search_state_transitions | 8 | 2 | 2 policies | 0 | No FK to search_sessions |
| 10 | conversations | 8 | 3 | 4 policies | 0 | No updated_at trigger |
| 11 | messages | 8 | 4 | 4 policies | 1 (last_message) | Missing updated_at |
| 12 | pipeline_items | 14 | 3 | 5 policies | 1 (updated_at) | OK |
| 13 | stripe_webhook_events | 6 | 2 | 3 policies | 0 | OK |
| 14 | audit_events | 7 | 4 | 2 policies | 0 | No retention monitoring |
| 15 | user_oauth_tokens | 9 | 2 | 4+1 policies | 0 | Missing updated_at trigger |
| 16 | google_sheets_exports | 8 | 4 | 4 policies | 0 | Missing updated_at trigger |
| 17 | classification_feedback | 14 | 2 | 5 policies | 0 | Missing updated_at, no service_role ALL |
| 18 | trial_email_log | 4 | 1 | 0 policies | 0 | No user-facing RLS (service-only) |
| 19 | alert_preferences | 7 | 2 | 4 policies | 2 | OK |
| 20 | alerts | 7 | 2 | 5 policies | 1 (updated_at) | OK |
| 21 | alert_sent_items | 4 | 3 | 2 policies | 0 | No retention policy |

### Summary
- **21 tables** in public schema (+ 1 system user in auth.users)
- **17 functions** (6 SECURITY DEFINER)
- **1 custom enum type** (alert_frequency)
- **2 extensions** (pg_trgm, pg_cron)
- **4 pg_cron retention jobs**

---

## 2. RLS Coverage

| Table | SELECT | INSERT | UPDATE | DELETE | Service Role | Gaps |
|-------|--------|--------|--------|--------|-------------|------|
| profiles | Own | Own + service | Own | NONE | ALL | **No DELETE policy** |
| plans | Public | NONE | NONE | NONE | NONE | Read-only, OK |
| plan_billing_periods | Public | NONE | NONE | NONE | ALL | OK |
| plan_features | Public | NONE | NONE | NONE | NONE | **No service_role write** |
| user_subscriptions | Own | NONE | NONE | NONE | ALL | **No user INSERT/UPDATE** |
| monthly_quota | Own | NONE | NONE | NONE | ALL | OK (service writes) |
| search_sessions | Own | Own | NONE | NONE | ALL | **No user UPDATE/DELETE** |
| search_results_cache | Own | NONE | NONE | NONE | ALL | OK (service writes) |
| search_state_transitions | Own (join) | NONE | NONE | NONE | INSERT only | **No service SELECT** |
| conversations | Own+admin | Own | Admin | NONE | ALL | **No DELETE** |
| messages | Own+admin | Own+admin | Own+admin | NONE | ALL | **No DELETE** |
| pipeline_items | Own | Own | Own | Own | ALL | OK |
| stripe_webhook_events | Admin+service | Service | NONE | NONE | Partial | **No UPDATE for status change** |
| audit_events | Admin | NONE | NONE | NONE | ALL | OK |
| user_oauth_tokens | Own | NONE | Own | Own | ALL | **No user INSERT** |
| google_sheets_exports | Own | Own | Own | NONE | ALL | **No DELETE** |
| classification_feedback | Own | Own | Own | Own | auth.role() check | **RLS uses auth.role() not TO clause** |
| trial_email_log | NONE | NONE | NONE | NONE | NONE | Service-role bypasses RLS |
| alert_preferences | Own | Own | Own | NONE | ALL (auth.role()) | **Service policy uses auth.role() not TO** |
| alerts | Own | Own | Own | Own | ALL (TO service_role) | OK |
| alert_sent_items | Own (join) | NONE | NONE | NONE | ALL (TO service_role) | OK |

### Critical RLS Gaps

1. **profiles has no DELETE policy** -- Users cannot delete own profile via RLS. Deletion relies on auth.users cascade. Not necessarily a problem but worth documenting.

2. **classification_feedback uses `auth.role() = 'service_role'`** (mig 006 in backend) -- This is the OLDER pattern. Best practice is `TO service_role` clause. The `auth.role()` check works but is less explicit.

3. **alert_preferences service policy uses `auth.role() = 'service_role'`** (mig 20260226100000) -- Same pattern issue as classification_feedback.

4. **stripe_webhook_events has no UPDATE policy** -- Migration 20260227120001 added a `status` column and GRANT UPDATE, but no RLS UPDATE policy exists. Service role bypasses RLS, so this works in practice, but is inconsistent.

5. **plan_features has no service_role write policy** -- Backend cannot modify feature flags via PostgREST. Modifications require direct SQL or migration.

---

## 3. Performance Issues

### Missing Indexes

| Table | Missing Index | Impact | Priority |
|-------|--------------|--------|----------|
| `plans` | `is_active` | Minor -- small table, sequential scan OK | LOW |
| `search_sessions` | `(user_id, created_at DESC, status)` covering index | Medium -- historico page queries | MEDIUM |
| `search_state_transitions` | `(created_at)` for retention cleanup | Low -- no pg_cron job yet | LOW |
| `alert_sent_items` | No retention cleanup index | Medium -- table grows unbounded | MEDIUM |

### N+1 Patterns (Identified and Resolved)

1. **Conversations N+1** -- Fixed by `get_conversations_with_unread_count()` RPC (mig 019). The backend code should verify it uses this RPC.

2. **Analytics summary** -- Fixed by `get_analytics_summary()` RPC (mig 019). Eliminates full-table scan.

### Query Optimization Opportunities

1. **search_sessions has 24 columns** -- Many columns added incrementally via ALTER TABLE. Consider a JSON `metadata` column for rarely-queried fields (failed_ufs, pipeline_stage, response_state) to reduce row width.

2. **search_results_cache.results JSONB** -- Can reach 2MB (CHECK constraint). Consider storing in Supabase Storage instead of inline JSONB for entries > 500KB. Would dramatically reduce table bloat and vacuum pressure.

3. **profiles table has 18 columns** -- Accumulated via 8 ALTER TABLE migrations. Context_data JSONB helps, but subscription_status, trial_expires_at, subscription_end_date, email_unsubscribed could be a separate `profile_settings` table.

---

## 4. Security Issues

### RLS Gaps

1. **`FOR ALL USING (true)` without `TO service_role`** -- Fixed for most tables in migrations 016, 027, 028. Remaining instances:
   - `classification_feedback.feedback_admin_all` uses `auth.role() = 'service_role'` (functional but suboptimal)
   - `alert_preferences` service policy uses `auth.role()` pattern

2. **Stripe price IDs hardcoded in migrations** -- Production Stripe price IDs (price_1Sy..., price_1T1..., price_1T54...) are in migration SQL files committed to git. Not a secret per se (they are public IDs), but environment-specific. Documented in migration 021 comments.

3. **System user with nil UUID** -- Migration 20260226110000 creates a user with ID `00000000-0000-0000-0000-000000000000` in auth.users. This is an internal system account for cache warming. Has `plan_type='master'` and `is_admin=false`. Acceptable pattern but should be documented as a known system account.

### Data Exposure Risks

1. **audit_events PII hashing** -- Good: SHA-256 truncated to 16 hex chars for actor_id, target_id, IP. LGPD/GDPR compliant.

2. **OAuth tokens marked as AES-256 encrypted** -- The schema comments state tokens are encrypted, but encryption is handled at application level (backend). No DB-level encryption beyond Supabase's at-rest encryption.

3. **search_results_cache.results** -- Contains full search results as JSONB. If exposed via RLS bypass, reveals business intelligence data. Current RLS (own + service_role) is adequate.

---

## 5. Data Integrity Issues

### Missing Constraints

| Table | Issue | Severity | Recommendation |
|-------|-------|----------|----------------|
| `search_state_transitions` | No FK to `search_sessions.search_id` | MEDIUM | Add FK with ON DELETE CASCADE (or SET NULL) |
| `search_sessions.status` | No CHECK on `error_code` values | LOW | Add CHECK constraint for documented error codes |
| `pipeline_items.uf` | No CHECK against valid UF codes | LOW | Add CHECK or validate in application |
| `search_results_cache.priority` | No CHECK constraint | LOW | Add CHECK: hot, warm, cold |
| `profiles.subscription_status` vs `user_subscriptions.subscription_status` | Duplicate concept | MEDIUM | Source of truth unclear -- profiles is denormalized copy |

### Orphan Data Risks

1. **search_state_transitions with no FK** -- If a search_session is deleted, its transitions remain. This is by design (audit trail), but there is no pg_cron cleanup job for this table. Over time, this table will grow unbounded.

2. **alert_sent_items without retention** -- No pg_cron job for cleanup. Items accumulate indefinitely. Should add a job to delete entries > 90 days.

3. **classification_feedback has no retention policy** -- Will grow indefinitely. Consider archival strategy.

### Cascade Gaps

| FK | ON DELETE | Issue |
|----|-----------|-------|
| user_subscriptions.plan_id -> plans.id | RESTRICT | Intentional (documented in mig 022) |
| All user_id FKs -> profiles.id | CASCADE | Correct |
| alert_sent_items.alert_id -> alerts.id | CASCADE | Correct |
| messages.conversation_id -> conversations.id | CASCADE | Correct |

---

## 6. Migration Health

### Migration Naming Inconsistency

The project uses TWO naming conventions:
1. **Sequential:** `001_profiles_and_sessions.sql` through `033_fix_missing_cache_columns.sql` (33 files)
2. **Timestamped:** `20260220120000_*.sql` through `20260227120003_*.sql` (14 files)

This causes:
- **Duplicate numbering:** `027_fix_plan_type_default_and_rls.sql` AND `027b_search_cache_add_sources_and_fetched_at.sql` share the `027` prefix. Migration 033 exists specifically to fix the columns that 027b was supposed to add.
- **Ordering ambiguity:** Sequential files (e.g., `033_`) sort AFTER timestamped files (e.g., `20260220...`) alphabetically, but chronologically `033` was earlier.

### Duplicate/Overlapping Migrations

| Issue | Files | Status |
|-------|-------|--------|
| 027/027b collision | 027_fix_plan_type + 027b_search_cache | Fixed by 033 |
| handle_new_user() redefined 8 times | 001, 007, 016, 024, 027, 20260224, 20260225110000 | Each version cumulative; only latest matters |
| profiles.plan_type CHECK redefined 4 times | 006a, 020, 029, present state | Normal evolution |

### Backend vs Supabase Migration Overlap

7 files in `backend/migrations/` duplicate content from `supabase/migrations/`:
- `002_monthly_quota.sql` = `supabase/002_monthly_quota.sql`
- `003_atomic_quota_increment.sql` = `supabase/003_atomic_quota_increment.sql`
- `004_google_oauth_tokens.sql` = `supabase/013_google_oauth_tokens.sql`
- `005_google_sheets_exports.sql` = `supabase/014_google_sheets_exports.sql`
- `007_search_session_lifecycle.sql` ~ `supabase/20260221100000_search_session_lifecycle.sql`
- `008_search_state_transitions.sql` ~ `supabase/20260221100002_create_search_state_transitions.sql`
- `009_add_search_id_to_search_sessions.sql` = `supabase/20260220120000_add_search_id_to_search_sessions.sql`

This dual-track is confusing. The `backend/migrations/` directory appears to be a historical artifact from before the team standardized on `supabase/migrations/`.

### Rollback Readiness

- **008_rollback.sql.bak** exists but is a `.bak` file (not executable).
- No other migration has a rollback script.
- Most migrations use `IF NOT EXISTS` / `IF EXISTS` for idempotency, which is good.
- The pg_cron jobs in migration 022 have `cron.unschedule()` commands documented in comments.

---

## 7. Redis Cache Architecture

### Key Patterns

| Key Pattern | Purpose | TTL | Module |
|-------------|---------|-----|--------|
| `smartlic:cache:{params_hash}` | Search results L1 cache | 4h (hot: 2h, warm: 6h, cold: 1h) | search_cache.py |
| `smartlic:auth:{token_hash}` | JWT validation cache (L2) | 5min | auth.py |
| `smartlic:quota:{user_id}:{month}` | Quota count cache | None (explicit invalidation) | quota.py |
| `smartlic:llm:{prompt_hash}` | LLM response cache | Variable | llm_arbiter.py |
| `smartlic:cb:*` | Circuit breaker state | Variable | Various |
| `features:*` | Feature flag cache | 5min | cache.py |

### TTL Strategy

```
L1 InMemory/Redis: 4h (Fresh)
  - Hot: 2h (high access, frequently refreshed)
  - Warm: 6h (moderate access)
  - Cold: 1h (low access, aggressive eviction)

L2 Supabase: 24h (Stale, SWR eligible)
L3 Local File: 24h (Emergency fallback only)

Auth cache: 60s L1, 5min L2 (Redis)
```

### Pool Configuration

| Pool | Max Connections | Socket Timeout | Purpose |
|------|-----------------|----------------|---------|
| Main async | 50 | 30s | General operations |
| SSE | 10 | 60s | SSE XREAD polling |
| Sync | 12 | 30s | LLM arbiter (ThreadPoolExecutor) |

### Cache Invalidation

- **Plan status cache:** Invalidated on Stripe webhook via `invalidate_plan_status_cache(user_id)` (5min TTL as backup)
- **Auth token cache:** LRU with 60s TTL, max 1000 entries
- **Search cache:** SWR pattern (serve stale, revalidate in background)
- **Feature flags:** TTL-based (5min), no explicit invalidation

### Resilience

- **Redis unavailable:** Falls back to `InMemoryCache` (LRU, 10K entries max)
- **Fallback monitoring:** `REDIS_AVAILABLE` Prometheus gauge, `REDIS_FALLBACK_DURATION` gauge
- **Warning after 5min:** Periodic WARNING log every 60s when in fallback > 5min

---

## 8. Technical Debt Inventory

| ID | Issue | Severity | Impact | Est. Hours |
|----|-------|----------|--------|------------|
| DB-001 | `search_state_transitions` has no FK to `search_sessions.search_id` | MEDIUM | Orphan rows on session deletion; no referential integrity | 2 |
| DB-002 | `classification_feedback` RLS uses `auth.role()` instead of `TO service_role` | LOW | Functional but inconsistent with project convention | 1 |
| DB-003 | `alert_preferences` service RLS uses `auth.role()` pattern | LOW | Same as DB-002 | 1 |
| DB-004 | `backend/migrations/` duplicates `supabase/migrations/` | MEDIUM | Confusion about source of truth for migrations | 2 |
| DB-005 | Migration naming inconsistency (sequential vs timestamped) | LOW | Ordering ambiguity, no runtime impact | 1 |
| DB-006 | `handle_new_user()` trigger redefined 8 times across migrations | LOW | Only latest version matters, but hard to audit | 0 |
| DB-007 | No retention policy for `search_state_transitions` | MEDIUM | Table grows unbounded (audit trail) | 2 |
| DB-008 | No retention policy for `alert_sent_items` | MEDIUM | Table grows unbounded | 1 |
| DB-009 | No retention policy for `classification_feedback` | LOW | Low volume currently | 1 |
| DB-010 | `search_results_cache.results` JSONB up to 2MB inline | MEDIUM | Table bloat, vacuum pressure, backup size | 8 |
| DB-011 | `profiles.subscription_status` duplicates `user_subscriptions.subscription_status` | MEDIUM | Two sources of truth for same concept | 4 |
| DB-012 | `search_sessions` has 24 columns (wide table) | LOW | Row width affects scan performance | 4 |
| DB-013 | `user_oauth_tokens` missing `updated_at` trigger | LOW | `updated_at` column exists but not auto-updated | 1 |
| DB-014 | `google_sheets_exports` missing `updated_at` trigger | LOW | Has `last_updated_at` but no trigger | 1 |
| DB-015 | `monthly_quota` has no `updated_at` trigger | LOW | `updated_at` column exists, updated manually in RPC | 0 |
| DB-016 | `stripe_webhook_events` no UPDATE RLS policy | LOW | Service role bypasses RLS, works but inconsistent | 1 |
| DB-017 | `plan_features` no service_role write policy | LOW | Cannot modify via PostgREST API; requires SQL | 1 |
| DB-018 | `conversations` missing `updated_at` auto-trigger | LOW | `updated_at` column exists; manually set in `update_conversation_last_message` | 1 |
| DB-019 | `search_results_cache.priority` has no CHECK constraint | LOW | Application enforces hot/warm/cold but DB allows any text | 1 |
| DB-020 | Duplicate `update_*_updated_at()` functions | LOW | 4 separate functions that all do `NEW.updated_at = now()`. Could reuse `update_updated_at()` | 2 |

### Severity Distribution
- **MEDIUM:** 6 items (DB-001, 004, 007, 008, 010, 011)
- **LOW:** 14 items

### Total Estimated Effort: ~35 hours

---

## 9. Questions for @architect

1. **search_state_transitions FK:** Should we add a FK from `search_state_transitions.search_id` to `search_sessions.search_id`? The lack of FK means transitions persist even after session deletion (audit benefit), but also means orphan rows accumulate. What is the retention policy?

2. **Dual subscription_status:** `profiles.subscription_status` and `user_subscriptions.subscription_status` both track subscription state. Which is the source of truth? Can we deprecate one? The `sync_profile_plan_type()` trigger was removed (mig 030) because it referenced a non-existent `status` column, suggesting the sync mechanism is broken.

3. **search_results_cache.results as JSONB:** At up to 2MB per row, this table can get large fast (10 entries/user * N users * 2MB). Should we move large results to Supabase Storage (bucket) with only a reference URL in the table? This would reduce table bloat significantly.

4. **Backend migrations directory:** Can we deprecate `backend/migrations/` entirely? All recent migrations go to `supabase/migrations/`. The duplicate files are a maintenance burden and potential source of confusion.

5. **Migration naming convention:** Should we standardize on timestamped naming (YYYYMMDDHHMMSS) going forward? The mixed sequential+timestamped scheme causes ordering issues.

6. **alert_sent_items retention:** This table has no cleanup job. At scale, it could grow large. Should we add a pg_cron job to delete entries > 90 days? Or should sent items be kept indefinitely for audit purposes?

7. **`update_*_updated_at()` function proliferation:** There are 4 separate trigger functions that all do `NEW.updated_at = now()`. The generic `update_updated_at()` from migration 001 does the same thing. Should we consolidate to use the generic one everywhere?

8. **Supabase Connection Pool Sizing:** `supabase_client.py` configures `max_connections=25` per worker. With 2 Gunicorn workers, that is 50 total. Supabase Free tier allows 50 connections, Pro allows more. Are we at risk of exhaustion during traffic spikes? The `SUPABASE_POOL_MAX_CONNECTIONS` env var makes this tunable, but the default may need review.

---

## Appendix: Migration Execution Order

For disaster recovery (recreate DB from migrations), execute in this order:

```
001_profiles_and_sessions.sql
002_monthly_quota.sql
003_atomic_quota_increment.sql
004_add_is_admin.sql
005_update_plans_to_new_tiers.sql
006a_update_profiles_plan_type_constraint.sql
006b_search_sessions_service_role_policy.sql
007_add_whatsapp_consent.sql
008_add_billing_period.sql
009_create_plan_features.sql
010_stripe_webhook_events.sql
011_add_billing_helper_functions.sql
012_create_messages.sql
013_google_oauth_tokens.sql
014_google_sheets_exports.sql
015_add_stripe_price_ids_monthly_annual.sql
016_security_and_index_fixes.sql
017_sync_plan_type_trigger.sql
018_standardize_fk_references.sql
019_rpc_performance_functions.sql
020_tighten_plan_type_constraint.sql
021_user_subscriptions_updated_at.sql
022_retention_cleanup.sql
023_audit_events.sql
024_add_profile_context.sql
025_create_pipeline_items.sql
026_search_results_cache.sql
027_fix_plan_type_default_and_rls.sql
027b_search_cache_add_sources_and_fetched_at.sql
028_fix_stripe_webhook_events_rls.sql
029_single_plan_model.sql
030_remove_dead_sync_trigger.sql
031_cache_health_metadata.sql
032_cache_priority_fields.sql
033_fix_missing_cache_columns.sql
20260220120000_add_search_id_to_search_sessions.sql
20260221100000_search_session_lifecycle.sql
20260221100001_create_get_table_columns_simple.sql
20260221100002_create_search_state_transitions.sql
20260223100000_add_params_hash_global.sql
20260224000000_phone_email_unique.sql
20260224100000_trial_email_log.sql
20260224200000_fix_cache_user_fk.sql
20260225100000_add_missing_profile_columns.sql
20260225110000_fix_handle_new_user_trigger.sql
20260225120000_standardize_fks_to_profiles.sql
20260225130000_rls_policy_hardening.sql
20260225140000_add_session_composite_index.sql
20260225150000_jsonb_storage_governance.sql
20260226100000_alert_preferences.sql
20260226110000_warming_user_profile.sql
20260226120000_story277_repricing_stripe_ids.sql
20260227100000_create_alerts.sql
20260227120001_concurrency_stripe_webhook.sql
20260227120002_concurrency_pipeline_version.sql
20260227120003_concurrency_quota_rpc.sql
```

Also apply from `backend/migrations/`:
```
006_classification_feedback.sql  (creates classification_feedback table)
010_normalize_session_arrays.sql (normalizes arrays in search_sessions)
```

Note: Backend migrations 002-005, 007-009 are duplicates of supabase migrations and should NOT be applied twice.
