# DEBT-114: Billing Legacy Cleanup — stripe_price_id

**Prioridade:** GTM-RISK (30 dias)
**Estimativa:** 4h
**Fonte:** Brownfield Discovery — @data-engineer (DB-013)
**Score Impact:** Billing 8→9

## Contexto
`plans.stripe_price_id` está marcado como DEPRECATED mas billing.py ainda usa como fallback. Source of truth é `plan_billing_periods.stripe_price_id` desde STORY-360.

## Acceptance Criteria

- [ ] AC1: billing.py usa APENAS plan_billing_periods para buscar stripe_price_id (remover fallback para plans.stripe_price_id)
- [ ] AC2: WARNING log adicionado se código legado for acessado (safety net por 1 semana)
- [ ] AC3: Todos os testes de billing passam (test_billing.py, test_stripe_webhook.py, test_payment_failed_webhook.py)
- [ ] AC4: Smoke test manual: criar checkout session via /planos funciona
- [ ] AC5: Após 1 semana sem WARNING logs, criar follow-up migration para DROP COLUMN plans.stripe_price_id

## File List
- [ ] `backend/routes/billing.py` (EDIT)
- [ ] `backend/services/billing.py` (EDIT — se existir)
