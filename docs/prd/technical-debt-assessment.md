# Technical Debt Assessment - FINAL

**Projeto:** SmartLic (smartlic.tech)
**Data:** 2026-03-21
**Versao:** 2.0
**Status:** FINAL -- Aprovado pelo QA Gate
**Revisores:** @architect (Atlas), @data-engineer (Delta), @ux-design-expert (Uma), @qa (Quinn)

---

## Executive Summary

| Metric | DRAFT | FINAL | Delta |
|--------|-------|-------|-------|
| **Total debt items** | 54 | 76 | +22 from specialist reviews |
| **Critical** | 3 | 4 | +1 (FE-002 upgraded) |
| **High** | 10 | 14 | +4 (FE-007/008 upgraded, DB-018/FE-017 added) |
| **Medium** | 20 | 25 | +5 net (3 downgraded, 8 added) |
| **Low** | 21 | 27 | +6 net (3 upgraded from low, 9 added) |
| **Info** | 0 | 1 | +1 (QA-DEBT-009) |
| **Design Choice (N/A)** | 1 | 2 | +1 (FE-010 confirmed) |
| **Total estimated effort** | ~297-325h | ~374-402h | +77h from new items + test safety net |
| **Quick wins (< 4h)** | 18 items | 22 items | +4 new quick wins |
| **Wave 0 (safety net)** | N/A | ~24h | New prerequisite per QA |

### Key Risks (updated)

1. **Monolithic file accumulation** -- Four backend files exceed 2,000 LOC (filter.py 3,871, pncp_client.py 2,515, search_cache.py 2,512, schemas.py 2,121). Most-modified files, highest merge conflict risk.
2. **Subscription status drift** -- Dual tracking in profiles vs user_subscriptions with mismatched enums. No sync trigger since migration 030. (DEBT-DB-001)
3. **Accessibility gaps** -- SearchForm zero ARIA (CRITICAL per UX review). Skip-link broken on all protected pages. Login form has no aria-invalid. (DEBT-FE-002, FE-008/022, FE-017)
4. **Account deletion not transactional** -- Multi-table manual deletion without transaction wrapping. Partial failure leaves inconsistent state. (DEBT-DB-018, new from @data-engineer)
5. **Test coverage blind spots** -- cron_jobs.py (2,039 LOC), supabase_client.py (537 LOC with circuit breaker), and 8 filter submodules have ZERO test files. Restructuring without tests is flying blind. (QA-DEBT-001 through QA-DEBT-005, new from @qa)
6. **Dead source consuming budget** -- ComprasGov v3 down since March 2026 but still active in pipeline. (DEBT-SYS-013)

---

## Inventario Completo de Debitos

### Sistema / Arquitetura (validado por @architect)

| # | ID | Debito | Severidade | Horas | Quick Win? | Wave |
|---|-----|--------|-----------|-------|-----------|------|
| 1 | DEBT-SYS-001 | `filter.py` at 3,871 LOC -- core matching logic not fully migrated to 11 submodules | CRITICAL | 8 | No | 3 |
| 2 | DEBT-SYS-002 | `schemas.py` at 2,121 LOC -- all Pydantic models in one file | CRITICAL | 6 | No | 3 |
| 3 | DEBT-SYS-003 | `pncp_client.py` imports sync `requests` alongside async `httpx` -- dual-client pattern | CRITICAL | 4 | Yes | 1 |
| 4 | DEBT-SYS-004 | 69 top-level Python files -- no package grouping | HIGH | 12 | No | 3 |
| 5 | DEBT-SYS-005 | `job_queue.py` (2,152 LOC) + `cron_jobs.py` (2,039 LOC) monoliths | HIGH | 6 | No | 3 |
| 6 | DEBT-SYS-006 | `search_cache.py` at 2,512 LOC -- L1, L2, SWR, serialization in one file | HIGH | 4 | No | 3 |
| 7 | DEBT-SYS-007 | `webhooks/stripe.py` at 1,192 LOC -- 10+ event types in single handler | HIGH | 6 | No | 3 |
| 8 | DEBT-SYS-008 | `api-types.generated.ts` 5,177 LOC bundle impact | **MEDIUM** | 2 | Yes | 1 |
| 9 | DEBT-SYS-009 | `quota.py` at 1,622 LOC -- mixes plan, quota, rate limiting, trial | HIGH | 4 | No | 3 |
| 10 | DEBT-SYS-010 | `main.py` still has 7 endpoints despite startup/ decomposition | MEDIUM | 4 | No | 3 |
| 11 | DEBT-SYS-011 | Test LOC (140K) is 1.8x source LOC (77K) -- uneven distribution | MEDIUM | 8 | No | 4 |
| 12 | DEBT-SYS-012 | 11 filter_*.py + filter.py -- ambiguous ownership, stale docstrings | MEDIUM | 3 | No | 3 |
| 13 | DEBT-SYS-013 | ComprasGov v3 down since Mar 2026 -- client still active | MEDIUM | 2 | Yes | 1 |
| 14 | DEBT-SYS-014 | 40+ feature flags, some permanently enabled/disabled | MEDIUM | 3 | No | 4 |
| 15 | DEBT-SYS-015 | 58 API proxy routes, generic factory underused | **LOW** | 4 | No | 4 |
| 16 | DEBT-SYS-016 | `onboarding/page.tsx` (783 LOC) + `signup/page.tsx` (703 LOC) no decomposition | MEDIUM | 4 | No | 3 |
| 17 | DEBT-SYS-017 | `backend/clients/` -- 5 clients with no shared base class | LOW | 4 | No | 4 |
| 18 | DEBT-SYS-018 | Backend docs/ currency unknown | LOW | 2 | No | 4 |
| 19 | DEBT-SYS-019 | scripts/ utility scripts not in CI test suite | LOW | 2 | No | 4 |
| 20 | DEBT-SYS-020 | startup/ module exists but main.py still does most initialization | LOW | 3 | No | 3 |
| 21 | DEBT-SYS-021 | blog.ts (785 LOC) hardcoded content | N/A | N/A | No | -- |

**Severity changes from DRAFT:** DEBT-SYS-008 HIGH->MEDIUM (per UX: verify tree-shaking before acting), DEBT-SYS-015 MEDIUM->LOW (per UX: zero user impact).

### Database (validado por @data-engineer)

