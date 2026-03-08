# SmartLic — Disaster Recovery Guide

**DEBT-002, Phase B (DB-043)**
**Last updated:** 2026-03-08
**Owner:** Tiago Sasaki (tiago.sasaki@gmail.com)

---

## 1. Emergency Contacts & Escalation

| Role | Contact | Method |
|------|---------|--------|
| DBA / Platform Owner | Tiago Sasaki | tiago.sasaki@gmail.com |
| Supabase Support | support@supabase.io | Dashboard > Support (Pro plan) |
| Railway Support | support@railway.app | Dashboard > Help, Discord |
| Stripe Support | dashboard.stripe.com/support | Dashboard ticket |
| Resend Support | support@resend.com | Dashboard ticket |

**Escalation order:**
1. Assess severity: data loss vs. downtime vs. degraded performance
2. If data loss: PITR immediately (Section 2)
3. If Supabase project unrecoverable: Full Recreation (Section 3)
4. Notify users via Resend if downtime exceeds 30 minutes

---

## 2. Point-in-Time Recovery (PITR) — Preferred Method

**Use this for:** accidental data deletion, data corruption, bad migration applied.
**Do NOT use this for:** project deletion or Supabase region outage.

**RPO:** up to 2 minutes (WAL archiving)
**RTO:** ~15-30 minutes

### Steps

1. Go to **Supabase Dashboard** > select project `fqqyovlzdzimiwfofdjk`
2. Navigate to **Database > Backups > Point in Time**
3. Select the target recovery timestamp (before the incident)
4. Click **Start recovery** — this creates a NEW project with restored data
5. Note the new project ref, URL, and keys
6. Update all environment variables (Section 5)
7. Verify with the post-recreation checklist (Section 7)
8. Update DNS/CNAME if the Supabase URL changed

### Important Notes

- PITR restores to a **new project** — the old project remains untouched
- Auth users, storage objects, and database are all restored
- Edge Functions and Auth settings (email templates, OAuth config) may need manual re-setup
- Supabase Pro plan includes 7 days of PITR history

---

## 3. Full Recreation from Migrations (Nuclear Option)

**Use this for:** project completely lost, starting fresh, or migrating to a new Supabase organization.
**WARNING:** This recreates the schema only. User data is NOT recovered unless you have a pg_dump backup.

### Prerequisites

```bash
# Ensure Supabase CLI is available
npx supabase --version

# Have the repo cloned with all migrations
cd D:/pncp-poc
ls supabase/migrations/ | wc -l   # Should show 80 files
```

### Step 1: Create New Supabase Project

1. Go to **supabase.com/dashboard** > New Project
2. **Region:** South America (São Paulo) — `sa-east-1`
3. **Name:** `smartlic-prod` (or `smartlic-dr-YYYYMMDD`)
4. **Database password:** Generate and save securely
5. Note the new **project ref** (replaces `fqqyovlzdzimiwfofdjk`)

### Step 2: Enable pg_cron Extension BEFORE Migrations

**CRITICAL — migrations 022, 023, 20260225150000, 20260304110000 will FAIL without this.**

1. Go to **Dashboard > Database > Extensions**
2. Search for `pg_cron`
3. Click **Enable**
4. Verify it appears in enabled extensions list

> Note: `pg_trgm` is created by migration 016 via SQL (`CREATE EXTENSION IF NOT EXISTS pg_trgm`) and does not need manual enabling.

### Step 3: Link and Apply Migrations

```bash
cd D:/pncp-poc

# Set access token
export SUPABASE_ACCESS_TOKEN=$(grep SUPABASE_ACCESS_TOKEN .env | cut -d '=' -f2)

# Link to new project
npx supabase link --project-ref <NEW_PROJECT_REF>

# Apply ALL migrations in order
npx supabase db push --include-all
```

If any migration fails:
- Check if it is a pg_cron issue (Step 2 missed)
- Check if it is an idempotency issue (early migrations 001-033 do not use IF NOT EXISTS)
- For early migrations that fail on re-run, this is expected in sequential Supabase migration tracking

### Step 4: Verify pg_cron Jobs

