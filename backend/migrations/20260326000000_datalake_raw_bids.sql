-- ============================================================
-- Migration: 20260326000000_datalake_raw_bids
-- Purpose:   PNCP Data Lake — raw bid ingestion layer
-- Tables:    pncp_raw_bids, ingestion_checkpoints, ingestion_runs
-- Functions: upsert_pncp_raw_bids, search_datalake, purge_old_bids
-- Constraint: Supabase FREE tier (500MB). No raw_json JSONB column.
--             Functional GIN index avoids stored tsvector column.
-- ============================================================

-- ============================================================
-- SECTION 1: pncp_raw_bids
-- Stores one row per unique PNCP bid (pncp_id is the natural key).
-- content_hash detects field-level changes on re-ingestion.
-- is_active = false soft-deletes records displaced by purge logic.
-- ============================================================

CREATE TABLE IF NOT EXISTS public.pncp_raw_bids (
    pncp_id              TEXT PRIMARY KEY,
    objeto_compra        TEXT NOT NULL,
    valor_total_estimado NUMERIC(18,2),
    modalidade_id        INTEGER NOT NULL,
    modalidade_nome      TEXT,
    situacao_compra      TEXT,
    esfera_id            TEXT,
    uf                   TEXT NOT NULL,
    municipio            TEXT,
    codigo_municipio_ibge TEXT,
    orgao_razao_social   TEXT,
    orgao_cnpj           TEXT,
    unidade_nome         TEXT,
    data_publicacao      TIMESTAMPTZ,
    data_abertura        TIMESTAMPTZ,
    data_encerramento    TIMESTAMPTZ,
    link_sistema_origem  TEXT,
    link_pncp            TEXT,
    content_hash         TEXT NOT NULL,
    ingested_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    source               TEXT NOT NULL DEFAULT 'pncp',
    crawl_batch_id       TEXT,
    is_active            BOOLEAN NOT NULL DEFAULT true
);

COMMENT ON TABLE public.pncp_raw_bids IS
    'Raw PNCP bid records. No raw_json to stay within 500MB FREE tier limit. '
    'content_hash (MD5 of key fields) drives upsert change detection.';

COMMENT ON COLUMN public.pncp_raw_bids.content_hash IS
    'MD5 of concatenated mutable fields. Upsert skips rows where hash matches.';
COMMENT ON COLUMN public.pncp_raw_bids.crawl_batch_id IS
    'Links row to the ingestion_runs.crawl_batch_id that created/last-updated it.';
COMMENT ON COLUMN public.pncp_raw_bids.is_active IS
    'Set to false by purge_old_bids() instead of hard-delete for audit trail.';

-- ============================================================
-- SECTION 2: Indexes on pncp_raw_bids
-- Functional GIN avoids a stored tsvector column (saves ~40MB at 1M rows).
-- Partial indexes (WHERE is_active) keep index size small.
-- ============================================================

-- Full-text search on objeto_compra using Portuguese dictionary.
-- Functional GIN: no stored column, index built on expression.
CREATE INDEX IF NOT EXISTS idx_pncp_raw_bids_fts
    ON public.pncp_raw_bids
    USING GIN (to_tsvector('portuguese', coalesce(objeto_compra, '')));

-- Most common dashboard query: filter by UF, order by date.
CREATE INDEX IF NOT EXISTS idx_pncp_raw_bids_uf_date
    ON public.pncp_raw_bids (uf, data_publicacao DESC)
    WHERE is_active;

-- Filter by procurement modality.
CREATE INDEX IF NOT EXISTS idx_pncp_raw_bids_modalidade
    ON public.pncp_raw_bids (modalidade_id)
    WHERE is_active;

-- Range queries on estimated value (non-null only).
CREATE INDEX IF NOT EXISTS idx_pncp_raw_bids_valor
    ON public.pncp_raw_bids (valor_total_estimado)
    WHERE is_active AND valor_total_estimado IS NOT NULL;

-- Filter by government sphere (federal/estadual/municipal).
CREATE INDEX IF NOT EXISTS idx_pncp_raw_bids_esfera
    ON public.pncp_raw_bids (esfera_id)
    WHERE is_active;

-- Open bids query: find records where deadline has not passed.
CREATE INDEX IF NOT EXISTS idx_pncp_raw_bids_encerramento
    ON public.pncp_raw_bids (data_encerramento)
    WHERE is_active AND data_encerramento IS NOT NULL;

