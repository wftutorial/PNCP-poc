# Database Specialist Review

**Reviewer:** @data-engineer
**Date:** 2026-02-25
**Input:** `docs/prd/technical-debt-DRAFT.md` (Phase 4 Brownfield Discovery)
**Cross-references:** `supabase/docs/DB-AUDIT.md`, `supabase/docs/SCHEMA.md`, backend source code

---

## Tier Validation

### Tier 1 (BLOCKING) -- DB Items

| ID | Debito | Validated? | Severity Correct? | Notes |
|----|--------|------------|-------------------|-------|
| T1-01 | `profiles.subscription_status` missing migration | YES -- confirmed | YES -- BLOCKING | Used in `webhooks/stripe.py` (lines 215, 222, 471, 476), `routes/billing.py` (line 164), `routes/subscriptions.py` (line 240), `routes/user.py` (lines 137-141), `schemas.py` (line 1512). 10+ references across 5 production modules. Column exists in production DB (added via Dashboard) but will be missing on DR rebuild. |
| T1-02 | `profiles.trial_expires_at` missing migration | YES -- confirmed | YES -- BLOCKING | Used in `routes/analytics.py` (line 278), `routes/user.py` (lines 135-136, 152, 185-190), `quota.py` (QuotaInfo dataclass field, lines 294, 675, 690, 718, 731, 795-796, 805). Deeply integrated into quota/billing logic. |
| T1-03 | `user_subscriptions.subscription_status` missing migration | YES -- confirmed | YES -- BLOCKING | Used in `webhooks/stripe.py` (lines 215, 471), `routes/billing.py` (line 164-175). Critical path for Stripe checkout and payment failure handling. `get_subscription_status()` reads this column to determine if subscription is active. |
| T1-04 | `trial_stats.py` references `user_pipeline` table | YES -- confirmed | YES -- BLOCKING | `backend/services/trial_stats.py` line 78: `sb.table("user_pipeline")`. Table does not exist -- correct name is `pipeline_items` (migration 025). This is a runtime error that will surface when trial stats are requested. The corresponding test file (`test_trial_usage_stats.py`) also mocks `user_pipeline`, so tests pass but production breaks. |

**Verdict:** All 4 Tier 1 items are correctly classified as BLOCKING. Severity is accurate. No items should be downgraded.

### Tier 2 (STABILITY) -- DB Items

