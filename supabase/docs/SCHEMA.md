# SmartLic Database Schema

**Date:** 2026-03-10 | **Supabase Project:** fqqyovlzdzimiwfofdjk | **PostgreSQL:** 17
**Migrations:** 86 (supabase/) + 10 (backend/, fully bridged via debt002)

---

## Tables Overview

| # | Table | Purpose | RLS | FK to profiles | Key Indexes |
|---|-------|---------|-----|----------------|-------------|
| 1 | `profiles` | User profile (extends auth.users) | Y | PK=auth.users(id) | subscription_status, context_porte, phone_unique |
| 2 | `plans` | Plan catalog (seed data) | Y | - | PK(id) |
| 3 | `plan_billing_periods` | Multi-period pricing per plan | Y | - | UNIQUE(plan_id, billing_period) |
| 4 | `plan_features` | Feature flags per plan+period | Y | - | idx_plan_features_lookup |
| 5 | `user_subscriptions` | Active/historical subscriptions | Y | user_id CASCADE | idx_active, idx_billing, idx_first_failed_at |
| 6 | `monthly_quota` | Monthly search usage counter | Y | user_id CASCADE | UNIQUE(user_id, month_year) |
| 7 | `search_sessions` | Search history per user | Y | user_id CASCADE | idx_created, idx_status, idx_inflight, idx_composite |
| 8 | `search_state_transitions` | State machine audit trail | Y | - (app-layer) | idx_search_id, idx_to_state |
| 9 | `search_results_cache` | L2 persistent cache (SWR) | Y | user_id CASCADE | UNIQUE(user_id, params_hash), idx_priority, idx_global_hash, idx_degraded |
| 10 | `search_results_store` | L3 persistent results store | Y | user_id (profiles via FK std) | idx_user, idx_expires, idx_user_expires |
| 11 | `pipeline_items` | Kanban pipeline opportunities | Y | user_id CASCADE | UNIQUE(user_id, pncp_id), idx_user_stage, idx_encerramento, idx_search_id |
| 12 | `conversations` | Support messaging threads | Y | user_id CASCADE | idx_user_id, idx_status, idx_last_message, idx_status_last_msg, idx_unanswered |
| 13 | `messages` | Individual messages in threads | Y | sender_id CASCADE | idx_conversation, idx_unread_by_user, idx_unread_by_admin |
| 14 | `classification_feedback` | User feedback on AI classification | Y | user_id CASCADE (profiles) | UNIQUE(user_id, search_id, bid_id), idx_sector_verdict, idx_user_created |
| 15 | `alerts` | User-defined email alerts | Y | user_id CASCADE | idx_user_id, idx_active |
| 16 | `alert_sent_items` | Dedup tracking for alert emails | Y | alert_id CASCADE | UNIQUE(alert_id, item_id), idx_sent_at |
| 17 | `alert_runs` | Alert execution history | Y | alert_id CASCADE | idx_alert_id, idx_run_at |
| 18 | `alert_preferences` | Email digest settings per user | Y | user_id CASCADE | UNIQUE(user_id), idx_digest_due |
| 19 | `stripe_webhook_events` | Stripe idempotency store | Y | - | idx_type, idx_recent, CHECK(id ~ '^evt_') |
| 20 | `audit_events` | Security audit trail (LGPD) | Y | - | idx_event_type, idx_timestamp, idx_actor, idx_type_timestamp |
| 21 | `user_oauth_tokens` | Google OAuth tokens (AES-256 encrypted) | Y | user_id CASCADE (profiles) | UNIQUE(user_id, provider), idx_expires_at |
| 22 | `google_sheets_exports` | Google Sheets export history | Y | user_id CASCADE (profiles) | idx_user_id, idx_created_at, idx_spreadsheet_id, GIN(search_params) |
| 23 | `trial_email_log` | Trial email sequence tracking | Y | user_id CASCADE | UNIQUE(user_id, email_number), idx_resend_id |
| 24 | `organizations` | Multi-user consultoria accounts | Y | owner_id RESTRICT (auth.users via std) | idx_owner |
| 25 | `organization_members` | Org membership with roles | Y | user_id CASCADE (auth.users) | UNIQUE(org_id, user_id), idx_org, idx_user |
| 26 | `partners` | Revenue share partner registry | Y | - | UNIQUE(slug), idx_slug |
| 27 | `partner_referrals` | Partner referral tracking | Y | partner_id CASCADE, referred_user_id SET NULL | UNIQUE(partner_id, referred_user_id) |
| 28 | `reconciliation_log` | Stripe <> DB sync audit | Y | - | idx_run_at |
| 29 | `health_checks` | Periodic health check results | Y | - | idx_checked_at |
| 30 | `incidents` | System incident status page | Y | - | idx_status, idx_started_at |
| 31 | `mfa_recovery_codes` | TOTP MFA backup codes (bcrypt) | Y | user_id CASCADE (auth.users) | idx_user_id, idx_used_at |
| 32 | `mfa_recovery_attempts` | Brute force tracking for MFA | Y | user_id CASCADE (auth.users) | idx_user_id_time |

