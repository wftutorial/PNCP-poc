# STORY-275: Enable Boleto/PIX Payment via Stripe

**GTM Audit Ref:** H12 + E-MED-004
**Priority:** P2
**Effort:** 2 days
**Squad:** @dev + @qa
**Source:** `docs/audits/gtm-validation-2026-02-25.md`, Track E

## Context

Brazilian B2G companies, especially smaller ones, strongly prefer Boleto Bancário and PIX for SaaS subscriptions. Finance departments often cannot approve credit card recurring charges. Stripe supports both Boleto and PIX in Brazil.

Currently, SmartLic only accepts credit cards. The pricing page FAQ mentions Boleto/PIX "em fase de implementação."

## Acceptance Criteria

### AC1: Enable Boleto in Stripe Checkout
- [ ] Add `boleto` to `payment_method_types` in Stripe checkout session creation
- [ ] Boleto has a 3-day payment window (configure in Stripe dashboard)
- [ ] Handle `checkout.session.async_payment_succeeded` webhook for Boleto (payment is async)
- [ ] Handle `checkout.session.async_payment_failed` webhook (Boleto expired)
- [ ] **File:** `backend/services/billing.py` (checkout session creation)
- [ ] **File:** `backend/webhooks/stripe.py` (new webhook handlers)

### AC2: Enable PIX in Stripe Checkout
- [ ] Add `pix` to `payment_method_types` in Stripe checkout session creation
- [ ] PIX has instant confirmation (synchronous)
- [ ] Verify: PIX payment flows through existing `checkout.session.completed` webhook
- [ ] **File:** `backend/services/billing.py`

### AC3: Update Pricing Page
- [ ] Show payment method icons: Cartão, Boleto, PIX
- [ ] Remove "em fase de implementação" from FAQ
- [ ] Update FAQ: "Aceitamos cartão de crédito, Boleto Bancário e PIX"
- [ ] **File:** `frontend/app/planos/page.tsx`

### AC4: Handle Boleto Async Payment Grace Period
- [ ] When user pays via Boleto: activate subscription immediately (grace period)
- [ ] If Boleto expires (3 days, no payment): revert to trial/free
- [ ] Send reminder email at day 2: "Seu boleto vence amanhã"
- [ ] **File:** `backend/webhooks/stripe.py`, `backend/email_service.py`

## Testing Strategy

- [ ] Unit tests: checkout session creation with boleto + pix payment methods
- [ ] Unit tests: async_payment_succeeded webhook handler
- [ ] Unit tests: async_payment_failed webhook handler (Boleto expired)
- [ ] Manual: test Boleto flow in Stripe test mode
- [ ] Manual: test PIX flow in Stripe test mode
- [ ] Regression: existing billing tests pass

## Files to Modify

| File | Change |
|------|--------|
| `backend/services/billing.py` | Add boleto + pix to payment_method_types |
| `backend/webhooks/stripe.py` | Handle async payment webhooks |
| `frontend/app/planos/page.tsx` | Payment method icons + FAQ update |
| `backend/email_service.py` | Boleto reminder email |
| `backend/tests/` | New tests for Boleto/PIX |

## Dependencies

- Stripe account must have Boleto and PIX enabled (Brazil-specific)
- Verify in Stripe Dashboard → Settings → Payment Methods