Run this in the **SQL Editor** (Dashboard > SQL Editor):

```sql
SELECT jobname, schedule, command
FROM cron.job
ORDER BY jobname;
```

**Expected 5 jobs:**

| Job Name | Schedule | Source Migration |
|----------|----------|-----------------|
| `cleanup-monthly-quota` | `0 2 1 * *` | 022 |
| `cleanup-webhook-events` | `0 3 * * *` | 022 |
| `cleanup-audit-events` | `0 4 1 * *` | 023 |
| `cleanup-cold-cache-entries` | `0 5 * * *` | 20260225150000 |
| `cleanup-expired-search-results` | `0 4 * * *` | 20260304110000 |

If any jobs are missing, re-run the `cron.schedule()` statements from the corresponding migration file manually in the SQL Editor.

### Step 5: Verify Tables and Functions

Run this verification script in the SQL Editor:

```sql
-- Count all public tables
SELECT COUNT(*) AS table_count
FROM information_schema.tables
WHERE table_schema = 'public' AND table_type = 'BASE TABLE';

-- List all tables
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
ORDER BY table_name;

-- Verify critical RPC functions exist
SELECT routine_name
FROM information_schema.routines
WHERE routine_schema = 'public'
  AND routine_name IN (
    'check_and_increment_quota',
    'increment_quota_atomic',
    'handle_new_user',
    'set_updated_at',
    'get_table_columns_simple'
  )
ORDER BY routine_name;

-- Verify critical triggers
SELECT trigger_name, event_object_table, action_timing, event_manipulation
FROM information_schema.triggers
WHERE trigger_schema = 'public'
ORDER BY event_object_table, trigger_name;

-- Verify RLS is enabled
SELECT tablename, COUNT(*) AS policy_count
FROM pg_policies
WHERE schemaname = 'public'
GROUP BY tablename
ORDER BY tablename;

-- Verify plan seed data
SELECT id, name, slug FROM public.plans ORDER BY id;
SELECT plan_id, billing_period, stripe_price_id FROM public.plan_billing_periods ORDER BY plan_id, billing_period;
```

### Step 6: Seed Admin User

1. Go to **Dashboard > Auth > Users**
2. Create user: `tiago.sasaki@gmail.com` (or invite via email)
3. After user is created, run in SQL Editor:

```sql
UPDATE public.profiles
SET is_admin = true, is_master = true
WHERE email = 'tiago.sasaki@gmail.com';
```

4. Repeat for master user `marinalvabaron@gmail.com` if needed:

```sql
UPDATE public.profiles
SET is_master = true
WHERE email = 'marinalvabaron@gmail.com';
```

### Step 7: Update Environment Variables

See Section 5 for the full list.

---

## 4. Manual Setup Steps NOT in Migrations

These items are configured via the Supabase Dashboard and are NOT captured in migration files:

| Item | Where to Configure | Notes |
|------|--------------------|-------|
| **pg_cron extension** | Database > Extensions | MUST be enabled BEFORE migrations 022, 023, 20260225150000, 20260304110000 |
| **Auth email templates** | Auth > Email Templates | Confirmation, magic link, password reset templates |
| **Auth redirect URLs** | Auth > URL Configuration | `https://smartlic.tech/auth/callback`, `http://localhost:3000/auth/callback` |
| **Google OAuth** | Auth > Providers > Google | Client ID + secret from Google Cloud Console |
| **Auth settings** | Auth > Settings | Email confirmations, password requirements |
| **Storage buckets** | Storage | None currently in use |
| **Edge Functions** | Edge Functions | None currently deployed |
| **Realtime** | Realtime | Not used for subscriptions |

---

## 5. Environment Variables to Update After Recovery

### Backend (.env / Railway)

```bash
SUPABASE_URL=https://<NEW_REF>.supabase.co
SUPABASE_KEY=<new_anon_key>
SUPABASE_SERVICE_ROLE_KEY=<new_service_role_key>
DATABASE_URL=postgresql://postgres:<password>@db.<NEW_REF>.supabase.co:5432/postgres
```

### Frontend (.env.local / Railway)

