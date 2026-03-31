-- rollback_20260331_search_results_cache_structure.sql
-- Tabela: search_results_cache
-- Propósito: Reverter mudanças de estrutura adicionadas nas últimas migrations
--
-- Migrations revertidas (cronológica decrescente):
--   20260321130100_debt_db010_jsonb_size_governance.sql
--     → DROP CONSTRAINT chk_search_results_cache_search_params_size
--     → DROP CONSTRAINT chk_search_results_cache_sources_json_size
--     → DROP CONSTRAINT chk_search_results_cache_coverage_size
--   20260323100000_debt_quick_wins.sql (DA-01/DB-L05)
--     → Reverter cleanup_search_cache_per_user() para versão DEBT-017 (5 entradas, FIFO)
--   20260308400000_debt010_schema_guards.sql (DB-018)
--     → DROP CONSTRAINT chk_search_results_cache_priority
--   20260315100000_debt120_db_optimization.sql (AC3)
--     → Recriar idx_search_cache_fetched_at (que foi dropado)
--   032_cache_priority_fields.sql
--     → DROP COLUMN priority, access_count, last_accessed_at
--     → DROP INDEX idx_search_cache_priority
--
-- INSTRUÇÕES DE USO:
-- 1. Verificar que PITR está disponível antes de executar
-- 2. Executar em staging com dados sintéticos primeiro
-- 3. Validar que o backend consegue funcionar sem os campos de priority
-- 4. NUNCA executar em produção sem backup confirmado
-- 5. cache.py e search_cache.py referenciam priority — atualizar código antes deste rollback
--
-- Última modificação: 2026-03-31

-- ============================================================
-- PRÉ-ROLLBACK: Verificar estado esperado
-- ============================================================

DO $$
BEGIN
    ASSERT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'search_results_cache'
    ), 'ERRO: Tabela search_results_cache não encontrada. Abortando rollback.';

    RAISE NOTICE 'PRÉ-VERIFICAÇÃO OK: Tabela search_results_cache encontrada';

    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'search_results_cache'
          AND column_name = 'priority'
    ) THEN
        RAISE NOTICE 'PRÉ-VERIFICAÇÃO: Coluna priority EXISTS — será removida';
    ELSE
        RAISE NOTICE 'PRÉ-AVISO: Coluna priority NÃO existe (já rollbacked?)';
    END IF;

    IF EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'public.search_results_cache'::regclass
          AND conname = 'chk_search_results_cache_priority'
    ) THEN
        RAISE NOTICE 'PRÉ-VERIFICAÇÃO: chk_search_results_cache_priority EXISTS — será removida';
    END IF;

    IF EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'public.search_results_cache'::regclass
          AND conname = 'chk_search_results_cache_search_params_size'
    ) THEN
        RAISE NOTICE 'PRÉ-VERIFICAÇÃO: chk_search_results_cache_search_params_size EXISTS — será removida';
    END IF;
END $$;

-- ============================================================
-- ROLLBACK: Operação principal
-- ============================================================

