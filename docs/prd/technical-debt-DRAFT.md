# Technical Debt Assessment - DRAFT

**Projeto:** SmartLic v0.5
**Data:** 2026-02-25
**Autor:** @architect (Archon) - Phase 4 Brownfield Discovery
**Fontes:** system-architecture.md (Phase 1), SCHEMA.md + DB-AUDIT.md (Phase 2), frontend-spec.md (Phase 3)
**Objetivo:** Viabilizar funcionalidades core em producao, aceitando dividas tecnicas controladas

---

## Executive Summary

This assessment consolidates findings from 4 documents produced during Phases 1-3 of the brownfield discovery audit: system architecture (69 backend modules, 29 pages), database schema and audit (42 migrations, 18 tables, 28 DB-specific debts), and frontend specification (100+ components, 28 frontend-specific debts). The total inventory comprises **92 technical debt items** spanning backend, database, and frontend.

The critical finding is that SmartLic's core functionalities are largely operational in production, but **3 database columns are missing from migrations** (added via Supabase Dashboard instead), and **1 code reference to a non-existent table** creates a runtime bug. These 4 items are the only true blockers -- if the Supabase project were recreated from migrations alone (disaster recovery scenario), Stripe billing, trial analytics, and trial stats would break. Additionally, the `handle_new_user()` trigger has regressed through 6 rewrites, potentially causing new user profiles to miss fields like `company` and `sector`.

The recommended action is immediate: fix the 4 blocking items (1 code fix + 1 consolidated migration for 3 missing columns), then address the 15 stability items within the next 2 sprints. The remaining 73 items are registered as accepted debts, organized by area and severity for future prioritization.

---

## Core Functionalities (must work reliably)

| # | Funcionalidade | Status | Blocking Issues |
|---|----------------|--------|-----------------|
| 1 | Busca multi-fonte (PNCP + PCP v2 + ComprasGov) | Operational | None blocking. TD-C02 (dual HTTP client) is maintenance burden, not a blocker. |
| 2 | Classificacao IA (LLM arbiter + zero-match) | Operational | None blocking. LLM fallback = REJECT (zero noise philosophy). |
| 3 | Pipeline de oportunidades (Kanban) | Operational | T1-04 (trial_stats references non-existent table) affects trial value display. |
| 4 | Billing (Stripe + trial) | Partially broken on fresh DB | T1-01, T1-02, T1-03 (missing migration columns). |
| 5 | Auth + Onboarding | Operational | T2-04 (handle_new_user trigger regression) may cause missing profile fields. |
| 6 | Relatorios (Excel + resumo IA) | Operational | None blocking. |
| 7 | Dashboard + Analytics | Partially broken on fresh DB | T1-02 (profiles.trial_expires_at missing migration). |

---

## Tier 1: BLOCKING (Acoes Imediatas)

Items that **prevent core features from functioning**. Must be fixed before any other work.

| ID | Debito | Area | Impacto no Core | Esforco | Acao Requerida |
|----|--------|------|-----------------|---------|----------------|
| T1-01 | `profiles.subscription_status` -- column used in 5+ backend modules but has no migration (DB-AUDIT-003) | Database | Stripe webhook processing silently fails on fresh DB setup. `/me` endpoint returns incomplete data. Billing core (4) broken. | 1 migration | `ALTER TABLE profiles ADD COLUMN IF NOT EXISTS subscription_status TEXT DEFAULT 'trial';` |
| T1-02 | `profiles.trial_expires_at` -- column used in analytics and user routes but has no migration (DB-AUDIT-004) | Database | Analytics endpoint fails on fresh DB. Trial status display broken. Dashboard/Analytics core (7) broken. | 1 migration | `ALTER TABLE profiles ADD COLUMN IF NOT EXISTS trial_expires_at TIMESTAMPTZ;` |
| T1-03 | `user_subscriptions.subscription_status` -- column used in Stripe webhook handler but has no migration (DB-AUDIT-005) | Database | Stripe webhook processing fails on checkout and payment failure events. Billing core (4) broken. | 1 migration | `ALTER TABLE user_subscriptions ADD COLUMN IF NOT EXISTS subscription_status TEXT DEFAULT 'active';` |
| T1-04 | `services/trial_stats.py` references non-existent `user_pipeline` table instead of `pipeline_items` (DB-AUDIT-028) | Backend Code | Runtime error when trial stats endpoint is called. Pipeline core (3) trial value display broken. | 1-line code fix | Change `sb.table("user_pipeline")` to `sb.table("pipeline_items")` in `backend/services/trial_stats.py` line 78. |

