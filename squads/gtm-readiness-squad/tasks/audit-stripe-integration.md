---
task: "Audit Stripe Integration"
responsavel: "@billing-auditor"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - backend/services/billing.py
  - backend/webhooks/stripe.py
  - backend/routes/billing.py
Saida: |
  - Stripe integration health check
  - Checkout flow validation
  - Webhook handler review
Checklist:
  - "[ ] Stripe API key is live mode"
  - "[ ] Products and prices exist in Stripe"
  - "[ ] Checkout session creates correctly"
  - "[ ] Customer portal accessible"
  - "[ ] Proration handled by Stripe"
  - "[ ] Invoice dunning configured"
---

# *audit-stripe

Validate Stripe integration end-to-end.

## Steps

1. Read `backend/services/billing.py` — check Stripe client setup
2. Read `backend/webhooks/stripe.py` — check webhook handlers
3. Read `backend/routes/billing.py` — check API endpoints
4. Verify Stripe API key is live (not test sk_test_*)
5. Test checkout flow if possible

## Output

Score (0-10) + findings + recommendations
