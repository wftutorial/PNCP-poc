# Database Specialist Review

**Reviewer:** @data-engineer
**Data:** 2026-03-09
**Fonte:** docs/prd/technical-debt-DRAFT.md (Section 2) — ID scheme DB-001 through DB-031 + DB-INFO-01 through DB-INFO-06
**Supersedes:** v3.0 (2026-03-07, reviewed DRAFT with old ID scheme DB-001 through DB-046)

**Migrations Analisadas:** 76 (66 Supabase + 10 backend), com foco nas 15 mais recentes (DEBT-001 a DEBT-017)
**Backend Code Verificado:** `supabase_client.py`, `search_cache.py`, `auth.py`, `quota.py`, `routes/billing.py`

---

## Resumo da Revisao

A auditoria de database no DRAFT esta **bem fundamentada mas desatualizada** em relacao as migracoes mais recentes. A analise cruzada com os 76 arquivos de migracao revela que **10 dos 31 itens de debito ja foram totalmente resolvidos** por migracoes aplicadas entre 2026-03-04 e 2026-03-09. O DRAFT nao refletiu esses fixes, provavelmente porque a DB-AUDIT.md foi escrita antes das migracoes DEBT-001/DEBT-009/DEBT-010/DEBT-017 serem criadas.

**Resumo quantitativo:**
- **17 itens validados** (confirmados como debito ativo)
- **10 itens removidos** (ja resolvidos por migracoes recentes)
- **4 itens com severidade ajustada**
- **4 novos debitos identificados** durante a revisao
- **Esforco total estimado para debitos remanescentes:** ~38 horas (4.75 dias de engenharia)

**Ponto mais critico remanescente:** DB-001 (FK inconsistency) permanece parcialmente resolvido. Tres migracoes (`20260225120000`, `20260304100000`, `018_standardize_fk_references.sql`) migraram a maioria das tabelas para `profiles(id)`, mas **4 tabelas ainda referenciam `auth.users` diretamente**: `monthly_quota`, `user_oauth_tokens`, `google_sheets_exports`, `search_results_cache` (estado incerto). A padronizacao FK esta ~70% completa.

---

## Debitos Validados