| # | ID | Debito | Severidade | Horas | Quick Win? | Wave |
|---|-----|--------|-----------|-------|-----------|------|
| 1 | DEBT-DB-001 | Dual subscription_status tracking -- profiles vs user_subscriptions, mismatched enums | HIGH | 3 | Yes | 1 |
| 2 | DEBT-DB-002 | classification_feedback FK references auth.users on fresh install | HIGH | 1 | Yes | 1 |
| 3 | DEBT-DB-003 | profiles table 20+ columns (wide table) | **LOW** | 10 | No | 4 |
| 4 | DEBT-DB-004 | pipeline_items.search_id TEXT vs search_sessions UUID | MEDIUM | 1.5 | Yes | 2 |
| 5 | DEBT-DB-005 | user_subscriptions active index missing created_at | **LOW** | 0.5 | Yes | 4 |
| 6 | DEBT-DB-006 | trial_email_log RLS enabled but no explicit policies | MEDIUM | 0.5 | Yes | 1 |
| 7 | DEBT-DB-007 | handle_new_user() TOCTOU race on phone uniqueness | **LOW** | 1 | Yes | 4 |
| 8 | DEBT-DB-008 | 85 migrations with 7 handle_new_user redefinitions -- squash needed | MEDIUM | 5 | No | 2 |
| 9 | DEBT-DB-009 | Stripe price IDs hardcoded in 4 migrations | MEDIUM | 3 | No | 2 |
| 10 | DEBT-DB-010 | JSONB columns without size governance | MEDIUM | 2 | Yes | 2 |
| 11 | DEBT-DB-011 | search_sessions 24 columns (wide table) | LOW | 16 | No | 4 |
| 12 | DEBT-DB-012 | organizations.plan_type CHECK overly permissive | LOW | 0.5 | Yes | 4 |
| 13 | DEBT-DB-013 | reconciliation_log no pg_cron retention job | LOW | 0.5 | Yes | 4 |
| 14 | DEBT-DB-014 | backend/migrations/ directory redundant | LOW | 0.5 | Yes | 4 |
| 15 | DEBT-DB-015 | Legacy plans ON DELETE RESTRICT (intentional) | LOW | 0.5 | Yes | 4 |
| 16 | DEBT-DB-016 | No CHECK constraint on search_sessions.error_code | LOW | 1 | No | 4 |
| 17 | DEBT-DB-017 | pg_cron scheduling collision at 4:00 UTC | LOW | 0.5 | Yes | 4 |
| 18 | DEBT-DB-018 | **Account deletion cascade misses tables -- non-transactional multi-table delete** | **HIGH** | 3 | Yes | 1 |
| 19 | DEBT-DB-019 | `select("*")` on search_sessions in sessions.py pulls 24 cols | LOW | 1 | Yes | 4 |
| 20 | DEBT-DB-020 | **No composite index on search_sessions(user_id, created_at DESC)** | MEDIUM | 0.5 | Yes | 1 |
| 21 | DEBT-DB-021 | `select("*")` on profiles in 8+ call sites | LOW | 2 | No | 4 |
| 22 | DEBT-DB-022 | **quota.py last-resort upsert fallback not truly atomic** | MEDIUM | 2 | Yes | 2 |

**Severity changes from DRAFT:** DEBT-DB-003 MEDIUM->LOW (per DE: <1K users, PK lookups, negative ROI to split), DEBT-DB-005 MEDIUM->LOW (per DE: sub-millisecond sort on <100 rows), DEBT-DB-007 MEDIUM->LOW (per DE: UNIQUE index is real guard).
**New items:** DEBT-DB-018 (HIGH, account deletion), DEBT-DB-019 (LOW, select *), DEBT-DB-020 (MEDIUM, composite index), DEBT-DB-021 (LOW, profiles select *), DEBT-DB-022 (MEDIUM, quota upsert).

### Frontend / UX (validado por @ux-design-expert)

| # | ID | Debito | Severidade | Horas | Quick Win? | Wave |
|---|-----|--------|-----------|-------|-----------|------|
| 1 | DEBT-FE-001 | react-hook-form in devDependencies, used in 3 production pages | HIGH | 0.5 | Yes | 1 |
| 2 | DEBT-FE-002 | **SearchForm zero ARIA attributes -- no role="search", no aria-label** | **CRITICAL** | 3 | Yes | 1 |
| 3 | DEBT-FE-003 | Inconsistent form handling -- 3 pages react-hook-form, rest raw useState | MEDIUM | 8 | No | 2 |
| 4 | DEBT-FE-004 | Framer Motion (~50KB gzip) loaded globally, used in 9 files only | MEDIUM | 6 | No | 2 |
| 5 | DEBT-FE-005 | 6 pages exceed 500 LOC without component decomposition | MEDIUM | 16 | No | 3 |
| 6 | DEBT-FE-006 | Search hooks: 3,287 LOC in 9 hooks, useSearchExecution 770 LOC | **LOW** | 4 | No | 4 |
| 7 | DEBT-FE-007 | **Missing error boundaries on onboarding, signup, login, planos** | **HIGH** | 3 | Yes | 1 |
| 8 | DEBT-FE-008 | Skip-link broken on all protected pages (subsumed by FE-022) | **HIGH** | 0 | -- | 1 |
| 9 | DEBT-FE-009 | Blog TODO placeholders (60+ instances) | LOW | 4 | No | 4 |
| 10 | DEBT-FE-010 | No i18n infrastructure (pt-BR only -- design choice) | N/A | N/A | No | -- |
| 11 | DEBT-FE-011 | Duplicate LoadingProgress + AddToPipelineButton across dirs | LOW | 2 | No | 4 |
| 12 | DEBT-FE-012 | Feature-gated pages (/alertas, /mensagens) show broken state | **MEDIUM** | 2 | Yes | 1 |
| 13 | DEBT-FE-013 | No skeleton loaders for admin, conta, alertas, mensagens, planos | LOW | 4 | No | 4 |
| 14 | DEBT-FE-014 | EnhancedLoadingProgress at 452 LOC | LOW | 4 | No | 4 |
| 15 | DEBT-FE-015 | BottomNav wrong Dashboard icon | LOW | 0.5 | Yes | 1 |
| 16 | DEBT-FE-016 | Raw CSS var() instead of Tailwind semantic classes | LOW | 4 | No | 4 |
| 17 | DEBT-FE-017 | **Login form lacks aria-invalid and aria-describedby** | **HIGH** | 1.5 | Yes | 1 |
| 18 | DEBT-FE-018 | **Mensagens status badges are color-only (no icon, no SR text)** | MEDIUM | 1 | Yes | 2 |
| 19 | DEBT-FE-019 | **Onboarding progress bar has no accessible semantics** | MEDIUM | 1 | No | 2 |
| 20 | DEBT-FE-020 | **Login mode toggle lacks tab/keyboard semantics** | MEDIUM | 1 | No | 2 |
| 21 | DEBT-FE-021 | **Planos FAQ accordion has no ARIA disclosure pattern** | LOW | 1.5 | No | 4 |
| 22 | DEBT-FE-022 | **Protected layout main tag missing id="main-content"** (root cause of FE-008) | **HIGH** | 0.25 | Yes | 1 |
| 23 | DEBT-FE-023 | **No focus management after search completes** | MEDIUM | 2 | No | 2 |
| 24 | DEBT-FE-024 | **Pricing page CTA button has no inline loading state** | LOW | 1 | No | 4 |

