-- STORY-362 AC4: Persistent L3 storage for search results
-- Prevents "Busca não encontrada ou expirada" after L1/L2 TTL expiry

CREATE TABLE IF NOT EXISTS search_results_store (
    search_id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id),
    results JSONB NOT NULL,
    sector TEXT,
    ufs TEXT[],
    total_filtered INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now(),
    expires_at TIMESTAMPTZ DEFAULT now() + INTERVAL '24 hours'
);

CREATE INDEX idx_search_results_user ON search_results_store(user_id);
CREATE INDEX idx_search_results_expires ON search_results_store(expires_at);

ALTER TABLE search_results_store ENABLE ROW LEVEL SECURITY;

-- AC12: RLS — users can only read their own results
CREATE POLICY "Users can read own results" ON search_results_store
    FOR SELECT USING (auth.uid() = user_id);

-- Service role can insert/delete (backend uses service_role_key)
CREATE POLICY "Service role full access" ON search_results_store
    FOR ALL USING (auth.role() = 'service_role');
