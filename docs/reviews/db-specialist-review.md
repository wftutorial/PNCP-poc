# Database Specialist Review — v3.0

**Reviewer:** @data-engineer (Delta)
**Date:** 2026-03-07
**Scope:** Database debts from technical-debt-DRAFT.md v3.0 (DB-001 through DB-046)
**Cross-references:** DB-AUDIT.md, all 76 migration files (66 Supabase + 10 backend), backend/oauth.py, backend/authorization.py
**Supersedes:** v2.0 (2026-03-04, reviewed DRAFT v2.0 with old ID scheme C-01/H-01/etc.)

---

## Validation Summary

| Status | Count |
|--------|-------|
| Confirmed | 38 |
| Severity Adjusted | 6 |
| Removed (false positive) | 1 |
| Added (new) | 4 |

---

## Debitos Validados

| ID | Debito | Original Sev | Adjusted Sev | Hours | Complexity | Sprint | Notes |
|----|--------|-------------|-------------|-------|------------|--------|-------|
| DB-001 | `classification_feedback` service_role policy uses `auth.role()` | CRITICAL | **HIGH** | 1 | simple | S1 | See Severity Adjustments. Confirmed in `backend/migrations/006_classification_feedback.sql` line 48. Migration `20260304200000` explicitly skipped this table (line 57: "Table does not exist yet"). |
| DB-002 | `health_checks` and `incidents` no user-facing policies | HIGH | **MEDIUM** | 2 | simple | S2 | See Severity Adjustments. Both tables are backend-only (service_role access). No frontend reads these tables. Not a gap -- it is by-design. Add explicit `TO service_role` policies for self-documentation. |
| DB-003 | OAuth tokens stored in plaintext | HIGH | **REMOVED** | 0 | n/a | n/a | **FALSE POSITIVE.** Verified: `backend/oauth.py` implements Fernet AES-256 encryption. Lines 84-131 define `encrypt_aes256()` and `decrypt_aes256()`. Lines 312-313 encrypt before storage. Lines 374-376 decrypt after retrieval. `ENCRYPTION_KEY` env var is required in production (lines 51-57). Tokens are NOT plaintext. |
| DB-004 | `mfa_recovery_codes` no rate limiting in DB | HIGH | **MEDIUM** | 4 | medium | S2 | DB-level rate limiting is unusual. Application-layer rate limiting via `mfa_recovery_attempts` table is the standard pattern. The table exists and tracks attempts. Risk is only if service_role key is compromised (which has much bigger implications). |
| DB-005 | `mfa_recovery_attempts` no SELECT for user | MEDIUM | MEDIUM | 1 | simple | Backlog | Intentional by design. Users should not see their own attempt history (information leakage risk). Document as accepted. |
| DB-006 | `trial_email_log` no user-facing policies | MEDIUM | MEDIUM | 1 | simple | Backlog | Backend-only table. Correct by design. Document. |
| DB-007 | `search_state_transitions` SELECT uses correlated subquery | MEDIUM | MEDIUM | 4 | medium | S2 | Confirmed. RLS policy joins to `search_sessions` via subquery. Index `idx_search_sessions_search_id` exists but per-row evaluation is still expensive at scale. Adding `user_id` column directly would be cleanest fix but requires backfill. |
| DB-008 | Stripe Price IDs visible in `plans` (public read RLS) | MEDIUM | LOW | 0 | n/a | Backlog | Accepted risk. Price IDs are used client-side in Stripe Checkout by design. Not a secret. Document as accepted. |
| DB-009 | `profiles.email` exposed via partner RLS cross-schema query | MEDIUM | MEDIUM | 2 | simple | S2 | Functionally correct. Could cache email in `partners.contact_email` comparison without cross-schema query. Low urgency. |
| DB-010 | System cache warmer account with empty password | LOW | LOW | 1 | simple | S2 | Confirmed in migration `20260226110000`. Supabase Auth will not authenticate `encrypted_password = ''`. Add `banned_until = '2099-12-31'` for defense-in-depth. |
| DB-011 | `handle_new_user()` trigger rewritten 7+ times | HIGH | MEDIUM | 4 | medium | S2 | Trigger has stabilized at version 20260225110000 (includes all 10 columns + ON CONFLICT DO NOTHING). The 7 rewrites were evolutionary, not indicative of ongoing instability. Fix is an integration test, not code changes. See Respostas Q7. |
| DB-012 | `updated_at` functions inconsistent (`update_updated_at` vs `set_updated_at`) | HIGH | HIGH | 2 | simple | S1 | Confirmed. Two identical functions exist. Some triggers use one, some the other. Consolidate to `set_updated_at()` and drop `update_updated_at()`. Safe migration with zero data impact. |
| DB-013 | `partner_referrals.referred_user_id` ON DELETE SET NULL vs NOT NULL | HIGH | HIGH | 1 | simple | S1 | Confirmed. Column is `NOT NULL` (migration 20260301200000 line 32) but FK is `ON DELETE SET NULL` (migration 20260304100000 line 77). DELETE of a profile WILL fail with constraint violation. Fix: `ALTER COLUMN referred_user_id DROP NOT NULL`. |
| DB-014 | `plans.stripe_price_id` legacy column coexists with period-specific | MEDIUM | MEDIUM | 2 | simple | Backlog | Confirmed. Legacy column always set to monthly price. Low risk since all billing code uses period-specific columns. Deprecate after confirming zero references. |
| DB-015 | `profiles.plan_type` vs `user_subscriptions.plan_id` duplication | MEDIUM | MEDIUM | 4 | medium | S2 | Intentional design decision (STORY-291 circuit breaker fail-open uses profiles.plan_type as fallback). Document as accepted. Add reconciliation cron job to detect drift. |
| DB-016 | `search_sessions.status` no transition enforcement in DB | MEDIUM | MEDIUM | 4 | medium | Backlog | Application-layer enforcement via `search_state_manager.py` is working. DB triggers for state machines add complexity. Document valid transitions in a CHECK or COMMENT instead. |
| DB-017 | Missing `NOT NULL` on several columns | LOW | LOW | 2 | simple | Backlog | Only 3 of the 5 listed columns receive UPDATEs. `google_sheets_exports.created_at` and `partners.created_at` should be `NOT NULL DEFAULT now()`. Others are append-only and less critical. |
| DB-018 | `search_results_cache.priority` no CHECK constraint | LOW | LOW | 0.5 | simple | S2 | Quick win. `CHECK (priority IN ('hot', 'warm', 'cold'))`. |
| DB-019 | `alert_runs.status` no CHECK constraint | LOW | LOW | 0.5 | simple | S2 | Quick win. Add CHECK with documented values including `'pending'`. |
| DB-020 | Naming inconsistency in constraints | LOW | LOW | 1 | simple | Backlog | Cosmetic. Adopt `chk_{table}_{column}` convention for future migrations only. Not worth renaming existing constraints. |
| DB-021 | `user_subscriptions.billing_period` constraint may conflict with legacy data | MEDIUM | LOW | 1 | simple | S2 | Migration 029 handles correctly with `DROP CONSTRAINT IF EXISTS` + `ADD CONSTRAINT`. Run validation query to confirm no orphan rows: `SELECT billing_period, count(*) FROM user_subscriptions GROUP BY 1`. |
| DB-022 | `profiles.phone_whatsapp` CHECK doesn't validate Brazilian structure | MEDIUM | LOW | 1 | simple | Backlog | Application-level validation is more appropriate for phone numbers. DB CHECK for format (digits-only, length) is sufficient. Brazilian DDD validation changes over time. |
| DB-023 | `search_results_cache` UNIQUE allows cross-user sharing with stale date range | LOW | LOW | 2 | medium | Backlog | `params_hash_global` is used for SWR warming. STORY-306 cache key includes dates in hash. Risk is theoretical and mitigated by TTL. |
| DB-024 | `plan_billing_periods` no `updated_at` column | LOW | LOW | 1 | simple | Backlog | Confirmed. Add `updated_at TIMESTAMPTZ DEFAULT now()` + trigger. Low urgency since pricing changes are infrequent and tracked via git migrations. |
| DB-025 | Dual migration directories (`supabase/` + `backend/`) | HIGH | HIGH | 8 | complex | S1 | Confirmed. 10 backend migrations exist outside Supabase CLI. Migration `20260305100000` explicitly acknowledges this caused missing RPCs. See Respostas Q1. |
| DB-026 | Naming non-sequential (mix `001_` + timestamps + `027b_`) | HIGH | MEDIUM | 4 | medium | S1 | Ordering ambiguity exists but Supabase CLI sorts by filename prefix. `027b_` sorts after `027_`. Timestamps sort naturally. Risk is confusion for developers, not execution order failure. |
| DB-027 | No down-migrations | MEDIUM | MEDIUM | 8 | complex | Backlog | Standard for Supabase projects. PITR (Point-in-Time Recovery) is the rollback mechanism. Down-migrations would be nice-to-have but not blocking. |
| DB-028 | Some migrations not idempotent | MEDIUM | MEDIUM | 4 | medium | S2 | Confirmed. `008_add_billing_period.sql` would fail on re-run. Add `IF NOT EXISTS` guards. Low urgency since migrations run once. |
| DB-029 | Hardcoded Stripe Price IDs in migrations | LOW | LOW | 2 | simple | Backlog | Blocks staging/dev environment setup but no production risk. |
| DB-030 | `backend/migrations/` never applied via CLI | HIGH | HIGH | 4 | medium | S1 | Subsumed by DB-025. Same root cause, same fix. Consolidate. |
| DB-031 | `search_results_cache.results` JSONB up to 2MB/row | HIGH | HIGH | 4 | medium | S2 | Confirmed. 2MB CHECK exists (migration 20260225150000). At 10 entries/user x 2MB = 20MB per user. Monitor with `pg_total_relation_size()`. |
| DB-032 | `search_results_store.results` no retention enforcement | HIGH | HIGH | 4 | medium | S1 | Confirmed. `expires_at` default is 24h but no pg_cron cleanup job exists. Table accumulates dead data indefinitely. Direct cost impact on Supabase storage billing. |
| DB-033 | `search_state_transitions` grows without limits | MEDIUM | MEDIUM | 2 | simple | S2 | Confirmed. 5-10 records per search. Add pg_cron: `DELETE WHERE created_at < NOW() - INTERVAL '30 days'`. |
| DB-034 | `cleanup_search_cache_per_user()` trigger on every INSERT | MEDIUM | MEDIUM | 2 | simple | Backlog | Overhead is minimal at current scale. Add short-circuit check: `IF (SELECT count(*) FROM search_results_cache WHERE user_id = NEW.user_id) <= 10 THEN RETURN NEW; END IF;`. |
| DB-035 | `get_conversations_with_unread_count()` correlated subquery | MEDIUM | MEDIUM | 2 | simple | Backlog | Rewrite as LEFT JOIN with GROUP BY for better performance. Low urgency -- messaging volume is low. |
| DB-036 | No table partitioning for append-heavy tables | LOW | LOW | 8 | complex | Backlog | Not needed at POC/beta scale. Plan for `audit_events`, `search_state_transitions` when monthly row count exceeds 1M. |
| DB-037 | `alert_sent_items` no retention cleanup | LOW | MEDIUM | 1 | simple | S2 | Upgraded because this table serves dedup. If rows accumulate without cleanup, dedup queries slow down. 180-day retention recommended. |
| DB-038 | Migration `20260307100000` references non-existent tables | HIGH | HIGH | 2 | simple | S1 | Confirmed. `searches`, `pipeline`, `feedback` do not exist. Actual tables are `search_sessions`, `pipeline_items`, `classification_feedback`. Indexes were never created. |
| DB-039 | `classification_feedback` no index on `user_id` | HIGH | HIGH | 1 | simple | S1 | Confirmed. Migration used wrong table name `feedback`. RLS `auth.uid() = user_id` causes full table scan. |
| DB-040 | Redundant index on `alert_preferences` (plain + UNIQUE on user_id) | LOW | LOW | 0.5 | simple | S2 | Confirmed. UNIQUE creates implicit B-tree. Drop `idx_alert_preferences_user_id`. |
| DB-041 | Redundant index on `trial_email_log` | LOW | LOW | 0.5 | simple | S2 | Composite unique `(user_id, email_number)` covers leading column queries. |
| DB-042 | Missing composite index for admin inbox on `conversations` | LOW | LOW | 1 | simple | S2 | `(status, last_message_at DESC)` would benefit admin queries. Low volume currently. |
| DB-043 | No documented disaster recovery procedure | HIGH | HIGH | 16 | complex | S1 | Confirmed. 76 migrations with no DR guide. Critical operational gap. See Respostas Q6. |
| DB-044 | pg_cron jobs not in migrations (require superuser) | MEDIUM | MEDIUM | 4 | medium | Backlog | Correct -- pg_cron requires `CREATE EXTENSION` which needs superuser. Document manual setup steps. |
| DB-045 | `stripe_webhook_events` idempotency depends on table | MEDIUM | MEDIUM | 2 | simple | S2 | 90-day retention (HARDEN-028) is appropriate. Events older than 90 days are unlikely to be retried by Stripe (72-hour max retry window). |
| DB-046 | No audit trail DB-level for schema changes | LOW | LOW | 4 | medium | Backlog | Policy-based mitigation: "never modify schema via dashboard without migration." DDL event triggers are complex and not worth the overhead. |

