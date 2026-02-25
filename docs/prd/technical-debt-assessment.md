# Technical Debt Assessment - FINAL

**Projeto:** SmartLic v0.5
**Data:** 2026-02-25
**Objetivo:** Viabilizar producao monetizada enterprise-grade
**QA Gate:** APPROVED
**Revisores:** @architect, @data-engineer, @ux-design-expert, @qa

---

## Executive Summary

Este assessment consolida a analise de 4 documentos produzidos nas Fases 1-3 do brownfield discovery (system-architecture, schema, DB-audit, frontend-spec), validados por 3 especialistas (DB, UX, QA) nas Fases 5-7. O inventario total compreende **92 debitos tecnicos** em 3 areas (sistema, database, frontend). Apos validacao cruzada, o QA gate aprovou o assessment com ajustes: **7 itens Tier 1** (bloqueantes), **14 itens Tier 2** (estabilidade), e **71 itens Tier 3** (aceitos).

A descoberta critica e que o core do SmartLic funciona em producao hoje, mas **5 colunas do banco existem apenas via Dashboard** (sem migration), o **trigger de signup descarta 6 campos do perfil**, e **error boundaries expoem erros tecnicos raw** ao usuario. Em cenario de disaster recovery (recriacao do DB a partir de migrations), billing, analytics, trial stats, e email opt-out quebram. A cada novo signup, `company`, `sector`, `whatsapp_consent` sao silenciosamente descartados.

**Acao recomendada:** Executar os 7 itens Tier 1 (2-3 horas) + 14 itens Tier 2 (10-12 horas) em 2 dias de trabalho. Isso coloca o SmartLic em posicao enterprise-ready para monetizacao em todos os 6 core flows.

---

## Core Functionalities Assessment

| Flow | Enterprise Ready Apos Fixes? | Riscos Restantes |
|------|------------------------------|------------------|
| **Busca multi-fonte** | SIM | In-memory `_active_trackers` limita a 1 instancia web (T3). Railway 120s timeout para buscas multi-UF grandes (T3). |
| **Billing/Subscription** | SIM | Apos T1-01, T1-03, T1-05: todos os webhooks Stripe gravam nas colunas corretas. localStorage plan cache pode mostrar plano stale por ate 1h (GAP-05, T3). |
| **Auth + Onboarding** | SIM | Apos T1-07: trigger popula todos os campos + ON CONFLICT guard. Google OAuth precisa teste manual. |
| **Pipeline (Kanban)** | SIM | Apos T1-04: trial stats query corrigida. Error boundary adicionada (T2-18). |
| **Relatorios (Excel + IA)** | SIM | Sem issues bloqueantes ou de estabilidade. ARQ background jobs funcionais. |
| **Dashboard/Analytics** | SIM | Apos T1-02: `trial_expires_at` existe para queries de analytics. |

**Veredicto:** Todos os 6 core flows estarao enterprise-ready apos os fixes Tier 1 + Tier 2.

---

## Tier 1: BLOCKING (Acoes Imediatas)

**Total: 7 itens | Esforco: ~3 horas (incluindo testes)**

