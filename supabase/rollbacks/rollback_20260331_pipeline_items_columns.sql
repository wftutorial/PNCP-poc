-- rollback_20260331_pipeline_items_columns.sql
-- Tabela: pipeline_items
-- Propósito: Reverter colunas adicionadas nas últimas migrations
--
-- Migrations revertidas (cronológica decrescente):
--   20260321130000_debt_db004_pipeline_search_id_comment.sql
--     → Reverter COMMENT em pipeline_items.search_id
--       (restaurar comentário de DEBT-120 AC5)
--   20260315100000_debt120_db_optimization.sql (AC5)
--     → DROP COLUMN search_id
--     → DROP INDEX idx_pipeline_items_search_id
--   20260308100000_debt001_database_integrity_fixes.sql (DB-038)
--     → DROP INDEX idx_pipeline_items_user_id
--       (criado como correção de índice errado — idx_pipeline_user_id)
--   20260227120002_concurrency_pipeline_version.sql
--     → DROP COLUMN version
--
-- INSTRUÇÕES DE USO:
-- 1. Verificar que PITR está disponível antes de executar
-- 2. Executar em staging com dados sintéticos primeiro
-- 3. Verificar que nenhum item no pipeline usa search_id antes de remover
-- 4. NUNCA executar em produção sem backup confirmado
-- 5. backend/routes/pipeline.py usa search_id — atualizar código antes deste rollback
-- 6. version é usado por otimistic locking (STORY-318) — desativar concurrency
--    check no backend antes de dropar esta coluna
--
-- Última modificação: 2026-03-31

-- ============================================================
-- PRÉ-ROLLBACK: Verificar estado esperado
-- ============================================================

DO $$
DECLARE
    items_with_search_id INTEGER;
BEGIN
    ASSERT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'pipeline_items'
    ), 'ERRO: Tabela pipeline_items não encontrada. Abortando rollback.';

    RAISE NOTICE 'PRÉ-VERIFICAÇÃO OK: Tabela pipeline_items encontrada';

    -- Verificar coluna search_id
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'pipeline_items'
          AND column_name = 'search_id'
    ) THEN
        -- Contar itens que usam search_id (para log informativo)
        SELECT COUNT(*) INTO items_with_search_id
        FROM public.pipeline_items
        WHERE search_id IS NOT NULL;

        RAISE NOTICE 'PRÉ-VERIFICAÇÃO: search_id EXISTS — será removida (% itens têm search_id preenchido)',
                     items_with_search_id;
    ELSE
        RAISE NOTICE 'PRÉ-AVISO: search_id NÃO existe (já rollbacked?)';
    END IF;

    -- Verificar coluna version
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'pipeline_items'
          AND column_name = 'version'
    ) THEN
        RAISE NOTICE 'PRÉ-VERIFICAÇÃO: version EXISTS — será removida';
    ELSE
        RAISE NOTICE 'PRÉ-AVISO: version NÃO existe (já rollbacked?)';
    END IF;
END $$;

-- ============================================================
-- ROLLBACK: Operação principal
-- ============================================================

BEGIN;

    -- PASSO 1: Reverter DEBT-DB-004 comment (restaurar o anterior de DEBT-120)
    -- O DEBT-120 tinha comentário: 'DEBT-120 AC5: Links pipeline item to the search session that discovered it'
    -- O DEBT-DB-004 expandiu para documentar o type mismatch intencional
    -- Restauramos o comentário mais simples do DEBT-120 (que ainda é válido)
    -- Nota: se a coluna for dropada no passo abaixo, este COMMENT não é necessário
    -- mas é incluído por completude em caso de rollback parcial
    COMMENT ON COLUMN public.pipeline_items.search_id IS
        'DEBT-120 AC5: Links pipeline item to the search session that discovered it';
    RAISE NOTICE 'ROLLBACK: COMMENT em pipeline_items.search_id restaurado para versão DEBT-120';

    -- PASSO 2: Reverter DEBT-120 AC5 — remover search_id
    DROP INDEX IF EXISTS public.idx_pipeline_items_search_id;
    ALTER TABLE public.pipeline_items
        DROP COLUMN IF EXISTS search_id;
    RAISE NOTICE 'ROLLBACK: DROP COLUMN search_id + idx_pipeline_items_search_id (DEBT-120 AC5)';

    -- PASSO 3: Reverter DEBT-001 DB-038 — remover index de user_id criado como correção
    -- Nota: idx_pipeline_items_user_id foi criado para substituir idx_pipeline_user_id errado
    -- Ao reverter, o index idx_pipeline_user_id (errado) não existe mais, então
    -- apenas removemos o correto para voltar ao estado anterior
    DROP INDEX IF EXISTS public.idx_pipeline_items_user_id;
    RAISE NOTICE 'ROLLBACK: DROP INDEX idx_pipeline_items_user_id (DEBT-001 DB-038)';

    -- PASSO 4: Reverter STORY-318 concurrency — remover version
    ALTER TABLE public.pipeline_items
        DROP COLUMN IF EXISTS version;
    RAISE NOTICE 'ROLLBACK: DROP COLUMN version (STORY-318 optimistic locking)';

COMMIT;

-- ============================================================
-- PÓS-ROLLBACK: Verificar estado revertido
-- ============================================================

DO $$
DECLARE
    col_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO col_count
    FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = 'pipeline_items'
      AND column_name IN ('search_id', 'version');

    IF col_count > 0 THEN
        RAISE WARNING 'PÓS-VERIFICAÇÃO FALHOU: % colunas alvo ainda existem em pipeline_items', col_count;
    ELSE
        RAISE NOTICE 'PÓS-VERIFICAÇÃO OK: Colunas search_id e version removidas de pipeline_items';
    END IF;

    IF EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE schemaname = 'public' AND tablename = 'pipeline_items'
          AND indexname IN ('idx_pipeline_items_search_id', 'idx_pipeline_items_user_id')
    ) THEN
        RAISE WARNING 'PÓS-VERIFICAÇÃO FALHOU: Ainda existem indexes alvo em pipeline_items';
    ELSE
        RAISE NOTICE 'PÓS-VERIFICAÇÃO OK: Indexes alvo removidos de pipeline_items';
    END IF;

    RAISE NOTICE 'PÓS-VERIFICAÇÃO: Rollback de pipeline_items completado';
    RAISE NOTICE 'AÇÃO REQUERIDA: Atualizar backend/routes/pipeline.py para remover uso de search_id e version';
    RAISE NOTICE 'AÇÃO REQUERIDA: Desativar optimistic locking (STORY-318) no backend';
END $$;
