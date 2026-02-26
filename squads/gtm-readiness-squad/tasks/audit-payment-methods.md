---
task: "Audit Payment Methods"
responsavel: "@billing-auditor"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - STORY-280 implementation (Boleto + PIX)
  - backend/services/billing.py
  - frontend/app/planos/page.tsx
Saida: |
  - Payment method coverage
  - Boleto/PIX validation status
  - User-facing payment flow review
Checklist:
  - "[ ] Credit card works end-to-end"
  - "[ ] Boleto generation works (STORY-280)"
  - "[ ] PIX QR code works (STORY-280)"
  - "[ ] Payment confirmation updates plan"
  - "[ ] Failed payment handled gracefully"
---

# *audit-payments

Test all payment methods: credit card, Boleto, PIX.

## Steps

1. Review STORY-280 implementation for Boleto + PIX
2. Check Stripe dashboard for payment method configuration
3. Verify frontend displays all payment options
4. Check webhook handlers for each payment type
5. Verify plan activation after successful payment

## Output

Score (0-10) + payment method status + gaps