**Severity changes from DRAFT:** DEBT-FE-002 HIGH->CRITICAL (per UX: core page invisible to assistive tech), DEBT-FE-006 MEDIUM->LOW (per UX: document only, decomposition is logical), DEBT-FE-007 MEDIUM->HIGH (per UX: conversion-critical pages crash without recovery), DEBT-FE-008 MEDIUM->HIGH (per UX: keyboard nav broken on all protected pages; subsumed by FE-022), DEBT-FE-012 LOW->MEDIUM (per UX: users see broken state from shared links).
**New items:** DEBT-FE-017 through DEBT-FE-024 (8 items, 11.25h total).

### Qualidade / Testing (identificado por @qa)

| # | ID | Debito | Severidade | Horas | Quick Win? | Wave |
|---|-----|--------|-----------|-------|-----------|------|
| 1 | QA-DEBT-001 | `cron_jobs.py` (2,039 LOC) has ZERO test files | HIGH | 6 | No | 0 |
| 2 | QA-DEBT-002 | `supabase_client.py` (537 LOC, circuit breaker) has ZERO test files | HIGH | 4 | No | 0 |
| 3 | QA-DEBT-003 | `search_state_manager.py` (544 LOC) has ZERO test files | MEDIUM | 3 | No | 0 |
| 4 | QA-DEBT-004 | `worker_lifecycle.py` (125 LOC) has ZERO test files | MEDIUM | 1 | No | 0 |
| 5 | QA-DEBT-005 | 11 `filter_*.py` submodules have no individual test files | MEDIUM | 6 | No | 0 |
| 6 | QA-DEBT-006 | Webhook handler coverage incomplete -- may not cover all 10+ event types | MEDIUM | 4 | No | 0 |
| 7 | QA-DEBT-007 | Frontend pages with zero tests: onboarding, mensagens, redefinir-senha, ajuda, features | MEDIUM | 8 | No | 4 |
| 8 | QA-DEBT-008 | No `requirements.txt` lockfile with hashes (supply chain risk) | LOW | 2 | No | 4 |
| 9 | QA-DEBT-009 | Test coverage unevenly distributed (some modules 10+ files, others zero) | INFO | 0 | No | -- |

### CI/CD (identificado por @qa)

| # | ID | Debito | Severidade | Horas | Quick Win? | Wave |
|---|-----|--------|-----------|-------|-----------|------|
| 1 | DEBT-CI-001 | `tests.yml` vs `backend-tests.yml` vs `backend-ci.yml` -- unclear which is PR gate | MEDIUM | 3 | No | 2 |
| 2 | DEBT-CI-002 | No `pip-audit` or `npm audit` in CI pipeline | LOW | 2 | No | 4 |

---

## Matriz de Priorizacao Final

Single ranked list of ALL 76 items, sorted by Wave then by impact/effort ratio.

