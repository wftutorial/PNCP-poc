-- ============================================================================
-- Migration: 20260308400000_debt010_schema_guards.sql
-- Story: DEBT-010 — Database Schema Guards & Monitoring
-- Date: 2026-03-08
--
-- Changes:
--   DB-018: CHECK constraint on search_results_cache.priority
--   DB-019: CHECK constraint on alert_runs.status
--   DB-040: DROP redundant idx_alert_preferences_user_id (UNIQUE covers it)
--   DB-041: DROP redundant idx_trial_email_log_user_id (composite unique covers it)
--   DB-042: Composite index for admin inbox on conversations
--   DB-021: Validate billing_period constraint vs semiannual data
-- ============================================================================

-- DB-018: CHECK constraint on search_results_cache.priority
-- Ensure priority is one of: hot, warm, cold
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'chk_search_results_cache_priority'
  ) THEN
    ALTER TABLE public.search_results_cache
      ADD CONSTRAINT chk_search_results_cache_priority
      CHECK (priority IN ('hot', 'warm', 'cold'));
  END IF;
END $$;

-- DB-019: CHECK constraint on alert_runs.status
-- Ensure status is one of the valid values
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'chk_alert_runs_status'
  ) THEN
    ALTER TABLE public.alert_runs
      ADD CONSTRAINT chk_alert_runs_status
      CHECK (status IN ('pending', 'running', 'completed', 'failed', 'matched', 'no_results', 'no_match', 'all_deduped', 'error'));
  END IF;
END $$;

-- DB-040: DROP redundant idx_alert_preferences_user_id
-- The UNIQUE constraint on user_id already creates a B-tree index
DROP INDEX IF EXISTS public.idx_alert_preferences_user_id;

-- DB-041: DROP redundant idx_trial_email_log_user_id
-- The UNIQUE(user_id, email_type) composite already covers leading column user_id
DROP INDEX IF EXISTS public.idx_trial_email_log_user_id;

-- DB-042: Composite index for admin inbox query
-- Optimizes: SELECT * FROM conversations WHERE status = 'aberto' ORDER BY last_message_at DESC
CREATE INDEX IF NOT EXISTS idx_conversations_status_last_msg
  ON public.conversations(status, last_message_at DESC);

-- DB-021: Validate billing_period constraint vs semiannual data
-- The current CHECK allows only ('monthly', 'annual'), but GTM-002 added 'semiannual'.
-- Update the constraint to include 'semiannual'.
DO $$
BEGIN
  -- Drop old constraint if it exists
  IF EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conrelid = 'public.user_subscriptions'::regclass
      AND conname LIKE '%billing_period%'
      AND contype = 'c'
  ) THEN
    -- Get actual constraint name dynamically
    EXECUTE (
      SELECT 'ALTER TABLE public.user_subscriptions DROP CONSTRAINT ' || conname
      FROM pg_constraint
      WHERE conrelid = 'public.user_subscriptions'::regclass
        AND conname LIKE '%billing_period%'
        AND contype = 'c'
      LIMIT 1
    );
  END IF;

  -- Add updated constraint including semiannual
  ALTER TABLE public.user_subscriptions
    ADD CONSTRAINT chk_user_subscriptions_billing_period
    CHECK (billing_period IN ('monthly', 'semiannual', 'annual'));
EXCEPTION
  WHEN duplicate_object THEN
    NULL; -- Constraint already exists with correct definition
END $$;

-- Verify: Report any data with invalid billing_period
DO $$
DECLARE
  invalid_count INT;
BEGIN
  SELECT COUNT(*) INTO invalid_count
  FROM public.user_subscriptions
  WHERE billing_period NOT IN ('monthly', 'semiannual', 'annual');

  IF invalid_count > 0 THEN
    RAISE WARNING 'DEBT-010 DB-021: % rows have invalid billing_period values', invalid_count;
  ELSE
    RAISE NOTICE 'DEBT-010 DB-021: All billing_period values valid (monthly/semiannual/annual)';
  END IF;
END $$;

-- ============================================================================
-- DB-031: RPC function for safe table size queries
-- Used by Prometheus gauge to track JSONB-heavy table sizes
-- ============================================================================
CREATE OR REPLACE FUNCTION public.pg_total_relation_size_safe(tbl text)
RETURNS bigint
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  result bigint;
BEGIN
  EXECUTE format('SELECT pg_total_relation_size(%L)', 'public.' || tbl) INTO result;
  RETURN COALESCE(result, 0);
EXCEPTION
  WHEN undefined_table THEN
    RETURN 0;
  WHEN insufficient_privilege THEN
    RETURN -1;
END $$;

COMMENT ON FUNCTION public.pg_total_relation_size_safe(text) IS 'DEBT-010 DB-031: Safe wrapper for pg_total_relation_size, returns 0 for missing tables';

-- Grant execute to authenticated users (needed for service_role via PostgREST)
GRANT EXECUTE ON FUNCTION public.pg_total_relation_size_safe(text) TO authenticated;
GRANT EXECUTE ON FUNCTION public.pg_total_relation_size_safe(text) TO service_role;

-- ============================================================================
-- DB-028: Fix non-idempotent migration 008_add_billing_period.sql
-- Original uses ALTER TABLE ADD COLUMN without IF NOT EXISTS
-- This migration ensures the columns exist with correct constraints
-- (The original migration already ran in production, this is a safety net)
-- ============================================================================
DO $$
BEGIN
  -- Ensure billing_period column exists (idempotent)
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'user_subscriptions'
      AND column_name = 'billing_period'
  ) THEN
    ALTER TABLE public.user_subscriptions
      ADD COLUMN billing_period VARCHAR(10) NOT NULL DEFAULT 'monthly';
  END IF;

  -- Ensure annual_benefits column exists (idempotent)
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'user_subscriptions'
      AND column_name = 'annual_benefits'
  ) THEN
    ALTER TABLE public.user_subscriptions
      ADD COLUMN annual_benefits JSONB NOT NULL DEFAULT '{}'::jsonb;
  END IF;
END $$;

-- Ensure billing index exists (idempotent)
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_billing
  ON public.user_subscriptions(user_id, billing_period, is_active)
  WHERE is_active = true;
