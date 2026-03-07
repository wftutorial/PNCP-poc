# DEBT-002: Migration Consolidation & Disaster Recovery

**Sprint:** 1
**Effort:** 24h
**Priority:** CRITICAL
**Agent:** @data-engineer (Delta) + @devops (Gage)

## Context

This is the single CRITICAL debt (CROSS-001, priority score 12.0). The SmartLic database has 76 migrations split across two directories (`supabase/migrations/` and `backend/migrations/`), with no documented disaster recovery procedure. The dual directory setup already caused a production incident (missing `check_and_increment_quota` RPC). Backend migrations (10 files) were never applied via Supabase CLI. Some migrations are not idempotent, and naming is non-sequential (mix of `001_` to `033_`, timestamps, and `027b_`).

If the database fails catastrophically, there is no documented procedure to recreate it. This is an existential risk for a platform handling B2G opportunity data.

**Risk assessment from executive report:** R$200K-R$500K potential impact from inability to recover database after failure.

## Scope

| ID | Debito | Horas |
|----|--------|-------|
| CROSS-001 | Migracoes nao-idempotentes + dual directories + sem DR docs — impossivel recriar DB de forma confiavel | (umbrella) |
| DB-025 | Dual migration directories (`supabase/migrations/` + `backend/migrations/`) — 10 backend migrations outside Supabase CLI | 8h |
| DB-030 | `backend/migrations/` never applied via CLI — subsumed by DB-025, same root cause | (bundled) |
| DB-043 | No documented disaster recovery procedure — 76 migrations without recreation guide | 16h |
| DB-026 | Non-sequential naming convention (mix of formats) — developer confusion risk | (documented as part of DR) |

## Tasks

### Phase A: Bridge Migration (DB-025, DB-030) — 8h

- [ ] Inventory all objects created by `backend/migrations/` (7 files): list functions, tables, indexes, triggers
- [ ] Verify each object exists in production via `pg_tables`, `pg_proc`, `pg_indexes`, `pg_trigger`
- [ ] Create bridge migration in `supabase/migrations/` with `CREATE OR REPLACE` / `IF NOT EXISTS` guards for every object
- [ ] Test bridge migration against fresh Supabase project (must succeed on empty DB)
- [ ] Test bridge migration against production clone (must be no-op on existing DB)
- [ ] Add deprecation notice to `backend/migrations/README.md` pointing to bridge migration
- [ ] Do NOT move or delete `backend/migrations/` files (historical reference)

### Phase B: Disaster Recovery Documentation (DB-043) — 16h

- [ ] Document PITR procedure for Supabase (point-in-time recovery)
- [ ] Create `DISASTER-RECOVERY.md` with step-by-step recreation guide
- [ ] Document all manual setup steps not in migrations (pg_cron jobs, extensions, superuser-only operations)
- [ ] Test full recreation on fresh Supabase project (free tier): apply all migrations, verify all objects exist
- [ ] Document seed data requirements (plans, billing periods, system accounts)
- [ ] Document env var dependencies for migration success (Stripe IDs, etc.)
- [ ] Add naming convention guidance for future migrations (DB-026)
- [ ] Create CI check that warns on new migrations touching `handle_new_user` (DB-011 guard)

## Acceptance Criteria

- [ ] AC1: `backend/migrations/` objects are all present in `supabase/migrations/` via bridge migration
- [ ] AC2: Bridge migration is idempotent (running twice produces no errors, no duplicates)
- [ ] AC3: Fresh Supabase project can be fully recreated from `supabase/migrations/` alone
- [ ] AC4: `DISASTER-RECOVERY.md` exists with tested step-by-step procedure
- [ ] AC5: DR test evidence documented (screenshots/logs of fresh project recreation)
- [ ] AC6: All pg_cron jobs, extensions, and manual setup steps documented
- [ ] AC7: CI grep guard for `handle_new_user` in new migrations is active

## Tests Required

- Bridge migration idempotency test (apply twice on same DB)
- Fresh project recreation test (apply all migrations from zero)
- Object verification script: compare `pg_catalog` objects against expected list
- CI guard test: PR with migration touching `handle_new_user` triggers warning

## Definition of Done

- [ ] All tasks complete
- [ ] Bridge migration applied to production
- [ ] DR procedure tested on fresh Supabase project
- [ ] DISASTER-RECOVERY.md reviewed by @devops
- [ ] Zero regressions in test suite
- [ ] No files deleted from `backend/migrations/`