---

## Detailed Schema

### 1. profiles

Extends `auth.users`. Auto-created via `handle_new_user()` trigger on signup.

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | uuid | N | - | PK, FK auth.users(id) ON DELETE CASCADE |
| email | text | N | - | - |
| full_name | text | Y | '' | - |
| company | text | Y | '' | - |
| sector | text | Y | '' | Added by migration 007 |
| phone_whatsapp | text | Y | NULL | Partial unique index (non-null, non-empty) |
| whatsapp_consent | boolean | Y | FALSE | Added by migration 007 |
| plan_type | text | N | 'free_trial' | CHECK IN (free_trial, consultor_agil, maquina, sala_guerra, master, smartlic_pro, consultoria) |
| is_admin | boolean | Y | FALSE | Added by migration 004 |
| is_master | boolean | Y | FALSE | Added by migration 004 |
| avatar_url | text | Y | NULL | - |
| subscription_status | text | Y | 'trial' | CHECK IN (trial, active, canceling, past_due, expired) |
| trial_expires_at | timestamptz | Y | NULL | Set on signup: created_at + 14 days |
| subscription_end_date | timestamptz | Y | NULL | When canceled subscription ends |
| email_unsubscribed | boolean | Y | FALSE | LGPD compliance opt-out |
| email_unsubscribed_at | timestamptz | Y | NULL | - |
| marketing_emails_enabled | boolean | N | TRUE | STORY-310 unsubscribe |
| context_data | jsonb | Y | '{}' | Onboarding wizard data |
| referred_by_partner_id | uuid | Y | NULL | FK partners(id) |
| created_at | timestamptz | N | now() | - |
| updated_at | timestamptz | N | now() | Auto-updated via trigger |

**RLS Policies:**
- `profiles_select_own` — SELECT where auth.uid() = id
- `profiles_update_own` — UPDATE where auth.uid() = id
- `profiles_service_all` — ALL for service_role

**Triggers:**
- `on_auth_user_created` — AFTER INSERT on auth.users -> handle_new_user()
- `trigger_create_alert_preferences_on_profile` — AFTER INSERT -> create default alert_preferences
- `profiles_updated_at` — BEFORE UPDATE -> set_updated_at()

---

### 2. plans

Catalog of subscription plans. Seeded with default data.

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | text | N | - | PK |
| name | text | N | - | - |
| description | text | Y | NULL | - |
| max_searches | int | Y | NULL | NULL = unlimited |
| price_brl | numeric(10,2) | N | 0 | - |
| duration_days | int | Y | NULL | NULL = perpetual |
| stripe_price_id | text | Y | NULL | DEPRECATED — use plan_billing_periods |
| stripe_price_id_monthly | text | Y | NULL | - |
| stripe_price_id_semiannual | text | Y | NULL | - |
| stripe_price_id_annual | text | Y | NULL | - |
| is_active | boolean | N | true | - |
| created_at | timestamptz | N | now() | - |
| updated_at | timestamptz | Y | now() | Auto-updated via trigger |

**Active Plans:** `smartlic_pro` (R$397/mo), `consultoria` (R$997/mo), `master`, `free`, `free_trial`
**Legacy (inactive):** `consultor_agil`, `maquina`, `sala_guerra`, `pack_5/10/20`, `monthly`, `annual`

**RLS:** `plans_select_all` — SELECT true (public catalog)

---

