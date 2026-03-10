# SmartLic Database Schema

**Provider:** Supabase (PostgreSQL 17)
**Project Ref:** `fqqyovlzdzimiwfofdjk`
**Schema Generated:** 2026-03-10

> Generated from 57 migration files (47 in `supabase/migrations/`, 10 in `backend/migrations/`).

---

## Tables

### 1. `profiles`

Extends `auth.users`. Auto-created via `handle_new_user()` trigger on signup.

| Column | Type | Nullable | Default | Constraint |
|--------|------|----------|---------|------------|
| `id` | uuid | NO | - | PK, FK -> auth.users(id) ON DELETE CASCADE |
| `email` | text | NO | - | UNIQUE (partial WHERE NOT NULL) |
| `full_name` | text | YES | - | - |
| `company` | text | YES | - | - |
| `plan_type` | text | NO | `'free_trial'` | CHECK: free_trial, consultor_agil, maquina, sala_guerra, master, smartlic_pro |
| `avatar_url` | text | YES | - | - |
| `is_admin` | boolean | NO | `false` | - |
| `sector` | text | YES | - | - |
| `phone_whatsapp` | text | YES | - | CHECK: `^[0-9]{10,11}$`, UNIQUE (partial WHERE NOT NULL) |
| `whatsapp_consent` | boolean | YES | `false` | - |
| `whatsapp_consent_at` | timestamptz | YES | - | - |
| `context_data` | jsonb | YES | `'{}'` | Schema: {ufs_atuacao, faixa_valor_min/max, porte_empresa, modalidades_interesse, palavras_chave, experiencia_licitacoes} |
| `subscription_status` | text | YES | `'trial'` | CHECK: trial, active, canceling, past_due, expired |
| `trial_expires_at` | timestamptz | YES | - | - |
| `subscription_end_date` | timestamptz | YES | - | - |
| `email_unsubscribed` | boolean | YES | `false` | - |
| `email_unsubscribed_at` | timestamptz | YES | - | - |
| `created_at` | timestamptz | NO | `now()` | - |
| `updated_at` | timestamptz | NO | `now()` | Auto-updated by trigger |

**Indexes:**
- `idx_profiles_is_admin` -- partial WHERE is_admin = true
- `idx_profiles_email_trgm` -- GIN trigram (pg_trgm) for ILIKE search
- `idx_profiles_whatsapp_consent` -- partial WHERE whatsapp_consent = true
- `idx_profiles_context_porte` -- btree on (context_data->>'porte_empresa')
- `idx_profiles_subscription_status` -- partial WHERE subscription_status != 'trial'
- `idx_profiles_phone_whatsapp_unique` -- partial unique WHERE NOT NULL
- `idx_profiles_email_unique` -- partial unique WHERE NOT NULL

**RLS Policies:**
- `profiles_select_own` -- SELECT: auth.uid() = id
- `profiles_update_own` -- UPDATE: auth.uid() = id
- `profiles_insert_own` -- INSERT: auth.uid() = id (TO authenticated)
- `profiles_insert_service` -- INSERT: true (TO service_role)
- `profiles_service_all` -- ALL: true (TO service_role)

**Trigger:** `profiles_updated_at` -- BEFORE UPDATE -> update_updated_at()

---

### 2. `plans`

Subscription plan catalog (public read).

| Column | Type | Nullable | Default | Constraint |
|--------|------|----------|---------|------------|
| `id` | text | NO | - | PK |
| `name` | text | NO | - | - |
| `description` | text | YES | - | - |
| `max_searches` | int | YES | - | null = unlimited |
| `price_brl` | numeric(10,2) | NO | `0` | - |
| `duration_days` | int | YES | - | null = perpetual |
| `stripe_price_id` | text | YES | - | Legacy (defaults to monthly) |
| `stripe_price_id_monthly` | text | YES | - | - |
| `stripe_price_id_semiannual` | text | YES | - | Added mig 029 |
| `stripe_price_id_annual` | text | YES | - | - |
| `is_active` | boolean | NO | `true` | - |
| `created_at` | timestamptz | NO | `now()` | - |
| `updated_at` | timestamptz | NO | `now()` | Auto-updated by trigger |

