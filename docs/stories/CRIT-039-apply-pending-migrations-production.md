# CRIT-039: Aplicar Migrações Pendentes em Produção

**Epic:** Production Stability
**Sprint:** Hotfix
**Priority:** P0 — CRITICAL
**Story Points:** 3 SP
**Estimate:** 1-2 horas
**Owner:** @devops + @data-engineer

---

## Problem

5 migrações locais não foram aplicadas ao Supabase de produção, causando erros PGRST205 em cascata:

- `health_checks` table ausente → health canary falha → CB abre → cascade de erros
- `incidents` table ausente → incident detection falha
- `alerts` table ausente → `/v1/alerts` retorna 500
- `profiles.marketing_emails_enabled` coluna ausente → trial email sequence falha (error 42703)

**Impacto:** Esses erros PGRST205 são contados como falhas pelo Supabase Circuit Breaker, que abre e bloqueia TODAS as operações Supabase (cache refresh, trial reminders, trial emails). Na última janela de 24h: 86 eventos de erro no Sentry, todos rastreáveis a tabelas/colunas ausentes.

**Root cause:** Migrações foram comitadas mas nunca aplicadas via `supabase db push`.

---

## Migrações Pendentes

| # | Arquivo | O que cria |
|---|---------|-----------|
| 1 | `20260227100000_create_alerts.sql` | Tabelas `alerts` + `alert_sent_items` |
| 2 | `20260227120001_concurrency_stripe_webhook.sql` | Colunas `status` + `received_at` em `stripe_webhook_events` |
| 3 | `20260227120002_concurrency_pipeline_version.sql` | Coluna `version` em `pipeline_items` |
| 4 | `20260227120003_concurrency_quota_rpc.sql` | Função `increment_quota_fallback_atomic()` |
| 5 | `20260227120004_concurrency_quota_rpc_grant.sql` | GRANT EXECUTE na função acima |
| 6 | `20260227140000_story310_trial_email_sequence.sql` | Coluna `profiles.marketing_emails_enabled` + tabela `trial_emails_sent` |
| 7 | `20260228150000_add_health_checks_table.sql` | Tabela `health_checks` |
| 8 | `20260228150001_add_incidents_table.sql` | Tabela `incidents` |
| 9 | `20260228160000_add_mfa_recovery_codes.sql` | Tabela `mfa_recovery_codes` |

---

## Acceptance Criteria

### Pré-aplicação

- [ ] **AC1:** Fazer backup Point-in-Time do Supabase (PITR snapshot) antes de aplicar
- [ ] **AC2:** Executar `supabase db diff` para validar estado atual vs migrações
- [ ] **AC3:** Confirmar que NENHUMA migração contém `DROP` ou `ALTER ... DROP COLUMN`

### Aplicação

- [ ] **AC4:** Aplicar migrações via `supabase db push` em sequência:
  - Aplicar uma por uma se `db push` falhar no batch
  - Usar `supabase migration repair --status applied` se alguma já estiver parcialmente aplicada
- [ ] **AC5:** Após cada batch, executar `NOTIFY pgrst, 'reload schema';` via SQL editor para forçar PostgREST cache refresh
- [ ] **AC6:** Verificar via `supabase db diff` que todas as migrações foram aplicadas

### Validação Pós-aplicação

- [ ] **AC7:** Verificar nos logs Railway que erros PGRST205 pararam (health_checks, incidents, alerts, marketing_emails_enabled)
- [ ] **AC8:** Verificar que Supabase CB permanece CLOSED (log: `Supabase circuit breaker: OPEN → CLOSED` ou ausência de OPEN transitions)
- [ ] **AC9:** Verificar que `GET /v1/alerts` retorna 200 (não 500)
- [ ] **AC10:** Verificar que trial email sequence roda sem erro 42703

---

## Riscos

- Migrações com `IF NOT EXISTS` são seguras para re-execução
- `concurrency_safety` original foi splitada em 4 arquivos separados — não tentar aplicar o arquivo original
- Após aplicação, PostgREST cache pode levar até 60s para atualizar — usar `NOTIFY pgrst` para forçar

---

## Referências

- [Supabase DB Migrations docs](https://supabase.com/docs/guides/deployment/database-migrations)
- [PostgREST PGRST205 schema cache](https://supabase.com/docs/guides/api/rest/postgrest-error-codes)
- MEMORY.md: "Pending migration: `20260227120000_concurrency_safety.sql` fails on multi-statement (needs split)"