### 3. plan_billing_periods

Multi-period pricing per plan. Source of truth for Stripe checkout.

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | uuid | N | gen_random_uuid() | PK |
| plan_id | text | N | - | FK plans(id) ON DELETE CASCADE |
| billing_period | text | N | - | CHECK IN (monthly, semiannual, annual) |
| price_cents | int | N | - | - |
| discount_percent | int | Y | 0 | - |
| stripe_price_id | text | Y | NULL | Stripe Price ID |
| created_at | timestamptz | Y | now() | - |
| updated_at | timestamptz | Y | now() | Auto-updated via trigger |

UNIQUE(plan_id, billing_period)

**Current Data:**
- smartlic_pro: monthly=39700, semiannual=35700 (10%), annual=29700 (25%)
- consultoria: monthly=99700, semiannual=89700 (10%), annual=79700 (20%)

**RLS:** Public read for authenticated+anon, service_role ALL

---

### 4. plan_features

Feature flags per plan and billing period.

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | serial | N | - | PK |
| plan_id | text | N | - | FK plans(id) ON DELETE CASCADE |
| billing_period | varchar(10) | N | - | CHECK IN (monthly, semiannual, annual) |
| feature_key | varchar(100) | N | - | - |
| enabled | boolean | N | true | - |
| metadata | jsonb | Y | '{}' | - |
| created_at | timestamptz | N | now() | - |
| updated_at | timestamptz | N | now() | Auto-updated via trigger |

UNIQUE(plan_id, billing_period, feature_key)

**RLS:** `plan_features_select_all` — SELECT true (public catalog)

---

### 5. user_subscriptions

Active and historical subscriptions per user.

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | uuid | N | gen_random_uuid() | PK |
| user_id | uuid | N | - | FK profiles(id) ON DELETE CASCADE |
| plan_id | text | N | - | FK plans(id) |
| credits_remaining | int | Y | NULL | NULL = unlimited |
| starts_at | timestamptz | N | now() | - |
| expires_at | timestamptz | Y | NULL | NULL = never expires |
| stripe_subscription_id | text | Y | NULL | - |
| stripe_customer_id | text | Y | NULL | - |
| is_active | boolean | N | true | - |
| billing_period | varchar(10) | N | 'monthly' | CHECK IN (monthly, semiannual, annual) |
| annual_benefits | jsonb | N | '{}' | - |
| subscription_status | text | Y | 'active' | CHECK IN (active, trialing, past_due, canceled, expired) |
| first_failed_at | timestamptz | Y | NULL | Dunning tracking |
| created_at | timestamptz | N | now() | - |
| updated_at | timestamptz | N | now() | Auto-updated via trigger |

**Indexes:**
- `idx_user_subscriptions_user` ON (user_id)
- `idx_user_subscriptions_active` ON (user_id, is_active) WHERE is_active = true
- `idx_user_subscriptions_billing` ON (user_id, billing_period, is_active) WHERE is_active = true
- `idx_user_subscriptions_first_failed_at` ON (first_failed_at) WHERE NOT NULL

**RLS:** `subscriptions_select_own` — SELECT where auth.uid() = user_id

---

### 6. monthly_quota

Monthly search usage tracking per user. Atomic increment via RPC functions.

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | uuid | N | gen_random_uuid() | PK |
| user_id | uuid | N | - | FK profiles(id) ON DELETE CASCADE |
| month_year | varchar(7) | N | - | Format: "2026-02" |
| searches_count | int | N | 0 | - |
| created_at | timestamptz | N | now() | - |
| updated_at | timestamptz | N | now() | - |

UNIQUE(user_id, month_year)

**RPC Functions:**
- `check_and_increment_quota(p_user_id, p_month_year, p_max_quota)` — Primary path
- `increment_quota_atomic(p_user_id, p_month_year, p_max_quota)` — Fallback path

**RLS:** Users SELECT own, service_role ALL

---

### 7. search_sessions

