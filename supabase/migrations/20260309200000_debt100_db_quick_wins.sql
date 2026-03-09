-- DEBT-100: DB Quick Wins — Integrity, Retention & Indexes
-- Addresses: DB-NEW-01, DB-NEW-02, DB-NEW-03, DB-NEW-04, DB-011, DB-015,
--            DB-016, DB-018, DB-021, DB-026
-- Idempotent: safe to run multiple times.

-- ============================================================================
-- AC1: DB-NEW-01 — search_results_store FK validation verification
-- The FK on search_results_store.user_id -> auth.users(id) was created
-- NOT VALID. We need to verify its current state.
-- If NOT VALID, validate it. If already valid, no-op.
-- ============================================================================

DO $$
DECLARE
    fk_is_valid BOOLEAN;
BEGIN
    -- Check if FK constraint is valid
    SELECT convalidated INTO fk_is_valid
    FROM pg_constraint
    WHERE conrelid = 'public.search_results_store'::regclass
      AND contype = 'f'
      AND conname LIKE '%user_id%'
    LIMIT 1;

    IF fk_is_valid IS NULL THEN
        RAISE NOTICE 'DB-NEW-01: No FK constraint found on search_results_store.user_id — may need manual review';
    ELSIF fk_is_valid THEN
        RAISE NOTICE 'DB-NEW-01: search_results_store FK on user_id is already VALIDATED';
    ELSE
        RAISE NOTICE 'DB-NEW-01: search_results_store FK on user_id is NOT VALID — validating now...';
        -- Validate the FK (takes ShareUpdateExclusiveLock, non-blocking on reads)
        -- Find the actual constraint name dynamically
        EXECUTE format(
            'ALTER TABLE public.search_results_store VALIDATE CONSTRAINT %I',
            (SELECT conname FROM pg_constraint
             WHERE conrelid = 'public.search_results_store'::regclass
               AND contype = 'f' AND conname LIKE '%user_id%' LIMIT 1)
        );
        RAISE NOTICE 'DB-NEW-01: FK validated successfully';
    END IF;
END $$;


-- ============================================================================
-- AC2: DB-NEW-04 — search_results_cache FK state verification
-- Multiple migrations touched this FK. Verify and validate if needed.
-- ============================================================================

DO $$
DECLARE
    fk_is_valid BOOLEAN;
BEGIN
    SELECT convalidated INTO fk_is_valid
    FROM pg_constraint
    WHERE conrelid = 'public.search_results_cache'::regclass
      AND contype = 'f'
      AND conname LIKE '%user_id%'
    LIMIT 1;

    IF fk_is_valid IS NULL THEN
        RAISE NOTICE 'DB-NEW-04: No FK constraint found on search_results_cache.user_id — may need manual review';
    ELSIF fk_is_valid THEN
        RAISE NOTICE 'DB-NEW-04: search_results_cache FK on user_id is already VALIDATED';
    ELSE
        RAISE NOTICE 'DB-NEW-04: search_results_cache FK on user_id is NOT VALID — validating now...';
        EXECUTE format(
            'ALTER TABLE public.search_results_cache VALIDATE CONSTRAINT %I',
            (SELECT conname FROM pg_constraint
             WHERE conrelid = 'public.search_results_cache'::regclass
               AND contype = 'f' AND conname LIKE '%user_id%' LIMIT 1)
        );
        RAISE NOTICE 'DB-NEW-04: FK validated successfully';
    END IF;
END $$;


-- ============================================================================
-- AC3: DB-NEW-03 — pg_cron job for search_results_store retention
-- expires_at exists but no pg_cron cleans up. Create daily cleanup.
-- Note: A job 'cleanup-expired-search-results' may already exist from
-- migration 022/search_results_store creation. We upsert to be safe.
-- ============================================================================

DO $$
BEGIN
    -- Remove existing job if present, then re-create with correct schedule
    PERFORM cron.unschedule('cleanup-expired-search-results');
EXCEPTION
    WHEN others THEN NULL; -- Job didn't exist, that's fine
END $$;

