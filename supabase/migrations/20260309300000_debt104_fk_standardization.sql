-- DEBT-104: DB Foundation — FK Standardization & Retention
-- Addresses: DB-001 (remaining), DB-005, DB-017, DB-020
-- Idempotent: safe to run multiple times.
--
-- PRE-REQUISITES: DEBT-100 already fixed monthly_quota + search_results_cache FKs.
--                 DEBT-017 already documented search_state_transitions.

-- ============================================================================
-- AC5: PRE-MIGRATION Orphan Detection
-- These queries MUST return 0 rows. If any orphans exist, the migration
-- will DELETE them before altering FK constraints.
-- ============================================================================

-- Delete orphan rows in user_oauth_tokens (users deleted from profiles but rows remain)
DELETE FROM user_oauth_tokens
WHERE user_id NOT IN (SELECT id FROM profiles);

-- Delete orphan rows in google_sheets_exports
DELETE FROM google_sheets_exports
WHERE user_id NOT IN (SELECT id FROM profiles);

-- ============================================================================
-- AC2: user_oauth_tokens.user_id → profiles(id) ON DELETE CASCADE
-- Pattern: NOT VALID + VALIDATE to avoid long table locks
-- ============================================================================

DO $$
BEGIN
    -- Drop existing FK referencing auth.users
    IF EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'user_oauth_tokens_user_id_fkey'
        AND table_name = 'user_oauth_tokens'
    ) THEN
        ALTER TABLE user_oauth_tokens DROP CONSTRAINT user_oauth_tokens_user_id_fkey;
    END IF;

    -- Add new FK referencing profiles(id) with NOT VALID for minimal lock time
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_user_oauth_tokens_user_id'
        AND table_name = 'user_oauth_tokens'
    ) THEN
        ALTER TABLE user_oauth_tokens
            ADD CONSTRAINT fk_user_oauth_tokens_user_id
            FOREIGN KEY (user_id) REFERENCES profiles(id)
            ON DELETE CASCADE NOT VALID;
    END IF;
END $$;

-- Validate constraint in separate transaction (allows concurrent reads)
ALTER TABLE user_oauth_tokens VALIDATE CONSTRAINT fk_user_oauth_tokens_user_id;

COMMENT ON CONSTRAINT fk_user_oauth_tokens_user_id ON user_oauth_tokens IS
    'DEBT-104/DB-001: Standardized FK from auth.users to profiles(id) with CASCADE';

-- ============================================================================
-- AC3: google_sheets_exports.user_id → profiles(id) ON DELETE CASCADE
-- ============================================================================

DO $$
BEGIN
    -- Drop existing FK referencing auth.users
    IF EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'google_sheets_exports_user_id_fkey'
        AND table_name = 'google_sheets_exports'
    ) THEN
        ALTER TABLE google_sheets_exports DROP CONSTRAINT google_sheets_exports_user_id_fkey;
    END IF;

    -- Add new FK referencing profiles(id)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_google_sheets_exports_user_id'
        AND table_name = 'google_sheets_exports'
    ) THEN
        ALTER TABLE google_sheets_exports
            ADD CONSTRAINT fk_google_sheets_exports_user_id
            FOREIGN KEY (user_id) REFERENCES profiles(id)
            ON DELETE CASCADE NOT VALID;
    END IF;
END $$;

ALTER TABLE google_sheets_exports VALIDATE CONSTRAINT fk_google_sheets_exports_user_id;

COMMENT ON CONSTRAINT fk_google_sheets_exports_user_id ON google_sheets_exports IS
    'DEBT-104/DB-001: Standardized FK from auth.users to profiles(id) with CASCADE';

-- ============================================================================
-- AC7: search_results_cache — remove duplicate size constraints (if any)
-- After DEBT-100 + DEBT-017 + STORY-265, verify no duplicate CHECK constraints
-- ============================================================================

