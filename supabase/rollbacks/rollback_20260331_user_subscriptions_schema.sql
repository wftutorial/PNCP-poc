-- rollback_20260331_user_subscriptions_schema.sql
-- Tabela: user_subscriptions
-- Propósito: Reverter mudanças recentes de schema em user_subscriptions
--
-- Migrations revertidas (cronológica decrescente):
--   20260321130100_debt_db010_jsonb_size_governance.sql
--     → DROP CONSTRAINT chk_user_subscriptions_annual_benefits_size
--   20260321100000_debt_db001_subscription_status_sync.sql
--     → DROP TRIGGER trg_sync_subscription_status
--     → DROP FUNCTION sync_subscription_status_to_profile
--   20260308400000_debt010_schema_guards.sql
--     → DROP CONSTRAINT chk_user_subscriptions_billing_period (semiannual)
--     → DROP INDEX idx_user_subscriptions_billing
--     → Restaurar billing_period para aceitar apenas ('monthly', 'annual')
--   20260227130000_add_dunning_fields.sql
--     → DROP COLUMN first_failed_at
--     → DROP INDEX idx_user_subscriptions_first_failed_at
--   20260225100000_add_missing_profile_columns.sql
--     → DROP COLUMN subscription_status
--     → DROP CONSTRAINT chk_user_subs_subscription_status
--
-- INSTRUÇÕES DE USO:
-- 1. Verificar que PITR está disponível antes de executar
-- 2. Executar em staging primeiro
-- 3. Validar que nenhum dado em billing_period='semiannual' existe antes de
--    reverter o constraint (se existir, o rollback do constraint falhará)
-- 4. NUNCA executar em produção sem backup confirmado e janela de manutenção
--
-- Última modificação: 2026-03-31

-- ============================================================
-- PRÉ-ROLLBACK: Verificar estado esperado
-- ============================================================

DO $$
DECLARE
    semiannual_count INTEGER;
BEGIN
    ASSERT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'user_subscriptions'
    ), 'ERRO: Tabela user_subscriptions não encontrada. Abortando rollback.';

    RAISE NOTICE 'PRÉ-VERIFICAÇÃO OK: Tabela user_subscriptions encontrada';

    -- CRÍTICO: Verificar se há dados com billing_period='semiannual'
    -- Se existirem, reverter o constraint vai falhar
    SELECT COUNT(*) INTO semiannual_count
    FROM public.user_subscriptions
    WHERE billing_period = 'semiannual';

    IF semiannual_count > 0 THEN
        RAISE WARNING 'PRÉ-AVISO CRÍTICO: % linhas com billing_period=''semiannual'' encontradas. '
                      'Reverter o constraint falhará. Migrar dados antes de continuar.',
                      semiannual_count;
    ELSE
        RAISE NOTICE 'PRÉ-VERIFICAÇÃO OK: Nenhum dado com billing_period=semiannual';
    END IF;

    -- Verificar coluna first_failed_at
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'user_subscriptions'
          AND column_name = 'first_failed_at'
    ) THEN
        RAISE NOTICE 'PRÉ-VERIFICAÇÃO: first_failed_at EXISTS — será removida';
    ELSE
        RAISE NOTICE 'PRÉ-AVISO: first_failed_at NÃO existe (já rollbacked?)';
    END IF;

    -- Verificar coluna subscription_status
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'user_subscriptions'
          AND column_name = 'subscription_status'
    ) THEN
        RAISE NOTICE 'PRÉ-VERIFICAÇÃO: subscription_status EXISTS — será removida';
    ELSE
        RAISE NOTICE 'PRÉ-AVISO: subscription_status NÃO existe (já rollbacked?)';
    END IF;
END $$;

-- ============================================================
-- ROLLBACK: Operação principal
-- ============================================================

BEGIN;

    -- PASSO 1: Remover trigger e função de sync (DEBT-DB-001)
    DROP TRIGGER IF EXISTS trg_sync_subscription_status ON public.user_subscriptions;
    DROP FUNCTION IF EXISTS public.sync_subscription_status_to_profile();
    RAISE NOTICE 'ROLLBACK: DROP TRIGGER trg_sync_subscription_status e função sync (DEBT-DB-001)';

    -- PASSO 2: Reverter DEBT-DB-010 — remover CHECK constraint de tamanho JSONB
    ALTER TABLE public.user_subscriptions
        DROP CONSTRAINT IF EXISTS chk_user_subscriptions_annual_benefits_size;
    RAISE NOTICE 'ROLLBACK: DROP CONSTRAINT chk_user_subscriptions_annual_benefits_size (DEBT-DB-010)';

    -- PASSO 3: Reverter DEBT-010 — billing_period constraint
    -- Voltar a aceitar apenas 'monthly' e 'annual' (sem 'semiannual')
    ALTER TABLE public.user_subscriptions
        DROP CONSTRAINT IF EXISTS chk_user_subscriptions_billing_period;
    -- Nota: Se existem dados com billing_period='semiannual', este ADD CONSTRAINT falhará
    ALTER TABLE public.user_subscriptions
        ADD CONSTRAINT chk_user_subscriptions_billing_period_legacy
        CHECK (billing_period IN ('monthly', 'annual'));
    RAISE NOTICE 'ROLLBACK: billing_period constraint revertido para (monthly, annual) — sem semiannual';

    -- PASSO 4: Reverter DEBT-010 — billing index
    DROP INDEX IF EXISTS public.idx_user_subscriptions_billing;
    RAISE NOTICE 'ROLLBACK: DROP INDEX idx_user_subscriptions_billing (DEBT-010)';

    -- PASSO 5: Reverter 20260227130000_add_dunning_fields.sql
    DROP INDEX IF EXISTS public.idx_user_subscriptions_first_failed_at;
    ALTER TABLE public.user_subscriptions
        DROP COLUMN IF EXISTS first_failed_at;
    RAISE NOTICE 'ROLLBACK: DROP COLUMN first_failed_at + index (STORY-309 dunning fields)';

    -- PASSO 6: Reverter 20260225100000_add_missing_profile_columns.sql
    ALTER TABLE public.user_subscriptions
        DROP CONSTRAINT IF EXISTS chk_user_subs_subscription_status;
    ALTER TABLE public.user_subscriptions
        DROP COLUMN IF EXISTS subscription_status;
    RAISE NOTICE 'ROLLBACK: DROP COLUMN subscription_status + constraint (20260225)';

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
    WHERE table_schema = 'public' AND table_name = 'user_subscriptions'
      AND column_name IN ('first_failed_at', 'subscription_status');

    IF col_count > 0 THEN
        RAISE WARNING 'PÓS-VERIFICAÇÃO FALHOU: % colunas alvo ainda existem em user_subscriptions', col_count;
    ELSE
        RAISE NOTICE 'PÓS-VERIFICAÇÃO OK: Colunas alvo removidas de user_subscriptions';
    END IF;

    -- Verificar que o trigger foi removido
    IF EXISTS (
        SELECT 1 FROM pg_trigger
        WHERE tgname = 'trg_sync_subscription_status'
    ) THEN
        RAISE WARNING 'PÓS-VERIFICAÇÃO FALHOU: trg_sync_subscription_status ainda existe';
    ELSE
        RAISE NOTICE 'PÓS-VERIFICAÇÃO OK: trg_sync_subscription_status removido';
    END IF;

    RAISE NOTICE 'PÓS-VERIFICAÇÃO: Rollback de user_subscriptions completado';
    RAISE NOTICE 'AÇÃO REQUERIDA: Reverter profiles.subscription_status também (ver rollback_profiles_recent_columns.sql)';
END $$;
