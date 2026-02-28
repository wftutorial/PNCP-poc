-- STORY-319: Reduce trial from 30 to 14 days
-- Grandfather clause for existing trial users

-- Step 1: Log current state for auditing
DO $$
DECLARE
  v_total_trial INTEGER;
  v_grandfathered INTEGER;
  v_new_limit INTEGER;
  v_already_expired INTEGER;
BEGIN
  -- Count all active trial users
  SELECT COUNT(*) INTO v_total_trial
  FROM profiles
  WHERE plan_type = 'free_trial'
    AND (trial_expires_at IS NULL OR trial_expires_at > NOW());

  -- Users created > 14 days ago: grandfather (keep their 30-day trial)
  SELECT COUNT(*) INTO v_grandfathered
  FROM profiles
  WHERE plan_type = 'free_trial'
    AND created_at < NOW() - INTERVAL '14 days'
    AND (trial_expires_at IS NULL OR trial_expires_at > NOW());

  -- Users created <= 14 days ago: apply new 14-day limit
  SELECT COUNT(*) INTO v_new_limit
  FROM profiles
  WHERE plan_type = 'free_trial'
    AND created_at >= NOW() - INTERVAL '14 days'
    AND (trial_expires_at IS NULL OR trial_expires_at > NOW());

  -- Users whose trial already expired
  SELECT COUNT(*) INTO v_already_expired
  FROM profiles
  WHERE plan_type = 'free_trial'
    AND trial_expires_at IS NOT NULL
    AND trial_expires_at <= NOW();

  RAISE NOTICE 'STORY-319 Trial Migration: total_active=%, grandfathered=%, new_limit=%, already_expired=%',
    v_total_trial, v_grandfathered, v_new_limit, v_already_expired;
END $$;

-- Step 2: Grandfather clause — users created > 14 days ago keep their 30-day trial
-- (No changes needed — their trial_expires_at is already set to created_at + 30 days)

-- Step 3: Users created <= 14 days ago — apply new 14-day limit
-- Only update if their current trial_expires_at is beyond created_at + 14 days
UPDATE profiles
SET trial_expires_at = created_at + INTERVAL '14 days'
WHERE plan_type = 'free_trial'
  AND created_at >= NOW() - INTERVAL '14 days'
  AND trial_expires_at IS NOT NULL
  AND trial_expires_at > created_at + INTERVAL '14 days';

-- Step 4: Users created <= 14 days ago with NULL trial_expires_at
-- Set trial_expires_at to created_at + 14 days
UPDATE profiles
SET trial_expires_at = created_at + INTERVAL '14 days'
WHERE plan_type = 'free_trial'
  AND created_at >= NOW() - INTERVAL '14 days'
  AND trial_expires_at IS NULL;

-- New users from this point forward will get 14-day trial via TRIAL_DURATION_DAYS=14 in config.py
