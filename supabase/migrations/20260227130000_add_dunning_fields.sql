-- STORY-309 AC7: Add dunning fields to user_subscriptions
-- first_failed_at: timestamp of first payment failure (for calculating days since failure)

ALTER TABLE user_subscriptions
ADD COLUMN IF NOT EXISTS first_failed_at TIMESTAMPTZ DEFAULT NULL;

-- Index for efficient dunning queries (find all past_due users)
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_first_failed_at
ON user_subscriptions (first_failed_at)
WHERE first_failed_at IS NOT NULL;

COMMENT ON COLUMN user_subscriptions.first_failed_at IS 'STORY-309: Timestamp of first payment failure for dunning sequence tracking';
