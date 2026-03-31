-- rollback_20260331_profiles_recent_columns.sql
-- Tabela: profiles
-- Propósito: Reverter colunas e constraints adicionadas nas últimas migrations
--
-- Migrations revertidas (cronológica decrescente):
--   20260321130100_debt_db010_jsonb_size_governance.sql
--     → DROP CONSTRAINT chk_profiles_context_data_size
--   20260225100000_add_missing_profile_columns.sql
--     → DROP COLUMN subscription_status, trial_expires_at, subscription_end_date,
--                   email_unsubscribed, email_unsubscribed_at
--     → DROP CONSTRAINT chk_profiles_subscription_status
--     → DROP INDEX idx_profiles_subscription_status
--
-- INSTRUÇÕES DE USO:
-- 1. Verificar que PITR (Point-in-Time Recovery) está disponível antes de executar
-- 2. Executar em staging com dados sintéticos primeiro
-- 3. Validar integridade de FKs e dependências após rollback
-- 4. NUNCA executar em produção sem backup confirmado e janela de manutenção
-- 5. O trigger trg_sync_subscription_status (DEBT-DB-001) depende de
--    profiles.subscription_status — desative-o antes de dropar a coluna
--
-- Última modificação: 2026-03-31

-- ============================================================
-- PRÉ-ROLLBACK: Verificar estado esperado
-- ============================================================

DO $$
BEGIN
    ASSERT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'profiles'
    ), 'ERRO: Tabela profiles não encontrada. Abortando rollback.';

    RAISE NOTICE 'PRÉ-VERIFICAÇÃO OK: Tabela profiles encontrada';

    -- Verificar quais colunas existem para log informativo
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'profiles'
          AND column_name = 'subscription_status'
    ) THEN
        RAISE NOTICE 'PRÉ-VERIFICAÇÃO: profiles.subscription_status EXISTS — será removida';
    ELSE
        RAISE NOTICE 'PRÉ-AVISO: profiles.subscription_status NÃO existe (já rollbacked?)';
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'profiles'
          AND column_name = 'trial_expires_at'
    ) THEN
        RAISE NOTICE 'PRÉ-VERIFICAÇÃO: profiles.trial_expires_at EXISTS — será removida';
    ELSE
        RAISE NOTICE 'PRÉ-AVISO: profiles.trial_expires_at NÃO existe (já rollbacked?)';
    END IF;

    IF EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'public.profiles'::regclass
          AND conname = 'chk_profiles_context_data_size'
    ) THEN
        RAISE NOTICE 'PRÉ-VERIFICAÇÃO: chk_profiles_context_data_size EXISTS — será removida';
    ELSE
        RAISE NOTICE 'PRÉ-AVISO: chk_profiles_context_data_size NÃO existe (já rollbacked?)';
    END IF;
END $$;

-- ============================================================
-- ROLLBACK: Operação principal
-- ============================================================

BEGIN;

    -- PASSO 1: Desativar o trigger que sincroniza subscription_status
    -- (DEBT-DB-001 — trg_sync_subscription_status usa profiles.subscription_status)
    DROP TRIGGER IF EXISTS trg_sync_subscription_status ON public.user_subscriptions;
    RAISE NOTICE 'ROLLBACK: trg_sync_subscription_status desativado';

    -- PASSO 2: Reverter DEBT-DB-010 — remover CHECK constraint de tamanho JSONB em profiles
    ALTER TABLE public.profiles
        DROP CONSTRAINT IF EXISTS chk_profiles_context_data_size;
    RAISE NOTICE 'ROLLBACK: DROP CONSTRAINT chk_profiles_context_data_size (DEBT-DB-010)';

    -- PASSO 3: Reverter 20260225100000_add_missing_profile_columns.sql
    -- Remover CHECK constraint de subscription_status
    ALTER TABLE public.profiles
        DROP CONSTRAINT IF EXISTS chk_profiles_subscription_status;
    RAISE NOTICE 'ROLLBACK: DROP CONSTRAINT chk_profiles_subscription_status';

    -- Remover índice parcial de subscription_status
    DROP INDEX IF EXISTS public.idx_profiles_subscription_status;
    RAISE NOTICE 'ROLLBACK: DROP INDEX idx_profiles_subscription_status';

    -- Remover colunas adicionadas em 20260225100000
    ALTER TABLE public.profiles
        DROP COLUMN IF EXISTS subscription_status,
        DROP COLUMN IF EXISTS trial_expires_at,
        DROP COLUMN IF EXISTS subscription_end_date,
        DROP COLUMN IF EXISTS email_unsubscribed,
        DROP COLUMN IF EXISTS email_unsubscribed_at;
    RAISE NOTICE 'ROLLBACK: DROP COLUMNS subscription_status, trial_expires_at, subscription_end_date, email_unsubscribed, email_unsubscribed_at';

COMMIT;

-- ============================================================
-- PÓS-ROLLBACK: Verificar estado revertido
-- ============================================================

DO $$
DECLARE
    col_count INTEGER;
BEGIN
    -- Verificar que as colunas foram removidas
    SELECT COUNT(*) INTO col_count
    FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = 'profiles'
      AND column_name IN (
          'subscription_status', 'trial_expires_at', 'subscription_end_date',
          'email_unsubscribed', 'email_unsubscribed_at'
      );

    IF col_count > 0 THEN
        RAISE WARNING 'PÓS-VERIFICAÇÃO FALHOU: % colunas ainda existem em profiles', col_count;
    ELSE
        RAISE NOTICE 'PÓS-VERIFICAÇÃO OK: Todas as colunas alvo foram removidas de profiles';
    END IF;

    -- Verificar que os constraints foram removidos
    IF EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'public.profiles'::regclass
          AND conname IN ('chk_profiles_subscription_status', 'chk_profiles_context_data_size')
    ) THEN
        RAISE WARNING 'PÓS-VERIFICAÇÃO FALHOU: Ainda existem constraints alvo em profiles';
    ELSE
        RAISE NOTICE 'PÓS-VERIFICAÇÃO OK: Constraints alvo removidos de profiles';
    END IF;

    RAISE NOTICE 'PÓS-VERIFICAÇÃO: Rollback de profiles completado';
    RAISE NOTICE 'AÇÃO REQUERIDA: Reverter sync_subscription_status_to_profile() function e '
                 'o trigger trg_sync_subscription_status se necessário (DEBT-DB-001)';
END $$;
