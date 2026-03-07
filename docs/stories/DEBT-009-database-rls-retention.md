# DEBT-009: Database RLS & Retention Hardening

**Sprint:** 2
**Effort:** 18h
**Priority:** HIGH
**Agent:** @data-engineer (Delta)

## Context

Several RLS policies use suboptimal `auth.role()` checks instead of the standard `TO service_role USING (true)` pattern. While functionally correct, this is inconsistent and slightly less performant. Multiple tables grow without retention limits — `search_state_transitions` generates ~15K rows/month, `alert_sent_items` serves active dedup but never cleans up, `health_checks` and `incidents` have "30-day retention" comments but no actual pg_cron jobs. The `search_state_transitions` RLS policy uses a correlated subquery that becomes expensive at scale. The system cache warmer account has an empty password (safe but lacks defense-in-depth).

## Scope

| ID | Debito | Horas |
|----|--------|-------|
| DB-001 | `classification_feedback` service_role policy uses `auth.role()` instead of `TO service_role` pattern | 1h |
| DB-048 | `partners` and `partner_referrals` service_role policies use `auth.role()` — not included in standardization migration | 0.5h |
| DB-033 | `search_state_transitions` grows without limits (~15K rows/month) | 1h |
| DB-037 | `alert_sent_items` no retention cleanup — dedup queries degrade over time | 1h |
| DB-049 | `health_checks` and `incidents` have "30-day retention" comments but no pg_cron jobs (~8,640 rows/month) | 1h |
| DB-007 | `search_state_transitions` SELECT policy uses expensive correlated subquery | 4h |
| DB-002 | `health_checks` and `incidents` without explicit service_role policies (backend-only by design) | 1h |
| DB-010 | System cache warmer account with empty password — add `banned_until = '2099-12-31'` | 1h |

**Retention pg_cron jobs bundle (~4h total for DB-033, DB-037, DB-049):**

| Table | Retention | Schedule |
|-------|-----------|----------|
| search_state_transitions | 30 days | Daily 4am UTC |
| alert_sent_items | 180 days | Daily 4am UTC |
| health_checks | 30 days | Daily 4am UTC |
| incidents | 90 days | Daily 4am UTC |
| mfa_recovery_attempts | 30 days | Daily 4am UTC |
| alert_runs (completed) | 90 days | Daily 4am UTC |

## Tasks

- [ ] Create migration: standardize `classification_feedback`, `partners`, `partner_referrals` RLS policies to `TO service_role USING (true)` (DB-001, DB-048)
- [ ] Create migration: add explicit `TO service_role USING (true)` to `health_checks` and `incidents` for documentation (DB-002)
- [ ] Create pg_cron jobs for all 6 retention policies (DB-033, DB-037, DB-049)
- [ ] Optimize `search_state_transitions` RLS: add `user_id` column with backfill from `search_sessions`, replace correlated subquery with direct column check (DB-007)
- [ ] Ban system cache warmer account: `UPDATE auth.users SET banned_until = '2099-12-31' WHERE email = 'cache-warmer@smartlic.internal'` (DB-010)
- [ ] Document all pg_cron jobs in `DISASTER-RECOVERY.md` (from DEBT-002)

## Acceptance Criteria

- [ ] AC1: Zero `auth.role()` calls in RLS policies (all standardized to `TO service_role`)
- [ ] AC2: 6 pg_cron retention jobs scheduled and verified with manual execution
- [ ] AC3: `search_state_transitions` RLS uses direct `user_id` column (no subquery)
- [ ] AC4: EXPLAIN on `search_state_transitions` shows Index Scan (not nested loop)
- [ ] AC5: Cache warmer account has `banned_until` set (cannot authenticate)
- [ ] AC6: All pg_cron jobs documented
- [ ] AC7: Zero regressions in backend test suite

## Tests Required

- Migration idempotency tests
- RLS verification: service_role can access all rows; anon cannot
- EXPLAIN ANALYZE on search_state_transitions with new user_id column
- pg_cron job execution test with sample expired data
- Cache warmer account login attempt (should fail)

## Definition of Done

- [ ] All tasks complete
- [ ] Migration applied to production
- [ ] Tests passing (backend 5774+ / 0 fail)
- [ ] No regressions
- [ ] pg_cron jobs verified in production
- [ ] Code reviewed
