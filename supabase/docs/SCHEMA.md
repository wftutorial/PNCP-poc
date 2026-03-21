# SmartLic Database Schema Documentation

> Generated: 2026-03-21 | Source: 85 Supabase migrations + 10 backend migrations
> Database: PostgreSQL 17 (Supabase Cloud)
> Supabase Project: fqqyovlzdzimiwfofdjk

---

## Table of Contents

1. [Table Categories](#table-categories)
2. [Tables](#tables)
3. [Custom Types & Enums](#custom-types--enums)
4. [Functions (RPC)](#functions-rpc)
5. [Triggers](#triggers)
6. [Indexes](#indexes)
7. [RLS Policies](#rls-policies)
8. [pg_cron Scheduled Jobs](#pg_cron-scheduled-jobs)
9. [Entity Relationships](#entity-relationships)
10. [Extensions](#extensions)

---

## Table Categories

| Domain | Tables |
|--------|--------|
| **Auth & Profiles** | `profiles`, `mfa_recovery_codes`, `mfa_recovery_attempts` |
| **Search** | `search_sessions`, `search_state_transitions`, `search_results_cache`, `search_results_store` |
| **Billing** | `plans`, `plan_billing_periods`, `plan_features`, `user_subscriptions`, `monthly_quota`, `stripe_webhook_events`, `reconciliation_log` |
| **Pipeline** | `pipeline_items` |
| **Messaging** | `conversations`, `messages` |
| **Alerts** | `alerts`, `alert_sent_items`, `alert_runs`, `alert_preferences` |
| **Feedback** | `classification_feedback` |
| **OAuth & Export** | `user_oauth_tokens`, `google_sheets_exports` |
| **Audit & Compliance** | `audit_events`, `trial_email_log` |
| **Monitoring** | `health_checks`, `incidents` |
| **Organizations** | `organizations`, `organization_members` |
| **Partners** | `partners`, `partner_referrals` |

**Total: 27 public tables**

---

## Tables

### profiles
Extends `auth.users` with application-specific fields. Central user table -- most FKs in the system reference `profiles(id)`.

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| `id` | uuid | NO | - | PK, FK -> auth.users(id) ON DELETE CASCADE |
| `email` | text | NO | - | UNIQUE (idx_profiles_email_unique) |
| `full_name` | text | YES | - | |
| `company` | text | YES | - | |
| `plan_type` | text | NO | `'free_trial'` | CHECK: free_trial, consultor_agil, maquina, sala_guerra, master, smartlic_pro, consultoria |
| `avatar_url` | text | YES | - | |
| `is_admin` | boolean | NO | `false` | Partial index WHERE is_admin = true |
| `sector` | text | YES | - | |
| `phone_whatsapp` | text | YES | - | CHECK: `^[0-9]{10,11}$`, UNIQUE (partial WHERE NOT NULL) |
| `whatsapp_consent` | boolean | YES | `false` | |
| `whatsapp_consent_at` | timestamptz | YES | - | |
| `context_data` | jsonb | YES | `'{}'::jsonb` | Onboarding wizard business context |
| `subscription_status` | text | YES | `'trial'` | CHECK: trial, active, canceling, past_due, expired |
| `trial_expires_at` | timestamptz | YES | - | |
| `subscription_end_date` | timestamptz | YES | - | |
| `email_unsubscribed` | boolean | YES | `false` | LGPD compliance |
| `email_unsubscribed_at` | timestamptz | YES | - | |
| `marketing_emails_enabled` | boolean | NO | `true` | |
| `referred_by_partner_id` | uuid | YES | - | FK -> partners(id) |
| `created_at` | timestamptz | NO | `now()` | |
| `updated_at` | timestamptz | NO | `now()` | Auto-updated via trigger |

---

### plans
Plan catalog (public pricing data).

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| `id` | text | NO | - | PK |
| `name` | text | NO | - | |
| `description` | text | YES | - | |
| `max_searches` | int | YES | - | NULL = unlimited |
| `price_brl` | numeric(10,2) | NO | `0` | |
| `duration_days` | int | YES | - | NULL = perpetual |
| `stripe_price_id` | text | YES | - | DEPRECATED: use period-specific columns |
| `stripe_price_id_monthly` | text | YES | - | |
| `stripe_price_id_semiannual` | text | YES | - | |
| `stripe_price_id_annual` | text | YES | - | |
| `is_active` | boolean | NO | `true` | |
| `created_at` | timestamptz | NO | `now()` | |
| `updated_at` | timestamptz | NO | `now()` | Auto-updated via trigger |

**Seed data:** free, pack_5, pack_10, pack_20 (inactive), monthly, annual (inactive), master, consultor_agil (inactive, legacy), maquina (inactive, legacy), sala_guerra (inactive, legacy), smartlic_pro (active), consultoria (active)

---

### plan_billing_periods
Multi-period pricing for plans. Source of truth for Stripe price IDs.

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| `id` | uuid | NO | `gen_random_uuid()` | PK |
| `plan_id` | text | NO | - | FK -> plans(id) ON DELETE CASCADE |
| `billing_period` | text | NO | - | CHECK: monthly, semiannual, annual |
| `price_cents` | integer | NO | - | |
| `discount_percent` | integer | YES | `0` | |
| `stripe_price_id` | text | YES | - | |
| `created_at` | timestamptz | YES | `now()` | |
| `updated_at` | timestamptz | YES | `now()` | Auto-updated via trigger |

UNIQUE: `(plan_id, billing_period)`

---

### plan_features
Billing-period-specific feature flags.

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| `id` | serial | NO | auto | PK |
| `plan_id` | text | NO | - | FK -> plans(id) ON DELETE CASCADE |
| `billing_period` | varchar(10) | NO | - | CHECK: monthly, semiannual, annual |
| `feature_key` | varchar(100) | NO | - | |
| `enabled` | boolean | NO | `true` | |
| `metadata` | jsonb | YES | `'{}'` | |
| `created_at` | timestamptz | NO | `now()` | |
| `updated_at` | timestamptz | NO | `now()` | Auto-updated via trigger |

UNIQUE: `(plan_id, billing_period, feature_key)`

---

### user_subscriptions
Active and historical user subscription records.

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| `id` | uuid | NO | `gen_random_uuid()` | PK |
| `user_id` | uuid | NO | - | FK -> profiles(id) ON DELETE CASCADE |
| `plan_id` | text | NO | - | FK -> plans(id) ON DELETE RESTRICT |
| `credits_remaining` | int | YES | - | NULL = unlimited |
| `starts_at` | timestamptz | NO | `now()` | |
| `expires_at` | timestamptz | YES | - | NULL = never expires |
| `stripe_subscription_id` | text | YES | - | UNIQUE (partial WHERE NOT NULL) |
| `stripe_customer_id` | text | YES | - | Indexed (partial WHERE NOT NULL) |
| `is_active` | boolean | NO | `true` | |
| `billing_period` | varchar(10) | NO | `'monthly'` | CHECK: monthly, semiannual, annual |
| `annual_benefits` | jsonb | NO | `'{}'` | |
| `subscription_status` | text | YES | `'active'` | CHECK: active, trialing, past_due, canceled, expired |
| `first_failed_at` | timestamptz | YES | - | Dunning tracking |
| `version` | integer | NO | `1` | Optimistic locking |
| `created_at` | timestamptz | NO | `now()` | |
| `updated_at` | timestamptz | NO | `now()` | Auto-updated via trigger |

---

### monthly_quota
Tracks monthly search usage per user for plan-based pricing.

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| `id` | uuid | NO | `gen_random_uuid()` | PK |
| `user_id` | uuid | NO | - | FK -> profiles(id) ON DELETE CASCADE |
| `month_year` | varchar(7) | NO | - | Format: "YYYY-MM" |
| `searches_count` | int | NO | `0` | |
| `created_at` | timestamptz | NO | `now()` | |
| `updated_at` | timestamptz | NO | `now()` | |

UNIQUE: `(user_id, month_year)`. Retention: 24 months (pg_cron).

---

### search_sessions
User search history with lifecycle tracking.

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| `id` | uuid | NO | `gen_random_uuid()` | PK |
| `user_id` | uuid | NO | - | FK -> profiles(id) ON DELETE CASCADE |
| `search_id` | uuid | YES | - | Links to SSE/ARQ |
| `sectors` | text[] | NO | - | |
| `ufs` | text[] | NO | - | |
| `data_inicial` | date | NO | - | |
| `data_final` | date | NO | - | |
| `custom_keywords` | text[] | YES | - | |
| `total_raw` | int | NO | `0` | |
| `total_filtered` | int | NO | `0` | |
| `valor_total` | numeric(14,2) | YES | `0` | |
| `resumo_executivo` | text | YES | - | |
| `destaques` | text[] | YES | - | |
| `excel_storage_path` | text | YES | - | |
| `status` | text | NO | `'created'` | CHECK: created, processing, completed, failed, timed_out, cancelled |
| `error_message` | text | YES | - | |
| `error_code` | text | YES | - | |
| `started_at` | timestamptz | NO | `now()` | |
| `completed_at` | timestamptz | YES | - | |
| `duration_ms` | integer | YES | - | |
| `pipeline_stage` | text | YES | - | |
| `raw_count` | integer | YES | `0` | |
| `response_state` | text | YES | - | live, cached, degraded, empty_failure |
| `failed_ufs` | text[] | YES | - | |
| `created_at` | timestamptz | NO | `now()` | |

Retention: 12 months (pg_cron).

---

### search_state_transitions
Audit trail for search state machine transitions. Fire-and-forget inserts.

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| `id` | uuid | NO | `gen_random_uuid()` | PK |
| `search_id` | uuid | NO | - | No FK (search_sessions.search_id not unique) |
| `user_id` | uuid | YES | - | FK -> profiles(id) ON DELETE CASCADE |
| `from_state` | text | YES | - | NULL for initial CREATED |
| `to_state` | text | NO | - | |
| `stage` | text | YES | - | |
| `details` | jsonb | YES | `'{}'` | |
| `duration_since_previous_ms` | integer | YES | - | |
| `created_at` | timestamptz | NO | `now()` | |

Retention: 30 days (pg_cron).

---

### search_results_cache
L2 persistent cache (SWR pattern). Max entries per user with priority-based eviction.

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| `id` | uuid | NO | `gen_random_uuid()` | PK |
| `user_id` | uuid | NO | - | FK -> profiles(id) ON DELETE CASCADE |
| `params_hash` | text | NO | - | |
| `params_hash_global` | text | YES | - | Cross-user cache sharing |
| `search_params` | jsonb | NO | - | |
| `results` | jsonb | NO | - | CHECK: octet_length <= 2MB |
| `total_results` | integer | NO | `0` | |
| `sources_json` | jsonb | NO | `'["pncp"]'` | |
| `fetched_at` | timestamptz | NO | `now()` | |
| `priority` | text | NO | `'cold'` | CHECK: hot, warm, cold |
| `access_count` | integer | NO | `0` | |
| `last_accessed_at` | timestamptz | YES | - | |
| `last_success_at` | timestamptz | YES | - | |
| `last_attempt_at` | timestamptz | YES | - | |
| `fail_streak` | integer | NO | `0` | |
| `degraded_until` | timestamptz | YES | - | |
| `coverage` | jsonb | YES | - | |
| `fetch_duration_ms` | integer | YES | - | |
| `created_at` | timestamptz | NO | `now()` | |

UNIQUE: `(user_id, params_hash)`. Cold entries > 7 days cleaned by pg_cron.

---

### search_results_store
L3 persistent storage. Prevents "Busca nao encontrada" after L1/L2 TTL expiry.

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| `search_id` | uuid | NO | - | PK |
| `user_id` | uuid | NO | - | FK -> profiles(id) ON DELETE CASCADE |
| `results` | jsonb | NO | - | CHECK: octet_length < 2MB |
| `sector` | text | YES | - | |
| `ufs` | text[] | YES | - | |
| `total_filtered` | int | YES | `0` | |
| `created_at` | timestamptz | YES | `now()` | |
| `expires_at` | timestamptz | YES | `now() + 24h` | |

Retention: daily pg_cron cleans expired rows.

---

### stripe_webhook_events
Idempotency store for Stripe webhook processing.

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| `id` | varchar(255) | NO | - | PK, CHECK: `^evt_` |
| `type` | varchar(100) | NO | - | |
| `processed_at` | timestamptz | NO | `now()` | |
| `payload` | jsonb | YES | - | |
| `status` | varchar(20) | NO | `'completed'` | |
| `received_at` | timestamptz | YES | `now()` | |

Retention: 90 days (pg_cron).

---

### pipeline_items
Kanban pipeline for tracking procurement opportunities.

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| `id` | uuid | NO | `gen_random_uuid()` | PK |
| `user_id` | uuid | NO | - | FK -> profiles(id) ON DELETE CASCADE |
| `pncp_id` | text | NO | - | |
| `objeto` | text | NO | - | |
| `orgao` | text | YES | - | |
| `uf` | text | YES | - | |
| `valor_estimado` | numeric | YES | - | |
| `data_encerramento` | timestamptz | YES | - | |
| `link_pncp` | text | YES | - | |
| `stage` | text | NO | `'descoberta'` | CHECK: descoberta, analise, preparando, enviada, resultado |
| `notes` | text | YES | - | |
| `version` | integer | NO | `1` | Optimistic locking |
| `search_id` | text | YES | - | Traceability to search origin |
| `created_at` | timestamptz | NO | `now()` | |
| `updated_at` | timestamptz | NO | `now()` | Auto-updated via trigger |

UNIQUE: `(user_id, pncp_id)`

---

### conversations
InMail support messaging system.

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| `id` | uuid | NO | `gen_random_uuid()` | PK |
| `user_id` | uuid | NO | - | FK -> profiles(id) ON DELETE CASCADE |
| `subject` | text | NO | - | CHECK: length <= 200 |
| `category` | text | NO | - | CHECK: suporte, sugestao, funcionalidade, bug, outro |
| `status` | text | NO | `'aberto'` | CHECK: aberto, respondido, resolvido |
| `last_message_at` | timestamptz | NO | `now()` | |
| `first_response_at` | timestamptz | YES | - | SLA tracking |
| `created_at` | timestamptz | NO | `now()` | |
| `updated_at` | timestamptz | NO | `now()` | |

Retention: 24 months (pg_cron).

---

### messages

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| `id` | uuid | NO | `gen_random_uuid()` | PK |
| `conversation_id` | uuid | NO | - | FK -> conversations(id) ON DELETE CASCADE |
| `sender_id` | uuid | NO | - | FK -> profiles(id) ON DELETE CASCADE |
| `body` | text | NO | - | CHECK: length 1-5000 |
| `is_admin_reply` | boolean | NO | `false` | |
| `read_by_user` | boolean | NO | `false` | |
| `read_by_admin` | boolean | NO | `false` | |
| `created_at` | timestamptz | NO | `now()` | |

Retention: 24 months (pg_cron orphan safety net).

---

### alerts
User-defined email alert filters.

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| `id` | uuid | NO | `gen_random_uuid()` | PK |
| `user_id` | uuid | NO | - | FK -> profiles(id) ON DELETE CASCADE |
| `name` | text | NO | `''` | |
| `filters` | jsonb | NO | `'{}'` | Schema: {setor, ufs[], valor_min, valor_max, keywords[]} |
| `active` | boolean | NO | `true` | |
| `created_at` | timestamptz | NO | `now()` | |
| `updated_at` | timestamptz | NO | `now()` | Auto-updated via trigger |

---

### alert_sent_items
Dedup tracking for alert emails.

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| `id` | uuid | NO | `gen_random_uuid()` | PK |
| `alert_id` | uuid | NO | - | FK -> alerts(id) ON DELETE CASCADE |
| `item_id` | text | NO | - | |
| `sent_at` | timestamptz | NO | `now()` | |

UNIQUE: `(alert_id, item_id)`. Retention: 180 days (pg_cron).

---

### alert_runs
Alert execution history.

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| `id` | uuid | NO | `gen_random_uuid()` | PK |
| `alert_id` | uuid | NO | - | FK -> alerts(id) ON DELETE CASCADE |
| `run_at` | timestamptz | NO | `now()` | |
| `items_found` | integer | NO | `0` | |
| `items_sent` | integer | NO | `0` | |
| `status` | text | NO | `'pending'` | CHECK: pending, running, completed, failed, matched, no_results, no_match, all_deduped, error |

Retention: 90 days completed only (pg_cron).

---

### alert_preferences
Per-user email digest scheduling.

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| `id` | uuid | NO | `gen_random_uuid()` | PK |
| `user_id` | uuid | NO | - | FK -> profiles(id) ON DELETE CASCADE, UNIQUE |
| `frequency` | alert_frequency | NO | `'daily'` | ENUM: daily, twice_weekly, weekly, off |
| `enabled` | boolean | NO | `true` | |
| `last_digest_sent_at` | timestamptz | YES | - | |
| `created_at` | timestamptz | NO | `now()` | |
| `updated_at` | timestamptz | NO | `now()` | Auto-updated via trigger |

Auto-created for new users via trigger on profiles INSERT.

---

### classification_feedback
User feedback on classification accuracy.

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| `id` | uuid | NO | `gen_random_uuid()` | PK |
| `user_id` | uuid | NO | - | FK -> profiles(id) ON DELETE CASCADE |
| `search_id` | uuid | NO | - | |
| `bid_id` | text | NO | - | |
| `setor_id` | text | NO | - | |
| `user_verdict` | text | NO | - | CHECK: false_positive, false_negative, correct |
| `reason` | text | YES | - | |
| `category` | text | YES | - | CHECK: wrong_sector, irrelevant_modality, too_small, too_large, closed, other |
| `bid_objeto` | text | YES | - | |
| `bid_valor` | decimal | YES | - | |
| `bid_uf` | text | YES | - | |
| `confidence_score` | integer | YES | - | |
| `relevance_source` | text | YES | - | |
| `created_at` | timestamptz | YES | `now()` | |

UNIQUE: `(user_id, search_id, bid_id)`. Retention: 24 months (pg_cron).

---

### user_oauth_tokens
Encrypted OAuth 2.0 tokens for third-party integrations.

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| `id` | uuid | NO | `gen_random_uuid()` | PK |
| `user_id` | uuid | NO | - | FK -> profiles(id) ON DELETE CASCADE |
| `provider` | varchar(50) | NO | - | CHECK: google, microsoft, dropbox |
| `access_token` | text | NO | - | AES-256 encrypted |
| `refresh_token` | text | YES | - | AES-256 encrypted |
| `expires_at` | timestamptz | NO | - | |
| `scope` | text | NO | - | |
| `created_at` | timestamptz | YES | `now()` | |
| `updated_at` | timestamptz | YES | `now()` | |

UNIQUE: `(user_id, provider)`

---

### google_sheets_exports
Export history for Google Sheets.

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| `id` | uuid | NO | `gen_random_uuid()` | PK |
| `user_id` | uuid | NO | - | FK -> profiles(id) ON DELETE CASCADE |
| `spreadsheet_id` | varchar(255) | NO | - | |
| `spreadsheet_url` | text | NO | - | |
| `search_params` | jsonb | NO | - | GIN index |
| `total_rows` | int | NO | - | CHECK: >= 0 |
| `created_at` | timestamptz | NO | `now()` | |
| `updated_at` | timestamptz | NO | `now()` | Auto-updated via trigger (renamed from last_updated_at) |

---

### audit_events
Persistent audit log. All PII stored as SHA-256 hashes (LGPD/GDPR).

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| `id` | uuid | NO | `gen_random_uuid()` | PK |
| `timestamp` | timestamptz | NO | `now()` | |
| `event_type` | text | NO | - | |
| `actor_id_hash` | text | YES | - | SHA-256 truncated 16 hex |
| `target_id_hash` | text | YES | - | SHA-256 truncated 16 hex |
| `details` | jsonb | YES | - | |
| `ip_hash` | text | YES | - | SHA-256 truncated 16 hex |

Retention: 12 months (pg_cron).

---

### trial_email_log
Tracks trial reminder emails sent per user.

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| `id` | uuid | NO | `gen_random_uuid()` | PK |
| `user_id` | uuid | NO | - | FK -> profiles(id) ON DELETE CASCADE |
| `email_type` | text | NO | - | midpoint, expiring, last_day, expired |
| `email_number` | integer | YES | - | CHECK: 1-6 |
| `opened_at` | timestamptz | YES | - | Resend webhook |
| `clicked_at` | timestamptz | YES | - | Resend webhook |
| `resend_email_id` | text | YES | - | |
| `sent_at` | timestamptz | NO | `now()` | |

UNIQUE: `(user_id, email_number)`

---

### reconciliation_log
Stripe-to-DB sync audit trail.

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| `id` | uuid | NO | `gen_random_uuid()` | PK |
| `run_at` | timestamptz | NO | `now()` | |
| `total_checked` | int | NO | `0` | |
| `divergences_found` | int | NO | `0` | |
| `auto_fixed` | int | NO | `0` | |
| `manual_review` | int | NO | `0` | |
| `duration_ms` | int | NO | `0` | |
| `details` | jsonb | YES | `'[]'` | |

---

### health_checks
Periodic health check results for uptime calculation.

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| `id` | uuid | NO | `gen_random_uuid()` | PK |
| `checked_at` | timestamptz | NO | `now()` | |
| `overall_status` | text | NO | - | CHECK: healthy, degraded, unhealthy |
| `sources_json` | jsonb | NO | `'{}'` | |
| `components_json` | jsonb | NO | `'{}'` | |
| `latency_ms` | integer | YES | - | |

Retention: 30 days (pg_cron).

---

### incidents
System incidents for public status page.

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| `id` | uuid | NO | `gen_random_uuid()` | PK |
| `started_at` | timestamptz | NO | `now()` | |
| `resolved_at` | timestamptz | YES | - | |
| `status` | text | NO | `'ongoing'` | CHECK: ongoing, resolved |
| `affected_sources` | text[] | NO | `'{}'` | |
| `description` | text | NO | `''` | |
| `updated_at` | timestamptz | NO | `now()` | Auto-updated via trigger |

Retention: 90 days (pg_cron).

---

### mfa_recovery_codes
Bcrypt-hashed recovery codes for TOTP MFA backup.

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| `id` | uuid | NO | `gen_random_uuid()` | PK |
| `user_id` | uuid | NO | - | FK -> profiles(id) ON DELETE CASCADE |
| `code_hash` | text | NO | - | |
| `used_at` | timestamptz | YES | - | |
| `created_at` | timestamptz | NO | `now()` | |

---

### mfa_recovery_attempts
Brute force tracking for recovery code attempts.

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| `id` | uuid | NO | `gen_random_uuid()` | PK |
| `user_id` | uuid | NO | - | FK -> profiles(id) ON DELETE CASCADE |
| `attempted_at` | timestamptz | NO | `now()` | |
| `success` | boolean | NO | `false` | |

Retention: 30 days (pg_cron).

---

### organizations
Multi-user organizations for consultoria/agency accounts.

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| `id` | uuid | NO | `gen_random_uuid()` | PK |
| `name` | text | NO | - | |
| `logo_url` | text | YES | - | |
| `owner_id` | uuid | NO | - | FK -> profiles(id) ON DELETE RESTRICT |
| `max_members` | int | NO | `5` | |
| `plan_type` | text | NO | `'consultoria'` | CHECK: multiple valid plan types |
| `stripe_customer_id` | text | YES | - | |
| `created_at` | timestamptz | NO | `now()` | |
| `updated_at` | timestamptz | NO | `now()` | Auto-updated via trigger |

---

### organization_members
Members of an organization with role-based access.

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| `id` | uuid | NO | `gen_random_uuid()` | PK |
| `org_id` | uuid | NO | - | FK -> organizations(id) ON DELETE CASCADE |
| `user_id` | uuid | NO | - | FK -> profiles(id) ON DELETE CASCADE |
| `role` | text | NO | `'member'` | CHECK: owner, admin, member |
| `invited_at` | timestamptz | NO | `now()` | |
| `accepted_at` | timestamptz | YES | - | NULL = pending |

UNIQUE: `(org_id, user_id)`

---

### partners
Revenue share partner accounts.

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| `id` | uuid | NO | `gen_random_uuid()` | PK |
| `name` | text | NO | - | |
| `slug` | text | NO | - | UNIQUE |
| `contact_email` | text | NO | - | |
| `contact_name` | text | YES | - | |
| `stripe_coupon_id` | text | YES | - | |
| `revenue_share_pct` | numeric(5,2) | YES | `25.00` | |
| `status` | text | YES | `'active'` | CHECK: active, inactive, pending |
| `created_at` | timestamptz | NO | `now()` | |
| `updated_at` | timestamptz | NO | `now()` | Auto-updated via trigger |

---

### partner_referrals
Partner referral tracking for revenue share.

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| `id` | uuid | NO | `gen_random_uuid()` | PK |
| `partner_id` | uuid | NO | - | FK -> partners(id) ON DELETE CASCADE |
| `referred_user_id` | uuid | YES | - | FK -> profiles(id) ON DELETE SET NULL |
| `signup_at` | timestamptz | YES | `now()` | |
| `converted_at` | timestamptz | YES | - | |
| `churned_at` | timestamptz | YES | - | |
| `monthly_revenue` | numeric(10,2) | YES | - | |
| `revenue_share_amount` | numeric(10,2) | YES | - | |

UNIQUE: `(partner_id, referred_user_id)`

---

## Custom Types & Enums

| Type | Values | Used By |
|------|--------|---------|
| `alert_frequency` | `daily`, `twice_weekly`, `weekly`, `off` | alert_preferences.frequency |

---

## Functions (RPC)

### Quota Functions
| Function | Returns | Purpose |
|----------|---------|---------|
| `check_and_increment_quota(uuid, varchar, int)` | TABLE(allowed, new_count, previous_count, quota_remaining) | Primary atomic quota check+increment |
| `increment_quota_atomic(uuid, varchar, int)` | TABLE(new_count, was_at_limit, previous_count) | Fallback quota increment |
| `increment_quota_fallback_atomic(uuid, text, int)` | TABLE(new_count) | Simplified fallback |

### Billing Helper Functions
| Function | Returns | Purpose |
|----------|---------|---------|
| `get_user_billing_period(uuid)` | VARCHAR(10) | Get user's current billing period |
| `user_has_feature(uuid, varchar)` | BOOLEAN | Check if user has specific feature |
| `get_user_features(uuid)` | TEXT[] | Get all enabled feature keys |

### Query Functions
| Function | Returns | Purpose |
|----------|---------|---------|
| `get_conversations_with_unread_count(...)` | TABLE | Eliminates N+1 query in conversation list (LEFT JOIN LATERAL) |
| `get_analytics_summary(uuid, timestamptz, timestamptz)` | TABLE | Analytics summary without full-table scan |
| `get_table_columns_simple(text)` | TABLE(column_name) | Schema validation helper |
| `pg_total_relation_size_safe(text)` | bigint | Safe table size query for Prometheus |

### Trigger Functions
| Function | Purpose |
|----------|---------|
| `set_updated_at()` | Canonical updated_at trigger (used by 13+ tables) |
| `handle_new_user()` | Auto-create profile on signup (phone normalization, plan_type=free_trial) |
| `update_conversation_last_message()` | Update conversation.last_message_at on new message |
| `cleanup_search_cache_per_user()` | Priority-based cache eviction (short-circuit if <=5 entries) |
| `create_default_alert_preferences()` | Auto-create alert preferences for new users |

---

## Triggers

| Trigger | Table | Event | Function |
|---------|-------|-------|----------|
| `on_auth_user_created` | auth.users | AFTER INSERT | `handle_new_user()` |
| `profiles_updated_at` | profiles | BEFORE UPDATE | `set_updated_at()` |
| `plans_updated_at` | plans | BEFORE UPDATE | `set_updated_at()` |
| `plan_features_updated_at` | plan_features | BEFORE UPDATE | `set_updated_at()` |
| `user_subscriptions_updated_at` | user_subscriptions | BEFORE UPDATE | `set_updated_at()` |
| `tr_pipeline_items_updated_at` | pipeline_items | BEFORE UPDATE | `set_updated_at()` |
| `tr_organizations_updated_at` | organizations | BEFORE UPDATE | `set_updated_at()` |
| `trigger_alert_preferences_updated_at` | alert_preferences | BEFORE UPDATE | `set_updated_at()` |
| `trigger_alerts_updated_at` | alerts | BEFORE UPDATE | `set_updated_at()` |
| `trg_plan_billing_periods_updated_at` | plan_billing_periods | BEFORE UPDATE | `set_updated_at()` |
| `trg_google_sheets_exports_updated_at` | google_sheets_exports | BEFORE UPDATE | `set_updated_at()` |
| `trg_incidents_updated_at` | incidents | BEFORE UPDATE | `set_updated_at()` |
| `trg_partners_updated_at` | partners | BEFORE UPDATE | `set_updated_at()` |
| `trg_update_conversation_last_message` | messages | AFTER INSERT | `update_conversation_last_message()` |
| `trg_cleanup_search_cache` | search_results_cache | AFTER INSERT | `cleanup_search_cache_per_user()` |
| `trigger_create_alert_preferences_on_profile` | profiles | AFTER INSERT | `create_default_alert_preferences()` |

---

## Indexes

### profiles (9 indexes)
| Index | Columns | Type | Notes |
|-------|---------|------|-------|
| `profiles_pkey` | (id) | btree unique | PK |
| `idx_profiles_is_admin` | (is_admin) | btree | Partial WHERE is_admin = true |
| `idx_profiles_email_trgm` | (email) | GIN gin_trgm_ops | Admin ILIKE search |
| `idx_profiles_email_unique` | (email) | btree unique | Partial WHERE NOT NULL |
| `idx_profiles_phone_whatsapp_unique` | (phone_whatsapp) | btree unique | Partial WHERE NOT NULL |
| `idx_profiles_whatsapp_consent` | (whatsapp_consent) | btree | Partial WHERE true |
| `idx_profiles_context_porte` | (context_data->>'porte_empresa') | btree | Partial WHERE NOT NULL |
| `idx_profiles_subscription_status` | (subscription_status) | btree | Partial WHERE != 'trial' |
| `idx_profiles_referred_by_partner` | (referred_by_partner_id) | btree | Partial WHERE NOT NULL |

### search_sessions (5 indexes)
| Index | Columns | Notes |
|-------|---------|-------|
| `idx_search_sessions_created` | (user_id, created_at DESC) | History listing |
| `idx_search_sessions_search_id` | (search_id) | Partial WHERE NOT NULL |
| `idx_search_sessions_status` | (status) | Partial WHERE IN (created, processing) |
| `idx_search_sessions_inflight` | (status, started_at) | Partial WHERE IN (created, processing) |
| `idx_search_sessions_user_status_created` | (user_id, status, created_at DESC) | Composite |

### search_results_cache (6 indexes)
| Index | Columns | Notes |
|-------|---------|-------|
| UNIQUE | (user_id, params_hash) | |
| `idx_search_cache_user` | (user_id, created_at DESC) | |
| `idx_search_cache_params_hash` | (params_hash) | Cross-user queries |
| `idx_search_cache_global_hash` | (params_hash_global, created_at DESC) | |
| `idx_search_cache_degraded` | (degraded_until) | Partial WHERE NOT NULL |
| `idx_search_cache_priority` | (user_id, priority, last_accessed_at) | Eviction |

### user_subscriptions (6 indexes)
| Index | Columns | Notes |
|-------|---------|-------|
| `idx_user_subscriptions_user` | (user_id) | |
| `idx_user_subscriptions_active` | (user_id, is_active) | Partial WHERE is_active = true |
| `idx_user_subscriptions_billing` | (user_id, billing_period, is_active) | Partial WHERE is_active = true |
| `idx_user_subscriptions_stripe_sub_id` | (stripe_subscription_id) | Unique partial WHERE NOT NULL |
| `idx_user_subscriptions_customer_id` | (stripe_customer_id) | Partial WHERE NOT NULL |
| `idx_user_subscriptions_first_failed_at` | (first_failed_at) | Partial WHERE NOT NULL |

### Other notable indexes
| Table | Index | Columns |
|-------|-------|---------|
| stripe_webhook_events | `idx_webhook_events_type` | (type, processed_at) |
| stripe_webhook_events | `idx_webhook_events_recent` | (processed_at DESC) |
| pipeline_items | `idx_pipeline_user_stage` | (user_id, stage) |
| pipeline_items | `idx_pipeline_encerramento` | (data_encerramento) partial |
| pipeline_items | `idx_pipeline_items_search_id` | (search_id) partial |
| conversations | `idx_conversations_user_id` | (user_id) |
| conversations | `idx_conversations_status_last_msg` | (status, last_message_at DESC) |
| conversations | `idx_conversations_unanswered` | (created_at) partial |
| messages | `idx_messages_conversation` | (conversation_id, created_at) |
| messages | `idx_messages_unread_by_user` | (conversation_id) partial |
| messages | `idx_messages_unread_by_admin` | (conversation_id) partial |
| audit_events | `idx_audit_events_type_timestamp` | (event_type, timestamp DESC) |
| audit_events | `idx_audit_events_actor` | (actor_id_hash) partial |
| search_state_transitions | `idx_state_transitions_search_id` | (search_id, created_at ASC) |
| search_state_transitions | `idx_search_state_transitions_user_id` | (user_id) |
| google_sheets_exports | `idx_google_sheets_exports_search_params` | (search_params) GIN |
| search_results_store | `idx_search_results_user` | (user_id) |
| search_results_store | `idx_search_results_store_user_expires` | (user_id, expires_at) |
| alert_sent_items | `idx_alert_sent_items_dedup` | (alert_id, item_id) unique |

---

## RLS Policies

All 27 public tables have RLS enabled. The standard pattern is:

- **User-facing tables**: `auth.uid() = user_id` for SELECT/INSERT/UPDATE/DELETE
- **Service role**: `FOR ALL TO service_role USING (true) WITH CHECK (true)`
- **Admin tables**: `EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND is_admin = true)`
- **Public catalog**: `FOR SELECT USING (true)` (plans, plan_features, plan_billing_periods)

### Policy Summary by Table

| Table | User Policies | Admin | Service Role | Public |
|-------|--------------|-------|-------------|--------|
| profiles | SELECT own, UPDATE own, INSERT own | - | ALL | - |
| plans | - | - | - | SELECT all |
| plan_billing_periods | - | - | ALL | SELECT all |
| plan_features | - | - | - | SELECT all |
| user_subscriptions | SELECT own | - | ALL | - |
| monthly_quota | SELECT own | - | ALL | - |
| search_sessions | SELECT own, INSERT own | - | ALL | - |
| search_state_transitions | SELECT own(user_id) | - | ALL | - |
| search_results_cache | SELECT own | - | ALL | - |
| search_results_store | SELECT own | - | ALL | - |
| stripe_webhook_events | - | SELECT (is_admin) | INSERT + SELECT | - |
| pipeline_items | SELECT/INSERT/UPDATE/DELETE own | - | ALL | - |
| conversations | SELECT own+admin, INSERT own, UPDATE admin | - | ALL | - |
| messages | SELECT/INSERT/UPDATE own+admin | - | ALL | - |
| alerts | SELECT/INSERT/UPDATE/DELETE own | - | ALL | - |
| alert_sent_items | SELECT own(via join) | - | ALL | - |
| alert_runs | SELECT own(via join) | - | ALL | - |
| alert_preferences | SELECT/INSERT/UPDATE own | - | ALL | - |
| classification_feedback | SELECT/INSERT/UPDATE/DELETE own | - | ALL | - |
| user_oauth_tokens | SELECT/UPDATE/DELETE own | - | ALL | - |
| google_sheets_exports | SELECT/INSERT/UPDATE own | - | ALL | - |
| audit_events | - | SELECT (is_admin) | ALL | - |
| trial_email_log | - | - | (service bypasses) | - |
| reconciliation_log | - | SELECT (is_admin) | ALL | - |
| health_checks | - | - | ALL | - |
| incidents | - | - | ALL | - |
| mfa_recovery_codes | SELECT own (authenticated) | - | ALL | - |
| mfa_recovery_attempts | - | - | ALL | - |
| organizations | SELECT owner+admin, INSERT/UPDATE owner | - | ALL | - |
| organization_members | SELECT own+org admin, INSERT org admin, DELETE org admin+self | - | ALL | - |
| partners | SELECT admin+self | ALL (admin) | ALL | - |
| partner_referrals | SELECT admin+partner | ALL (admin) | ALL | - |

---

## pg_cron Scheduled Jobs

| Job Name | Schedule | Retention | Table |
|----------|----------|-----------|-------|
| `cleanup-monthly-quota` | 2:00 UTC, 1st monthly | 24 months | monthly_quota |
| `cleanup-webhook-events` | 3:00 UTC daily | 90 days | stripe_webhook_events |
| `cleanup-audit-events` | 4:00 UTC, 1st monthly | 12 months | audit_events |
| `cleanup-search-state-transitions` | 4:00 UTC daily | 30 days | search_state_transitions |
| `cleanup-cold-cache-entries` | 5:00 UTC daily | 7 days (cold) | search_results_cache |
| `cleanup-alert-sent-items` | 4:05 UTC daily | 180 days | alert_sent_items |
| `cleanup-health-checks` | 4:10 UTC daily | 30 days | health_checks |
| `cleanup-incidents` | 4:15 UTC daily | 90 days | incidents |
| `cleanup-mfa-recovery-attempts` | 4:20 UTC daily | 30 days | mfa_recovery_attempts |
| `cleanup-alert-runs` | 4:25 UTC daily | 90 days (completed) | alert_runs |
| `cleanup-expired-search-results` | 4:00 UTC daily | expired rows | search_results_store |
| `cleanup-old-search-sessions` | 4:30 UTC daily | 12 months | search_sessions |
| `cleanup-classification-feedback` | 4:45 UTC daily | 24 months | classification_feedback |
| `cleanup-old-conversations` | 4:50 UTC daily | 24 months | conversations |
| `cleanup-orphan-messages` | 4:55 UTC daily | 24 months | messages |

---

## Entity Relationships

```
auth.users (Supabase managed)
  |-- profiles (1:1, ON DELETE CASCADE) *** Central hub ***
       |-- user_subscriptions (1:N, CASCADE)
       |-- monthly_quota (1:N, CASCADE)
       |-- search_sessions (1:N, CASCADE)
       |-- search_results_cache (1:N, CASCADE)
       |-- search_results_store (1:N, CASCADE)
       |-- pipeline_items (1:N, CASCADE)
       |-- conversations (1:N, CASCADE)
       |-- messages (via sender_id, CASCADE)
       |-- alerts (1:N, CASCADE)
       |-- alert_preferences (1:1, CASCADE)
       |-- classification_feedback (1:N, CASCADE)
       |-- user_oauth_tokens (1:N, CASCADE)
       |-- google_sheets_exports (1:N, CASCADE)
       |-- mfa_recovery_codes (1:N, CASCADE)
       |-- mfa_recovery_attempts (1:N, CASCADE)
       |-- organization_members (N:M via org_id, CASCADE)
       |-- organizations (via owner_id, RESTRICT)
       |-- partner_referrals (via referred_user_id, SET NULL)
       |-- search_state_transitions (1:N, CASCADE)
       |-- trial_email_log (1:N, CASCADE)

plans
  |-- plan_billing_periods (1:N, CASCADE)
  |-- plan_features (1:N, CASCADE)
  |-- user_subscriptions (via plan_id, RESTRICT)

conversations
  |-- messages (1:N, CASCADE)

alerts
  |-- alert_sent_items (1:N, CASCADE)
  |-- alert_runs (1:N, CASCADE)

organizations
  |-- organization_members (1:N, CASCADE)

partners
  |-- partner_referrals (1:N, CASCADE)
  |-- profiles (via referred_by_partner_id)
```

---

## Extensions

| Extension | Purpose |
|-----------|---------|
| `pg_trgm` | Trigram matching for email ILIKE search |
| `pg_cron` | Scheduled retention cleanup jobs (15 jobs) |

---

## System Account

A system cache warmer account exists at UUID `00000000-0000-0000-0000-000000000000`:
- Email: `system-cache-warmer@internal.smartlic.tech`
- Plan: `master`
- Banned until: 2099-12-31 (cannot authenticate)
- Purpose: Background cache warming jobs use this user_id to avoid counting against real user quotas