| ID | Debito | Area | Impacto | Esforco | Validado por | Teste Requerido |
|----|--------|------|---------|---------|-------------|-----------------|
| T1-01 | `profiles.subscription_status` sem migration — usado em 5+ modulos (webhooks/stripe.py, routes/billing.py, routes/user.py, schemas.py) | DB | Stripe webhooks falham em DB fresh. `/me` retorna dados incompletos. | 0.25h | @data-engineer | Migration em test DB + `pytest tests/test_stripe_webhooks.py` + verificar `/me` retorna campo |
| T1-02 | `profiles.trial_expires_at` sem migration — usado em analytics, quota, user routes | DB | Analytics endpoint falha em DB fresh. Trial status display quebrado. | 0.25h | @data-engineer | Migration + `pytest -k "analytics"` |
| T1-03 | `user_subscriptions.subscription_status` sem migration — usado em Stripe checkout/payment failure | DB | Webhook de checkout falha em DB fresh. | 0.25h | @data-engineer | Migration + `pytest tests/test_stripe_webhooks.py` |
| T1-04 | `services/trial_stats.py` referencia tabela `user_pipeline` inexistente (correto: `pipeline_items`) + teste mascara o bug | Backend | Runtime error no endpoint trial stats. Afeta todo trial user no pipeline. | 0.5h | @qa | Fix `trial_stats.py:78` + `test_trial_usage_stats.py:70,79,151,188` + `pytest tests/test_trial_usage_stats.py -v` |
| T1-05 | `profiles.subscription_end_date` sem migration — usado em `routes/subscriptions.py:241` no fluxo de cancelamento | DB | Cancel subscription perde `end_date` em DB fresh. | 0.25h | @data-engineer | Migration + `pytest -k "subscriptions"` |
| T1-06 | `profiles.email_unsubscribed` + `email_unsubscribed_at` sem migration — usado em `search_pipeline.py:79`, `routes/emails.py:147-148`. Coluna LGPD compliance. | DB | Email unsubscribe escreve em coluna inexistente em DB fresh. | 0.25h | @data-engineer | Migration + `pytest tests/test_email_triggers.py` |
| T1-07 | `handle_new_user()` trigger regredido — migration `20260224000000` insere apenas 4 campos (id, email, full_name, phone_whatsapp), descartando company, sector, whatsapp_consent, plan_type, avatar_url, context_data. Sem ON CONFLICT. | DB | Todo novo signup perde 6 campos do perfil. Re-signup edge case bloqueia registro (unique violation). | 1.0h | @data-engineer + @qa | Trigger rewrite + teste signup email com metadata + Google OAuth + re-signup + phone normalization |

### Migration SQL — Tier 1

```sql
-- Migration: 20260225100000_add_missing_profile_columns.sql
-- Fixes: T1-01, T1-02, T1-03, T1-05, T1-06
-- Safe: All ADD COLUMN IF NOT EXISTS (idempotent, no-op on production)

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

-- T1-06: profiles.email_unsubscribed + email_unsubscribed_at (LGPD)
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

```sql
-- Migration: 20260225110000_fix_handle_new_user_trigger.sql
-- Fix: T1-07
-- DEPENDS ON: 20260225100000 (new columns must exist before trigger references them)

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
DECLARE
  _phone text;
BEGIN
  _phone := regexp_replace(COALESCE(NEW.raw_user_meta_data->>'phone_whatsapp', ''), '[^0-9]', '', 'g');
  IF length(_phone) > 11 AND left(_phone, 2) = '55' THEN _phone := substring(_phone from 3); END IF;
  IF left(_phone, 1) = '0' THEN _phone := substring(_phone from 2); END IF;
  IF length(_phone) NOT IN (10, 11) THEN _phone := NULL; END IF;

  INSERT INTO public.profiles (
    id, email, full_name, company, sector,
    phone_whatsapp, whatsapp_consent, plan_type,
    avatar_url, context_data
  )
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'full_name', ''),
    COALESCE(NEW.raw_user_meta_data->>'company', ''),
    COALESCE(NEW.raw_user_meta_data->>'sector', ''),
    _phone,
    COALESCE((NEW.raw_user_meta_data->>'whatsapp_consent')::boolean, FALSE),
    'free_trial',
    NEW.raw_user_meta_data->>'avatar_url',
    '{}'::jsonb
  )
  ON CONFLICT (id) DO NOTHING;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

**Backend code fix T1-04:**
```python
# backend/services/trial_stats.py line 78
# ANTES: sb.table("user_pipeline")
# DEPOIS: sb.table("pipeline_items")

# backend/tests/test_trial_usage_stats.py lines 70, 79, 151, 188
# ANTES: mock "user_pipeline"
# DEPOIS: mock "pipeline_items"
```

---

## Tier 2: STABILITY (Estabilidade Enterprise)

**Total: 14 itens | Esforco: ~12 horas (incluindo testes)**

