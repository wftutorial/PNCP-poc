-- Fix sessions stuck in 'processing' status (ISSUE-014)
-- These are sessions where partial results were returned but status was never updated
UPDATE search_sessions
SET status = 'timed_out',
    completed_at = COALESCE(completed_at, NOW())
WHERE status = 'processing'
AND created_at < NOW() - INTERVAL '1 hour';
