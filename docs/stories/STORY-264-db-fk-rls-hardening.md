# STORY-264: Database FK & RLS Hardening

## Metadata
- **Epic:** Enterprise Readiness (EPIC-ENT-001)
- **Priority:** P1 (Stability)
- **Effort:** 3 hours
- **Area:** Database
- **Depends on:** STORY-261 (Phase A completa)
- **Risk:** Medium (FK repointing requer orphan check)
- **Assessment IDs:** T2-01, T2-02, T2-05, T2-07, T2-08, T2-09

## Context

3 tabelas referenciam `auth.users(id)` em vez de `profiles(id)`, criando risco de orphaned rows. `classification_feedback` nao tem ON DELETE CASCADE, bloqueando delecao de usuarios. 3 tabelas faltam service_role policies (defense-in-depth). `search_state_transitions` permite INSERT por qualquer usuario autenticado (audit log injection). `search_sessions` falta indice composto para queries frequentes.

## Acceptance Criteria

- [ ] AC1: `pipeline_items.user_id` FK aponta para `profiles(id) ON DELETE CASCADE`
- [ ] AC2: `classification_feedback.user_id` FK aponta para `profiles(id) ON DELETE CASCADE`
- [ ] AC3: `trial_email_log.user_id` FK aponta para `profiles(id) ON DELETE CASCADE`
- [ ] AC4: Deletar profile cascadeia para pipeline_items, classification_feedback, trial_email_log
- [ ] AC5: `search_state_transitions` INSERT restrito a service_role
- [ ] AC6: `profiles` tem service_role ALL policy
- [ ] AC7: `conversations` e `messages` tem service_role ALL policies
- [ ] AC8: Index composto `(user_id, status, created_at DESC)` existe em `search_sessions`
- [ ] AC9: Zero orphaned rows antes de aplicar migrations
- [ ] AC10: Full backend test suite passa

## Tasks

- [ ] Task 1: **PRE-CHECK** — Query producao para orphaned `user_id` em pipeline_items, classification_feedback, trial_email_log que nao existem em `profiles`
- [ ] Task 2: Se orphans existem, limpar ANTES da migration
- [ ] Task 3: Criar migration `supabase/migrations/20260225120000_standardize_fks_to_profiles.sql`
- [ ] Task 4: Criar migration `supabase/migrations/20260225130000_rls_policy_hardening.sql`
- [ ] Task 5: Criar migration `supabase/migrations/20260225140000_add_session_composite_index.sql`
- [ ] Task 6: Aplicar migrations em staging
- [ ] Task 7: Testar cascade delete
- [ ] Task 8: Testar RLS policies (service_role vs authenticated)
- [ ] Task 9: Deploy em producao

## Migration SQL

### Migration C: FK Standardization
```sql
-- 20260225120000_standardize_fks_to_profiles.sql
BEGIN;

-- pipeline_items
DO $$ BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'pipeline_items_user_id_fkey' AND table_name = 'pipeline_items')
    THEN ALTER TABLE pipeline_items DROP CONSTRAINT pipeline_items_user_id_fkey;
    END IF;
END $$;
ALTER TABLE pipeline_items ADD CONSTRAINT pipeline_items_user_id_profiles_fkey
    FOREIGN KEY (user_id) REFERENCES profiles(id) ON DELETE CASCADE NOT VALID;
ALTER TABLE pipeline_items VALIDATE CONSTRAINT pipeline_items_user_id_profiles_fkey;

-- classification_feedback
DO $$ BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'classification_feedback_user_id_fkey' AND table_name = 'classification_feedback')
    THEN ALTER TABLE classification_feedback DROP CONSTRAINT classification_feedback_user_id_fkey;
    END IF;
END $$;
ALTER TABLE classification_feedback ADD CONSTRAINT classification_feedback_user_id_profiles_fkey
    FOREIGN KEY (user_id) REFERENCES profiles(id) ON DELETE CASCADE NOT VALID;
ALTER TABLE classification_feedback VALIDATE CONSTRAINT classification_feedback_user_id_profiles_fkey;

-- trial_email_log
DO $$ BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'trial_email_log_user_id_fkey' AND table_name = 'trial_email_log')
    THEN ALTER TABLE trial_email_log DROP CONSTRAINT trial_email_log_user_id_fkey;
    END IF;
END $$;
ALTER TABLE trial_email_log ADD CONSTRAINT trial_email_log_user_id_profiles_fkey
    FOREIGN KEY (user_id) REFERENCES profiles(id) ON DELETE CASCADE NOT VALID;
ALTER TABLE trial_email_log VALIDATE CONSTRAINT trial_email_log_user_id_profiles_fkey;

COMMIT;
```

### Migration D: RLS Policy Hardening
```sql
-- 20260225130000_rls_policy_hardening.sql
BEGIN;

DROP POLICY IF EXISTS "Service role can insert transitions" ON search_state_transitions;
CREATE POLICY "Service role can insert transitions" ON search_state_transitions
    FOR INSERT TO service_role WITH CHECK (true);

DROP POLICY IF EXISTS "profiles_service_all" ON public.profiles;
CREATE POLICY "profiles_service_all" ON public.profiles
    FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "conversations_service_all" ON conversations;
CREATE POLICY "conversations_service_all" ON conversations
    FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "messages_service_all" ON messages;
CREATE POLICY "messages_service_all" ON messages
    FOR ALL TO service_role USING (true) WITH CHECK (true);

COMMIT;
```

### Migration E: Session Index
```sql
-- 20260225140000_add_session_composite_index.sql
CREATE INDEX IF NOT EXISTS idx_search_sessions_user_status_created
    ON search_sessions (user_id, status, created_at DESC);
```

## Test Plan

1. **Pre-check orphans:** `SELECT user_id FROM pipeline_items WHERE user_id NOT IN (SELECT id FROM profiles)` (same for other 2 tables)
2. **Cascade delete:** Delete test profile -> verify pipeline_items, classification_feedback, trial_email_log rows deleted
3. **RLS T2-05:** INSERT into `search_state_transitions` as authenticated user -> must fail
4. **RLS T2-05:** INSERT as service_role -> must succeed
5. **Index:** `EXPLAIN ANALYZE` on `SELECT * FROM search_sessions WHERE user_id=X AND status='completed' ORDER BY created_at DESC`
6. Full `pytest`

## Regression Risks

- **MEDIO:** Se orphaned data existe, FK creation falha e transaction rollback. Usar `NOT VALID` + `VALIDATE` two-phase.
- **MEDIO:** Se algum code path insere em `search_state_transitions` sem service_role, inserts falham apos T2-05. Verificar com grep.
- **Mitigacao:** Pre-check orphans obrigatorio. Grep por todos INSERT paths de `search_state_transitions`.

## Files Changed

- `supabase/migrations/20260225120000_standardize_fks_to_profiles.sql` (NEW)
- `supabase/migrations/20260225130000_rls_policy_hardening.sql` (NEW)
- `supabase/migrations/20260225140000_add_session_composite_index.sql` (NEW)

## Definition of Done

- [ ] Pre-check orphans executado (zero orphans)
- [ ] 3 migrations criadas e aplicadas
- [ ] Cascade delete funcional
- [ ] RLS policies validadas
- [ ] Index criado e usado em query plans
- [ ] Full test suite passing