---

## Debitos Adicionados

### DB-NEW-01 (MEDIUM) — `search_results_store.results` JSONB has no size CHECK constraint

Unlike `search_results_cache` which has a 2MB CHECK (migration 20260225150000), `search_results_store` stores the same JSONB payload structure with no size limit. A pathological multi-UF search could insert 5-10MB per row.

**Fix:**
```sql
ALTER TABLE search_results_store
  ADD CONSTRAINT chk_store_results_max_size
  CHECK (octet_length(results::text) <= 2097152);
```
**Hours:** 0.5 | **Complexity:** simple | **Sprint:** S1 (bundle with DB-032)

### DB-NEW-02 (MEDIUM) — `partners` and `partner_referrals` service_role policies use `auth.role()`

Migration 20260301200000 has `USING (auth.role() = 'service_role')` for both tables. These were not included in the `20260304200000` standardization migration and are not mentioned in any DB-xxx item.

**Hours:** 0.5 | **Complexity:** simple | **Sprint:** S2 (batch with DB-001 fix)

### DB-NEW-03 (MEDIUM) — `health_checks` and `incidents` missing retention pg_cron job

Migration 20260228150000 table comment says "30-day retention" but no cleanup job was created. At 5-minute intervals, `health_checks` generates ~8,640 rows/month.

