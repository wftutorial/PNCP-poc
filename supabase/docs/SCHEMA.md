# SmartLic Database Schema Documentation

**Provider:** Supabase (PostgreSQL 17)
**Project Ref:** `fqqyovlzdzimiwfofdjk`
**Schema Generated:** 2026-03-09
**Migrations Analyzed:** 76 files (66 Supabase + 10 backend)
**Total Tables:** 27
**Total Functions:** 13
**Total Custom Types:** 1 (`alert_frequency`)

---

## Table of Contents

1. [Tables](#tables)
   - [Core User & Auth](#core-user--auth)
   - [Billing & Plans](#billing--plans)
   - [Search Pipeline](#search-pipeline)
   - [Messaging](#messaging)
   - [Alerts & Notifications](#alerts--notifications)
   - [Analytics & Audit](#analytics--audit)
   - [Integrations](#integrations)
   - [Organizations & Partners](#organizations--partners)
   - [Infrastructure](#infrastructure)
2. [Relationships (ER Diagram)](#relationships)
3. [Indexes](#indexes)
4. [RLS Policies](#rls-policies)
5. [Functions and Triggers](#functions-and-triggers)
6. [Custom Types (Enums)](#custom-types)
7. [Scheduled Jobs (pg_cron)](#scheduled-jobs)

---

## Tables

### Core User & Auth

#### 1. `profiles`

Extends `auth.users` with application-specific data. Central user table created automatically via `handle_new_user()` trigger on signup.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | -- | PK, FK -> `auth.users(id) ON DELETE CASCADE` |
| `email` | `text` | NOT NULL | -- | Trigram index for admin ILIKE search |
| `full_name` | `text` | YES | -- | |
| `company` | `text` | YES | -- | |
| `plan_type` | `text` | NOT NULL | `'free_trial'` | CHECK: `free_trial, consultor_agil, maquina, sala_guerra, master, smartlic_pro, consultoria` |
| `avatar_url` | `text` | YES | -- | |
| `is_admin` | `boolean` | NOT NULL | `false` | Admin access flag (added migration 004) |
| `sector` | `text` | YES | -- | User business sector |
| `phone_whatsapp` | `text` | YES | -- | Normalized 10-11 digits. Partial unique index |
| `whatsapp_consent` | `boolean` | YES | `false` | LGPD consent flag |
| `whatsapp_consent_at` | `timestamptz` | YES | -- | LGPD audit trail |
| `context_data` | `jsonb` | YES | `'{}'::jsonb` | Onboarding wizard data (STORY-247). Schema: `{ufs_atuacao, faixa_valor_min, faixa_valor_max, porte_empresa, modalidades_interesse, palavras_chave, experiencia_licitacoes}` |
| `subscription_status` | `text` | YES | `'trial'` | CHECK: `trial, active, canceling, past_due, expired` |
| `trial_expires_at` | `timestamptz` | YES | -- | Trial expiration date |
| `subscription_end_date` | `timestamptz` | YES | -- | When canceled subscription ends |
| `email_unsubscribed` | `boolean` | YES | `false` | Email opt-out (LGPD) |
| `email_unsubscribed_at` | `timestamptz` | YES | -- | Opt-out timestamp |
| `marketing_emails_enabled` | `boolean` | NOT NULL | `true` | Marketing email preference |
| `referred_by_partner_id` | `uuid` | YES | -- | FK -> `partners(id)`. Partner referral tracking |
| `created_at` | `timestamptz` | NOT NULL | `now()` | |
| `updated_at` | `timestamptz` | NOT NULL | `now()` | Auto-updated via `set_updated_at()` trigger |

**Constraints:**
- `profiles_plan_type_check`: CHECK on `plan_type` values
- `chk_profiles_subscription_status`: CHECK on `subscription_status` values

**Indexes:**
- `profiles_pkey` (PK on `id`)
- `idx_profiles_email_trgm` (GIN trigram on `email` for ILIKE search)
- `idx_profiles_subscription_status` (partial, WHERE `subscription_status != 'trial'`)
- `idx_profiles_context_porte` (B-tree on `context_data->>'porte_empresa'` WHERE NOT NULL)
- `idx_profiles_phone_whatsapp_unique` (partial unique on `phone_whatsapp` WHERE NOT NULL)
- `idx_profiles_referred_by_partner` (on `referred_by_partner_id` WHERE NOT NULL)

**RLS Policies:**
- `profiles_select_own`: SELECT WHERE `auth.uid() = id`
- `profiles_update_own`: UPDATE WHERE `auth.uid() = id`
- `profiles_insert_own`: INSERT WHERE `auth.uid() = id` (TO authenticated)
- `profiles_insert_service`: INSERT (TO service_role)
- `profiles_service_all`: ALL (TO service_role)

**Triggers:**
- `profiles_updated_at`: BEFORE UPDATE -> `set_updated_at()`
- `on_auth_user_created` (on `auth.users`): AFTER INSERT -> `handle_new_user()`

---

#### 2. `monthly_quota`

Tracks monthly search quota usage per user for plan-based pricing. Uses lazy reset via `month_year` key format.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` | PK |
| `user_id` | `uuid` | NOT NULL | -- | FK -> `auth.users(id) ON DELETE CASCADE` |
| `month_year` | `varchar(7)` | NOT NULL | -- | Format: `YYYY-MM` (e.g., `2026-02`) |
| `searches_count` | `int` | NOT NULL | `0` | |
| `created_at` | `timestamptz` | NOT NULL | `now()` | |
| `updated_at` | `timestamptz` | NOT NULL | `now()` | |

**Constraints:**
- `unique_user_month`: UNIQUE(`user_id`, `month_year`)

**Indexes:**
- `idx_monthly_quota_user_month` (on `user_id, month_year`)

**RLS Policies:**
- `Users can view own quota`: SELECT WHERE `auth.uid() = user_id`
- `Service role can manage quota`: ALL (TO service_role)

---

### Billing & Plans

#### 3. `plans`

Plan catalog. Seed data for all plan tiers. Source of truth for pricing.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `text` | NOT NULL | -- | PK. Values: `free, pack_5, pack_10, pack_20, monthly, annual, consultor_agil, maquina, sala_guerra, smartlic_pro, consultoria, master` |
| `name` | `text` | NOT NULL | -- | Display name |
| `description` | `text` | YES | -- | |
| `max_searches` | `int` | YES | -- | NULL = unlimited |
| `price_brl` | `numeric(10,2)` | NOT NULL | `0` | Base price in BRL |
| `duration_days` | `int` | YES | -- | NULL = perpetual |
| `stripe_price_id` | `text` | YES | -- | **DEPRECATED** (DEBT-017/DB-014). Use `stripe_price_id_monthly` etc. |
| `stripe_price_id_monthly` | `text` | YES | -- | Stripe Price ID for monthly billing |
| `stripe_price_id_semiannual` | `text` | YES | -- | Stripe Price ID for semiannual billing |
| `stripe_price_id_annual` | `text` | YES | -- | Stripe Price ID for annual billing |
| `is_active` | `boolean` | NOT NULL | `true` | Soft-delete for legacy plans |
| `created_at` | `timestamptz` | NOT NULL | `now()` | |
| `updated_at` | `timestamptz` | NOT NULL | `now()` | Auto-updated via trigger |

**Active plans (as of 2026-03):** `free` (inactive), `smartlic_pro`, `consultoria`, `master`
**Deactivated legacy plans:** `pack_5, pack_10, pack_20, monthly, annual, consultor_agil, maquina, sala_guerra`

**RLS Policies:**
- `plans_select_all`: SELECT USING (true) -- public catalog

**Triggers:**
- `plans_updated_at`: BEFORE UPDATE -> `set_updated_at()`

---

#### 4. `plan_billing_periods`

Multi-period pricing for subscription plans. Source of truth for Stripe Price IDs per billing period.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` | PK |
| `plan_id` | `text` | NOT NULL | -- | FK -> `plans(id) ON DELETE CASCADE` |
| `billing_period` | `text` | NOT NULL | -- | CHECK: `monthly, semiannual, annual` |
| `price_cents` | `integer` | NOT NULL | -- | Price in centavos (e.g., 199900 = R$1,999.00) |
| `discount_percent` | `integer` | YES | `0` | Discount vs. monthly (10% semi, 20% annual) |
| `stripe_price_id` | `text` | YES | -- | Stripe Price ID |
| `created_at` | `timestamptz` | YES | `now()` | |
| `updated_at` | `timestamptz` | YES | `now()` | Added by DEBT-017 |

**Constraints:**
- UNIQUE(`plan_id`, `billing_period`)

**RLS Policies:**
- `plan_billing_periods_public_read`: SELECT (TO authenticated, anon)
- `plan_billing_periods_service_all`: ALL (TO service_role)

**Triggers:**
- `trg_plan_billing_periods_updated_at`: BEFORE UPDATE -> `set_updated_at()`

---

#### 5. `plan_features`

Billing-period-specific feature flags for subscription plans.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `serial` | NOT NULL | auto-increment | PK |
| `plan_id` | `text` | NOT NULL | -- | FK -> `plans(id) ON DELETE CASCADE` |
| `billing_period` | `varchar(10)` | NOT NULL | -- | CHECK: `monthly, semiannual, annual` |
| `feature_key` | `varchar(100)` | NOT NULL | -- | e.g., `early_access, proactive_search, ai_analysis, multi_user, custom_branding` |
| `enabled` | `boolean` | NOT NULL | `true` | |
| `metadata` | `jsonb` | YES | `'{}'::jsonb` | Feature-specific config |
| `created_at` | `timestamptz` | NOT NULL | `now()` | |
| `updated_at` | `timestamptz` | NOT NULL | `now()` | |

**Constraints:**
- UNIQUE(`plan_id`, `billing_period`, `feature_key`)
- `plan_features_billing_period_check`: CHECK on `billing_period`

**Indexes:**
- `idx_plan_features_lookup` (on `plan_id, billing_period, enabled` WHERE `enabled = true`)

**RLS Policies:**
- `plan_features_select_all`: SELECT USING (true)

**Triggers:**
- `plan_features_updated_at`: BEFORE UPDATE -> `set_updated_at()`

---

#### 6. `user_subscriptions`

Active user subscriptions and purchased packs. Links to Stripe subscription/customer IDs.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` | PK |
| `user_id` | `uuid` | NOT NULL | -- | FK -> `profiles(id) ON DELETE CASCADE` |
| `plan_id` | `text` | NOT NULL | -- | FK -> `plans(id)` |
| `credits_remaining` | `int` | YES | -- | NULL = unlimited (monthly/annual/master) |
| `starts_at` | `timestamptz` | NOT NULL | `now()` | |
| `expires_at` | `timestamptz` | YES | -- | NULL = never expires |
| `stripe_subscription_id` | `text` | YES | -- | Stripe Subscription ID (unique, partial) |
| `stripe_customer_id` | `text` | YES | -- | Stripe Customer ID |
| `is_active` | `boolean` | NOT NULL | `true` | |
| `billing_period` | `varchar(10)` | NOT NULL | `'monthly'` | CHECK: `monthly, semiannual, annual` |
| `annual_benefits` | `jsonb` | NOT NULL | `'{}'::jsonb` | Annual-exclusive features |
| `subscription_status` | `text` | YES | `'active'` | CHECK: `active, trialing, past_due, canceled, expired` |
| `created_at` | `timestamptz` | NOT NULL | `now()` | |
| `updated_at` | `timestamptz` | NOT NULL | `now()` | Auto-updated via trigger |

**Indexes:**
- `idx_user_subscriptions_user` (on `user_id`)
- `idx_user_subscriptions_active` (on `user_id, is_active` WHERE `is_active = true`)
- `idx_user_subscriptions_billing` (on `user_id, billing_period, is_active` WHERE `is_active = true`)
- `idx_user_subscriptions_stripe_sub_id` (UNIQUE on `stripe_subscription_id` WHERE NOT NULL)

**RLS Policies:**
- `subscriptions_select_own`: SELECT WHERE `auth.uid() = user_id`
- `Service role can manage subscriptions`: ALL (TO service_role)

**Triggers:**
- `user_subscriptions_updated_at`: BEFORE UPDATE -> `set_updated_at()`

---

#### 7. `stripe_webhook_events`

Idempotency table for Stripe webhook processing. Prevents duplicate event processing.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `varchar(255)` | NOT NULL | -- | PK. Stripe event ID (`evt_xxx`). CHECK: starts with `evt_` |
| `type` | `varchar(100)` | NOT NULL | -- | Stripe event type |
| `processed_at` | `timestamptz` | NOT NULL | `now()` | |
| `payload` | `jsonb` | YES | -- | Full Stripe event object for debugging |

**Constraints:**
- `check_event_id_format`: CHECK (`id ~ '^evt_'`)

**Indexes:**
- `idx_webhook_events_type` (on `type, processed_at`)
- `idx_webhook_events_recent` (on `processed_at DESC`)

**RLS Policies:**
- `webhook_events_insert_service`: INSERT WITH CHECK (true) -- service role bypasses
- `webhook_events_select_admin`: SELECT WHERE profile `is_admin = true`

---

### Search Pipeline

#### 8. `search_sessions`

Search history per user. Records every search attempt with lifecycle tracking.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` | PK |
| `user_id` | `uuid` | NOT NULL | -- | FK -> `profiles(id) ON DELETE CASCADE` |
| `search_id` | `uuid` | YES | -- | Correlation ID linking SSE, ARQ jobs, cache |
| `sectors` | `text[]` | NOT NULL | -- | |
| `ufs` | `text[]` | NOT NULL | -- | |
| `data_inicial` | `date` | NOT NULL | -- | |
| `data_final` | `date` | NOT NULL | -- | |
| `custom_keywords` | `text[]` | YES | -- | |
| `total_raw` | `int` | NOT NULL | `0` | Items fetched before filtering |
| `total_filtered` | `int` | NOT NULL | `0` | Items after filtering |
| `valor_total` | `numeric(14,2)` | YES | `0` | |
| `resumo_executivo` | `text` | YES | -- | LLM-generated summary |
| `destaques` | `text[]` | YES | -- | Highlights |
| `excel_storage_path` | `text` | YES | -- | Supabase Storage path |
| `status` | `text` | NOT NULL | `'created'` | CHECK: `created, processing, completed, failed, timed_out, cancelled` |
| `error_message` | `text` | YES | -- | Human-readable error |
| `error_code` | `text` | YES | -- | Machine-readable: `sources_unavailable, timeout, filter_error, llm_error, db_error, quota_exceeded, unknown` |
| `started_at` | `timestamptz` | NOT NULL | `now()` | |
| `completed_at` | `timestamptz` | YES | -- | |
| `duration_ms` | `integer` | YES | -- | |
| `pipeline_stage` | `text` | YES | -- | Last stage: `validate, prepare, execute, filter, enrich, generate, persist` |
| `raw_count` | `integer` | YES | `0` | |
| `response_state` | `text` | YES | -- | `live, cached, degraded, empty_failure` |
| `failed_ufs` | `text[]` | YES | -- | UF codes that failed |
| `created_at` | `timestamptz` | NOT NULL | `now()` | |

**Indexes:**
- `idx_search_sessions_user` (on `user_id`)
- `idx_search_sessions_created` (on `user_id, created_at DESC`)
- `idx_search_sessions_search_id` (on `search_id` WHERE NOT NULL)
- `idx_search_sessions_status` (on `status` WHERE `status IN ('created', 'processing')`)
- `idx_search_sessions_inflight` (on `status, started_at` WHERE `status IN ('created', 'processing')`)
- `idx_search_sessions_user_id` (on `user_id`)

**RLS Policies:**
- `sessions_select_own`: SELECT WHERE `auth.uid() = user_id`
- `sessions_insert_own`: INSERT WITH CHECK `auth.uid() = user_id`
- `Service role can manage search sessions`: ALL (TO service_role)

---

#### 9. `search_state_transitions`

Audit trail for search state machine transitions. Fire-and-forget inserts from pipeline.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` | PK |
| `search_id` | `uuid` | NOT NULL | -- | Correlates with `search_sessions.search_id` (no FK -- see DEBT-017/DB-050) |
| `from_state` | `text` | YES | -- | NULL for initial CREATED |
| `to_state` | `text` | NOT NULL | -- | |
| `stage` | `text` | YES | -- | Pipeline stage that triggered transition |
| `details` | `jsonb` | YES | `'{}'` | Arbitrary metadata |
| `duration_since_previous_ms` | `integer` | YES | -- | |
| `created_at` | `timestamptz` | NOT NULL | `now()` | |

**Indexes:**
- `idx_state_transitions_search_id` (on `search_id, created_at ASC`)
- `idx_state_transitions_to_state` (on `to_state, created_at`)

**RLS Policies:**
- `Users can read own transitions`: SELECT WHERE `search_id IN (SELECT search_id FROM search_sessions WHERE user_id = auth.uid())`
- `Service role can insert transitions`: INSERT (TO service_role)

**Design Note:** No FK to `search_sessions.search_id` because that column is nullable and not unique (retries can share IDs). Integrity enforced at application layer.

---

#### 10. `search_results_cache`

Persistent L2 cache of search results per user. Supports SWR pattern with hot/warm/cold priority.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` | PK |
| `user_id` | `uuid` | NOT NULL | -- | FK -> `auth.users(id) ON DELETE CASCADE` |
| `params_hash` | `text` | NOT NULL | -- | Per-user cache key |
| `params_hash_global` | `text` | YES | -- | Cross-user cache key for fallback |
| `search_params` | `jsonb` | NOT NULL | -- | Search parameters snapshot |
| `results` | `jsonb` | NOT NULL | -- | CHECK: <= 2MB (`chk_results_max_size`) |
| `total_results` | `integer` | NOT NULL | `0` | |
| `sources_json` | `jsonb` | NOT NULL | `'["pncp"]'::jsonb` | Data sources used |
| `fetched_at` | `timestamptz` | NOT NULL | `now()` | When data was fetched |
| `priority` | `text` | NOT NULL | `'cold'` | `hot, warm, cold` |
| `access_count` | `integer` | NOT NULL | `0` | |
| `last_accessed_at` | `timestamptz` | YES | -- | |
| `last_success_at` | `timestamptz` | YES | -- | |
| `last_attempt_at` | `timestamptz` | YES | -- | |
| `fail_streak` | `integer` | NOT NULL | `0` | |
| `degraded_until` | `timestamptz` | YES | -- | |
| `coverage` | `jsonb` | YES | -- | |
| `fetch_duration_ms` | `integer` | YES | -- | |
| `created_at` | `timestamptz` | NOT NULL | `now()` | |

**Constraints:**
- UNIQUE(`user_id`, `params_hash`)
- `chk_results_max_size`: CHECK (`octet_length(results::text) <= 2097152`)

**Indexes:**
- `idx_search_cache_user` (on `user_id, created_at DESC`)
- `idx_search_cache_params_hash` (on `params_hash`)
- `idx_search_cache_global_hash` (on `params_hash_global, created_at DESC`)
- `idx_search_cache_degraded` (on `degraded_until` WHERE NOT NULL)
- `idx_search_cache_priority` (on `user_id, priority, last_accessed_at`)
- `idx_search_cache_fetched_at` (on `fetched_at`)

**RLS Policies:**
- `Users can read own search cache`: SELECT WHERE `auth.uid() = user_id`
- `Service role full access on search_results_cache`: ALL (TO service_role)

**Triggers:**
- `trg_cleanup_search_cache`: AFTER INSERT -> `cleanup_search_cache_per_user()` (priority-aware eviction, max 10 per user)

---

#### 11. `search_results_store`

Persistent L3 storage for search results. Prevents "Busca nao encontrada" after L1/L2 TTL expiry.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `search_id` | `uuid` | NOT NULL | -- | PK |
| `user_id` | `uuid` | NOT NULL | -- | FK -> `auth.users(id)` |
| `results` | `jsonb` | NOT NULL | -- | CHECK: <= 2MB (`chk_result_data_size`) |
| `sector` | `text` | YES | -- | |
| `ufs` | `text[]` | YES | -- | |
| `total_filtered` | `int` | YES | `0` | |
| `created_at` | `timestamptz` | YES | `now()` | |
| `expires_at` | `timestamptz` | YES | `now() + '24 hours'` | |

**Constraints:**
- `chk_result_data_size`: CHECK (`octet_length(results::text) < 2097152`)

**Indexes:**
- `idx_search_results_user` (on `user_id`)
- `idx_search_results_expires` (on `expires_at`)
- `idx_search_results_store_user_id` (on `user_id`)
- `idx_search_results_store_user_expires` (on `user_id, expires_at`)

**RLS Policies:**
- `Users can read own results`: SELECT WHERE `auth.uid() = user_id`
- `Service role full access`: ALL WHERE `auth.role() = 'service_role'`

---

#### 12. `pipeline_items`

Opportunity pipeline -- tracking procurement opportunities through kanban stages.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` | PK |
| `user_id` | `uuid` | NOT NULL | -- | FK -> `auth.users(id) ON DELETE CASCADE` |
| `pncp_id` | `text` | NOT NULL | -- | PNCP unique ID (snapshot) |
| `objeto` | `text` | NOT NULL | -- | Procurement object description |
| `orgao` | `text` | YES | -- | Government agency |
| `uf` | `text` | YES | -- | State code |
| `valor_estimado` | `numeric` | YES | -- | |
| `data_encerramento` | `timestamptz` | YES | -- | Closing date |
| `link_pncp` | `text` | YES | -- | |
| `stage` | `text` | NOT NULL | `'descoberta'` | CHECK: `descoberta, analise, preparando, enviada, resultado` |
| `notes` | `text` | YES | -- | User notes |
| `created_at` | `timestamptz` | NOT NULL | `now()` | |
| `updated_at` | `timestamptz` | NOT NULL | `now()` | |

**Constraints:**
- UNIQUE(`user_id`, `pncp_id`)

**Indexes:**
- `idx_pipeline_user_stage` (on `user_id, stage`)
- `idx_pipeline_encerramento` (on `data_encerramento` WHERE `stage NOT IN ('enviada', 'resultado')`)
- `idx_pipeline_user_created` (on `user_id, created_at DESC`)
- `idx_pipeline_items_user_id` (on `user_id`)

**RLS Policies:**
- `Users can view/insert/update/delete own pipeline items` (4 per-operation policies)
- `Service role full access on pipeline_items`: ALL (TO service_role)

**Triggers:**
- `tr_pipeline_items_updated_at`: BEFORE UPDATE -> `update_pipeline_updated_at()`

---

#### 13. `classification_feedback`

User feedback on search result relevance for continuous LLM improvement.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` | PK |
| `user_id` | `uuid` | NOT NULL | -- | FK -> `auth.users(id)` |
| `search_id` | `uuid` | NOT NULL | -- | |
| `bid_id` | `text` | NOT NULL | -- | |
| `setor_id` | `text` | NOT NULL | -- | |
| `user_verdict` | `text` | NOT NULL | -- | CHECK: `false_positive, false_negative, correct` |
| `reason` | `text` | YES | -- | |
| `category` | `text` | YES | -- | CHECK: `wrong_sector, irrelevant_modality, too_small, too_large, closed, other` |
| `bid_objeto` | `text` | YES | -- | Snapshot of bid description |
| `bid_valor` | `decimal` | YES | -- | |
| `bid_uf` | `text` | YES | -- | |
| `confidence_score` | `integer` | YES | -- | |
| `relevance_source` | `text` | YES | -- | |
| `created_at` | `timestamptz` | YES | `now()` | |

**Constraints:**
- UNIQUE(`user_id`, `search_id`, `bid_id`)

**Indexes:**
- `idx_feedback_sector_verdict` (on `setor_id, user_verdict, created_at`)
- `idx_feedback_user_created` (on `user_id, created_at`)
- `idx_classification_feedback_user_id` (on `user_id`)

**RLS Policies:**
- `feedback_insert_own`: INSERT WHERE `auth.uid() = user_id`
- `feedback_select_own`: SELECT WHERE `auth.uid() = user_id`
- `feedback_update_own`: UPDATE WHERE `auth.uid() = user_id`
- `feedback_delete_own`: DELETE WHERE `auth.uid() = user_id`
- `service_role_all`: ALL (TO service_role)

---

### Messaging

#### 14. `conversations`

Internal support messaging system. User-to-admin conversation threads.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` | PK |
| `user_id` | `uuid` | NOT NULL | -- | FK -> `profiles(id) ON DELETE CASCADE` |
| `subject` | `text` | NOT NULL | -- | CHECK: `char_length <= 200` |
| `category` | `text` | NOT NULL | -- | CHECK: `suporte, sugestao, funcionalidade, bug, outro` |
| `status` | `text` | NOT NULL | `'aberto'` | CHECK: `aberto, respondido, resolvido` |
| `last_message_at` | `timestamptz` | NOT NULL | `now()` | Auto-updated by trigger |
| `first_response_at` | `timestamptz` | YES | -- | SLA tracking (STORY-353) |
| `created_at` | `timestamptz` | NOT NULL | `now()` | |
| `updated_at` | `timestamptz` | NOT NULL | `now()` | |

**Indexes:**
- `idx_conversations_user_id` (on `user_id`)
- `idx_conversations_status` (on `status`)
- `idx_conversations_last_message` (on `last_message_at DESC`)
- `idx_conversations_unanswered` (on `created_at` WHERE `first_response_at IS NULL AND status != 'resolvido'`)

**RLS Policies:**
- `conversations_select_own`: SELECT (own or admin)
- `conversations_insert_own`: INSERT WHERE `auth.uid() = user_id`
- `conversations_update_admin`: UPDATE (admin only)
- `conversations_service_all`: ALL (TO service_role)

**Triggers:**
- `trg_update_conversation_last_message` (on `messages`): AFTER INSERT -> `update_conversation_last_message()`

---

#### 15. `messages`

Individual messages within conversations.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` | PK |
| `conversation_id` | `uuid` | NOT NULL | -- | FK -> `conversations(id) ON DELETE CASCADE` |
| `sender_id` | `uuid` | NOT NULL | -- | FK -> `profiles(id) ON DELETE CASCADE` |
| `body` | `text` | NOT NULL | -- | CHECK: `1 <= char_length <= 5000` |
| `is_admin_reply` | `boolean` | NOT NULL | `false` | |
| `read_by_user` | `boolean` | NOT NULL | `false` | |
| `read_by_admin` | `boolean` | NOT NULL | `false` | |
| `created_at` | `timestamptz` | NOT NULL | `now()` | |

**Indexes:**
- `idx_messages_conversation` (on `conversation_id, created_at`)
- `idx_messages_unread_by_user` (on `conversation_id` WHERE `is_admin_reply = true AND read_by_user = false`)
- `idx_messages_unread_by_admin` (on `conversation_id` WHERE `is_admin_reply = false AND read_by_admin = false`)

**RLS Policies:**
- `messages_select`: SELECT via conversation ownership
- `messages_insert_user`: INSERT via conversation ownership + sender check
- `messages_update_read`: UPDATE via conversation ownership
- `messages_service_all`: ALL (TO service_role)

---

### Alerts & Notifications

#### 16. `alert_preferences`

Per-user email alert preferences for digest scheduling.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` | PK |
| `user_id` | `uuid` | NOT NULL | -- | FK -> `profiles(id) ON DELETE CASCADE`. UNIQUE |
| `frequency` | `alert_frequency` | NOT NULL | `'daily'` | ENUM: `daily, twice_weekly, weekly, off` |
| `enabled` | `boolean` | NOT NULL | `true` | |
| `last_digest_sent_at` | `timestamptz` | YES | -- | |
| `created_at` | `timestamptz` | NOT NULL | `now()` | |
| `updated_at` | `timestamptz` | NOT NULL | `now()` | |

**Indexes:**
- `idx_alert_preferences_user_id` (on `user_id`) -- NOTE: redundant with unique constraint
- `idx_alert_preferences_digest_due` (on `enabled, frequency, last_digest_sent_at` WHERE `enabled = true AND frequency != 'off'`)

**RLS Policies:**
- Users can view/insert/update own alert preferences (3 policies)
- `Service role full access to alert preferences`: ALL WHERE `auth.role() = 'service_role'`

**Triggers:**
- `trigger_alert_preferences_updated_at`: BEFORE UPDATE -> `update_alert_preferences_updated_at()`
- `trigger_create_alert_preferences_on_profile` (on `profiles`): AFTER INSERT -> `create_default_alert_preferences()`

---

#### 17. `alerts`

User-defined email alerts with search filters.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` | PK |
| `user_id` | `uuid` | NOT NULL | -- | FK -> `profiles(id) ON DELETE CASCADE` |
| `name` | `text` | NOT NULL | `''` | |
| `filters` | `jsonb` | NOT NULL | `'{}'::jsonb` | `{setor, ufs[], valor_min, valor_max, keywords[]}` |
| `active` | `boolean` | NOT NULL | `true` | |
| `created_at` | `timestamptz` | NOT NULL | `now()` | |
| `updated_at` | `timestamptz` | NOT NULL | `now()` | |

**Indexes:**
- `idx_alerts_user_id` (on `user_id`)
- `idx_alerts_active` (on `user_id, active` WHERE `active = true`)

**RLS Policies:**
- Users can view/insert/update/delete own alerts (4 policies)
- `Service role full access to alerts`: ALL (TO service_role)

**Triggers:**
- `trigger_alerts_updated_at`: BEFORE UPDATE -> `update_alerts_updated_at()`

---

#### 18. `alert_sent_items`

Dedup tracking for alert items already sent. Prevents duplicate notifications.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` | PK |
| `alert_id` | `uuid` | NOT NULL | -- | FK -> `alerts(id) ON DELETE CASCADE` |
| `item_id` | `text` | NOT NULL | -- | PNCP item ID |
| `sent_at` | `timestamptz` | NOT NULL | `now()` | |

**Indexes:**
- `idx_alert_sent_items_dedup` (UNIQUE on `alert_id, item_id`)
- `idx_alert_sent_items_alert_id` (on `alert_id`)
- `idx_alert_sent_items_sent_at` (on `sent_at`)

**RLS Policies:**
- `Service role full access to alert_sent_items`: ALL (TO service_role)
- `Users can view own alert sent items`: SELECT via join to alerts

---

#### 19. `trial_email_log`

Tracks trial reminder emails to prevent duplicate sends.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` | PK |
| `user_id` | `uuid` | NOT NULL | -- | FK -> `auth.users(id) ON DELETE CASCADE` |
| `email_type` | `text` | NOT NULL | -- | `midpoint, expiring, last_day, expired` |
| `sent_at` | `timestamptz` | NOT NULL | `now()` | |

**Constraints:**
- UNIQUE(`user_id`, `email_type`)

**Indexes:**
- `idx_trial_email_log_user_id` (on `user_id`)

**RLS Policies:**
- No user-facing policies. Only accessible via service_role (bypasses RLS).

---

### Analytics & Audit

#### 20. `audit_events`

Persistent audit log for security-relevant events. PII stored as SHA-256 hashes for LGPD/GDPR compliance. 12-month retention.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` | PK |
| `timestamp` | `timestamptz` | NOT NULL | `now()` | |
| `event_type` | `text` | NOT NULL | -- | e.g., `auth.login, billing.checkout, data.search` |
| `actor_id_hash` | `text` | YES | -- | SHA-256 truncated to 16 hex chars |
| `target_id_hash` | `text` | YES | -- | SHA-256 truncated to 16 hex chars |
| `details` | `jsonb` | YES | -- | Sanitized metadata |
| `ip_hash` | `text` | YES | -- | SHA-256 truncated to 16 hex chars |

**Indexes:**
- `idx_audit_events_event_type` (on `event_type`)
- `idx_audit_events_timestamp` (on `timestamp`)
- `idx_audit_events_actor` (on `actor_id_hash` WHERE NOT NULL)
- `idx_audit_events_type_timestamp` (on `event_type, timestamp DESC`)

**RLS Policies:**
- `Service role can manage audit events`: ALL (TO service_role)
- `Admins can read audit events`: SELECT WHERE profile `is_admin = true`

**Retention:** 12 months via pg_cron (`cleanup-audit-events`, 1st of month 4am UTC)

---

### Integrations

#### 21. `user_oauth_tokens`

Encrypted OAuth 2.0 tokens for third-party integrations (Google Sheets).

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` | PK |
| `user_id` | `uuid` | NOT NULL | -- | FK -> `auth.users(id) ON DELETE CASCADE` |
| `provider` | `varchar(50)` | NOT NULL | -- | CHECK: `google, microsoft, dropbox` |
| `access_token` | `text` | NOT NULL | -- | AES-256 encrypted |
| `refresh_token` | `text` | YES | -- | AES-256 encrypted |
| `expires_at` | `timestamptz` | NOT NULL | -- | |
| `scope` | `text` | NOT NULL | -- | |
| `created_at` | `timestamptz` | YES | `now()` | |
| `updated_at` | `timestamptz` | YES | `now()` | |

**Constraints:**
- `unique_user_provider`: UNIQUE(`user_id`, `provider`)

**Indexes:**
- `idx_user_oauth_tokens_user_id` (on `user_id`)
- `idx_user_oauth_tokens_expires_at` (on `expires_at`)
- `idx_user_oauth_tokens_provider` (on `provider`)

**RLS Policies:**
- Users can view/update/delete own OAuth tokens (3 policies)
- `Service role can manage all OAuth tokens`: ALL (TO service_role)

---

#### 22. `google_sheets_exports`

Audit trail for Google Sheets exports. Enables "re-open last export".

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` | PK |
| `user_id` | `uuid` | NOT NULL | -- | FK -> `auth.users(id) ON DELETE CASCADE` |
| `spreadsheet_id` | `varchar(255)` | NOT NULL | -- | |
| `spreadsheet_url` | `text` | NOT NULL | -- | |
| `search_params` | `jsonb` | NOT NULL | -- | GIN-indexed |
| `total_rows` | `int` | NOT NULL | -- | CHECK: `>= 0` |
| `created_at` | `timestamptz` | NOT NULL | `now()` | |
| `last_updated_at` | `timestamptz` | YES | `now()` | |

**Indexes:**
- `idx_google_sheets_exports_user_id` (on `user_id`)
- `idx_google_sheets_exports_created_at` (on `created_at DESC`)
- `idx_google_sheets_exports_spreadsheet_id` (on `spreadsheet_id`)
- `idx_google_sheets_exports_search_params` (GIN on `search_params`)

**RLS Policies:**
- Users can view/insert/update own exports (3 policies)
- `Service role can manage all Google Sheets exports`: ALL (TO service_role)

---

### Organizations & Partners

#### 23. `organizations`

Multi-user organizations for consultoria/agency accounts (STORY-322).

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` | PK |
| `name` | `text` | NOT NULL | -- | |
| `logo_url` | `text` | YES | -- | |
| `owner_id` | `uuid` | NOT NULL | -- | FK -> `auth.users(id) ON DELETE RESTRICT` |
| `max_members` | `int` | NOT NULL | `5` | |
| `plan_type` | `text` | NOT NULL | `'consultoria'` | |
| `stripe_customer_id` | `text` | YES | -- | |
| `created_at` | `timestamptz` | NOT NULL | `now()` | |
| `updated_at` | `timestamptz` | NOT NULL | `now()` | |

**Indexes:**
- `idx_organizations_owner` (on `owner_id`)

**RLS Policies:**
- `Org owner can view organization`: SELECT WHERE `auth.uid() = owner_id`
- `Org admins can view organization`: SELECT via member role check
- `Owner can insert/update organization` (2 policies)
- `Service role full access on organizations`: ALL WHERE `auth.role() = 'service_role'`

**Triggers:**
- `tr_organizations_updated_at`: BEFORE UPDATE -> `set_updated_at()`

---

#### 24. `organization_members`

Members of organizations with role-based access.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` | PK |
| `org_id` | `uuid` | NOT NULL | -- | FK -> `organizations(id) ON DELETE CASCADE` |
| `user_id` | `uuid` | NOT NULL | -- | FK -> `auth.users(id) ON DELETE CASCADE` |
| `role` | `text` | NOT NULL | `'member'` | CHECK: `owner, admin, member` |
| `invited_at` | `timestamptz` | NOT NULL | `now()` | |
| `accepted_at` | `timestamptz` | YES | -- | NULL = pending invitation |

**Constraints:**
- UNIQUE(`org_id`, `user_id`)

**Indexes:**
- `idx_org_members_org` (on `org_id`)
- `idx_org_members_user` (on `user_id`)

**RLS Policies:**
- `Users can view own membership`: SELECT WHERE `auth.uid() = user_id`
- `Org owner/admin can view all members`: SELECT via role check
- `Org owner/admin can insert/delete members` (2 policies, with owner bootstrap)
- `Service role full access on organization_members`: ALL WHERE `auth.role() = 'service_role'`

---

#### 25. `partners`

Revenue share partner tracking (STORY-323).

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` | PK |
| `name` | `text` | NOT NULL | -- | |
| `slug` | `text` | NOT NULL | -- | UNIQUE. URL-safe identifier |
| `contact_email` | `text` | NOT NULL | -- | |
| `contact_name` | `text` | YES | -- | |
| `stripe_coupon_id` | `text` | YES | -- | |
| `revenue_share_pct` | `numeric(5,2)` | YES | `25.00` | |
| `status` | `text` | YES | `'active'` | CHECK: `active, inactive, pending` |
| `created_at` | `timestamptz` | NOT NULL | `now()` | |

**Indexes:**
- `idx_partners_slug` (on `slug`)
- `idx_partners_status` (on `status`)

**RLS Policies:**
- `partners_admin_all`: ALL WHERE profile `is_admin = true`
- `partners_self_read`: SELECT WHERE `contact_email` matches user email
- `partners_service_role`: ALL WHERE `auth.role() = 'service_role'`

---

#### 26. `partner_referrals`

Referral tracking between partners and users.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` | PK |
| `partner_id` | `uuid` | NOT NULL | -- | FK -> `partners(id)` |
| `referred_user_id` | `uuid` | YES | -- | FK -> `auth.users(id)` (nullable for ON DELETE SET NULL) |
| `signup_at` | `timestamptz` | YES | `now()` | |
| `converted_at` | `timestamptz` | YES | -- | |
| `churned_at` | `timestamptz` | YES | -- | |
| `monthly_revenue` | `numeric(10,2)` | YES | -- | |
| `revenue_share_amount` | `numeric(10,2)` | YES | -- | |

**Constraints:**
- UNIQUE(`partner_id`, `referred_user_id`)

**Indexes:**
- `idx_partner_referrals_partner_id` (on `partner_id`)
- `idx_partner_referrals_referred_user_id` (on `referred_user_id`)

**RLS Policies:**
- `partner_referrals_admin_all`: ALL WHERE profile `is_admin = true`
- `partner_referrals_partner_read`: SELECT via partner ownership
- `partner_referrals_service_role`: ALL WHERE `auth.role() = 'service_role'`

---

### Infrastructure

#### 27. `health_checks`

Periodic health check results for uptime calculation (STORY-316). 30-day retention.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` | PK |
| `checked_at` | `timestamptz` | NOT NULL | `now()` | |
| `overall_status` | `text` | NOT NULL | -- | CHECK: `healthy, degraded, unhealthy` |
| `sources_json` | `jsonb` | NOT NULL | `'{}'` | |
| `components_json` | `jsonb` | NOT NULL | `'{}'` | |
| `latency_ms` | `integer` | YES | -- | |

**Indexes:**
- `idx_health_checks_checked_at` (on `checked_at DESC`)

**RLS Policies:**
- `service_role_all`: ALL (TO service_role)

---

#### 28. `incidents`

System incidents for public status page (STORY-316).

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | `uuid` | NOT NULL | `gen_random_uuid()` | PK |
| `started_at` | `timestamptz` | NOT NULL | `now()` | |
| `resolved_at` | `timestamptz` | YES | -- | |
| `status` | `text` | NOT NULL | `'ongoing'` | CHECK: `ongoing, resolved` |
| `affected_sources` | `text[]` | NOT NULL | `'{}'` | |
| `description` | `text` | NOT NULL | `''` | |

**Indexes:**
- `idx_incidents_status` (on `status` WHERE `status = 'ongoing'`)
- `idx_incidents_started_at` (on `started_at DESC`)

**RLS Policies:**
- `service_role_all`: ALL (TO service_role)

---

## Relationships

```
auth.users (Supabase managed)
  |
  |-- 1:1 --> profiles (id = auth.users.id)
  |              |-- 1:N --> user_subscriptions
  |              |-- 1:N --> search_sessions
  |              |-- 1:N --> conversations
  |              |-- 1:N --> pipeline_items
  |              |-- 1:N --> alerts
  |              |-- 1:1 --> alert_preferences
  |              |-- 0:1 --> organizations (via owner_id)
  |              |-- N:M --> organizations (via organization_members)
  |
  |-- 1:N --> monthly_quota
  |-- 1:N --> user_oauth_tokens
  |-- 1:N --> google_sheets_exports
  |-- 1:N --> classification_feedback
  |-- 1:N --> trial_email_log
  |-- 1:N --> search_results_cache
  |-- 1:N --> search_results_store
  |-- 0:N --> partner_referrals (via referred_user_id)

plans
  |-- 1:N --> plan_billing_periods
  |-- 1:N --> plan_features
  |-- 1:N --> user_subscriptions (via plan_id)

search_sessions
  |-- (logical) --> search_state_transitions (via search_id, no FK)

alerts
  |-- 1:N --> alert_sent_items

organizations
  |-- 1:N --> organization_members

partners
  |-- 1:N --> partner_referrals
  |-- 0:N <-- profiles (via referred_by_partner_id)

conversations
  |-- 1:N --> messages
```

### FK Reference Summary

| Child Table | Column | Parent Table | Parent Column | ON DELETE |
|-------------|--------|--------------|---------------|-----------|
| `profiles` | `id` | `auth.users` | `id` | CASCADE |
| `profiles` | `referred_by_partner_id` | `partners` | `id` | (none) |
| `monthly_quota` | `user_id` | `auth.users` | `id` | CASCADE |
| `user_subscriptions` | `user_id` | `profiles` | `id` | CASCADE |
| `user_subscriptions` | `plan_id` | `plans` | `id` | (none) |
| `plan_billing_periods` | `plan_id` | `plans` | `id` | CASCADE |
| `plan_features` | `plan_id` | `plans` | `id` | CASCADE |
| `search_sessions` | `user_id` | `profiles` | `id` | CASCADE |
| `search_results_cache` | `user_id` | `auth.users` | `id` | CASCADE |
| `search_results_store` | `user_id` | `auth.users` | `id` | (none) |
| `pipeline_items` | `user_id` | `auth.users` | `id` | CASCADE |
| `classification_feedback` | `user_id` | `auth.users` | `id` | (none) |
| `conversations` | `user_id` | `profiles` | `id` | CASCADE |
| `messages` | `conversation_id` | `conversations` | `id` | CASCADE |
| `messages` | `sender_id` | `profiles` | `id` | CASCADE |
| `user_oauth_tokens` | `user_id` | `auth.users` | `id` | CASCADE |
| `google_sheets_exports` | `user_id` | `auth.users` | `id` | CASCADE |
| `alert_preferences` | `user_id` | `profiles` | `id` | CASCADE |
| `alerts` | `user_id` | `profiles` | `id` | CASCADE |
| `alert_sent_items` | `alert_id` | `alerts` | `id` | CASCADE |
| `trial_email_log` | `user_id` | `auth.users` | `id` | CASCADE |
| `audit_events` | (none) | -- | -- | -- |
| `organizations` | `owner_id` | `auth.users` | `id` | RESTRICT |
| `organization_members` | `org_id` | `organizations` | `id` | CASCADE |
| `organization_members` | `user_id` | `auth.users` | `id` | CASCADE |
| `partners` | (none) | -- | -- | -- |
| `partner_referrals` | `partner_id` | `partners` | `id` | (none) |
| `partner_referrals` | `referred_user_id` | `auth.users` | `id` | (SET NULL) |
| `health_checks` | (none) | -- | -- | -- |
| `incidents` | (none) | -- | -- | -- |
| `stripe_webhook_events` | (none) | -- | -- | -- |

**Note on FK targets:** Some tables reference `auth.users(id)` directly, others reference `profiles(id)`. Both work because `profiles.id` is the same UUID as `auth.users.id`. The inconsistency is documented in DB-AUDIT.md.

---

## Indexes

### Complete Index Inventory (70+)

| Table | Index | Columns | Type | Notes |
|-------|-------|---------|------|-------|
| **profiles** | `profiles_pkey` | `id` | PK | |
| | `idx_profiles_email_trgm` | `email` | GIN trigram | Admin search |
| | `idx_profiles_subscription_status` | `subscription_status` | Partial | WHERE != 'trial' |
| | `idx_profiles_context_porte` | `context_data->>'porte_empresa'` | B-tree | WHERE NOT NULL |
| | `idx_profiles_phone_whatsapp_unique` | `phone_whatsapp` | Partial unique | WHERE NOT NULL |
| | `idx_profiles_referred_by_partner` | `referred_by_partner_id` | Partial | WHERE NOT NULL |
| **plans** | `plans_pkey` | `id` | PK | |
| **plan_billing_periods** | `plan_billing_periods_pkey` | `id` | PK | |
| | (unique) | `plan_id, billing_period` | UNIQUE | |
| **plan_features** | `plan_features_pkey` | `id` | PK (serial) | |
| | (unique) | `plan_id, billing_period, feature_key` | UNIQUE | |
| | `idx_plan_features_lookup` | `plan_id, billing_period, enabled` | Partial | WHERE enabled |
| **user_subscriptions** | `user_subscriptions_pkey` | `id` | PK | |
| | `idx_user_subscriptions_user` | `user_id` | B-tree | |
| | `idx_user_subscriptions_active` | `user_id, is_active` | Partial | WHERE active |
| | `idx_user_subscriptions_billing` | `user_id, billing_period, is_active` | Partial | WHERE active |
| | `idx_user_subscriptions_stripe_sub_id` | `stripe_subscription_id` | Partial unique | WHERE NOT NULL |
| **stripe_webhook_events** | `stripe_webhook_events_pkey` | `id` | PK | |
| | `idx_webhook_events_type` | `type, processed_at` | B-tree | |
| | `idx_webhook_events_recent` | `processed_at` | B-tree DESC | |
| **monthly_quota** | `monthly_quota_pkey` | `id` | PK | |
| | `idx_monthly_quota_user_month` | `user_id, month_year` | B-tree | |
| | `unique_user_month` | `user_id, month_year` | UNIQUE | |
| **search_sessions** | `search_sessions_pkey` | `id` | PK | |
| | `idx_search_sessions_user` | `user_id` | B-tree | |
| | `idx_search_sessions_created` | `user_id, created_at DESC` | B-tree | |
| | `idx_search_sessions_search_id` | `search_id` | Partial | WHERE NOT NULL |
| | `idx_search_sessions_status` | `status` | Partial | WHERE in-flight |
| | `idx_search_sessions_inflight` | `status, started_at` | Partial | WHERE in-flight |
| | `idx_search_sessions_user_id` | `user_id` | B-tree | Potentially redundant with idx_search_sessions_user |
| **search_state_transitions** | `search_state_transitions_pkey` | `id` | PK | |
| | `idx_state_transitions_search_id` | `search_id, created_at ASC` | B-tree | |
| | `idx_state_transitions_to_state` | `to_state, created_at` | B-tree | |
| **search_results_cache** | `search_results_cache_pkey` | `id` | PK | |
| | (unique) | `user_id, params_hash` | UNIQUE | |
| | `idx_search_cache_user` | `user_id, created_at DESC` | B-tree | |
| | `idx_search_cache_params_hash` | `params_hash` | B-tree | |
| | `idx_search_cache_global_hash` | `params_hash_global, created_at DESC` | B-tree | |
| | `idx_search_cache_degraded` | `degraded_until` | Partial | WHERE NOT NULL |
| | `idx_search_cache_priority` | `user_id, priority, last_accessed_at` | B-tree | |
| | `idx_search_cache_fetched_at` | `fetched_at` | B-tree | |
| **search_results_store** | `search_results_store_pkey` | `search_id` | PK | |
| | `idx_search_results_user` | `user_id` | B-tree | |
| | `idx_search_results_expires` | `expires_at` | B-tree | |
| | `idx_search_results_store_user_id` | `user_id` | B-tree | Redundant with idx_search_results_user |
| | `idx_search_results_store_user_expires` | `user_id, expires_at` | B-tree | |
| **pipeline_items** | `pipeline_items_pkey` | `id` | PK | |
| | (unique) | `user_id, pncp_id` | UNIQUE | |
| | `idx_pipeline_user_stage` | `user_id, stage` | B-tree | |
| | `idx_pipeline_encerramento` | `data_encerramento` | Partial | WHERE stage not done |
| | `idx_pipeline_user_created` | `user_id, created_at DESC` | B-tree | |
| | `idx_pipeline_items_user_id` | `user_id` | B-tree | |
| **classification_feedback** | (unique) | `user_id, search_id, bid_id` | UNIQUE | |
| | `idx_feedback_sector_verdict` | `setor_id, user_verdict, created_at` | B-tree | |
| | `idx_feedback_user_created` | `user_id, created_at` | B-tree | |
| | `idx_classification_feedback_user_id` | `user_id` | B-tree | |
| **conversations** | `idx_conversations_user_id` | `user_id` | B-tree | |
| | `idx_conversations_status` | `status` | B-tree | |
| | `idx_conversations_last_message` | `last_message_at DESC` | B-tree | |
| | `idx_conversations_unanswered` | `created_at` | Partial | WHERE unanswered |
| **messages** | `idx_messages_conversation` | `conversation_id, created_at` | B-tree | |
| | `idx_messages_unread_by_user` | `conversation_id` | Partial | |
| | `idx_messages_unread_by_admin` | `conversation_id` | Partial | |
| **alert_preferences** | `alert_preferences_user_id_unique` | `user_id` | UNIQUE | |
| | `idx_alert_preferences_user_id` | `user_id` | B-tree | Redundant |
| | `idx_alert_preferences_digest_due` | `enabled, frequency, last_digest_sent_at` | Partial | |
| **alerts** | `idx_alerts_user_id` | `user_id` | B-tree | |
| | `idx_alerts_active` | `user_id, active` | Partial | WHERE active |
| **alert_sent_items** | `idx_alert_sent_items_dedup` | `alert_id, item_id` | UNIQUE | |
| | `idx_alert_sent_items_alert_id` | `alert_id` | B-tree | |
| | `idx_alert_sent_items_sent_at` | `sent_at` | B-tree | |
| **trial_email_log** | (unique) | `user_id, email_type` | UNIQUE | |
| | `idx_trial_email_log_user_id` | `user_id` | B-tree | |
| **audit_events** | `idx_audit_events_event_type` | `event_type` | B-tree | |
| | `idx_audit_events_timestamp` | `timestamp` | B-tree | |
| | `idx_audit_events_actor` | `actor_id_hash` | Partial | WHERE NOT NULL |
| | `idx_audit_events_type_timestamp` | `event_type, timestamp DESC` | B-tree | |
| **user_oauth_tokens** | (unique) | `user_id, provider` | UNIQUE | |
| | `idx_user_oauth_tokens_user_id` | `user_id` | B-tree | |
| | `idx_user_oauth_tokens_expires_at` | `expires_at` | B-tree | |
| | `idx_user_oauth_tokens_provider` | `provider` | B-tree | |
| **google_sheets_exports** | `idx_google_sheets_exports_user_id` | `user_id` | B-tree | |
| | `idx_google_sheets_exports_created_at` | `created_at DESC` | B-tree | |
| | `idx_google_sheets_exports_spreadsheet_id` | `spreadsheet_id` | B-tree | |
| | `idx_google_sheets_exports_search_params` | `search_params` | GIN | |
| **organizations** | `idx_organizations_owner` | `owner_id` | B-tree | |
| **organization_members** | (unique) | `org_id, user_id` | UNIQUE | |
| | `idx_org_members_org` | `org_id` | B-tree | |
| | `idx_org_members_user` | `user_id` | B-tree | |
| **partners** | (unique) | `slug` | UNIQUE | |
| | `idx_partners_slug` | `slug` | B-tree | Redundant with unique |
| | `idx_partners_status` | `status` | B-tree | |
| **partner_referrals** | (unique) | `partner_id, referred_user_id` | UNIQUE | |
| | `idx_partner_referrals_partner_id` | `partner_id` | B-tree | |
| | `idx_partner_referrals_referred_user_id` | `referred_user_id` | B-tree | |
| **health_checks** | `idx_health_checks_checked_at` | `checked_at DESC` | B-tree | |
| **incidents** | `idx_incidents_status` | `status` | Partial | WHERE ongoing |
| | `idx_incidents_started_at` | `started_at DESC` | B-tree | |

---

## RLS Policies

All 27 tables have RLS enabled. Policy patterns used:

| Pattern | Description | Tables |
|---------|-------------|--------|
| **User-own** | `auth.uid() = user_id` | profiles, monthly_quota, search_sessions, user_subscriptions, pipeline_items, conversations, alerts, alert_preferences, classification_feedback, user_oauth_tokens, google_sheets_exports |
| **Service-role-only** | `TO service_role USING (true)` | All tables with backend write access |
| **Admin** | Profile `is_admin = true` join | audit_events, stripe_webhook_events, conversations (update), partners, partner_referrals |
| **Public read** | `USING (true)` | plans, plan_features, plan_billing_periods |
| **Conversation-chain** | JOIN through conversation ownership | messages, alert_sent_items |
| **No user policies** | service_role only | trial_email_log, health_checks, incidents |

---

## Functions and Triggers

### Functions

| Function | Returns | Security | Purpose |
|----------|---------|----------|---------|
| `handle_new_user()` | trigger | DEFINER | Auto-creates profile on signup. Normalizes phone number. Sets `plan_type = 'free_trial'` |
| `set_updated_at()` | trigger | -- | Canonical `updated_at = NOW()` trigger (consolidated from DEBT-001) |
| `increment_quota_atomic(uuid, varchar, int)` | TABLE | -- | Atomic quota check + increment with row locking |
| `check_and_increment_quota(uuid, varchar, int)` | TABLE | -- | Combined check-and-increment for `/buscar` flow |
| `cleanup_search_cache_per_user()` | trigger | DEFINER | Priority-aware eviction (max 10 per user, cold -> warm -> hot) |
| `update_conversation_last_message()` | trigger | -- | Updates `conversations.last_message_at` on new message |
| `update_pipeline_updated_at()` | trigger | -- | `pipeline_items.updated_at` trigger |
| `update_alert_preferences_updated_at()` | trigger | -- | `alert_preferences.updated_at` trigger |
| `update_alerts_updated_at()` | trigger | -- | `alerts.updated_at` trigger |
| `create_default_alert_preferences()` | trigger | -- | Auto-creates `alert_preferences` row on new profile |
| `get_conversations_with_unread_count(uuid, bool, text, int, int)` | TABLE | DEFINER | Optimized conversations query with LEFT JOIN LATERAL for unread count |

### Trigger Inventory

| Trigger | Table | Event | Function |
|---------|-------|-------|----------|
| `on_auth_user_created` | `auth.users` | AFTER INSERT | `handle_new_user()` |
| `profiles_updated_at` | `profiles` | BEFORE UPDATE | `set_updated_at()` |
| `plans_updated_at` | `plans` | BEFORE UPDATE | `set_updated_at()` |
| `plan_features_updated_at` | `plan_features` | BEFORE UPDATE | `set_updated_at()` |
| `user_subscriptions_updated_at` | `user_subscriptions` | BEFORE UPDATE | `set_updated_at()` |
| `trg_plan_billing_periods_updated_at` | `plan_billing_periods` | BEFORE UPDATE | `set_updated_at()` |
| `tr_organizations_updated_at` | `organizations` | BEFORE UPDATE | `set_updated_at()` |
| `trg_update_conversation_last_message` | `messages` | AFTER INSERT | `update_conversation_last_message()` |
| `tr_pipeline_items_updated_at` | `pipeline_items` | BEFORE UPDATE | `update_pipeline_updated_at()` |
| `trigger_alert_preferences_updated_at` | `alert_preferences` | BEFORE UPDATE | `update_alert_preferences_updated_at()` |
| `trigger_alerts_updated_at` | `alerts` | BEFORE UPDATE | `update_alerts_updated_at()` |
| `trigger_create_alert_preferences_on_profile` | `profiles` | AFTER INSERT | `create_default_alert_preferences()` |
| `trg_cleanup_search_cache` | `search_results_cache` | AFTER INSERT | `cleanup_search_cache_per_user()` |

---

## Custom Types

### `alert_frequency` (ENUM)

```sql
CREATE TYPE alert_frequency AS ENUM ('daily', 'twice_weekly', 'weekly', 'off');
```

Used by `alert_preferences.frequency`.

---

## Scheduled Jobs (pg_cron)

| Job Name | Schedule | Action |
|----------|----------|--------|
| `cleanup-audit-events` | `0 4 1 * *` (1st of month, 4am UTC) | DELETE audit_events older than 12 months |
| `cleanup-expired-search-results` | `0 4 * * *` (daily, 4am UTC) | DELETE search_results_store expired > 7 days |
| `cleanup-cold-cache-entries` | `0 5 * * *` (daily, 5am UTC) | DELETE search_results_cache where priority = 'cold' and > 7 days |

---

## Extensions

| Extension | Purpose |
|-----------|---------|
| `pg_trgm` | Trigram index for profiles.email ILIKE search |
| `pg_cron` | Scheduled retention/cleanup jobs |

---

## Migration History

76 total migration files:
- **66 Supabase migrations** in `supabase/migrations/` (001 through 20260309)
- **10 backend migrations** in `backend/migrations/` (002 through 010, now fully bridged via DEBT-002)
- Backend migrations are **redundant** after DEBT-002 bridge migration

Key milestones:
- 001: Initial schema (profiles, plans, subscriptions, sessions)
- 005: Plan tier update (3-tier model)
- 016: Security hardening (RLS fixes, trigram index)
- 029: Single plan model (SmartLic Pro)
- DEBT-001: Database integrity fixes (trigger consolidation, index corrections)
- DEBT-017: Long-term optimization (NOT NULL governance, deprecated column docs, query optimization)