| ID | Debito | Area | Risco | Esforco | Validado por | Teste Requerido |
|----|--------|------|-------|---------|-------------|-----------------|
| T2-01 | 3 tabelas com FK para `auth.users` em vez de `profiles`: pipeline_items, classification_feedback, trial_email_log | DB | Cascade inconsistente. Orphaned rows se profile deletado independentemente. | 1.0h | @data-engineer | Pre-check orphans + migration + teste delete cascade |
| T2-02 | `classification_feedback.user_id` FK sem ON DELETE (default RESTRICT) | DB | Delecao de usuario bloqueada por feedback orfao. | (bundled T2-01) | @data-engineer | Teste delete usuario com feedback existente |
| T2-03 | `search_results_cache.results` JSONB blob sem limite — 50-500KB por entry, ate 5MB por usuario | DB | Inflacao de storage. Queries lentas quando results incluido em SELECT. | 2.0h | @data-engineer | Query production max size ANTES + CHECK constraint + pg_cron cleanup |
| T2-05 | `search_state_transitions` INSERT policy nao scoped para service_role — qualquer usuario autenticado pode inserir | DB | Audit log injection. Usuarios podem inserir transicoes falsas. | 0.25h | @qa | Migration + teste INSERT como authenticated (deve falhar) + INSERT como service_role (deve funcionar) |
| T2-07 | `profiles` sem service_role UPDATE/DELETE policy | DB | Gap defense-in-depth. Backend usa service_role que bypassa RLS. | 0.25h | @qa | Migration + verificar policy existe |
| T2-08 | `conversations` e `messages` sem service_role policies | DB | Mesmo gap defense-in-depth. | 0.25h | @qa | Migration + `pytest -k "messages"` |
| T2-09 | `search_sessions` sem indice composto `(user_id, status, created_at)` | DB | Queries lentas para cleanup de sessoes stale, analytics, SIGTERM shutdown. | 0.25h | @data-engineer | Migration + EXPLAIN ANALYZE em query pattern |
| T2-11 | BottomNav drawer overlay sem focus trap | Frontend | WCAG 2.4.3 a11y violation. Mobile users podem Tab fora do drawer. | 1.5h | @ux-design-expert | Abrir drawer mobile + Tab cycle + Escape close + focus return |
| T2-13 | Dockerfile usa Python 3.11-slim mas pyproject.toml targeta 3.12 | Backend | Version mismatch. Incompatibilidades sutis com type hints e stdlib. | 0.5h | @qa | Alinhar Dockerfile para `python:3.12-slim` + rebuild + full test suite |
| T2-14 | User-Agent hardcoded "BidIQ" em vez de "SmartLic" | Backend | Misleading para provedores de API (PNCP, PCP). | 0.25h | @qa | Update strings em `pncp_client.py` + grep por "BidIQ" |
| T2-16 | 404 page com "Pagina nao encontrada" sem acentos | Frontend | Signal de produto inacabado para decision-maker enterprise. | 0.1h | @ux-design-expert | Visual inspection em `/pagina-inexistente` |
| T2-17 | `global-error.tsx` usa inline styles fora do design system (hardcoded `#f9fafb`, `system-ui`) | Frontend | Quando root layout crasheia, error page parece produto diferente. | 0.5h | @ux-design-expert | Trigger root error + verificar brand match em light/dark |
| T2-18 | Error boundaries faltando para `/pipeline`, `/historico`, `/mensagens`, `/conta` — fall through para root `error.tsx` que expoe raw `error.message` | Frontend | Enterprise user ve `TypeError: Cannot read properties of undefined` em monospace. | 2.0h | @ux-design-expert + @qa | Adicionar error boundaries + trigger error em cada pagina + verificar mensagem amigavel |
| T2-19 | `error.message` nao filtrado por `getUserFriendlyError()` em nenhum dos 4 error boundary files existentes | Frontend | **Issue UX mais danoso para percepcao enterprise.** Raw JS errors visiveis ao usuario. Funcao existe e e usada em 27 files — mas NAO nos error boundaries. | 1.0h | @ux-design-expert + @qa | Import + apply `getUserFriendlyError()` nos 4 error boundaries + trigger errors |

### Migration SQL — Tier 2

```sql
-- Migration: 20260225120000_standardize_fks_to_profiles.sql
-- Fixes: T2-01, T2-02

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

-- classification_feedback (also adds ON DELETE CASCADE)
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

```sql
-- Migration: 20260225130000_rls_policy_hardening.sql
-- Fixes: T2-05, T2-07, T2-08

BEGIN;

-- T2-05: Scope state transitions INSERT to service_role
DROP POLICY IF EXISTS "Service role can insert transitions" ON search_state_transitions;
CREATE POLICY "Service role can insert transitions" ON search_state_transitions
    FOR INSERT TO service_role WITH CHECK (true);