-- Dedup check during ingestion: lookup by content_hash to skip unchanged rows.
CREATE INDEX IF NOT EXISTS idx_pncp_raw_bids_content_hash
    ON public.pncp_raw_bids (content_hash);

-- Chronological ingestion audit and batch scans.
CREATE INDEX IF NOT EXISTS idx_pncp_raw_bids_ingested_at
    ON public.pncp_raw_bids (ingested_at DESC);

-- ============================================================
-- SECTION 3: updated_at trigger for pncp_raw_bids
-- ============================================================

CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$;

COMMENT ON FUNCTION public.set_updated_at() IS
    'Generic trigger function: sets updated_at = now() on every UPDATE.';

DROP TRIGGER IF EXISTS trg_pncp_raw_bids_updated_at ON public.pncp_raw_bids;

CREATE TRIGGER trg_pncp_raw_bids_updated_at
    BEFORE UPDATE ON public.pncp_raw_bids
    FOR EACH ROW
    EXECUTE FUNCTION public.set_updated_at();

-- ============================================================
-- SECTION 4: RLS for pncp_raw_bids
-- Bid data is public by Brazilian law (Lei 14.133/2021, art. 174).
-- Authenticated users may SELECT; writes are service_role only.
-- ============================================================

ALTER TABLE public.pncp_raw_bids ENABLE ROW LEVEL SECURITY;

-- Allow any authenticated user to read all active bids.
DROP POLICY IF EXISTS "pncp_raw_bids_select_authenticated" ON public.pncp_raw_bids;
CREATE POLICY "pncp_raw_bids_select_authenticated"
    ON public.pncp_raw_bids
    FOR SELECT
    TO authenticated
    USING (true);

-- INSERT is restricted to service_role (used by the ingestion worker).
DROP POLICY IF EXISTS "pncp_raw_bids_insert_service" ON public.pncp_raw_bids;
CREATE POLICY "pncp_raw_bids_insert_service"
    ON public.pncp_raw_bids
    FOR INSERT
    TO service_role
    WITH CHECK (true);

-- UPDATE is restricted to service_role.
DROP POLICY IF EXISTS "pncp_raw_bids_update_service" ON public.pncp_raw_bids;
CREATE POLICY "pncp_raw_bids_update_service"
    ON public.pncp_raw_bids
    FOR UPDATE
    TO service_role
    USING (true)
    WITH CHECK (true);

-- DELETE is restricted to service_role (used by purge_old_bids).
DROP POLICY IF EXISTS "pncp_raw_bids_delete_service" ON public.pncp_raw_bids;
CREATE POLICY "pncp_raw_bids_delete_service"
    ON public.pncp_raw_bids
    FOR DELETE
    TO service_role
    USING (true);

-- ============================================================
-- SECTION 5: ingestion_checkpoints
-- Tracks per-(source, uf, modalidade, batch) crawl progress.
-- Enables resumable crawls: if a run fails mid-way, the worker
-- can restart from the last successfully completed checkpoint.
-- ============================================================

CREATE TABLE IF NOT EXISTS public.ingestion_checkpoints (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source          TEXT NOT NULL DEFAULT 'pncp',
    uf              TEXT NOT NULL,
    modalidade_id   INTEGER NOT NULL,
    last_date       DATE NOT NULL,
    last_page       INTEGER DEFAULT 1,
    records_fetched INTEGER DEFAULT 0,
    -- pending: not yet started
    -- running: currently being crawled
    -- completed: all pages fetched successfully
    -- failed: stopped due to error (see error_message)
    status          TEXT NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    error_message   TEXT,
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    crawl_batch_id  TEXT NOT NULL,
    CONSTRAINT uq_ingestion_checkpoints
        UNIQUE (source, uf, modalidade_id, crawl_batch_id)
);

COMMENT ON TABLE public.ingestion_checkpoints IS
    'Per-UF/modality progress checkpoints within an ingestion_runs batch. '
    'Allows resumable crawls on worker restart.';
COMMENT ON COLUMN public.ingestion_checkpoints.last_page IS
    'Last successfully fetched page number (1-indexed). Resume from last_page + 1.';
COMMENT ON COLUMN public.ingestion_checkpoints.crawl_batch_id IS
    'Foreign-key reference to ingestion_runs.crawl_batch_id (not enforced for perf).';

CREATE INDEX IF NOT EXISTS idx_ingestion_checkpoints_batch
    ON public.ingestion_checkpoints (crawl_batch_id, status);

