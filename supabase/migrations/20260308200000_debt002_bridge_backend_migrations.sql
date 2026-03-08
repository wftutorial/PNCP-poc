-- ══════════════════════════════════════════════════════════════════════════════
-- DEBT-002: Bridge Migration — Consolidate backend/migrations/ into supabase/
-- ══════════════════════════════════════════════════════════════════════════════
--
-- Purpose: Ensures ALL objects from backend/migrations/ (002-010) are present
-- in the Supabase-managed schema, making backend/migrations/ fully redundant.
--
-- Most objects already exist via earlier supabase migrations:
--   002 → 002_monthly_quota.sql
--   003 → 003_atomic_quota_increment.sql + 20260305100000
--   004 → 013_google_oauth_tokens.sql
--   005 → 014_google_sheets_exports.sql
--   007 → 20260221100000_search_session_lifecycle.sql
--   008 → 20260221100002_create_search_state_transitions.sql
--   009 → 20260220120000_add_search_id_to_search_sessions.sql
--
-- Two objects are UNIQUE to backend/migrations/ and created here:
--   006 → classification_feedback table + indexes + RLS + policies
--   010 → Array normalization UPDATEs on search_sessions
--
-- All statements are fully idempotent — safe to run on any environment.
-- ══════════════════════════════════════════════════════════════════════════════


-- ┌──────────────────────────────────────────────────────────────────────────┐
-- │ SECTION 1: Defensive verification of pre-existing objects (002-005,     │
-- │            007-009). Logs warnings via RAISE NOTICE if missing.         │
-- └──────────────────────────────────────────────────────────────────────────┘

DO $$
BEGIN
  -- 002: monthly_quota table
  IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = 'monthly_quota') THEN
    RAISE WARNING 'DEBT-002: monthly_quota table NOT FOUND — expected from 002_monthly_quota.sql';
  ELSE
    RAISE NOTICE 'DEBT-002: monthly_quota table ✓ exists';
  END IF;

  -- 003: increment_quota_atomic function
  IF NOT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'increment_quota_atomic' AND pronamespace = 'public'::regnamespace) THEN
    RAISE WARNING 'DEBT-002: increment_quota_atomic function NOT FOUND — expected from 003 + 20260305100000';
  ELSE
    RAISE NOTICE 'DEBT-002: increment_quota_atomic function ✓ exists';
  END IF;

  -- 003: check_and_increment_quota function
  IF NOT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'check_and_increment_quota' AND pronamespace = 'public'::regnamespace) THEN
    RAISE WARNING 'DEBT-002: check_and_increment_quota function NOT FOUND — expected from 20260305100000';
  ELSE
    RAISE NOTICE 'DEBT-002: check_and_increment_quota function ✓ exists';
  END IF;

  -- 004: user_oauth_tokens table
  IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = 'user_oauth_tokens') THEN
    RAISE WARNING 'DEBT-002: user_oauth_tokens table NOT FOUND — expected from 013_google_oauth_tokens.sql';
  ELSE
    RAISE NOTICE 'DEBT-002: user_oauth_tokens table ✓ exists';
  END IF;

  -- 005: google_sheets_exports table
  IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = 'google_sheets_exports') THEN
    RAISE WARNING 'DEBT-002: google_sheets_exports table NOT FOUND — expected from 014_google_sheets_exports.sql';
  ELSE
    RAISE NOTICE 'DEBT-002: google_sheets_exports table ✓ exists';
  END IF;

  -- 009: search_sessions.search_id column
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = 'search_sessions' AND column_name = 'search_id'
  ) THEN
    RAISE WARNING 'DEBT-002: search_sessions.search_id column NOT FOUND — expected from 20260220120000';
  ELSE
    RAISE NOTICE 'DEBT-002: search_sessions.search_id column ✓ exists';
  END IF;

  -- 007: search_sessions.status column
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = 'search_sessions' AND column_name = 'status'
  ) THEN
    RAISE WARNING 'DEBT-002: search_sessions.status column NOT FOUND — expected from 20260221100000';
  ELSE
    RAISE NOTICE 'DEBT-002: search_sessions.status column ✓ exists';
  END IF;

  -- 008: search_state_transitions table
  IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = 'search_state_transitions') THEN
    RAISE WARNING 'DEBT-002: search_state_transitions table NOT FOUND — expected from 20260221100002';
  ELSE
    RAISE NOTICE 'DEBT-002: search_state_transitions table ✓ exists';
  END IF;