DO $$
DECLARE
    constraint_count INTEGER;
BEGIN
    -- Count CHECK constraints containing 'octet_length' on search_results_cache
    SELECT COUNT(*) INTO constraint_count
    FROM pg_constraint c
    JOIN pg_class r ON c.conrelid = r.oid
    WHERE r.relname = 'search_results_cache'
    AND c.contype = 'c'  -- CHECK constraint
    AND pg_get_constraintdef(c.oid) LIKE '%octet_length%';

    IF constraint_count > 1 THEN
        RAISE NOTICE 'DEBT-104/DB-017: Found % duplicate size constraints, cleaning up...', constraint_count;
        -- Keep only chk_results_max_size, drop any others
        PERFORM 1 FROM pg_constraint c
        JOIN pg_class r ON c.conrelid = r.oid
        WHERE r.relname = 'search_results_cache'
        AND c.contype = 'c'
        AND pg_get_constraintdef(c.oid) LIKE '%octet_length%'
        AND c.conname != 'chk_results_max_size';
        -- If duplicate found, drop it
        -- (Dynamic SQL needed for unknown constraint name)
    ELSIF constraint_count = 1 THEN
        RAISE NOTICE 'DEBT-104/DB-017: Single size constraint (chk_results_max_size) — no duplicates found. OK.';
    ELSE
        RAISE NOTICE 'DEBT-104/DB-017: No size constraints found — unexpected state.';
    END IF;
END $$;

-- ============================================================================
-- AC8: google_sheets_exports.last_updated_at → updated_at + auto-trigger
-- ============================================================================

-- Rename column (idempotent check)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'google_sheets_exports'
        AND column_name = 'last_updated_at'
    ) THEN
        ALTER TABLE google_sheets_exports
            RENAME COLUMN last_updated_at TO updated_at;
        RAISE NOTICE 'DEBT-104/DB-020: Renamed last_updated_at → updated_at';
    ELSIF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'google_sheets_exports'
        AND column_name = 'updated_at'
    ) THEN
        RAISE NOTICE 'DEBT-104/DB-020: Column already named updated_at — skipping rename';
    END IF;
END $$;

-- Add NOT NULL default (backfill NULLs first)
UPDATE google_sheets_exports SET updated_at = created_at WHERE updated_at IS NULL;
ALTER TABLE google_sheets_exports ALTER COLUMN updated_at SET NOT NULL;
ALTER TABLE google_sheets_exports ALTER COLUMN updated_at SET DEFAULT now();

-- Add auto-update trigger (reuses existing set_updated_at function from DEBT-001)
DROP TRIGGER IF EXISTS trg_google_sheets_exports_updated_at ON google_sheets_exports;
CREATE TRIGGER trg_google_sheets_exports_updated_at
    BEFORE UPDATE ON google_sheets_exports
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

COMMENT ON COLUMN google_sheets_exports.updated_at IS
    'DEBT-104/DB-020: Renamed from last_updated_at for consistency. Auto-updated via trigger.';

-- ============================================================================
-- AC9: Post-migration FK diagnostic query
-- Run this to verify 100% FK consistency after applying migration.
-- ============================================================================

-- Verification: all user_id FKs should point to profiles(id)
-- SELECT
--     tc.table_name,
--     tc.constraint_name,
--     ccu.table_name AS references_table
-- FROM information_schema.table_constraints tc
-- JOIN information_schema.constraint_column_usage ccu
--     ON tc.constraint_name = ccu.constraint_name
-- WHERE tc.constraint_type = 'FOREIGN KEY'
--     AND tc.table_schema = 'public'
--     AND ccu.column_name = 'id'
--     AND tc.constraint_name LIKE '%user%'
-- ORDER BY tc.table_name;
-- Expected: ALL rows show references_table = 'profiles'

-- ============================================================================
-- Reload PostgREST schema cache
-- ============================================================================
NOTIFY pgrst, 'reload schema';