**Total effort:** 1 SQL migration (T1-01 through T1-03 combined) + 1 Python code fix (T1-04).
**Estimated time:** 1-2 hours including testing.
**Risk:** Low -- all changes are additive (no data modification, no column drops).

---

## Tier 2: STABILITY (Estabilidade em Producao)

Items that cause **intermittent failures, degraded experience, or security gaps** in production. Fix within next 2 sprints.

| ID | Debito | Area | Risco | Esforco | Acao Requerida |
|----|--------|------|-------|---------|----------------|
| T2-01 | 3 tables still reference `auth.users(id)` instead of `profiles(id)`: `pipeline_items`, `classification_feedback`, `trial_email_log` (DB-AUDIT-001) | Database | Inconsistent cascade behavior. If profile deleted without auth.users deletion, orphaned rows may appear. | 1 migration | Repoint FKs to `profiles(id) ON DELETE CASCADE`. |
| T2-02 | `classification_feedback.user_id` FK has no ON DELETE clause, defaulting to RESTRICT (DB-AUDIT-002) | Database | User deletion blocked by orphaned feedback rows. Unlike all other user-owned tables. | Part of T2-01 | Add `ON DELETE CASCADE` when switching to `profiles(id)`. |
| T2-03 | `search_results_cache.results` JSONB blob growing unbounded -- 50-500 KB per entry, up to 5 MB per user (DB-AUDIT-023, DB-AUDIT-014) | Database | Database size inflation. Slow queries when results included in SELECT. Most likely performance bottleneck at scale. | pg_cron + constraint | Add `CHECK (octet_length(results::text) < 1048576)` + pg_cron cleanup for cold entries > 7 days. |
| T2-04 | `handle_new_user()` trigger regressed -- final version (mig 20260224000000) dropped `company`, `sector`, `whatsapp_consent`, `context_data` fields (DB-AUDIT-006) | Database | New user profiles missing business fields from signup metadata. Onboarding data not persisted at signup. Auth/Onboarding core (5) degraded. | 1 migration | Rewrite trigger with all profile fields. Test signup flow after. |
| T2-05 | `search_state_transitions` INSERT policy not scoped to service_role -- any authenticated user can insert fake transition records (DB-AUDIT-007) | Database | Audit log data integrity compromised. Users can inject arbitrary state transitions. | 1 migration | `DROP POLICY + CREATE POLICY ... FOR INSERT TO service_role WITH CHECK (true)`. |
| T2-06 | `classification_feedback` admin policy uses `auth.role()` function instead of `TO service_role` (DB-AUDIT-009) | Database | Per-row function evaluation overhead. Not a correctness issue but violates modern Supabase convention. | 1 migration | Rewrite with `TO service_role`. |
| T2-07 | `profiles` table missing service_role UPDATE/DELETE policies (DB-AUDIT-010) | Database | Defense-in-depth gap. Backend updates profiles via service_role key which currently bypasses RLS. | 1 migration | Add `FOR ALL TO service_role USING (true) WITH CHECK (true)`. |
| T2-08 | `conversations` and `messages` tables missing service_role policies (DB-AUDIT-011) | Database | Same defense-in-depth gap. Backend accesses messaging tables via service_role. | 1 migration | Add service_role ALL policies to both tables. |
| T2-09 | `search_sessions` missing composite index `(user_id, status, created_at)` (DB-AUDIT-013) | Database | Slower queries for stale session cleanup, analytics, and SIGTERM shutdown. Degrades as sessions grow. | 1 migration | `CREATE INDEX idx_search_sessions_user_status_created ON search_sessions (user_id, status, created_at DESC);` |
| T2-10 | No GIN indexes on `search_sessions.sectors` and `search_sessions.ufs` arrays (DB-AUDIT-024, DB-AUDIT-022) | Database | Analytics queries on "searches per sector/UF" require full table scans. Degrades linearly with session count. | 1 migration | `CREATE INDEX ... USING GIN(sectors); CREATE INDEX ... USING GIN(ufs);` |
| T2-11 | BottomNav drawer overlay lacks focus trap (D-008 from frontend-spec) | Frontend | WCAG 2.4.3 a11y violation. Mobile users can Tab out of the drawer into hidden content. | Small code change | Add focus trap to `BottomNav.tsx` drawer overlay. |
| T2-12 | `trial_email_log` has RLS enabled but no policies (DB-AUDIT-008) | Database | Confusing for developers. Service_role bypasses RLS so functional, but should have explicit policy. | 1 migration | Add explicit service_role policy. |
| T2-13 | Dockerfile uses Python 3.11-slim but pyproject.toml targets Python 3.12 (TD-C01) | Backend | Runtime version mismatch. Subtle compatibility issues with type hints and stdlib features between 3.11 and 3.12. | Low effort | Align Dockerfile to `python:3.12-slim` or update pyproject.toml to target 3.11. |
| T2-14 | Hardcoded User-Agent still says "BidIQ" instead of "SmartLic" (TD-H05) | Backend | Misleading for API providers (PNCP, PCP). Could cause issues if providers use User-Agent for analytics or blocking. | Low effort | Update User-Agent strings in `pncp_client.py`. |
| T2-15 | `synchronous sleep` in `quota.py` -- `time.sleep(0.3)` blocks the async event loop (TD-M06) | Backend | Blocks Gunicorn uvicorn worker event loop for 300ms on every quota save retry. Under load, this degrades request throughput. | 1-line code fix | Replace `time.sleep(0.3)` with `await asyncio.sleep(0.3)`. |

