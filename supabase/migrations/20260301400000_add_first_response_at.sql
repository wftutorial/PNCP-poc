-- STORY-353 AC1: Add first_response_at to conversations for SLA tracking
-- Records when the admin first replied to a conversation.

ALTER TABLE conversations
    ADD COLUMN IF NOT EXISTS first_response_at timestamptz;

-- Index for SLA queries: find unanswered conversations efficiently
CREATE INDEX IF NOT EXISTS idx_conversations_unanswered
    ON conversations(created_at)
    WHERE first_response_at IS NULL AND status != 'resolvido';
