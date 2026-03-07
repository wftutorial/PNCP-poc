# HARDEN-008: Cache Invalidation Imediata no Stripe Webhook

**Severidade:** ALTA
**Esforço:** 15 min
**Quick Win:** Sim
**Origem:** Conselho CTO — Auditoria de Fragilidades (2026-03-06)

## Contexto

Stripe webhook atualiza `profiles.plan_type` mas não limpa `_plan_status_cache` em `quota.py`. Usuário mantém quota do plano antigo por até 5 min (TTL do cache). Permite quota bypass após plan downgrade.

## Critérios de Aceitação

- [x] AC1: Webhook handler limpa `_plan_status_cache[user_id]` após update
- [x] AC2: `clear_plan_capabilities_cache()` chamado no webhook
- [x] AC3: Teste unitário valida invalidação no downgrade
- [x] AC4: Teste unitário valida invalidação no upgrade
- [x] AC5: Zero regressions

## Arquivos Afetados

- `backend/webhooks/stripe.py` — handlers de subscription
- `backend/quota.py` — expor função de invalidação por user_id
- `backend/tests/` — novos testes
