---
task: "Audit Webhook Reliability"
responsavel: "@billing-auditor"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - backend/webhooks/stripe.py
  - Stripe webhook event types
Saida: |
  - Webhook handler coverage
  - Signature verification check
  - Idempotency validation
Checklist:
  - "[ ] checkout.session.completed handled"
  - "[ ] customer.subscription.updated handled"
  - "[ ] customer.subscription.deleted handled"
  - "[ ] invoice.payment_failed handled"
  - "[ ] invoice.paid handled"
  - "[ ] Signature verification enabled"
  - "[ ] Idempotency: duplicates safe"
  - "[ ] Fail-to-last-plan policy enforced"
---

# *audit-webhooks

Validate Stripe webhook handlers for reliability and completeness.

## Steps

1. Read `backend/webhooks/stripe.py` — list all handled events
2. Verify signature verification (webhook secret)
3. Check idempotency handling (duplicate events)
4. Verify "fail to last known plan" policy
5. Check error handling (webhook failures don't crash server)

## Critical: "Fail to Last Known Plan"

On any DB error during webhook processing, the system MUST NOT default to free_trial. It should keep the last known valid plan.

## Output

Score (0-10) + handler coverage + reliability assessment