**Active Plans (as of mig 029 + STORY-277):**
- `smartlic_pro` -- R$397/mes, 1000 searches/month
- `master` -- unlimited, internal
- `free_trial` -- implicit (default plan_type, not in plans table)

**Legacy (is_active=false):** free, pack_5, pack_10, pack_20, monthly, annual, consultor_agil, maquina, sala_guerra

**RLS:** `plans_select_all` -- SELECT: true (public catalog)

**Trigger:** `plans_updated_at` -- BEFORE UPDATE -> update_updated_at()

---

### 3. `plan_billing_periods`

Multi-period pricing for plans (created mig 029).

| Column | Type | Nullable | Default | Constraint |
|--------|------|----------|---------|------------|
| `id` | uuid | NO | `gen_random_uuid()` | PK |
| `plan_id` | text | NO | - | FK -> plans(id) ON DELETE CASCADE |
| `billing_period` | text | NO | - | CHECK: monthly, semiannual, annual |
| `price_cents` | integer | NO | - | - |
| `discount_percent` | integer | YES | `0` | - |
| `stripe_price_id` | text | YES | - | - |
| `created_at` | timestamptz | YES | `now()` | - |

**Unique:** (plan_id, billing_period)

**RLS:**
- `plan_billing_periods_public_read` -- SELECT: true (TO authenticated, anon)
- `plan_billing_periods_service_all` -- ALL: true (TO service_role)

---

### 4. `plan_features`

Billing-period-specific feature flags for plans.

| Column | Type | Nullable | Default | Constraint |
|--------|------|----------|---------|------------|
| `id` | serial | NO | - | PK |
| `plan_id` | text | NO | - | FK -> plans(id) ON DELETE CASCADE |
| `billing_period` | varchar(10) | NO | - | CHECK: monthly, semiannual, annual |
| `feature_key` | varchar(100) | NO | - | - |
| `enabled` | boolean | NO | `true` | - |
| `metadata` | jsonb | YES | `'{}'` | - |
| `created_at` | timestamptz | NO | `now()` | - |
| `updated_at` | timestamptz | NO | `now()` | Auto-updated by trigger |

**Unique:** (plan_id, billing_period, feature_key)

**Indexes:** `idx_plan_features_lookup` -- partial WHERE enabled = true

**RLS:** `plan_features_select_all` -- SELECT: true (public)

**Trigger:** `plan_features_updated_at` -> update_updated_at()

---

### 5. `user_subscriptions`

Tracks user subscription history and active billing.

| Column | Type | Nullable | Default | Constraint |
|--------|------|----------|---------|------------|
| `id` | uuid | NO | `gen_random_uuid()` | PK |
| `user_id` | uuid | NO | - | FK -> profiles(id) ON DELETE CASCADE |
| `plan_id` | text | NO | - | FK -> plans(id) ON DELETE RESTRICT (intentional) |
| `credits_remaining` | int | YES | - | null = unlimited |
| `starts_at` | timestamptz | NO | `now()` | - |
| `expires_at` | timestamptz | YES | - | null = never expires |
| `stripe_subscription_id` | text | YES | - | UNIQUE (partial WHERE NOT NULL) |
| `stripe_customer_id` | text | YES | - | - |
| `is_active` | boolean | NO | `true` | - |
| `billing_period` | varchar(10) | NO | `'monthly'` | CHECK: monthly, semiannual, annual |
| `annual_benefits` | jsonb | NO | `'{}'` | - |
| `subscription_status` | text | YES | `'active'` | CHECK: active, trialing, past_due, canceled, expired |
| `created_at` | timestamptz | NO | `now()` | - |
| `updated_at` | timestamptz | NO | `now()` | Auto-updated by trigger |

**Indexes:**
- `idx_user_subscriptions_user` -- (user_id)
- `idx_user_subscriptions_active` -- partial (user_id, is_active) WHERE is_active = true
- `idx_user_subscriptions_billing` -- partial (user_id, billing_period, is_active) WHERE is_active = true
- `idx_user_subscriptions_stripe_sub_id` -- UNIQUE partial WHERE NOT NULL
- `idx_user_subscriptions_customer_id` -- partial WHERE NOT NULL