| ID | Debito | Validated? | Move to Tier? | Notes |
|----|--------|------------|---------------|-------|
| T2-01 | 3 tables FK to `auth.users` instead of `profiles` | YES | Keep Tier 2 | Inconsistency is real. `pipeline_items`, `classification_feedback`, `trial_email_log` reference `auth.users(id)`. Since `profiles.id` FK -> `auth.users(id) ON DELETE CASCADE`, the cascade chain works transitively today. Only breaks if profiles row is deleted independently of auth.users, which current code never does. |
| T2-02 | `classification_feedback` FK missing ON DELETE | YES | Keep Tier 2 | Correct -- defaults to RESTRICT. Blocks user deletion if feedback exists. Fix is bundled with T2-01. |
| T2-03 | JSONB results blob unbounded | YES | Keep Tier 2 | Real concern at scale. The `CHECK (octet_length(...) < 1048576)` constraint is safe to add only if current data is under 1MB. **CAUTION:** Cannot answer what current max size is without production query (see Answers to Architect Q2 below). The 1MB constraint should be tested against production data BEFORE applying. |
| T2-04 | `handle_new_user()` trigger regression | YES -- confirmed worse than stated | **Consider Tier 1.5** | Verified: migration `20260224000000` is the latest version. It inserts ONLY `id, email, full_name, phone_whatsapp`. Missing: `company`, `sector`, `whatsapp_consent`, `plan_type`, `avatar_url`, `context_data`. Additionally, it has NO `ON CONFLICT (id) DO NOTHING` clause -- a duplicate auth user creation will raise an exception instead of gracefully skipping. This affects every new signup in production right now. |
| T2-05 | `search_state_transitions` INSERT not scoped | YES | Keep Tier 2 | Low risk -- audit log injection is not a revenue-impacting issue. |
| T2-06 | `classification_feedback` admin policy uses `auth.role()` | YES | **Move to Tier 3** | Functional correctness is fine. The per-row evaluation overhead is negligible for this table (feedback rows are few). This is a style/convention issue. |
| T2-07 | `profiles` missing service_role ALL policy | YES | Keep Tier 2 | Defense-in-depth. Service_role bypasses RLS today, but explicit policy is good practice for enterprise. |
| T2-08 | `conversations`/`messages` missing service_role policies | YES | Keep Tier 2 | Same rationale as T2-07. |
| T2-09 | `search_sessions` missing composite index | YES | Keep Tier 2 | The composite `(user_id, status, created_at DESC)` will help cron cleanup and SIGTERM queries. Low risk addition. |
| T2-10 | No GIN indexes on `sectors`/`ufs` arrays | YES -- but lower priority than stated | **Move to Tier 3** | Verified: `routes/analytics.py` fetches ALL sessions for a user (`eq("user_id", user_id)`) and aggregates in Python. No `@>` array containment queries at the DB level. GIN indexes only help if future code adds DB-level array filtering. Currently, the `(user_id, created_at DESC)` index covers the query. |
| T2-12 | `trial_email_log` RLS enabled but no policies | YES | **Move to Tier 3** | Zero functional impact. Service_role bypasses RLS. Adding an explicit policy is documentation, not stability. |
| T2-15 | `time.sleep(0.3)` in `quota.py` | **NO -- ALREADY FIXED** | **Remove from DRAFT** | Verified: `quota.py` lines 1101, 1191, 1259 all use `await asyncio.sleep(0.3)`. This debt no longer exists. The DRAFT references stale information. |

**Summary of recommended tier changes:**
- T2-04: Escalate urgency -- affects every new signup NOW
- T2-06: Demote to Tier 3 (convention only)
- T2-10: Demote to Tier 3 (no current DB-level array queries)
- T2-12: Demote to Tier 3 (zero functional impact)
- T2-15: Remove entirely (already fixed)

---

## Migration SQL Review

### T1 Migration SQL (T1-01, T1-02, T1-03)

**Safe?** YES -- all use `ADD COLUMN IF NOT EXISTS`, making them idempotent. On production where columns already exist (added via Dashboard), these are no-ops. On a fresh DB rebuild, they create the columns.

**Missing from DRAFT migration:**

1. **CHECK constraint for `profiles.subscription_status`** -- The DB-AUDIT.md proposed `CHECK (subscription_status IN ('trial', 'active', 'canceling', 'past_due', 'expired'))` but the DRAFT migration omits it. I recommend adding it. The code explicitly sets these 5 values and no others. However, note that `routes/subscriptions.py` line 240 also sets `"canceling"`, which is already in the list, so it is safe.

2. **CHECK constraint for `user_subscriptions.subscription_status`** -- DB-AUDIT.md proposed `CHECK (subscription_status IN ('active', 'trialing', 'past_due', 'canceled', 'expired'))`. The DRAFT omits it. I recommend adding it.

3. **Index on `profiles.trial_expires_at`** -- Not critical for now, but as user count grows, queries filtering expired trials will benefit from a partial index: `WHERE trial_expires_at IS NOT NULL AND trial_expires_at < now()`. Can be deferred.

**Verdict:** The T1 migration SQL is safe for production. The `IF NOT EXISTS` clauses handle idempotency correctly.

### T2 Migration SQL