**Total effort:** 1 consolidated SQL migration (T2-01 through T2-12) + 4 small code fixes (T2-11, T2-13, T2-14, T2-15).
**Estimated time:** 1-2 days including testing.
**Risk:** Low to medium (T2-04 requires signup flow testing).

---

## Tier 3: ACCEPTED DEBTS (Registrados, Nao Bloqueantes)

### 3.1 Sistema (from system-architecture.md)

| ID | Debito | Severidade | Categoria |
|----|--------|------------|-----------|
| T3-S01 | Dual HTTP client implementations (sync `requests` + async `httpx`) in `pncp_client.py` -- ~1500 lines of duplicated logic (TD-C02) | Critical | Code duplication |
| T3-S02 | Routes mounted twice (versioned `/v1/` + legacy root) -- doubles route table to ~100+ endpoints (TD-C03) | High | Architecture |
| T3-S03 | In-memory progress tracker (`_active_trackers`) not horizontally scalable -- main blocker for scaling beyond 1 web instance (TD-H01) | High | Scalability |
| T3-S04 | In-memory auth token cache (`_token_cache`) not shared across instances (TD-H02) | High | Scalability |
| T3-S05 | `search_pipeline.py` is god module -- 7 stages with inline helpers create tightly coupled module (TD-H03) | High | Architecture |
| T3-S06 | No backend linting enforcement in CI -- ruff and mypy configured but not run (TD-H04) | High | CI/CD |
| T3-S07 | 3 test files in `backend/` root outside `tests/` directory (TD-H07) | High | Code organization |
| T3-S08 | Excel base64 fallback writes to filesystem -- not scalable, not cleaned on crash (TD-H08) | High | Scalability |
| T3-S09 | 100+ root-level markdown files clutter repository (TD-H09) | High | Code organization |
| T3-S10 | Feature flags in env vars only -- no UI for runtime toggling, requires restart (TD-M01) | Medium | Operations |
| T3-S11 | No pre-commit hooks -- developers can commit non-conforming code (TD-M02) | Medium | DX |
| T3-S12 | Frontend test quarantine growing -- quarantined tests are effectively dead (TD-M03) | Medium | Testing |
| T3-S13 | `dotenv` loaded before `setup_logging` -- env vars read at import time may use stale values (TD-M04) | Medium | Startup |
| T3-S14 | No database connection pooling in Supabase client (TD-M05) | Medium | Performance |
| T3-S15 | Lead prospecting modules (5 files) not integrated -- potentially dead code (TD-M07) | Medium | Dead code |
| T3-S16 | Both `requests` and `httpx` as production dependencies -- should consolidate (TD-M08) | Medium | Dependencies |
| T3-S17 | No request timeout for Stripe webhook handler (TD-M09) | Medium | Reliability |
| T3-S18 | OpenAPI schema drift detection only via snapshots -- no CI contract testing (TD-M10) | Medium | API contracts |
| T3-S19 | Screenshot/image files in git root -- 18+ untracked PNGs (TD-L01) | Low | Code organization |
| T3-S20 | Deprecated `asyncio.get_event_loop().time()` pattern (TD-L02) | Low | Code quality |
| T3-S21 | `format_resumo_html` function unused -- dead code in `llm.py` (TD-L03) | Low | Dead code |
| T3-S22 | `dangerouslySetInnerHTML` for theme script without security comment (TD-L04) | Low | Documentation |
| T3-S23 | Temporary file `routes/search.py.tmp` committed to repository (TD-L05) | Low | Code organization |
| T3-S24 | `pyproject.toml` still references "bidiq-uniformes-backend" branding (TD-L06) | Low | Naming |
| T3-S25 | `unsafe-inline` and `unsafe-eval` in CSP -- weakens Content Security Policy (TD-S01) | Medium | Security |
| T3-S26 | Service role key used for all backend operations -- any backend vulnerability exposes all data (TD-S02) | Low | Security |
| T3-S27 | Google verification code in public HTML (TD-S03) | Low | Security |
| T3-S28 | Railway 1GB memory limit with 2 workers -- duplicated in-memory caches risk OOM (TD-P01) | High | Performance |
| T3-S29 | No CDN for static assets (TD-P02) | Medium | Performance |
| T3-S30 | PNCP page size reduced to 50 requiring 10x more API calls (TD-P03) | Medium | Performance |

