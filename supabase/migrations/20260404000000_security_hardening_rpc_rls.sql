-- ╔══════════════════════════════════════════════════════════════════════════╗
-- ║  SECURITY HARDENING: RPC auth.uid() guards + profiles privilege lock   ║
-- ║  Fixes: CRIT-SEC-001, CRIT-SEC-002, CRIT-SEC-004                     ║
-- ╚══════════════════════════════════════════════════════════════════════════╝

-- ──────────────────────────────────────────────────────────────────────────
-- SECTION 1: REVOKE direct RPC access for quota functions
-- These should ONLY be callable by service_role (backend), never by users
-- via PostgREST. Fixes CRIT-SEC-001 (quota manipulation).
-- ──────────────────────────────────────────────────────────────────────────

REVOKE EXECUTE ON FUNCTION public.increment_quota_atomic(UUID, VARCHAR, INT) FROM PUBLIC;
REVOKE EXECUTE ON FUNCTION public.increment_quota_atomic(UUID, VARCHAR, INT) FROM authenticated;
GRANT  EXECUTE ON FUNCTION public.increment_quota_atomic(UUID, VARCHAR, INT) TO service_role;

REVOKE EXECUTE ON FUNCTION public.check_and_increment_quota(UUID, VARCHAR, INT) FROM PUBLIC;
REVOKE EXECUTE ON FUNCTION public.check_and_increment_quota(UUID, VARCHAR, INT) FROM authenticated;
GRANT  EXECUTE ON FUNCTION public.check_and_increment_quota(UUID, VARCHAR, INT) TO service_role;

-- increment_quota_fallback_atomic (from older migration)
DO $$ BEGIN
  REVOKE EXECUTE ON FUNCTION public.increment_quota_fallback_atomic(UUID, TEXT, INTEGER) FROM PUBLIC;
  REVOKE EXECUTE ON FUNCTION public.increment_quota_fallback_atomic(UUID, TEXT, INTEGER) FROM authenticated;
  GRANT  EXECUTE ON FUNCTION public.increment_quota_fallback_atomic(UUID, TEXT, INTEGER) TO service_role;
EXCEPTION WHEN undefined_function THEN NULL;
END $$;


-- ──────────────────────────────────────────────────────────────────────────
-- SECTION 2: Add auth.uid() guard to user-facing RPC functions
-- These are called by users via PostgREST — must verify ownership.
-- Pattern: if auth.uid() IS NOT NULL (user context) then p_user_id must match.
-- Service role calls have auth.uid() = NULL and pass through.
-- ──────────────────────────────────────────────────────────────────────────