**RLS:**
- `subscriptions_select_own` -- SELECT: auth.uid() = user_id
- `Service role can manage subscriptions` -- ALL: true (TO service_role)

**Trigger:** `user_subscriptions_updated_at` -> update_updated_at()

---

### 6. `monthly_quota`

Monthly search quota tracking per user.

| Column | Type | Nullable | Default | Constraint |
|--------|------|----------|---------|------------|
| `id` | uuid | NO | `gen_random_uuid()` | PK |
| `user_id` | uuid | NO | - | FK -> profiles(id) ON DELETE CASCADE |
| `month_year` | varchar(7) | NO | - | Format: "YYYY-MM" |
| `searches_count` | int | NO | `0` | - |
| `created_at` | timestamptz | NO | `now()` | - |
| `updated_at` | timestamptz | NO | `now()` | - |

**Unique:** (user_id, month_year)

**Indexes:** `idx_monthly_quota_user_month` -- (user_id, month_year)

**RLS:**
- `Users can view own quota` -- SELECT: auth.uid() = user_id
- `Service role can manage quota` -- ALL: true (TO service_role)

**Retention:** pg_cron job `cleanup-monthly-quota` deletes rows > 24 months.

---

### 7. `search_sessions`

Search history per user.

| Column | Type | Nullable | Default | Constraint |
|--------|------|----------|---------|------------|
| `id` | uuid | NO | `gen_random_uuid()` | PK |
| `user_id` | uuid | NO | - | FK -> profiles(id) ON DELETE CASCADE |
| `search_id` | uuid | YES | - | Correlation with SSE/ARQ |
| `sectors` | text[] | NO | - | - |
| `ufs` | text[] | NO | - | - |
| `data_inicial` | date | NO | - | - |
| `data_final` | date | NO | - | - |
| `custom_keywords` | text[] | YES | - | - |
| `total_raw` | int | NO | `0` | - |
| `total_filtered` | int | NO | `0` | - |
| `valor_total` | numeric(14,2) | YES | `0` | - |
| `resumo_executivo` | text | YES | - | - |
| `destaques` | text[] | YES | - | - |
| `excel_storage_path` | text | YES | - | - |
| `status` | text | NO | `'created'` | CHECK: created, processing, completed, failed, timed_out, cancelled |
| `error_message` | text | YES | - | - |
| `error_code` | text | YES | - | - |
| `started_at` | timestamptz | NO | `now()` | - |
| `completed_at` | timestamptz | YES | - | - |
| `duration_ms` | integer | YES | - | - |
| `pipeline_stage` | text | YES | - | - |
| `raw_count` | integer | YES | `0` | - |
| `response_state` | text | YES | - | - |
| `failed_ufs` | text[] | YES | - | - |
| `created_at` | timestamptz | NO | `now()` | - |

**Indexes:**
- `idx_search_sessions_user` -- (user_id)
- `idx_search_sessions_created` -- (user_id, created_at DESC)
- `idx_search_sessions_search_id` -- partial WHERE search_id IS NOT NULL
- `idx_search_sessions_status` -- partial WHERE status IN ('created', 'processing')
- `idx_search_sessions_inflight` -- (status, started_at) partial
- `idx_search_sessions_user_status_created` -- (user_id, status, created_at DESC)

**RLS:**
- `sessions_select_own` -- SELECT: auth.uid() = user_id
- `sessions_insert_own` -- INSERT: auth.uid() = user_id
- `Service role can manage search sessions` -- ALL: true (TO service_role)

---

### 8. `search_results_cache`

Persistent L2 cache of search results (SWR pattern).

