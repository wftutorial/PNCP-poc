# DEPRECATED — Backend Migrations Directory

**Status:** DEPRECATED as of DEBT-002 (2026-03-08)

## What happened?

This directory contained 9 migration files (002-010) that were applied directly to the database via Python scripts, NOT through the Supabase CLI migration pipeline. This dual-directory approach caused:

- A production incident (missing `check_and_increment_quota` RPC — CRIT-039)
- Confusion about which migrations were applied
- Inability to recreate the database from scratch

## Where did they go?

All objects from these migrations have been consolidated into `supabase/migrations/` via the **bridge migration**:

```
supabase/migrations/20260308200000_debt002_bridge_backend_migrations.sql
```

### Migration mapping:

| Backend Migration | Supabase Equivalent | Status |
|---|---|---|
| 002_monthly_quota.sql | 002_monthly_quota.sql | Already duplicated |
| 003_atomic_quota_increment.sql | 003 + 20260305100000_restore_check_and_increment_quota.sql | Already duplicated + restored |
| 004_google_oauth_tokens.sql | 013_google_oauth_tokens.sql | Already promoted |
| 005_google_sheets_exports.sql | 014_google_sheets_exports.sql | Already promoted |
| 006_classification_feedback.sql | **20260308200000_debt002_bridge** | NEW — bridged |
| 007_search_session_lifecycle.sql | 20260221100000_search_session_lifecycle.sql | Already in supabase |
| 008_search_state_transitions.sql | 20260221100002_create_search_state_transitions.sql | Already in supabase |
| 009_add_search_id_to_search_sessions.sql | 20260220120000_add_search_id_to_search_sessions.sql | Already in supabase (redundant) |
| 010_normalize_session_arrays.sql | **20260308200000_debt002_bridge** | NEW — bridged |

## What should I do?

- **DO NOT** create new migrations in this directory
- **DO NOT** delete these files (they serve as historical reference)
- All new migrations go in `supabase/migrations/` using timestamp format: `YYYYMMDDHHMMSS_description.sql`
- See `DISASTER-RECOVERY.md` for the full database recreation guide
