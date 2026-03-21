-- DEBT-DB-004: Document pipeline_items.search_id type mismatch
-- search_id is TEXT while search_sessions.id is UUID.
-- This is INTENTIONAL — pipeline items can originate from:
--   1. Normal search sessions (UUID from search_sessions.search_id)
--   2. Manual additions via UI (no search session)
--   3. Alert-triggered discoveries (alert run ID)
--   4. External imports (arbitrary string IDs)
--
-- A UUID FK constraint would break cases 2-4. TEXT with max_length=100
-- (enforced in Pydantic schema) is the correct choice.
--
-- Reference: backend/schemas.py PipelineItemCreate.search_id
-- Reference: backend/routes/pipeline.py line ~195

COMMENT ON COLUMN public.pipeline_items.search_id IS
  'Traceability to search origin. TEXT (not UUID FK) intentionally: '
  'accepts UUIDs from search_sessions, alert run IDs, or NULL for manual adds. '
  'Max 100 chars enforced at API layer (Pydantic). DEBT-DB-004 reviewed 2026-03-21.';