**Hours:** 1 | **Complexity:** simple | **Sprint:** S2

### DB-NEW-04 (LOW) — No FK from `search_state_transitions.search_id` to `search_sessions.search_id`

Orphan transition records can exist for deleted sessions. However, `search_sessions.search_id` is nullable and has no UNIQUE constraint, making a proper FK impossible without schema changes. The RLS policy already filters orphans (they become invisible to users).

**Hours:** 4 (if adding UNIQUE + FK) | **Complexity:** medium | **Sprint:** Backlog

---

## Severity Adjustments

### DB-001: CRITICAL -> HIGH

**Justification:** The `auth.role() = 'service_role'` pattern is functionally equivalent to `TO service_role USING (true)` in all current Supabase PostgreSQL versions. Both work correctly. The difference is:
- `auth.role()` evaluates the JWT `role` claim per-row (marginally slower)
- `TO service_role` uses PostgreSQL's native GRANT-based role bypass (instant)

This is a consistency and best-practice issue, not a security or data-loss risk. At the current table size (<10K rows), the performance difference is negligible. CRITICAL should be reserved for data loss or security breach scenarios.

### DB-002: HIGH -> MEDIUM

**Justification:** These tables are backend-only (service_role access). No frontend component reads them. The "absence of user-facing policies" is by design, not a gap. Service_role bypasses RLS entirely. Adding explicit `TO service_role` policies would improve self-documentation but is not urgent.