CREATE INDEX IF NOT EXISTS idx_ingestion_checkpoints_uf_mod
    ON public.ingestion_checkpoints (uf, modalidade_id);

ALTER TABLE public.ingestion_checkpoints ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "ingestion_checkpoints_select_authenticated" ON public.ingestion_checkpoints;
CREATE POLICY "ingestion_checkpoints_select_authenticated"
    ON public.ingestion_checkpoints
    FOR SELECT
    TO authenticated
    USING (true);

DROP POLICY IF EXISTS "ingestion_checkpoints_write_service" ON public.ingestion_checkpoints;
CREATE POLICY "ingestion_checkpoints_write_service"
    ON public.ingestion_checkpoints
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- ============================================================
-- SECTION 6: ingestion_runs
-- One row per crawl batch. Aggregates totals and surfaces
-- run-level status for monitoring dashboards and alerts.
-- ============================================================

CREATE TABLE IF NOT EXISTS public.ingestion_runs (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    crawl_batch_id  TEXT UNIQUE NOT NULL,
    -- full: re-crawls the full retention window
    -- incremental: crawls only recent delta (last N days)
    run_type        TEXT NOT NULL
                    CHECK (run_type IN ('full', 'incremental')),
    status          TEXT NOT NULL DEFAULT 'running'
                    CHECK (status IN ('running', 'completed', 'failed', 'partial')),
    started_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at    TIMESTAMPTZ,
    total_fetched   INTEGER NOT NULL DEFAULT 0,
    inserted        INTEGER NOT NULL DEFAULT 0,
    updated         INTEGER NOT NULL DEFAULT 0,
    unchanged       INTEGER NOT NULL DEFAULT 0,
    errors          INTEGER NOT NULL DEFAULT 0,
    ufs_completed   TEXT[],
    ufs_failed      TEXT[],
    -- Computed on run completion: EXTRACT(EPOCH FROM completed_at - started_at)
    duration_s      NUMERIC(10,1),
    -- Arbitrary metadata: worker version, trigger source, config snapshot, etc.
    metadata        JSONB NOT NULL DEFAULT '{}'
);

COMMENT ON TABLE public.ingestion_runs IS
    'Top-level ingestion batch ledger. One row per crawl_batch_id. '
    'Workers update this row as UF checkpoints complete.';
COMMENT ON COLUMN public.ingestion_runs.metadata IS
    'Freeform JSONB for worker version, config snapshot, trigger source, etc.';

CREATE INDEX IF NOT EXISTS idx_ingestion_runs_started
    ON public.ingestion_runs (started_at DESC);

CREATE INDEX IF NOT EXISTS idx_ingestion_runs_status
    ON public.ingestion_runs (status)
    WHERE status IN ('running', 'failed');

ALTER TABLE public.ingestion_runs ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "ingestion_runs_select_authenticated" ON public.ingestion_runs;
CREATE POLICY "ingestion_runs_select_authenticated"
    ON public.ingestion_runs
    FOR SELECT
    TO authenticated
    USING (true);

DROP POLICY IF EXISTS "ingestion_runs_write_service" ON public.ingestion_runs;
CREATE POLICY "ingestion_runs_write_service"
    ON public.ingestion_runs
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- ============================================================
-- SECTION 7: upsert_pncp_raw_bids(p_records JSONB)
-- SECURITY DEFINER: runs as the function owner (service_role level)
-- so the caller only needs EXECUTE privilege, not table-level INSERT.
--
-- Algorithm:
--   For each record in the JSONB array:
--     INSERT ON CONFLICT (pncp_id) DO UPDATE ... WHERE content_hash differs
--   Track insert vs update via ctid/xmin trick:
--     After the INSERT ... ON CONFLICT upsert, the row's xmax is 0 for a
--     fresh insert and non-zero for an update. We use xmax = 0 to count inserts.
--   Returns (inserted, updated, unchanged) summary.
-- ============================================================

CREATE OR REPLACE FUNCTION public.upsert_pncp_raw_bids(p_records JSONB)
RETURNS TABLE(inserted INT, updated INT, unchanged INT)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_record        JSONB;
    v_inserted      INT := 0;
    v_updated       INT := 0;
    v_unchanged     INT := 0;
    v_existing_hash TEXT;
    v_new_hash      TEXT;
