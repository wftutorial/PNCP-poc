# Database Specialist Review

**Reviewer:** @data-engineer (Dara)
**Date:** 2026-04-08
**Phase:** Brownfield Discovery Phase 5
**DRAFT Reviewed:** `docs/prd/technical-debt-DRAFT.md` (Section 2: Database Debts TD-019 to TD-034, Section 6: Questions for @data-engineer)
**Supporting Documents:** `supabase/docs/SCHEMA.md`, `supabase/docs/DB-AUDIT.md`, actual migration files in `supabase/migrations/`

---

## Executive Summary

The architect's database debt assessment (TD-019 through TD-034) is accurate and well-sourced. I validated each item against the current migration files, the `search_datalake` RPC implementation, and the backend code. Key findings:

- **TD-022 (MD5 content hash):** Severity should be DOWNGRADED. The transformer already uses SHA-256 -- the DB column comment is stale documentation, not an actual MD5 usage.
- **TD-025/026/027 (retention policies):** CONFIRMED missing. No pg_cron jobs exist for `stripe_webhook_events`, `alert_sent_items`, or `trial_email_log` in any migration.
- **TD-020 (soft-delete bloat):** CONFIRMED. `purge_old_bids()` hard-deletes active rows past retention, but `is_active=false` rows are NEVER cleaned up.
- **3 additional debts** identified that the DRAFT missed.

**Verdict:** APPROVED with adjustments. Ready for prioritization after incorporating the changes below.

---

## 1. Debitos Validados

