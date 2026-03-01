# Session: STORY-314 — Stripe ⇄ DB Reconciliation

**Date:** 2026-02-28
**Commit:** `ed2880d`
**Status:** COMPLETE — 17/17 ACs delivered

## What Was Done

Full implementation of Stripe ⇄ DB reconciliation service with 17 acceptance criteria across backend worker, scheduling, reporting, metrics, frontend, and tests.

### Files Created
- `backend/services/stripe_reconciliation.py` — Core reconciliation service (479 lines)
- `backend/tests/test_stripe_reconciliation.py` — 24 tests across 8 test classes (835 lines)
- `supabase/migrations/20260228140000_add_reconciliation_log.sql` — reconciliation_log table + RLS

### Files Modified
- `backend/admin.py` — +2 endpoints (GET history, POST trigger)
- `backend/config.py` — +2 config flags (RECONCILIATION_ENABLED, RECONCILIATION_HOUR_UTC)
- `backend/cron_jobs.py` — +3 functions (start_reconciliation_task, run_reconciliation, _reconciliation_loop)
- `backend/main.py` — startup/shutdown task registration
- `backend/metrics.py` — +4 Prometheus metrics
- `frontend/app/admin/page.tsx` — reconciliation widget with history + manual trigger

## Key Decisions

1. **Stripe = source of truth** — DB is always updated to match Stripe, never the reverse
2. **pending_payment is valid** — Boleto/PIX async payments are NOT treated as divergence
3. **past_due is valid** — Dunning state is NOT treated as divergence
4. **Asyncio cron (not ARQ)** — Background task via asyncio.create_task, same pattern as cache/session cleanup
5. **Redis lock with 30min TTL** — Prevents duplicate execution, graceful fallback if Redis down

## Test Mock Patterns (IMPORTANT for future maintenance)

- **Stripe objects**: Use `_StripeObj(dict)` subclass for dual dict/attribute access
- **Supabase chains**: Use `_FakeChain` class for `.table().select().not_.is_().execute()` pattern
- **Local imports**: Patch at SOURCE module (e.g., `services.stripe_reconciliation.reconcile_subscriptions`), NOT at import site
- **Alert email**: Patch `email_service.send_email_async` and `templates.emails.base.email_base` (source modules)
- **Admin endpoints**: Patch `supabase_client.get_supabase` (not `admin.get_supabase`) and `cron_jobs.run_reconciliation`

## Regression Results

- **STORY-314 tests**: 24/24 passing
- **Full suite**: 6262 passed, 8 failed (all pre-existing), 5 skipped
- **Frontend TypeScript**: Clean (0 errors)
- **OpenAPI snapshot**: Updated to include new endpoints
