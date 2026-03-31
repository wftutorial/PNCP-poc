-- DEBT-DB-NEW-005: Table bloat monitoring for pncp_raw_bids
-- pncp_raw_bids has 40K+ rows with daily hard deletes (purge job via purge_old_bids())
-- Without VACUUM ANALYZE, dead tuples accumulate and degrade query performance.
-- The purge_old_bids() function uses hard DELETE (not soft-delete), generating bloat.
--
-- This migration adds:
--   1. check_pncp_raw_bids_bloat() — monitoring function
--   2. pg_cron job scheduled daily at 6:30 UTC (after purge at 7:00 UTC)
--   3. pncp_raw_bids_bloat_stats — diagnostic view for manual inspection

-- ============================================================
-- SECTION 1: Bloat monitoring function
-- ============================================================

CREATE OR REPLACE FUNCTION public.check_pncp_raw_bids_bloat()
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_total_pages      bigint;
    v_live_tup         bigint;
    v_dead_tup         bigint;
    v_table_size_mb    numeric;
    v_dead_ratio       numeric;
    v_bloat_threshold  numeric := 0.20; -- 20% dead rows threshold
BEGIN
    -- Fetch table stats from pg_stat_user_tables
    SELECT
        relpages,
        n_live_tup,
        n_dead_tup,
        pg_total_relation_size('public.pncp_raw_bids')::numeric / (1024 * 1024)
    INTO v_total_pages, v_live_tup, v_dead_tup, v_table_size_mb
    FROM pg_stat_user_tables
    WHERE schemaname = 'public' AND relname = 'pncp_raw_bids';

    IF NOT FOUND THEN
        RAISE LOG 'check_pncp_raw_bids_bloat: tabela pncp_raw_bids não encontrada em pg_stat_user_tables';
        RETURN;
    END IF;

    -- Calculate dead row ratio (primary bloat indicator)
    v_dead_ratio := CASE
        WHEN (v_live_tup + v_dead_tup) > 0
        THEN v_dead_tup::numeric / (v_live_tup + v_dead_tup)
        ELSE 0
    END;

    -- Log current state
    RAISE LOG 'pncp_raw_bids bloat check: pages=%, live_rows=%, dead_rows=%, size_mb=%, dead_ratio=%.1f%%',
        v_total_pages,
        v_live_tup,
        v_dead_tup,
        ROUND(v_table_size_mb, 2),
        v_dead_ratio * 100;

    -- Alert if dead row ratio exceeds threshold
    IF v_dead_ratio > v_bloat_threshold THEN
        RAISE WARNING 'HIGH BLOAT ALERT: pncp_raw_bids has %.1f%% dead rows (threshold: %.0f%%, dead=%, live=%). '
                      'Run: VACUUM ANALYZE public.pncp_raw_bids;',
            v_dead_ratio * 100,
            v_bloat_threshold * 100,
            v_dead_tup,
            v_live_tup;
    END IF;

    -- Secondary alert: table growing beyond expected size
    -- At 40K rows with ~1KB/row average, 40MB is reasonable; warn above 200MB
    IF v_table_size_mb > 200 THEN
        RAISE WARNING 'SIZE ALERT: pncp_raw_bids is %.1f MB (expected < 200 MB). '
                      'Check retention policy (purge_old_bids) and autovacuum settings.',
            v_table_size_mb;
    END IF;
END;
$$;

COMMENT ON FUNCTION public.check_pncp_raw_bids_bloat() IS
    'DEBT-DB-NEW-005: Monitors bloat in pncp_raw_bids caused by daily hard deletes '
    '(purge_old_bids). Logs dead row ratio and raises WARNING when > 20%. '
    'Scheduled via pg_cron at 6:30 UTC daily. '
    'SECURITY DEFINER: safe to call with authenticated role.';

GRANT EXECUTE ON FUNCTION public.check_pncp_raw_bids_bloat() TO service_role;