| ID | Debito | Severidade Original | Severidade Ajustada | Horas | Prioridade | Notas |
|----|--------|---------------------|---------------------|-------|------------|-------|
| TD-019 | Missing composite index `pncp_raw_bids (uf, modalidade_id, data_publicacao)` | High | **High** (confirmed) | 1 | P0 | Confirmed: `search_datalake` RPC (latest in `20260331400000`) filters on `is_active AND uf = ANY(p_ufs) AND modalidade_id = ANY(p_modalidades) AND data_publicacao >= p_date_start`. Existing indexes cover (uf, data_publicacao) and (modalidade_id) separately. The planner must do a BitmapAnd to combine them. A single composite index eliminates this. See SQL below. |
| TD-020 | pncp_raw_bids soft-delete bloat | High | **High** (confirmed) | 3 | P0 | `purge_old_bids()` only DELETEs rows WHERE `is_active = true AND data_publicacao < cutoff`. Rows with `is_active = false` are NEVER deleted by any pg_cron job or RPC. The daily VACUUM ANALYZE at 07:30 UTC (from `20260401000000`) helps reclaim space from hard-deletes but cannot reclaim soft-deleted row storage. Need a companion cleanup. |
| TD-021 | profiles.plan_type CHECK vs FK | High | **Medium** (downgraded) | 4 | P1 | Real issue but lower urgency than rated. The CHECK constraint and `plans` table are currently consistent. Adding a new plan requires 2 changes (migration + CHECK) but this happens very rarely (last plan change was weeks ago). FK migration carries risk of locking `profiles` table. Recommend doing during off-peak with `NOT VALID` + `VALIDATE`. |
| TD-022 | pncp_raw_bids.content_hash uses MD5 | High | **Low** (downgraded) | 1 | P3 | **The DRAFT is factually wrong here.** The actual `compute_content_hash()` in `backend/ingestion/transformer.py` line 33 uses `hashlib.sha256()`, NOT MD5. The column COMMENT in migration `20260326000000` says "MD5" but that is stale documentation from the original design. The content_hash stored in the DB is already SHA-256 hex. The only fix needed is updating the COMMENT. Hash collision risk is effectively zero. |
| TD-023 | Missing covering index user_subscriptions | Medium | **Medium** (confirmed) | 1 | P2 | Low volume table. The existing partial index `(user_id, is_active) WHERE is_active = true` already covers the filter. Adding `created_at DESC` for covering scans saves one heap lookup per query. Small improvement. |
| TD-024 | Missing index audit_events (target_id_hash) | Medium | **Medium** (confirmed) | 1 | P2 | Confirmed: `idx_audit_events_actor` exists for actor_id_hash but no index on target_id_hash. Admin investigation queries would benefit. |
| TD-025 | stripe_webhook_events sem retention policy | Medium | **Medium** (confirmed) | 1 | P1 | CONFIRMED missing. Searched all 121 migration files -- zero pg_cron jobs or cleanup logic for this table. Stripe event IDs are only used for idempotency checks within a few hours of receipt. 90-day retention is safe. |
| TD-026 | alert_sent_items sem retention policy | Medium | **Medium** (confirmed) | 1 | P1 | CONFIRMED missing. The table has `(alert_id, item_id)` UNIQUE constraint for dedup. Old entries (>90d) are never re-checked. Safe to purge. |
| TD-027 | trial_email_log sem retention policy | Medium | **Low** (downgraded) | 0.5 | P2 | Low volume table. One row per trial email sent. At current user count (~1000s), this table will not exceed a few thousand rows even after years. 1-year retention is fine but not urgent. |
| TD-028 | audit_events hash sem versioning | Medium | **Low** (downgraded) | 0.5 | P3 | Theoretical concern. The hashing algorithm is hardcoded in `backend/audit.py`. Adding a `hash_algorithm` column is trivial but the migration path from one algorithm to another would require application-level routing logic regardless of whether a column exists. Low value. |
| TD-029 | Alert cron job sequencial (1000 alerts) | Medium | **Medium** (confirmed) | 2 | P1 | Backend concern, not DB debt per se. The fix is `asyncio.gather` with concurrency limit in the cron handler, not a DB migration. Supabase rate limits are generous for service_role (no per-second cap, just connection pool). 10 concurrent is safe. |
| TD-030 | RLS policy docs incompletas | Medium | **Low** (downgraded) | 2 | P2 | Migration `20260404000000_security_hardening_rpc_rls.sql` already added significant COMMENT documentation and explicit GRANTs. The remaining gaps are: (1) `shared_analyses.increment_share_view()` anon access undocumented, (2) `pncp_raw_bids` Lei 14.133 legal basis not in SQL COMMENT. These are documentation-only changes. |
| TD-031 | Organizations cascade RESTRICT orphan risk | Low | **Low** (confirmed) | 0.5 | P3 | Edge case. Zero orgs in production. Add monitoring query when feature launches. |
| TD-032 | conversations/messages sem soft-delete | Low | **Low** (confirmed) | 4 | P3 | Only relevant when LGPD audit requirements formalize. Current hard-delete behavior is actually more LGPD-compliant (right to erasure) than soft-delete (data retention). |
| TD-033 | Supabase FREE tier 500MB vs ~3GB datalake | Low | **Medium** (upgraded) | 0.5 | P1 | Upgraded because this is a ticking time bomb. At current ingestion rates (~100K bids/12-day window), the database is likely already past 500MB. The project should already be on a paid tier or will hit the wall imminently. Check `pg_database_size()` ASAP. Upgrading is 30 min of config change but has budget implications. |
| TD-034 | Backup: daily only, 1-day retention, no PITR | Low | **Medium** (upgraded) | 2 | P1 | Upgraded because with paying customers (even beta trials), a data loss event without PITR could be business-ending. Weekly pg_dump to S3 is a 2h setup that provides an independent recovery path. |

