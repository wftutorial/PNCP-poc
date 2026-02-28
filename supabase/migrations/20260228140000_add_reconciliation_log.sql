-- STORY-314 AC7: Reconciliation log table for Stripe ⇄ DB sync audit trail
CREATE TABLE IF NOT EXISTS reconciliation_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    total_checked INT NOT NULL DEFAULT 0,
    divergences_found INT NOT NULL DEFAULT 0,
    auto_fixed INT NOT NULL DEFAULT 0,
    manual_review INT NOT NULL DEFAULT 0,
    duration_ms INT NOT NULL DEFAULT 0,
    details JSONB DEFAULT '[]'::jsonb
);

-- Index for quick history queries (last 30 runs)
CREATE INDEX IF NOT EXISTS idx_reconciliation_log_run_at
    ON reconciliation_log (run_at DESC);

-- RLS: admin-only access
ALTER TABLE reconciliation_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Admin read reconciliation_log"
    ON reconciliation_log FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.id = auth.uid()
            AND profiles.is_admin = true
        )
    );

CREATE POLICY "Service role full access reconciliation_log"
    ON reconciliation_log FOR ALL
    USING (auth.role() = 'service_role');