Search history with full lifecycle tracking.

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | uuid | N | gen_random_uuid() | PK |
| user_id | uuid | N | - | FK profiles(id) ON DELETE CASCADE |
| search_id | text | Y | NULL | Links to SSE progress |
| sectors | text[] | N | - | Sorted array |
| ufs | text[] | N | - | Sorted array |
| data_inicial | date | N | - | - |
| data_final | date | N | - | - |
| custom_keywords | text[] | Y | NULL | - |
| total_raw | int | N | 0 | - |
| total_filtered | int | N | 0 | - |
| valor_total | numeric(14,2) | Y | 0 | - |
| resumo_executivo | text | Y | NULL | LLM-generated summary |
| destaques | text[] | Y | NULL | - |
| excel_storage_path | text | Y | NULL | - |
| status | text | N | 'created' | CHECK IN (created, processing, completed, failed, timed_out, cancelled) |
| error_message | text | Y | NULL | - |
| error_code | text | Y | NULL | - |
| started_at | timestamptz | N | now() | - |
| completed_at | timestamptz | Y | NULL | - |
| duration_ms | int | Y | NULL | - |
| pipeline_stage | text | Y | NULL | - |
| raw_count | int | Y | 0 | - |
| response_state | text | Y | NULL | live, cached, degraded, empty_failure |
| failed_ufs | text[] | Y | NULL | - |
| created_at | timestamptz | N | now() | - |

**Indexes:** idx_search_sessions_created (user_id, created_at DESC), idx_status, idx_inflight, idx_search_sessions_user_id, idx_composite (created by 20260225140000)

**Retention:** 12 months via pg_cron (cleanup-old-search-sessions, 4:30 UTC daily)

**RLS:** Users SELECT+INSERT own, service_role ALL

---

### 8. search_state_transitions

Audit trail for search state machine. Fire-and-forget inserts.

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | uuid | N | gen_random_uuid() | PK |
| search_id | uuid | N | - | No FK (app-layer integrity) |
| from_state | text | Y | NULL | NULL for initial CREATED |
| to_state | text | N | - | - |
| stage | text | Y | NULL | Pipeline stage |
| details | jsonb | Y | '{}' | - |
| duration_since_previous_ms | int | Y | NULL | - |
| created_at | timestamptz | N | now() | - |

**RLS:** Users SELECT own (via join to search_sessions), service_role INSERT

---

### 9. search_results_cache

L2 persistent cache (SWR pattern). Max 5 entries per user.

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | uuid | N | gen_random_uuid() | PK |
| user_id | uuid | N | - | FK profiles(id) ON DELETE CASCADE |
| params_hash | text | N | - | - |
| search_params | jsonb | N | - | - |
| results | jsonb | N | - | CHECK octet_length <= 2MB |
| total_results | int | N | 0 | - |
| priority | text | Y | NULL | CHECK IN (hot, warm, cold) |
| sources | jsonb | Y | NULL | - |
| fetched_at | timestamptz | Y | NULL | - |
| params_hash_global | text | Y | NULL | For cross-user dedup |
| degraded_until | timestamptz | Y | NULL | - |
| created_at | timestamptz | N | now() | - |

UNIQUE(user_id, params_hash)

**Cleanup Trigger:** `trg_cleanup_search_cache` — AFTER INSERT deletes oldest beyond 5 per user (short-circuit if <=5)

**Indexes:** idx_search_cache_user, idx_search_cache_params_hash, idx_search_cache_priority, idx_search_cache_global_hash, idx_search_cache_degraded (partial)

**Retention:** Cold entries > 7 days via pg_cron (cleanup-cold-cache-entries, 5:00 UTC daily)

**RLS:** Users SELECT own. **WARNING:** service_role policy uses `USING(true)` without `TO service_role` — any authenticated user bypasses RLS. See DB-AUDIT.md H-004.

---

### 10. search_results_store

L3 persistent results store. Prevents "Busca nao encontrada" after L1/L2 TTL expiry.

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| search_id | uuid | N | - | PK |
| user_id | uuid | N | - | FK profiles(id) (standardized) |
| results | jsonb | N | - | CHECK octet_length < 2MB |
| sector | text | Y | NULL | - |
| ufs | text[] | Y | NULL | - |
| total_filtered | int | Y | 0 | - |
| created_at | timestamptz | Y | now() | - |
| expires_at | timestamptz | Y | now() + 24h | - |

**Retention:** Expired results cleaned daily by pg_cron (4:00 UTC)

**RLS:** Users SELECT own, service_role ALL

---

### 11. pipeline_items

