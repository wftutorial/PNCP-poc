# STORY-285: Webhook Idempotency Race Condition Fix

**Priority:** P1
**Effort:** S (0.5 day)
**Squad:** @dev
**Fundamentacao:** GTM Readiness Audit Track 3 (Billing) — race condition no idempotency check
**Status:** TODO
**Sprint:** GTM Sprint 1

---

## Contexto

O webhook handler do Stripe em `backend/webhooks/stripe.py` (lines 110-146) tem uma race condition no idempotency check. O SELECT e o INSERT sao operacoes separadas — se dois deliveries identicos chegarem simultaneamente, ambos passam o SELECT antes de qualquer INSERT, resultando em processamento duplicado ou erro de unique constraint.

---

## Acceptance Criteria

### AC1: Atomic idempotency check
- [ ] Substituir SELECT-then-INSERT por INSERT-first com `ON CONFLICT DO NOTHING`
- [ ] Verificar resultado do INSERT: se `count == 0`, evento ja processado → retornar early
- [ ] Se `count == 1`, evento novo → processar normalmente
- [ ] Alternativa aceita: `SELECT ... FOR UPDATE` dentro de transaction

### AC2: Handle unique constraint gracefully
- [ ] Se INSERT falhar por unique constraint (edge case), retornar `{"status": "already_processed"}` com HTTP 200
- [ ] Nunca retornar HTTP 500 para eventos duplicados

### AC3: Testes
- [ ] Teste unitario: dois eventos com mesmo ID processados sequencialmente → segundo retorna "already_processed"
- [ ] Teste unitario: verificar que apenas um webhook handler executa a logica de negocio
- [ ] Teste existente de idempotency continua passando

---

## Arquivos Impactados

| Arquivo | Mudanca |
|---------|---------|
| `backend/webhooks/stripe.py` | Atomic idempotency check (lines 110-146) |
| `backend/tests/` | Novos testes de race condition |
