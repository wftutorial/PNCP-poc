# Bloat Monitoring — pncp_raw_bids

**Story:** DEBT-DB-NEW-005 (part of DEBT-203)
**Migration:** `20260331000000_debt203_bloat_monitoring.sql`
**Last updated:** 2026-03-31

---

## Why pncp_raw_bids Bloats

`pncp_raw_bids` receives two types of write traffic that generate PostgreSQL bloat:

1. **Daily hard deletes** — `purge_old_bids()` runs via ARQ cron at 7:00 UTC, deleting all rows where `data_publicacao < now() - 12 days`. At 40K+ rows, this removes thousands of rows per run.
2. **Frequent upserts** — `upsert_pncp_raw_bids()` runs 3x/day (8am/2pm/8pm BRT) for incremental crawls and 1x/day for full crawls. Each UPDATE creates a dead tuple for MVCC.

PostgreSQL's autovacuum is tuned conservatively by default. On Supabase Free tier (500MB), the table may not trigger autovacuum frequently enough, causing dead tuples to accumulate and degrading full-text search (GIN index) performance.

**Symptoms of bloat:**
- Slower `search_datalake()` queries (GIN index scans over dead tuples)
- Growing table size without proportional data growth
- `dead_row_ratio_pct > 20%` in `pncp_raw_bids_bloat_stats`

---

## Diagnostic Queries

### Quick status check

```sql
SELECT * FROM public.pncp_raw_bids_bloat_stats;
```

Expected healthy state:
- `dead_row_ratio_pct` < 20%
- `last_autovacuum` within the last 24h (or `last_vacuum` within 24h)
- `total_size` < 200 MB

### Manual bloat check (calls monitoring function directly)

```sql
SELECT public.check_pncp_raw_bids_bloat();
-- Check PostgreSQL logs for WARNING messages
```

### Check pg_cron job status

```sql
SELECT jobname, schedule, command, active
FROM cron.job
WHERE jobname = 'bloat-check-pncp-raw-bids';
```

### Detailed bloat estimate (via pgstattuple, if available)

```sql
-- Requires pg_stat_statements or pgstattuple extension
SELECT
    table_len,
    tuple_count,
    tuple_len,
    dead_tuple_count,
    dead_tuple_len,
    ROUND(dead_tuple_len::numeric / table_len * 100, 2) AS bloat_pct
FROM pgstattuple('public.pncp_raw_bids');
```

### Index bloat check

```sql
SELECT
    indexname,
    pg_size_pretty(pg_relation_size(indexname::regclass)) AS index_size,
    idx_scan,
    idx_tup_read
FROM pg_stat_user_indexes
WHERE relname = 'pncp_raw_bids'
ORDER BY pg_relation_size(indexname::regclass) DESC;
```

---

## pg_cron Job

The monitoring function is scheduled via pg_cron:

| Job name | Schedule | Timing |
|---|---|---|
| `bloat-check-pncp-raw-bids` | `30 6 * * *` | Daily at 6:30 UTC |

The check runs at **6:30 UTC** — before the purge job at **7:00 UTC** — to capture the worst-case bloat state (pre-purge = maximum dead tuples from previous day's upserts).

**Manage the job:**

```sql
-- View job
SELECT * FROM cron.job WHERE jobname = 'bloat-check-pncp-raw-bids';

-- Disable temporarily
UPDATE cron.job SET active = false WHERE jobname = 'bloat-check-pncp-raw-bids';

-- Re-enable
UPDATE cron.job SET active = true WHERE jobname = 'bloat-check-pncp-raw-bids';

-- Remove and reschedule
SELECT cron.unschedule('bloat-check-pncp-raw-bids');
SELECT cron.schedule('bloat-check-pncp-raw-bids', '30 6 * * *',
    'SELECT public.check_pncp_raw_bids_bloat()');
```

---

## Threshold Configuration

The monitoring function uses these thresholds (defined as constants in the function body):

| Threshold | Value | Action |
|---|---|---|
| `v_bloat_threshold` | 20% dead rows | Emit `WARNING` in PostgreSQL logs |
| Table size alert | 200 MB total | Emit `WARNING` in PostgreSQL logs |

**Changing thresholds:** Edit `check_pncp_raw_bids_bloat()` and update `v_bloat_threshold` and the size check value. Re-apply with `supabase db push`.

---

## What to Do When Threshold Is Reached

### Option 1: Manual VACUUM (safe for production)

```sql
-- Non-blocking, can run while app is live
VACUUM ANALYZE public.pncp_raw_bids;
```

Typical duration: 5–30 seconds at 40K rows. The GIN index on `objeto_compra` is reindexed during ANALYZE, which may take longer at high row counts.

### Option 2: Full VACUUM (reclaims disk space)

```sql
-- Acquires AccessExclusiveLock — schedule during maintenance window
VACUUM FULL ANALYZE public.pncp_raw_bids;
```

Use only if `total_size` has grown significantly and `VACUUM` alone isn't reclaiming space.

### Option 3: Tune autovacuum for this table

```sql
-- Lower thresholds for aggressive vacuuming on this high-churn table
ALTER TABLE public.pncp_raw_bids SET (
    autovacuum_vacuum_scale_factor = 0.01,    -- vacuum at 1% dead tuples (default 20%)
    autovacuum_analyze_scale_factor = 0.005,  -- analyze at 0.5% changes (default 10%)
    autovacuum_vacuum_cost_delay = 2           -- less throttling for this table
);
```

### Option 4: Review retention window

If bloat persists, the 12-day retention window may be too wide. Reducing to 10 days would decrease the purge volume per run:

```sql
-- Test smaller retention (discuss with team first)
SELECT purge_old_bids(10);
```

---

## Diagnostic View Reference

```sql
SELECT * FROM public.pncp_raw_bids_bloat_stats;
```

| Column | Description |
|---|---|
| `live_rows` | Active rows (n_live_tup from pg_stat_user_tables) |
| `dead_rows` | Dead tuples pending vacuum (n_dead_tup) |
| `dead_row_ratio_pct` | `dead / (live + dead) * 100` — main bloat indicator |
| `last_vacuum` | Last manual VACUUM timestamp |
| `last_autovacuum` | Last autovacuum run timestamp |
| `last_analyze` | Last manual ANALYZE timestamp |
| `last_autoanalyze` | Last autoanalyze run timestamp |
| `total_size` | Total table + indexes (human-readable) |
| `table_size` | Table data only (human-readable) |
| `indexes_size` | All indexes combined (human-readable) |
| `rows_modified_since_analyze` | Rows changed since last analyze |
| `sequential_scans` | Cumulative full table scans (high = missing index) |
| `index_scans` | Cumulative index scans (healthy if high) |

---

## Related Files

| File | Purpose |
|---|---|
| `supabase/migrations/20260331000000_debt203_bloat_monitoring.sql` | Migration creating function, cron job, view |
| `supabase/migrations/20260326000000_datalake_raw_bids.sql` | Original table creation + purge_old_bids() |
| `supabase/rollbacks/rollback_20260331_pncp_raw_bids_indexes.sql` | Rollback script for pncp_raw_bids changes |
| `backend/ingestion/scheduler.py` | ARQ cron job that calls purge_old_bids() |
| `backend/ingestion/loader.py` | purge_old_bids() Python caller |
