-- rollback_20260331_pncp_raw_bids_indexes.sql
-- Tabela: pncp_raw_bids
-- Propósito: Reverter indexes, constraints e mudanças adicionados nas últimas migrations
--
-- Migrations revertidas (cronológica decrescente):
--   20260330120000_debt_phase1_db_governance.sql (DEBT-DB-NEW-001)
--     → Reverter COMMENT em pncp_raw_bids.is_active
--       (restaurar comentário original da migration 20260326000000)
--   20260330120000_debt_phase1_db_governance.sql (DEBT-DB-002 — ingestion_runs)
--     → DROP CONSTRAINT chk_ingestion_runs_metadata_size
--       (nota: esta constraint é em ingestion_runs, tabela do mesmo sistema)
--   20260326000000_datalake_raw_bids.sql
--     → DROP todos os indexes criados (rollback completo da tabela seria
--       muito destrutivo — reverter apenas indexes recentes)
--
-- NOTA IMPORTANTE: A tabela pncp_raw_bids foi criada integralmente em
-- 20260326000000. Um rollback completo (DROP TABLE) destruiria 40K+ rows
-- de dados de ingestão. Este script reverte apenas mudanças incrementais
-- pós-criação:
--   - O comentário corrigido em is_active (DEBT-DB-NEW-001)
--   - A constraint de tamanho em ingestion_runs.metadata (DEBT-DB-002)
--
-- Para reverter a tabela completamente (emergência extrema), veja
-- a seção ROLLBACK COMPLETO comentada ao final.
--
-- INSTRUÇÕES DE USO:
-- 1. Verificar que PITR está disponível antes de executar
-- 2. Parar o worker de ingestão antes de executar
-- 3. Executar em staging com dados sintéticos primeiro
-- 4. NUNCA executar em produção sem backup confirmado
-- 5. Após rollback, reiniciar ingestão com cuidado (dedup via content_hash)
--
-- Última modificação: 2026-03-31

-- ============================================================
-- PRÉ-ROLLBACK: Verificar estado esperado
-- ============================================================

DO $$
BEGIN
    ASSERT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'pncp_raw_bids'
    ), 'ERRO: Tabela pncp_raw_bids não encontrada. Abortando rollback.';

    RAISE NOTICE 'PRÉ-VERIFICAÇÃO OK: Tabela pncp_raw_bids encontrada';

    ASSERT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'ingestion_runs'
    ), 'ERRO: Tabela ingestion_runs não encontrada. Abortando rollback.';

    RAISE NOTICE 'PRÉ-VERIFICAÇÃO OK: Tabela ingestion_runs encontrada';

    -- Verificar estado do constraint
    IF EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'public.ingestion_runs'::regclass
          AND conname = 'chk_ingestion_runs_metadata_size'
    ) THEN
        RAISE NOTICE 'PRÉ-VERIFICAÇÃO: chk_ingestion_runs_metadata_size EXISTS — será removida';
    ELSE
        RAISE NOTICE 'PRÉ-AVISO: chk_ingestion_runs_metadata_size NÃO existe (já rollbacked?)';
    END IF;

    -- Verificar indexes existentes
    IF EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE schemaname = 'public' AND tablename = 'pncp_raw_bids'
          AND indexname = 'idx_pncp_raw_bids_fts'
    ) THEN
        RAISE NOTICE 'PRÉ-VERIFICAÇÃO: Indexes principais de pncp_raw_bids existem';
    ELSE
        RAISE WARNING 'PRÉ-AVISO: idx_pncp_raw_bids_fts não encontrado — tabela em estado inesperado';
    END IF;
END $$;

-- ============================================================
-- ROLLBACK: Operação principal
-- ============================================================

