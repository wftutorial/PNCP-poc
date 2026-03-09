-- DEBT-009: Ban Cache Warmer System Account (DB-010)
-- Defense-in-depth: set banned_until to prevent any authentication attempt.
-- Account already has empty password, but banning adds another layer.

UPDATE auth.users
SET banned_until = '2099-12-31T23:59:59Z'
WHERE email = 'system-cache-warmer@internal.smartlic.tech';

-- ══════════════════════════════════════════════════════════════════
-- Verification:
-- SELECT id, email, banned_until FROM auth.users
-- WHERE email = 'system-cache-warmer@internal.smartlic.tech';
-- Expected: banned_until = 2099-12-31T23:59:59Z
-- ══════════════════════════════════════════════════════════════════