| Column | Type | Nullable | Default | Constraint |
|--------|------|----------|---------|------------|
| `id` | uuid | NO | `gen_random_uuid()` | PK |
| `user_id` | uuid | NO | - | FK -> profiles(id) ON DELETE CASCADE |
| `params_hash` | text | NO | - | - |
| `params_hash_global` | text | YES | - | Cross-user fallback hash |
| `search_params` | jsonb | NO | - | - |
| `results` | jsonb | NO | - | CHECK: octet_length <= 2 MB |
| `total_results` | integer | NO | `0` | - |
| `sources_json` | jsonb | NO | `'["pncp"]'` | Which data sources contributed |
| `fetched_at` | timestamptz | NO | `now()` | When live fetch occurred |
| `last_success_at` | timestamptz | YES | - | Last successful refresh |
| `last_attempt_at` | timestamptz | YES | - | Last refresh attempt |
| `fail_streak` | integer | NO | `0` | Consecutive failures |
| `degraded_until` | timestamptz | YES | - | Degraded mode expiry |
| `coverage` | jsonb | YES | - | Source coverage metadata |
| `fetch_duration_ms` | integer | YES | - | - |
| `priority` | text | NO | `'cold'` | hot/warm/cold tiering |
| `access_count` | integer | NO | `0` | - |
| `last_accessed_at` | timestamptz | YES | - | - |
| `created_at` | timestamptz | NO | `now()` | - |

**Unique:** (user_id, params_hash)

**Indexes:**
- `idx_search_cache_user` -- (user_id, created_at DESC)
- `idx_search_cache_params_hash` -- (params_hash)
- `idx_search_cache_fetched_at` -- (fetched_at)
- `idx_search_cache_degraded` -- partial WHERE degraded_until IS NOT NULL
- `idx_search_cache_priority` -- (user_id, priority, last_accessed_at)
- `idx_search_cache_global_hash` -- (params_hash_global, created_at DESC)

**RLS:**
- `Users can read own search cache` -- SELECT: auth.uid() = user_id
- `Service role full access` -- ALL: true (TO service_role)

**Trigger:** `trg_cleanup_search_cache` -- AFTER INSERT -> cleanup_search_cache_per_user() (evict > 10 entries, priority-aware)

**Retention:** pg_cron `cleanup-cold-cache-entries` -- daily, deletes cold > 7 days

---

### 9. `search_state_transitions`

Audit trail for search state machine transitions.

| Column | Type | Nullable | Default | Constraint |
|--------|------|----------|---------|------------|
| `id` | uuid | NO | `gen_random_uuid()` | PK |
| `search_id` | uuid | NO | - | Correlates with search_sessions.search_id (no FK) |
| `from_state` | text | YES | - | NULL for initial CREATED |
| `to_state` | text | NO | - | - |
| `stage` | text | YES | - | Pipeline stage |
| `details` | jsonb | YES | `'{}'` | - |
| `duration_since_previous_ms` | integer | YES | - | - |
| `created_at` | timestamptz | NO | `now()` | - |

**Indexes:**
- `idx_state_transitions_search_id` -- (search_id, created_at ASC)
- `idx_state_transitions_to_state` -- (to_state, created_at)

**RLS:**
- `Users can read own transitions` -- SELECT via join to search_sessions
- `Service role can insert transitions` -- INSERT: true (TO service_role)

---

### 10. `conversations`

InMail messaging system.

| Column | Type | Nullable | Default | Constraint |
|--------|------|----------|---------|------------|
| `id` | uuid | NO | `gen_random_uuid()` | PK |
| `user_id` | uuid | NO | - | FK -> profiles(id) ON DELETE CASCADE |
| `subject` | text | NO | - | CHECK: length <= 200 |
| `category` | text | NO | - | CHECK: suporte, sugestao, funcionalidade, bug, outro |
| `status` | text | NO | `'aberto'` | CHECK: aberto, respondido, resolvido |
| `last_message_at` | timestamptz | NO | `now()` | - |
| `created_at` | timestamptz | NO | `now()` | - |
| `updated_at` | timestamptz | NO | `now()` | - |

**Indexes:**
- `idx_conversations_user_id`, `idx_conversations_status`, `idx_conversations_last_message`

**RLS:** SELECT own+admin, INSERT own, UPDATE admin, service_role ALL

---

### 11. `messages`