Kanban pipeline for tracking procurement opportunities through stages.

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | uuid | N | gen_random_uuid() | PK |
| user_id | uuid | N | - | FK (standardized to profiles) |
| pncp_id | text | N | - | - |
| objeto | text | N | - | - |
| orgao | text | Y | NULL | - |
| uf | text | Y | NULL | - |
| valor_estimado | numeric | Y | NULL | - |
| data_encerramento | timestamptz | Y | NULL | - |
| link_pncp | text | Y | NULL | - |
| stage | text | N | 'descoberta' | CHECK IN (descoberta, analise, preparando, enviada, resultado) |
| notes | text | Y | NULL | - |
| search_id | text | Y | NULL | DEBT-120: search-to-pipeline traceability |
| created_at | timestamptz | N | now() | - |
| updated_at | timestamptz | N | now() | Auto-updated via trigger |

UNIQUE(user_id, pncp_id)

**RLS:** Users full CRUD on own. **WARNING:** service_role policy uses `USING(true)` without `TO service_role` — any authenticated user bypasses RLS. See DB-AUDIT.md H-003.

---

### 12. conversations

Support messaging threads between users and admin.

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | uuid | N | gen_random_uuid() | PK |
| user_id | uuid | N | - | FK profiles(id) ON DELETE CASCADE |
| subject | text | N | - | CHECK char_length <= 200 |
| category | text | N | - | CHECK IN (suporte, sugestao, funcionalidade, bug, outro) |
| status | text | N | 'aberto' | CHECK IN (aberto, respondido, resolvido) |
| last_message_at | timestamptz | N | now() | Auto-updated via trigger on message insert |
| first_response_at | timestamptz | Y | NULL | SLA tracking |
| created_at | timestamptz | N | now() | - |
| updated_at | timestamptz | N | now() | - |

**Retention:** 24 months via pg_cron

**RLS:** Users SELECT own + admin can see all, users INSERT own, admin UPDATE, service_role ALL

---

### 13. messages

Individual messages within a conversation thread.

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | uuid | N | gen_random_uuid() | PK |
| conversation_id | uuid | N | - | FK conversations(id) ON DELETE CASCADE |
| sender_id | uuid | N | - | FK profiles(id) ON DELETE CASCADE |
| body | text | N | - | CHECK char_length BETWEEN 1 AND 5000 |
| is_admin_reply | boolean | N | false | - |
| read_by_user | boolean | N | false | - |
| read_by_admin | boolean | N | false | - |
| created_at | timestamptz | N | now() | - |

**Trigger:** `trg_update_conversation_last_message` — Updates conversation.last_message_at on INSERT

**RLS:** SELECT/INSERT/UPDATE via join to conversations (user_id check + admin check), service_role ALL

---

### 14. classification_feedback

User verdicts on AI classification results for feedback loop.

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | uuid | N | gen_random_uuid() | PK |
| user_id | uuid | N | - | FK profiles(id) ON DELETE CASCADE |
| search_id | uuid | N | - | - |
| bid_id | text | N | - | - |
| setor_id | text | N | - | - |
| user_verdict | text | N | - | CHECK IN (false_positive, false_negative, correct) |
| reason | text | Y | NULL | - |
| category | text | Y | NULL | CHECK IN (wrong_sector, irrelevant_modality, too_small, too_large, closed, other) |
| bid_objeto | text | Y | NULL | - |
| bid_valor | decimal | Y | NULL | - |
| bid_uf | text | Y | NULL | - |
| confidence_score | int | Y | NULL | - |
| relevance_source | text | Y | NULL | - |
| created_at | timestamptz | Y | now() | - |

UNIQUE(user_id, search_id, bid_id)

**Retention:** 24 months via pg_cron

**RLS:** Users INSERT/SELECT/UPDATE/DELETE own, service_role ALL

---

### 15-17. Alert System (alerts, alert_sent_items, alert_runs)

**alerts** — User-defined saved searches for email notifications.

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| id | uuid | N | gen_random_uuid() |
| user_id | uuid | N | FK profiles(id) CASCADE |
| name | text | N | '' |
| filters | jsonb | N | '{}' |
| active | boolean | N | true |
| created_at/updated_at | timestamptz | N | now() |

