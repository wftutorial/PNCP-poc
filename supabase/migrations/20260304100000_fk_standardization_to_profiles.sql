-- TD-001 AC1-AC6: Re-point 6 FKs from auth.users(id) to public.profiles(id)
-- Uses NOT VALID + separate VALIDATE for zero-downtime (no table lock on ADD)
--
-- CRITICAL: Run orphan detection BEFORE applying:
-- SELECT 'search_results_store' AS tbl, count(*) FROM search_results_store WHERE user_id NOT IN (SELECT id FROM profiles)
-- UNION ALL SELECT 'mfa_recovery_codes', count(*) FROM mfa_recovery_codes WHERE user_id NOT IN (SELECT id FROM profiles)
-- UNION ALL SELECT 'mfa_recovery_attempts', count(*) FROM mfa_recovery_attempts WHERE user_id NOT IN (SELECT id FROM profiles)
-- UNION ALL SELECT 'organizations', count(*) FROM organizations WHERE owner_id NOT IN (SELECT id FROM profiles)
-- UNION ALL SELECT 'organization_members', count(*) FROM organization_members WHERE user_id NOT IN (SELECT id FROM profiles)
-- UNION ALL SELECT 'partner_referrals', count(*) FROM partner_referrals WHERE referred_user_id NOT IN (SELECT id FROM profiles);

BEGIN;

-- ══════════════════════════════════════════════════════════════════
-- 1. search_results_store: user_id → profiles(id) ON DELETE CASCADE (AC3/H-02)
-- ══════════════════════════════════════════════════════════════════
ALTER TABLE public.search_results_store
  DROP CONSTRAINT IF EXISTS search_results_store_user_id_fkey;

ALTER TABLE public.search_results_store
  ADD CONSTRAINT search_results_store_user_id_fkey
  FOREIGN KEY (user_id) REFERENCES public.profiles(id) ON DELETE CASCADE
  NOT VALID;

-- ══════════════════════════════════════════════════════════════════
-- 2. mfa_recovery_codes: user_id → profiles(id) ON DELETE CASCADE
-- ══════════════════════════════════════════════════════════════════
ALTER TABLE public.mfa_recovery_codes
  DROP CONSTRAINT IF EXISTS mfa_recovery_codes_user_id_fkey;

ALTER TABLE public.mfa_recovery_codes
  ADD CONSTRAINT mfa_recovery_codes_user_id_fkey
  FOREIGN KEY (user_id) REFERENCES public.profiles(id) ON DELETE CASCADE
  NOT VALID;

-- ══════════════════════════════════════════════════════════════════
-- 3. mfa_recovery_attempts: user_id → profiles(id) ON DELETE CASCADE
-- ══════════════════════════════════════════════════════════════════
ALTER TABLE public.mfa_recovery_attempts
  DROP CONSTRAINT IF EXISTS mfa_recovery_attempts_user_id_fkey;

ALTER TABLE public.mfa_recovery_attempts
  ADD CONSTRAINT mfa_recovery_attempts_user_id_fkey
  FOREIGN KEY (user_id) REFERENCES public.profiles(id) ON DELETE CASCADE
  NOT VALID;

-- ══════════════════════════════════════════════════════════════════
-- 4. organizations: owner_id → profiles(id) ON DELETE RESTRICT
-- ══════════════════════════════════════════════════════════════════
ALTER TABLE public.organizations
  DROP CONSTRAINT IF EXISTS organizations_owner_id_fkey;

ALTER TABLE public.organizations
  ADD CONSTRAINT organizations_owner_id_fkey
  FOREIGN KEY (owner_id) REFERENCES public.profiles(id) ON DELETE RESTRICT
  NOT VALID;

-- ══════════════════════════════════════════════════════════════════
-- 5. organization_members: user_id → profiles(id) ON DELETE CASCADE
-- ══════════════════════════════════════════════════════════════════
ALTER TABLE public.organization_members
  DROP CONSTRAINT IF EXISTS organization_members_user_id_fkey;

ALTER TABLE public.organization_members
  ADD CONSTRAINT organization_members_user_id_fkey
  FOREIGN KEY (user_id) REFERENCES public.profiles(id) ON DELETE CASCADE
  NOT VALID;

-- ══════════════════════════════════════════════════════════════════
-- 6. partner_referrals: referred_user_id → profiles(id) ON DELETE SET NULL (AC4/M-03)
-- ══════════════════════════════════════════════════════════════════
ALTER TABLE public.partner_referrals
  DROP CONSTRAINT IF EXISTS partner_referrals_referred_user_id_fkey;

ALTER TABLE public.partner_referrals
  ADD CONSTRAINT partner_referrals_referred_user_id_fkey
  FOREIGN KEY (referred_user_id) REFERENCES public.profiles(id) ON DELETE SET NULL
  NOT VALID;

COMMIT;

-- ══════════════════════════════════════════════════════════════════
-- VALIDATE all constraints (concurrent-safe, reads-only, no locks) (AC2)
-- Run outside transaction for better concurrency
-- ══════════════════════════════════════════════════════════════════
ALTER TABLE public.search_results_store VALIDATE CONSTRAINT search_results_store_user_id_fkey;
ALTER TABLE public.mfa_recovery_codes VALIDATE CONSTRAINT mfa_recovery_codes_user_id_fkey;
ALTER TABLE public.mfa_recovery_attempts VALIDATE CONSTRAINT mfa_recovery_attempts_user_id_fkey;
ALTER TABLE public.organizations VALIDATE CONSTRAINT organizations_owner_id_fkey;
ALTER TABLE public.organization_members VALIDATE CONSTRAINT organization_members_user_id_fkey;
ALTER TABLE public.partner_referrals VALIDATE CONSTRAINT partner_referrals_referred_user_id_fkey;
