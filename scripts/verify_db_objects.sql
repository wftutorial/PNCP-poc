-- DEBT-002: Database Object Verification Script
-- Run this in Supabase SQL Editor after migration apply or recovery.
-- All queries should return results — missing results indicate a problem.

-- ══════════════════════════════════════════════════════════════════
-- 1. Expected Tables (should be ~25+ tables)
-- ══════════════════════════════════════════════════════════════════
SELECT 'TABLES' AS check_type, COUNT(*) AS count
FROM information_schema.tables
WHERE table_schema = 'public' AND table_type = 'BASE TABLE';

-- Critical tables check
SELECT table_name,
    CASE WHEN table_name IS NOT NULL THEN '✓' ELSE '✗ MISSING' END AS status
FROM (VALUES
    ('profiles'), ('plans'), ('user_subscriptions'), ('search_sessions'),
    ('monthly_quota'), ('user_oauth_tokens'), ('google_sheets_exports'),
    ('classification_feedback'), ('search_state_transitions'),
    ('pipeline_items'), ('stripe_webhook_events'), ('audit_events'),
    ('search_results_cache'), ('plan_features'), ('plan_billing_periods'),
    ('messages'), ('conversations'), ('search_results_store'),
    ('alert_preferences'), ('alerts'), ('alert_runs'),
    ('organizations'), ('partners'), ('partner_referrals'),
    ('health_checks'), ('incidents'), ('mfa_recovery_codes'),
    ('trial_email_log'), ('reconciliation_log')
) AS expected(table_name)
LEFT JOIN information_schema.tables t
    ON t.table_name = expected.table_name
    AND t.table_schema = 'public'
    AND t.table_type = 'BASE TABLE';

-- ══════════════════════════════════════════════════════════════════
-- 2. Critical Functions
-- ══════════════════════════════════════════════════════════════════
SELECT routine_name,
    CASE WHEN routine_name IS NOT NULL THEN '✓' ELSE '✗ MISSING' END AS status
FROM (VALUES
    ('handle_new_user'), ('check_and_increment_quota'),
    ('increment_quota_atomic'), ('set_updated_at'),
    ('get_table_columns_simple')
) AS expected(routine_name)
LEFT JOIN information_schema.routines r
    ON r.routine_name = expected.routine_name
    AND r.routine_schema = 'public';

-- ══════════════════════════════════════════════════════════════════
-- 3. Critical Triggers
-- ══════════════════════════════════════════════════════════════════
SELECT trigger_name, event_object_table
FROM information_schema.triggers
WHERE trigger_schema = 'public'
ORDER BY event_object_table, trigger_name;

-- Check handle_new_user trigger specifically
SELECT 'handle_new_user trigger' AS check_item,
    CASE WHEN COUNT(*) > 0 THEN '✓ EXISTS' ELSE '✗ MISSING — CRITICAL' END AS status
FROM pg_trigger t
JOIN pg_proc p ON t.tgfoid = p.oid
WHERE p.proname = 'handle_new_user';

-- ══════════════════════════════════════════════════════════════════
-- 4. RLS Policies per table
-- ══════════════════════════════════════════════════════════════════
SELECT tablename, COUNT(*) AS policy_count
FROM pg_policies
WHERE schemaname = 'public'
GROUP BY tablename
ORDER BY tablename;

-- ══════════════════════════════════════════════════════════════════
-- 5. Extensions
-- ══════════════════════════════════════════════════════════════════
SELECT extname, extversion
FROM pg_extension
WHERE extname IN ('pg_cron', 'pg_trgm', 'pgcrypto', 'uuid-ossp')
ORDER BY extname;

-- ══════════════════════════════════════════════════════════════════
-- 6. pg_cron Jobs (requires pg_cron enabled)
-- ══════════════════════════════════════════════════════════════════
SELECT jobname, schedule, command
FROM cron.job
ORDER BY jobname;

-- ══════════════════════════════════════════════════════════════════
-- 7. Seed Data Verification
-- ══════════════════════════════════════════════════════════════════
SELECT 'plans' AS table_name, COUNT(*) AS row_count FROM plans
UNION ALL
SELECT 'plan_billing_periods', COUNT(*) FROM plan_billing_periods
UNION ALL
SELECT 'plan_features', COUNT(*) FROM plan_features;
