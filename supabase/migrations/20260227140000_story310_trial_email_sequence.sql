-- STORY-310: Trial Email Sequence — 8 emails over 30 days
-- AC10: Enhance trial_email_log with email_number + tracking columns
-- AC5: Add marketing_emails_enabled to profiles for unsubscribe support

-- 1. Add email_number column to trial_email_log
ALTER TABLE trial_email_log
  ADD COLUMN IF NOT EXISTS email_number INTEGER;

-- 2. Add tracking columns for Resend webhook (AC11)
ALTER TABLE trial_email_log
  ADD COLUMN IF NOT EXISTS opened_at TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS clicked_at TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS resend_email_id TEXT;

-- 3. Backfill email_number from email_type for existing rows
UPDATE trial_email_log SET email_number = CASE email_type
  WHEN 'midpoint'  THEN 2
  WHEN 'expiring'  THEN 6
  WHEN 'last_day'  THEN 7
  WHEN 'expired'   THEN 8
  ELSE NULL
END
WHERE email_number IS NULL;

-- 4. Add UNIQUE constraint on (user_id, email_number) — AC10
-- Drop old constraint first (if exists), then add new one
DO $$
BEGIN
  -- Drop old unique constraint on (user_id, email_type) if it exists
  IF EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'trial_email_log_user_id_email_type_key'
  ) THEN
    ALTER TABLE trial_email_log DROP CONSTRAINT trial_email_log_user_id_email_type_key;
  END IF;
END $$;

-- Add new unique constraint
ALTER TABLE trial_email_log
  ADD CONSTRAINT trial_email_log_user_id_email_number_key UNIQUE (user_id, email_number);

-- 5. Index for efficient webhook lookups by resend_email_id
CREATE INDEX IF NOT EXISTS idx_trial_email_log_resend_id
  ON trial_email_log(resend_email_id) WHERE resend_email_id IS NOT NULL;

-- 6. Add marketing_emails_enabled to profiles (AC5: unsubscribe support)
ALTER TABLE profiles
  ADD COLUMN IF NOT EXISTS marketing_emails_enabled BOOLEAN NOT NULL DEFAULT TRUE;

COMMENT ON COLUMN trial_email_log.email_number IS 'STORY-310: Sequential email number (1-8) in the trial sequence';
COMMENT ON COLUMN trial_email_log.opened_at IS 'STORY-310 AC11: Timestamp when email was opened (Resend webhook)';
COMMENT ON COLUMN trial_email_log.clicked_at IS 'STORY-310 AC11: Timestamp when email CTA was clicked (Resend webhook)';
COMMENT ON COLUMN trial_email_log.resend_email_id IS 'STORY-310 AC11: Resend email ID for webhook correlation';
COMMENT ON COLUMN profiles.marketing_emails_enabled IS 'STORY-310 AC5: User opt-out for marketing/trial emails';
