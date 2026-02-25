-- ============================================================================
-- Migration: JSONB Storage Governance
-- STORY-265: search_results_cache.results size control + cold entry cleanup
-- Date: 2026-02-25
-- ============================================================================
-- PRE-CHECK RESULTS (2026-02-25):
--   total=7, avg_bytes=616886, max_bytes=1588205, over_1mb=2, over_2mb=0
-- DECISION: 2MB limit (no existing data violates; 2 entries at ~1.59MB are safe)
-- ============================================================================

-- ============================================================
-- 1. CHECK constraint: results JSONB <= 2 MB
--    Prevents unbounded growth from multi-UF searches
--    Application-level truncation in search_cache.py handles graceful fallback
-- ============================================================

ALTER TABLE public.search_results_cache
  ADD CONSTRAINT chk_results_max_size
  CHECK (octet_length(results::text) <= 2097152);

COMMENT ON CONSTRAINT chk_results_max_size ON public.search_results_cache IS
  'STORY-265 AC2: JSONB results capped at 2 MB to prevent storage bloat and slow queries. '
  'Application-level truncation in search_cache.py provides graceful fallback before this hard limit.';

-- ============================================================
-- 2. pg_cron cleanup job: cold entries > 7 days
--    Schedule: Daily at 5:00 AM UTC
--    Only deletes entries with priority = 'cold' older than 7 days
--    Hot/warm entries are preserved regardless of age
-- ============================================================

SELECT cron.schedule(
  'cleanup-cold-cache-entries',
  '0 5 * * *',
  $$
    DELETE FROM public.search_results_cache
    WHERE priority = 'cold'
      AND created_at < NOW() - INTERVAL '7 days'
  $$
);

-- ============================================================
-- 3. Initial cleanup (run once — deletes cold entries > 7 days)
-- ============================================================

DELETE FROM public.search_results_cache
WHERE priority = 'cold'
  AND created_at < NOW() - INTERVAL '7 days';

-- ============================================================
-- Verification queries (run after applying):
-- ============================================================
-- 1. Verify CHECK constraint exists:
--    SELECT conname, pg_get_constraintdef(oid)
--    FROM pg_constraint
--    WHERE conrelid = 'public.search_results_cache'::regclass
--      AND conname = 'chk_results_max_size';
--
-- 2. Verify no existing data violates constraint:
--    SELECT count(*) FROM search_results_cache
--    WHERE octet_length(results::text) > 2097152;
--    -- Should return 0
--
-- 3. Verify pg_cron job is scheduled:
--    SELECT jobname, schedule FROM cron.job
--    WHERE jobname = 'cleanup-cold-cache-entries';
--
-- 4. Test insert > 2MB should fail:
--    INSERT INTO search_results_cache (user_id, params_hash, search_params, results, total_results)
--    VALUES ('00000000-0000-0000-0000-000000000000', 'test', '{}',
--            repeat('x', 2200000)::jsonb, 0);
--    -- Should fail with CHECK constraint violation
-- ============================================================
