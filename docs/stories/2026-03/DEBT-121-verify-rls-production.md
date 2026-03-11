# DEBT-121: Verify P0 RLS in Production
**Priority:** P0-verify
**Effort:** 10min
**Owner:** @devops
**Sprint:** Week 1, Day 1

## Context

Migration 027 (`027_fix_plan_type_default_and_rls.sql`) fixes two critical RLS policy gaps on `pipeline_items` and `search_results_cache` that could allow cross-user data access. The deploy pipeline auto-applies migrations, so this fix should already be live. However, production state has never been explicitly verified. This is the single remaining question mark before declaring GTM-ready with confidence.

## Acceptance Criteria

- [ ] AC1: `pg_policies` query confirms both `pipeline_items` and `search_results_cache` service-role policies have `roles = {service_role}` (not `{0}`)
- [ ] AC2: Authenticated non-admin user query returns only own pipeline items (negative test)
- [ ] AC3: All existing pipeline CRUD tests pass (`test_pipeline.py`, `test_pipeline_coverage.py`, `test_pipeline_resilience.py`)
- [ ] AC4: FK validation query confirms `search_results_store` FK is validated (`convalidated = true`)
- [ ] AC5: Retention cron jobs query shows 4+ active cleanup jobs
- [ ] AC6: Profile defaults query confirms `plan_type` default is `'free_trial'::text`

## Technical Notes

Run these queries in Supabase SQL Editor (Dashboard > SQL Editor):

**RLS policies (primary verification):**
```sql
SELECT tablename, policyname, roles, cmd
FROM pg_policies
WHERE tablename IN ('pipeline_items', 'search_results_cache')
  AND policyname LIKE '%service%'
ORDER BY tablename, policyname;
```
Expected: `roles` contains `{service_role}`, NOT `{0}`.

**FK validation (secondary):**
```sql
SELECT conname, convalidated
FROM pg_constraint
WHERE conrelid = 'public.search_results_store'::regclass AND contype = 'f';
```
Expected: `convalidated = true`.

**Retention cron jobs (secondary):**
```sql
SELECT jobname, schedule, command
FROM cron.job
WHERE jobname LIKE 'cleanup-%'
ORDER BY jobname;
```
Expected: 4+ cleanup jobs.

**Profile defaults (secondary):**
```sql
SELECT column_default
FROM information_schema.columns
WHERE table_name = 'profiles' AND column_name = 'plan_type';
```
Expected: `'free_trial'::text`.

**If migration 027 is NOT applied:** Run `supabase db push --include-all` immediately. Migration is idempotent.

## Test Requirements

- [ ] Existing tests pass: `pytest tests/test_td001_rls_security.py` (7 tests)
- [ ] Existing tests pass: `pytest tests/test_pipeline.py tests/test_pipeline_coverage.py tests/test_pipeline_resilience.py`

## Files to Modify

- None (verification only). If migration not applied: `supabase db push --include-all`

## Definition of Done

- [ ] All 4 production verification queries return expected results
- [ ] Results documented in this story (paste query output below)
- [ ] If any query fails, remediation applied and re-verified