| Rank | ID | Debito | Area | Sev. | Horas | Wave | Deps |
|------|-----|--------|------|------|-------|------|------|
| **Wave 0: Safety Net** | | | | | | | |
| 1 | QA-DEBT-001 | cron_jobs.py zero tests | QA | HIGH | 6 | 0 | Prereq for SYS-005 |
| 2 | QA-DEBT-002 | supabase_client.py zero tests | QA | HIGH | 4 | 0 | Prereq for SYS-006 |
| 3 | QA-DEBT-005 | filter_*.py submodules zero tests | QA | MED | 6 | 0 | Prereq for SYS-001 |
| 4 | QA-DEBT-006 | Webhook handler incomplete coverage | QA | MED | 4 | 0 | Prereq for SYS-007 |
| 5 | QA-DEBT-003 | search_state_manager.py zero tests | QA | MED | 3 | 0 | -- |
| 6 | QA-DEBT-004 | worker_lifecycle.py zero tests | QA | MED | 1 | 0 | -- |
| **Wave 1: Quick Wins + Critical** | | | | | | | |
| 7 | DEBT-FE-022 | Protected layout id="main-content" | FE | HIGH | 0.25 | 1 | Fixes FE-008 |
| 8 | DEBT-FE-001 | react-hook-form to dependencies | FE | HIGH | 0.5 | 1 | -- |
| 9 | DEBT-FE-015 | BottomNav wrong Dashboard icon | FE | LOW | 0.5 | 1 | -- |
| 10 | DEBT-DB-006 | trial_email_log missing RLS policy | DB | MED | 0.5 | 1 | -- |
| 11 | DEBT-DB-020 | search_sessions composite index | DB | MED | 0.5 | 1 | -- |
| 12 | DEBT-DB-002 | classification_feedback FK fix | DB | HIGH | 1 | 1 | Prereq for DB-008 |
| 13 | DEBT-FE-017 | Login form aria-invalid + aria-describedby | FE | HIGH | 1.5 | 1 | -- |
| 14 | DEBT-SYS-013 | ComprasGov v3 dead source disable | SYS | MED | 2 | 1 | -- |
| 15 | DEBT-SYS-008 | api-types.generated.ts bundle verify | SYS | MED | 2 | 1 | -- |
| 16 | DEBT-FE-012 | Feature-gated "Em breve" component | FE | MED | 2 | 1 | -- |
| 17 | DEBT-FE-002 | **SearchForm ARIA (role="search", aria-label, aria-live)** | FE | CRIT | 3 | 1 | -- |
| 18 | DEBT-FE-007 | Error boundaries onboarding/signup/login/planos | FE | HIGH | 3 | 1 | -- |
| 19 | DEBT-DB-018 | **Account deletion transaction wrap** | DB | HIGH | 3 | 1 | -- |
| 20 | DEBT-DB-001 | Dual subscription_status enum unification + sync trigger | DB | HIGH | 3 | 1 | Prereq for DB-008, info-dep SYS-007/009 |
| 21 | DEBT-SYS-003 | pncp_client sync/async dual pattern removal | SYS | CRIT | 4 | 1 | -- |
| **Wave 2: High Priority** | | | | | | | |
| 22 | DEBT-FE-018 | Mensagens color-only status badges | FE | MED | 1 | 2 | -- |
| 23 | DEBT-FE-019 | Onboarding progress bar a11y semantics | FE | MED | 1 | 2 | -- |
| 24 | DEBT-FE-020 | Login mode toggle tab semantics | FE | MED | 1 | 2 | -- |
| 25 | DEBT-DB-004 | pipeline_items.search_id TEXT vs UUID | DB | MED | 1.5 | 2 | -- |
| 26 | DEBT-DB-010 | JSONB columns size constraints | DB | MED | 2 | 2 | -- |
| 27 | DEBT-DB-022 | quota.py upsert fallback not atomic | DB | MED | 2 | 2 | Before SYS-009 |
| 28 | DEBT-FE-023 | Focus management post-search | FE | MED | 2 | 2 | After FE-002 |
| 29 | DEBT-DB-009 | Stripe price IDs in migrations -> env vars | DB | MED | 3 | 2 | Prereq for DB-008 |
| 30 | DEBT-CI-001 | CI workflow overlap clarification | CI | MED | 3 | 2 | Prereq for Wave 3 |
| 31 | DEBT-DB-008 | Migration squash baseline + CI validation | DB | MED | 5 | 2 | After DB-001, DB-002, DB-009 |
| 32 | DEBT-FE-004 | Framer Motion lazy-load for landing only | FE | MED | 6 | 2 | -- |
| 33 | DEBT-FE-003 | Migrate login/reset to react-hook-form + zod | FE | MED | 8 | 2 | -- |
| **Wave 3: Structural Refactoring** | | | | | | | |
| 34 | DEBT-SYS-020 | Complete startup/ module extraction | SYS | LOW | 3 | 3 | Prereq for SYS-010 |
| 35 | DEBT-SYS-012 | filter module naming cleanup | SYS | MED | 3 | 3 | With SYS-001 |
| 36 | DEBT-SYS-010 | main.py endpoint extraction | SYS | MED | 4 | 3 | After SYS-020 |
| 37 | DEBT-SYS-006 | search_cache.py split | SYS | HIGH | 4 | 3 | After SYS-004, QA-002 |
| 38 | DEBT-SYS-009 | quota.py split (plan, quota, rate limiting) | SYS | HIGH | 4 | 3 | After SYS-004, DB-022 |
| 39 | DEBT-SYS-016 | onboarding + signup page decomposition | SYS | MED | 4 | 3 | -- |
| 40 | DEBT-SYS-002 | schemas.py split by domain | SYS | CRIT | 6 | 3 | After SYS-004 |
| 41 | DEBT-SYS-005 | job_queue + cron_jobs split | SYS | HIGH | 6 | 3 | After SYS-004, QA-001 |
| 42 | DEBT-SYS-007 | Stripe webhook handler split by event type | SYS | HIGH | 6 | 3 | After QA-006 |
| 43 | DEBT-SYS-001 | filter.py full decomposition | SYS | CRIT | 8 | 3 | After SYS-004, QA-005, SYS-012 |
| 44 | DEBT-SYS-004 | Backend package grouping (filter/, search/, billing/, jobs/) | SYS | HIGH | 12 | 3 | Gateway for SYS-001/002/005/006/009 |
| 45 | DEBT-FE-005 | 6 pages > 500 LOC decomposition | FE | MED | 16 | 3 | -- |
| **Wave 4: Polish + Optimization** | | | | | | | |
| 46 | DEBT-DB-005 | user_subscriptions index optimization | DB | LOW | 0.5 | 4 | Defer to 10K+ subs |
| 47 | DEBT-DB-012 | organizations.plan_type CHECK | DB | LOW | 0.5 | 4 | When feature ships |
| 48 | DEBT-DB-013 | reconciliation_log retention | DB | LOW | 0.5 | 4 | -- |
| 49 | DEBT-DB-014 | backend/migrations/ redundant dir | DB | LOW | 0.5 | 4 | -- |
| 50 | DEBT-DB-015 | Legacy plans ON DELETE RESTRICT | DB | LOW | 0.5 | 4 | -- |
| 51 | DEBT-DB-017 | pg_cron collision at 4:00 UTC | DB | LOW | 0.5 | 4 | -- |
| 52 | DEBT-FE-024 | Planos checkout button inline loading | FE | LOW | 1 | 4 | -- |
| 53 | DEBT-DB-007 | handle_new_user TOCTOU error message | DB | LOW | 1 | 4 | -- |
| 54 | DEBT-DB-016 | CHECK on search_sessions.error_code | DB | LOW | 1 | 4 | -- |
| 55 | DEBT-DB-019 | select("*") on search_sessions column projection | DB | LOW | 1 | 4 | -- |
| 56 | DEBT-FE-021 | Planos FAQ accordion ARIA | FE | LOW | 1.5 | 4 | -- |
| 57 | DEBT-CI-002 | pip-audit + npm audit in CI | CI | LOW | 2 | 4 | -- |
| 58 | DEBT-DB-021 | select("*") on profiles column projections | DB | LOW | 2 | 4 | -- |
| 59 | DEBT-FE-011 | Duplicate component consolidation | FE | LOW | 2 | 4 | -- |
| 60 | DEBT-SYS-018 | Stale backend docs | SYS | LOW | 2 | 4 | -- |
| 61 | DEBT-SYS-019 | Scripts not in CI test suite | SYS | LOW | 2 | 4 | -- |
| 62 | QA-DEBT-008 | requirements.txt lockfile with hashes | QA | LOW | 2 | 4 | -- |
| 63 | DEBT-SYS-014 | Dead feature flag cleanup | SYS | MED | 3 | 4 | -- |
| 64 | DEBT-FE-006 | Search hooks documentation | FE | LOW | 4 | 4 | -- |
| 65 | DEBT-FE-009 | Blog TODO placeholder cleanup | FE | LOW | 4 | 4 | -- |
| 66 | DEBT-FE-013 | Skeleton loaders (planos priority) | FE | LOW | 4 | 4 | -- |
| 67 | DEBT-FE-014 | EnhancedLoadingProgress decomposition | FE | LOW | 4 | 4 | -- |
| 68 | DEBT-FE-016 | Raw CSS var() -> Tailwind classes | FE | LOW | 4 | 4 | -- |
| 69 | DEBT-SYS-015 | API proxy factory | SYS | LOW | 4 | 4 | -- |
| 70 | DEBT-SYS-017 | Shared base class for clients/ | SYS | LOW | 4 | 4 | -- |
| 71 | DEBT-SYS-011 | Test LOC audit for duplication | SYS | MED | 8 | 4 | -- |
| 72 | QA-DEBT-007 | Frontend page tests (onboarding, mensagens, etc.) | QA | MED | 8 | 4 | -- |
| 73 | DEBT-DB-003 | profiles wide table extraction | DB | LOW | 10 | 4 | Post-10K users |
| 74 | DEBT-DB-011 | search_sessions 24 columns | DB | LOW | 16 | 4 | Post-1M rows |
| -- | DEBT-SYS-021 | blog.ts hardcoded content | SYS | N/A | N/A | -- | Design choice |
| -- | DEBT-FE-010 | No i18n infrastructure | FE | N/A | N/A | -- | Design choice |
| -- | QA-DEBT-009 | Test coverage uneven distribution | QA | INFO | 0 | -- | Informational |

