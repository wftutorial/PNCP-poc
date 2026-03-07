# HARDEN-028: Stripe Webhook Events Purge (90 dias)

**Severidade:** BAIXA
**Esforço:** 10 min
**Quick Win:** Nao
**Origem:** Conselho CTO — Auditoria de Fragilidades (2026-03-06)

## Contexto

Cada webhook event é salvo em `stripe_webhook_events` para idempotency/audit, mas não há purge. Tabela cresce indefinidamente — bloat de DB, queries lentas, custo de storage.

## Critérios de Aceitação

- [ ] AC1: Cron job (ou Supabase scheduled function) deleta eventos > 90 dias
- [ ] AC2: Roda diariamente
- [ ] AC3: Log count de eventos deletados
- [ ] AC4: Teste unitário

## Arquivos Afetados

- `backend/cron_jobs.py` — novo cleanup job
- Ou: `supabase/migrations/` — pg_cron schedule