END
$$;


-- ┌──────────────────────────────────────────────────────────────────────────┐
-- │ SECTION 2: classification_feedback table (from backend 006)             │
-- │ This is the FIRST object unique to backend/migrations/.                 │
-- └──────────────────────────────────────────────────────────────────────────┘

CREATE TABLE IF NOT EXISTS public.classification_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id),
    search_id UUID NOT NULL,
    bid_id TEXT NOT NULL,
    setor_id TEXT NOT NULL,
    user_verdict TEXT NOT NULL CHECK (user_verdict IN ('false_positive', 'false_negative', 'correct')),
    reason TEXT,
    category TEXT CHECK (category IN ('wrong_sector', 'irrelevant_modality', 'too_small', 'too_large', 'closed', 'other')),
    bid_objeto TEXT,
    bid_valor DECIMAL,
    bid_uf TEXT,
    confidence_score INTEGER,
    relevance_source TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE (user_id, search_id, bid_id)
);

-- Indexes (IF NOT EXISTS for idempotency)
CREATE INDEX IF NOT EXISTS idx_feedback_sector_verdict
    ON public.classification_feedback (setor_id, user_verdict, created_at);

CREATE INDEX IF NOT EXISTS idx_feedback_user_created
    ON public.classification_feedback (user_id, created_at);

CREATE INDEX IF NOT EXISTS idx_classification_feedback_user_id
    ON public.classification_feedback (user_id);

-- RLS
ALTER TABLE public.classification_feedback ENABLE ROW LEVEL SECURITY;

-- Policies: DROP IF EXISTS before CREATE (policies lack IF NOT EXISTS syntax)
DO $$
BEGIN
  -- feedback_insert_own
  IF EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'classification_feedback' AND policyname = 'feedback_insert_own') THEN
    DROP POLICY feedback_insert_own ON public.classification_feedback;
  END IF;

  -- feedback_select_own
  IF EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'classification_feedback' AND policyname = 'feedback_select_own') THEN
    DROP POLICY feedback_select_own ON public.classification_feedback;
  END IF;

  -- feedback_update_own
  IF EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'classification_feedback' AND policyname = 'feedback_update_own') THEN
    DROP POLICY feedback_update_own ON public.classification_feedback;
  END IF;

  -- feedback_delete_own
  IF EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'classification_feedback' AND policyname = 'feedback_delete_own') THEN
    DROP POLICY feedback_delete_own ON public.classification_feedback;
  END IF;

  -- feedback_admin_all
  IF EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'classification_feedback' AND policyname = 'feedback_admin_all') THEN
    DROP POLICY feedback_admin_all ON public.classification_feedback;
  END IF;
END
$$;

CREATE POLICY feedback_insert_own ON public.classification_feedback
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY feedback_select_own ON public.classification_feedback
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY feedback_update_own ON public.classification_feedback
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY feedback_delete_own ON public.classification_feedback
    FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY feedback_admin_all ON public.classification_feedback
    FOR ALL USING (auth.role() = 'service_role');


-- ┌──────────────────────────────────────────────────────────────────────────┐
-- │ SECTION 3: Array normalization on search_sessions (from backend 010)    │
-- │ This is the SECOND object unique to backend/migrations/.               │
-- │ Idempotent: sorting an already-sorted array is a no-op.                │
-- └──────────────────────────────────────────────────────────────────────────┘

UPDATE public.search_sessions
SET ufs = (SELECT array_agg(u ORDER BY u) FROM unnest(ufs) u)
WHERE ufs IS NOT NULL;

UPDATE public.search_sessions
SET sectors = (SELECT array_agg(s ORDER BY s) FROM unnest(sectors) s)
WHERE sectors IS NOT NULL;


-- ┌──────────────────────────────────────────────────────────────────────────┐
-- │ SECTION 4: Notify PostgREST to reload schema cache                     │
-- └──────────────────────────────────────────────────────────────────────────┘

NOTIFY pgrst, 'reload schema';