### 3.2 Database (from DB-AUDIT.md)

| ID | Debito | Severidade | Categoria |
|----|--------|------------|-----------|
| T3-D01 | Dual migration numbering schemes (sequential + timestamp) (DB-AUDIT-016) | Medium | Convention |
| T3-D02 | Backend migrations directory duplicates Supabase migrations (DB-AUDIT-017) | Medium | Convention |
| T3-D03 | No rollback scripts for any migration (DB-AUDIT-018) | Low | Disaster recovery |
| T3-D04 | Superseded migration 027b still present in directory (DB-AUDIT-019) | Low | Cleanup |
| T3-D05 | Inconsistent trigger naming conventions -- 3 different patterns (DB-AUDIT-020) | Low | Convention |
| T3-D06 | Duplicate `updated_at` functions -- `update_updated_at()` and `update_pipeline_updated_at()` have identical logic (DB-AUDIT-021) | Low | Code duplication |
| T3-D07 | `search_sessions` uses PostgreSQL arrays that break 1NF (DB-AUDIT-022) | Medium | Normalization |
| T3-D08 | Redundant standalone index on `search_results_cache.params_hash` -- justified by queries on hash alone (DB-AUDIT-015) | Low | Index optimization |
| T3-D09 | `plans` table has no index on `is_active` -- negligible at 6-8 rows (DB-AUDIT-012) | Low | Index optimization |
| T3-D10 | `get_conversations_with_unread_count` has correlated subquery per row (DB-AUDIT-025) | Medium | Performance |
| T3-D11 | `search_state_transitions.search_id` has no FK -- intentional for fire-and-forget design (DB-AUDIT-026) | Low | Data integrity |
| T3-D12 | No CHECK constraint on `search_state_transitions.to_state` values (DB-AUDIT-027) | Low | Data integrity |

### 3.3 Frontend/UX (from frontend-spec.md)