**T2-01/T2-02 (FK standardization):**
- **Safe?** YES with caution. The `DO $$ ... END $$` blocks correctly check constraint existence before dropping/creating. However, there is a subtle risk: if data exists in `pipeline_items` where `user_id` does NOT have a matching `profiles.id` (orphaned data), the new FK will fail to create. **Recommendation:** Add a pre-check query in the migration or use `NOT VALID` initially:
  ```sql
  ALTER TABLE pipeline_items ADD CONSTRAINT ... FOREIGN KEY ... NOT VALID;
  ALTER TABLE pipeline_items VALIDATE CONSTRAINT ...;
  ```
  This two-phase approach prevents a full table lock during validation.

**T2-04 (handle_new_user trigger):**
- **Safe?** The proposed trigger in the DRAFT is significantly better than the current production version. It restores `company`, `sector`, `whatsapp_consent`, `plan_type`, `avatar_url`, `context_data`, and includes `ON CONFLICT (id) DO NOTHING`.
- **Issue:** The current production trigger (migration 20260224000000) has NO `ON CONFLICT` clause. If this migration is applied to production, it will replace the current trigger. The proposed version is strictly better.
- **Testing required:** Must test the full signup flow after deploying. Verify metadata fields propagate from `auth.users.raw_user_meta_data` to `profiles`.

**T2-05 through T2-12 (RLS policies + indexes):**
- **Safe?** YES. All use `DROP POLICY IF EXISTS` before `CREATE POLICY`, making them idempotent.
- **Note on `CREATE INDEX IF NOT EXISTS`:** These are non-blocking by default in PostgreSQL, but creating indexes on tables with active writes can cause brief performance dips. For a production deployment during low traffic, this is acceptable. For a larger deployment, use `CREATE INDEX CONCURRENTLY`.

**Transaction safety:**
- The entire migration is wrapped in `BEGIN; ... COMMIT;`. This is correct for policy and column changes.
- However, `CREATE INDEX CONCURRENTLY` cannot run inside a transaction. If concurrent index creation is needed, the indexes (T2-09, T2-10) should be in a separate migration file without the transaction wrapper.
- **Recommendation:** Keep the current `BEGIN/COMMIT` approach for simplicity at this scale. Switch to `CONCURRENTLY` when table sizes exceed 100K rows.

### Missing Items from Migration

1. **`profiles.subscription_end_date`** -- Used in `routes/subscriptions.py` line 241 (`"subscription_end_date": ends_at_iso`). No migration creates it. Should be added to T1 migration.

2. **`profiles.email_unsubscribed`** -- Used in `search_pipeline.py` line 79 (SELECT), line 82 (conditional check), `routes/emails.py` line 147 (UPDATE). No migration creates it.

3. **`profiles.email_unsubscribed_at`** -- Used in `routes/emails.py` line 148 (UPDATE alongside `email_unsubscribed`). No migration creates it.

These 3 columns are the same category as T1-01/T1-02/T1-03 -- used in production code, exist in production DB (added via Dashboard), but have no migration. They should be included in the Tier 1 consolidated migration.

---

## Missed Items

### MISSED-01: `profiles.subscription_end_date` missing migration [CRITICAL -- same as T1-01 pattern]

**Evidence:** `backend/routes/subscriptions.py` line 241:
```python
sb.table("profiles").update({
    "subscription_status": "canceling",
    "subscription_end_date": ends_at_iso,
    ...
}).eq("id", user_id).execute()
```

No migration creates this column. On a fresh DB, subscription cancellation will silently fail (Supabase ignores unknown columns on update, but the data is lost).

**Remediation:**
```sql
ALTER TABLE public.profiles
    ADD COLUMN IF NOT EXISTS subscription_end_date TIMESTAMPTZ;

COMMENT ON COLUMN profiles.subscription_end_date IS
    'When subscription access ends after cancellation. Set during cancel flow.';
```

### MISSED-02: `profiles.email_unsubscribed` missing migration [HIGH]