| Column | Type | Nullable | Default | Constraint |
|--------|------|----------|---------|------------|
| `id` | uuid | NO | `gen_random_uuid()` | PK |
| `conversation_id` | uuid | NO | - | FK -> conversations(id) ON DELETE CASCADE |
| `sender_id` | uuid | NO | - | FK -> profiles(id) ON DELETE CASCADE |
| `body` | text | NO | - | CHECK: 1 <= length <= 5000 |
| `is_admin_reply` | boolean | NO | `false` | - |
| `read_by_user` | boolean | NO | `false` | - |
| `read_by_admin` | boolean | NO | `false` | - |
| `created_at` | timestamptz | NO | `now()` | - |

**Indexes:** conversation+created, unread partials

**Trigger:** `trg_update_conversation_last_message` -- updates conversation.last_message_at

---

### 12. `pipeline_items`

Opportunity pipeline (kanban).

| Column | Type | Nullable | Default | Constraint |
|--------|------|----------|---------|------------|
| `id` | uuid | NO | `gen_random_uuid()` | PK |
| `user_id` | uuid | NO | - | FK -> profiles(id) ON DELETE CASCADE |
| `pncp_id` | text | NO | - | - |
| `objeto` | text | NO | - | - |
| `orgao` | text | YES | - | - |
| `uf` | text | YES | - | - |
| `valor_estimado` | numeric | YES | - | - |
| `data_encerramento` | timestamptz | YES | - | - |
| `link_pncp` | text | YES | - | - |
| `stage` | text | NO | `'descoberta'` | CHECK: descoberta, analise, preparando, enviada, resultado |
| `notes` | text | YES | - | - |
| `version` | integer | NO | `1` | Optimistic locking |
| `created_at` | timestamptz | NO | `now()` | - |
| `updated_at` | timestamptz | NO | `now()` | - |

**Unique:** (user_id, pncp_id)

**RLS:** Full CRUD own + service_role ALL

---

### 13. `stripe_webhook_events`

Stripe webhook idempotency.

| Column | Type | Nullable | Default | Constraint |
|--------|------|----------|---------|------------|
| `id` | varchar(255) | NO | - | PK, CHECK: `^evt_` |
| `type` | varchar(100) | NO | - | - |
| `processed_at` | timestamptz | NO | `now()` | - |
| `payload` | jsonb | YES | - | - |
| `status` | varchar(20) | NO | `'completed'` | - |
| `received_at` | timestamptz | YES | `now()` | - |

**Retention:** pg_cron daily, > 90 days

---

### 14. `audit_events`

Security audit log (SHA-256 hashed PII).

| Column | Type | Nullable | Default | Constraint |
|--------|------|----------|---------|------------|
| `id` | uuid | NO | `gen_random_uuid()` | PK |
| `timestamp` | timestamptz | NO | `now()` | - |
| `event_type` | text | NO | - | - |
| `actor_id_hash` | text | YES | - | SHA-256 (16 hex) |
| `target_id_hash` | text | YES | - | SHA-256 (16 hex) |
| `details` | jsonb | YES | - | - |
| `ip_hash` | text | YES | - | SHA-256 (16 hex) |

**Retention:** pg_cron monthly, > 12 months

---

### 15. `user_oauth_tokens`

Encrypted OAuth 2.0 tokens (Google Sheets).

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| `id` | uuid | NO | gen_random_uuid() |
| `user_id` | uuid | NO | FK -> profiles(id) |
| `provider` | varchar(50) | NO | CHECK: google, microsoft, dropbox |
| `access_token` | text | NO | AES-256 encrypted |
| `refresh_token` | text | YES | AES-256 encrypted |
| `expires_at` | timestamptz | NO | - |
| `scope` | text | NO | - |

**Unique:** (user_id, provider)

---

### 16. `google_sheets_exports`

| `user_id`, `spreadsheet_id`, `spreadsheet_url`, `search_params` (JSONB, GIN), `total_rows`, timestamps.

---

### 17. `classification_feedback`

User feedback on search classification quality.