| ID | Debito | Severidade | Categoria |
|----|--------|------------|-----------|
| T3-F01 | `EmptyState` component duplicated in 2 directories with different APIs (D-001) | Critical | Component duplication |
| T3-F02 | `LoadingProgress` component duplicated in 2 directories (D-002) | Critical | Component duplication |
| T3-F03 | `SearchForm` has 40+ props -- extreme prop drilling, no context (D-003) | Critical | Architecture |
| T3-F04 | All protected pages fully client-rendered -- no RSC data fetching (D-004) | Critical | Performance |
| T3-F05 | SVG icons duplicated as literal JSX in `Sidebar.tsx` and `BottomNav.tsx` -- ~200 lines (D-005) | High | Code duplication |
| T3-F06 | Mixed icon systems -- `lucide-react` for landing, inline SVGs for app (D-006) | High | Inconsistency |
| T3-F07 | `global-error.tsx` uses inline styles instead of design system tokens (D-007) | High | Design system |
| T3-F08 | `ALL_UFS` array defined independently in 4+ files (D-009) | High | Code duplication |
| T3-F09 | Components split across 4 directories with no clear separation principle (D-010) | High | Architecture |
| T3-F10 | `ThemeProvider` duplicates CSS variables already in `globals.css` -- dual source of truth (D-011) | High | Design system |
| T3-F11 | No state management library -- complex state via hooks + prop drilling + localStorage (D-012) | High | Architecture |
| T3-F12 | `AddToPipelineButton` uses `catch (err: any)` -- suppresses TypeScript safety (D-013) | Medium | Type safety |
| T3-F13 | Portuguese strings hardcoded throughout -- no i18n framework (D-014) | Medium | Localization |
| T3-F14 | `FeedbackButtons` has custom toast instead of using `sonner` (D-015) | Medium | Inconsistency |
| T3-F15 | 404 page missing Portuguese accents (D-016) | Medium | Quality |
| T3-F16 | Shepherd.js uses Tailwind `@apply` with hardcoded classes instead of design tokens (D-017) | Medium | Design system |
| T3-F17 | Only search page has per-page error boundary -- others use root (D-018) | Medium | Error handling |
| T3-F18 | Coverage thresholds (50-55%) below documented target (60%) (D-019) | Medium | Testing |
| T3-F19 | No `dynamic()` imports for heavy libraries (Recharts, @dnd-kit, Shepherd.js) (D-020) | Medium | Bundle size |
| T3-F20 | Most `useEffect` fetch calls lack AbortController (D-021) | Medium | Memory safety |
| T3-F21 | Inconsistent date display -- mixed `date-fns` and `toLocaleDateString` (D-022) | Medium | Inconsistency |
| T3-F22 | Legacy `bidiq-theme` to `smartlic-theme` migration code still present (D-023) | Low | Dead code |
| T3-F23 | `not-found.tsx` missing viewport configuration (D-024) | Low | SSR |
| T3-F24 | Unused `@types/js-yaml` in devDependencies (D-025) | Low | Dependencies |
| T3-F25 | Mixed Tailwind defaults and CSS variable usage in some components (D-026) | Low | Design system |
| T3-F26 | Blog hero uses inline font-family style override (D-027) | Low | Design system |
| T3-F27 | `@types/uuid` in dependencies instead of devDependencies (D-028) | Low | Packaging |
| T3-F28 | Inline SVG icons inconsistently labeled for accessibility (a11y gap) | Medium | Accessibility |
| T3-F29 | Date picker calendar may lack screen reader announcements (a11y gap) | Medium | Accessibility |
| T3-F30 | Dropdown menus lack `role="menu"` (a11y gap) | Medium | Accessibility |
| T3-F31 | Toast notifications may not be announced to screen readers (a11y gap) | Medium | Accessibility |

---

## Dependency Map

### Tier 1 Execution Order

```
T1-01, T1-02, T1-03 ──────────────> Single consolidated migration
                                     (can be combined into one file)
T1-04 ─────────────────────────────> Independent code fix
                                     (can run in parallel with migration)
```