**alert_sent_items** — Dedup tracking. UNIQUE(alert_id, item_id). FK alerts(id) CASCADE.

**alert_runs** — Execution history. FK alerts(id) CASCADE. Status CHECK IN (pending, running, completed, failed, matched, no_results, no_match, all_deduped, error).

---

### 18. alert_preferences

Per-user email digest settings. Auto-created on profile insert.

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| id | uuid | N | gen_random_uuid() |
| user_id | uuid | N | FK profiles(id) CASCADE, UNIQUE |
| frequency | alert_frequency (enum) | N | 'daily' |
| enabled | boolean | N | true |
| last_digest_sent_at | timestamptz | Y | NULL |
| created_at/updated_at | timestamptz | N | now() |

**Enum:** `alert_frequency` = (daily, twice_weekly, weekly, off)

---

### 19. stripe_webhook_events

Idempotency store for Stripe webhooks.

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| id | varchar(255) | N | - | PK, CHECK(id ~ '^evt_') |
| type | varchar(100) | N | - |
| processed_at | timestamptz | N | now() |
| payload | jsonb | Y | NULL |

**RLS:** service_role INSERT (bypasses RLS), admin SELECT (plan_type='master')

---

### 20. audit_events

Security audit trail with LGPD/GDPR compliant hashing.

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| id | uuid | N | gen_random_uuid() |
| timestamp | timestamptz | N | now() |
| event_type | text | N | - |
| actor_id_hash | text | Y | NULL | SHA-256 truncated to 16 hex |
| target_id_hash | text | Y | NULL | SHA-256 truncated to 16 hex |
| details | jsonb | Y | NULL |
| ip_hash | text | Y | NULL | SHA-256 truncated to 16 hex |

**Retention:** 12 months via pg_cron (1st of month, 4:00 UTC)

**RLS:** service_role ALL, admin SELECT (is_admin=true)

---

### 21-22. OAuth & Google Sheets

**user_oauth_tokens** — AES-256 encrypted OAuth tokens. UNIQUE(user_id, provider). Provider CHECK IN (google, microsoft, dropbox).

**google_sheets_exports** — Export history with JSONB search_params snapshot. GIN index on search_params.

---

### 23. trial_email_log

Trial email sequence tracking (8 emails over 14 days). service_role only.

| Column | Type | Nullable | Default |
|--------|------|----------|---------|
| id | uuid | N | gen_random_uuid() |
| user_id | uuid | N | FK auth.users(id) CASCADE |
| email_type | text | N | - |
| email_number | int | Y | NULL |
| sent_at | timestamptz | N | now() |
| opened_at | timestamptz | Y | NULL | Resend webhook |
| clicked_at | timestamptz | Y | NULL | Resend webhook |
| resend_email_id | text | Y | NULL | - |

UNIQUE(user_id, email_number)

---

### 24-25. Organizations

**organizations** — Multi-user accounts for consultoria. owner_id FK auth.users(id) ON DELETE RESTRICT.

**organization_members** — Members with roles (owner/admin/member). UNIQUE(org_id, user_id).

---

### 26-27. Partners

**partners** — Revenue share partner registry. UNIQUE(slug). Status CHECK IN (active, inactive, pending).

**partner_referrals** — Referral tracking. referred_user_id nullable (ON DELETE SET NULL). UNIQUE(partner_id, referred_user_id).

---

### 28-30. Operations Tables

**reconciliation_log** — Stripe<>DB sync audit. Admin-only.

**health_checks** — Periodic health results. 30-day retention.

**incidents** — System status page. Status CHECK IN (ongoing, resolved).

---

### 31-32. MFA

**mfa_recovery_codes** — bcrypt-hashed recovery codes. service_role write, users SELECT own.

**mfa_recovery_attempts** — Brute force tracking. service_role only.

---

## Relationships (ERD)

```
auth.users ──1:1──> profiles
                       |
         ┌─────────────┼──────────────────────────────────────┐
         │             │                                      │
    user_subscriptions search_sessions    pipeline_items     conversations
         │                 │                   │                  │
    monthly_quota    search_state_      search_results_     messages
                     transitions         store/cache
         │
    plan_billing_periods ──> plans ──> plan_features

profiles ──> alert_preferences
profiles ──> alerts ──> alert_sent_items
                   ──> alert_runs

profiles ──> classification_feedback
profiles ──> user_oauth_tokens
profiles ──> google_sheets_exports

organizations ──> organization_members
partners ──> partner_referrals
profiles.referred_by_partner_id ──> partners
```

