# DEBT-010: Database Schema Guards & Monitoring

**Sprint:** 2
**Effort:** 15h
**Priority:** MEDIUM
**Agent:** @data-engineer (Delta)

## Context

Multiple schema-level improvements strengthen data integrity and monitoring. The `handle_new_user()` trigger has been rewritten 7+ times and needs a CI guard. The `profiles.plan_type` duplication with `user_subscriptions.plan_id` is intentional (circuit breaker fail-open) but needs reconciliation monitoring. Several migrations lack `IF NOT EXISTS` guards. Missing CHECK constraints on `search_results_cache.priority` and `alert_runs.status` allow invalid values. Redundant indexes waste space. JSONB table sizes need Prometheus monitoring.

## Scope

| ID | Debito | Horas |
|----|--------|-------|
| DB-011 | `handle_new_user()` trigger rewritten 7+ times — needs CI guard + integration test | 4h |
| DB-015 | `profiles.plan_type` vs `user_subscriptions.plan_id` duplication — intentional but needs reconciliation cron | 4h |
| DB-028 | Some migrations not idempotent (`008_add_billing_period.sql` lacks `IF NOT EXISTS`) | 4h |
| DB-018 | `search_results_cache.priority` no CHECK constraint | 0.5h |
| DB-019 | `alert_runs.status` no CHECK constraint | 0.5h |
| DB-040 | Redundant index on `alert_preferences` (plain + UNIQUE on same user_id) | 0.5h |
| DB-041 | Partially redundant index on `trial_email_log` | 0.5h |
| DB-042 | Missing composite index for admin inbox in `conversations` | 1h |
| DB-021 | `user_subscriptions.billing_period` constraint may conflict with legacy data | 1h |
| DB-045 | `stripe_webhook_events` idempotency retention documentation | 1h |
| DB-031 | JSONB cache tables up to 2MB/row — need Prometheus gauge for table sizes | 2h |

## Tasks

- [ ] Add CI grep guard: fail/warn if new migration touches `handle_new_user` (DB-011)
- [ ] Create integration test verifying `handle_new_user()` output matches expected profile schema (DB-011)
- [ ] Create reconciliation cron: compare `profiles.plan_type` vs `user_subscriptions.plan_id`, log drift (DB-015)
- [ ] Add `IF NOT EXISTS` / `CREATE OR REPLACE` guards to non-idempotent migrations (DB-028)
- [ ] Add CHECK: `search_results_cache.priority IN ('hot', 'warm', 'cold')` (DB-018)
- [ ] Add CHECK: `alert_runs.status IN ('pending', 'running', 'completed', 'failed')` (DB-019)
- [ ] DROP redundant `idx_alert_preferences_user_id` (UNIQUE already creates B-tree) (DB-040)
- [ ] DROP redundant `idx_trial_email_log_user_id` (composite unique covers leading column) (DB-041)
- [ ] CREATE INDEX `idx_conversations_status_last_msg` ON `conversations(status, last_message_at DESC)` (DB-042)
- [ ] Validate `billing_period` constraint vs existing data: `SELECT billing_period, count(*) GROUP BY 1` (DB-021)
- [ ] Document `stripe_webhook_events` 90-day retention as appropriate (Stripe retry window = 72h max) (DB-045)
- [ ] Add Prometheus gauge `smartlic_table_size_bytes` for JSONB-heavy tables (DB-031)

## Acceptance Criteria

- [ ] AC1: CI warns on PRs touching `handle_new_user` trigger
- [ ] AC2: Integration test for `handle_new_user()` exists and passes
- [ ] AC3: Plan reconciliation cron detects drift between `profiles.plan_type` and `user_subscriptions`
- [ ] AC4: Non-idempotent migrations have `IF NOT EXISTS` guards
- [ ] AC5: CHECK constraints exist on `search_results_cache.priority` and `alert_runs.status`
- [ ] AC6: Zero redundant indexes (DB-040, DB-041 dropped)
- [ ] AC7: Admin inbox query uses composite index (EXPLAIN verification)
- [ ] AC8: Prometheus gauge tracks JSONB table sizes
- [ ] AC9: Zero regressions

## Tests Required

- handle_new_user integration test (insert auth.user, verify profile created correctly)
- Plan reconciliation: insert drift scenario, verify detection
- CHECK constraint violation tests (insert invalid priority/status)
- EXPLAIN ANALYZE on conversations admin query

## Definition of Done

- [ ] All tasks complete
- [ ] Migrations applied to production
- [ ] Tests passing (backend 5774+ / 0 fail)
- [ ] No regressions
- [ ] Code reviewed