All 4 Tier 1 items are **independent** and can be executed in parallel:
- T1-01 through T1-03 combine into one migration
- T1-04 is a Python code fix

### Tier 1 to Tier 2 Dependencies

```
T1-01 (subscription_status) ───> T2-07 (profiles service_role policies)
                                  Reason: service_role needs to update the new column

T1-03 (user_subscriptions.subscription_status) ───> No dependency

T2-01 (FK standardization) ───> T2-02 (ON DELETE CASCADE)
                                  Reason: T2-02 is part of T2-01

T2-04 (handle_new_user trigger) ───> Independent
                                  Reason: Affects signup flow, can be tested separately

T2-05 through T2-12 ───> Independent of each other
                                  Reason: Each is a separate RLS policy or index
```

### Parallelizable Tier 2 Items

| Group | Items | Can Parallelize |
|-------|-------|-----------------|
| DB Security Policies | T2-05, T2-06, T2-07, T2-08, T2-12 | Yes -- all are independent policy changes |
| DB Indexes | T2-09, T2-10 | Yes -- independent CREATE INDEX statements |
| DB Schema | T2-01/T2-02, T2-03, T2-04 | T2-01/T2-02 independent of T2-03 and T2-04 |
| Backend Code | T2-13, T2-14, T2-15 | Yes -- independent code changes |
| Frontend Code | T2-11 | Independent |

**Recommended consolidation:** All Tier 2 database items (T2-01 through T2-12) can be combined into a single migration for atomic deployment.

---

## Perguntas para Especialistas

### @data-engineer

1. **Missing columns (T1-01 through T1-03):** Can you confirm via `SELECT column_name FROM information_schema.columns WHERE table_name = 'profiles'` that `subscription_status` and `trial_expires_at` already exist in the production database (added via Dashboard)? If so, the migration only needs `ADD COLUMN IF NOT EXISTS` for idempotency.

2. **JSONB results blob (T2-03):** What is the current `avg(octet_length(results::text))` and `max(octet_length(results::text))` in `search_results_cache`? This determines whether the 1 MB constraint will cause immediate issues or is safe to add.

3. **`handle_new_user()` trigger (T2-04):** What is the current version of this function in production? The migrations show 6 rewrites -- we need to know which version is live before deploying the fix.

4. **Array columns (T3-D07):** Are there any current analytics queries that filter by `sectors @> ARRAY['X']` pattern? If so, the GIN indexes (T2-10) should be prioritized.

5. **State transitions cleanup (T3-D11):** How many rows exist in `search_state_transitions` currently? Is there any pg_cron job cleaning old records, or is it growing unbounded?

### @ux-design-expert

1. **Focus trap (T2-11):** Is the BottomNav drawer used frequently enough on mobile to prioritize the a11y fix? What is the mobile traffic percentage?

2. **Component duplication (T3-F01, T3-F02):** Which version of `EmptyState` and `LoadingProgress` should be the canonical one -- the `app/components/` version or the `components/` version? Are there API differences that need reconciliation?

3. **SearchForm props (T3-F03):** What is the recommended state management approach? React Context for search state, or a lightweight library like Zustand? The 40+ props are the primary DX pain point.

4. **Icon system (T3-F05, T3-F06):** Should we standardize on Lucide React for all icons (eliminating inline SVGs), or create a custom icon component library?

5. **Protected pages RSC (T3-F04):** Is there a plan to migrate any protected pages to server component data fetching in the near term? This is the biggest performance improvement opportunity.

---

## Proposed Migration SQL

All Tier 1 + Tier 2 database fixes can be addressed in a single consolidated migration. Reference the full SQL from DB-AUDIT.md Section 11 "Consolidated Migration Proposal":