SELECT cron.schedule(
    'cleanup-expired-search-results',
    '0 4 * * *',  -- Daily at 4:00 UTC (aligned with other cleanup jobs)
    $$DELETE FROM public.search_results_store WHERE expires_at < now()$$
);

COMMENT ON COLUMN search_results_store.expires_at IS
    'DEBT-100/DB-NEW-03: Cleaned up daily by pg_cron job cleanup-expired-search-results (4:00 UTC)';


-- ============================================================================
-- AC4: DB-026 — pg_cron job for search_sessions retention (12 months)
-- search_sessions accumulating without retention policy.
-- ============================================================================

DO $$
BEGIN
    PERFORM cron.unschedule('cleanup-old-search-sessions');
EXCEPTION
    WHEN others THEN NULL;
END $$;

SELECT cron.schedule(
    'cleanup-old-search-sessions',
    '30 4 * * *',  -- Daily at 4:30 UTC (staggered from other jobs)
    $$DELETE FROM public.search_sessions WHERE created_at < now() - interval '12 months'$$
);


-- ============================================================================
-- AC5: DB-021 — organizations.plan_type CHECK constraint
-- Currently accepts any text. Add CHECK with valid values.
-- ============================================================================

DO $$
BEGIN
    -- Add CHECK constraint if not already present
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'public.organizations'::regclass
          AND conname = 'chk_organizations_plan_type'
    ) THEN
        ALTER TABLE public.organizations
            ADD CONSTRAINT chk_organizations_plan_type
            CHECK (plan_type IN (
                'free_trial', 'smartlic_pro', 'consultoria',
                'consultor_agil', 'maquina', 'sala_guerra',
                'pro', 'free', 'avulso', 'pack', 'monthly', 'annual', 'master'
            ));
        RAISE NOTICE 'DB-021: CHECK constraint chk_organizations_plan_type added';
    ELSE
        RAISE NOTICE 'DB-021: CHECK constraint chk_organizations_plan_type already exists';
    END IF;
END $$;


-- ============================================================================
-- AC6: DB-018 — partner_referrals.partner_id ON DELETE CASCADE
-- Currently has no CASCADE behavior. Replace FK with CASCADE.
-- ============================================================================

DO $$
DECLARE
    fk_name TEXT;
BEGIN
    -- Find existing FK constraint name
    SELECT conname INTO fk_name
    FROM pg_constraint
    WHERE conrelid = 'public.partner_referrals'::regclass
      AND contype = 'f'
      AND conname LIKE '%partner_id%'
      AND confrelid = 'public.partners'::regclass
    LIMIT 1;

    IF fk_name IS NOT NULL THEN
        -- Check if it already has CASCADE
        IF EXISTS (
            SELECT 1 FROM pg_constraint
            WHERE conrelid = 'public.partner_referrals'::regclass
              AND conname = fk_name
              AND confdeltype = 'c'  -- 'c' = CASCADE
        ) THEN
            RAISE NOTICE 'DB-018: partner_referrals.partner_id FK already has ON DELETE CASCADE';
        ELSE
            EXECUTE format('ALTER TABLE public.partner_referrals DROP CONSTRAINT %I', fk_name);
            ALTER TABLE public.partner_referrals
                ADD CONSTRAINT fk_partner_referrals_partner_id
                FOREIGN KEY (partner_id) REFERENCES public.partners(id) ON DELETE CASCADE;
            RAISE NOTICE 'DB-018: partner_referrals.partner_id FK replaced with ON DELETE CASCADE';
        END IF;
    ELSE
        -- No FK exists, create one
        ALTER TABLE public.partner_referrals
            ADD CONSTRAINT fk_partner_referrals_partner_id
            FOREIGN KEY (partner_id) REFERENCES public.partners(id) ON DELETE CASCADE;
        RAISE NOTICE 'DB-018: partner_referrals.partner_id FK created with ON DELETE CASCADE';
    END IF;
END $$;


-- ============================================================================
-- AC7: DB-015 — monthly_quota.user_id references profiles(id)
-- Migration 018 already changed this from auth.users to profiles(id).
-- Verify the FK is correct and has ON DELETE CASCADE.
-- ============================================================================