BEGIN;

    -- PASSO 1: Reverter DEBT-DB-010 — remover CHECK constraints de tamanho JSONB
    ALTER TABLE public.search_results_cache
        DROP CONSTRAINT IF EXISTS chk_search_results_cache_search_params_size;
    ALTER TABLE public.search_results_cache
        DROP CONSTRAINT IF EXISTS chk_search_results_cache_sources_json_size;
    ALTER TABLE public.search_results_cache
        DROP CONSTRAINT IF EXISTS chk_search_results_cache_coverage_size;
    RAISE NOTICE 'ROLLBACK: DROP CONSTRAINTs de tamanho JSONB em search_results_cache (DEBT-DB-010)';

    -- PASSO 2: Reverter DEBT-010 DB-018 — remover CHECK constraint de priority
    ALTER TABLE public.search_results_cache
        DROP CONSTRAINT IF EXISTS chk_search_results_cache_priority;
    RAISE NOTICE 'ROLLBACK: DROP CONSTRAINT chk_search_results_cache_priority (DEBT-010 DB-018)';

    -- PASSO 3: Reverter prioridade-aware eviction (DA-01/DB-L05 de 20260323)
    -- Voltar para a versão FIFO simples com limite de 5 entradas (DEBT-017)
    CREATE OR REPLACE FUNCTION public.cleanup_search_cache_per_user()
    RETURNS TRIGGER AS $$
    DECLARE
        entry_count INTEGER;
    BEGIN
        -- Versão revertida: FIFO com 5 entradas (DEBT-017 original)
        SELECT COUNT(*) INTO entry_count
        FROM search_results_cache
        WHERE user_id = NEW.user_id;

        IF entry_count <= 5 THEN
            RETURN NEW;
        END IF;

        DELETE FROM search_results_cache
        WHERE id IN (
            SELECT id FROM search_results_cache
            WHERE user_id = NEW.user_id
            ORDER BY created_at DESC
            OFFSET 5
        );
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql SECURITY DEFINER;
    RAISE NOTICE 'ROLLBACK: cleanup_search_cache_per_user() revertida para FIFO/5 entradas (DEBT-017)';

    -- PASSO 4: Reverter 032_cache_priority_fields.sql
    -- Remover índice de priority primeiro
    DROP INDEX IF EXISTS public.idx_search_cache_priority;
    RAISE NOTICE 'ROLLBACK: DROP INDEX idx_search_cache_priority (032_cache_priority_fields)';

    -- Remover colunas de priority/access
    ALTER TABLE public.search_results_cache
        DROP COLUMN IF EXISTS priority,
        DROP COLUMN IF EXISTS access_count,
        DROP COLUMN IF EXISTS last_accessed_at;
    RAISE NOTICE 'ROLLBACK: DROP COLUMNS priority, access_count, last_accessed_at (032_cache_priority_fields)';

    -- PASSO 5: Recriar idx_search_cache_fetched_at (removido em DEBT-120 AC3)
    -- Nota: só recriar se a coluna fetched_at ainda existir
    DO $inner$
    BEGIN
        IF EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'search_results_cache'
              AND column_name = 'fetched_at'
        ) THEN
            CREATE INDEX IF NOT EXISTS idx_search_cache_fetched_at
                ON public.search_results_cache (fetched_at);
            RAISE NOTICE 'ROLLBACK: RECREATE INDEX idx_search_cache_fetched_at (DEBT-120 reversal)';
        ELSE
            RAISE NOTICE 'ROLLBACK SKIP: fetched_at coluna não existe — idx_search_cache_fetched_at não recriado';
        END IF;
    END $inner$;

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
    WHERE table_schema = 'public' AND table_name = 'search_results_cache'
      AND column_name IN ('priority', 'access_count', 'last_accessed_at');

    IF col_count > 0 THEN
        RAISE WARNING 'PÓS-VERIFICAÇÃO FALHOU: % colunas de priority ainda existem em search_results_cache', col_count;
    ELSE
        RAISE NOTICE 'PÓS-VERIFICAÇÃO OK: Colunas de priority removidas de search_results_cache';
    END IF;

    IF EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'public.search_results_cache'::regclass
          AND conname IN (
              'chk_search_results_cache_priority',
              'chk_search_results_cache_search_params_size',
              'chk_search_results_cache_sources_json_size',
              'chk_search_results_cache_coverage_size'
          )
    ) THEN
        RAISE WARNING 'PÓS-VERIFICAÇÃO FALHOU: Ainda existem constraints alvo em search_results_cache';
    ELSE
        RAISE NOTICE 'PÓS-VERIFICAÇÃO OK: Constraints alvo removidos de search_results_cache';
    END IF;

    RAISE NOTICE 'PÓS-VERIFICAÇÃO: Rollback de search_results_cache completado';
    RAISE NOTICE 'AÇÃO REQUERIDA: Atualizar backend/cache.py e backend/search_cache.py para '
                 'remover referências a priority, access_count, last_accessed_at';
END $$;