```sql
-- Migration: 20260225100000_technical_debt_assessment_fixes.sql
-- Fixes: T1-01, T1-02, T1-03, T2-01, T2-02, T2-04, T2-05, T2-06, T2-07, T2-08, T2-09, T2-10, T2-12
-- Author: @architect (Phase 4 Brownfield Discovery)

BEGIN;

-- ================================================================
-- TIER 1: BLOCKING FIXES
-- ================================================================

-- T1-01: Add subscription_status to profiles (used in 5+ modules)
ALTER TABLE public.profiles
    ADD COLUMN IF NOT EXISTS subscription_status TEXT DEFAULT 'trial';

CREATE INDEX IF NOT EXISTS idx_profiles_subscription_status
    ON profiles (subscription_status)
    WHERE subscription_status != 'trial';

COMMENT ON COLUMN profiles.subscription_status IS
    'Subscription lifecycle state. Set by Stripe webhooks. Fix for DB-AUDIT-003.';

-- T1-02: Add trial_expires_at to profiles (used in analytics, user routes)
ALTER TABLE public.profiles
    ADD COLUMN IF NOT EXISTS trial_expires_at TIMESTAMPTZ;

COMMENT ON COLUMN profiles.trial_expires_at IS
    'When the trial period expires. Set during signup. Fix for DB-AUDIT-004.';

-- T1-03: Add subscription_status to user_subscriptions (used in Stripe webhooks)
ALTER TABLE public.user_subscriptions
    ADD COLUMN IF NOT EXISTS subscription_status TEXT DEFAULT 'active';

COMMENT ON COLUMN user_subscriptions.subscription_status IS
    'Subscription lifecycle state from Stripe. Fix for DB-AUDIT-005.';

-- ================================================================
-- TIER 2: STABILITY FIXES
-- ================================================================

-- T2-01 + T2-02: Standardize FKs to profiles(id) ON DELETE CASCADE
-- pipeline_items
DO $$ BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'pipeline_items_user_id_fkey' AND table_name = 'pipeline_items')
    THEN ALTER TABLE pipeline_items DROP CONSTRAINT pipeline_items_user_id_fkey;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'pipeline_items_user_id_profiles_fkey' AND table_name = 'pipeline_items')
    THEN ALTER TABLE pipeline_items ADD CONSTRAINT pipeline_items_user_id_profiles_fkey
        FOREIGN KEY (user_id) REFERENCES profiles(id) ON DELETE CASCADE;
    END IF;
END $$;

-- classification_feedback (also adds ON DELETE CASCADE -- T2-02)
DO $$ BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'classification_feedback_user_id_fkey' AND table_name = 'classification_feedback')
    THEN ALTER TABLE classification_feedback DROP CONSTRAINT classification_feedback_user_id_fkey;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'classification_feedback_user_id_profiles_fkey' AND table_name = 'classification_feedback')
    THEN ALTER TABLE classification_feedback ADD CONSTRAINT classification_feedback_user_id_profiles_fkey
        FOREIGN KEY (user_id) REFERENCES profiles(id) ON DELETE CASCADE;
    END IF;
END $$;

-- trial_email_log
DO $$ BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'trial_email_log_user_id_fkey' AND table_name = 'trial_email_log')
    THEN ALTER TABLE trial_email_log DROP CONSTRAINT trial_email_log_user_id_fkey;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'trial_email_log_user_id_profiles_fkey' AND table_name = 'trial_email_log')
    THEN ALTER TABLE trial_email_log ADD CONSTRAINT trial_email_log_user_id_profiles_fkey
        FOREIGN KEY (user_id) REFERENCES profiles(id) ON DELETE CASCADE;
    END IF;
END $$;

-- T2-04: Restore handle_new_user() trigger with all profile fields
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
DECLARE
  _phone text;
BEGIN
  -- Normalize phone: strip non-digits, remove country code 55, remove leading 0
  _phone := regexp_replace(COALESCE(NEW.raw_user_meta_data->>'phone_whatsapp', ''), '[^0-9]', '', 'g');
  IF length(_phone) > 11 AND left(_phone, 2) = '55' THEN _phone := substring(_phone from 3); END IF;
  IF left(_phone, 1) = '0' THEN _phone := substring(_phone from 2); END IF;
  IF length(_phone) NOT IN (10, 11) THEN _phone := NULL; END IF;

  INSERT INTO public.profiles (
    id, email, full_name, company, sector,
    phone_whatsapp, whatsapp_consent, plan_type,
    avatar_url, context_data
  )
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'full_name', ''),
    COALESCE(NEW.raw_user_meta_data->>'company', ''),
    COALESCE(NEW.raw_user_meta_data->>'sector', ''),
    _phone,
    COALESCE((NEW.raw_user_meta_data->>'whatsapp_consent')::boolean, FALSE),
    'free_trial',
    NEW.raw_user_meta_data->>'avatar_url',
    '{}'::jsonb
  )
  ON CONFLICT (id) DO NOTHING;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- T2-05: Scope state transitions INSERT to service_role only
DROP POLICY IF EXISTS "Service role can insert transitions" ON search_state_transitions;
CREATE POLICY "Service role can insert transitions" ON search_state_transitions
    FOR INSERT TO service_role WITH CHECK (true);

-- T2-06: Fix classification_feedback admin policy
DROP POLICY IF EXISTS feedback_admin_all ON classification_feedback;
CREATE POLICY feedback_admin_all ON classification_feedback
    FOR ALL TO service_role USING (true) WITH CHECK (true);

-- T2-07: Add profiles service_role ALL policy
DROP POLICY IF EXISTS "profiles_service_all" ON public.profiles;
CREATE POLICY "profiles_service_all" ON public.profiles
    FOR ALL TO service_role USING (true) WITH CHECK (true);

-- T2-08: Add messaging service_role policies
DROP POLICY IF EXISTS "conversations_service_all" ON conversations;
CREATE POLICY "conversations_service_all" ON conversations
    FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "messages_service_all" ON messages;
CREATE POLICY "messages_service_all" ON messages
    FOR ALL TO service_role USING (true) WITH CHECK (true);

-- T2-09: Add composite index for session queries
CREATE INDEX IF NOT EXISTS idx_search_sessions_user_status_created
    ON search_sessions (user_id, status, created_at DESC);

-- T2-10: Add GIN indexes for array analytics queries
CREATE INDEX IF NOT EXISTS idx_search_sessions_sectors
    ON search_sessions USING GIN(sectors);
CREATE INDEX IF NOT EXISTS idx_search_sessions_ufs
    ON search_sessions USING GIN(ufs);

-- T2-12: Add explicit service_role policy on trial_email_log
DROP POLICY IF EXISTS "Service role full access on trial_email_log" ON trial_email_log;
CREATE POLICY "Service role full access on trial_email_log"
    ON trial_email_log FOR ALL TO service_role USING (true) WITH CHECK (true);

COMMIT;
```