### DB-003: HIGH -> REMOVED (false positive)

**Justification:** Verified in `backend/oauth.py`: Fernet (AES-256 GCM) encryption is implemented and active. `encrypt_aes256()` is called before DB writes (line 312-313), `decrypt_aes256()` after reads (line 374). `ENCRYPTION_KEY` is required in production (raises RuntimeError if missing). Tokens are encrypted at rest.

### DB-004: HIGH -> MEDIUM

**Justification:** Database-level rate limiting is not an industry standard pattern. Application-layer rate limiting via the `mfa_recovery_attempts` table is the correct approach. The concern about "bypass via direct DB access" would require the service_role key to be compromised, which has far larger implications than MFA bypass.

### DB-011: HIGH -> MEDIUM

**Justification:** The trigger has stabilized at its current version (migration 20260225110000) for 10+ days with no further changes. The 7 historical rewrites represent evolutionary development, not ongoing instability. The fix is adding a test guard, not changing the trigger.

### DB-026: HIGH -> MEDIUM

**Justification:** Supabase CLI sorts migrations by filename prefix lexicographically. The mixed naming (`001_` through `033_` + timestamps) does sort correctly because: (1) numeric prefixes `001-033` sort before `20260220`, and (2) `027b_` sorts after `027_` correctly. The risk is developer confusion, not execution order failure.

