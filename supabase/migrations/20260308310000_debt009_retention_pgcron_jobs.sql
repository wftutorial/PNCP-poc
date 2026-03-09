-- DEBT-009: Retention pg_cron Jobs (DB-033, DB-037, DB-049)
-- Creates 6 daily cleanup jobs for tables that grow unbounded.
--
-- | Table                      | Retention | Schedule       |
-- |----------------------------|-----------|----------------|
-- | search_state_transitions   | 30 days   | Daily 4:00 UTC |
-- | alert_sent_items           | 180 days  | Daily 4:05 UTC |
-- | health_checks              | 30 days   | Daily 4:10 UTC |
-- | incidents                  | 90 days   | Daily 4:15 UTC |
-- | mfa_recovery_attempts      | 30 days   | Daily 4:20 UTC |
-- | alert_runs (completed)     | 90 days   | Daily 4:25 UTC |
--
-- Staggered by 5 minutes to avoid I/O spikes.
-- Idempotent: unschedule + schedule pattern.

-- ══════════════════════════════════════════════════════════════════
-- 1. search_state_transitions — 30 days (DB-033, ~15K rows/month)
-- ══════════════════════════════════════════════════════════════════
SELECT cron.unschedule('cleanup-search-state-transitions')
WHERE EXISTS (SELECT 1 FROM cron.job WHERE jobname = 'cleanup-search-state-transitions');

SELECT cron.schedule(
    'cleanup-search-state-transitions',
    '0 4 * * *',
    $$DELETE FROM public.search_state_transitions WHERE created_at < now() - interval '30 days'$$
);

-- ══════════════════════════════════════════════════════════════════
-- 2. alert_sent_items — 180 days (DB-037, dedup degrades over time)
-- ══════════════════════════════════════════════════════════════════
SELECT cron.unschedule('cleanup-alert-sent-items')
WHERE EXISTS (SELECT 1 FROM cron.job WHERE jobname = 'cleanup-alert-sent-items');

SELECT cron.schedule(
    'cleanup-alert-sent-items',
    '5 4 * * *',
    $$DELETE FROM public.alert_sent_items WHERE sent_at < now() - interval '180 days'$$
);

-- ══════════════════════════════════════════════════════════════════
-- 3. health_checks — 30 days (DB-049, ~8640 rows/month at 1/5min)
-- ══════════════════════════════════════════════════════════════════
SELECT cron.unschedule('cleanup-health-checks')
WHERE EXISTS (SELECT 1 FROM cron.job WHERE jobname = 'cleanup-health-checks');

SELECT cron.schedule(
    'cleanup-health-checks',
    '10 4 * * *',
    $$DELETE FROM public.health_checks WHERE checked_at < now() - interval '30 days'$$
);

-- ══════════════════════════════════════════════════════════════════
-- 4. incidents — 90 days (DB-049)
-- ══════════════════════════════════════════════════════════════════
SELECT cron.unschedule('cleanup-incidents')
WHERE EXISTS (SELECT 1 FROM cron.job WHERE jobname = 'cleanup-incidents');

SELECT cron.schedule(
    'cleanup-incidents',
    '15 4 * * *',
    $$DELETE FROM public.incidents WHERE started_at < now() - interval '90 days'$$
);

-- ══════════════════════════════════════════════════════════════════
-- 5. mfa_recovery_attempts — 30 days
-- ══════════════════════════════════════════════════════════════════
SELECT cron.unschedule('cleanup-mfa-recovery-attempts')
WHERE EXISTS (SELECT 1 FROM cron.job WHERE jobname = 'cleanup-mfa-recovery-attempts');

SELECT cron.schedule(
    'cleanup-mfa-recovery-attempts',
    '20 4 * * *',
    $$DELETE FROM public.mfa_recovery_attempts WHERE attempted_at < now() - interval '30 days'$$
);

-- ══════════════════════════════════════════════════════════════════
-- 6. alert_runs (completed only) — 90 days
-- ══════════════════════════════════════════════════════════════════
SELECT cron.unschedule('cleanup-alert-runs')
WHERE EXISTS (SELECT 1 FROM cron.job WHERE jobname = 'cleanup-alert-runs');

SELECT cron.schedule(
    'cleanup-alert-runs',
    '25 4 * * *',
    $$DELETE FROM public.alert_runs WHERE status = 'completed' AND run_at < now() - interval '90 days'$$
);

-- ══════════════════════════════════════════════════════════════════
-- Verification: Should return 11 total jobs (5 existing + 6 new)
-- SELECT jobname, schedule, command FROM cron.job ORDER BY jobname;
-- ══════════════════════════════════════════════════════════════════