**Backend code fix for T1-04** (separate from migration):
```python
# File: backend/services/trial_stats.py, line 78
# Change: sb.table("user_pipeline") -> sb.table("pipeline_items")
```

**Backend code fix for T2-15** (separate from migration):
```python
# File: backend/quota.py
# Change: time.sleep(0.3) -> await asyncio.sleep(0.3)
```

---

## Summary Statistics

| Tier | Count | Effort | Timeline |
|------|-------|--------|----------|
| Tier 1: Blocking | 4 | 1-2 hours | Immediate |
| Tier 2: Stability | 15 | 1-2 days | Next 2 sprints |
| Tier 3: Accepted (System) | 30 | Variable | Backlog |
| Tier 3: Accepted (Database) | 12 | Variable | Backlog |
| Tier 3: Accepted (Frontend) | 31 | Variable | Backlog |
| **Total** | **92** | | |

**Testing required after Tier 1 + 2 deployment:**
1. Run full backend test suite (`pytest`)
2. Run full frontend test suite (`npm test`)
3. Verify Stripe webhook flow (subscribe, cancel, payment failure)
4. Test new user signup flow (verify profile fields populated)
5. Test trial stats endpoint (verify pipeline_items query works)
6. Test search flow end-to-end (verify session creation with new indexes)

---

*Generated by @architect (Archon) during Phase 4 of SmartLic Brownfield Discovery.*
*Cross-references: system-architecture.md (Phase 1), SCHEMA.md + DB-AUDIT.md (Phase 2), frontend-spec.md (Phase 3).*