**Evidence:** `backend/search_pipeline.py` line 79:
```python
profile = sb.table("profiles").select("email, full_name, email_unsubscribed").eq("id", user_id).single().execute()
```
`backend/routes/emails.py` line 147:
```python
sb.table("profiles").update({
    "email_unsubscribed": True,
    ...
})
```

On a fresh DB, the SELECT will return `null` for this column (Supabase returns null for unknown columns in some configurations, or may error). The unsubscribe flow writes to a non-existent column.

**Remediation:**
```sql
ALTER TABLE public.profiles
    ADD COLUMN IF NOT EXISTS email_unsubscribed BOOLEAN DEFAULT FALSE;
ALTER TABLE public.profiles
    ADD COLUMN IF NOT EXISTS email_unsubscribed_at TIMESTAMPTZ;

COMMENT ON COLUMN profiles.email_unsubscribed IS
    'Whether user has opted out of marketing emails. LGPD compliance.';
```

### MISSED-03: `test_trial_usage_stats.py` mocks `user_pipeline` -- test masks production bug (T1-04 related)

The test file `backend/tests/test_trial_usage_stats.py` (lines 70, 79, 151, 188) mocks the Supabase table call with `user_pipeline`, which means tests pass but production breaks. When T1-04 is fixed (changing to `pipeline_items`), the test file must also be updated to mock `pipeline_items`.

### MISSED-04: Current `handle_new_user()` trigger lacks `ON CONFLICT (id) DO NOTHING`

The production trigger (migration 20260224000000) does a plain `INSERT INTO public.profiles` with NO conflict handling. If a profile row already exists for a given `auth.users.id` (possible in edge cases like re-signup after auth deletion/recreation), the trigger will throw a unique violation error and the entire auth.users INSERT will fail, blocking user registration entirely.

The DRAFT's proposed fix (T2-04) correctly includes `ON CONFLICT (id) DO NOTHING`. This is important to deploy.

---

## Effort Estimates

| ID | Item | Hours | Complexity | Notes |
|----|------|-------|------------|-------|
| T1-01 | `profiles.subscription_status` migration | 0.25h | Low | `ADD COLUMN IF NOT EXISTS` |
| T1-02 | `profiles.trial_expires_at` migration | 0.25h | Low | `ADD COLUMN IF NOT EXISTS` |
| T1-03 | `user_subscriptions.subscription_status` migration | 0.25h | Low | `ADD COLUMN IF NOT EXISTS` |
| T1-04 | Fix `user_pipeline` -> `pipeline_items` in code + tests | 0.5h | Low | 2 files: `trial_stats.py` + `test_trial_usage_stats.py` |
| MISSED-01 | `profiles.subscription_end_date` migration | 0.25h | Low | Same pattern as T1-01 |
| MISSED-02 | `profiles.email_unsubscribed` + `email_unsubscribed_at` migration | 0.25h | Low | Same pattern as T1-01 |
| T2-01/02 | FK standardization (3 tables) | 1.0h | Medium | Needs orphan data check before apply |
| T2-03 | JSONB size constraint + pg_cron cleanup | 2.0h | Medium | Requires production data size check first |
| T2-04 | `handle_new_user()` trigger rewrite | 1.5h | Medium | Must test full signup flow (email, Google OAuth, metadata propagation) |
| T2-05 | `search_state_transitions` INSERT policy scoping | 0.25h | Low | Simple policy rewrite |
| T2-06 | `classification_feedback` admin policy rewrite | 0.25h | Low | Convention change only |
| T2-07 | `profiles` service_role ALL policy | 0.25h | Low | Additive policy |
| T2-08 | `conversations`/`messages` service_role policies | 0.25h | Low | Additive policies |
| T2-09 | `search_sessions` composite index | 0.25h | Low | `CREATE INDEX IF NOT EXISTS` |
| T2-10 | GIN indexes on `sectors`/`ufs` arrays | 0.25h | Low | No current query benefit, future-proofing |
| T2-12 | `trial_email_log` explicit service_role policy | 0.15h | Low | Documentation policy |
| **Migration testing** | Full regression: signup, billing, search, trial stats | 2.0h | Medium | Stripe webhook flow, new user signup, analytics |
| **Total T1 + missed** | | **1.75h** | | |
| **Total T2 DB** | | **6.15h** | | |
| **Total with testing** | | **9.90h** | | ~1.25 working days |