BEGIN;

    -- PASSO 1: Reverter DEBT-DB-002 — remover CHECK constraint de metadata em ingestion_runs
    ALTER TABLE public.ingestion_runs
        DROP CONSTRAINT IF EXISTS chk_ingestion_runs_metadata_size;
    RAISE NOTICE 'ROLLBACK: DROP CONSTRAINT chk_ingestion_runs_metadata_size em ingestion_runs (DEBT-DB-002)';

    -- PASSO 2: Reverter DEBT-DB-NEW-001 — restaurar comentário original em is_active
    -- O comentário original (20260326000000) dizia "soft delete for audit trail"
    -- O corrigido (DEBT-DB-NEW-001) dizia "hard delete periodicamente"
    -- Restauramos o original pois é o que estava antes desta migration
    COMMENT ON COLUMN public.pncp_raw_bids.is_active IS
        'Set to false by purge_old_bids() instead of hard-delete for audit trail.';
    RAISE NOTICE 'ROLLBACK: COMMENT em pncp_raw_bids.is_active restaurado para versão original (DEBT-DB-NEW-001 revertido)';

    -- PASSO 3: Nenhum index adicional foi criado após 20260326000000 para pncp_raw_bids
    -- Os indexes abaixo são da migration original e NÃO devem ser removidos
    -- em um rollback incremental:
    --   idx_pncp_raw_bids_fts, idx_pncp_raw_bids_uf_date, idx_pncp_raw_bids_modalidade,
    --   idx_pncp_raw_bids_valor, idx_pncp_raw_bids_esfera, idx_pncp_raw_bids_encerramento,
    --   idx_pncp_raw_bids_content_hash, idx_pncp_raw_bids_ingested_at
    RAISE NOTICE 'ROLLBACK INFO: Indexes originais de pncp_raw_bids mantidos (fazem parte da criação da tabela)';

COMMIT;

-- ============================================================
-- PÓS-ROLLBACK: Verificar estado revertido
-- ============================================================

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'public.ingestion_runs'::regclass
          AND conname = 'chk_ingestion_runs_metadata_size'
    ) THEN
        RAISE WARNING 'PÓS-VERIFICAÇÃO FALHOU: chk_ingestion_runs_metadata_size ainda existe';
    ELSE
        RAISE NOTICE 'PÓS-VERIFICAÇÃO OK: chk_ingestion_runs_metadata_size removido de ingestion_runs';
    END IF;

    -- Verificar que indexes originais ainda existem (sanity check)
    IF EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE schemaname = 'public' AND tablename = 'pncp_raw_bids'
          AND indexname = 'idx_pncp_raw_bids_fts'
    ) THEN
        RAISE NOTICE 'PÓS-VERIFICAÇÃO OK: Indexes originais de pncp_raw_bids preservados';
    ELSE
        RAISE WARNING 'PÓS-VERIFICAÇÃO AVISO: idx_pncp_raw_bids_fts não encontrado após rollback — verificar manualmente';
    END IF;

    RAISE NOTICE 'PÓS-VERIFICAÇÃO: Rollback de pncp_raw_bids/ingestion_runs completado';
END $$;

-- ============================================================
-- ROLLBACK COMPLETO (EMERGÊNCIA EXTREMA — COMENTADO)
-- Descomente APENAS se necessário dropar a tabela por completo.
-- DESTRUTIVO: apaga 40K+ rows de dados de ingestão.
-- Requer re-ingestão completa após execução.
-- ============================================================
/*
BEGIN;
    DROP TABLE IF EXISTS public.pncp_raw_bids CASCADE;
    DROP TABLE IF EXISTS public.ingestion_checkpoints CASCADE;
    DROP TABLE IF EXISTS public.ingestion_runs CASCADE;
    DROP FUNCTION IF EXISTS public.upsert_pncp_raw_bids(JSONB);
    DROP FUNCTION IF EXISTS public.search_datalake(TEXT[], DATE, DATE, TEXT, INTEGER[], NUMERIC, NUMERIC, TEXT[], TEXT, INTEGER);
    DROP FUNCTION IF EXISTS public.purge_old_bids(INTEGER);
    DROP FUNCTION IF EXISTS public.check_pncp_raw_bids_bloat();
    DROP VIEW IF EXISTS public.pncp_raw_bids_bloat_stats;
COMMIT;
*/