### DB-037: LOW -> MEDIUM

**Justification:** `alert_sent_items` serves an active dedup function (preventing re-sending the same procurement item). Without cleanup, dedup queries scan an ever-growing table, degrading alert execution performance. 180-day retention is needed to balance dedup accuracy with performance.

---

## Respostas ao Architect

### Q1: Estrategia de consolidacao de migracoes (DB-025/030)

**Recommendation: Bridge migration with `CREATE OR REPLACE` / `IF NOT EXISTS` guards.**

The 10 `backend/migrations/` files were applied to production via direct SQL execution (not Supabase CLI). The critical items have already been addressed:
- `003_atomic_quota_increment.sql` -- restored by `20260305100000_restore_check_and_increment_quota.sql`
- `006_classification_feedback.sql` -- table exists in production (confirmed by RLS policy functioning)
- `007-010` -- `search_sessions` lifecycle columns exist (confirmed by search functionality working)

**Consolidation approach:**

1. **Verify production state first** (30 min):
```sql
-- Run against production via Supabase SQL Editor or psql
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('classification_feedback', 'search_state_transitions');

SELECT routine_name FROM information_schema.routines
WHERE routine_schema = 'public'
AND routine_name IN ('check_and_increment_quota_atomic', 'check_and_increment_quota');
```

2. **Create bridge migration** (2h): `20260308100000_consolidate_backend_migrations.sql`
   - Wrap each backend migration's content in `IF NOT EXISTS` / `CREATE OR REPLACE`
   - Add verification queries at the end
   - Mark `backend/migrations/` as deprecated with a README

3. **Do NOT move files** -- moving backend migrations into `supabase/migrations/` would create duplicate migration content (since the production state already has these objects). Instead, the bridge migration ensures a fresh `supabase db push` recreates everything.

4. **Add `backend/migrations/DEPRECATED.md`** explaining these were consolidated into Supabase migrations as of the bridge migration timestamp.

**Hours:** 4h total (verification + bridge migration + testing + documentation)

### Q2: Validacao de indices em producao (DB-038/039)

**Yes, run the production query.** The migration `20260307100000` used wrong table names, so those indexes were never created.

**Validation query:**
```sql
-- Check which RLS-supporting indexes actually exist
SELECT schemaname, tablename, indexname
FROM pg_indexes
WHERE schemaname = 'public'
AND tablename IN (
  'classification_feedback', 'search_sessions', 'pipeline_items',
  'search_results_store', 'search_results_cache'
)
AND indexname LIKE '%user_id%'
ORDER BY tablename, indexname;
```

**Expected findings:**
- `search_sessions`: `idx_search_sessions_user_id` exists (from migration 016)
- `pipeline_items`: `idx_pipeline_items_user_id` exists (from migration 025)
- `search_results_store`: `idx_search_results_user` exists (from 20260303100000)
- `classification_feedback`: **MISSING** -- needs `CREATE INDEX idx_classification_feedback_user_id ON classification_feedback(user_id);`

**Corrective migration:**
```sql
-- Fix DB-038/039: Create indexes with correct table names
DROP INDEX IF EXISTS idx_searches_user_id;    -- from wrong table name
DROP INDEX IF EXISTS idx_pipeline_user_id;    -- from wrong table name
DROP INDEX IF EXISTS idx_feedback_user_id;    -- from wrong table name

CREATE INDEX IF NOT EXISTS idx_classification_feedback_user_id
  ON classification_feedback(user_id);

-- search_sessions and pipeline_items already have user_id indexes
-- search_results_store already has idx_search_results_user
```

**Hours:** 1h (query + corrective migration + deploy)

### Q3: Retention policies (DB-033/037)

