-- DEBT-DB-009: Document hardcoded Stripe price IDs in migrations
--
-- PROBLEM: Migrations 015, 021, 029, 20260226120000, and 20260301300000
-- contain hardcoded PRODUCTION Stripe price IDs (price_1Sy*, price_1Sz*,
-- price_1T1*, price_1T5*). These are fine for production (idempotent upserts)
-- but break staging/dev environments that use Stripe TEST mode.
--
-- WHY NOT ENV-BASED: SQL migrations run via `supabase db push` which has
-- no mechanism to inject environment variables. Supabase migrations are
-- pure SQL — no templating engine, no variable substitution.
--
-- RECOMMENDED APPROACH FOR NEW ENVIRONMENTS:
-- 1. Run all migrations normally (production IDs will be inserted)
-- 2. Run the seed script to overwrite with env-specific IDs:
--    python scripts/seed_stripe_prices.py
--    (reads STRIPE_PRICE_* from .env and updates plans + plan_billing_periods)
--
-- CURRENT PRODUCTION STRIPE PRICE IDS (as of 2026-03-21):
-- ┌─────────────────┬─────────────┬──────────────────────────────────────┐
-- │ Plan            │ Period      │ Stripe Price ID                      │
-- ├─────────────────┼─────────────┼──────────────────────────────────────┤
-- │ smartlic_pro    │ monthly     │ price_1T54vN9FhmvPslGYgfTGIAzV       │
-- │ smartlic_pro    │ semiannual  │ price_1T54w99FhmvPslGY0coDMQGn       │
-- │ smartlic_pro    │ annual      │ price_1T54wt9FhmvPslGYqX6bTNo0       │
-- │ consultoria     │ monthly     │ price_1T5xgc9FhmvPslGYgN2Mw3RL      │
-- │ consultoria     │ semiannual  │ price_1T5xge9FhmvPslGYvlyTokpt      │
-- │ consultoria     │ annual      │ price_1T5xgg9FhmvPslGYu9rD7XbC      │
-- └─────────────────┴─────────────┴──────────────────────────────────────┘
--
-- LEGACY (inactive plans, kept for historical subscriptions):
-- │ consultor_agil  │ monthly     │ price_1Syir09FhmvPslGYOCbOvWVB       │
-- │ consultor_agil  │ annual      │ price_1SzRAC9FhmvPslGYLBuYTaSa       │
-- │ maquina         │ monthly     │ price_1Syirk9FhmvPslGY1kbNWxaz       │
-- │ maquina         │ annual      │ price_1SzR8F9FhmvPslGYDW84AzYA       │
-- │ sala_guerra     │ monthly     │ price_1Syise9FhmvPslGYAR8Fbf5E       │
-- │ sala_guerra     │ annual      │ price_1SzR5c9FhmvPslGYQym74G6K       │

-- Add comments to the tables documenting the price ID source
COMMENT ON COLUMN public.plans.stripe_price_id_monthly IS
  'Stripe monthly price ID. Production values set by migrations. '
  'For staging/dev: run scripts/seed_stripe_prices.py with STRIPE_PRICE_* env vars. '
  'See DEBT-DB-009 migration for full price ID registry.';

COMMENT ON COLUMN public.plans.stripe_price_id_semiannual IS
  'Stripe semiannual price ID. See stripe_price_id_monthly comment for setup instructions.';

COMMENT ON COLUMN public.plans.stripe_price_id_annual IS
  'Stripe annual price ID. See stripe_price_id_monthly comment for setup instructions.';

COMMENT ON COLUMN public.plan_billing_periods.stripe_price_id IS
  'Stripe price ID for this billing period. Source of truth for checkout. '
  'Production values set by migrations. For staging/dev: run scripts/seed_stripe_prices.py.';