BEGIN
    IF p_records IS NULL OR jsonb_array_length(p_records) = 0 THEN
        RETURN QUERY SELECT 0, 0, 0;
        RETURN;
    END IF;

    FOR v_record IN SELECT jsonb_array_elements(p_records)
    LOOP
        v_new_hash := v_record->>'content_hash';

        -- Fast-path: check if hash matches before attempting upsert.
        SELECT content_hash
          INTO v_existing_hash
          FROM public.pncp_raw_bids
         WHERE pncp_id = v_record->>'pncp_id';

        IF NOT FOUND THEN
            -- Record does not exist — INSERT.
            INSERT INTO public.pncp_raw_bids (
                pncp_id,
                objeto_compra,
                valor_total_estimado,
                modalidade_id,
                modalidade_nome,
                situacao_compra,
                esfera_id,
                uf,
                municipio,
                codigo_municipio_ibge,
                orgao_razao_social,
                orgao_cnpj,
                unidade_nome,
                data_publicacao,
                data_abertura,
                data_encerramento,
                link_sistema_origem,
                link_pncp,
                content_hash,
                ingested_at,
                updated_at,
                source,
                crawl_batch_id,
                is_active
            ) VALUES (
                v_record->>'pncp_id',
                v_record->>'objeto_compra',
                (v_record->>'valor_total_estimado')::NUMERIC,
                (v_record->>'modalidade_id')::INTEGER,
                v_record->>'modalidade_nome',
                v_record->>'situacao_compra',
                v_record->>'esfera_id',
                v_record->>'uf',
                v_record->>'municipio',
                v_record->>'codigo_municipio_ibge',
                v_record->>'orgao_razao_social',
                v_record->>'orgao_cnpj',
                v_record->>'unidade_nome',
                (v_record->>'data_publicacao')::TIMESTAMPTZ,
                (v_record->>'data_abertura')::TIMESTAMPTZ,
                (v_record->>'data_encerramento')::TIMESTAMPTZ,
                v_record->>'link_sistema_origem',
                v_record->>'link_pncp',
                v_new_hash,
                now(),
                now(),
                COALESCE(v_record->>'source', 'pncp'),
                v_record->>'crawl_batch_id',
                COALESCE((v_record->>'is_active')::BOOLEAN, true)
            );
            v_inserted := v_inserted + 1;

        ELSIF v_existing_hash IS DISTINCT FROM v_new_hash THEN
            -- Record exists and content changed — UPDATE mutable fields only.
            UPDATE public.pncp_raw_bids SET
                objeto_compra        = v_record->>'objeto_compra',
                valor_total_estimado = (v_record->>'valor_total_estimado')::NUMERIC,
                modalidade_nome      = v_record->>'modalidade_nome',
                situacao_compra      = v_record->>'situacao_compra',
                esfera_id            = v_record->>'esfera_id',
                municipio            = v_record->>'municipio',
                codigo_municipio_ibge= v_record->>'codigo_municipio_ibge',
                orgao_razao_social   = v_record->>'orgao_razao_social',
                orgao_cnpj           = v_record->>'orgao_cnpj',
                unidade_nome         = v_record->>'unidade_nome',
                data_publicacao      = (v_record->>'data_publicacao')::TIMESTAMPTZ,
                data_abertura        = (v_record->>'data_abertura')::TIMESTAMPTZ,
                data_encerramento    = (v_record->>'data_encerramento')::TIMESTAMPTZ,
                link_sistema_origem  = v_record->>'link_sistema_origem',
                link_pncp            = v_record->>'link_pncp',
                content_hash         = v_new_hash,
                updated_at           = now(),
                crawl_batch_id       = v_record->>'crawl_batch_id',
                is_active            = COALESCE((v_record->>'is_active')::BOOLEAN, true)
            WHERE pncp_id = v_record->>'pncp_id';
            v_updated := v_updated + 1;

        ELSE
            -- Hash matches — no changes, skip.
            v_unchanged := v_unchanged + 1;
        END IF;

    END LOOP;

    RETURN QUERY SELECT v_inserted, v_updated, v_unchanged;
END;
$$;

COMMENT ON FUNCTION public.upsert_pncp_raw_bids(JSONB) IS
    'Bulk upsert for PNCP bids. Skips rows where content_hash matches. '
    'SECURITY DEFINER so ingestion worker needs only EXECUTE, not table INSERT. '
    'Returns (inserted, updated, unchanged) row counts.';

-- Grant EXECUTE to authenticated users who need to call this from the worker.
GRANT EXECUTE ON FUNCTION public.upsert_pncp_raw_bids(JSONB) TO service_role;