DO $$
DECLARE
    fk_target TEXT;
    fk_name TEXT;
    fk_cascade CHAR;
BEGIN
    SELECT conname, confdeltype,
           (SELECT relname FROM pg_class WHERE oid = confrelid)
    INTO fk_name, fk_cascade, fk_target
    FROM pg_constraint
    WHERE conrelid = 'public.monthly_quota'::regclass
      AND contype = 'f'
      AND conname LIKE '%user_id%'
    LIMIT 1;

    IF fk_name IS NULL THEN
        -- No FK, create one pointing to profiles
        ALTER TABLE public.monthly_quota
            ADD CONSTRAINT fk_monthly_quota_user_id
            FOREIGN KEY (user_id) REFERENCES public.profiles(id) ON DELETE CASCADE
            NOT VALID;
        ALTER TABLE public.monthly_quota
            VALIDATE CONSTRAINT fk_monthly_quota_user_id;
        RAISE NOTICE 'DB-015: monthly_quota.user_id FK created -> profiles(id) ON DELETE CASCADE';
    ELSIF fk_target = 'profiles' AND fk_cascade = 'c' THEN
        RAISE NOTICE 'DB-015: monthly_quota.user_id FK already references profiles(id) with CASCADE — OK';
    ELSIF fk_target = 'profiles' AND fk_cascade != 'c' THEN
        -- Points to profiles but without CASCADE
        EXECUTE format('ALTER TABLE public.monthly_quota DROP CONSTRAINT %I', fk_name);
        ALTER TABLE public.monthly_quota
            ADD CONSTRAINT fk_monthly_quota_user_id
            FOREIGN KEY (user_id) REFERENCES public.profiles(id) ON DELETE CASCADE;
        RAISE NOTICE 'DB-015: monthly_quota.user_id FK re-created with ON DELETE CASCADE';
    ELSE
        -- Points to auth.users, need to change to profiles
        EXECUTE format('ALTER TABLE public.monthly_quota DROP CONSTRAINT %I', fk_name);
        ALTER TABLE public.monthly_quota
            ADD CONSTRAINT fk_monthly_quota_user_id
            FOREIGN KEY (user_id) REFERENCES public.profiles(id) ON DELETE CASCADE
            NOT VALID;
        ALTER TABLE public.monthly_quota
            VALIDATE CONSTRAINT fk_monthly_quota_user_id;
        RAISE NOTICE 'DB-015: monthly_quota.user_id FK changed from auth.users to profiles(id) ON DELETE CASCADE';
    END IF;
END $$;


-- ============================================================================
-- AC8: DB-NEW-02 — Remove duplicate index on search_results_store
-- idx_search_results_user and idx_search_results_store_user_id are both
-- on (user_id). Keep the one with more descriptive name, drop the other.
-- Only drop if idx_scan = 0 or both exist (one is redundant by definition).
-- ============================================================================

DO $$
BEGIN
    -- Drop the shorter-named duplicate (if it exists)
    IF EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE tablename = 'search_results_store'
          AND indexname = 'idx_search_results_user'
    ) AND EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE tablename = 'search_results_store'
          AND indexname = 'idx_search_results_store_user_id'
    ) THEN
        -- Both exist — drop the less specific one
        DROP INDEX IF EXISTS idx_search_results_store_user_id;
        RAISE NOTICE 'DB-NEW-02: Dropped duplicate index idx_search_results_store_user_id (kept idx_search_results_user)';
    ELSE
        RAISE NOTICE 'DB-NEW-02: No duplicate indexes found — one or both already removed';
    END IF;
END $$;


-- ============================================================================
-- AC9: DB-016 — Add updated_at to incidents and partners + trigger
-- ============================================================================

-- Helper function for updated_at trigger (reusable)
CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- incidents: add updated_at column
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'incidents'
          AND column_name = 'updated_at'
    ) THEN
        ALTER TABLE public.incidents
            ADD COLUMN updated_at TIMESTAMPTZ NOT NULL DEFAULT now();
        RAISE NOTICE 'DB-016: incidents.updated_at column added';
    ELSE
        RAISE NOTICE 'DB-016: incidents.updated_at already exists';
    END IF;
