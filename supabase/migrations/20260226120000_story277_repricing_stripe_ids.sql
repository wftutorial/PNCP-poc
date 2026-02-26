-- Migration: STORY-277 Repricing — Update Stripe Price IDs
-- Date: 2026-02-26
-- Author: AIOS Development Team
-- Story: STORY-277
--
-- Summary:
-- Updates Stripe Price IDs for SmartLic Pro to reflect new market-aligned pricing:
--   Monthly:    R$ 397/mês   (was R$ 1.999/mês)
--   Semiannual: R$ 2.142/6mo (was R$ 10.794/6mo) — R$ 357/mês, 10% off
--   Annual:     R$ 3.564/ano (was R$ 19.188/ano) — R$ 297/mês, 25% off
--
-- Old prices archived in Stripe Dashboard (0 active subscriptions).

BEGIN;

-- 1. Update plans table with new Stripe Price IDs
UPDATE public.plans SET
  price_brl = 397.00,
  stripe_price_id_monthly = 'price_1T54vN9FhmvPslGYgfTGIAzV',
  stripe_price_id_semiannual = 'price_1T54w99FhmvPslGY0coDMQGn',
  stripe_price_id_annual = 'price_1T54wt9FhmvPslGYqX6bTNo0'
WHERE id = 'smartlic_pro';

-- 2. Update plan_billing_periods table with new prices and Stripe Price IDs
UPDATE public.plan_billing_periods SET
  price_cents = 39700,
  discount_percent = 0,
  stripe_price_id = 'price_1T54vN9FhmvPslGYgfTGIAzV'
WHERE plan_id = 'smartlic_pro' AND billing_period = 'monthly';

UPDATE public.plan_billing_periods SET
  price_cents = 35700,
  discount_percent = 10,
  stripe_price_id = 'price_1T54w99FhmvPslGY0coDMQGn'
WHERE plan_id = 'smartlic_pro' AND billing_period = 'semiannual';

UPDATE public.plan_billing_periods SET
  price_cents = 29700,
  discount_percent = 25,
  stripe_price_id = 'price_1T54wt9FhmvPslGYqX6bTNo0'
WHERE plan_id = 'smartlic_pro' AND billing_period = 'annual';

COMMIT;