---

## Plano de Resolucao

### Wave 0: Safety Net (Prerequisite)

**Timeline:** 1 semana | **Esforco:** ~24h | **Owner:** @qa + @dev

Write tests for untested production-critical modules BEFORE any Wave 3 restructuring. Per @qa recommendation, this is a hard prerequisite.

| # | ID | Debito | Horas | Entregavel |
|---|-----|--------|-------|------------|
| 1 | QA-DEBT-001 | Tests for cron_jobs.py | 6 | `test_cron_jobs.py` covering all 15+ scheduled tasks |
| 2 | QA-DEBT-002 | Tests for supabase_client.py + SupabaseCircuitBreaker | 4 | `test_supabase_client.py` covering CB states (CLOSED, OPEN, HALF-OPEN) |
| 3 | QA-DEBT-005 | Tests for 8 filter_*.py submodules | 6 | `test_filter_basic.py`, `test_filter_density.py`, `test_filter_keywords.py`, `test_filter_recovery.py`, `test_filter_status.py`, `test_filter_uf.py`, `test_filter_utils.py`, `test_filter_value.py` |
| 4 | QA-DEBT-006 | Complete webhook handler test matrix | 4 | All 10+ Stripe event types verified in `test_stripe_webhook.py` |
| 5 | QA-DEBT-003 | Tests for search_state_manager.py | 3 | State machine transitions (PENDING -> RUNNING -> COMPLETED/FAILED) tested |
| 6 | QA-DEBT-004 | Tests for worker_lifecycle.py | 1 | Startup/shutdown/reconnect tested |

**Success criteria:**
- All new test files pass: `python scripts/run_tests_safe.py --parallel 4`
- Baseline test count recorded: `pytest --co -q | wc -l` (expected: 7,332+ becomes ~7,500+)
- Zero new failures introduced

**Can run in parallel with Wave 1** -- these are additive tests, not code changes.

### Wave 1: Quick Wins + Critical

**Timeline:** 2 semanas | **Esforco:** ~26.25h | **Owner:** @dev (backend + frontend)

Ship as 3 thematic PRs per @qa recommendation:

**PR 1 -- Security + Accessibility (~10h):**

| # | ID | Debito | Horas |
|---|-----|--------|-------|
| 1 | DEBT-FE-022 | Add id="main-content" to protected layout (fixes skip-link) | 0.25 |
| 2 | DEBT-FE-001 | Move react-hook-form to dependencies | 0.5 |
| 3 | DEBT-DB-006 | trial_email_log RLS policy | 0.5 |
| 4 | DEBT-DB-020 | search_sessions composite index (CREATE INDEX CONCURRENTLY) | 0.5 |
| 5 | DEBT-DB-002 | classification_feedback FK fix (idempotent migration) | 1 |
| 6 | DEBT-FE-017 | Login form aria-invalid + aria-describedby | 1.5 |
| 7 | DEBT-FE-002 | SearchForm role="search" + aria-label | 3 |
| 8 | DEBT-DB-018 | Account deletion -- restructure to use CASCADE, wrap in transaction | 3 |

**PR 2 -- Backend Cleanup (~8h):**

| # | ID | Debito | Horas |
|---|-----|--------|-------|
| 1 | DEBT-SYS-013 | ComprasGov v3 disable via feature flag or removal | 2 |
| 2 | DEBT-SYS-008 | api-types bundle analysis + tree-shake verification | 2 |
| 3 | DEBT-SYS-003 | pncp_client sync/async dual pattern -- remove sync `requests`, keep only httpx | 4 |

**PR 3 -- Frontend Polish (~8.25h):**

| # | ID | Debito | Horas |
|---|-----|--------|-------|
| 1 | DEBT-FE-015 | BottomNav Dashboard icon fix | 0.5 |
| 2 | DEBT-FE-012 | Feature-gated "Em breve" component (distinctive design, not EmptyState) | 2 |
| 3 | DEBT-FE-007 | Error boundaries for onboarding/signup/login/planos | 3 |
| 4 | DEBT-DB-001 | Subscription status enum unify + sync trigger (per @data-engineer plan) | 3 |

**Success criteria:**
- All 3 PRs merged, zero test regressions
- axe-core /buscar returns 0 critical WCAG violations
- Skip-link works on all protected pages (keyboard verification)
- Account deletion is atomic (integration test with simulated failure)
- ComprasGov source disabled, pipeline source count = 2 (PNCP + PCP)

### Wave 2: High Priority

**Timeline:** 2 semanas | **Esforco:** ~35.5h | **Owner:** @dev + @data-engineer

| # | ID | Debito | Horas |
|---|-----|--------|-------|
| 1 | DEBT-FE-018 | Mensagens color-only badges -- add icon + SR text | 1 |
| 2 | DEBT-FE-019 | Onboarding progress bar a11y (role="progressbar", aria-valuenow) | 1 |
| 3 | DEBT-FE-020 | Login mode toggle (role="tablist"/role="tab", aria-selected, arrow keys) | 1 |
| 4 | DEBT-DB-004 | pipeline_items.search_id -- document or add CHECK for UUID format | 1.5 |
| 5 | DEBT-DB-010 | JSONB CHECK constraints (NOT VALID, then VALIDATE) | 2 |
| 6 | DEBT-DB-022 | quota.py upsert fallback -- fix or remove misleading code path | 2 |
| 7 | DEBT-FE-023 | Focus management post-search (shift focus to results header) | 2 |
| 8 | DEBT-DB-009 | Stripe price IDs -- move to env-based seed script (per @data-engineer) | 3 |
| 9 | DEBT-CI-001 | CI workflow audit -- document roles, remove redundancy | 3 |
| 10 | DEBT-DB-008 | Migration squash baseline + weekly CI validation job | 5 |
| 11 | DEBT-FE-004 | Framer Motion lazy-load via next/dynamic (landing only) | 6 |
| 12 | DEBT-FE-003 | Migrate login/recuperar-senha/redefinir-senha to react-hook-form + zod | 8 |