END $$;

-- incidents: create trigger
DROP TRIGGER IF EXISTS trg_incidents_updated_at ON public.incidents;
CREATE TRIGGER trg_incidents_updated_at
    BEFORE UPDATE ON public.incidents
    FOR EACH ROW
    EXECUTE FUNCTION public.set_updated_at();

-- partners: add updated_at column
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'partners'
          AND column_name = 'updated_at'
    ) THEN
        ALTER TABLE public.partners
            ADD COLUMN updated_at TIMESTAMPTZ NOT NULL DEFAULT now();
        RAISE NOTICE 'DB-016: partners.updated_at column added';
    ELSE
        RAISE NOTICE 'DB-016: partners.updated_at already exists';
    END IF;
END $$;

-- partners: create trigger
DROP TRIGGER IF EXISTS trg_partners_updated_at ON public.partners;
CREATE TRIGGER trg_partners_updated_at
    BEFORE UPDATE ON public.partners
    FOR EACH ROW
    EXECUTE FUNCTION public.set_updated_at();


-- ============================================================================
-- AC10: DB-011 — Remove redundant indexes (after verifying idx_scan = 0)
-- Targets: search_sessions and partners tables
-- search_sessions: idx_search_sessions_user vs idx_search_sessions_created
--   - idx_search_sessions_user ON (user_id) — subsumed by
--     idx_search_sessions_created ON (user_id, created_at DESC)
-- partners: idx_partners_status ON (status) — low cardinality, likely unused
-- ============================================================================

-- search_sessions: drop idx_search_sessions_user if redundant
DO $$
DECLARE
    scan_count BIGINT;
BEGIN
    SELECT idx_scan INTO scan_count
    FROM pg_stat_user_indexes
    WHERE indexrelname = 'idx_search_sessions_user';

    IF scan_count IS NULL THEN
        RAISE NOTICE 'DB-011: idx_search_sessions_user not found — already removed or renamed';
    ELSIF scan_count = 0 THEN
        DROP INDEX IF EXISTS idx_search_sessions_user;
        RAISE NOTICE 'DB-011: Dropped idx_search_sessions_user (idx_scan=0, subsumed by idx_search_sessions_created)';
    ELSE
        RAISE NOTICE 'DB-011: idx_search_sessions_user has idx_scan=% — keeping (not redundant in practice)', scan_count;
    END IF;
END $$;

-- partners: drop idx_partners_status if unused
DO $$
DECLARE
    scan_count BIGINT;
BEGIN
    SELECT idx_scan INTO scan_count
    FROM pg_stat_user_indexes
    WHERE indexrelname = 'idx_partners_status';

    IF scan_count IS NULL THEN
        RAISE NOTICE 'DB-011: idx_partners_status not found — already removed or renamed';
    ELSIF scan_count = 0 THEN
        DROP INDEX IF EXISTS idx_partners_status;
        RAISE NOTICE 'DB-011: Dropped idx_partners_status (idx_scan=0, low cardinality)';
    ELSE
        RAISE NOTICE 'DB-011: idx_partners_status has idx_scan=% — keeping', scan_count;
    END IF;
END $$;


-- ============================================================================
-- Verification summary (run after migration)
-- ============================================================================
-- SELECT jobname, schedule, command FROM cron.job ORDER BY jobname;
-- SELECT conname, convalidated, confdeltype
--   FROM pg_constraint
--   WHERE conrelid IN (
--     'public.search_results_store'::regclass,
--     'public.search_results_cache'::regclass,
--     'public.monthly_quota'::regclass,
--     'public.partner_referrals'::regclass,
--     'public.organizations'::regclass
--   ) AND contype = 'f';
-- SELECT indexname, tablename FROM pg_indexes
--   WHERE tablename IN ('search_results_store','search_sessions','partners')
--   ORDER BY tablename, indexname;