| Column | Type | Notable |
|--------|------|---------|
| `user_id` | uuid | FK -> profiles(id) |
| `search_id` | uuid | - |
| `bid_id` | text | - |
| `setor_id` | text | - |
| `user_verdict` | text | CHECK: false_positive, false_negative, correct |
| `category` | text | CHECK: wrong_sector, irrelevant_modality, etc. |

**Unique:** (user_id, search_id, bid_id)

---

### 18. `trial_email_log`

| `user_id`, `email_type` (midpoint/expiring/last_day/expired), `sent_at`. UNIQUE(user_id, email_type). Service-role only.

---

### 19. `alert_preferences`

Per-user email alert scheduling. Auto-created on profile insert.

| Column | Type | Notable |
|--------|------|---------|
| `user_id` | uuid | UNIQUE, FK -> profiles(id) |
| `frequency` | alert_frequency (enum) | daily, twice_weekly, weekly, off |
| `enabled` | boolean | default true |
| `last_digest_sent_at` | timestamptz | - |

---

### 20. `alerts`

User-defined email alerts with search filters.

| `user_id`, `name`, `filters` (JSONB: setor, ufs, valor_min/max, keywords), `active`, timestamps.

---

### 21. `alert_sent_items`

Dedup tracking. FK -> alerts(id) ON DELETE CASCADE. UNIQUE(alert_id, item_id).

---

## Functions

| Function | Purpose | Security |
|----------|---------|----------|
| `handle_new_user()` | Auto-create profile on signup | DEFINER |
| `update_updated_at()` | Generic updated_at trigger | - |
| `increment_quota_atomic()` | Atomic quota check+increment with row lock | - |
| `check_and_increment_quota()` | Combined check+increment (no TOCTOU) | - |
| `increment_quota_fallback_atomic()` | Simpler atomic fallback | - |
| `get_user_billing_period()` | User's current billing period | DEFINER |
| `user_has_feature()` | Check user feature by plan+period | DEFINER |
| `get_user_features()` | Get all enabled features | DEFINER |
| `update_conversation_last_message()` | Update conversation timestamp on new message | - |
| `get_conversations_with_unread_count()` | RPC: conversations + unread count | DEFINER |
| `get_analytics_summary()` | RPC: analytics with date range | DEFINER |
| `cleanup_search_cache_per_user()` | Priority-aware cache eviction (max 10/user) | DEFINER |
| `get_table_columns_simple()` | Schema validation RPC | DEFINER |
| `create_default_alert_preferences()` | Auto-create alert prefs on profile insert | - |

## Custom Types

| Type | Kind | Values |
|------|------|--------|
| `alert_frequency` | ENUM | daily, twice_weekly, weekly, off |

## Extensions

| Extension | Purpose |
|-----------|---------|
| `pg_trgm` | Trigram matching for ILIKE |
| `pg_cron` | Scheduled cleanup jobs |

## pg_cron Jobs

| Job | Schedule | Retention |
|-----|----------|-----------|
| `cleanup-monthly-quota` | 2am 1st/month | > 24 months |
| `cleanup-webhook-events` | 3am daily | > 90 days |
| `cleanup-audit-events` | 4am 1st/month | > 12 months |
| `cleanup-cold-cache-entries` | 5am daily | cold > 7 days |

## Entity Relationships

```
auth.users (1) -----> (1) profiles
profiles   (1) -----> (*) user_subscriptions
profiles   (1) -----> (*) search_sessions
profiles   (1) -----> (*) search_results_cache
profiles   (1) -----> (*) monthly_quota
profiles   (1) -----> (*) pipeline_items
profiles   (1) -----> (*) conversations -----> (*) messages
profiles   (1) -----> (*) user_oauth_tokens
profiles   (1) -----> (*) google_sheets_exports
profiles   (1) -----> (*) classification_feedback
profiles   (1) -----> (*) trial_email_log
profiles   (1) -----> (1) alert_preferences
profiles   (1) -----> (*) alerts -----> (*) alert_sent_items
plans      (1) -----> (*) user_subscriptions (RESTRICT)
plans      (1) -----> (*) plan_features
plans      (1) -----> (*) plan_billing_periods
search_sessions ...... search_state_transitions (via search_id, no FK)
```
