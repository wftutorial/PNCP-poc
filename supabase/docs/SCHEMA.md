# SmartLic Database Schema Documentation

**Provider:** Supabase (PostgreSQL 17)
**Project Ref:** `fqqyovlzdzimiwfofdjk`
**Schema Generated:** 2026-03-07
**Migrations Analyzed:** 76 files (66 Supabase + 10 backend)
**Total Tables:** 27
**Total Functions:** 13
**Total Custom Types:** 1

---

## Table of Contents

1. [Tables](#tables)
2. [Relationships (Entity-Relationship)](#relationships)
3. [Indexes](#indexes)
4. [RLS Policies](#rls-policies)
5. [Functions and Triggers](#functions-and-triggers)
6. [Custom Types (Enums)](#custom-types)
7. [Scheduled Jobs (pg_cron)](#scheduled-jobs)

---

## Tables

### 1. `profiles`

Extends `auth.users` with application-specific data. Central user table.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | — | PK, FK -> `auth.users(id) ON DELETE CASCADE` |
| `email` | `text` | NOT NULL | — | UNIQUE (partial index) |
| `full_name` | `text` | YES | — | |
| `company` | `text` | YES | — | |
| `plan_type` | `text` | NOT NULL | `'free_trial'` | CHECK: `free_trial, consultor_agil, maquina, sala_guerra, master, smartlic_pro, consultoria` |
| `avatar_url` | `text` | YES | — | |
| `is_admin` | `boolean` | NOT NULL | `false` | Admin access flag |
| `sector` | `text` | YES | — | User business sector |
| `phone_whatsapp` | `text` | YES | — | CHECK: 10-11 digits. UNIQUE (partial) |
| `whatsapp_consent` | `boolean` | YES | `false` | LGPD consent flag |
| `whatsapp_consent_at` | `timestamptz` | YES | — | LGPD audit trail |
| `context_data` | `jsonb` | YES | `'{}'::jsonb` | Onboarding wizard data |
| `subscription_status` | `text` | YES | `'trial'` | CHECK: `trial, active, canceling, past_due, expired` |
| `trial_expires_at` | `timestamptz` | YES | — | Trial expiration date |
| `subscription_end_date` | `timestamptz` | YES | — | When canceled sub ends |
| `email_unsubscribed` | `boolean` | YES | `false` | Email opt-out |
| `email_unsubscribed_at` | `timestamptz` | YES | — | Opt-out timestamp |
| `marketing_emails_enabled` | `boolean` | NOT NULL | `true` | Marketing email opt-out |
| `referred_by_partner_id` | `uuid` | YES | — | FK -> `partners(id)` |
| `created_at` | `timestamptz` | NOT NULL | `now()` | |
| `updated_at` | `timestamptz` | NOT NULL | `now()` | Auto-updated via trigger |

**Constraints:**
- `profiles_plan_type_check` — CHECK on plan_type values
- `chk_profiles_subscription_status` — CHECK on subscription_status values
- `phone_whatsapp_format` — CHECK: `phone_whatsapp ~ '^[0-9]{10,11}$'`

---

### 2. `plans`

Subscription plan catalog (pricing, limits).

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `text` | NOT NULL | — | PK (e.g., `smartlic_pro`, `consultoria`) |
| `name` | `text` | NOT NULL | — | |
| `description` | `text` | YES | — | |
| `max_searches` | `int` | YES | — | NULL = unlimited |
| `price_brl` | `numeric(10,2)` | NOT NULL | `0` | Monthly price |
| `duration_days` | `int` | YES | — | NULL = perpetual |
| `stripe_price_id` | `text` | YES | — | Legacy default Stripe price |
| `stripe_price_id_monthly` | `text` | YES | — | Monthly Stripe Price ID |
| `stripe_price_id_semiannual` | `text` | YES | — | Semiannual Stripe Price ID |
| `stripe_price_id_annual` | `text` | YES | — | Annual Stripe Price ID |
| `is_active` | `boolean` | NOT NULL | `true` | Soft-delete via deactivation |
| `created_at` | `timestamptz` | NOT NULL | `now()` | |
| `updated_at` | `timestamptz` | NOT NULL | `now()` | Auto-updated via trigger |

**Seeded plans:** `free`, `pack_5`, `pack_10`, `pack_20`, `monthly`, `annual` (all inactive), `consultor_agil`, `maquina`, `sala_guerra` (inactive/legacy), `smartlic_pro` (active), `consultoria` (active), `master` (internal).

---

### 3. `plan_billing_periods`

Multi-period pricing per plan (monthly/semiannual/annual).

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` | PK |
| `plan_id` | `text` | NOT NULL | — | FK -> `plans(id) ON DELETE CASCADE` |
| `billing_period` | `text` | NOT NULL | — | CHECK: `monthly, semiannual, annual` |
| `price_cents` | `integer` | NOT NULL | — | Price in cents |
| `discount_percent` | `integer` | YES | `0` | |
| `stripe_price_id` | `text` | YES | — | |
| `created_at` | `timestamptz` | YES | `now()` | |

**Constraints:** UNIQUE(`plan_id`, `billing_period`)

---

### 4. `plan_features`

Billing-period-specific feature flags per plan.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `serial` | NOT NULL | auto-increment | PK |
| `plan_id` | `text` | NOT NULL | — | FK -> `plans(id) ON DELETE CASCADE` |
| `billing_period` | `varchar(10)` | NOT NULL | — | CHECK: `monthly, semiannual, annual` |
| `feature_key` | `varchar(100)` | NOT NULL | — | Feature identifier |
| `enabled` | `boolean` | NOT NULL | `true` | |
| `metadata` | `jsonb` | YES | `'{}'::jsonb` | Feature-specific config |
| `created_at` | `timestamptz` | NOT NULL | `now()` | |
| `updated_at` | `timestamptz` | NOT NULL | `now()` | Auto-updated via trigger |

**Constraints:** UNIQUE(`plan_id`, `billing_period`, `feature_key`)

---

### 5. `user_subscriptions`

User subscription records (linked to Stripe).

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` | PK |
| `user_id` | `uuid` | NOT NULL | — | FK -> `profiles(id) ON DELETE CASCADE` |
| `plan_id` | `text` | NOT NULL | — | FK -> `plans(id) ON DELETE RESTRICT` |
| `credits_remaining` | `int` | YES | — | NULL = unlimited |
| `starts_at` | `timestamptz` | NOT NULL | `now()` | |
| `expires_at` | `timestamptz` | YES | — | NULL = never |
| `stripe_subscription_id` | `text` | YES | — | UNIQUE (partial, WHERE NOT NULL) |
| `stripe_customer_id` | `text` | YES | — | |
| `is_active` | `boolean` | NOT NULL | `true` | |
| `billing_period` | `varchar(10)` | NOT NULL | `'monthly'` | CHECK: `monthly, semiannual, annual` |
| `annual_benefits` | `jsonb` | NOT NULL | `'{}'::jsonb` | |
| `subscription_status` | `text` | YES | `'active'` | CHECK: `active, trialing, past_due, canceled, expired` |
| `first_failed_at` | `timestamptz` | YES | — | Dunning: first payment failure |
| `created_at` | `timestamptz` | NOT NULL | `now()` | |
| `updated_at` | `timestamptz` | NOT NULL | `now()` | Auto-updated via trigger |

---

### 6. `monthly_quota`

Tracks monthly search usage per user (lazy-reset by month key).

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` | PK |
| `user_id` | `uuid` | NOT NULL | — | FK -> `profiles(id) ON DELETE CASCADE` |
| `month_year` | `varchar(7)` | NOT NULL | — | Format: `YYYY-MM` |
| `searches_count` | `int` | NOT NULL | `0` | |
| `created_at` | `timestamptz` | NOT NULL | `now()` | |
| `updated_at` | `timestamptz` | NOT NULL | `now()` | |

**Constraints:** UNIQUE(`user_id`, `month_year`)
**Retention:** 24 months (pg_cron cleanup)

---

### 7. `search_sessions`

Search history per user (every search attempt is recorded).

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` | PK |
| `user_id` | `uuid` | NOT NULL | — | FK -> `profiles(id) ON DELETE CASCADE` |
| `search_id` | `uuid` | YES | — | SSE correlation ID |
| `sectors` | `text[]` | NOT NULL | — | |
| `ufs` | `text[]` | NOT NULL | — | |
| `data_inicial` | `date` | NOT NULL | — | |
| `data_final` | `date` | NOT NULL | — | |
| `custom_keywords` | `text[]` | YES | — | |
| `total_raw` | `int` | NOT NULL | `0` | |
| `total_filtered` | `int` | NOT NULL | `0` | |
| `valor_total` | `numeric(14,2)` | YES | `0` | |
| `resumo_executivo` | `text` | YES | — | |
| `destaques` | `text[]` | YES | — | |
| `excel_storage_path` | `text` | YES | — | |
| `status` | `text` | NOT NULL | `'created'` | CHECK: `created, processing, completed, failed, timed_out, cancelled` |
| `error_message` | `text` | YES | — | |
| `error_code` | `text` | YES | — | |
| `started_at` | `timestamptz` | NOT NULL | `now()` | |
| `completed_at` | `timestamptz` | YES | — | |
| `duration_ms` | `integer` | YES | — | |
| `pipeline_stage` | `text` | YES | — | |
| `raw_count` | `integer` | YES | `0` | |
| `response_state` | `text` | YES | — | `live, cached, degraded, empty_failure` |
| `failed_ufs` | `text[]` | YES | — | |
| `created_at` | `timestamptz` | NOT NULL | `now()` | |

---

### 8. `search_results_cache`

Persistent L2 cache of search results (Supabase layer of two-level SWR cache).

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` | PK |
| `user_id` | `uuid` | NOT NULL | — | FK -> `profiles(id) ON DELETE CASCADE` |
| `params_hash` | `text` | NOT NULL | — | |
| `params_hash_global` | `text` | YES | — | Cross-user cache sharing hash |
| `search_params` | `jsonb` | NOT NULL | — | |
| `results` | `jsonb` | NOT NULL | — | CHECK: `<= 2MB` (octet_length) |
| `total_results` | `integer` | NOT NULL | `0` | |
| `sources_json` | `jsonb` | NOT NULL | `'["pncp"]'` | Data source tracking |
| `fetched_at` | `timestamptz` | NOT NULL | `now()` | Live fetch timestamp |
| `last_success_at` | `timestamptz` | YES | — | |
| `last_attempt_at` | `timestamptz` | YES | — | |
| `fail_streak` | `integer` | NOT NULL | `0` | |
| `degraded_until` | `timestamptz` | YES | — | |
| `coverage` | `jsonb` | YES | — | |
| `fetch_duration_ms` | `integer` | YES | — | |
| `priority` | `text` | NOT NULL | `'cold'` | `hot, warm, cold` |
| `access_count` | `integer` | NOT NULL | `0` | |
| `last_accessed_at` | `timestamptz` | YES | — | |
| `created_at` | `timestamptz` | NOT NULL | `now()` | |

**Constraints:** UNIQUE(`user_id`, `params_hash`), `chk_results_max_size` (2MB limit)

---

### 9. `search_results_store`

Persistent L3 storage for search results (prevents "not found" after L1/L2 TTL expiry).

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `search_id` | `uuid` | NOT NULL | — | PK |
| `user_id` | `uuid` | NOT NULL | — | FK -> `profiles(id) ON DELETE CASCADE` |
| `results` | `jsonb` | NOT NULL | — | CHECK: `< 2MB` |
| `sector` | `text` | YES | — | |
| `ufs` | `text[]` | YES | — | |
| `total_filtered` | `int` | YES | `0` | |
| `created_at` | `timestamptz` | YES | `now()` | |
| `expires_at` | `timestamptz` | YES | `now() + 24h` | |

**Retention:** pg_cron deletes rows expired > 7 days.

---

### 10. `search_state_transitions`

Audit trail for search state machine transitions.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` | PK |
| `search_id` | `uuid` | NOT NULL | — | Correlates with `search_sessions.search_id` |
| `from_state` | `text` | YES | — | NULL for initial CREATED |
| `to_state` | `text` | NOT NULL | — | |
| `stage` | `text` | YES | — | Pipeline stage |
| `details` | `jsonb` | YES | `'{}'` | |
| `duration_since_previous_ms` | `integer` | YES | — | |
| `created_at` | `timestamptz` | NOT NULL | `now()` | |

---

### 11. `stripe_webhook_events`

Stripe webhook idempotency and audit trail.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `varchar(255)` | NOT NULL | — | PK (Stripe event ID: `evt_xxx`). CHECK: `id ~ '^evt_'` |
| `type` | `varchar(100)` | NOT NULL | — | Stripe event type |
| `processed_at` | `timestamptz` | NOT NULL | `now()` | |
| `payload` | `jsonb` | YES | — | Full Stripe event |
| `status` | `varchar(20)` | NOT NULL | `'completed'` | Processing state |
| `received_at` | `timestamptz` | YES | `now()` | For stuck event detection |

**Retention:** 90 days (pg_cron cleanup daily at 3 AM UTC).

---

### 12. `conversations`

InMail messaging system - conversation threads.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` | PK |
| `user_id` | `uuid` | NOT NULL | — | FK -> `profiles(id) ON DELETE CASCADE` |
| `subject` | `text` | NOT NULL | — | CHECK: `<= 200 chars` |
| `category` | `text` | NOT NULL | — | CHECK: `suporte, sugestao, funcionalidade, bug, outro` |
| `status` | `text` | NOT NULL | `'aberto'` | CHECK: `aberto, respondido, resolvido` |
| `first_response_at` | `timestamptz` | YES | — | SLA tracking |
| `last_message_at` | `timestamptz` | NOT NULL | `now()` | Auto-updated by trigger |
| `created_at` | `timestamptz` | NOT NULL | `now()` | |
| `updated_at` | `timestamptz` | NOT NULL | `now()` | |

---

### 13. `messages`

Individual messages within conversations.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` | PK |
| `conversation_id` | `uuid` | NOT NULL | — | FK -> `conversations(id) ON DELETE CASCADE` |
| `sender_id` | `uuid` | NOT NULL | — | FK -> `profiles(id) ON DELETE CASCADE` |
| `body` | `text` | NOT NULL | — | CHECK: `1-5000 chars` |
| `is_admin_reply` | `boolean` | NOT NULL | `false` | |
| `read_by_user` | `boolean` | NOT NULL | `false` | |
| `read_by_admin` | `boolean` | NOT NULL | `false` | |
| `created_at` | `timestamptz` | NOT NULL | `now()` | |

---

### 14. `pipeline_items`

Kanban pipeline for tracking procurement opportunities.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` | PK |
| `user_id` | `uuid` | NOT NULL | — | FK -> `profiles(id) ON DELETE CASCADE` |
| `pncp_id` | `text` | NOT NULL | — | Unique procurement ID |
| `objeto` | `text` | NOT NULL | — | |
| `orgao` | `text` | YES | — | |
| `uf` | `text` | YES | — | |
| `valor_estimado` | `numeric` | YES | — | |
| `data_encerramento` | `timestamptz` | YES | — | |
| `link_pncp` | `text` | YES | — | |
| `stage` | `text` | NOT NULL | `'descoberta'` | CHECK: `descoberta, analise, preparando, enviada, resultado` |
| `notes` | `text` | YES | — | |
| `version` | `integer` | NOT NULL | `1` | Optimistic locking |
| `created_at` | `timestamptz` | NOT NULL | `now()` | |
| `updated_at` | `timestamptz` | NOT NULL | `now()` | Auto-updated via trigger |

**Constraints:** UNIQUE(`user_id`, `pncp_id`)

---

### 15. `classification_feedback`

User feedback on search result relevance (created via backend migration).

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` | PK |
| `user_id` | `uuid` | NOT NULL | — | FK -> `profiles(id) ON DELETE CASCADE` |
| `search_id` | `uuid` | NOT NULL | — | |
| `bid_id` | `text` | NOT NULL | — | |
| `setor_id` | `text` | NOT NULL | — | |
| `user_verdict` | `text` | NOT NULL | — | CHECK: `false_positive, false_negative, correct` |
| `reason` | `text` | YES | — | |
| `category` | `text` | YES | — | CHECK: `wrong_sector, irrelevant_modality, too_small, too_large, closed, other` |
| `bid_objeto` | `text` | YES | — | |
| `bid_valor` | `decimal` | YES | — | |
| `bid_uf` | `text` | YES | — | |
| `confidence_score` | `integer` | YES | — | |
| `relevance_source` | `text` | YES | — | |
| `created_at` | `timestamptz` | YES | `now()` | |

**Constraints:** UNIQUE(`user_id`, `search_id`, `bid_id`)

---

### 16. `user_oauth_tokens`

Encrypted OAuth 2.0 tokens (Google Sheets integration).

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` | PK |
| `user_id` | `uuid` | NOT NULL | — | FK -> `profiles(id) ON DELETE CASCADE` |
| `provider` | `varchar(50)` | NOT NULL | — | CHECK: `google, microsoft, dropbox` |
| `access_token` | `text` | NOT NULL | — | AES-256 encrypted |
| `refresh_token` | `text` | YES | — | AES-256 encrypted |
| `expires_at` | `timestamptz` | NOT NULL | — | |
| `scope` | `text` | NOT NULL | — | |
| `created_at` | `timestamptz` | YES | `now()` | |
| `updated_at` | `timestamptz` | YES | `now()` | |

**Constraints:** UNIQUE(`user_id`, `provider`)

---

### 17. `google_sheets_exports`

Google Sheets export history and audit trail.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` | PK |
| `user_id` | `uuid` | NOT NULL | — | FK -> `profiles(id) ON DELETE CASCADE` |
| `spreadsheet_id` | `varchar(255)` | NOT NULL | — | |
| `spreadsheet_url` | `text` | NOT NULL | — | |
| `search_params` | `jsonb` | NOT NULL | — | GIN indexed |
| `total_rows` | `int` | NOT NULL | — | CHECK: `>= 0` |
| `created_at` | `timestamptz` | YES | `now()` | |
| `last_updated_at` | `timestamptz` | YES | `now()` | |

---

### 18. `audit_events`

Security audit log (PII stored as SHA-256 hashes for LGPD/GDPR).

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` | PK |
| `timestamp` | `timestamptz` | NOT NULL | `now()` | |
| `event_type` | `text` | NOT NULL | — | |
| `actor_id_hash` | `text` | YES | — | SHA-256 truncated 16 hex |
| `target_id_hash` | `text` | YES | — | SHA-256 truncated 16 hex |
| `details` | `jsonb` | YES | — | |
| `ip_hash` | `text` | YES | — | SHA-256 truncated 16 hex |

**Retention:** 12 months (pg_cron cleanup monthly at 4 AM UTC).

---

### 19. `alert_preferences`

Per-user email alert scheduling preferences.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` | PK |
| `user_id` | `uuid` | NOT NULL | — | FK -> `profiles(id) ON DELETE CASCADE`. UNIQUE |
| `frequency` | `alert_frequency` | NOT NULL | `'daily'` | Enum: `daily, twice_weekly, weekly, off` |
| `enabled` | `boolean` | NOT NULL | `true` | |
| `last_digest_sent_at` | `timestamptz` | YES | — | |
| `created_at` | `timestamptz` | NOT NULL | `now()` | |
| `updated_at` | `timestamptz` | NOT NULL | `now()` | Auto-updated via trigger |

---

### 20. `alerts`

User-defined email alerts with search filters.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` | PK |
| `user_id` | `uuid` | NOT NULL | — | FK -> `profiles(id) ON DELETE CASCADE` |
| `name` | `text` | NOT NULL | `''` | |
| `filters` | `jsonb` | NOT NULL | `'{}'` | `{setor, ufs[], valor_min, valor_max, keywords[]}` |
| `active` | `boolean` | NOT NULL | `true` | |
| `created_at` | `timestamptz` | NOT NULL | `now()` | |
| `updated_at` | `timestamptz` | NOT NULL | `now()` | Auto-updated via trigger |

---

### 21. `alert_sent_items`

Dedup tracking for alert notifications.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` | PK |
| `alert_id` | `uuid` | NOT NULL | — | FK -> `alerts(id) ON DELETE CASCADE` |
| `item_id` | `text` | NOT NULL | — | |
| `sent_at` | `timestamptz` | NOT NULL | `now()` | |

**Constraints:** UNIQUE(`alert_id`, `item_id`)

---

### 22. `alert_runs`

Alert execution history for debugging.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` | PK |
| `alert_id` | `uuid` | NOT NULL | — | FK -> `alerts(id) ON DELETE CASCADE` |
| `run_at` | `timestamptz` | NOT NULL | `now()` | |
| `items_found` | `integer` | NOT NULL | `0` | |
| `items_sent` | `integer` | NOT NULL | `0` | |
| `status` | `text` | NOT NULL | `'pending'` | `matched, no_results, no_match, all_deduped, error` |

---

### 23. `trial_email_log`

Trial email sequence tracking (6 emails over 14 days).

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` | PK |
| `user_id` | `uuid` | NOT NULL | — | FK -> `profiles(id) ON DELETE CASCADE` |
| `email_type` | `text` | NOT NULL | — | `midpoint, expiring, last_day, expired` |
| `email_number` | `integer` | YES | — | CHECK: `1-6` |
| `sent_at` | `timestamptz` | NOT NULL | `now()` | |
| `opened_at` | `timestamptz` | YES | — | Resend webhook |
| `clicked_at` | `timestamptz` | YES | — | Resend webhook |
| `resend_email_id` | `text` | YES | — | |

**Constraints:** UNIQUE(`user_id`, `email_number`)

---

### 24. `reconciliation_log`

Stripe-to-DB sync audit trail.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` | PK |
| `run_at` | `timestamptz` | NOT NULL | `now()` | |
| `total_checked` | `int` | NOT NULL | `0` | |
| `divergences_found` | `int` | NOT NULL | `0` | |
| `auto_fixed` | `int` | NOT NULL | `0` | |
| `manual_review` | `int` | NOT NULL | `0` | |
| `duration_ms` | `int` | NOT NULL | `0` | |
| `details` | `jsonb` | YES | `'[]'` | |

---

### 25. `organizations`

Multi-user organizations for consultoria/agency accounts.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` | PK |
| `name` | `text` | NOT NULL | — | |
| `logo_url` | `text` | YES | — | |
| `owner_id` | `uuid` | NOT NULL | — | FK -> `profiles(id) ON DELETE RESTRICT` |
| `max_members` | `int` | NOT NULL | `5` | |
| `plan_type` | `text` | NOT NULL | `'consultoria'` | |
| `stripe_customer_id` | `text` | YES | — | |
| `created_at` | `timestamptz` | NOT NULL | `now()` | |
| `updated_at` | `timestamptz` | NOT NULL | `now()` | Auto-updated via trigger |

---

### 26. `organization_members`

Members of an organization with role-based access.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` | PK |
| `org_id` | `uuid` | NOT NULL | — | FK -> `organizations(id) ON DELETE CASCADE` |
| `user_id` | `uuid` | NOT NULL | — | FK -> `profiles(id) ON DELETE CASCADE` |
| `role` | `text` | NOT NULL | `'member'` | CHECK: `owner, admin, member` |
| `invited_at` | `timestamptz` | NOT NULL | `now()` | |
| `accepted_at` | `timestamptz` | YES | — | NULL = pending |

**Constraints:** UNIQUE(`org_id`, `user_id`)

---

### 27. `partners`

Revenue share partner tracking.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` | PK |
| `name` | `text` | NOT NULL | — | |
| `slug` | `text` | NOT NULL | — | UNIQUE |
| `contact_email` | `text` | NOT NULL | — | |
| `contact_name` | `text` | YES | — | |
| `stripe_coupon_id` | `text` | YES | — | |
| `revenue_share_pct` | `numeric(5,2)` | YES | `25.00` | |
| `status` | `text` | YES | `'active'` | CHECK: `active, inactive, pending` |
| `created_at` | `timestamptz` | YES | `now()` | |

### `partner_referrals`

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` | PK |
| `partner_id` | `uuid` | NOT NULL | — | FK -> `partners(id)` |
| `referred_user_id` | `uuid` | NOT NULL | — | FK -> `profiles(id) ON DELETE SET NULL` |
| `signup_at` | `timestamptz` | YES | `now()` | |
| `converted_at` | `timestamptz` | YES | — | |
| `churned_at` | `timestamptz` | YES | — | |
| `monthly_revenue` | `numeric(10,2)` | YES | — | |
| `revenue_share_amount` | `numeric(10,2)` | YES | — | |

**Constraints:** UNIQUE(`partner_id`, `referred_user_id`)

### Additional Tables (from backend migrations or security features)

**`health_checks`** — Periodic health check results (30-day retention).

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` |
| `checked_at` | `timestamptz` | NOT NULL | `now()` |
| `overall_status` | `text` | NOT NULL | CHECK: `healthy, degraded, unhealthy` |
| `sources_json` | `jsonb` | NOT NULL | `'{}'` |
| `components_json` | `jsonb` | NOT NULL | `'{}'` |
| `latency_ms` | `integer` | YES | — |

**`incidents`** — System incidents for public status page.

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` |
| `started_at` | `timestamptz` | NOT NULL | `now()` |
| `resolved_at` | `timestamptz` | YES | — |
| `status` | `text` | NOT NULL | `'ongoing'` CHECK: `ongoing, resolved` |
| `affected_sources` | `text[]` | NOT NULL | `'{}'` |
| `description` | `text` | NOT NULL | `''` |

**`mfa_recovery_codes`** — Bcrypt-hashed TOTP MFA backup codes.

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` |
| `user_id` | `uuid` | NOT NULL | FK -> `profiles(id) ON DELETE CASCADE` |
| `code_hash` | `text` | NOT NULL | — |
| `used_at` | `timestamptz` | YES | — |
| `created_at` | `timestamptz` | NOT NULL | `now()` |

**`mfa_recovery_attempts`** — Brute force tracking for MFA recovery.

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` |
| `user_id` | `uuid` | NOT NULL | FK -> `profiles(id) ON DELETE CASCADE` |
| `attempted_at` | `timestamptz` | NOT NULL | `now()` |
| `success` | `boolean` | NOT NULL | `false` |

---

## Relationships

### Entity-Relationship Summary

```
auth.users (1) ──── (1) profiles
                          │
          ┌───────────────┼───────────────┬──────────────────┐
          │               │               │                  │
    user_subscriptions  search_sessions  pipeline_items  monthly_quota
          │                    │
        plans              search_results_cache
          │                search_results_store
    plan_billing_periods   search_state_transitions
    plan_features
                        conversations ──── messages

                        alerts ──── alert_sent_items
                               ──── alert_runs

                        alert_preferences (1:1 with profiles)

                        organizations ──── organization_members

                        partners ──── partner_referrals
                                ──── profiles.referred_by_partner_id
```

### FK Constraints (Final State After All Migrations)

All user-related FKs have been standardized to reference `profiles(id)` (not `auth.users(id)`), except:

- `profiles.id` -> `auth.users(id) ON DELETE CASCADE` (root FK)
- `mfa_recovery_codes.user_id` -> `profiles(id) ON DELETE CASCADE`
- `mfa_recovery_attempts.user_id` -> `profiles(id) ON DELETE CASCADE`

ON DELETE behaviors:
- **CASCADE** (most tables) — deleting a profile cascades to all user data
- **RESTRICT** — `user_subscriptions.plan_id -> plans(id)` (prevents deleting plans with active subs)
- **RESTRICT** — `organizations.owner_id -> profiles(id)` (prevents deleting org owners)
- **SET NULL** — `partner_referrals.referred_user_id -> profiles(id)` (preserves revenue data)

---

## Indexes

### profiles
| Index | Type | Columns | Condition |
|-------|------|---------|-----------|
| `profiles_pkey` | B-tree (PK) | `id` | — |
| `idx_profiles_is_admin` | B-tree (partial) | `is_admin` | `WHERE is_admin = true` |
| `idx_profiles_email_trgm` | GIN (trigram) | `email` | — (requires `pg_trgm`) |
| `idx_profiles_email_unique` | B-tree (unique, partial) | `email` | `WHERE email IS NOT NULL` |
| `idx_profiles_phone_whatsapp_unique` | B-tree (unique, partial) | `phone_whatsapp` | `WHERE phone_whatsapp IS NOT NULL` |
| `idx_profiles_whatsapp_consent` | B-tree (partial) | `whatsapp_consent` | `WHERE whatsapp_consent = TRUE` |
| `idx_profiles_subscription_status` | B-tree (partial) | `subscription_status` | `WHERE subscription_status != 'trial'` |
| `idx_profiles_context_porte` | B-tree | `context_data->>'porte_empresa'` | `WHERE ... IS NOT NULL` |
| `idx_profiles_referred_by_partner` | B-tree (partial) | `referred_by_partner_id` | `WHERE ... IS NOT NULL` |

### user_subscriptions
| Index | Type | Columns | Condition |
|-------|------|---------|-----------|
| `idx_user_subscriptions_user` | B-tree | `user_id` | — |
| `idx_user_subscriptions_active` | B-tree (partial) | `user_id, is_active` | `WHERE is_active = true` |
| `idx_user_subscriptions_billing` | B-tree (partial) | `user_id, billing_period, is_active` | `WHERE is_active = true` |
| `idx_user_subscriptions_stripe_sub_id` | B-tree (unique, partial) | `stripe_subscription_id` | `WHERE ... IS NOT NULL` |
| `idx_user_subscriptions_customer_id` | B-tree (partial) | `stripe_customer_id` | `WHERE ... IS NOT NULL` |
| `idx_user_subscriptions_first_failed_at` | B-tree (partial) | `first_failed_at` | `WHERE ... IS NOT NULL` |

### search_sessions
| Index | Type | Columns | Condition |
|-------|------|---------|-----------|
| `idx_search_sessions_user` | B-tree | `user_id` | — |
| `idx_search_sessions_created` | B-tree | `user_id, created_at DESC` | — |
| `idx_search_sessions_search_id` | B-tree (partial) | `search_id` | `WHERE search_id IS NOT NULL` |
| `idx_search_sessions_status` | B-tree (partial) | `status` | `WHERE status IN ('created','processing')` |
| `idx_search_sessions_inflight` | B-tree (partial) | `status, started_at` | `WHERE status IN ('created','processing')` |
| `idx_search_sessions_user_status_created` | B-tree | `user_id, status, created_at DESC` | — |

### search_results_cache
| Index | Type | Columns | Condition |
|-------|------|---------|-----------|
| `idx_search_cache_user` | B-tree | `user_id, created_at DESC` | — |
| `idx_search_cache_params_hash` | B-tree | `params_hash` | — |
| `idx_search_cache_fetched_at` | B-tree | `fetched_at` | — |
| `idx_search_cache_degraded` | B-tree (partial) | `degraded_until` | `WHERE ... IS NOT NULL` |
| `idx_search_cache_priority` | B-tree | `user_id, priority, last_accessed_at` | — |
| `idx_search_cache_global_hash` | B-tree | `params_hash_global, created_at DESC` | — |

### search_results_store
| Index | Type | Columns |
|-------|------|---------|
| `idx_search_results_user` | B-tree | `user_id` |
| `idx_search_results_expires` | B-tree | `expires_at` |
| `idx_search_results_store_user_expires` | B-tree | `user_id, expires_at` |

### Other Notable Indexes
| Table | Index | Columns |
|-------|-------|---------|
| `monthly_quota` | `idx_monthly_quota_user_month` | `user_id, month_year` |
| `stripe_webhook_events` | `idx_webhook_events_type` | `type, processed_at` |
| `stripe_webhook_events` | `idx_webhook_events_recent` | `processed_at DESC` |
| `conversations` | `idx_conversations_user_id` | `user_id` |
| `conversations` | `idx_conversations_status` | `status` |
| `conversations` | `idx_conversations_last_message` | `last_message_at DESC` |
| `conversations` | `idx_conversations_unanswered` | `created_at` WHERE `first_response_at IS NULL AND status != 'resolvido'` |
| `messages` | `idx_messages_conversation` | `conversation_id, created_at` |
| `messages` | `idx_messages_unread_by_user` | `conversation_id` WHERE `is_admin_reply=true AND read_by_user=false` |
| `messages` | `idx_messages_unread_by_admin` | `conversation_id` WHERE `is_admin_reply=false AND read_by_admin=false` |
| `pipeline_items` | `idx_pipeline_user_stage` | `user_id, stage` |
| `pipeline_items` | `idx_pipeline_encerramento` | `data_encerramento` WHERE `stage NOT IN ('enviada','resultado')` |
| `pipeline_items` | `idx_pipeline_user_created` | `user_id, created_at DESC` |
| `classification_feedback` | `idx_feedback_sector_verdict` | `setor_id, user_verdict, created_at` |
| `classification_feedback` | `idx_feedback_user_created` | `user_id, created_at` |
| `audit_events` | `idx_audit_events_event_type` | `event_type` |
| `audit_events` | `idx_audit_events_timestamp` | `timestamp` |
| `audit_events` | `idx_audit_events_actor` | `actor_id_hash` WHERE NOT NULL |
| `audit_events` | `idx_audit_events_type_timestamp` | `event_type, timestamp DESC` |
| `alerts` | `idx_alerts_user_id` | `user_id` |
| `alerts` | `idx_alerts_active` | `user_id, active` WHERE `active = true` |
| `alert_sent_items` | `idx_alert_sent_items_dedup` | UNIQUE `alert_id, item_id` |
| `alert_runs` | `idx_alert_runs_alert_id` | `alert_id` |
| `alert_runs` | `idx_alert_runs_run_at` | `run_at DESC` |
| `reconciliation_log` | `idx_reconciliation_log_run_at` | `run_at DESC` |
| `google_sheets_exports` | `idx_google_sheets_exports_search_params` | GIN `search_params` |
| `organizations` | `idx_organizations_owner` | `owner_id` |
| `organization_members` | `idx_org_members_org` | `org_id` |
| `organization_members` | `idx_org_members_user` | `user_id` |
| `partners` | `idx_partners_slug` | `slug` |
| `partners` | `idx_partners_status` | `status` |
| `partner_referrals` | `idx_partner_referrals_partner_id` | `partner_id` |
| `partner_referrals` | `idx_partner_referrals_referred_user_id` | `referred_user_id` |

---

## RLS Policies

All tables have RLS enabled. Policies follow these patterns:

### Pattern 1: User-only access (`auth.uid() = user_id`)
Used by: `profiles`, `user_subscriptions`, `monthly_quota`, `search_sessions`, `pipeline_items`, `user_oauth_tokens`, `google_sheets_exports`, `classification_feedback`, `alert_preferences`, `alerts`, `search_results_cache`, `search_results_store`, `conversations` (user's own), `messages` (via conversation ownership)

### Pattern 2: Service role full access (`TO service_role USING (true) WITH CHECK (true)`)
Applied to every table that the backend writes to. After migration 20260304200000, all service_role policies use `TO service_role` (not `auth.role() = 'service_role'`).

### Pattern 3: Admin access (is_admin check)
Used by: `stripe_webhook_events`, `audit_events`, `reconciliation_log`, `conversations` (admin can see all)

### Pattern 4: Public read (`USING (true)`)
Used by: `plans`, `plan_features`, `plan_billing_periods`

### Detailed Policy Listing

| Table | Policy | Operation | Logic |
|-------|--------|-----------|-------|
| **profiles** | `profiles_select_own` | SELECT | `auth.uid() = id` |
| | `profiles_update_own` | UPDATE | `auth.uid() = id` |
| | `profiles_insert_own` | INSERT | `auth.uid() = id` (TO authenticated) |
| | `profiles_insert_service` | INSERT | `true` (TO service_role) |
| | `profiles_service_all` | ALL | `true` (TO service_role) |
| **plans** | `plans_select_all` | SELECT | `true` (public) |
| **plan_billing_periods** | `plan_billing_periods_public_read` | SELECT | `true` (TO authenticated, anon) |
| | `plan_billing_periods_service_all` | ALL | `true` (TO service_role) |
| **plan_features** | `plan_features_select_all` | SELECT | `true` (public) |
| **user_subscriptions** | `subscriptions_select_own` | SELECT | `auth.uid() = user_id` |
| | `Service role can manage subscriptions` | ALL | `true` (TO service_role) |
| **monthly_quota** | `Users can view own quota` | SELECT | `auth.uid() = user_id` |
| | `Service role can manage quota` | ALL | `true` (TO service_role) |
| **search_sessions** | `sessions_select_own` | SELECT | `auth.uid() = user_id` |
| | `sessions_insert_own` | INSERT | `auth.uid() = user_id` |
| | `Service role can manage search sessions` | ALL | `true` (TO service_role) |
| **search_results_cache** | `Users can read own search cache` | SELECT | `auth.uid() = user_id` |
| | `Service role full access on search_results_cache` | ALL | `true` (TO service_role) |
| **search_results_store** | `Users can read own results` | SELECT | `auth.uid() = user_id` |
| | `service_role_all` | ALL | `true` (TO service_role) |
| **search_state_transitions** | `Users can read own transitions` | SELECT | `search_id IN (SELECT search_id FROM search_sessions WHERE user_id = auth.uid())` |
| | `Service role can insert transitions` | INSERT | `true` (TO service_role) |
| **stripe_webhook_events** | `webhook_events_insert_service` | INSERT | `true` (TO service_role) |
| | `webhook_events_select_admin` | SELECT | `is_admin = true` (TO authenticated) |
| | `webhook_events_service_role_select` | SELECT | `true` (TO service_role) |
| **conversations** | `conversations_select_own` | SELECT | `auth.uid() = user_id OR is_admin` |
| | `conversations_insert_own` | INSERT | `auth.uid() = user_id` |
| | `conversations_update_admin` | UPDATE | `is_admin` |
| | `conversations_service_all` | ALL | `true` (TO service_role) |
| **messages** | `messages_select` | SELECT | Via conversation ownership or is_admin |
| | `messages_insert_user` | INSERT | `auth.uid() = sender_id` + conversation ownership |
| | `messages_update_read` | UPDATE | Via conversation ownership or is_admin |
| | `messages_service_all` | ALL | `true` (TO service_role) |
| **pipeline_items** | Per-operation user policies | SELECT/INSERT/UPDATE/DELETE | `auth.uid() = user_id` |
| | `Service role full access on pipeline_items` | ALL | `true` (TO service_role) |
| **classification_feedback** | Per-operation user policies | SELECT/INSERT/UPDATE/DELETE | `auth.uid() = user_id` |
| **audit_events** | `Admins can read audit events` | SELECT | `is_admin = true` |
| | `Service role can manage audit events` | ALL | `true` (TO service_role) |
| **alert_preferences** | Per-operation user policies | SELECT/INSERT/UPDATE | `auth.uid() = user_id` |
| | `service_role_all` | ALL | `true` (TO service_role) |
| **alerts** | Per-operation user policies | SELECT/INSERT/UPDATE/DELETE | `auth.uid() = user_id` |
| | `Service role full access to alerts` | ALL | `true` (TO service_role) |
| **alert_sent_items** | `Users can view own alert sent items` | SELECT | Via alert ownership join |
| | `Service role full access to alert_sent_items` | ALL | `true` (TO service_role) |
| **alert_runs** | `Users can view own alert runs` | SELECT | Via alert ownership join |
| | `Service role full access to alert_runs` | ALL | `true` (TO service_role) |
| **trial_email_log** | (no user policies) | — | Service role only (bypasses RLS) |
| **reconciliation_log** | `Admin read reconciliation_log` | SELECT | `is_admin = true` |
| | `service_role_all` | ALL | `true` (TO service_role) |
| **organizations** | Owner/admin SELECT, owner INSERT/UPDATE | Various | Via `owner_id` or membership join |
| | `service_role_all` | ALL | `true` (TO service_role) |
| **organization_members** | User can see own membership, admin can see all | Various | Complex membership-based policies |
| | `service_role_all` | ALL | `true` (TO service_role) |
| **partners** | `partners_admin_all` | ALL | `is_admin = true` |
| | `partners_self_read` | SELECT | `contact_email = auth user email` |
| | `service_role_all` | ALL | `true` (TO service_role) |
| **partner_referrals** | `partner_referrals_admin_all` | ALL | `is_admin = true` |
| | `partner_referrals_partner_read` | SELECT | Via partner contact_email |
| | `service_role_all` | ALL | `true` (TO service_role) |
| **health_checks** | `service_role_all` | ALL | `true` (TO service_role) |
| **incidents** | `service_role_all` | ALL | `true` (TO service_role) |
| **mfa_recovery_codes** | `Users can view own recovery codes` | SELECT | `auth.uid() = user_id` (TO authenticated) |
| | `Service role full access to recovery codes` | ALL | `true` (TO service_role) |
| **mfa_recovery_attempts** | `Service role full access to recovery attempts` | ALL | `true` (TO service_role) |

---

## Functions and Triggers

### Functions

| Function | Returns | Security | Purpose |
|----------|---------|----------|---------|
| `handle_new_user()` | trigger | DEFINER | Auto-creates profile row on auth.users INSERT. Includes phone normalization, plan_type='free_trial', context_data default |
| `update_updated_at()` | trigger | — | Generic updated_at = now() trigger function |
| `set_updated_at()` | trigger | — | Canonical version (consolidated from duplicates) |
| `increment_quota_atomic(uuid, varchar, int)` | TABLE(new_count, was_at_limit, previous_count) | — | Atomic quota increment with row-level locking |
| `check_and_increment_quota(uuid, varchar, int)` | TABLE(allowed, new_count, previous_count, quota_remaining) | — | Atomic check + increment (primary quota path) |
| `increment_quota_fallback_atomic(uuid, text, int)` | TABLE(new_count) | — | Simplified fallback for STORY-318 concurrency fix |
| `get_user_billing_period(uuid)` | varchar(10) | DEFINER | Quick billing period lookup (default: 'monthly') |
| `user_has_feature(uuid, varchar)` | boolean | DEFINER | Check if user has specific plan feature |
| `get_user_features(uuid)` | text[] | DEFINER | Get all enabled feature keys for user |
| `get_conversations_with_unread_count(uuid, boolean, text, int, int)` | TABLE | DEFINER | Eliminates N+1 query in conversation list |
| `get_analytics_summary(uuid, timestamptz, timestamptz)` | TABLE | DEFINER | Optimized analytics summary (single query) |
| `get_table_columns_simple(text)` | TABLE(column_name) | DEFINER | Schema validation helper (CRIT-004) |
| `cleanup_search_cache_per_user()` | trigger | DEFINER | Priority-aware eviction (limit 10/user, cold first) |
| `update_conversation_last_message()` | trigger | — | Auto-updates conversation.last_message_at |
| `create_default_alert_preferences()` | trigger | — | Creates alert_preferences on profile insert |

### Triggers

| Trigger | Table | Event | Function |
|---------|-------|-------|----------|
| `on_auth_user_created` | `auth.users` | AFTER INSERT | `handle_new_user()` |
| `profiles_updated_at` | `profiles` | BEFORE UPDATE | `update_updated_at()` |
| `plans_updated_at` | `plans` | BEFORE UPDATE | `update_updated_at()` |
| `user_subscriptions_updated_at` | `user_subscriptions` | BEFORE UPDATE | `update_updated_at()` |
| `plan_features_updated_at` | `plan_features` | BEFORE UPDATE | `update_updated_at()` |
| `tr_pipeline_items_updated_at` | `pipeline_items` | BEFORE UPDATE | `set_updated_at()` |
| `trigger_alert_preferences_updated_at` | `alert_preferences` | BEFORE UPDATE | `set_updated_at()` |
| `trigger_alerts_updated_at` | `alerts` | BEFORE UPDATE | `set_updated_at()` |
| `tr_organizations_updated_at` | `organizations` | BEFORE UPDATE | `update_updated_at()` |
| `trg_update_conversation_last_message` | `messages` | AFTER INSERT | `update_conversation_last_message()` |
| `trg_cleanup_search_cache` | `search_results_cache` | AFTER INSERT | `cleanup_search_cache_per_user()` |
| `trigger_create_alert_preferences_on_profile` | `profiles` | AFTER INSERT | `create_default_alert_preferences()` |

**Removed triggers:**
- `trg_sync_profile_plan_type` on `user_subscriptions` — dropped in migration 030 (referenced non-existent `status` column; plan sync now handled by billing.py Stripe webhooks).

---

## Custom Types

### `alert_frequency`

```sql
CREATE TYPE alert_frequency AS ENUM ('daily', 'twice_weekly', 'weekly', 'off');
```

Used by: `alert_preferences.frequency`

---

## Scheduled Jobs

pg_cron extension is used for automated retention cleanup.

| Job Name | Schedule | Action |
|----------|----------|--------|
| `cleanup-monthly-quota` | `0 2 1 * *` (1st of month, 2 AM UTC) | DELETE monthly_quota older than 24 months |
| `cleanup-webhook-events` | `0 3 * * *` (daily, 3 AM UTC) | DELETE stripe_webhook_events older than 90 days |
| `cleanup-audit-events` | `0 4 1 * *` (1st of month, 4 AM UTC) | DELETE audit_events older than 12 months |
| `cleanup-cold-cache-entries` | `0 5 * * *` (daily, 5 AM UTC) | DELETE search_results_cache WHERE priority='cold' AND older than 7 days |
| `cleanup-expired-search-results` | `0 4 * * *` (daily, 4 AM UTC) | DELETE search_results_store expired > 7 days |

---

## Extensions

| Extension | Purpose |
|-----------|---------|
| `pg_trgm` | Trigram indexes for fuzzy text search (profiles.email ILIKE) |
| `pg_cron` | Scheduled retention cleanup jobs |
