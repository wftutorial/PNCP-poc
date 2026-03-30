-- Phase 1 Track 1A: Database governance fixes
-- DEBT-DB-002: JSONB size constraint on ingestion_runs.metadata
-- DEBT-DB-NEW-001: Fix incorrect COMMENT on pncp_raw_bids.is_active
-- DEBT-DB-007: SKIPPED — already resolved in 20260308300000_debt009_rls_standardize_remaining.sql

-- ============================================================================
-- DEBT-DB-002: ingestion_runs.metadata — Worker config/version data, typically < 5KB
-- Last remaining JSONB column without size governance.
-- Uses NOT VALID + VALIDATE pattern for zero-downtime on existing data.
-- ============================================================================
ALTER TABLE public.ingestion_runs
  ADD CONSTRAINT chk_ingestion_runs_metadata_size
  CHECK (pg_column_size(metadata) < 524288) NOT VALID;

ALTER TABLE public.ingestion_runs
  VALIDATE CONSTRAINT chk_ingestion_runs_metadata_size;

COMMENT ON CONSTRAINT chk_ingestion_runs_metadata_size ON public.ingestion_runs IS
  'DEBT-DB-002: JSONB size governance — max 512KB per value. Prevents unbounded growth.';

-- ============================================================================
-- DEBT-DB-NEW-001: Fix incorrect COMMENT on pncp_raw_bids.is_active
-- Old comment says "soft delete for audit trail" but purge job actually does
-- hard DELETE (see backend/ingestion/loader.py purge_old_bids).
-- ============================================================================
COMMENT ON COLUMN public.pncp_raw_bids.is_active IS
  'Flag de atividade. FALSE = marcado para purge. Purge job executa hard delete (DELETE) periodicamente.';

NOTIFY pgrst, 'reload schema';
