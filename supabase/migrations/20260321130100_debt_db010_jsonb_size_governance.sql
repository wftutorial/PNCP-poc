-- DEBT-DB-010: Add size governance to JSONB columns without constraints
-- Uses NOT VALID + VALIDATE pattern for zero-downtime on existing data.
-- Limit: 512KB (524288 bytes) per JSONB value — generous for all use cases.
-- Columns already constrained (search_results_cache.results, search_results_store.results)
-- are excluded since they already have 2MB octet_length checks.

-- ============================================================================
-- profiles.context_data — Onboarding wizard data, typically < 5KB
-- ============================================================================
ALTER TABLE public.profiles
  ADD CONSTRAINT chk_profiles_context_data_size
  CHECK (pg_column_size(context_data) < 524288) NOT VALID;

ALTER TABLE public.profiles
  VALIDATE CONSTRAINT chk_profiles_context_data_size;

-- ============================================================================
-- plan_features.metadata — Small config objects, typically < 1KB
-- ============================================================================
ALTER TABLE public.plan_features
  ADD CONSTRAINT chk_plan_features_metadata_size
  CHECK (pg_column_size(metadata) < 524288) NOT VALID;

ALTER TABLE public.plan_features
  VALIDATE CONSTRAINT chk_plan_features_metadata_size;

-- ============================================================================
-- user_subscriptions.annual_benefits — Small config, typically < 1KB
-- ============================================================================
ALTER TABLE public.user_subscriptions
  ADD CONSTRAINT chk_user_subscriptions_annual_benefits_size
  CHECK (pg_column_size(annual_benefits) < 524288) NOT VALID;

ALTER TABLE public.user_subscriptions
  VALIDATE CONSTRAINT chk_user_subscriptions_annual_benefits_size;

-- ============================================================================
-- search_state_transitions.details — Audit details, typically < 10KB
-- ============================================================================
ALTER TABLE public.search_state_transitions
  ADD CONSTRAINT chk_search_state_transitions_details_size
  CHECK (pg_column_size(details) < 524288) NOT VALID;

ALTER TABLE public.search_state_transitions
  VALIDATE CONSTRAINT chk_search_state_transitions_details_size;

-- ============================================================================
-- search_results_cache.search_params — Query params, typically < 5KB
-- ============================================================================
ALTER TABLE public.search_results_cache
  ADD CONSTRAINT chk_search_results_cache_search_params_size
  CHECK (pg_column_size(search_params) < 524288) NOT VALID;

ALTER TABLE public.search_results_cache
  VALIDATE CONSTRAINT chk_search_results_cache_search_params_size;

-- ============================================================================
-- search_results_cache.sources_json — Array of source names, typically < 1KB
-- ============================================================================
ALTER TABLE public.search_results_cache
  ADD CONSTRAINT chk_search_results_cache_sources_json_size
  CHECK (pg_column_size(sources_json) < 524288) NOT VALID;

ALTER TABLE public.search_results_cache
  VALIDATE CONSTRAINT chk_search_results_cache_sources_json_size;

-- ============================================================================
-- search_results_cache.coverage — Coverage metadata, typically < 5KB
-- ============================================================================
ALTER TABLE public.search_results_cache
  ADD CONSTRAINT chk_search_results_cache_coverage_size
  CHECK (pg_column_size(coverage) < 524288) NOT VALID;

ALTER TABLE public.search_results_cache
  VALIDATE CONSTRAINT chk_search_results_cache_coverage_size;

-- ============================================================================
-- stripe_webhook_events.payload — Stripe event payloads, typically < 50KB
-- ============================================================================
ALTER TABLE public.stripe_webhook_events
  ADD CONSTRAINT chk_stripe_webhook_events_payload_size
  CHECK (pg_column_size(payload) < 524288) NOT VALID;

ALTER TABLE public.stripe_webhook_events
  VALIDATE CONSTRAINT chk_stripe_webhook_events_payload_size;

-- ============================================================================
-- alerts.filters — User alert filter config, typically < 5KB
-- ============================================================================
ALTER TABLE public.alerts
  ADD CONSTRAINT chk_alerts_filters_size
  CHECK (pg_column_size(filters) < 524288) NOT VALID;

ALTER TABLE public.alerts
  VALIDATE CONSTRAINT chk_alerts_filters_size;

-- ============================================================================
-- google_sheets_exports.search_params — Query params snapshot, typically < 5KB
-- ============================================================================
ALTER TABLE public.google_sheets_exports
  ADD CONSTRAINT chk_google_sheets_exports_search_params_size
  CHECK (pg_column_size(search_params) < 524288) NOT VALID;

ALTER TABLE public.google_sheets_exports
  VALIDATE CONSTRAINT chk_google_sheets_exports_search_params_size;

-- ============================================================================
-- audit_events.details — Audit detail JSON, typically < 10KB
-- ============================================================================
ALTER TABLE public.audit_events
  ADD CONSTRAINT chk_audit_events_details_size
  CHECK (pg_column_size(details) < 524288) NOT VALID;

ALTER TABLE public.audit_events
  VALIDATE CONSTRAINT chk_audit_events_details_size;

-- ============================================================================
-- reconciliation_log.details — Reconciliation details array, typically < 50KB
-- ============================================================================
ALTER TABLE public.reconciliation_log
  ADD CONSTRAINT chk_reconciliation_log_details_size
  CHECK (pg_column_size(details) < 524288) NOT VALID;

ALTER TABLE public.reconciliation_log
  VALIDATE CONSTRAINT chk_reconciliation_log_details_size;

-- ============================================================================
-- health_checks.sources_json + components_json — Status snapshots, typically < 5KB
-- ============================================================================
ALTER TABLE public.health_checks
  ADD CONSTRAINT chk_health_checks_sources_json_size
  CHECK (pg_column_size(sources_json) < 524288) NOT VALID;

ALTER TABLE public.health_checks
  VALIDATE CONSTRAINT chk_health_checks_sources_json_size;

ALTER TABLE public.health_checks
  ADD CONSTRAINT chk_health_checks_components_json_size
  CHECK (pg_column_size(components_json) < 524288) NOT VALID;

ALTER TABLE public.health_checks
  VALIDATE CONSTRAINT chk_health_checks_components_json_size;

-- ============================================================================
-- Summary comment
-- ============================================================================
COMMENT ON CONSTRAINT chk_profiles_context_data_size ON public.profiles IS
  'DEBT-DB-010: JSONB size governance — max 512KB per value. Prevents unbounded growth.';