-- T2-07: profiles service_role ALL policy
DROP POLICY IF EXISTS "profiles_service_all" ON public.profiles;
CREATE POLICY "profiles_service_all" ON public.profiles
    FOR ALL TO service_role USING (true) WITH CHECK (true);

-- T2-08: conversations + messages service_role policies
DROP POLICY IF EXISTS "conversations_service_all" ON conversations;
CREATE POLICY "conversations_service_all" ON conversations
    FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "messages_service_all" ON messages;
CREATE POLICY "messages_service_all" ON messages
    FOR ALL TO service_role USING (true) WITH CHECK (true);

COMMIT;
```

```sql
-- Migration: 20260225140000_add_session_composite_index.sql
-- Fix: T2-09

CREATE INDEX IF NOT EXISTS idx_search_sessions_user_status_created
    ON search_sessions (user_id, status, created_at DESC);
```

### Frontend Fixes — Tier 2

| ID | Arquivo | Mudanca |
|----|---------|---------|
| T2-16 | `frontend/app/not-found.tsx` | Corrigir acentos portugueses nas strings |
| T2-17 | `frontend/app/global-error.tsx` | Substituir inline styles hardcoded por valores do design system + `<style>` tag para dark mode media query |
| T2-18 | Criar `frontend/app/pipeline/error.tsx`, `historico/error.tsx`, `mensagens/error.tsx`, `conta/error.tsx` | Copiar pattern de `buscar/error.tsx` com mensagem contextual em portugues |
| T2-19 | `frontend/app/error.tsx`, `buscar/error.tsx`, `dashboard/error.tsx`, `admin/error.tsx` | Importar e aplicar `getUserFriendlyError()` de `lib/error-messages.ts` no render de `error.message` |
| T2-11 | `frontend/app/components/BottomNav.tsx` | Adicionar focus trap ao drawer overlay |
| T2-13 | `backend/Dockerfile` ou `backend/pyproject.toml` | Alinhar versao Python (3.12-slim ou target 3.11) |
| T2-14 | `backend/pncp_client.py` | Substituir User-Agent "BidIQ" por "SmartLic" |

---

## Cross-Area Risk Matrix

| Risco | Areas | Impacto no Core | Mitigacao |
|-------|-------|-----------------|-----------|
| **Colunas DB missing + Backend code usando** (T1-01/02/03/05/06) | DB + Backend | Em DB fresh: Stripe webhooks falham, `/me` incompleto, analytics crasheia, cancel perde end_date, email unsubscribe escreve no void. **Em producao hoje: funcional.** | Migration unica com `ADD COLUMN IF NOT EXISTS`. Zero risco. |
| **Trigger regression + Onboarding** (T1-07) | DB + Backend + Frontend | Novos usuarios perdem `company`, `sector`, `context_data` no signup. Dados preenchidos no form sao descartados silenciosamente. | T1-07 trigger rewrite. Testar: email signup, Google OAuth, re-signup. |
| **Trigger sem ON CONFLICT + Re-signup** (T1-07) | DB + Auth | Re-signup levanta unique violation. **Bloqueia signup completamente.** | T1-07 inclui `ON CONFLICT (id) DO NOTHING`. |
| **RLS gaps + Dados enterprise** (T2-05/07/08) | DB + Security | T2-05: authenticated pode injetar state transitions. T2-07/08: defense-in-depth. **Risco real baixo.** | RLS policy fixes. |
| **Raw error.message + Error boundary gaps** (T2-18/19) | Frontend + UX | Erro React nao-tratado mostra raw JS error ao usuario. **Risk de percepcao enterprise.** | Error boundaries + `getUserFriendlyError()`. |
| **Trial stats runtime error** (T1-04) | Backend + Frontend | Query tabela inexistente. **Afeta todo trial user.** | 1-line code fix. |
| **FK para auth.users + User deletion** (T2-01/02) | DB | Orphaned rows possiveis. **Probabilidade baixa.** | Repoint FKs + CASCADE. |

---

## Identified Gaps (Awareness — Tier 3)

| Gap | Descricao | Recomendacao |
|-----|-----------|--------------|
| **GAP-01** | Sem mecanismo para detectar migration drift (colunas adicionadas via Dashboard escapam tracking). | CI step que valida schema contra migrations. |
| **GAP-02** | Stripe webhook idempotency sob delivery concorrente — verificar tratamento de unique violation. | Verificar handler. Nao bloqueia monetizacao. |
| **GAP-03** | Sem resultados de load testing. Railway 120s timeout e o failure mode mais provavel sob carga. | Rodar locust test contra staging. |
| **GAP-04** | Email delivery — verificar SPF/DKIM para `smartlic.tech` no Resend. | Verificacao operacional. |
| **GAP-05** | Frontend localStorage plan cache (1hr TTL) — UI pode mostrar plano stale apos Stripe webhook. | Reduzir TTL para 5min ou cache-bust apos checkout. |

---

## Tier 3: ACCEPTED DEBTS (Resumo por Categoria)

| Categoria | Count | Mais Severo | Exemplos |
|-----------|-------|-------------|----------|
| **Architecture** | 8 | Critical | Dual HTTP client (sync+async), dual route mounting, god module search_pipeline.py |
| **Scalability** | 5 | High | In-memory progress tracker, auth cache, Railway 1GB memory, Excel filesystem fallback |
| **Code Organization** | 5 | High | Test files fora de tests/, 100+ markdowns na raiz, `.py.tmp` commitado |
| **CI/CD** | 3 | High | No backend linting in CI, no pre-commit hooks, OpenAPI contract testing |
| **Component Duplication** | 6 | Critical | EmptyState x2, LoadingProgress x2, UFS x4, inline SVGs x200 lines |
| **Design System** | 5 | High | ThemeProvider dual source, mixed icon systems, Shepherd hardcoded classes |
| **Frontend Architecture** | 4 | Critical | SearchForm 40+ props, no state management, no RSC for protected pages |
| **Performance** | 4 | Medium | No CDN, PNCP 50 page limit, no dynamic imports, JSONB correlated subquery |
| **Database Convention** | 8 | Medium | Dual migration numbering, no rollback scripts, trigger naming, array columns |
| **Security** | 3 | Medium | CSP unsafe-inline, service role scope, Google verification token |
| **Testing** | 3 | Medium | Coverage below target, test quarantine growing, snapshot-only API contract |
| **Accessibility** | 4 | Medium | Inline SVGs unlabeled, date picker screen reader, dropdown roles, toast announcements |
| **Other** | 6 | Low | Dead code, deprecated patterns, legacy branding, i18n prep |
| **TOTAL** | **71** | | |

---

## Execution Plan

### Phase A: Tier 1 Fixes (Dia 1 manha — ~3 horas)

| Step | Item | Acao | Dependencia |
|------|------|------|-------------|
| 1 | T1-01/02/03/05/06 | Migration A: `20260225100000_add_missing_profile_columns.sql` | Nenhuma |
| 2 | T1-04 + teste | Code fix: `trial_stats.py` + `test_trial_usage_stats.py` | Nenhuma (paralelo com Step 1) |
| 3 | Validacao | `pytest` full suite | Steps 1+2 |
| 4 | T1-07 | Migration B: `20260225110000_fix_handle_new_user_trigger.sql` | Step 1 (colunas devem existir antes) |
| 5 | Validacao T1-07 | Teste signup: email com metadata, Google OAuth, re-signup, phone normalization | Step 4 |

### Phase B: Tier 2 Fixes (Dia 1 tarde + Dia 2 — ~12 horas)

| Step | Item | Acao | Dependencia |
|------|------|------|-------------|
| 6 | T2-01/02 | Migration C: FK standardization (pre-check orphans!) | Phase A |
| 7 | T2-05/07/08 | Migration D: RLS policy hardening | Nenhuma |
| 8 | T2-09 | Migration E: Composite index | Nenhuma |
| 9 | T2-03 | Migration F: JSONB governance (verificar max size em prod ANTES) | Nenhuma |
| 10 | T2-13 | Alinhar Python version (Dockerfile/pyproject) | Nenhuma |
| 11 | T2-14 | Update User-Agent "BidIQ" -> "SmartLic" | Nenhuma |
| 12 | T2-16 | Fix 404 acentos (5 min) | Nenhuma |
| 13 | T2-19 | `getUserFriendlyError()` em 4 error boundaries | Nenhuma |
| 14 | T2-18 | Criar error boundaries para 4 paginas | Nenhuma |
| 15 | T2-17 | `global-error.tsx` brand alignment | Nenhuma |
| 16 | T2-11 | BottomNav focus trap | Nenhuma |

### Phase C: Verificacao Final

| Check | Como |
|-------|------|
| Backend tests | `pytest` — 100% pass, 0 failures |
| Frontend tests | `npm test` — 100% pass, 0 failures |
| Stripe webhook flow | Subscribe, cancel, payment failure (manual ou staging) |
| Signup flow | Email signup com metadata, Google OAuth, re-signup edge case |
| Trial stats | Verificar pipeline trial value display funcional |
| Error states | Trigger errors em cada pagina protegida — verificar mensagens amigaveis |
| 404 page | Navegar para URL inexistente — verificar acentos corretos |

---

## Regression Risks

### Alto Risco

| Mudanca | O Que Pode Quebrar | Mitigacao |
|---------|--------------------|-----------|
| **T1-07 trigger rewrite** | Se trigger tem syntax error, TODOS os signups falham. | Deploy em staging primeiro. Testar 3 metodos de signup. Manter rollback SQL pronto. |
| **T2-01/02 FK repointing** | Se orphaned data existe, FK creation falha e transaction faz rollback. | Run orphan check ANTES. Usar `NOT VALID` + `VALIDATE` two-phase. |
| **T2-03 JSONB CHECK** | Se entries excedem CHECK limit, constraint nao pode ser adicionada. | Query production max JSONB size antes. Considerar 2MB em vez de 1MB. |

### Medio Risco

| Mudanca | O Que Pode Quebrar | Mitigacao |
|---------|--------------------|-----------|
| **T2-05 INSERT scoping** | Code paths que inserem state transitions sem service_role falham com RLS violation. | Grep por todos INSERT paths de `search_state_transitions`. |
| **CHECK constraints** | Codigo que escreve status fora da CHECK list falha. | Revisar todos code paths que SET `subscription_status`. |

### Baixo Risco

| Mudanca | Mitigacao |
|---------|-----------|
| T1-01/02/03/05/06 (column additions) | `ADD COLUMN IF NOT EXISTS` — idempotente. |
| T1-04 (table name fix) | Atualizar teste simultaneamente. |
| T2-07/08/09 (policies e indexes) | Todos aditivos e idempotentes. |
| T2-16/17/18/19 (frontend fixes) | String replacements e novos arquivos. |

---

## Metrics of Success

| Metrica | Valor Esperado Apos Fixes |
|---------|--------------------------|
| Backend test suite | 5131+ passing, 0 failures |
| Frontend test suite | 2681+ passing, 0 failures |
| Stripe webhook: checkout | Profile `subscription_status` = `active` |
| Stripe webhook: cancel | Profile `subscription_end_date` preenchido |
| New signup (email) | Profile contem company, sector, whatsapp_consent |
| New signup (Google OAuth) | Profile contem full_name, avatar_url |
| Trial stats endpoint | Retorna dados de `pipeline_items` sem erro |
| Error boundaries | Nenhuma pagina protegida mostra raw `error.message` |
| 404 page | Texto com acentos corretos em portugues |
| UX Enterprise Score | 4.0+/5 (de 3.7/5 atual) |

---

## Total Investment

| Categoria | Horas |
|-----------|-------|
| Tier 1: Blocking (7 items) | 3h |
| Tier 2: Stability — DB (8 items) | 4h |
| Tier 2: Stability — Backend (2 items) | 0.75h |
| Tier 2: Stability — Frontend (4 items) | 5.1h |
| Teste e verificacao | 2h |
| **TOTAL** | **~15h (~2 dias de trabalho)** |

**ROI:** 15 horas de investimento -> sistema enterprise-ready para monetizacao confiavel em todos os 6 core flows.

---

*Gerado por @architect durante Fase 8 do SmartLic Brownfield Discovery.*
*Validado por: @data-engineer (Fase 5), @ux-design-expert (Fase 6), @qa (Fase 7 — APPROVED).*
*Cross-references: system-architecture.md, SCHEMA.md, DB-AUDIT.md, frontend-spec.md, db-specialist-review.md, ux-specialist-review.md, qa-review.md.*