**Dependency chain:** DB-001 (Wave 1) -> DB-009 (3h) -> DB-008 (5h, last in chain).

**Success criteria:**
- Migration squash replays cleanly on fresh PostgreSQL 17 (CI validation passes)
- CI workflow roles documented, no redundant workflows
- Framer Motion only loads on landing page (bundle analyzer confirms)
- All auth forms have consistent real-time validation UX
- JSONB constraints applied without downtime

### Wave 3: Structural Refactoring

**Timeline:** 4 semanas | **Esforco:** ~76h | **Owner:** @dev + @architect

**Hard prerequisite:** Wave 0 (safety net tests) MUST be complete. Baseline test count recorded.

Each DEBT-SYS item is a separate PR with full test validation. Execute in this order:

| # | ID | Debito | Horas | Rationale for order |
|---|-----|--------|-------|---------------------|
| 1 | DEBT-SYS-020 | startup/ module completion | 3 | Prereq for SYS-010 |
| 2 | DEBT-SYS-004 | Package grouping: filter/, search/, billing/, jobs/ | 12 | Gateway -- all subsequent splits depend on package structure |
| 3 | DEBT-SYS-012 + SYS-001 | filter.py decomposition + naming cleanup | 11 | Largest monolith, biggest merge conflict risk |
| 4 | DEBT-SYS-002 | schemas.py split by domain (search, billing, pipeline, user) | 6 | High IDE impact, clear domain boundaries |
| 5 | DEBT-SYS-010 | main.py endpoint extraction to routes/ | 4 | After startup/ is complete |
| 6 | DEBT-SYS-009 | quota.py split (plan_definitions, quota_checker, rate_limiter) | 4 | After package structure + DB-022 fix |
| 7 | DEBT-SYS-006 | search_cache.py split (l1_cache, l2_cache, swr_manager, key_generator) | 4 | After search/ package exists |
| 8 | DEBT-SYS-005 | job_queue + cron_jobs split by domain | 6 | After jobs/ package exists, QA-001 tests exist |
| 9 | DEBT-SYS-007 | Stripe webhook handler split by event type | 6 | After QA-006 webhook test matrix |
| 10 | DEBT-SYS-016 | onboarding + signup page decomposition (step components) | 4 | Parallel with backend work |
| 11 | DEBT-FE-005 | 6 pages > 500 LOC decomposition (onboarding -> planos -> login -> admin) | 16 | Parallel with backend work |

**Per-step validation protocol (from @qa):**
1. Before each PR: record `pytest --co -q | wc -l` (must be >= baseline)
2. After each PR: `python scripts/run_tests_safe.py --parallel 4` -- zero new failures
3. Use backward-compat re-exports (e.g., `schemas.py` re-exports all models from `schemas/`) during transition
4. After Wave 3 completes: add CI guard checking that no old import paths remain in non-test code

**Success criteria:**
- No restructured file exceeds 1,000 LOC
- filter.py reduced to < 500 LOC (orchestration/re-export only)
- All import paths updated; CI guard passes
- Test count >= baseline after every step
- schemas.py has backward-compat re-exports until all consumers updated

### Wave 4: Polish + Optimization

**Timeline:** 4 semanas (ongoing, interleaved with feature work) | **Esforco:** ~97h | **Owner:** Team

Lower priority items addressed opportunistically or when touching related code:

| Category | Items | Total Hours |
|----------|-------|-------------|
| DB hygiene (trivial fixes) | DB-005, DB-007, DB-012, DB-013, DB-014, DB-015, DB-016, DB-017, DB-019, DB-021 | ~9h |
| Frontend polish | FE-006, FE-009, FE-011, FE-013, FE-014, FE-016, FE-021, FE-024 | ~25h |
| Backend cleanup | SYS-014, SYS-015, SYS-017, SYS-018, SYS-019 | ~15h |
| Testing + QA | SYS-011, QA-007, QA-008 | ~18h |
| CI/CD | CI-002 | ~2h |
| Deferred (scale-dependent) | DB-003 (10h at 10K users), DB-011 (16h at 1M rows) | ~26h |

**Trigger-based items (fix when touching related feature):**
- DEBT-DB-003: Revisit at 10K users or when profiles exceeds 30 columns
- DEBT-DB-011: Revisit at 1M search_sessions rows
- DEBT-FE-013: Add skeleton for planos when optimizing conversion funnel
- DEBT-FE-006: Document search hooks when onboarding a new frontend developer
- DEBT-FE-018: Fix when un-gating the mensagens feature (if not done in Wave 2)

**Success criteria:**
- No known CRITICAL or HIGH items remain
- Backend test coverage >= 70% (existing CI gate)
- Frontend test coverage >= 60% (existing CI gate)
- Bundle size stable or improved vs current baseline

---

## Dependencias Entre Waves

```
Wave 0 (Safety Net) ──────────────────────────────> Wave 3 (Structural)
    |                                                     |
    | (runs in parallel)                                  |
    v                                                     v
Wave 1 (Quick Wins) ───> Wave 2 (High Priority) ───> Wave 4 (Polish)

Critical path within Waves:

  Wave 1: DB-002 (FK fix) ──────────────────────────────> feeds Wave 2
  Wave 2: DB-001 (from W1) ──> DB-009 (price IDs) ──> DB-008 (squash, LAST)
  Wave 3: SYS-020 ──> SYS-004 ──> SYS-001/002/005/006/009/010

Parallel tracks:
  - Frontend FE-* can run alongside backend SYS-* in any wave
  - Database DB-* is independent of frontend FE-* work
  - Wave 0 test creation runs fully in parallel with Wave 1 quick wins
```

**Key blockers:**

| Blocker | Blocks | Resolution |
|---------|--------|------------|
| Wave 0 incomplete | ALL of Wave 3 | Hard gate: no restructuring PR merges without Wave 0 complete |
| DEBT-DB-001 + DB-002 + DB-009 | DEBT-DB-008 (squash) | Sequential chain: FK fix -> enum unify -> price IDs -> squash |
| DEBT-CI-001 (CI clarity) | Wave 3 confidence | Resolve in Wave 2 before high-change period |
| DEBT-DB-022 (quota fix) | DEBT-SYS-009 (quota split) | Fix the bug before refactoring the module |
| QA-DEBT-005 (filter tests) | DEBT-SYS-001 (filter decomp) | Cannot verify correctness of submodules without tests |
| QA-DEBT-001 (cron tests) | DEBT-SYS-005 (job split) | Cannot verify scheduled tasks survive restructuring |
| QA-DEBT-006 (webhook tests) | DEBT-SYS-007 (webhook split) | Cannot split event handlers without full coverage |