| Table | Recommended Retention | Schedule | Rationale |
|-------|----------------------|----------|-----------|
| `search_state_transitions` | **30 days** | Daily 4:00 AM UTC | Debugging only needs recent window. 5-10 rows/search x ~50 searches/day = 15K rows/month. 30 days = ~15K rows max. |
| `alert_sent_items` | **180 days** | Weekly Sunday 5:00 AM UTC | Serves active dedup function. Procurement items older than 6 months are typically closed. Deleting too early causes re-sending. |
| `mfa_recovery_attempts` | **30 days** | Daily 4:30 AM UTC | Brute force detection window. Only recent attempts matter for rate limiting. |
| `alert_runs` | **90 days** | Daily 4:45 AM UTC | Execution history for debugging. Quarterly review cycle. ~100 rows/day at current scale. |
| `health_checks` | **30 days** | Daily 3:00 AM UTC | Monitoring data. 8,640 rows/month at 5-min intervals. |
| `incidents` | **90 days** | Daily 3:15 AM UTC | Incident history for post-mortems. Longer than health_checks because incidents are rarer and more valuable. |

**Analytics use case:** None of these tables are used for analytics dashboards currently. If analytics needs arise, archive to a separate analytics schema or export to a data warehouse before purging.

**Implementation:** Single migration with staggered cron times to avoid concurrent cleanup load:
```sql
SELECT cron.schedule('cleanup-state-transitions', '0 4 * * *',
  $$DELETE FROM search_state_transitions WHERE created_at < NOW() - INTERVAL '30 days'$$);
SELECT cron.schedule('cleanup-mfa-attempts', '30 4 * * *',
  $$DELETE FROM mfa_recovery_attempts WHERE attempted_at < NOW() - INTERVAL '30 days'$$);
SELECT cron.schedule('cleanup-alert-runs', '45 4 * * *',
  $$DELETE FROM alert_runs WHERE run_at < NOW() - INTERVAL '90 days'$$);
SELECT cron.schedule('cleanup-alert-sent-items', '0 5 * * 0',
  $$DELETE FROM alert_sent_items WHERE sent_at < NOW() - INTERVAL '180 days'$$);
SELECT cron.schedule('cleanup-health-checks', '0 3 * * *',
  $$DELETE FROM health_checks WHERE checked_at < NOW() - INTERVAL '30 days'$$);
SELECT cron.schedule('cleanup-incidents', '15 3 * * *',
  $$DELETE FROM incidents WHERE created_at < NOW() - INTERVAL '90 days'$$);
```

### Q4: OAuth token encryption (DB-003)

**CONFIRMED: Tokens ARE encrypted.** This is a false positive in the DRAFT.

Evidence from `backend/oauth.py`:
- Lines 45-77: Fernet cipher initialized from `ENCRYPTION_KEY` env var (base64-encoded 32-byte key)
- Lines 84-109: `encrypt_aes256()` encrypts plaintext using Fernet (AES-256 GCM with HMAC authentication)
- Lines 113-131: `decrypt_aes256()` decrypts ciphertext
- Lines 312-313: `encrypted_access = encrypt_aes256(access_token)` before DB insert
- Lines 374-376: `access_token = decrypt_aes256(token_record["access_token"])` after DB read
- Lines 51-57: Production startup raises `RuntimeError` if `ENCRYPTION_KEY` is not set

The DB-AUDIT.md correctly noted "encryption happens at the application layer (not database)" but the DRAFT incorrectly characterized this as "plaintext." The tokens in the database ARE ciphertext (Fernet tokens are base64-encoded authenticated ciphertext).

**Priority: None needed.** Remove DB-003 from the debt list entirely.

### Q5: JSONB size monitoring (DB-031/032)

**Current table sizes** should be checked with:
```sql
SELECT
  'search_results_cache' AS table_name,
  pg_size_pretty(pg_total_relation_size('search_results_cache')) AS total_size,
  (SELECT count(*) FROM search_results_cache) AS row_count,
  pg_size_pretty((SELECT avg(octet_length(results::text)) FROM search_results_cache)) AS avg_row_size
UNION ALL
SELECT
  'search_results_store',
  pg_size_pretty(pg_total_relation_size('search_results_store')),
  (SELECT count(*) FROM search_results_store),
  pg_size_pretty((SELECT avg(octet_length(results::text)) FROM search_results_store));
```