---

## Recommended Execution Order

### Phase 1: Immediate (Day 1 morning) -- 2 hours total

1. **Migration A: All missing columns** (T1-01 + T1-02 + T1-03 + MISSED-01 + MISSED-02)
   - Single migration file: `20260225100000_add_missing_profile_columns.sql`
   - All `ADD COLUMN IF NOT EXISTS` -- zero risk, no data changes
   - Dependencies: None
   - **Must deploy before Phase 2**

2. **Code fix: T1-04 + MISSED-03** (parallel with Migration A)
   - Fix `backend/services/trial_stats.py`: `user_pipeline` -> `pipeline_items`
   - Fix `backend/tests/test_trial_usage_stats.py`: update mock table name
   - Run: `pytest tests/test_trial_usage_stats.py -v`

3. **Validation**
   - Run `pytest` -- full backend suite
   - Verify Stripe webhook handler in staging/production logs
   - Verify `/me` endpoint returns `subscription_status` and `trial_expires_at`

### Phase 2: Stability Sprint 1 (Day 1 afternoon) -- 3 hours total

4. **Migration B: `handle_new_user()` trigger** (T2-04 + MISSED-04)
   - Separate migration: `20260225110000_fix_handle_new_user_trigger.sql`
   - **Must test signup flow after deployment** (email signup + Google OAuth)
   - Dependencies: Phase 1 complete (new columns must exist before trigger references them)

5. **Migration C: FK standardization** (T2-01 + T2-02)
   - Separate migration: `20260225120000_standardize_fks_to_profiles.sql`
   - Pre-check: verify no orphaned `user_id` values in `pipeline_items`, `classification_feedback`, `trial_email_log`
   - Dependencies: None (but logically after Phase 1)

### Phase 3: Stability Sprint 2 (Day 2) -- 4 hours total

6. **Migration D: RLS policies** (T2-05 + T2-07 + T2-08)
   - Combined migration: `20260226100000_rls_policy_hardening.sql`
   - Dependencies: None

7. **Migration E: Indexes** (T2-09)
   - Separate migration: `20260226110000_add_session_composite_index.sql`
   - Dependencies: None

8. **Migration F: JSONB governance** (T2-03)
   - Requires production data size check first (see Answers to Architect Q2)
   - If max JSONB size < 1MB: add CHECK constraint safely
   - If max JSONB size >= 1MB: must clean up offending rows first, then add constraint
   - pg_cron cleanup job for entries > 7 days with priority = 'cold'
   - Dependencies: Data size verification

### Phase 4: Low-priority cleanup (Backlog)

9. T2-06 (classification_feedback policy convention) -- demoted to Tier 3
10. T2-10 (GIN indexes) -- demoted to Tier 3, no current query benefit
11. T2-12 (trial_email_log explicit policy) -- demoted to Tier 3

**Why separate migration files instead of one consolidated migration:**
- Smaller blast radius on failure
- Easier to identify which change caused an issue
- T2-04 (trigger) requires separate testing (signup flow)
- T2-03 (JSONB) may need data cleanup before constraint
- Indexes can cause brief performance dips and should be isolated

---

## Answers to Architect

### Q1: Missing columns -- do they exist in production?

> Can you confirm via `SELECT column_name FROM information_schema.columns WHERE table_name = 'profiles'` that `subscription_status` and `trial_expires_at` already exist in the production database?

**Answer:** I cannot run production queries without direct database access. However, the evidence strongly indicates YES:

- The application is live at smartlic.tech with active users
- Stripe webhook handling writes `subscription_status` on every checkout (line 215) and payment failure (line 471) -- if the column did not exist, these would error and no subscription would ever activate
- The `/me` endpoint returns `subscription_status` (tested by `test_api_me.py` tests 119, 161, 200 which validate specific values)
- `trial_expires_at` is read in `routes/analytics.py` line 278 -- if missing, the trial value analytics page would crash

**Recommendation:** The migration MUST use `ADD COLUMN IF NOT EXISTS` (as already proposed in the DRAFT) for idempotency. This handles both cases: on production (no-op) and on fresh DB (creates column).

### Q2: JSONB results blob size

> What is the current `avg(octet_length(results::text))` and `max(octet_length(results::text))` in `search_results_cache`?

**Answer:** I cannot query production data directly. However, I can estimate from code analysis:

- Each licitacao result contains: `objeto` (text, ~200 chars), `orgao` (text, ~100 chars), `valor` (number), `uf`, `data_publicacao`, `modalidade`, plus LLM classification metadata (~500 bytes per item)
- With `tamanhoPagina=50` per PNCP page, a multi-UF search could return 100-500 results after dedup
- **Estimated range:** 50KB-500KB per entry, with outliers up to 1MB for large multi-UF searches with 500+ results
- The 10-entry-per-user limit (migration 032) caps user storage at ~5MB worst case

**Recommendation:**
1. Run this query on production BEFORE adding the CHECK constraint:
   ```sql
   SELECT
     count(*) as total_entries,
     avg(octet_length(results::text)) as avg_bytes,
     max(octet_length(results::text)) as max_bytes,
     count(*) FILTER (WHERE octet_length(results::text) > 1048576) as over_1mb
   FROM search_results_cache;
   ```
2. If `over_1mb > 0`, either:
   - Increase the CHECK limit to 2MB, or
   - Truncate oversized entries (compress/trim results array) before adding constraint
3. The pg_cron cleanup is safe to add regardless of current sizes

### Q3: `handle_new_user()` current version in production

> What is the current version of this function in production?

**Answer:** The latest migration modifying this function is `20260224000000_phone_email_unique.sql`. Based on migration ordering, this is the version running in production. I verified its content:

```sql
-- Current production version (20260224000000)
INSERT INTO public.profiles (id, email, full_name, phone_whatsapp)
VALUES (
    NEW.id, NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'full_name', ''),
    _phone
);
```

**Key differences from the DRAFT's proposed fix:**
| Field | Current (production) | Proposed (DRAFT T2-04) |
|-------|---------------------|----------------------|
| `id` | YES | YES |
| `email` | YES | YES |
| `full_name` | YES | YES |
| `phone_whatsapp` | YES | YES |
| `company` | **MISSING** | YES |
| `sector` | **MISSING** | YES |
| `whatsapp_consent` | **MISSING** | YES |
| `plan_type` | **MISSING** (relies on DEFAULT) | YES (`'free_trial'`) |
| `avatar_url` | **MISSING** | YES |
| `context_data` | **MISSING** | YES (`'{}'::jsonb`) |
| `ON CONFLICT` | **MISSING** | YES (`DO NOTHING`) |
| Phone uniqueness check | YES (raises exception) | YES (same logic) |

**Impact of current production version:** Every new user registered since migration 20260224000000 was deployed has `company = NULL`, `sector = NULL`, `whatsapp_consent = NULL` (not `FALSE`), `context_data = NULL` (not `'{}'::jsonb`). If the signup form collects these fields, the data is silently discarded by the trigger.

### Q4: Array column analytics queries

> Are there any current analytics queries that filter by `sectors @> ARRAY['X']` pattern?

**Answer:** NO. I searched all backend Python code. The analytics endpoint (`routes/analytics.py` lines 210-232) fetches all sessions for a user and iterates in Python:

```python
sessions_result = db.table("search_sessions")
    .select("ufs, sectors, valor_total")
    .eq("user_id", user_id)
    .execute()

for s in sessions:
    for sector in (s.get("sectors") or []):
        sectors_agg[sector]["count"] += 1
```

No `@>` or `.contains()` or `.cs()` operators are used at the Supabase query level. GIN indexes would provide zero benefit for current queries.

**Recommendation:** Demote T2-10 (GIN indexes) to Tier 3. Add them only when/if DB-level array filtering is introduced.

### Q5: `search_state_transitions` row count and cleanup

> How many rows exist? Is there a pg_cron job cleaning old records?

**Answer:** I cannot query production row count. From code analysis:

- **No pg_cron cleanup exists** for this table. Verified: no migration creates a cron schedule for `search_state_transitions`.
- Each search generates 2-4 transitions (CREATED -> PROCESSING -> COMPLETED/FAILED). With the `search_state_transitions.search_id` having no FK (intentional fire-and-forget design, DB-AUDIT-026), orphaned rows are expected.
- **Growth estimate:** At 100 searches/day, this is ~300-400 rows/day, ~10K/month, ~120K/year. At this scale, a monthly cleanup of rows > 90 days old is sufficient.

**Recommendation:** Add pg_cron cleanup as a Tier 3 item (not urgent):
```sql
SELECT cron.schedule('cleanup-state-transitions', '0 3 * * 0',
    $$DELETE FROM search_state_transitions WHERE created_at < NOW() - INTERVAL '90 days'$$);
```
Requires `pg_cron` extension to be enabled on Supabase project.

---

## Enterprise Readiness Assessment

### Data Integrity Guarantees

| Aspect | Current State | Gap | Priority |
|--------|--------------|-----|----------|
| FK consistency | 3 of 18 tables still reference `auth.users` instead of `profiles` | T2-01/02 fixes this | Sprint 1 |
| Column migrations | 5 columns exist in production but not in migrations (3 in DRAFT + 2 missed) | T1-01/02/03 + MISSED-01/02 | Immediate |
| Trigger correctness | `handle_new_user()` drops 6 fields on every new signup | T2-04 | Sprint 1 |
| CHECK constraints | `subscription_status` columns lack value constraints | Add with T1 migration | Immediate |
| NOT NULL enforcement | `email_unsubscribed` should default to FALSE, not NULL | Add with MISSED-02 | Immediate |

**Assessment:** Data integrity is functional but fragile. The 5 missing column migrations are the highest risk -- a disaster recovery rebuild would produce a broken schema. Once these are formalized, the integrity baseline is acceptable for enterprise beta.

### Backup/Recovery Capability

| Aspect | Current State | Gap |
|--------|--------------|-----|
| Schema reproducibility | PARTIAL -- 5 columns and current trigger state not captured in migrations | T1 + MISSED items fix this |
| Rollback scripts | NONE for any migration (DB-AUDIT-018) | Low priority -- `ADD COLUMN IF NOT EXISTS` is safe to re-run |
| Point-in-time recovery | Supabase provides PITR on Pro plan | Verify PITR is enabled |
| Migration idempotency | GOOD -- most migrations use `IF NOT EXISTS` / `IF EXISTS` guards | No action needed |

**Assessment:** The critical gap is that 5 production columns are not in migrations. Once Phase 1 migrations are applied, the schema is fully reproducible. Rollback scripts remain a Tier 3 concern -- at POC stage, forward-only migrations with `IF NOT EXISTS` guards are acceptable.

### RLS Coverage

