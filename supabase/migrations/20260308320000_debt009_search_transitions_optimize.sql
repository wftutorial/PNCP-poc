-- DEBT-009: Optimize search_state_transitions RLS (DB-007)
-- Replace expensive correlated subquery with direct user_id column.
--
-- Before: SELECT ... WHERE search_id IN (SELECT search_id FROM search_sessions WHERE user_id = auth.uid())
-- After:  SELECT ... WHERE user_id = auth.uid()
--
-- Steps:
-- 1. Add user_id column (nullable for backfill)
-- 2. Backfill from search_sessions
-- 3. Create index on user_id
-- 4. Replace SELECT RLS policy
-- 5. Fix INSERT policy to use TO service_role (was missing)

BEGIN;

-- ══════════════════════════════════════════════════════════════════
-- Step 1: Add user_id column
-- ══════════════════════════════════════════════════════════════════
ALTER TABLE public.search_state_transitions
    ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE;

-- ══════════════════════════════════════════════════════════════════
-- Step 2: Backfill user_id from search_sessions
-- ══════════════════════════════════════════════════════════════════
UPDATE public.search_state_transitions sst
SET user_id = ss.user_id
FROM public.search_sessions ss
WHERE sst.search_id = ss.search_id
  AND ss.search_id IS NOT NULL
  AND sst.user_id IS NULL;

-- ══════════════════════════════════════════════════════════════════
-- Step 3: Index on user_id for fast RLS evaluation
-- ══════════════════════════════════════════════════════════════════
CREATE INDEX IF NOT EXISTS idx_search_state_transitions_user_id
    ON public.search_state_transitions (user_id);

-- ══════════════════════════════════════════════════════════════════
-- Step 4: Replace SELECT policy (remove correlated subquery)
-- ══════════════════════════════════════════════════════════════════
DROP POLICY IF EXISTS "Users can read own transitions" ON public.search_state_transitions;

CREATE POLICY "Users can read own transitions"
    ON public.search_state_transitions
    FOR SELECT
    USING (user_id = auth.uid());

-- ══════════════════════════════════════════════════════════════════
-- Step 5: Fix INSERT policy — add TO service_role (was open to all)
-- ══════════════════════════════════════════════════════════════════
DROP POLICY IF EXISTS "Service role can insert transitions" ON public.search_state_transitions;

CREATE POLICY "service_role_all" ON public.search_state_transitions
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

COMMIT;

-- ══════════════════════════════════════════════════════════════════
-- Verification:
--
-- 1. Check user_id column exists:
-- SELECT column_name, data_type, is_nullable
-- FROM information_schema.columns
-- WHERE table_name = 'search_state_transitions' AND column_name = 'user_id';
--
-- 2. Check backfill completeness (should be 0 or very few orphans):
-- SELECT COUNT(*) FROM search_state_transitions WHERE user_id IS NULL;
--
-- 3. EXPLAIN should show Index Scan (not nested loop):
-- EXPLAIN SELECT * FROM search_state_transitions WHERE user_id = '00000000-0000-0000-0000-000000000001';
--
-- 4. Verify no correlated subquery in policies:
-- SELECT policyname, qual FROM pg_policies WHERE tablename = 'search_state_transitions';
-- ══════════════════════════════════════════════════════════════════

NOTIFY pgrst, 'reload schema';