**Prometheus monitoring:** Yes, add a gauge metric. The cleanest approach is a pg_cron job that writes sizes to a monitoring table, which the backend reads via RPC and exposes as Prometheus gauge:

```python
# In metrics.py
smartlic_db_table_size_bytes = Gauge(
    'smartlic_db_table_size_bytes',
    'Database table total size in bytes',
    ['table_name']
)
```

Update via the existing health check cron (no additional cron needed). This avoids giving the backend direct access to `pg_total_relation_size()`.

### Q6: Disaster Recovery (DB-043)

**Current state:**
- **Supabase PITR:** Available on Pro plan. RPO depends on WAL archiving frequency (typically seconds). RTO is ~30 minutes for full restore.
- **Migration-based recreation:** Never tested. Would require running all 76 migrations in order. Several would fail due to non-idempotent operations (DB-028).
- **No documented procedure exists.**

**Immediate actions (S1):**

1. **Create `supabase/docs/DISASTER-RECOVERY.md`** documenting:
   - Supabase PITR restoration steps
   - Migration order dependencies
   - Post-migration verification queries
   - Manual pg_cron setup steps (since extensions require superuser)
   - Known non-idempotent migrations to skip or patch

2. **Test migration-based recreation** on a fresh Supabase project (can use `supabase start` locally). Document failures.

3. **Add backup verification cron** -- weekly `pg_dump` of schema-only to git for diff detection against migration state.

**Hours:** 16h is correct for the documentation + testing + verification setup.

### Q7: `handle_new_user()` trigger (DB-011) -- migrate to application layer?

**Recommendation: Keep as trigger. Add integration test guard.**

**Arguments to keep as trigger:**

1. **Atomicity** -- Profile creation is guaranteed within the same transaction as `auth.users` INSERT. Application-layer would require intercepting Supabase Auth callbacks (webhook or post-signup API call), creating a window where auth.users exists without a profiles row. During that window, any RLS policy using `auth.uid() = user_id` with a JOIN to profiles would fail.

2. **Multi-entry-point coverage** -- Supabase Auth handles email/password signup, Google OAuth, magic links, and phone OTP. All flow through the same `auth.users` INSERT trigger. Application-layer would need to handle each entry point separately.

3. **Stability** -- The current trigger (migration 20260225110000) is correct, includes all 10 columns, and has `ON CONFLICT (id) DO NOTHING`. The 7 historical modifications were evolutionary development, not inherent trigger fragility. The trigger has been stable for 10+ days.

**Mitigation (3h):**
1. Backend integration test: `test_handle_new_user_trigger.py` that validates all 10 columns are populated after auth.users INSERT
2. CI guard: GitHub Actions step that greps new migration files for `handle_new_user` and flags for mandatory review
3. Canonical comment block in the function listing all expected columns

---

## Resolution Roadmap

### Sprint 1 (Week 1-2) -- Critical & Quick Wins

| # | IDs | Description | Hours | Dependencies |
|---|-----|-------------|-------|-------------|
| 1 | DB-038, DB-039 | Fix RLS indexes (correct table names + classification_feedback index) | 2 | None |
| 2 | DB-013 | Fix partner_referrals NOT NULL vs SET NULL conflict | 1 | None |
| 3 | DB-012 | Consolidate updated_at trigger functions | 2 | None |
| 4 | DB-032, DB-NEW-01 | search_results_store retention pg_cron + 2MB CHECK + 7-day default | 4 | None |
| 5 | DB-025, DB-030 | Bridge migration to consolidate backend/migrations/ | 4 | Q1 verification queries |
| 6 | DB-043 | Write DISASTER-RECOVERY.md + test migration recreation | 16 | DB-025 first |
| **Total S1** | | | **29h** | |

### Sprint 2 (Week 3-4) -- High Priority