| Table | RLS Enabled | User Policies | Service Role Policy | Gap |
|-------|-------------|---------------|--------------------|----|
| `profiles` | YES | SELECT, UPDATE, INSERT (own) | INSERT only | Missing ALL policy (T2-07) |
| `plans` | YES | SELECT (public) | NONE | Low risk -- read-only public data |
| `user_subscriptions` | YES | SELECT (own) | ALL | OK |
| `plan_features` | YES | SELECT (active) | NONE | Low risk -- reference data |
| `monthly_quota` | YES | SELECT (own) | ALL | OK |
| `search_sessions` | YES | SELECT, INSERT (own) | ALL | OK |
| `search_results_cache` | YES | SELECT (own) | ALL | OK |
| `search_state_transitions` | YES | SELECT (own) | INSERT (not scoped!) | T2-05 |
| `pipeline_items` | YES | Full CRUD (own) | ALL | OK |
| `conversations` | YES | Admin-aware SELECT | NONE | T2-08 |
| `messages` | YES | Admin-aware SELECT/INSERT | NONE | T2-08 |
| `stripe_webhook_events` | YES | NONE | ALL | OK -- backend only |
| `classification_feedback` | YES | SELECT/INSERT (own) | `auth.role()` pattern | T2-06 |
| `trial_email_log` | YES | NONE | NONE | T2-12 |
| `audit_events` | YES | SELECT (admin-only) | ALL | OK |

**Assessment:** All 18 tables have RLS enabled. The gaps are defense-in-depth (service_role bypasses RLS anyway). T2-05 (state transitions INSERT scoping) is the only one with a real exploitable gap, and even that is low-impact (audit log injection). For enterprise readiness, applying T2-05, T2-07, and T2-08 is recommended.

### Orphaned Data Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| `pipeline_items` FK to `auth.users` (not profiles) | Medium | T2-01 repoints to profiles with CASCADE |
| `classification_feedback` FK to `auth.users` with RESTRICT | Medium | T2-01/02 fixes cascade |
| `trial_email_log` FK to `auth.users` | Low | T2-01 repoints |
| `search_state_transitions` no FK on `search_id` | Low | Intentional -- fire-and-forget design (DB-AUDIT-026) |
| `search_results_cache` -- cold entries grow unbounded | Medium | T2-03 adds cleanup |

**Assessment:** Orphan risk is low. The FK repointing (T2-01) is the main fix. The `search_state_transitions` no-FK design is acceptable for audit logs.

### Audit Trail Capability

| Capability | Current State |
|------------|--------------|
| Auth events | Supabase Auth logs (built-in) |
| Search state transitions | `search_state_transitions` table (fire-and-forget) |
| Stripe events | `stripe_webhook_events` table (full event storage) |
| Profile changes | `profiles.updated_at` trigger (timestamp only, no before/after) |
| Admin actions | `audit_events` table (admin operations logged) |
| Email history | `trial_email_log` (email send records) |

**Assessment:** Audit trail covers critical paths (auth, billing, search). The gap is **before/after tracking on profile changes** -- currently only `updated_at` is bumped. For enterprise-grade, consider adding a `profile_changes` audit log or using Supabase's built-in audit extension. This is a Tier 3 concern for future.

---

## Summary

The DRAFT is fundamentally sound. The Tier 1 items are correctly identified and truly blocking for disaster recovery scenarios. My review adds:

1. **3 additional missing columns** (MISSED-01, MISSED-02) that follow the same pattern as T1-01/02/03 and should be included in the same migration
2. **T2-15 should be removed** -- already fixed in codebase
3. **T2-06, T2-10, T2-12 should be demoted** to Tier 3
4. **T2-04 urgency should be elevated** -- it silently drops 6 profile fields on every new user signup in production right now
5. **Phase 1 migration should be expanded** to include 5 missing columns (not 3)
6. **Separate migration files** recommended over one consolidated migration for safety

**Total estimated effort:** ~10 hours (1.25 working days) for all Tier 1 + Tier 2 items including testing.

---

*Reviewed by @data-engineer during Phase 5 of SmartLic Brownfield Discovery.*
*Methodology: Code-level verification of every DRAFT claim against actual source files in `backend/` and `supabase/migrations/`.*