-- 2.1 get_analytics_summary — user can only query own analytics
CREATE OR REPLACE FUNCTION public.get_analytics_summary(
    p_user_id UUID,
    p_start_date TIMESTAMPTZ DEFAULT NULL,
    p_end_date TIMESTAMPTZ DEFAULT NULL
)
RETURNS TABLE (
    total_searches BIGINT,
    total_downloads BIGINT,
    total_opportunities BIGINT,
    total_value_discovered NUMERIC,
    member_since TIMESTAMPTZ
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    -- CRIT-SEC-001: Prevent cross-user data access via direct PostgREST call
    IF auth.uid() IS NOT NULL AND p_user_id != auth.uid() THEN
        RAISE EXCEPTION 'Forbidden: cannot access other user data'
            USING ERRCODE = '42501';  -- insufficient_privilege
    END IF;

    RETURN QUERY
    SELECT
        COUNT(*)::BIGINT as total_searches,
        COUNT(*) FILTER (WHERE ss.total_filtered > 0)::BIGINT as total_downloads,
        COALESCE(SUM(ss.total_filtered), 0)::BIGINT as total_opportunities,
        COALESCE(SUM(ss.valor_total), 0)::NUMERIC as total_value_discovered,
        (SELECT p.created_at FROM profiles p WHERE p.id = p_user_id) as member_since
    FROM search_sessions ss
    WHERE ss.user_id = p_user_id
        AND (p_start_date IS NULL OR ss.created_at >= p_start_date)
        AND (p_end_date IS NULL OR ss.created_at <= p_end_date);
END;
$$;

-- 2.2 get_conversations_with_unread_count — fix p_is_admin bypass (CRIT-SEC-004)
CREATE OR REPLACE FUNCTION public.get_conversations_with_unread_count(
    p_user_id UUID,
    p_is_admin BOOLEAN DEFAULT FALSE,
    p_status TEXT DEFAULT NULL,
    p_limit INT DEFAULT 50,
    p_offset INT DEFAULT 0
)
RETURNS TABLE (
    id UUID,
    user_id UUID,
    user_email TEXT,
    subject TEXT,
    category TEXT,
    status TEXT,
    last_message_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ,
    unread_count BIGINT,
    total_count BIGINT
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_is_admin BOOLEAN := FALSE;
BEGIN
    -- CRIT-SEC-004: Never trust p_is_admin parameter from client.
    -- Verify admin status from database instead.
    IF auth.uid() IS NOT NULL THEN
        -- User context: enforce ownership
        IF p_user_id != auth.uid() AND p_is_admin = FALSE THEN
            RAISE EXCEPTION 'Forbidden: cannot access other user data'
                USING ERRCODE = '42501';
        END IF;
        -- Verify actual admin status from profiles table
        SELECT COALESCE(p.is_admin, FALSE) INTO v_is_admin
        FROM profiles p WHERE p.id = auth.uid();
        -- If user claims admin but isn't, deny
        IF p_is_admin = TRUE AND v_is_admin = FALSE THEN
            RAISE EXCEPTION 'Forbidden: admin access required'
                USING ERRCODE = '42501';
        END IF;
    ELSE
        -- Service role context: trust p_is_admin
        v_is_admin := p_is_admin;
    END IF;

    RETURN QUERY
    WITH filtered_conversations AS (
        SELECT c.*,
            p.email as profile_email,
            COUNT(*) OVER() as total
        FROM conversations c
        LEFT JOIN profiles p ON p.id = c.user_id
        WHERE (v_is_admin OR c.user_id = p_user_id)
            AND (p_status IS NULL OR c.status = p_status)
        ORDER BY c.last_message_at DESC
        LIMIT p_limit OFFSET p_offset
    )
    SELECT
        fc.id,
        fc.user_id,
        CASE WHEN v_is_admin THEN fc.profile_email ELSE NULL END,
        fc.subject,
        fc.category,
        fc.status,
        fc.last_message_at,
        fc.created_at,
        COALESCE(uc.unread, 0)::BIGINT as unread_count,
        fc.total as total_count
    FROM filtered_conversations fc
    LEFT JOIN LATERAL (
        SELECT COUNT(*) as unread
        FROM messages m
        WHERE m.conversation_id = fc.id
        AND CASE
            WHEN v_is_admin THEN (m.is_admin_reply = FALSE AND m.read_by_admin = FALSE)
            ELSE (m.is_admin_reply = TRUE AND m.read_by_user = FALSE)
        END
    ) uc ON TRUE;
END;
$$;

-- 2.3 get_user_billing_period — user can only query own billing
CREATE OR REPLACE FUNCTION public.get_user_billing_period(p_user_id UUID)
RETURNS VARCHAR(10)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_billing_period VARCHAR(10);
BEGIN
  IF auth.uid() IS NOT NULL AND p_user_id != auth.uid() THEN
      RAISE EXCEPTION 'Forbidden: cannot access other user data'
          USING ERRCODE = '42501';
  END IF;

  SELECT billing_period INTO v_billing_period
  FROM public.user_subscriptions
  WHERE user_id = p_user_id AND is_active = true
  ORDER BY created_at DESC
  LIMIT 1;

  RETURN COALESCE(v_billing_period, 'monthly');
END;
$$;

-- 2.4 user_has_feature — user can only check own features
CREATE OR REPLACE FUNCTION public.user_has_feature(
  p_user_id UUID,
  p_feature_key VARCHAR(100)
)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_plan_id TEXT;
  v_billing_period VARCHAR(10);
  v_has_feature BOOLEAN;
BEGIN
  IF auth.uid() IS NOT NULL AND p_user_id != auth.uid() THEN
      RAISE EXCEPTION 'Forbidden: cannot access other user data'
          USING ERRCODE = '42501';
  END IF;

  SELECT us.plan_id, us.billing_period INTO v_plan_id, v_billing_period
  FROM public.user_subscriptions us
  WHERE us.user_id = p_user_id AND us.is_active = true
  ORDER BY us.created_at DESC
  LIMIT 1;

  IF v_plan_id IS NULL THEN
    RETURN false;
  END IF;

  SELECT EXISTS (
    SELECT 1 FROM public.plan_features
    WHERE plan_id = v_plan_id
      AND billing_period = v_billing_period
      AND feature_key = p_feature_key
      AND enabled = true
  ) INTO v_has_feature;

  RETURN v_has_feature;
END;
$$;

-- 2.5 get_user_features — user can only list own features
CREATE OR REPLACE FUNCTION public.get_user_features(p_user_id UUID)
RETURNS TEXT[]
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_plan_id TEXT;
  v_billing_period VARCHAR(10);
  v_features TEXT[];
BEGIN
  IF auth.uid() IS NOT NULL AND p_user_id != auth.uid() THEN
      RAISE EXCEPTION 'Forbidden: cannot access other user data'
          USING ERRCODE = '42501';
  END IF;

  SELECT us.plan_id, us.billing_period INTO v_plan_id, v_billing_period
  FROM public.user_subscriptions us
  WHERE us.user_id = p_user_id AND us.is_active = true
  ORDER BY us.created_at DESC
  LIMIT 1;

  IF v_plan_id IS NULL THEN
    RETURN ARRAY[]::TEXT[];
  END IF;

  SELECT ARRAY_AGG(feature_key) INTO v_features
  FROM public.plan_features
  WHERE plan_id = v_plan_id
    AND billing_period = v_billing_period
    AND enabled = true;

  RETURN COALESCE(v_features, ARRAY[]::TEXT[]);
END;
$$;


-- ──────────────────────────────────────────────────────────────────────────
-- SECTION 3: Profiles privilege escalation trigger (CRIT-SEC-002)
-- Prevents users from modifying protected columns via direct PostgREST PATCH.
-- Service role (backend) can still modify these columns.
-- ──────────────────────────────────────────────────────────────────────────

CREATE OR REPLACE FUNCTION public.prevent_privilege_escalation()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_role TEXT;
BEGIN
    -- Check if any protected field was changed
    IF (NEW.is_admin IS DISTINCT FROM OLD.is_admin) OR
       (NEW.is_master IS DISTINCT FROM OLD.is_master) OR
       (NEW.plan_type IS DISTINCT FROM OLD.plan_type) THEN

        -- Allow service_role (backend) to modify these fields
        v_role := coalesce(
            current_setting('request.jwt.claim.role', true),
            current_setting('role', true)
        );

        IF v_role IS DISTINCT FROM 'service_role' THEN
            RAISE EXCEPTION 'Cannot modify protected fields (is_admin, is_master, plan_type). Use the application API.'
                USING ERRCODE = '42501';
        END IF;
    END IF;

    RETURN NEW;
END;
$$;

-- Drop if exists to make idempotent
DROP TRIGGER IF EXISTS protect_profiles_escalation ON profiles;

CREATE TRIGGER protect_profiles_escalation
    BEFORE UPDATE ON profiles
    FOR EACH ROW
    EXECUTE FUNCTION prevent_privilege_escalation();


-- ──────────────────────────────────────────────────────────────────────────
-- SECTION 4: Restrict admin/system-only RPC functions
-- These should not be callable by regular authenticated users.
-- ──────────────────────────────────────────────────────────────────────────

-- upsert_pncp_raw_bids — ingestion only
DO $$ BEGIN
  REVOKE EXECUTE ON FUNCTION public.upsert_pncp_raw_bids FROM PUBLIC;
  REVOKE EXECUTE ON FUNCTION public.upsert_pncp_raw_bids FROM authenticated;
EXCEPTION WHEN undefined_function THEN NULL;
END $$;

-- purge_old_bids — maintenance only
DO $$ BEGIN
  REVOKE EXECUTE ON FUNCTION public.purge_old_bids FROM PUBLIC;
  REVOKE EXECUTE ON FUNCTION public.purge_old_bids FROM authenticated;
EXCEPTION WHEN undefined_function THEN NULL;
END $$;

-- check_ingestion_orphans — monitoring only
REVOKE EXECUTE ON FUNCTION public.check_ingestion_orphans() FROM PUBLIC;
REVOKE EXECUTE ON FUNCTION public.check_ingestion_orphans() FROM authenticated;
GRANT  EXECUTE ON FUNCTION public.check_ingestion_orphans() TO service_role;

-- check_pncp_raw_bids_bloat — monitoring only
DO $$ BEGIN
  REVOKE EXECUTE ON FUNCTION public.check_pncp_raw_bids_bloat FROM PUBLIC;
  REVOKE EXECUTE ON FUNCTION public.check_pncp_raw_bids_bloat FROM authenticated;
EXCEPTION WHEN undefined_function THEN NULL;
END $$;

-- pg_total_relation_size_safe — admin diagnostic only
REVOKE EXECUTE ON FUNCTION public.pg_total_relation_size_safe(TEXT) FROM PUBLIC;
REVOKE EXECUTE ON FUNCTION public.pg_total_relation_size_safe(TEXT) FROM authenticated;
GRANT  EXECUTE ON FUNCTION public.pg_total_relation_size_safe(TEXT) TO service_role;

-- get_table_columns_simple — admin diagnostic only
REVOKE EXECUTE ON FUNCTION public.get_table_columns_simple(TEXT) FROM PUBLIC;
REVOKE EXECUTE ON FUNCTION public.get_table_columns_simple(TEXT) FROM authenticated;
GRANT  EXECUTE ON FUNCTION public.get_table_columns_simple(TEXT) TO service_role;