| # | IDs | Description | Hours | Dependencies |
|---|-----|-------------|-------|-------------|
| 7 | DB-001, DB-NEW-02 | Standardize auth.role() policies (classification_feedback + partners + partner_referrals) | 2 | None |
| 8 | DB-033, DB-037, DB-NEW-03 | Retention pg_cron jobs (state_transitions 30d, alert_sent_items 180d, health_checks 30d, incidents 90d, mfa_attempts 30d, alert_runs 90d) | 4 | None |
| 9 | DB-007 | Evaluate search_state_transitions RLS subquery optimization | 4 | None |
| 10 | DB-011 | Integration test for handle_new_user() + CI guard | 4 | None |
| 11 | DB-015 | Document plan_type duplication as accepted + add reconciliation cron | 4 | None |
| 12 | DB-002 | Add explicit service_role policies to health_checks/incidents | 1 | None |
| 13 | DB-010 | Ban system cache warmer account (`banned_until`) | 1 | None |
| 14 | DB-040, DB-041 | Drop redundant indexes (alert_preferences, trial_email_log) | 1 | None |
| 15 | DB-018, DB-019 | Add CHECK constraints (cache priority, alert_runs status) | 1 | None |
| 16 | DB-028 | Add IF NOT EXISTS guards to non-idempotent migrations | 4 | None |
| 17 | DB-042 | Add composite index for admin inbox conversations | 1 | None |
| 18 | DB-045 | Document stripe_webhook_events retention implications | 1 | None |
| 19 | DB-021 | Validate billing_period constraint vs legacy data | 1 | None |
| 20 | DB-031 | Add Prometheus gauge for JSONB table sizes | 2 | None |
| **Total S2** | | | **31h** | |

### Backlog (Month 2+)

| IDs | Description | Hours |
|-----|-------------|-------|
| DB-005, DB-006, DB-008 | Document accepted design decisions (mfa_recovery_attempts, trial_email_log, Stripe Price IDs) | 2 |
| DB-009 | Optimize partner RLS cross-schema query | 2 |
| DB-014 | Deprecate legacy stripe_price_id column | 2 |
| DB-016 | Document valid status transitions (CHECK or COMMENT) | 2 |
| DB-017 | Add NOT NULL to created_at columns | 2 |
| DB-020 | Adopt constraint naming convention | 1 |
| DB-022 | Evaluate phone validation enhancement | 1 |
| DB-023 | Review cache UNIQUE constraint implications | 2 |
| DB-024 | Add updated_at to plan_billing_periods | 1 |
| DB-026 | Document migration naming convention for future | 1 |
| DB-027 | Evaluate down-migration strategy | 8 |
| DB-029 | Move Stripe Price IDs to env-driven seeding | 2 |
| DB-034 | Optimize cleanup_search_cache_per_user trigger | 2 |
| DB-035 | Rewrite get_conversations_with_unread_count as JOIN | 2 |
| DB-036 | Plan table partitioning for append-heavy tables | 8 |
| DB-044 | Document pg_cron manual setup steps | 4 |
| DB-046 | Establish "no dashboard schema changes" policy | 1 |
| DB-NEW-04 | Evaluate FK for search_state_transitions | 4 |
| **Total Backlog** | | **~47h** |

---

## Recomendacoes

### Top 5 Recommendations for Database Health

1. **Fix DB-038/039 immediately (RLS indexes).** These are the highest-impact quick wins. Every query from authenticated users against `classification_feedback` triggers a full table scan. The corrective migration takes 15 minutes to write and deploy. This should be done today.

2. **Add retention jobs before user growth (DB-032/033/037/NEW-03).** Six tables grow unbounded. At 50 beta users this is invisible, but at 500 users it becomes the largest line item on Supabase billing. The `search_results_store` is the most urgent because each row stores 100KB-1.5MB of JSONB with no cleanup.

3. **Consolidate backend/migrations/ now (DB-025/030).** The dual-directory problem has already caused one production incident (missing `check_and_increment_quota` RPC). Every day this remains unfixed increases the risk that a fresh database deployment fails. The bridge migration approach is safe and non-destructive.

4. **Document disaster recovery (DB-043).** With 76 migrations and no DR guide, a database failure would require senior engineering intervention to recover. This is an unacceptable operational risk for a production system with paying users (even beta). The PITR procedure should be documented and tested quarterly.

5. **Remove DB-003 from the debt list.** OAuth token encryption IS implemented and working. Keeping a false positive on the debt list erodes trust in the assessment and could misdirect engineering effort.

---

*Review completed 2026-03-07 by @data-engineer (Delta).*
*Methodology: Code-level verification of every DRAFT claim against actual migration SQL files, DB-AUDIT.md findings, and ripgrep across the codebase. All severity adjustments include evidence-based justification.*
*Ready for architect consolidation into FINAL.*
