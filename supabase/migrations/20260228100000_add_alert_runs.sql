-- STORY-315 AC10: alert_runs table for alert execution history and debugging
-- Tracks each cron execution per alert: items found, items sent, status

CREATE TABLE IF NOT EXISTS alert_runs (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  alert_id UUID NOT NULL REFERENCES alerts(id) ON DELETE CASCADE,
  run_at TIMESTAMPTZ DEFAULT now() NOT NULL,
  items_found INTEGER NOT NULL DEFAULT 0,
  items_sent INTEGER NOT NULL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'pending'
);

COMMENT ON TABLE alert_runs IS 'STORY-315 AC10: Alert execution history for debugging and auditing';
COMMENT ON COLUMN alert_runs.status IS 'Run outcome: matched, no_results, no_match, all_deduped, error';

-- Indexes for efficient querying
CREATE INDEX idx_alert_runs_alert_id ON alert_runs(alert_id);
CREATE INDEX idx_alert_runs_run_at ON alert_runs(run_at DESC);

-- RLS: service role for cron, users can view own alert runs
ALTER TABLE alert_runs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role full access to alert_runs"
  ON alert_runs FOR ALL
  TO service_role
  USING (true) WITH CHECK (true);

CREATE POLICY "Users can view own alert runs"
  ON alert_runs FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM alerts
      WHERE alerts.id = alert_runs.alert_id
      AND alerts.user_id = auth.uid()
    )
  );