```bash
NEXT_PUBLIC_SUPABASE_URL=https://<NEW_REF>.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<new_anon_key>
```

### Railway Update Commands

```bash
# Backend service
railway variables set SUPABASE_URL=https://<NEW_REF>.supabase.co --service bidiq-backend
railway variables set SUPABASE_KEY=<new_anon_key> --service bidiq-backend
railway variables set SUPABASE_SERVICE_ROLE_KEY=<new_service_role_key> --service bidiq-backend

# Frontend service
railway variables set NEXT_PUBLIC_SUPABASE_URL=https://<NEW_REF>.supabase.co --service bidiq-frontend
railway variables set NEXT_PUBLIC_SUPABASE_ANON_KEY=<new_anon_key> --service bidiq-frontend
```

### External Services to Update

| Service | What to Update | Where |
|---------|---------------|-------|
| **Stripe** | Webhook endpoint URL (if Supabase URL changed in webhook handler) | Stripe Dashboard > Webhooks |
| **Railway** | Redeploy both services after env var changes | `railway up` or push to main |
| **GitHub Actions** | `SUPABASE_PROJECT_REF`, `SUPABASE_ACCESS_TOKEN`, `SUPABASE_DB_URL` secrets | Repo > Settings > Secrets |

### Migration-Hardcoded Values (No Env Dependency)

These values are hardcoded in SQL migrations and do NOT depend on environment variables:
- **Stripe price IDs** in `029_single_plan_model.sql` and `20260301300000_consultoria_stripe_ids.sql`
- **Plan definitions** (names, slugs, quotas) in migrations 001, 005, 029, 20260301300000

If Stripe products/prices were recreated, you must manually update the `plan_billing_periods.stripe_price_id` column.

---

## 6. Seed Data Requirements

| Table | Seeded By | Mechanism |
|-------|-----------|-----------|
| `plans` | 001, 005, 029, 20260301300000 | INSERT ... ON CONFLICT DO UPDATE |
| `plan_billing_periods` | 029, 20260301300000 | INSERT ... ON CONFLICT DO UPDATE |
| `plan_features` | 009, 029, 20260301300000 | INSERT ... ON CONFLICT DO NOTHING |

All seed data is embedded in migrations and applied automatically during `db push`. No separate seed script is needed.

**User data** (profiles, searches, pipeline items, etc.) is NOT seeded — it only exists in production backups or PITR restores.

---

## 7. Post-Recreation Verification Checklist

Run through this checklist after any recovery operation:

### Database

- [ ] All 80 migrations applied without errors (`npx supabase db push --include-all`)
- [ ] pg_cron extension enabled and 5 jobs scheduled (query `cron.job`)
- [ ] pg_trgm extension enabled (query `pg_extension`)
- [ ] `handle_new_user` trigger exists on `auth.users`
- [ ] `check_and_increment_quota` RPC function exists
- [ ] `increment_quota_atomic` RPC function exists
- [ ] `set_updated_at` function exists (consolidated by DEBT-001)
- [ ] All RLS policies active: `SELECT tablename, COUNT(*) FROM pg_policies GROUP BY tablename`
- [ ] Plans table has correct entries: `SELECT * FROM plans`
- [ ] Billing periods have Stripe price IDs: `SELECT * FROM plan_billing_periods`

### Backend

- [ ] `.env` updated with new Supabase credentials
- [ ] `uvicorn main:app --port 8000` starts without errors
- [ ] `GET /health` returns 200
- [ ] `GET /health/cache` returns 200
- [ ] `GET /setores` returns 15 sectors
- [ ] `GET /plans` returns plan data
- [ ] Login works (test with admin account)
- [ ] Search pipeline produces results (run a test search)

### Frontend

- [ ] `.env.local` updated with new Supabase credentials
- [ ] `npm run build` succeeds
- [ ] Login page loads at `/login`
- [ ] Login with admin credentials works
- [ ] Search page loads at `/buscar`
- [ ] Dashboard loads at `/dashboard`

### External Integrations

- [ ] Stripe webhooks receiving events (check Stripe Dashboard > Webhooks > Recent events)
- [ ] Railway services healthy (both backend and frontend)
- [ ] GitHub Actions secrets updated (if project ref changed)
- [ ] Custom domain `smartlic.tech` resolving correctly