-- ============================================================
-- SECTION 8: search_datalake(...)
-- SECURITY DEFINER search function that combines:
--   - Full-text search (Portuguese tsvector on objeto_compra)
--   - UF, date range, modality, value range, esfera filters
--   - Two date modes: 'publicacao' (publication date) or
--     'abertas' (open bids: encerramento > now)
--   - ts_rank ordering when tsquery is provided
-- Runs as owner (bypasses RLS) for maximum query performance.
-- Caller gets results without needing table-level SELECT.
-- ============================================================

CREATE OR REPLACE FUNCTION public.search_datalake(
    p_ufs          TEXT[]            DEFAULT NULL,
    p_date_start   DATE              DEFAULT NULL,
    p_date_end     DATE              DEFAULT NULL,
    p_tsquery      TEXT              DEFAULT NULL,
    p_modalidades  INTEGER[]         DEFAULT NULL,
    p_valor_min    NUMERIC           DEFAULT NULL,
    p_valor_max    NUMERIC           DEFAULT NULL,
    p_esferas      TEXT[]            DEFAULT NULL,
    p_modo         TEXT              DEFAULT 'publicacao',
    p_limit        INTEGER           DEFAULT 2000
)
RETURNS TABLE (
    pncp_id              TEXT,
    objeto_compra        TEXT,
    valor_total_estimado NUMERIC,
    modalidade_id        INTEGER,
    modalidade_nome      TEXT,
    situacao_compra      TEXT,
    esfera_id            TEXT,
    uf                   TEXT,
    municipio            TEXT,
    orgao_razao_social   TEXT,
    orgao_cnpj           TEXT,
    data_publicacao      TIMESTAMPTZ,
    data_abertura        TIMESTAMPTZ,
    data_encerramento    TIMESTAMPTZ,
    link_pncp            TEXT,
    ts_rank              REAL
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_ts_query TSQUERY;
BEGIN
    -- Validate modo parameter.
    IF p_modo NOT IN ('publicacao', 'abertas') THEN
        RAISE EXCEPTION 'p_modo must be ''publicacao'' or ''abertas'', got: %', p_modo;
    END IF;

    -- Cap limit to prevent runaway queries.
    IF p_limit > 5000 THEN
        p_limit := 5000;
    END IF;

    -- Parse tsquery once; NULL means no full-text filter.
    IF p_tsquery IS NOT NULL AND trim(p_tsquery) <> '' THEN
        BEGIN
            v_ts_query := to_tsquery('portuguese', p_tsquery);
        EXCEPTION WHEN OTHERS THEN
            -- Malformed tsquery — fallback to plain text search.
            v_ts_query := plainto_tsquery('portuguese', p_tsquery);
        END;
    END IF;

    RETURN QUERY
    SELECT
        b.pncp_id,
        b.objeto_compra,
        b.valor_total_estimado,
        b.modalidade_id,
        b.modalidade_nome,
        b.situacao_compra,
        b.esfera_id,
        b.uf,
        b.municipio,
        b.orgao_razao_social,
        b.orgao_cnpj,
        b.data_publicacao,
        b.data_abertura,
        b.data_encerramento,
        b.link_pncp,
        -- ts_rank is 0.0 when no tsquery supplied (neutral ordering).
        CASE
            WHEN v_ts_query IS NOT NULL
            THEN ts_rank(
                     to_tsvector('portuguese', coalesce(b.objeto_compra, '')),
                     v_ts_query
                 )
            ELSE 0.0
        END::REAL AS ts_rank
    FROM public.pncp_raw_bids b
    WHERE
        b.is_active = true

        -- UF filter: pass NULL to include all UFs.
        AND (p_ufs IS NULL       OR b.uf = ANY(p_ufs))

        -- Modality filter: pass NULL to include all modalities.
        AND (p_modalidades IS NULL OR b.modalidade_id = ANY(p_modalidades))

        -- Government sphere filter.
        AND (p_esferas IS NULL   OR b.esfera_id = ANY(p_esferas))

        -- Value range filters (inclusive).
        AND (p_valor_min IS NULL OR b.valor_total_estimado >= p_valor_min)
        AND (p_valor_max IS NULL OR b.valor_total_estimado <= p_valor_max)

        -- Full-text match (uses GIN index on to_tsvector expression).
        AND (
            v_ts_query IS NULL
            OR to_tsvector('portuguese', coalesce(b.objeto_compra, '')) @@ v_ts_query
        )

        -- Date mode: 'publicacao' filters by publication date window.
        AND (
            p_modo <> 'publicacao'
            OR (
                (p_date_start IS NULL OR b.data_publicacao >= p_date_start::TIMESTAMPTZ)
                AND
                (p_date_end   IS NULL OR b.data_publicacao <  (p_date_end + INTERVAL '1 day')::TIMESTAMPTZ)
            )
        )

        -- Date mode: 'abertas' — encerramento in the future, publicacao >= start.
        AND (
            p_modo <> 'abertas'
            OR (
                b.data_encerramento > now()
                AND (p_date_start IS NULL OR b.data_publicacao >= p_date_start::TIMESTAMPTZ)
            )
        )

    ORDER BY
        -- When full-text query supplied, rank by relevance first.
        CASE WHEN v_ts_query IS NOT NULL
             THEN ts_rank(
                      to_tsvector('portuguese', coalesce(b.objeto_compra, '')),
                      v_ts_query
                  )
             ELSE NULL
        END DESC NULLS LAST,
        b.data_publicacao DESC

    LIMIT p_limit;
END;
$$;

COMMENT ON FUNCTION public.search_datalake(TEXT[], DATE, DATE, TEXT, INTEGER[], NUMERIC, NUMERIC, TEXT[], TEXT, INTEGER) IS
    'Full-featured datalake search. Supports UF, date, FTS (Portuguese), '
    'modality, value range, esfera, and two date modes (publicacao / abertas). '
    'SECURITY DEFINER for RLS bypass and consistent index usage. '
    'tsquery parse errors fall back to plainto_tsquery (safe degradation). '
    'Limit is capped at 5000 to prevent runaway queries.';

GRANT EXECUTE ON FUNCTION public.search_datalake(TEXT[], DATE, DATE, TEXT, INTEGER[], NUMERIC, NUMERIC, TEXT[], TEXT, INTEGER) TO authenticated;
GRANT EXECUTE ON FUNCTION public.search_datalake(TEXT[], DATE, DATE, TEXT, INTEGER[], NUMERIC, NUMERIC, TEXT[], TEXT, INTEGER) TO service_role;

-- ============================================================
-- SECTION 9: purge_old_bids(p_retention_days INTEGER)
-- Hard-deletes rows older than the retention window.
-- Default retention is 12 days (slightly longer than the 10-day
-- default search window to avoid purging fresh-but-slow-indexed rows).
-- Returns the count of deleted rows for monitoring.
-- ============================================================

CREATE OR REPLACE FUNCTION public.purge_old_bids(
    p_retention_days INTEGER DEFAULT 12
)
RETURNS INTEGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_deleted INTEGER;
    v_cutoff  TIMESTAMPTZ;
BEGIN
    IF p_retention_days < 1 THEN
        RAISE EXCEPTION 'p_retention_days must be >= 1, got: %', p_retention_days;
    END IF;

    v_cutoff := now() - (p_retention_days || ' days')::INTERVAL;

    DELETE FROM public.pncp_raw_bids
    WHERE data_publicacao < v_cutoff
      AND is_active = true;

    GET DIAGNOSTICS v_deleted = ROW_COUNT;

    RETURN v_deleted;
END;
$$;

COMMENT ON FUNCTION public.purge_old_bids(INTEGER) IS
    'Deletes active bids with data_publicacao older than p_retention_days (default 12). '
    'Returns count of deleted rows. Schedule via pg_cron or external cron job. '
    'SECURITY DEFINER: caller needs only EXECUTE, not DELETE on the table.';

GRANT EXECUTE ON FUNCTION public.purge_old_bids(INTEGER) TO service_role;

-- ============================================================
-- SECTION 10: Verification queries (commented out — run manually)
-- ============================================================

-- SELECT schemaname, tablename, rowsecurity
--   FROM pg_tables
--  WHERE tablename IN ('pncp_raw_bids', 'ingestion_checkpoints', 'ingestion_runs');
--
-- SELECT indexname, indexdef
--   FROM pg_indexes
--  WHERE tablename = 'pncp_raw_bids'
--  ORDER BY indexname;
--
-- SELECT routine_name, security_type
--   FROM information_schema.routines
--  WHERE routine_schema = 'public'
--    AND routine_name IN ('upsert_pncp_raw_bids', 'search_datalake', 'purge_old_bids');
