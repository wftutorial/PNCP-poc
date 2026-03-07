-- HARDEN-023: Add indexes on user_id columns for RLS performance
-- Supabase docs recommend indexing columns used in RLS policies
-- to avoid full table scans (100x+ improvement documented)

CREATE INDEX IF NOT EXISTS idx_searches_user_id ON searches(user_id);
CREATE INDEX IF NOT EXISTS idx_pipeline_user_id ON pipeline(user_id);
CREATE INDEX IF NOT EXISTS idx_feedback_user_id ON feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_search_results_store_user_id ON search_results_store(user_id);
CREATE INDEX IF NOT EXISTS idx_search_sessions_user_id ON search_sessions(user_id);