---

## 8. Migration Naming Convention (DB-026)

| Format | Example | Usage |
|--------|---------|-------|
| `YYYYMMDDHHMMSS_description.sql` | `20260308200000_debt002_bridge.sql` | **Current standard** — use for ALL new migrations |
| `NNN_description.sql` | `001_profiles_and_sessions.sql` | **Legacy** — DO NOT use for new migrations |

### Rules for New Migrations

1. Always use timestamp format (`YYYYMMDDHHMMSS`)
2. Use `IF NOT EXISTS` / `CREATE OR REPLACE` / `ON CONFLICT` for idempotency
3. Include verification queries as SQL comments at the end of the file
4. One logical change per migration (do not bundle unrelated changes)
5. Test on fresh DB AND on existing DB before applying to production
6. New migrations go in `supabase/migrations/` ONLY (`backend/migrations/` is DEPRECATED)

---

## 9. Backup Schedule & Retention

| Backup Type | Frequency | Retention | Method |
|-------------|-----------|-----------|--------|
| Supabase automatic | Daily | 7 days | Managed by Supabase (Pro plan) |
| PITR (WAL archiving) | Continuous | 7 days | Managed by Supabase (Pro plan) |
| Manual pg_dump | As needed | Keep indefinitely | See below |

### Manual Backup (pg_dump)

For extra safety before risky operations:

```bash
# Get connection string from Dashboard > Settings > Database > Connection string (URI)
pg_dump "postgresql://postgres:<password>@db.fqqyovlzdzimiwfofdjk.supabase.co:5432/postgres" \
  --format=custom \
  --file=smartlic_backup_$(date +%Y%m%d_%H%M%S).dump

# Restore to a target database
pg_restore --dbname="<target_connection_string>" smartlic_backup_YYYYMMDD_HHMMSS.dump
```

---

## 10. Known Gotchas

### Migration Ordering

- **pg_cron must be enabled manually** before running migrations. Migration 022 has `CREATE EXTENSION IF NOT EXISTS pg_cron` but this requires superuser on Supabase, which only works via the Dashboard Extensions page.
- Early migrations (001-033) use legacy naming and some lack `IF NOT EXISTS` guards. They will fail if re-run on an existing DB — this is normal for Supabase's sequential migration tracking.

### Critical Functions and Triggers

- **`handle_new_user()` trigger on `auth.users`**: If missing, new signups create an auth user but NO profile row, causing cascading 401/403 errors on every subsequent request. This is the single most critical trigger.
- **`set_updated_at()` function**: Consolidated by DEBT-001 migration (`20260308100000`). Replaces the older `update_updated_at()`. Both names may exist in the DB; the old one is dropped by DEBT-001.
- **`check_and_increment_quota` RPC**: If missing, all searches fail with "quota check failed". Restored by migration `20260305100000`.

### Deprecated Directories

- `backend/migrations/` is DEPRECATED. All migrations live in `supabase/migrations/`. The backend directory contains 7 legacy Python-based migrations that are no longer used.

### Stripe Integration

- Stripe price IDs are hardcoded in migrations 029 and 20260301300000. If you recreate Stripe products, you must UPDATE `plan_billing_periods.stripe_price_id` to match the new price IDs.
- The Stripe webhook signing secret (`STRIPE_WEBHOOK_SECRET`) must match the webhook endpoint configured in Stripe Dashboard.

### Railway Deployment After Recovery

- After updating env vars, both Railway services need redeployment: `railway up --service bidiq-backend` and `railway up --service bidiq-frontend`
- Railway does NOT auto-restart services when env vars change via CLI — you must trigger a deploy.

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-03-08 | Created this document (DEBT-002/DB-043) | No DR runbook existed; 80 migrations with implicit dependencies |
| 2026-03-08 | PITR designated as preferred recovery method | Faster, preserves data, lower risk than full recreation |
| 2026-03-08 | pg_cron identified as manual pre-requisite | 4 migrations depend on it; cannot be auto-enabled via SQL on Supabase |
