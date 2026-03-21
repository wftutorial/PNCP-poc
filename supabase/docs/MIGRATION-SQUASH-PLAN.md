# Migration Squash Plan — DEBT-DB-008

> Status: PLANNED (not yet executed)
> Created: 2026-03-21
> Author: @data-engineer

## Current State

- **96 migration files** in `supabase/migrations/`
- **Two naming schemes**: legacy (`001_` through `033_`) and timestamped (`20260220120000_` onward)
- **8 redefinitions of `handle_new_user`** across migrations 001, 007, 016, 020, 024, 027, 20260224000000, 20260225110000
- **Multiple additive-then-fix chains**: e.g., 031/032/033 for cache columns, 006a/006b for profiles
- **Rollback artifacts**: `008_rollback.sql.bak` (should not be in migrations dir)

## Migration Categories

| Category | Count | Examples |
|----------|-------|---------|
| Table creation | ~15 | 001, 002, 012, 013, 014, 023, 025, 026, ... |
| Schema evolution (ALTER) | ~25 | 004, 006a, 008, 009, 015, 031-033, ... |
| RLS/security policies | ~12 | 006b, 016, 027, 20260225130000, 20260304200000, ... |
| Function/trigger defs | ~10 | 003, 011, 017, 019, 020, 20260225110000, ... |
| Data seeds (plans, billing) | ~8 | 005, 015, 029, 20260226120000, 20260301300000, ... |
| Indexes & performance | ~8 | 20260225140000, 20260307100000, 20260309100000, ... |
| pg_cron retention jobs | ~3 | 022, 20260308310000 |
| Debt cleanup / fixes | ~15 | 20260308* series, 20260309*, 20260311*, ... |

## Squash Strategy

### Phase 1: Generate Baseline (estimated 2h)

1. Spin up a clean Supabase local instance:
   ```bash
   npx supabase start
   ```

2. Apply all 96 migrations sequentially:
   ```bash
   npx supabase db push --local
   ```

3. Dump the resulting schema:
   ```bash
   pg_dump --schema-only --no-owner --no-privileges \
     -d postgresql://postgres:postgres@localhost:54322/postgres \
     > supabase/baseline/000_baseline_schema.sql
   ```

4. Dump seed data (plans, plan_billing_periods, plan_features):
   ```bash
   pg_dump --data-only --table=plans --table=plan_billing_periods \
     --table=plan_features --inserts \
     -d postgresql://postgres:postgres@localhost:54322/postgres \
     > supabase/baseline/001_baseline_seeds.sql
   ```

### Phase 2: Validate Equivalence (estimated 1h)

1. Create a second local DB and apply only the baseline:
   ```bash
   psql -d test_baseline -f supabase/baseline/000_baseline_schema.sql
   psql -d test_baseline -f supabase/baseline/001_baseline_seeds.sql
   ```

2. Diff the two schemas:
   ```bash
   pg_dump --schema-only db_original > /tmp/original.sql
   pg_dump --schema-only db_baseline > /tmp/baseline.sql
   diff /tmp/original.sql /tmp/baseline.sql
   ```

3. Must produce zero diff (excluding migration history table).

### Phase 3: Replace Migrations (estimated 1h)

1. Archive old migrations:
   ```bash
   mkdir -p supabase/migrations-archive
   mv supabase/migrations/0*.sql supabase/migrations-archive/
   mv supabase/migrations/202602*.sql supabase/migrations-archive/
   mv supabase/migrations/202603*.sql supabase/migrations-archive/
   ```

2. Place baseline files:
   ```bash
   cp supabase/baseline/000_baseline_schema.sql supabase/migrations/20260401000000_baseline_schema.sql
   cp supabase/baseline/001_baseline_seeds.sql supabase/migrations/20260401000001_baseline_seeds.sql
   ```

3. Mark existing migration history as applied:
   ```sql
   -- On production, insert baseline migration into supabase_migrations.schema_migrations
   -- so it's treated as "already applied"
   INSERT INTO supabase_migrations.schema_migrations (version, name)
   VALUES ('20260401000000', 'baseline_schema');
   INSERT INTO supabase_migrations.schema_migrations (version, name)
   VALUES ('20260401000001', 'baseline_seeds');
   ```

### Phase 4: CI Validation (estimated 1h)

See `.github/workflows/migration-validate.yml` for the CI skeleton.

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Production migration history mismatch | Mark baseline as "applied" in schema_migrations before deploying |
| Seed data drift | Separate seeds from schema; seeds can be re-run idempotently |
| Missing pg_cron jobs | Include pg_cron setup in baseline, with IF NOT EXISTS guards |
| RLS policy ordering | pg_dump captures policies; validate with `\dp` comparison |
| handle_new_user multiple versions | Baseline captures final version only (correct) |
| Rollback impossible for baseline | Keep archive; rollback = restore from archive |

## handle_new_user Redefinition History

The `handle_new_user()` trigger function has been redefined **8 times** across migrations. Each redefinition adds fields or changes defaults. The baseline will capture only the final version.

| Migration | Change |
|-----------|--------|
| 001 | Initial: id, email, full_name, plan_type, trial_expires_at |
| 007 | Added: whatsapp_consent default |
| 016 | Added: subscription_status, security hardening |
| 020 | Changed: plan_type constraint values |
| 024 | Added: context_data default |
| 027 | Changed: plan_type default logic |
| 20260224000000 | Added: phone normalization |
| 20260225110000 | Fixed: null handling, email_unsubscribed default |

## Files to Clean Up During Squash

- `008_rollback.sql.bak` — Rollback artifact, should not be in migrations/
- Any `.sql~` backup files
- Migrations that are pure no-ops after later migrations (e.g., 031 columns added then 033 re-adds them)

## Prerequisites

- [ ] All current migrations applied to production (verify with `npx supabase db diff`)
- [ ] No pending migration PRs
- [ ] Backend tests green (full suite)
- [ ] Backup production DB before squash deploy
- [ ] Schedule during low-traffic window (squash itself is metadata-only, but safety first)