-- ============================================================
-- SECTION 2: pg_cron scheduling
-- ============================================================

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_cron') THEN
        -- Remove existing job if present (idempotent)
        PERFORM cron.unschedule('bloat-check-pncp-raw-bids')
        WHERE EXISTS (SELECT 1 FROM cron.job WHERE jobname = 'bloat-check-pncp-raw-bids');

        -- Schedule daily at 6:30 UTC
        -- Purge job runs at 7:00 UTC (DEBT-009 scheduler config), so this
        -- check runs BEFORE the purge to capture worst-case bloat state.
        PERFORM cron.schedule(
            'bloat-check-pncp-raw-bids',
            '30 6 * * *',
            'SELECT public.check_pncp_raw_bids_bloat()'
        );
        RAISE NOTICE 'DEBT-DB-NEW-005: pg_cron job scheduled: bloat-check-pncp-raw-bids (daily 6:30 UTC)';
    ELSE
        RAISE NOTICE 'DEBT-DB-NEW-005: pg_cron extension not available — '
                     'check_pncp_raw_bids_bloat() function created but NOT scheduled. '
                     'Run manually or schedule via external cron.';
    END IF;
END $$;

-- ============================================================
-- SECTION 3: Diagnostic view
-- ============================================================

CREATE OR REPLACE VIEW public.pncp_raw_bids_bloat_stats AS
SELECT
    s.schemaname,
    s.relname                                               AS table_name,
    s.n_live_tup                                            AS live_rows,
    s.n_dead_tup                                            AS dead_rows,
    CASE
        WHEN (s.n_live_tup + s.n_dead_tup) > 0
        THEN ROUND(
                 s.n_dead_tup::numeric / (s.n_live_tup + s.n_dead_tup) * 100,
                 2
             )
        ELSE 0
    END                                                     AS dead_row_ratio_pct,
    s.last_vacuum,
    s.last_autovacuum,
    s.last_analyze,
    s.last_autoanalyze,
    pg_size_pretty(
        pg_total_relation_size('public.pncp_raw_bids')
    )                                                       AS total_size,
    pg_size_pretty(
        pg_relation_size('public.pncp_raw_bids')
    )                                                       AS table_size,
    pg_size_pretty(
        pg_indexes_size('public.pncp_raw_bids')
    )                                                       AS indexes_size,
    s.n_mod_since_analyze                                   AS rows_modified_since_analyze,
    s.seq_scan                                              AS sequential_scans,
    s.idx_scan                                              AS index_scans
FROM pg_stat_user_tables s
WHERE s.schemaname = 'public'
  AND s.relname    = 'pncp_raw_bids';

COMMENT ON VIEW public.pncp_raw_bids_bloat_stats IS
    'DEBT-DB-NEW-005: Diagnostic view for pncp_raw_bids bloat monitoring. '
    'dead_row_ratio_pct > 20% → run VACUUM ANALYZE public.pncp_raw_bids. '
    'last_autovacuum NULL → autovacuum may need tuning (see bloat-monitoring.md). '
    'Usage: SELECT * FROM pncp_raw_bids_bloat_stats;';

-- Grant SELECT to authenticated users for admin dashboard queries
GRANT SELECT ON public.pncp_raw_bids_bloat_stats TO authenticated;
GRANT SELECT ON public.pncp_raw_bids_bloat_stats TO service_role;

-- ============================================================
-- SECTION 4: Verification
-- ============================================================

DO $$
BEGIN
    ASSERT EXISTS (
        SELECT 1 FROM pg_proc
        WHERE proname = 'check_pncp_raw_bids_bloat'
          AND pronamespace = 'public'::regnamespace
    ), 'ASSERTION FAILED: check_pncp_raw_bids_bloat function not created';

    ASSERT EXISTS (
        SELECT 1 FROM pg_views
        WHERE schemaname = 'public' AND viewname = 'pncp_raw_bids_bloat_stats'
    ), 'ASSERTION FAILED: pncp_raw_bids_bloat_stats view not created';

    RAISE NOTICE 'DEBT-DB-NEW-005: Migration applied successfully. '
                 'Function: check_pncp_raw_bids_bloat() | View: pncp_raw_bids_bloat_stats';
END $$;

NOTIFY pgrst, 'reload schema';