---

## Riscos e Mitigacoes

| Risco | Probabilidade | Impacto | Mitigacao | Owner |
|-------|---------------|---------|-----------|-------|
| **Billing status drift causes access bugs** (DB-001 + SYS-007 + SYS-009 + QA-006) | MEDIUM | CRITICAL | Unify enums in Wave 1. Complete webhook test matrix in Wave 0. Validate sync trigger with integration test. | @data-engineer + @qa |
| **Backend restructuring breaks 344 test files** (all Wave 3) | HIGH during Wave 3 | HIGH | Wave 0 safety net. Per-step test count validation. Separate PRs per item. Backward-compat re-exports during transition. Import path CI guard after completion. | @dev + @qa |
| **Account deletion leaves partial state** (DB-018) | LOW | HIGH | Transaction wrap in Wave 1 PR 1. Integration test simulating auth.users delete failure. Per @data-engineer: use CASCADE from profiles, only manually delete Stripe-dependent rows. | @data-engineer |
| **Filter decomposition without submodule tests** (SYS-001 + QA-005) | HIGH if Wave 0 skipped | MEDIUM | QA-DEBT-005 in Wave 0 creates dedicated test files for all 8 filter_*.py submodules. Hard gate: no SYS-001 PR without QA-005 complete. | @qa |
| **Migration squash captures inconsistent state** (DB-008) | LOW | HIGH | Critical path enforced: DB-001 + DB-002 + DB-009 all complete before squash. CI job diffs squash result against production schema weekly. | @data-engineer |
| **Cron jobs break after restructuring** (QA-001 + SYS-005) | LOW | HIGH | QA-DEBT-001 creates cron_jobs.py tests in Wave 0. Full suite run before and after SYS-005 split. | @qa |
| **Framer Motion removal degrades landing page** (FE-004) | LOW | MEDIUM | Keep framer-motion for landing page via next/dynamic. Only replace usage on authenticated pages with CSS animations. Per @ux: landing animations deliver premium feel. | @dev |
| **CI confusion during Wave 3** (CI-001) | MEDIUM | MEDIUM | Resolve workflow overlap in Wave 2 DEBT-CI-001. Document which workflow is the PR gate. Clarify before high-change period. | @devops |
| **Feature work blocked by debt resolution** | MEDIUM | MEDIUM | Waves 0+1 are parallel. Wave 4 interleaves with features. Only Wave 3 requires 4 weeks of dedicated refactoring focus. Plan feature freezes accordingly. | @pm |
| **3 pre-existing frontend test failures** grow during debt work | LOW | LOW | Fix or document the 3 known failures before starting frontend debt items (Wave 1 PR 3). Maintain clean baseline. | @qa |

---

## Criterios de Sucesso

### Per-Wave Metrics

| Wave | Metric | Target | How to Measure |
|------|--------|--------|----------------|
| 0 | New test files created | >= 12 new files | `find backend/tests -name "test_cron*" -o -name "test_supabase_client*" -o -name "test_filter_basic*"` etc. |
| 0 | Test count increase | >= 150 new tests added to baseline | `pytest --co -q \| wc -l` delta from current 7,332+ |
| 1 | WCAG critical violations on /buscar | 0 | axe-core Playwright spec (extend `accessibility-audit.spec.ts`) |
| 1 | Skip-link functional on protected pages | Tab -> Enter navigates to main content | E2E keyboard test on /dashboard, /pipeline, /historico |
| 1 | Account deletion atomicity | No partial state on simulated failure | Integration test: mock auth.users delete failure, verify profiles + children intact |
| 1 | Pipeline source count | 2 (PNCP + PCP only) | Health endpoint shows ComprasGov disabled |
| 2 | Migration squash clean replay | 0 schema diff vs production | CI job: fresh PostgreSQL 17 -> apply squash -> apply remaining migrations -> `pg_dump --schema-only` diff |
| 2 | Auth forms consistent validation | All use react-hook-form + zod | Manual test + jest coverage on login/recuperar-senha/redefinir-senha |
| 2 | Framer Motion loading scope | Landing page only | `npm run build` + bundle analyzer shows no framer-motion chunks on /buscar |
| 3 | Largest backend file after restructuring | < 1,000 LOC | `wc -l` on all files in restructured packages |
| 3 | filter.py LOC | < 500 (orchestration + re-exports only) | `wc -l backend/filter.py` |
| 3 | Test count post-restructuring | >= Wave 0 baseline (7,500+) | `pytest --co -q \| wc -l` |
| 3 | Old import paths in non-test code | 0 occurrences | CI guard: `grep -r "from filter import" --include="*.py" backend/ \| grep -v tests/` |
| 4 | Backend test coverage | >= 70% | `pytest --cov` (existing CI gate) |
| 4 | Frontend test coverage | >= 60% | `npm run test:coverage` (existing CI gate) |
| 4 | Known CRITICAL items remaining | 0 | This document |
| 4 | Known HIGH items remaining | 0 | This document |

### Overall Health Indicators

- **Backend test baseline:** 7,332+ passing, 0 failures. Must never decrease.
- **Frontend test baseline:** 5,583+ passing, 3 pre-existing failures (fix before Wave 1 PR 3).
- **Bundle size:** Record current with `npm run build`. No increase from Wave 2 onward.
- **CI run time:** Monitor for regressions during Wave 3. If suite exceeds 15 minutes, investigate parallelization.
- **Zero-failure policy:** 0 test failures is the only acceptable baseline per project rules (CLAUDE.md).

---

## Esforco Total por Wave

| Wave | Items | Horas | Timeline | Parallelizable? |
|------|-------|-------|----------|-----------------|
| Wave 0: Safety Net | 6 | ~24h | 1 semana | Yes, with Wave 1 |
| Wave 1: Quick Wins + Critical | 15 | ~26.25h | 2 semanas | Yes, with Wave 0 |
| Wave 2: High Priority | 12 | ~35.5h | 2 semanas | FE/DB in parallel |
| Wave 3: Structural | 11 | ~76h | 4 semanas | FE/BE in parallel, but sequential within BE |
| Wave 4: Polish | ~25 | ~97h | 4+ semanas (interleaved) | All items independent |
| **Total actionable** | **69** | **~258.75h** | **~13 semanas** | |

