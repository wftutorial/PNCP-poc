# SmartLic Database Schema Documentation

**Project:** PNCP-poc (SmartLic)
**Database:** Supabase (PostgreSQL 17)
**Generated:** 2026-04-08
**Auditor:** @data-engineer (Dara) -- Brownfield Discovery Phase 2

---

## Table of Contents

1. [Core Tables](#core-tables)
2. [Subscription & Billing](#subscription--billing)
3. [Search & Analytics](#search--analytics)
4. [Data Lake (PNCP Ingestion)](#data-lake-pncp-ingestion)
5. [Messaging & Support](#messaging--support)
6. [Organizations & Multi-User](#organizations--multi-user)
7. [Monitoring & Audit](#monitoring--audit)
8. [Third-Party Integrations](#third-party-integrations)
9. [Indexes](#indexes)
10. [RLS Policies](#rls-policies)
11. [Functions & RPCs](#functions--rpcs)
12. [Triggers](#triggers)
13. [Enums & Custom Types](#enums--custom-types)

---

## Core Tables

### profiles
**Purpose:** User account metadata (extends Supabase auth.users)
**Primary Key:** `id` (UUID, references auth.users)
**Rows:** ~1,000s

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | UUID | No | Foreign key to auth.users |
| email | TEXT | No | User email |
| full_name | TEXT | Yes | Full name |
| company | TEXT | Yes | Company name |
| sector | TEXT | Yes | Business sector |
| phone_whatsapp | TEXT | Yes | WhatsApp contact |
| whatsapp_consent | BOOLEAN | Yes | LGPD consent for WhatsApp |
| plan_type | TEXT | No | `free_trial` \| `smartlic_pro` \| `master` \| legacy types |
| is_admin | BOOLEAN | Yes | Admin flag |
| avatar_url | TEXT | Yes | Profile picture URL |
| context_data | JSONB | Yes | Onboarding context: ufs_atuacao, faixa_valor_min/max, porte_empresa, etc. |
| timezone | TEXT | Yes | User timezone (e.g., "America/Sao_Paulo") |
| created_at | TIMESTAMPTZ | No | Account creation timestamp |
| updated_at | TIMESTAMPTZ | No | Last profile update |

**Constraints:**
- `plan_type` CHECK: `free_trial` | `consultor_agil` | `maquina` | `sala_guerra` | `smartlic_pro` | `master`
- Unique: `(id)`

**Indexes:**
- `idx_profiles_context_porte`: GIN on `context_data->>'porte_empresa'` (WHERE porte_empresa IS NOT NULL)

---

### plans
**Purpose:** Catalog of available subscription plans
**Primary Key:** `id` (TEXT)
**Rows:** ~6 active

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | TEXT | No | e.g., `smartlic_pro`, `free` |
| name | TEXT | No | User-facing plan name |
| description | TEXT | Yes | Marketing description |
| max_searches | INT | Yes | NULL = unlimited |
| price_brl | NUMERIC(10,2) | No | BRL price (legacy, see plan_billing_periods) |
| duration_days | INT | Yes | Subscription period (NULL = perpetual/master) |
| stripe_price_id | TEXT | Yes | Stripe Price ID (legacy, see plan_billing_periods) |
| stripe_price_id_monthly | TEXT | Yes | Monthly Stripe Price ID |
| stripe_price_id_semiannual | TEXT | Yes | Semiannual Stripe Price ID (10% off) |
| stripe_price_id_annual | TEXT | Yes | Annual Stripe Price ID (20% off) |
| is_active | BOOLEAN | No | Soft-delete flag |
| created_at | TIMESTAMPTZ | No | Creation timestamp |

---

### user_subscriptions
**Purpose:** Track active subscriptions and purchased packs per user
**Primary Key:** `id` (UUID)
**Foreign Keys:** `user_id` -> profiles(id), `plan_id` -> plans(id)
**Rows:** ~10,000s (active subscriptions)

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | UUID | No | Unique subscription instance |
| user_id | UUID | No | References profiles(id) |
| plan_id | TEXT | No | References plans(id) |
| billing_period | VARCHAR(10) | Yes | `monthly` \| `semiannual` \| `annual` |
| credits_remaining | INT | Yes | NULL = unlimited (monthly/annual) |
| starts_at | TIMESTAMPTZ | No | Subscription start date |
| expires_at | TIMESTAMPTZ | Yes | Expiration (NULL = never expires) |
| stripe_subscription_id | TEXT | Yes | Stripe recurring subscription ID |
| stripe_customer_id | TEXT | Yes | Stripe customer ID |
| is_active | BOOLEAN | No | Soft-delete flag |
| created_at | TIMESTAMPTZ | No | Record creation |

**Constraints:**
- `billing_period` CHECK: `monthly` | `semiannual` | `annual`

**Indexes:**
- `idx_user_subscriptions_user`: (user_id)
- `idx_user_subscriptions_active`: (user_id, is_active) WHERE is_active = true

---

### plan_billing_periods
**Purpose:** Multi-period pricing for plans (monthly, semiannual 10% off, annual 20% off)
**Primary Key:** `id` (UUID)
**Foreign Keys:** `plan_id` -> plans(id)
**Rows:** ~10

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | UUID | No | Unique billing period config |
| plan_id | TEXT | No | References plans(id) |
| billing_period | VARCHAR(10) | No | `monthly` \| `semiannual` \| `annual` |
| price_cents | INT | No | Price in cents (BRL) |
| discount_percent | INT | Yes | Discount for this period (0, 10, 20) |
| stripe_price_id | TEXT | Yes | Stripe Price ID for this period |
| created_at | TIMESTAMPTZ | No | Creation timestamp |

**Constraints:**
- `UNIQUE(plan_id, billing_period)`
- `billing_period` CHECK: `monthly` | `semiannual` | `annual`

---

### plan_features
**Purpose:** Feature flags per plan + billing period
**Primary Key:** `id` (SERIAL)
**Foreign Keys:** `plan_id` -> plans(id)
**Rows:** ~20

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | SERIAL | No | Auto-increment |
| plan_id | TEXT | No | References plans(id) |
| billing_period | VARCHAR(10) | No | `monthly` \| `semiannual` \| `annual` |
| feature_key | VARCHAR(100) | No | e.g., `early_access`, `proactive_search`, `ai_analysis` |
| enabled | BOOLEAN | No | Feature is active for this plan+period |
| metadata | JSONB | Yes | Feature-specific configuration |
| created_at | TIMESTAMPTZ | No | Creation timestamp |
| updated_at | TIMESTAMPTZ | No | Last update |

**Constraints:**
- `UNIQUE(plan_id, billing_period, feature_key)`
- `billing_period` CHECK: `monthly` | `semiannual` | `annual`

**Indexes:**
- `idx_plan_features_lookup`: (plan_id, billing_period, enabled) WHERE enabled = true

---

## Subscription & Billing

### monthly_quota
**Purpose:** Track monthly search quota per user for plan-based pricing
**Primary Key:** `id` (UUID)
**Unique:** `(user_id, month_year)`
**Rows:** ~10,000s (one row per user-month)

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | UUID | No | Unique record |
| user_id | UUID | No | References auth.users(id) |
| month_year | VARCHAR(7) | No | Format: "2026-02" |
| searches_count | INT | No | Number of searches this month |
| created_at | TIMESTAMPTZ | No | Creation timestamp |
| updated_at | TIMESTAMPTZ | No | Last update |

**Indexes:**
- `idx_monthly_quota_user_month`: (user_id, month_year)

---

### stripe_webhook_events
**Purpose:** Idempotency log for Stripe webhook processing
**Primary Key:** `id` (VARCHAR(255), Stripe event ID)
**Rows:** ~100,000s (90-day retention)

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | VARCHAR(255) | No | Stripe event ID (evt_xxx) |
| type | VARCHAR(100) | No | Event type (e.g., customer.subscription.updated) |
| processed_at | TIMESTAMPTZ | No | Processing timestamp |
| payload | JSONB | Yes | Full Stripe event object |

**Constraints:**
- `id` REGEX CHECK: `^evt_`

**Indexes:**
- `idx_webhook_events_type`: (type, processed_at)
- `idx_webhook_events_recent`: (processed_at DESC)

---

## Search & Analytics

### search_sessions
**Purpose:** History of user search queries
**Primary Key:** `id` (UUID)
**Foreign Keys:** `user_id` -> profiles(id)
**Rows:** ~100,000s

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | UUID | No | Unique search session |
| user_id | UUID | No | References profiles(id) |
| sectors | TEXT[] | No | Sectors searched (array) |
| ufs | TEXT[] | No | States searched (array) |
| data_inicial | DATE | No | Start date for search |
| data_final | DATE | No | End date for search |
| custom_keywords | TEXT[] | Yes | User-provided keywords |
| total_raw | INT | No | Total raw results found |
| total_filtered | INT | No | Results after filtering |
| valor_total | NUMERIC(14,2) | Yes | Total estimated value |
| resumo_executivo | TEXT | Yes | Executive summary (AI-generated) |
| destaques | TEXT[] | Yes | Key highlights |
| excel_storage_path | TEXT | Yes | Supabase Storage path (future) |
| search_id | UUID | Yes | Search ID for pipeline linking |
| created_at | TIMESTAMPTZ | No | Session creation |

**Indexes:**
- `idx_search_sessions_user`: (user_id)
- `idx_search_sessions_created`: (user_id, created_at DESC)

---

### search_results_cache
**Purpose:** Persistent cache of last 5 search results per user
**Primary Key:** `id` (UUID)
**Unique:** `(user_id, params_hash)`
**Rows:** ~5,000s

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | UUID | No | Unique cache entry |
| user_id | UUID | No | References auth.users(id) |
| params_hash | TEXT | No | Hash of search parameters |
| search_params | JSONB | No | Search parameters snapshot |
| results | JSONB | No | Cached result rows |
| total_results | INT | No | Number of results |
| sources | TEXT[] | Yes | Result sources |
| fetched_at | TIMESTAMPTZ | Yes | When results were fetched |
| created_at | TIMESTAMPTZ | No | Cache entry creation |

**Indexes:**
- `idx_search_cache_user`: (user_id, created_at DESC)
- `idx_search_cache_params_hash`: (params_hash)

---

### search_state_transitions
**Purpose:** Track search state machine transitions for diagnostics
**Primary Key:** `id` (UUID)
**Rows:** ~1,000,000s

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | UUID | No | Unique transition record |
| search_id | UUID | No | References search session |
| from_state | TEXT | No | Previous state |
| to_state | TEXT | No | New state |
| metadata | JSONB | Yes | Transition metadata |
| transitioned_at | TIMESTAMPTZ | No | Timestamp |

---

### pipeline_items
**Purpose:** User's procurement opportunity pipeline (opportunity tracking)
**Primary Key:** `id` (UUID)
**Foreign Keys:** `user_id` -> auth.users(id)
**Unique:** `(user_id, pncp_id)`
**Rows:** ~10,000s

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | UUID | No | Unique pipeline item |
| user_id | UUID | No | References auth.users(id) |
| pncp_id | TEXT | No | Bid ID snapshot |
| objeto | TEXT | No | Procurement object description |
| orgao | TEXT | Yes | Procurement agency name |
| uf | TEXT | Yes | State |
| valor_estimado | NUMERIC | Yes | Estimated value |
| data_encerramento | TIMESTAMPTZ | Yes | Bid deadline |
| link_pncp | TEXT | Yes | Link to PNCP |
| stage | TEXT | No | `descoberta` \| `analise` \| `preparando` \| `enviada` \| `resultado` |
| notes | TEXT | Yes | User notes |
| created_at | TIMESTAMPTZ | No | Creation timestamp |
| updated_at | TIMESTAMPTZ | No | Last update |

**Constraints:**
- `stage` CHECK: `descoberta` | `analise` | `preparando` | `enviada` | `resultado`

**Indexes:**
- `idx_pipeline_user_stage`: (user_id, stage)
- `idx_pipeline_encerramento`: (data_encerramento) WHERE stage NOT IN ('enviada', 'resultado')
- `idx_pipeline_user_created`: (user_id, created_at DESC)

---

## Data Lake (PNCP Ingestion)

### pncp_raw_bids
**Purpose:** Core data lake: raw PNCP bid records (12-day retention)
**Primary Key:** `pncp_id` (TEXT)
**Rows:** ~100,000s (12-day rolling window)

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| pncp_id | TEXT | No | PNCP unique identifier |
| objeto_compra | TEXT | No | Procurement object description |
| valor_total_estimado | NUMERIC(18,2) | Yes | Estimated total value |
| modalidade_id | INT | No | Procurement modality code |
| modalidade_nome | TEXT | Yes | Modality name |
| situacao_compra | TEXT | Yes | Purchase situation/status |
| esfera_id | TEXT | Yes | Government sphere (federal/state/municipal) |
| uf | TEXT | No | State (2-letter code) |
| municipio | TEXT | Yes | Municipality name |
| codigo_municipio_ibge | TEXT | Yes | IBGE municipality code |
| orgao_razao_social | TEXT | Yes | Agency legal name |
| orgao_cnpj | TEXT | Yes | Agency CNPJ |
| unidade_nome | TEXT | Yes | Unit name |
| data_publicacao | TIMESTAMPTZ | Yes | Publication date |
| data_abertura | TIMESTAMPTZ | Yes | Opening date |
| data_encerramento | TIMESTAMPTZ | Yes | Closing date |
| link_sistema_origem | TEXT | Yes | Link to source system |
| link_pncp | TEXT | Yes | PNCP link |
| content_hash | TEXT | No | MD5 of mutable fields (change detection) |
| tsv | TSVECTOR | No | Pre-computed Portuguese tsvector of objeto_compra |
| ingested_at | TIMESTAMPTZ | No | Ingestion timestamp |
| updated_at | TIMESTAMPTZ | No | Last update |
| source | TEXT | No | Source system (default: `pncp`) |
| crawl_batch_id | TEXT | Yes | Ingestion run batch ID |
| is_active | BOOLEAN | No | Soft-delete flag |

**Indexes:**
- `idx_pncp_raw_bids_fts`: GIN (tsv) -- full-text search
- `idx_pncp_raw_bids_uf_date`: (uf, data_publicacao DESC) WHERE is_active
- `idx_pncp_raw_bids_modalidade`: (modalidade_id) WHERE is_active
- `idx_pncp_raw_bids_valor`: (valor_total_estimado) WHERE is_active AND valor_total_estimado IS NOT NULL
- `idx_pncp_raw_bids_esfera`: (esfera_id) WHERE is_active
- `idx_pncp_raw_bids_encerramento`: (data_encerramento) WHERE is_active AND data_encerramento IS NOT NULL
- `idx_pncp_raw_bids_content_hash`: (content_hash)
- `idx_pncp_raw_bids_ingested_at`: (ingested_at DESC)

---

### ingestion_runs
**Purpose:** Top-level ledger for data lake ingestion batches
**Primary Key:** `id` (BIGINT IDENTITY)
**Unique:** `(crawl_batch_id)`
**Rows:** ~100s

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | BIGINT | No | Auto-increment |
| crawl_batch_id | TEXT | No | Batch identifier (unique) |
| run_type | TEXT | No | `full` \| `incremental` |
| status | TEXT | No | `running` \| `completed` \| `failed` \| `partial` |
| started_at | TIMESTAMPTZ | No | Run start time |
| completed_at | TIMESTAMPTZ | Yes | Run completion time |
| total_fetched | INT | No | Total rows fetched from source |
| inserted | INT | No | New rows inserted |
| updated | INT | No | Existing rows updated |
| unchanged | INT | No | Rows skipped (unchanged) |
| errors | INT | No | Rows that failed |
| ufs_completed | TEXT[] | Yes | States that completed |
| ufs_failed | TEXT[] | Yes | States that failed |
| duration_s | NUMERIC(10,1) | Yes | Execution time in seconds |
| metadata | JSONB | No | Worker version, config snapshot, trigger source |

**Constraints:**
- `status` CHECK: `running` | `completed` | `failed` | `partial`
- `run_type` CHECK: `full` | `incremental`

**Indexes:**
- `idx_ingestion_runs_started`: (started_at DESC)
- `idx_ingestion_runs_status`: (status) WHERE status IN ('running', 'failed')

---

### ingestion_checkpoints
**Purpose:** Per-UF/modality progress tracking within a crawl batch
**Primary Key:** `id` (BIGINT IDENTITY)
**Unique:** `(source, uf, modalidade_id, crawl_batch_id)`
**Rows:** ~10,000s

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | BIGINT | No | Auto-increment |
| source | TEXT | No | Source system (default: `pncp`) |
| uf | TEXT | No | State code |
| modalidade_id | INT | No | Modality code |
| last_date | DATE | No | Last date processed |
| last_page | INT | Yes | Last page number (1-indexed) |
| records_fetched | INT | Yes | Records fetched in this checkpoint |
| status | TEXT | No | `pending` \| `running` \| `completed` \| `failed` |
| error_message | TEXT | Yes | Error message if failed |
| started_at | TIMESTAMPTZ | Yes | Start timestamp |
| completed_at | TIMESTAMPTZ | Yes | Completion timestamp |
| crawl_batch_id | TEXT | No | References ingestion_runs.crawl_batch_id |

**Constraints:**
- `status` CHECK: `pending` | `running` | `completed` | `failed`

**Indexes:**
- `idx_ingestion_checkpoints_batch`: (crawl_batch_id, status)
- `idx_ingestion_checkpoints_uf_mod`: (uf, modalidade_id)

---

## Messaging & Support

### conversations
**Purpose:** Support/messaging conversations between users and admins
**Primary Key:** `id` (UUID)
**Foreign Keys:** `user_id` -> profiles(id)
**Rows:** ~10,000s

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | UUID | No | Unique conversation |
| user_id | UUID | No | References profiles(id) |
| subject | TEXT | No | Conversation subject (max 200 chars) |
| category | TEXT | No | `suporte` \| `sugestao` \| `funcionalidade` \| `bug` \| `outro` |
| status | TEXT | No | `aberto` \| `respondido` \| `resolvido` |
| last_message_at | TIMESTAMPTZ | No | Timestamp of latest message |
| created_at | TIMESTAMPTZ | No | Creation timestamp |
| updated_at | TIMESTAMPTZ | No | Last update |

**Constraints:**
- `subject` CHECK: length <= 200
- `category` CHECK: `suporte` | `sugestao` | `funcionalidade` | `bug` | `outro`
- `status` CHECK: `aberto` | `respondido` | `resolvido`

**Indexes:**
- `idx_conversations_user_id`: (user_id)
- `idx_conversations_status`: (status)
- `idx_conversations_last_message`: (last_message_at DESC)

---

### messages
**Purpose:** Individual messages within conversations
**Primary Key:** `id` (UUID)
**Foreign Keys:** `conversation_id` -> conversations(id), `sender_id` -> profiles(id)
**Rows:** ~100,000s

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | UUID | No | Unique message |
| conversation_id | UUID | No | References conversations(id) |
| sender_id | UUID | No | References profiles(id) |
| body | TEXT | No | Message content (1-5000 chars) |
| is_admin_reply | BOOLEAN | No | Message is from admin |
| read_by_user | BOOLEAN | No | User has read this message |
| read_by_admin | BOOLEAN | No | Admin has read this message |
| created_at | TIMESTAMPTZ | No | Message timestamp |

**Constraints:**
- `body` CHECK: length BETWEEN 1 AND 5000

**Indexes:**
- `idx_messages_conversation`: (conversation_id, created_at)
- `idx_messages_unread_by_user`: (conversation_id) WHERE is_admin_reply = true AND read_by_user = false
- `idx_messages_unread_by_admin`: (conversation_id) WHERE is_admin_reply = false AND read_by_admin = false

---

## Organizations & Multi-User

### organizations
**Purpose:** Multi-user organization accounts (consultoria/agency)
**Primary Key:** `id` (UUID)
**Foreign Keys:** `owner_id` -> auth.users(id)
**Rows:** ~100s

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | UUID | No | Unique organization |
| name | TEXT | No | Organization name |
| logo_url | TEXT | Yes | Logo URL |
| owner_id | UUID | No | References auth.users(id) (RESTRICT delete) |
| max_members | INT | No | Member limit (default 5) |
| plan_type | TEXT | No | Organization plan (default: `consultoria`) |
| stripe_customer_id | TEXT | Yes | Stripe customer for org billing |
| created_at | TIMESTAMPTZ | No | Creation timestamp |
| updated_at | TIMESTAMPTZ | No | Last update |

**Indexes:**
- `idx_organizations_owner`: (owner_id)

---

### organization_members
**Purpose:** Organization membership with role-based access
**Primary Key:** `id` (UUID)
**Foreign Keys:** `org_id` -> organizations(id), `user_id` -> auth.users(id)
**Unique:** `(org_id, user_id)`
**Rows:** ~1,000s

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | UUID | No | Unique membership record |
| org_id | UUID | No | References organizations(id) |
| user_id | UUID | No | References auth.users(id) |
| role | TEXT | No | `owner` \| `admin` \| `member` |
| invited_at | TIMESTAMPTZ | No | Invitation timestamp |
| accepted_at | TIMESTAMPTZ | Yes | Acceptance timestamp (NULL = pending) |

**Constraints:**
- `role` CHECK: `owner` | `admin` | `member`

**Indexes:**
- `idx_org_members_org`: (org_id)
- `idx_org_members_user`: (user_id)

---

## Monitoring & Audit

### audit_events
**Purpose:** Security audit log (12-month retention)
**Primary Key:** `id` (UUID)
**Rows:** ~1,000,000s (12-month rolling)

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | UUID | No | Unique audit event |
| timestamp | TIMESTAMPTZ | No | Event timestamp |
| event_type | TEXT | No | Event category (auth.login, billing.checkout, etc.) |
| actor_id_hash | TEXT | Yes | SHA-256 hash of actor user ID (16 hex chars) |
| target_id_hash | TEXT | Yes | SHA-256 hash of target user ID (16 hex chars) |
| details | JSONB | Yes | Structured event metadata (sanitized) |
| ip_hash | TEXT | Yes | SHA-256 hash of client IP (16 hex chars) |

**Indexes:**
- `idx_audit_events_event_type`: (event_type)
- `idx_audit_events_timestamp`: (timestamp)
- `idx_audit_events_actor`: (actor_id_hash) WHERE actor_id_hash IS NOT NULL
- `idx_audit_events_type_timestamp`: (event_type, timestamp DESC)

---

### incidents
**Purpose:** System incident tracking for status page
**Primary Key:** `id` (UUID)
**Rows:** ~10s

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | UUID | No | Unique incident |
| started_at | TIMESTAMPTZ | No | Incident start time |
| resolved_at | TIMESTAMPTZ | Yes | Incident resolution time |
| status | TEXT | No | `ongoing` \| `resolved` |
| affected_sources | TEXT[] | No | Affected components |
| description | TEXT | No | Incident description |

**Constraints:**
- `status` CHECK: `ongoing` | `resolved`

**Indexes:**
- `idx_incidents_status`: (status) WHERE status = 'ongoing'
- `idx_incidents_started_at`: (started_at DESC)

---

### health_checks
**Purpose:** Periodic health check results
**Primary Key:** `id` (UUID)
**Rows:** ~10,000s

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | UUID | No | Unique check result |
| check_name | TEXT | No | Health check name |
| status | TEXT | No | `ok` \| `warning` \| `error` |
| details | JSONB | Yes | Check details |
| checked_at | TIMESTAMPTZ | No | Check timestamp |

---

## Alerts & Notifications

### alerts
**Purpose:** User-defined email alert rules with search filters
**Primary Key:** `id` (UUID)
**Foreign Keys:** `user_id` -> profiles(id)
**Rows:** ~1,000s

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | UUID | No | Unique alert rule |
| user_id | UUID | No | References profiles(id) |
| name | TEXT | No | Alert name |
| filters | JSONB | No | Search filters: {setor, ufs[], valor_min, valor_max, keywords[]} |
| active | BOOLEAN | No | Alert is active |
| created_at | TIMESTAMPTZ | No | Creation timestamp |
| updated_at | TIMESTAMPTZ | No | Last update |

**Indexes:**
- `idx_alerts_user_id`: (user_id)
- `idx_alerts_active`: (user_id, active) WHERE active = true

---

### alert_sent_items
**Purpose:** Dedup tracking for alert sent items
**Primary Key:** `id` (UUID)
**Unique:** `(alert_id, item_id)`
**Rows:** ~100,000s

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | UUID | No | Unique record |
| alert_id | UUID | No | References alerts(id) |
| item_id | TEXT | No | Bid ID sent in this alert |
| sent_at | TIMESTAMPTZ | No | Send timestamp |

**Indexes:**
- `idx_alert_sent_items_dedup`: UNIQUE (alert_id, item_id)
- `idx_alert_sent_items_alert_id`: (alert_id)
- `idx_alert_sent_items_sent_at`: (sent_at)

---

### alert_preferences
**Purpose:** User preferences for alerts (email frequency, quiet hours, etc.)
**Primary Key:** `id` (UUID)
**Foreign Keys:** `user_id` -> profiles(id)
**Unique:** `(user_id)`
**Rows:** ~1,000s

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | UUID | No | Unique preferences record |
| user_id | UUID | No | References profiles(id) |
| email_frequency | TEXT | No | `immediate` \| `daily` \| `weekly` \| `never` |
| quiet_hours_start | INT | Yes | Hour in 24h format (0-23) |
| quiet_hours_end | INT | Yes | Hour in 24h format (0-23) |
| created_at | TIMESTAMPTZ | No | Creation timestamp |
| updated_at | TIMESTAMPTZ | No | Last update |

---

## Viral Growth & Sharing

### shared_analyses
**Purpose:** Shareable public bid analyses (30-day expiration)
**Primary Key:** `id` (UUID)
**Unique:** `(hash)`
**Foreign Keys:** `user_id` -> auth.users(id)
**Rows:** ~10,000s

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | UUID | No | Unique analysis |
| hash | VARCHAR(12) | No | Short shareable hash (unique) |
| user_id | UUID | No | References auth.users(id) |
| bid_id | TEXT | No | PNCP bid ID |
| bid_title | TEXT | No | Bid title snapshot |
| bid_orgao | TEXT | Yes | Bid agency |
| bid_uf | TEXT | Yes | Bid state |
| bid_valor | NUMERIC | Yes | Bid value |
| bid_modalidade | TEXT | Yes | Bid modality |
| viability_score | INT | No | 0-100 score |
| viability_level | TEXT | No | `alta` \| `media` \| `baixa` |
| viability_factors | JSONB | No | Factors determining score |
| view_count | INT | Yes | Public view count |
| created_at | TIMESTAMPTZ | No | Creation timestamp |
| expires_at | TIMESTAMPTZ | No | Expiration timestamp (default +30 days) |

**Constraints:**
- `viability_score` CHECK: BETWEEN 0 AND 100
- `viability_level` CHECK: `alta` | `media` | `baixa`

**Indexes:**
- `idx_shared_analyses_hash`: (hash)
- `idx_shared_analyses_user`: (user_id)
- `idx_shared_analyses_expires`: (expires_at)

---

## SEO & Marketing

### leads
**Purpose:** Email capture (calculadora, CNPJ, alerts signup)
**Primary Key:** `id` (UUID)
**Unique:** `(email, source)`
**Rows:** ~100,000s

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | UUID | No | Unique lead |
| email | TEXT | No | Email address |
| source | TEXT | No | Lead source (calculadora, cnpj, alertas, etc.) |
| setor | TEXT | Yes | Business sector (if provided) |
| uf | TEXT | Yes | State (if provided) |
| captured_at | TIMESTAMPTZ | No | Capture timestamp |

**Indexes:**
- `idx_leads_email_source`: (email, source)

---

### seo_metrics
**Purpose:** Weekly Google Search Console snapshots
**Primary Key:** `id` (BIGINT IDENTITY)
**Unique:** `(date, source)`
**Rows:** ~52 (weekly GSC data)

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | BIGINT | No | Auto-increment |
| date | DATE | No | Metric date |
| source | TEXT | No | Source (default: `gsc`) |
| impressions | INT | No | Google Search impressions |
| clicks | INT | No | Click-through count |
| ctr | NUMERIC(6,4) | No | Click-through rate |
| avg_position | NUMERIC(6,2) | No | Average ranking position |
| pages_indexed | INT | No | Pages indexed in Google |
| top_queries | JSONB | No | Top search queries |
| top_pages | JSONB | No | Top landing pages |
| created_at | TIMESTAMPTZ | No | Record creation |

**Indexes:**
- `idx_seo_metrics_date_desc`: (date DESC)

---

### referrals
**Purpose:** Referral program tracking
**Primary Key:** `id` (UUID)
**Rows:** ~100s

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | UUID | No | Unique referral |
| referrer_id | UUID | Yes | References profiles(id) |
| referred_email | TEXT | Yes | Email of referred person |
| status | TEXT | No | `pending` \| `signed_up` \| `trial_ended` \| `converted` |
| code | TEXT | Yes | Unique referral code |
| created_at | TIMESTAMPTZ | No | Creation timestamp |

---

## Enums & Custom Types

**plan_type (profiles.plan_type, organizations.plan_type):**
- `free_trial` -- Free trial period
- `smartlic_pro` -- Single plan tier (monthly, semiannual, annual)
- `consultor_agil` -- Legacy (deprecated)
- `maquina` -- Legacy (deprecated)
- `sala_guerra` -- Legacy (deprecated)
- `master` -- Admin unlimited access

**billing_period (user_subscriptions, plan_features, plan_billing_periods):**
- `monthly`
- `semiannual` (10% discount)
- `annual` (20% discount)

**pipeline_stage (pipeline_items.stage):**
- `descoberta` -- Discovery
- `analise` -- Analysis
- `preparando` -- Preparing proposal
- `enviada` -- Bid submitted
- `resultado` -- Result (won/lost)

**conversation_status (conversations.status):**
- `aberto` -- Open
- `respondido` -- Replied
- `resolvido` -- Resolved

**conversation_category (conversations.category):**
- `suporte` -- Support
- `sugestao` -- Suggestion
- `funcionalidade` -- Feature request
- `bug` -- Bug report
- `outro` -- Other

**ingestion_status (ingestion_runs.status, ingestion_checkpoints.status):**
- `pending`, `running`, `completed`, `failed`, `partial`

**incident_status (incidents.status):**
- `ongoing`, `resolved`

**organization_role (organization_members.role):**
- `owner` -- Full control
- `admin` -- Manage members
- `member` -- Read-only access

**oauth_provider (user_oauth_tokens.provider):**
- `google`, `microsoft`, `dropbox`
