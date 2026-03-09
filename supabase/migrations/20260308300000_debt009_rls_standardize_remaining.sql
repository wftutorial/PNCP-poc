-- DEBT-009: RLS Policy Standardization (DB-001, DB-002)
-- Standardize remaining auth.role() patterns to TO service_role USING (true)
-- Also adds explicit service_role policies where missing.
--
-- DB-001: classification_feedback uses auth.role() in feedback_admin_all
-- DB-048: partners/partner_referrals — ALREADY FIXED in 20260304200000 (no action)
-- DB-002: health_checks and incidents have RLS enabled but no service_role policy

-- All statements use DROP IF EXISTS + CREATE for full idempotency.

-- ══════════════════════════════════════════════════════════════════
-- 1. classification_feedback (DB-001)
-- Replace auth.role() policy with TO service_role pattern
-- ══════════════════════════════════════════════════════════════════
DROP POLICY IF EXISTS "feedback_admin_all" ON public.classification_feedback;
DROP POLICY IF EXISTS "service_role_all" ON public.classification_feedback;

CREATE POLICY "service_role_all" ON public.classification_feedback
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- ══════════════════════════════════════════════════════════════════
-- 2. health_checks (DB-002)
-- Backend-only table: RLS enabled but no policies → backend blocked
-- ══════════════════════════════════════════════════════════════════
DROP POLICY IF EXISTS "service_role_all" ON public.health_checks;

CREATE POLICY "service_role_all" ON public.health_checks
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- ══════════════════════════════════════════════════════════════════
-- 3. incidents (DB-002)
-- Backend-only table: same issue as health_checks
-- ══════════════════════════════════════════════════════════════════
DROP POLICY IF EXISTS "service_role_all" ON public.incidents;

CREATE POLICY "service_role_all" ON public.incidents
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- ══════════════════════════════════════════════════════════════════
-- Verification: Should return 0 rows (no auth.role() in public RLS)
-- SELECT schemaname, tablename, policyname, qual
-- FROM pg_policies
-- WHERE schemaname = 'public' AND qual LIKE '%auth.role()%';
-- ══════════════════════════════════════════════════════════════════

NOTIFY pgrst, 'reload schema';