**Note:** Wave 4 deferred items (DB-003 at 10h, DB-011 at 16h) and design-choice items (FE-010, SYS-021) add ~26h if ever needed. Full theoretical inventory including all items: ~285h.

---

## Apendice: Changelog DRAFT -> FINAL

### Severity Changes (13 adjustments)

| ID | DRAFT | FINAL | Reviewer | Reason |
|----|-------|-------|----------|--------|
| DEBT-FE-002 | HIGH | **CRITICAL** | @ux | Core page invisible to assistive tech; buscar is #1 page |
| DEBT-FE-007 | MEDIUM | **HIGH** | @ux | Conversion-critical pages (signup, onboarding, planos) crash without recovery |
| DEBT-FE-008 | MEDIUM | **HIGH** | @ux | Keyboard nav broken on all protected pages; subsumed by FE-022 (0h, same fix) |
| DEBT-FE-012 | LOW | **MEDIUM** | @ux | Users reaching /alertas or /mensagens via URL see API errors with no explanation |
| DEBT-FE-006 | MEDIUM | **LOW** | @ux | Not user-facing; decomposition is already logical, only needs documentation |
| DEBT-SYS-008 | HIGH | **MEDIUM** | @ux | Minimal user impact if tree-shaken by Next.js; verify with bundle analyzer first |
| DEBT-SYS-015 | MEDIUM | **LOW** | @ux | Zero user impact; backend/DX concern only |
| DEBT-DB-003 | MEDIUM | **LOW** | @data-engineer | <1K users, all PK lookups, splitting creates more migration complexity than it saves |
| DEBT-DB-005 | MEDIUM | **LOW** | @data-engineer | Sub-millisecond sort on <100 rows; defer to 10K+ subscriptions |
| DEBT-DB-007 | MEDIUM | **LOW** | @data-engineer | UNIQUE partial index is the real guard; trigger check is redundant defense |
| DEBT-FE-010 | LOW | **N/A** | @ux | Confirmed as intentional design choice for pt-BR-only market, not debt |

### New Items (22 additions)

| Source | Count | IDs | Total Hours |
|--------|-------|-----|-------------|
| @data-engineer | 5 | DEBT-DB-018 (account deletion, 3h), DB-019 (select * sessions, 1h), DB-020 (composite index, 0.5h), DB-021 (select * profiles, 2h), DB-022 (quota upsert, 2h) | 8.5h |
| @ux-design-expert | 8 | DEBT-FE-017 (login aria, 1.5h), FE-018 (color-only badges, 1h), FE-019 (progress bar a11y, 1h), FE-020 (tab semantics, 1h), FE-021 (FAQ ARIA, 1.5h), FE-022 (main-content id, 0.25h), FE-023 (focus management, 2h), FE-024 (CTA loading, 1h) | 9.25h |
| @qa | 9 | QA-DEBT-001 (cron tests, 6h), QA-002 (supabase tests, 4h), QA-003 (state mgr tests, 3h), QA-004 (worker tests, 1h), QA-005 (filter submodule tests, 6h), QA-006 (webhook coverage, 4h), QA-007 (FE page tests, 8h), QA-008 (lockfile, 2h), QA-009 (info, 0h) | 34h |
| @qa (CI) | 2 | DEBT-CI-001 (workflow overlap, 3h), CI-002 (audit in CI, 2h) | 5h |

### Structural Changes from DRAFT

1. **Wave 0 added** -- Per @qa: safety net tests are a hard prerequisite before any Wave 3 restructuring. This is the single most impactful structural change from the DRAFT.
2. **Wave 1 organized into 3 thematic PRs** -- Per @qa: avoids 18 individual PRs (review fatigue) while keeping each PR coherent and independently revertible.
3. **DB execution order refined** -- Per @data-engineer critical path: DB-002 (1h) -> DB-001 (3h) -> DB-009 (3h) -> DB-008 (5h, must be last).
4. **Accessibility priority clarified** -- Per @ux: FE-022 first (0.25h, fixes root cause of skip-link on all protected pages), then FE-002 (3h, SearchForm ARIA), then FE-017 (1.5h, login form).
5. **FE-008 subsumed by FE-022** -- Both are the same fix (add id="main-content" to protected layout). Tracked under FE-022 only, FE-008 set to 0h.
6. **Risk matrix expanded** -- 3 new cross-cutting risks from @qa: (a) billing + untested webhooks, (b) filter decomposition + no submodule tests, (c) cron jobs + migration squash.

### Specialist Answers Incorporated

| Question | Decision | Impact |
|----------|----------|--------|
| DB-001 approach | Option (c) with migration path: unify enums + sync trigger + document canonical source | DB-001 plan confirmed at 3h |
| DB-003 timing | Defer to post-10K users | Moved to Wave 4 deferred |
| DB-008 CI validation | Weekly CI job replays squash + diffs against production schema | Included in DB-008 5h estimate |
| DB-009 Stripe staging | No staging exists. Use env-based seed script (simplest, 2h) | DB-009 approach set at 3h |
| DB-010 JSONB limits | Apply CHECK with NOT VALID for zero-downtime, then VALIDATE | DB-010 confirmed at 2h |
| FE-002 aria-live scope | ResultsHeader already has aria-live="polite" -- sufficient. Focus on role="search" + aria-label | FE-002 scope confirmed |
| FE-004 Framer Motion | Keep for landing (next/dynamic), replace on auth pages with CSS animations | FE-004 approach set at 6h |
| FE-005 page decomp order | Onboarding first (783 LOC, first protected experience), then Planos, then Login, then Admin | Decomposition order established |
| FE-012 design | Distinctive "Coming soon" with notification toggle, NOT generic EmptyState | Design spec established |
| FE-013 skeleton priority | Planos only now (conversion anxiety); defer rest | Scope reduced |
| QA test strategy | Baseline count + per-step validation + import path CI guard | Wave 3 protocol defined |
| QA PR batching | 3 thematic PRs (security/a11y, backend, frontend) | Wave 1 structure set |
| QA accessibility validation | Phase 1 axe-core automated (2h, immediate); Phase 2 manual NVDA/VO (4h, next sprint) | A11y testing phased |

---

*Document finalized 2026-03-21 by @architect (Atlas) during Brownfield Discovery Phase 8.*
*Consolidates: technical-debt-DRAFT.md (54 items) + db-specialist-review.md (+5 items, 3 downgrades) + ux-specialist-review.md (+8 items, 5 severity changes) + qa-review.md (+9 items, +2 CI items, Wave 0 prerequisite).*
*Final inventory: 76 items across 5 categories. 69 actionable. Estimated effort: ~259h over 13 weeks.*
