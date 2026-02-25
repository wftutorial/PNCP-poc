# STORY-261: Database Schema Integrity — Missing Columns

## Metadata
- **Epic:** Enterprise Readiness (EPIC-ENT-001)
- **Priority:** P0 (Blocking)
- **Effort:** 1.5 hours
- **Area:** Database
- **Depends on:** None
- **Risk:** Low (all ADD COLUMN IF NOT EXISTS — idempotent)
- **Assessment IDs:** T1-01, T1-02, T1-03, T1-05, T1-06

## Context

5 colunas do banco de dados existem em producao (adicionadas via Supabase Dashboard) mas **nao tem migration**. Em cenario de disaster recovery (recriacao do DB a partir de migrations), Stripe billing, analytics, trial status, subscription cancel, e email opt-out quebram. Isso impede producao enterprise-grade confiavel.

## Acceptance Criteria

- [ ] AC1: Coluna `profiles.subscription_status` existe com DEFAULT 'trial' e CHECK constraint
- [ ] AC2: Coluna `profiles.trial_expires_at` existe como TIMESTAMPTZ
- [ ] AC3: Coluna `profiles.subscription_end_date` existe como TIMESTAMPTZ
- [ ] AC4: Coluna `profiles.email_unsubscribed` existe com DEFAULT FALSE
- [ ] AC5: Coluna `profiles.email_unsubscribed_at` existe como TIMESTAMPTZ
- [ ] AC6: Coluna `user_subscriptions.subscription_status` existe com DEFAULT 'active' e CHECK constraint
- [ ] AC7: Index parcial em `profiles.subscription_status` criado
- [ ] AC8: Migration e idempotente (roda sem erro em DB que ja tem as colunas)
- [ ] AC9: `pytest tests/test_stripe_webhooks.py` passa
- [ ] AC10: `pytest tests/test_api_me.py` passa — `/me` retorna `subscription_status`
- [ ] AC11: `pytest -k "analytics"` passa
- [ ] AC12: `pytest -k "subscriptions"` passa

## Tasks

- [ ] Task 1: Criar migration `supabase/migrations/20260225100000_add_missing_profile_columns.sql`
- [ ] Task 2: Aplicar migration em ambiente de teste
- [ ] Task 3: Rodar full backend test suite (`pytest`)
- [ ] Task 4: Verificar que migration e no-op em producao (colunas ja existem)

## Migration SQL

```sql
-- Migration: 20260225100000_add_missing_profile_columns.sql

BEGIN;

-- T1-01: profiles.subscription_status
ALTER TABLE public.profiles
    ADD COLUMN IF NOT EXISTS subscription_status TEXT DEFAULT 'trial';
ALTER TABLE public.profiles
    ADD CONSTRAINT chk_profiles_subscription_status
    CHECK (subscription_status IN ('trial', 'active', 'canceling', 'past_due', 'expired'));
CREATE INDEX IF NOT EXISTS idx_profiles_subscription_status
    ON profiles (subscription_status)
    WHERE subscription_status != 'trial';

-- T1-02: profiles.trial_expires_at
ALTER TABLE public.profiles
    ADD COLUMN IF NOT EXISTS trial_expires_at TIMESTAMPTZ;

-- T1-05: profiles.subscription_end_date
ALTER TABLE public.profiles
    ADD COLUMN IF NOT EXISTS subscription_end_date TIMESTAMPTZ;

-- T1-06: profiles.email_unsubscribed (LGPD compliance)
ALTER TABLE public.profiles
    ADD COLUMN IF NOT EXISTS email_unsubscribed BOOLEAN DEFAULT FALSE;
ALTER TABLE public.profiles
    ADD COLUMN IF NOT EXISTS email_unsubscribed_at TIMESTAMPTZ;

-- T1-03: user_subscriptions.subscription_status
ALTER TABLE public.user_subscriptions
    ADD COLUMN IF NOT EXISTS subscription_status TEXT DEFAULT 'active';
ALTER TABLE public.user_subscriptions
    ADD CONSTRAINT chk_user_subs_subscription_status
    CHECK (subscription_status IN ('active', 'trialing', 'past_due', 'canceled', 'expired'));

COMMIT;
```

## Test Plan

1. Run migration on test DB — verify all columns created
2. `pytest tests/test_stripe_webhooks.py` — Stripe webhooks write `subscription_status`
3. `pytest tests/test_api_me.py` — `/me` returns `subscription_status` field
4. `pytest -k "analytics"` — analytics endpoint reads `trial_expires_at`
5. `pytest -k "subscriptions"` — cancel flow writes `subscription_end_date`
6. Full `pytest` suite — 0 regressions

## Regression Risks

- **Risco:** CHECK constraint pode rejeitar valores inesperados se codigo escreve status fora da lista.
- **Mitigacao:** Valores foram validados contra codigo-fonte: profiles usa (trial, active, canceling, past_due, expired); user_subscriptions usa (active, trialing, past_due, canceled, expired).
- **Severidade:** Baixa — `ADD COLUMN IF NOT EXISTS` e idempotente.

## Files Changed

- `supabase/migrations/20260225100000_add_missing_profile_columns.sql` (NEW)

## Definition of Done

- [ ] Migration criada e aplicada
- [ ] Todos os acceptance criteria met
- [ ] Full pytest suite passing (5131+ tests, 0 failures)
- [ ] No regressions
