-- TD-002: RLS Policies (C-02) + Trigger Consolidation (H-01)

-- ══════════════════════════════════════════════════════════════════
-- AC1: RLS policies for health_checks (service_role only)
-- RLS already enabled in 20260303200000_enable_rls_health_incidents.sql
-- ══════════════════════════════════════════════════════════════════
CREATE POLICY "service_role_all" ON public.health_checks
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- ══════════════════════════════════════════════════════════════════
-- AC2: RLS policies for incidents (service_role only)
-- ══════════════════════════════════════════════════════════════════
CREATE POLICY "service_role_all" ON public.incidents
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- ══════════════════════════════════════════════════════════════════
-- AC5-AC6: Consolidate duplicate updated_at trigger functions
-- Keep public.update_updated_at() as the single canonical function.
-- Original defined in 001_profiles_and_sessions.sql.
-- ══════════════════════════════════════════════════════════════════

-- Ensure the canonical function exists (idempotent)
CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ── Re-point pipeline_items trigger to canonical function ──
DROP TRIGGER IF EXISTS tr_pipeline_items_updated_at ON public.pipeline_items;
DROP FUNCTION IF EXISTS public.update_pipeline_updated_at();

CREATE TRIGGER tr_pipeline_items_updated_at
  BEFORE UPDATE ON public.pipeline_items
  FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- ── Re-point alert_preferences trigger to canonical function ──
DROP TRIGGER IF EXISTS trigger_alert_preferences_updated_at ON public.alert_preferences;
DROP FUNCTION IF EXISTS public.update_alert_preferences_updated_at();

CREATE TRIGGER trigger_alert_preferences_updated_at
  BEFORE UPDATE ON public.alert_preferences
  FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- ── Re-point alerts trigger to canonical function ──
DROP TRIGGER IF EXISTS trigger_alerts_updated_at ON public.alerts;
DROP FUNCTION IF EXISTS public.update_alerts_updated_at();

CREATE TRIGGER trigger_alerts_updated_at
  BEFORE UPDATE ON public.alerts
  FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