---

## Functions & Triggers

### Functions

| Function | Type | Purpose |
|----------|------|---------|
| `handle_new_user()` | SECURITY DEFINER | Auto-create profile on auth.users INSERT (10 fields + phone normalization) |
| `set_updated_at()` | TRIGGER | Canonical updated_at function (consolidated from duplicates) |
| `cleanup_search_cache_per_user()` | SECURITY DEFINER | Enforce max 5 cache entries per user (short-circuit if <=5) |
| `update_conversation_last_message()` | TRIGGER | Update conversation.last_message_at on message INSERT |
| `create_default_alert_preferences()` | TRIGGER | Auto-create alert_preferences on profile INSERT |
| `check_and_increment_quota()` | RPC | Atomic quota check+increment (primary path) |
| `increment_quota_atomic()` | RPC | Atomic quota increment (fallback path) |
| `get_conversations_with_unread_count()` | SECURITY DEFINER | LEFT JOIN LATERAL query for conversation inbox |
| `pg_total_relation_size_safe()` | SECURITY DEFINER | Safe wrapper for monitoring table sizes |

### Triggers

| Trigger | Table | Event | Function |
|---------|-------|-------|----------|
| `on_auth_user_created` | auth.users | AFTER INSERT | handle_new_user() |
| `profiles_updated_at` | profiles | BEFORE UPDATE | set_updated_at() |
| `user_subscriptions_updated_at` | user_subscriptions | BEFORE UPDATE | set_updated_at() |
| `plans_updated_at` | plans | BEFORE UPDATE | set_updated_at() |
| `plan_features_updated_at` | plan_features | BEFORE UPDATE | set_updated_at() |
| `tr_pipeline_items_updated_at` | pipeline_items | BEFORE UPDATE | set_updated_at() |
| `trigger_alert_preferences_updated_at` | alert_preferences | BEFORE UPDATE | set_updated_at() |
| `trigger_alerts_updated_at` | alerts | BEFORE UPDATE | set_updated_at() |
| `tr_organizations_updated_at` | organizations | BEFORE UPDATE | set_updated_at() |
| `trg_incidents_updated_at` | incidents | BEFORE UPDATE | set_updated_at() |
| `trg_partners_updated_at` | partners | BEFORE UPDATE | set_updated_at() |
| `trg_google_sheets_exports_updated_at` | google_sheets_exports | BEFORE UPDATE | set_updated_at() |
| `trg_plan_billing_periods_updated_at` | plan_billing_periods | BEFORE UPDATE | set_updated_at() |
| `trg_cleanup_search_cache` | search_results_cache | AFTER INSERT | cleanup_search_cache_per_user() |
| `trg_update_conversation_last_message` | messages | AFTER INSERT | update_conversation_last_message() |
| `trigger_create_alert_preferences_on_profile` | profiles | AFTER INSERT | create_default_alert_preferences() |

---

## Enum Types

| Enum | Values |
|------|--------|
| `alert_frequency` | daily, twice_weekly, weekly, off |

---

## pg_cron Jobs (Retention)

| Job Name | Schedule | Target | Retention |
|----------|----------|--------|-----------|
| cleanup-audit-events | 4:00 AM 1st/month | audit_events | 12 months |
| cleanup-old-search-sessions | 4:30 AM daily | search_sessions | 12 months |
| cleanup-expired-search-results | 4:00 AM daily | search_results_store | expires_at + 7 days |
| cleanup-cold-cache-entries | 5:00 AM daily | search_results_cache | 7 days (cold only) |
| cleanup-classification-feedback | 4:45 AM daily | classification_feedback | 24 months |
| cleanup-old-conversations | 4:50 AM daily | conversations | 24 months |
| cleanup-orphan-messages | 4:55 AM daily | messages | 24 months |

---

## System Accounts

| UUID | Email | Plan | Purpose |
|------|-------|------|---------|
| 00000000-...000 | system-cache-warmer@internal.smartlic.tech | master | Background cache warming job |