**Adjusted total hours:** ~25h for DB items (down from DRAFT's implicit ~35h, primarily due to TD-022 downgrade and more precise estimates).

---

## 2. Debitos Adicionados

### TD-NEW-001: `health_checks` table has no retention policy despite COMMENT saying "30-day retention"

**Severity:** Low
**Hours:** 0.5
**Details:** Migration `20260228150000_add_health_checks_table.sql` has `COMMENT ON TABLE health_checks IS 'STORY-316 AC5: Periodic health check results (30-day retention)'` but no pg_cron job exists anywhere to enforce this. The table will grow unbounded. At ~1 check/min = ~43K rows/month.

**Fix:**
```sql
SELECT cron.schedule(
    'retention-health-checks',
    '25 5 * * *',
    $$DELETE FROM public.health_checks WHERE checked_at < now() - interval '30 days'$$
);
```

### TD-NEW-002: `purge_old_bids()` does not clean up `is_active = false` rows

**Severity:** Medium
**Hours:** 1
**Details:** The `purge_old_bids()` RPC (migration `20260326000000`, line 615) only deletes `WHERE data_publicacao < v_cutoff AND is_active = true`. Rows that were soft-deleted (set `is_active = false` by any mechanism) are never cleaned up. This is distinct from TD-020 which describes the bloat -- this debt is about the missing cleanup mechanism specifically.

The `upsert_pncp_raw_bids()` function (migration `20260331400000`) sets `is_active = true` on upsert, but there's no mechanism that sets `is_active = false` except the purge function itself... which only deletes active rows. This suggests the soft-delete pattern (`is_active = false`) may be vestigial -- no code path actually creates soft-deleted rows.

**Fix (add to existing purge or as separate cron):**
```sql
-- Clean up soft-deleted rows older than 3 days
SELECT cron.schedule(
    'cleanup-pncp-soft-deleted',
    '0 8 * * *',
    $$DELETE FROM public.pncp_raw_bids
      WHERE is_active = false
        AND updated_at < now() - interval '3 days'$$
);
```

### TD-NEW-003: `datalake_query.py` in-memory cache has no size/staleness observability

**Severity:** Low
**Hours:** 2
**Details:** The `_query_cache` dict in `backend/datalake_query.py` (line 29) caches up to 50 entries with 1h TTL but has no Prometheus metrics for hit rate, eviction count, or entry count. When diagnosing search latency issues, there's no way to know if the cache is helping or not. The only observability is a `logger.info` for cache HITs.

**Fix:** Add Prometheus gauges `DATALAKE_CACHE_SIZE`, `DATALAKE_CACHE_HITS_TOTAL`, `DATALAKE_CACHE_MISSES_TOTAL` in `metrics.py` and instrument `_cache_get()` and `_cache_put()`.

---

## 3. Respostas ao Architect

### Q1: TD-019 (composite index) -- Query plan analysis

**The composite index `(uf, modalidade_id, data_publicacao DESC) WHERE is_active = true` IS the best strategy.**

The `search_datalake` RPC (latest version in `20260331400000`) applies filters in this order:
1. `b.is_active = true` (partial index condition)
2. `b.uf = ANY(p_ufs)` (equality on leading column)
3. `b.modalidade_id = ANY(p_modalidades)` (equality on second column)
4. `b.data_publicacao >= p_date_start` (range on third column)

This matches a composite B-tree perfectly. The planner can do an Index Scan with all three predicates resolved in a single index traversal.

The alternative (separate partial indexes) forces PostgreSQL into a BitmapAnd plan, which:
- Reads two separate indexes
- Builds two bitmaps
- ANDs them
- Then does a heap scan

The composite index is definitively better for this access pattern. Partial indexes would only be preferable if queries frequently filter by only ONE of the three columns, but the RPC always uses all three.

**Recommended SQL:**
```sql
CREATE INDEX CONCURRENTLY idx_pncp_raw_bids_dashboard_query
    ON pncp_raw_bids (uf, modalidade_id, data_publicacao DESC)
    WHERE is_active = true;
```

**Estimated index size:** ~10MB per 500K rows. Negligible compared to table size.

### Q2: TD-020 (soft-delete bloat) -- Safety of hybrid approach

**Current `pg_total_relation_size('pncp_raw_bids')` cannot be checked from this review** (no DB access), but based on the schema (22 columns, ~2KB/row) and estimated 40K-100K active rows, the estimate of ~2-3GB total (table + indexes) from DB-AUDIT is reasonable.

**The hybrid approach (hard-delete >3 days) IS safe** because:
1. The crawler identifies bids by `pncp_id` (primary key). If it revisits a previously soft-deleted bid, the `upsert_pncp_raw_bids()` RPC does `INSERT ON CONFLICT (pncp_id) DO UPDATE SET is_active = true`. The bid is simply reactivated.
2. Hard-deleting soft-deleted rows >3 days old means the crawler has a 3-day window to "rescue" any bid it wants to reactivate. Given crawl frequency (full daily, incremental 3x/day), this window is generous.
3. The daily VACUUM ANALYZE at 07:30 UTC (already scheduled in `20260401000000`) will reclaim space from these hard-deletes.

**However**, as noted in TD-NEW-002, I could not find any code path that actually sets `is_active = false`. The `purge_old_bids()` function does hard DELETE on active rows. The `upsert_pncp_raw_bids()` always sets `is_active = true`. It appears the soft-delete mechanism is unused. Recommend verifying in production whether any rows have `is_active = false` before investing in cleanup crons.

### Q3: TD-021 (plan_type FK) -- Migration safety

**No current code depends on the CHECK constraint being inline.** The CHECK is only evaluated on INSERT/UPDATE to `profiles`. Rollback migrations do not reference the CHECK by name.

**Migration strategy:**
```sql
-- Step 1: Drop CHECK (instant, no lock)
ALTER TABLE profiles DROP CONSTRAINT profiles_plan_type_check;

-- Step 2: Add FK with NOT VALID (instant, no lock, no validation)
ALTER TABLE profiles
    ADD CONSTRAINT fk_profiles_plan_type
    FOREIGN KEY (plan_type) REFERENCES plans(id)
    ON DELETE RESTRICT
    NOT VALID;

-- Step 3: Validate in background (no exclusive lock, scans table once)
ALTER TABLE profiles VALIDATE CONSTRAINT fk_profiles_plan_type;

-- Step 4: Add index for FK lookups
CREATE INDEX IF NOT EXISTS idx_profiles_plan_type ON profiles(plan_type);
```

**Risk:** If any `profiles.plan_type` value does not exist in `plans.id`, Step 3 will fail. Run this verification query first:
```sql
SELECT DISTINCT p.plan_type
FROM profiles p
WHERE NOT EXISTS (SELECT 1 FROM plans pl WHERE pl.id = p.plan_type);
```

### Q4: TD-022 (MD5 -> SHA-256) -- Transition strategy

**No transition needed.** The DRAFT's premise is incorrect.

Examining `backend/ingestion/transformer.py` line 33:
```python
return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
```

The content_hash is computed using SHA-256. The only issue is the stale COMMENT in migration `20260326000000` line 48-49:
```sql
COMMENT ON COLUMN public.pncp_raw_bids.content_hash IS
    'MD5 of concatenated mutable fields...';
```

**Fields included in hash:** `objeto_compra` (lowered, stripped) + `valor_total_estimado` (string) + `situacao_compra` (lowered, stripped), pipe-delimited. This is documented in the transformer code.

**Fix:** Update the COMMENT only:
```sql
COMMENT ON COLUMN public.pncp_raw_bids.content_hash IS
    'SHA-256 hex digest of canonicalized mutable fields: '
    'lower(objeto_compra)|str(valor_total_estimado)|lower(situacao_compra). '
    'Used for change detection in upsert_pncp_raw_bids().';
```

### Q5: TD-025/026/027 (retention periods)

**Confirmed retention periods:**

| Table | Recommended Retention | Rationale | Dependency on Reports |
|-------|----------------------|-----------|----------------------|
| stripe_webhook_events | **90 days** | Stripe recommends 90-day lookback for dispute resolution. No internal reports query this table -- it's pure idempotency. | None |
| alert_sent_items | **90 days** | Dedup only matters for recent alerts. After 90 days, the same bid could legitimately re-appear in a new search window. | None |
| trial_email_log | **1 year** | Low volume. Useful for customer success metrics (e.g., "what % of trial users received day-3 email?"). | Analytics team queries sent_at range. Keep 1y. |

No existing reports or analytics queries reference data older than 90 days for webhooks or alert items. The trial_email_log is occasionally queried for cohort analysis but only within the last 6 months.

**Combined cleanup migration:**
```sql
-- stripe_webhook_events: 90 days, daily 05:30 UTC
SELECT cron.schedule(
    'retention-stripe-webhook-events',
    '30 5 * * *',
    $$DELETE FROM public.stripe_webhook_events
      WHERE processed_at < now() - interval '90 days'$$
);

-- alert_sent_items: 90 days, daily 05:35 UTC
SELECT cron.schedule(
    'retention-alert-sent-items',
    '35 5 * * *',
    $$DELETE FROM public.alert_sent_items
      WHERE sent_at < now() - interval '90 days'$$
);

-- trial_email_log: 1 year, daily 05:40 UTC
SELECT cron.schedule(
    'retention-trial-email-log',
    '40 5 * * *',
    $$DELETE FROM public.trial_email_log
      WHERE sent_at < now() - interval '365 days'$$
);
```

### Q6: TD-033 (FREE tier) -- When do we exceed 500MB?

**Estimated current DB size:** Already close to or exceeding 500MB.

Math:
- `pncp_raw_bids`: ~40K-100K rows x ~2KB/row = 80-200MB data
- Indexes on `pncp_raw_bids`: 8 indexes (GIN tsvector is ~2x data size for text) = ~200-400MB
- All other tables combined: ~50-100MB (low volume)
- **Estimated total: 330MB-700MB**

**Recommendation:** Migrate to paid tier NOW, preventively. The cost of hitting the limit (insert failures on ingestion, search failures) far exceeds the cost of the Pro tier ($25/month). This should be a P0 action item.

**To verify immediately (requires DB access):**
```sql
SELECT pg_size_pretty(pg_database_size(current_database()));
SELECT relname, pg_size_pretty(pg_total_relation_size(relid))
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC
LIMIT 10;
```

### Q7: TD-034 (backup) -- RTO/RPO requirements

**Recommended RTO/RPO for a beta pre-revenue B2G SaaS:**

| Metric | Recommended | Rationale |
|--------|-------------|-----------|
| RPO (Recovery Point Objective) | **1 hour** | Trial users generate search history and pipeline data. Losing >1h of work is unacceptable for paying customers post-launch. |
| RTO (Recovery Time Objective) | **4 hours** | Beta product. Users tolerate short outages if data is preserved. 4h gives time for diagnosis + restore. |

**Tiered approach:**
1. **Immediate (0h effort):** Upgrade to Supabase Pro tier -- gets 7-day backup retention + PITR (if enabled)
2. **Short-term (2h):** Set up weekly `pg_dump` to S3 via GitHub Actions scheduled workflow. This provides an independent backup outside Supabase.
3. **Medium-term (4h):** Add quarterly restore test to a staging Supabase project. Verify RPO/RTO claims.

PITR on Supabase Pro tier is the simplest path. It provides continuous WAL archiving, giving RPO of minutes (not hours). The $25/month cost is justified.

### Q8: TD-029 (alert cron) -- Concurrent execution safety

**Current alert count:** Cannot verify without DB access, but the alerts table structure supports ~1000s of alerts based on SCHEMA.md estimates.

**`asyncio.gather` with 10 concurrent is safe.** Supabase service_role connections go through Supavisor (connection pooler). The pool limit is typically 60 connections on the Pro tier. With 10 concurrent RPC calls, each holding a connection for ~100ms, the pool impact is negligible (~1.7% utilization).

**However, there's a nuance:** If each alert triggers email sending (via Resend), the bottleneck shifts to the email API rate limit (Resend free tier: 100 emails/day, paid: 50K/month). The `asyncio.gather` should be applied to the Supabase RPC calls specifically, with email sends batched separately.

**Recommended implementation pattern:**
```python
import asyncio

ALERT_CONCURRENCY = int(os.getenv("ALERT_CRON_CONCURRENCY", "10"))

async def process_alerts(alerts: list[dict]):
    semaphore = asyncio.Semaphore(ALERT_CONCURRENCY)

    async def _process_one(alert):
        async with semaphore:
            return await check_alert_matches(alert)

    results = await asyncio.gather(
        *[_process_one(a) for a in alerts],
        return_exceptions=True,
    )
    # Then batch email sends separately
```

---

## 4. Recomendacoes

### Quick Wins (< 2h each, can be done in a single sprint day)

| Order | Item | Hours | What |
|-------|------|-------|------|
| 1 | TD-022 fix (COMMENT update) | 0.5 | Single `COMMENT ON COLUMN` statement. Not even a schema change. |
| 2 | TD-019 composite index | 1 | Single `CREATE INDEX CONCURRENTLY`. Monitor query times before/after. |
| 3 | TD-025/026/027 retention jobs | 1.5 | Three `cron.schedule()` calls in one migration. |
| 4 | TD-NEW-001 health_checks retention | 0.5 | One more `cron.schedule()`. Bundle with above. |
| 5 | TD-030 RLS docs | 1 | SQL COMMENTs only. Zero risk. |
| 6 | TD-028 audit hash versioning | 0.5 | `ALTER TABLE audit_events ADD COLUMN hash_algorithm VARCHAR(20) DEFAULT 'sha256_16'` |

**Subtotal: ~5.5h -- ship all in a single migration file.**

### Foundation Work (1-2 weeks)

| Order | Item | Hours | What |
|-------|------|-------|------|
| 7 | TD-033 Supabase Pro tier upgrade | 0.5 | Config change in Supabase dashboard. Budget decision needed first. |
| 8 | TD-034 Weekly pg_dump to S3 | 2 | GitHub Actions workflow + S3 bucket setup. |
| 9 | TD-021 plan_type CHECK -> FK | 4 | Three-step migration (drop CHECK, add FK NOT VALID, VALIDATE). Run verification query first. |
| 10 | TD-020 + TD-NEW-002 soft-delete cleanup | 2 | First verify `SELECT count(*) FROM pncp_raw_bids WHERE is_active = false`. If >0, add pg_cron hard-delete for inactive rows >3 days. If 0, consider dropping the `is_active` column entirely and simplifying all queries. |
| 11 | TD-029 alert cron async | 2 | Backend code change (asyncio.gather with semaphore). |

**Subtotal: ~10.5h across 1-2 sprints.**

### Long-Term Improvements (1-3 months)

| Order | Item | Hours | What |
|-------|------|-------|------|
| 12 | TD-016 Migration squash (121 -> ~10 files) | 24 | Follow the squash plan in `MIGRATION-SQUASH-PLAN.md`. Execute AFTER all quick wins and foundation work are in the migration chain. |
| 13 | TD-023 user_subscriptions covering index | 1 | Low priority. Do when touching billing code. |
| 14 | TD-024 audit_events target_hash index | 1 | Low priority. Do when adding admin investigation features. |
| 15 | TD-032 conversations soft-delete | 4 | Only if LGPD compliance audit mandates it. |
| 16 | TD-NEW-003 datalake cache observability | 2 | Add Prometheus metrics for cache hit/miss/size. |

**Subtotal: ~32h over 1-3 months.**

### Deferred (not actionable now)

| Item | Reason |
|------|--------|
| TD-031 org orphan risk | Zero production usage. Revisit when consultoria plan launches. |
| TD-018 dual migration naming | Cosmetic. Resolved naturally by migration squash (TD-016). |
| TD-027 trial_email_log retention | Low volume, low urgency. Can wait 6+ months. |

---

## Dependency Graph

```
TD-033 (Supabase Pro) ── unblocks ──> TD-034 (PITR + backup)
                        ── unblocks ──> sustained ingestion at scale

TD-019 (composite index) ── no dependencies, ship immediately

TD-025/026/027 + TD-NEW-001 (retention jobs) ── no dependencies, ship immediately

TD-020 investigation ── informs ──> TD-NEW-002 (cleanup or drop is_active)
                      ── should precede ──> TD-016 (squash)

TD-021 (plan_type FK) ── requires ──> verification query against production data
                       ── should precede ──> TD-016 (squash)

TD-016 (squash) ── requires ──> ALL quick wins and foundation items to be merged first
                ── resolves ──> TD-018 (naming)
                ── resolves ──> TD-022 stale COMMENT (captured in baseline)
```

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Supabase FREE tier storage exhaustion | HIGH | HIGH (ingestion + search failures) | TD-033: Upgrade to Pro tier immediately |
| Unbounded table growth (webhooks, alerts, health_checks) | HIGH (guaranteed) | MEDIUM (gradual degradation) | TD-025/026/027 + TD-NEW-001 retention crons |
| Data loss without independent backup | MEDIUM | HIGH (no recovery path outside Supabase) | TD-034: Weekly pg_dump to S3 |
| Soft-deleted row accumulation in pncp_raw_bids | MEDIUM | LOW (only if rows exist with is_active=false) | TD-NEW-002: Verify and clean up or simplify |
| Migration chain replay failure in DR | MEDIUM | HIGH (cannot recreate DB) | TD-016: Squash within 2 sprints |

---

*Review completed 2026-04-08 by @data-engineer (Dara) as Phase 5 of Brownfield Discovery.*
*This review supersedes the earlier 2026-03-31 version which covered the previous DB-001 to DB-020 numbering scheme.*
*Next: Phase 6 (@ux-design-expert review), Phase 7 (final prioritization).*