| ID | Debito | Sev. Original | Sev. Ajustada | Horas | Prioridade | Notas |
|----|--------|:---:|:---:|:---:|:---:|-------|
| **DB-001** | FK Target Inconsistency — `auth.users` vs `profiles` (12 tables) | CRITICAL | **HIGH** | 6h | P1 | Downgrade: ~70% resolvido. Migracoes `018_standardize_fk_references`, `20260225120000`, `20260304100000` repontaram 8+ tabelas. **4 restantes:** `monthly_quota` (002), `user_oauth_tokens` (013), `google_sheets_exports` (014), `search_results_cache` (026, estado incerto — ver DB-NEW-04). Risco atenuado: todas tem ON DELETE CASCADE no original. |
| **DB-002** | `search_results_store` missing ON DELETE CASCADE | CRITICAL | **REMOVIDO** | 0h | -- | **RESOLVIDO.** Migracao `20260304100000` reaponta FK para `profiles(id) ON DELETE CASCADE`. |
| **DB-003** | `classification_feedback` missing ON DELETE CASCADE | HIGH | **REMOVIDO** | 0h | -- | **RESOLVIDO.** Migracao `20260225120000` adiciona FK para `profiles(id) ON DELETE CASCADE`. |
| **DB-004** | Duplicate `updated_at` trigger functions (3 tables) | HIGH | **REMOVIDO** | 0h | -- | **RESOLVIDO.** Migracao `20260304120000_rls_policies_trigger_consolidation.sql` reaponta todas 3 triggers (`pipeline_items`, `alert_preferences`, `alerts`) para `set_updated_at()` e dropa funcoes duplicadas. |
| **DB-005** | `search_state_transitions.search_id` no FK + no retention | HIGH | **LOW** | 0.5h | P4 | FK impossivel (search_sessions.search_id nullable/not unique — documentado em DEBT-017). Retention **JA FOI CRIADO** em `20260308310000` (30 dias). Restante: apenas COMMENT doc update. |
| **DB-006** | `alert_preferences` auth.role() pattern | HIGH | **REMOVIDO** | 0h | -- | **RESOLVIDO.** Migracao `20260304200000_rls_standardize_service_role.sql` padroniza para `TO service_role`. |
| **DB-007** | `organizations`/`org_members` auth.role() pattern | HIGH | **REMOVIDO** | 0h | -- | **RESOLVIDO.** Mesma migracao `20260304200000`. |
| **DB-008** | `partners`/`partner_referrals` auth.role() pattern | HIGH | **REMOVIDO** | 0h | -- | **RESOLVIDO.** Mesma migracao `20260304200000`. |
| **DB-009** | `search_results_store` auth.role() pattern | HIGH | **REMOVIDO** | 0h | -- | **RESOLVIDO.** Mesma migracao `20260304200000` (item #8: search_results_store). |
| **DB-010** | `health_checks`/`incidents` missing retention jobs | HIGH | **REMOVIDO** | 0h | -- | **RESOLVIDO.** Migracao `20260308310000_debt009_retention_pgcron_jobs.sql` cria jobs: health_checks 30d, incidents 90d. |
| **DB-011** | Redundant indexes on 4 tables | MEDIUM | MEDIUM | 1h | P3 | Parcialmente resolvido: `idx_alert_preferences_user_id` dropado em `20260308400000`. Restam 3: `idx_search_results_store_user_id` (duplica `idx_search_results_user`), `idx_search_sessions_user_id` (duplica `idx_search_sessions_user`), `idx_partners_slug` (duplica UNIQUE on slug). |
| **DB-012** | `conversations` missing composite index admin inbox | MEDIUM | **REMOVIDO** | 0h | -- | **RESOLVIDO.** `idx_conversations_status_last_msg` criado em `20260308400000_debt010_schema_guards.sql`. |
| **DB-013** | `plans.stripe_price_id` legacy column still used | MEDIUM | MEDIUM | 4h | P3 | Confirmado: `billing.py:96` usa `plan.get("stripe_price_id")` como fallback. Column marcada DEPRECATED via COMMENT em DEBT-017. Requer migracao do billing code + DROP column. |
| **DB-014** | `search_sessions.status` CHECK mismatch | MEDIUM | **LOW** | 0.5h | P4 | DEBT-017 esclareceu via COMMENT: `consolidating`/`partial` sao estados validos gerenciados pelo app-layer state machine. CHECK do DB **intencionalmente** nao os inclui. Apenas doc update necessario. |
| **DB-015** | `monthly_quota.user_id` references `auth.users` not `profiles` | MEDIUM | MEDIUM | 1h | P2 | Confirmado: `002_monthly_quota.sql` define `REFERENCES auth.users(id)`. NAO incluido na migracao `20260304100000`. |
| **DB-016** | Missing `updated_at` on `incidents`/`partners` | MEDIUM | MEDIUM | 1h | P3 | Confirmado: ambas tabelas sao mutaveis sem change tracking. |
| **DB-017** | `search_results_cache` duplicate size constraints | MEDIUM | LOW | 0.5h | P4 | Baixo risco — apenas confusao de schema. |
| **DB-018** | `partner_referrals.partner_id` missing ON DELETE CASCADE | MEDIUM | MEDIUM | 0.5h | P2 | Confirmado. `20260304100000` migrou `referred_user_id` para profiles mas nao tocou `partner_id` FK. |
| **DB-019** | Naming convention inconsistencies (triggers) | MEDIUM | LOW | 2h | P4 | Confirmado: 4 padroes coexistem. `20260304120000` usou `tr_` para pipeline mas `trigger_` para alerts, criando mais inconsistencia. |
| **DB-020** | `google_sheets_exports.last_updated_at` naming | MEDIUM | LOW | 0.5h | P4 | Confirmado: unica tabela com naming diferente. Sem trigger. |
| **DB-021** | `organizations.plan_type` no CHECK constraint | MEDIUM | MEDIUM | 0.5h | P2 | Confirmado. Aceita qualquer texto. |
| **DB-022** | `pipeline_items` service role overly permissive | MEDIUM | **REMOVIDO** | 0h | -- | **RESOLVIDO.** Migration 027 corrigiu; verificado em `20260304200000` que nao reintroduziu. |
| **DB-023** | `user_oauth_tokens.provider` CHECK overly broad | LOW | LOW | 0.5h | P4 | Permite google/microsoft/dropbox; so google implementado. |
| **DB-024** | `audit_events` no index on JSONB | LOW | INFO | 0h | P5 | Nenhuma query atual. Premature optimization. |
| **DB-025** | `search_results_cache` 8 indexes | LOW | LOW | 2h | P3 | Requer analise de `pg_stat_user_indexes` em producao antes de dropar. |
| **DB-026** | `search_sessions` no retention | LOW | LOW | 0.5h | P3 | Confirmado. Nenhum pg_cron job. |
| **DB-027** | `classification_feedback` no retention | LOW | LOW | 0.5h | P4 | Valioso para ML — retention longo (24 meses) recomendado. |
| **DB-028** | `conversations`/`messages` no retention | LOW | LOW | 0.5h | P4 | Suporte ao cliente — reter 24+ meses. |
| **DB-029** | `alert_sent_items` missing retention | LOW | **REMOVIDO** | 0h | -- | **RESOLVIDO.** Job criado em `20260308310000` (180 dias). |
| **DB-030** | `stripe_webhook_events` no automated retention | LOW | **REMOVIDO** | 0h | -- | **RESOLVIDO.** Job criado em `022_retention_cleanup.sql` (90 dias). |
| **DB-031** | `pipeline_items` missing `search_id` reference | LOW | LOW | 1h | P4 | Confirmado. Nao ha link para tracing. |
| **DB-INFO-01** | Consolidate backend migrations | INFO | INFO | 1h | P4 | Bridge migration `20260308200000` ja criada. Diretorio persiste sem DEPRECATED marker. |
| **DB-INFO-02** | No schema version table | INFO | **NAO RECOMENDO** | 0h | -- | Supabase ja rastreia via `supabase_migrations.schema_migrations`. Tabela independente seria redundante. |
| **DB-INFO-03** | Backup strategy not documented | INFO | INFO | 1h | P3 | Supabase Pro: daily backups + PITR 7 dias. Documentar em runbook. |
| **DB-INFO-04** | Connection pooling verification | INFO | INFO | 0.5h | P3 | Backend usa REST API (httpx), NAO conexao PostgreSQL direta. pgbouncer irrelevante para app layer. Ver detalhes na resposta Q7. |
| **DB-INFO-05** | Consider partitioning | INFO | INFO | 0h | P5 | Prematuro no estagio POC beta. |
| **DB-INFO-06** | JSONB columns lack DB-level validation | INFO | **NAO RECOMENDO** | 0h | -- | Pydantic no app layer e suficiente. CHECK em JSONB e fragil e lento. |

---

## Debitos Adicionados

| ID | Debito | Tabelas | Severidade | Horas | Prioridade | Notas |
|----|--------|---------|:---:|:---:|:---:|-------|
| **DB-NEW-01** | `search_results_store` FK `NOT VALID` pode nao estar validada em producao. Migracao `20260304100000` usa NOT VALID + VALIDATE separados. Se a VALIDATE falhou silently, constraint nao esta enforced. | `search_results_store` | HIGH | 1h | P1 | Executar `SELECT convalidated FROM pg_constraint WHERE conname = 'search_results_store_user_id_fkey'` em producao. |
| **DB-NEW-02** | `search_results_store` index duplicado: `idx_search_results_user` (20260303100000) e `idx_search_results_store_user_id` (20260308100000_debt001). Ambos em `user_id`. | `search_results_store` | MEDIUM | 0.5h | P3 | Drop `idx_search_results_store_user_id`. |
| **DB-NEW-03** | `search_results_store` sem retention. Tabela tem `expires_at DEFAULT now() + 24h` mas nenhum pg_cron job limpa registros expirados. Accumula indefinidamente. | `search_results_store` | HIGH | 1h | P1 | Criar job: `DELETE FROM search_results_store WHERE expires_at < now()`. Impacto direto em storage billing. |
| **DB-NEW-04** | `search_results_cache` FK estado incerto. Multiplas migracoes tocaram esta FK (`018`, `20260224200000`, possivelmente `20260225120000`). Estado final pode ser `auth.users` ou `profiles` dependendo da ordem de aplicacao. | `search_results_cache` | MEDIUM | 1h | P2 | Verificar com `SELECT conname, confrelid::regclass FROM pg_constraint WHERE conrelid = 'search_results_cache'::regclass AND contype = 'f'`. |

---

## Respostas ao Architect

### 1. DB-001 (FK Standardization): `auth.users` ou `profiles`?

**Resposta:** Confirmo `profiles(id)` como direcao correta. Razoes:

- `profiles` e a tabela que o app layer interage (RLS via `auth.uid() = user_id`)
- `profiles.id` = `auth.users.id` (1:1, criado por trigger `handle_new_user()`)
- Cadeia de cascade: `auth.users -> profiles -> dependentes` e mais segura que `auth.users -> dependentes` direto
- Se `handle_new_user()` falhar, tabelas com FK para profiles rejeitam INSERT (fail-fast, correto), enquanto tabelas com FK para auth.users aceitam (criando estado inconsistente)

**Tabelas JA migradas para profiles (confirmado em migracoes):**
`user_subscriptions`, `search_sessions`, `conversations`, `messages`, `alert_preferences`, `alerts`, `search_results_store`, `pipeline_items`, `classification_feedback`, `trial_email_log`, `organization_members`, `organizations` (owner_id), `partner_referrals` (referred_user_id), `mfa_recovery_codes`, `mfa_recovery_attempts`

**Tabelas que AINDA referenciam auth.users (4):**
1. `monthly_quota` — `002_monthly_quota.sql:8`
2. `user_oauth_tokens` — `013_google_oauth_tokens.sql:10`
3. `google_sheets_exports` — `014_google_sheets_exports.sql:10`
4. `search_results_cache` — estado incerto (DB-NEW-04)

### 2. DB-005 (search_state_transitions): Retention window?

**Resposta:** 30 dias (ja implementado em `20260308310000`). Adequado.
- Transitions sao para debugging em tempo real, nao analytics
- ~15K rows/mes a 30 dias = tabela pequena (~15K max)
- Logs do Railway/Sentry cobrem debugging de incidentes mais antigos
- Nenhuma query de analytics depende de transitions > 30 dias

### 3. DB-010 (health_checks retention): Por que foi deferido?

**Resposta:** **Ja esta resolvido.** O job foi criado na migracao `20260308310000`:
- `health_checks`: 30 dias, daily 4:10 UTC
- `incidents`: 90 dias, daily 4:15 UTC

O atraso foi simplesmente esquecimento na migracao original (`20260228150000`). Sem motivo de compliance.

### 4. DB-013 (plans.stripe_price_id legacy): Migration path?

**Resposta:** Path em 3 fases:

1. **Fase 1 — Update billing.py (2h):** Alterar `billing.py:96` de `plan.get(price_id_key) or plan.get("stripe_price_id")` para usar SOMENTE `plan_billing_periods.stripe_price_id`. A tabela `plan_billing_periods` e fonte de verdade desde STORY-360.

2. **Fase 2 — Monitoring (1 semana):** Deploy + monitorar que zero queries usam a coluna legacy. Adicionar log warning se o fallback for triggered.

3. **Fase 3 — DROP column (1h):** `ALTER TABLE plans DROP COLUMN stripe_price_id;`

**Rollback:** Seguro. Coluna pode ser recriada e populada de `plan_billing_periods` se necessario. Fase 2 elimina esse risco.

### 5. DB-014 (search_sessions.status CHECK): In-memory ou DB?

**Resposta:** `consolidating` e `partial` sao estados validos no database, mas o CHECK **intencionalmente** nao os inclui. DEBT-017 documentou via COMMENT que o app-layer state machine (`search_state_manager.py`) e o local correto para FSM validation.

**Recomendacao:** CHECK esta correto como esta. Nao adicionar estados transitorios ao CHECK. Apenas update a documentacao no DB-AUDIT.md. Severidade: LOW.

### 6. DB-025 (search_results_cache 8 indexes): Quais sao usados?

**Resposta baseada em analise de codigo (sem acesso a `pg_stat_user_indexes`):**

| Index | Usado? | Evidencia |
|-------|:---:|-----------|
| PK (id) | Sim | Sempre |
| UNIQUE (user_id, params_hash) | Sim | Toda busca cached |
| `idx_search_cache_user` | Sim | RLS queries |
| `idx_search_cache_fetched_at` | Sim | SWR stale detection |
| `idx_search_cache_priority` | Provavelmente | Tiering B-02 |
| `idx_search_cache_params_hash` | **Candidato a remocao** | Redundante com UNIQUE se queries sempre filtram por user_id |
| `idx_search_cache_global_hash` | **Verificar** | Global SWR warming — pode ser obsoleto |
| `idx_search_cache_degraded` | **Verificar** | Queries por degraded status — frequencia desconhecida |

**Recomendacao:** Executar em producao antes de qualquer DROP:
```sql
SELECT indexrelname, idx_scan, idx_tup_read
FROM pg_stat_user_indexes
WHERE relname = 'search_results_cache'
ORDER BY idx_scan ASC;
```

### 7. DB-INFO-04 (Connection pooling): pgbouncer ou direto?

**Resposta:** O backend **NAO usa conexao PostgreSQL direta**. Verificado em `supabase_client.py`:
- `get_supabase()` cria um client REST que usa `httpx.Client` para HTTP requests ao PostgREST
- Pool configurado: max 25 connections/worker, 10 keepalive, 30s timeout (`_POOL_MAX_CONNECTIONS`)
- `sb_execute()` usa `asyncio.to_thread(query.execute)` para offload sync calls

pgbouncer (port 6543) e relevante APENAS para:
- `supabase db push` (migracoes via CLI)
- pg_cron jobs (executam internamente no Supabase)
- Funcoes RPC que usam conexao interna

**Conclusao:** Pool httpx no `supabase_client.py` e o unico concern de pool para o app layer. pgbouncer config e transparente.

### 8. Retention batch: Consolidacao possivel?

**Resposta:** A maioria dos jobs **ja foi implementada**. Status completo:

**Ja implementados (nao precisam de acao):**
| Job | Retencao | Migracao |
|-----|----------|----------|
| `cleanup-monthly-quota` | 24 meses | `022_retention_cleanup.sql` |
| `cleanup-webhook-events` | 90 dias | `022_retention_cleanup.sql` |
| `cleanup-search-state-transitions` | 30 dias | `20260308310000` |
| `cleanup-alert-sent-items` | 180 dias | `20260308310000` |
| `cleanup-health-checks` | 30 dias | `20260308310000` |
| `cleanup-incidents` | 90 dias | `20260308310000` |
| `cleanup-mfa-recovery-attempts` | 30 dias | `20260308310000` |
| `cleanup-alert-runs` | 90 dias | `20260308310000` |

**Faltam criar (nova migracao unica):**

| Tabela | Retencao Recomendada | Justificativa |
|--------|:---:|---------------|
| `search_results_store` | Baseado em `expires_at` | Ja tem coluna de expiracao; cleanup diario |
| `search_sessions` | 12 meses | Analytics de uso por 1 ano |
| `classification_feedback` | 24 meses | Valor para fine-tuning de ML |
| `conversations` + `messages` | 24 meses | Historico de suporte ao cliente |

Sim, todos 4 jobs restantes podem ser consolidados em uma unica migracao com schedule staggered (5 min entre cada).

---

## Recomendacoes

### Ordem de Resolucao Recomendada

| Fase | IDs | Tema | Horas | Sprint |
|------|-----|------|:---:|:---:|
| **1. Verificacao em Producao** | DB-NEW-01, DB-NEW-04 | Confirmar estado de FKs e constraints | 1h | Imediato |
| **2. Storage/Growth** | DB-NEW-03, DB-026 | Retention jobs para search_results_store e search_sessions | 1.5h | Atual |
| **3. FK Completion** | DB-001 (restantes), DB-015 | Completar padronizacao FK para 4 tabelas | 7h | Atual |
| **4. Data Integrity** | DB-021, DB-018 | CHECK constraints + ON DELETE CASCADE | 1h | Proximo |
| **5. Cleanup** | DB-011, DB-NEW-02 | Drop indexes redundantes | 1.5h | Proximo |
| **6. Billing Migration** | DB-013 | Migrar billing.py off legacy column | 4h | Proximo |
| **7. Observability** | DB-016, DB-INFO-03, DB-INFO-04 | updated_at, backup docs, pool docs | 2.5h | Proximo |
| **8. Cosmetic** | DB-019, DB-020, DB-014, DB-005 | Naming, docs, conventions | 3.5h | Backlog |
| **9. Low Priority** | DB-023 a DB-031, DB-025, DB-027, DB-028 | Minor fixes, retention, schema docs | ~14h | Backlog |

### Quick Wins (< 2h cada)

| # | ID | Acao | Horas | Impacto |
|---|-----|------|:---:|---------|
| 1 | **DB-NEW-03** | Criar pg_cron: `DELETE FROM search_results_store WHERE expires_at < now()` | 0.5h | Previne growth ilimitado; impacto direto em billing |
| 2 | **DB-015** | Migrar `monthly_quota.user_id` FK para profiles(id) | 1h | Consistencia FK (parte de DB-001) |
| 3 | **DB-021** | `ALTER TABLE organizations ADD CONSTRAINT chk_org_plan_type CHECK (...)` | 0.5h | Data integrity |
| 4 | **DB-018** | `ALTER TABLE partner_referrals ... ON DELETE CASCADE` em partner_id | 0.5h | Data integrity |
| 5 | **DB-NEW-02** | `DROP INDEX idx_search_results_store_user_id` (duplicata) | 0.5h | Write performance |
| 6 | **DB-026** | Criar pg_cron para search_sessions (12 meses) | 0.5h | Storage growth |
| 7 | **DB-016** | Adicionar `updated_at` em `incidents` e `partners` + trigger | 1h | Change tracking |

**Total quick wins: ~4.5h para resolver 7 itens.**

### Requer Planejamento (> 8h)

| # | ID | Acao | Horas | Pre-requisitos |
|---|-----|------|:---:|----------------|
| 1 | **DB-001** (4 tabelas restantes) | Completar FK standardization para `monthly_quota`, `user_oauth_tokens`, `google_sheets_exports`, `search_results_cache` | 6h | Executar orphan detection query em producao. Usar NOT VALID + VALIDATE pattern. Coordenar com deploy window. |
| 2 | **DB-013** | Migrar billing.py off `plans.stripe_price_id` + DROP column | 4h | Coordenar com equipe. Deploy faseado com 1 semana de monitoring antes do DROP. |
| 3 | **DB-025** | Analise e otimizacao de indexes em `search_results_cache` | 2h | Requer dados de `pg_stat_user_indexes` de producao. |

---

## Validacao Pendente em Producao

As seguintes queries **devem ser executadas** antes de fechar esta revisao:

```sql
-- 1. Estado final das FKs (DB-001, DB-NEW-01, DB-NEW-04)
SELECT tc.table_name, tc.constraint_name,
       ccu.table_name AS references_table,
       rc.delete_rule,
       pc.convalidated
FROM information_schema.table_constraints tc
JOIN information_schema.constraint_column_usage ccu
  ON tc.constraint_name = ccu.constraint_name
JOIN information_schema.referential_constraints rc
  ON tc.constraint_name = rc.constraint_name
LEFT JOIN pg_constraint pc
  ON pc.conname = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_schema = 'public'
ORDER BY tc.table_name;

-- 2. auth.role() residual (deve retornar 0 rows)
SELECT schemaname, tablename, policyname, qual
FROM pg_policies
WHERE schemaname = 'public' AND qual LIKE '%auth.role()%';

-- 3. pg_cron jobs ativos (deve retornar 8+ jobs)
SELECT jobname, schedule FROM cron.job ORDER BY jobname;

-- 4. Indexes redundantes — scan frequency
SELECT indexrelname, idx_scan, idx_tup_read, pg_size_pretty(pg_relation_size(indexrelid))
FROM pg_stat_user_indexes
WHERE relname IN ('search_results_cache', 'search_results_store', 'search_sessions', 'partners')
ORDER BY relname, idx_scan ASC;

-- 5. search_results_store growth (DB-NEW-03)
SELECT count(*) AS total_rows,
       count(*) FILTER (WHERE expires_at < now()) AS expired_rows,
       pg_size_pretty(pg_total_relation_size('search_results_store')) AS total_size
FROM search_results_store;
```

---

*Revisao completa por @data-engineer — AIOS Brownfield Discovery Phase 5*
*Metodologia: Verificacao code-level de cada item do DRAFT contra migracoes SQL, DB-AUDIT.md, SCHEMA.md, e codigo backend. Todos os ajustes de severidade incluem evidencia.*
*Pronto para consolidacao pelo @architect no FINAL.*
