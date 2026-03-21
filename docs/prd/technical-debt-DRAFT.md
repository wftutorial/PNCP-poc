# Technical Debt Assessment - DRAFT

**Projeto:** SmartLic (smartlic.tech)
**Data:** 2026-03-21
**Status:** DRAFT -- Pendente revisao dos especialistas
**Autor:** @architect (Atlas) -- Consolidacao da Brownfield Discovery (Phases 1-4)
**Fontes:** system-architecture.md (Phase 2), DB-AUDIT.md (Phase 3a), frontend-spec.md (Phase 3b)

---

## 1. Executive Summary

| Metric | Value |
|--------|-------|
| **Total debt items** | 55 (across 3 audits) |
| **Critical** | 3 |
| **High** | 10 |
| **Medium** | 20 |
| **Low** | 21 |
| **Resolved/Accepted** | 1 (DB-DEBT-006 verified present) |
| **Actionable items** | 54 |
| **Total estimated effort** | ~297h (min), ~325h (max) |
| **Quick wins (< 4h, high ROI)** | 11 items |

### Key Risks

1. **Monolithic file accumulation** -- Four backend files exceed 2,000 LOC (filter.py 3,871, pncp_client.py 2,515, search_cache.py 2,512, schemas.py 2,121). These are the most-modified files and the most likely to cause merge conflicts and regression bugs.
2. **Subscription status drift** -- Dual tracking in profiles vs user_subscriptions with non-identical enum values (DB-DEBT-001). Billing decisions could use stale data.
3. **Accessibility gaps** -- SearchForm (the most-used component) has zero ARIA attributes (FE-DEBT-002). Skip-link broken on all protected pages (FE-DEBT-008).
4. **Migration fragility** -- 85 migration files with 7 redefinitions of handle_new_user(). Fresh install replay is risky (DB-DEBT-008). classification_feedback FK could point to auth.users on disaster recovery (DB-DEBT-002).
5. **Dead source consuming budget** -- ComprasGov v3 down since March 2026 but still active in pipeline, consuming timeout and circuit breaker resources (DEBT-SYS-013).

---

## 2. Debitos de Sistema (from system-architecture.md)

### 2.1 Critical

| ID | Debito | Impacto | Esforco (h) | Area |
|----|--------|---------|-------------|------|
| DEBT-SYS-001 | `filter.py` at 3,871 LOC -- core matching logic not fully migrated to 11 submodules | Maintenance burden, merge conflicts, hard to reason about filtering | 8 | Backend/Architecture |
| DEBT-SYS-002 | `schemas.py` at 2,121 LOC -- all Pydantic models for 126 endpoints in one file | Slow IDE, merge conflicts, no domain boundary enforcement | 6 | Backend/Architecture |
| DEBT-SYS-003 | `pncp_client.py` imports sync `requests` alongside async `httpx` -- dual-client pattern | Code duplication, potential thread pool exhaustion under load | 4 | Backend/Performance |

### 2.2 High

| ID | Debito | Impacto | Esforco (h) | Area |
|----|--------|---------|-------------|------|
| DEBT-SYS-004 | 69 top-level Python files -- no package grouping for filter/search/PNCP clusters | Developer onboarding friction, hard to navigate | 12 | Backend/Architecture |
| DEBT-SYS-005 | `job_queue.py` (2,152 LOC) + `cron_jobs.py` (2,039 LOC) -- monolithic job definitions | Hard to test individual jobs, import side effects | 6 | Backend/Architecture |
| DEBT-SYS-006 | `search_cache.py` at 2,512 LOC -- L1, L2, SWR, key generation, serialization in one file | Complex state management in single module | 4 | Backend/Maintainability |
| DEBT-SYS-007 | `webhooks/stripe.py` at 1,192 LOC -- 10+ event types in single handler | Hard to audit security-critical billing logic | 6 | Backend/Security |
| DEBT-SYS-008 | Frontend `api-types.generated.ts` at 5,177 LOC -- possibly not tree-shaken | Larger bundle size, slower page loads | 2 | Frontend/Performance |
| DEBT-SYS-009 | `quota.py` at 1,622 LOC -- mixes plan definition, quota, rate limiting, trial | Multiple responsibilities, hard to modify billing rules | 4 | Backend/Architecture |

### 2.3 Medium

| ID | Debito | Impacto | Esforco (h) | Area |
|----|--------|---------|-------------|------|
| DEBT-SYS-010 | `main.py` still has 7 endpoints + Sentry init despite startup/ decomposition | Entrypoint does too much | 4 | Backend/Maintainability |
| DEBT-SYS-011 | Test LOC (140K) is 1.8x source LOC (77K) -- potential duplication or over-specification | Slower CI, test maintenance burden | 8 | Backend/Testing |
| DEBT-SYS-012 | 11 filter_*.py + filter.py -- ambiguous ownership, stale docstrings | Confusing module naming | 3 | Backend/Maintainability |
| DEBT-SYS-013 | ComprasGov v3 down since Mar 2026 -- client (838 LOC) still active | Wasted timeout budget, confusing health dashboard | 2 | Backend/Infrastructure |
| DEBT-SYS-014 | 40+ feature flags, some may be permanently enabled/disabled | Dead flag accumulation, config complexity | 3 | Backend/Maintainability |
| DEBT-SYS-015 | 58 API proxy routes, many identical patterns -- generic factory underused | Code duplication across proxy routes | 4 | Frontend/Architecture |
| DEBT-SYS-016 | `onboarding/page.tsx` (783 LOC) + `signup/page.tsx` (703 LOC) no component decomposition | Hard to test form steps, maintenance burden | 4 | Frontend/Maintainability |

### 2.4 Low

| ID | Debito | Impacto | Esforco (h) | Area |
|----|--------|---------|-------------|------|
| DEBT-SYS-017 | `backend/clients/` -- 5 clients with no shared base class despite base.py existing | Inconsistent error handling across sources | 4 | Backend/Maintainability |
| DEBT-SYS-018 | Backend docs/ currency unknown | Potentially stale documentation | 2 | Documentation |
| DEBT-SYS-019 | scripts/ utility scripts not in CI test suite | Script quality not validated | 2 | Backend/Testing |
| DEBT-SYS-020 | startup/ module exists but main.py still does most initialization | Incomplete refactoring, two paths | 3 | Backend/Architecture |
| DEBT-SYS-021 | blog.ts (785 LOC) -- hardcoded blog content, requires deploys to update | Content updates require code changes | N/A | Frontend/Design Choice |

---

## 3. Debitos de Database (from DB-AUDIT.md)

> **PENDENTE:** Revisao do @data-engineer para validacao de estimativas e prioridade.

### 3.1 High

| ID | Debito | Impacto | Esforco (h) | Area |
|----|--------|---------|-------------|------|
| DEBT-DB-001 | Dual subscription_status tracking -- profiles vs user_subscriptions with mismatched enums ("canceling" vs "canceled", "trial" vs "trialing") | Status drift, billing decisions on stale data | 3-4 | Schema/Billing |
| DEBT-DB-002 | classification_feedback FK references auth.users in CREATE TABLE (DEBT-002 bridge migration). DEBT-113 fixes at runtime, but fresh install could fail | Disaster recovery replay creates wrong FK | 1 | Security/Migrations |

### 3.2 Medium

| ID | Debito | Impacto | Esforco (h) | Area |
|----|--------|---------|-------------|------|
| DEBT-DB-003 | profiles table 20+ columns (auth + billing + marketing + context) | Every query pulls all columns, trigger complexity | 8-12 | Schema |
| DEBT-DB-004 | pipeline_items.search_id is TEXT, search_sessions.search_id is UUID -- type mismatch | No FK possible, implicit casts in joins | 1-2 | Schema |
| DEBT-DB-005 | user_subscriptions active index missing created_at for ORDER BY DESC | Sort step after index lookup, matters at 10K+ subs | 0.5 | Indexes |
| DEBT-DB-006 | trial_email_log has RLS enabled but no explicit policies | Violates project pattern (every table has service_role_all) | 0.5 | Security |
| DEBT-DB-007 | handle_new_user() TOCTOU race on phone uniqueness check | Race condition (caught by UNIQUE index, but error message is wrong) | 1 | Security |
| DEBT-DB-008 | 85 migrations with complex dependency chains, 7 redefinitions of handle_new_user() | Fresh replay risky, hard to understand current state | 4-6 | Migrations |
| DEBT-DB-009 | Stripe price IDs hardcoded in 4 migrations | Dev/staging environments point to prod Stripe prices | 3-4 | Migrations |
| DEBT-DB-010 | JSONB columns without size governance (audit_events, stripe_webhook_events, alerts.filters, etc.) | Malicious/buggy large inserts cause storage bloat | 2 | Performance |

### 3.3 Low

| ID | Debito | Impacto | Esforco (h) | Area |
|----|--------|---------|-------------|------|
| DEBT-DB-011 | search_sessions 24 columns (wide table) | Large row size, historical queries fetch extra | 16+ | Schema |
| DEBT-DB-012 | organizations.plan_type CHECK overly permissive (13 values, feature not yet active) | Allows invalid data, no practical impact | 0.5 | Schema |
| DEBT-DB-013 | reconciliation_log no pg_cron retention job | Unbounded growth (~30 rows/month) | 0.5 | Indexes |
| DEBT-DB-014 | backend/migrations/ directory fully redundant (covered by Supabase migrations) | Developer confusion about which set to use | 0.5 | Migrations |
| DEBT-DB-015 | Legacy plans cannot be deleted (ON DELETE RESTRICT, intentional) | 12 rows instead of 3, frontends must filter | 0.5 | Integrity |
| DEBT-DB-016 | No CHECK constraint on search_sessions.error_code | Inconsistent error codes, analytics GROUP BY surprises | 1 | Integrity |
| DEBT-DB-017 | pg_cron scheduling collision at 4:00 UTC (two jobs) | Brief I/O contention, negligible at current volume | 0.5 | Performance |

**Note:** DB-DEBT-006 (conversations index) was verified as RESOLVED -- index exists. DB-DEBT-015 (search_state_transitions FK) was accepted as intentional (0h effort).

---

## 4. Debitos de Frontend/UX (from frontend-spec.md)

> **PENDENTE:** Revisao do @ux-design-expert para impacto UX e prioridade de acessibilidade.

### 4.1 High

| ID | Debito | Impacto | Esforco (h) | Area |
|----|--------|---------|-------------|------|
| DEBT-FE-001 | react-hook-form in devDependencies but used in 3 production pages | Potential build failure in strict environments | 0.5 | Maintainability |
| DEBT-FE-002 | SearchForm has zero ARIA attributes -- no role="search", no aria-label, no aria-live | Screen readers cannot identify search or receive result announcements | 3 | Accessibility |

### 4.2 Medium

| ID | Debito | Impacto | Esforco (h) | Area |
|----|--------|---------|-------------|------|
| DEBT-FE-003 | Inconsistent form handling -- 3 pages use react-hook-form + zod, rest use raw useState | Inconsistent validation UX, login lacks real-time feedback | 8 | Consistency |
| DEBT-FE-004 | Framer Motion (~50KB gzip) loaded globally, used in only 9 files | Increased bundle for all pages including non-animated ones | 6 | Performance |
| DEBT-FE-005 | 6 pages exceed 500 LOC without component decomposition | Hard to maintain, test, and review | 16 | Maintainability |
| DEBT-FE-006 | Search hooks: 3,287 LOC in 9 hooks, useSearchExecution alone 770 LOC | High onboarding cost, hard to trace state flow | 24 (refactor) / 4 (docs) | Maintainability |
| DEBT-FE-007 | Missing error boundaries on onboarding, signup, login | Errors lose navigation context, full-page crash | 3 | UX |
| DEBT-FE-008 | Skip-link target broken on all protected pages (missing id="main-content") | Keyboard users cannot bypass navigation on buscar/dashboard/pipeline | 0.5 | Accessibility |

### 4.3 Low

| ID | Debito | Impacto | Esforco (h) | Area |
|----|--------|---------|-------------|------|
| DEBT-FE-009 | Blog TODO placeholders (60+ instances for MKT-003/MKT-005 internal links) | Missing SEO internal linking | 4 | SEO |
| DEBT-FE-010 | No i18n infrastructure (all strings hardcoded pt-BR) | Internationalization would require touching every file | 80+ | Design Choice |
| DEBT-FE-011 | Duplicate LoadingProgress + AddToPipelineButton in app/components/ and components/ | Developer confusion, potential inconsistency | 2 | Consistency |
| DEBT-FE-012 | Feature-gated pages (/alertas, /mensagens) still routable, show broken state | Users see error without explanation | 2 | UX |
| DEBT-FE-013 | No skeleton loaders for admin, conta, alertas, mensagens, planos | Generic spinner instead of content-shaped skeletons | 4 | UX |
| DEBT-FE-014 | EnhancedLoadingProgress at 452 LOC -- progress, UF grid, phases, fallback in one file | Hard to test individual behaviors | 4 | Maintainability |
| DEBT-FE-015 | BottomNav uses wrong icon for Dashboard (search instead of LayoutDashboard) | Visual inconsistency between mobile and desktop nav | 0.5 | UX |
| DEBT-FE-016 | Raw CSS variable usage (`var(--...)`) instead of Tailwind semantic classes in some components | Inconsistent styling, no Tailwind intellisense | 4 | Consistency |

---

## 5. Matriz de Priorizacao Preliminar

All 54 actionable items ranked by severity, then by impact/effort ratio (highest ROI first). Items marked "Quick Win" are < 4h effort AND high impact.

| Rank | ID | Debito | Area | Sev. | Esforco | Quick Win? |
|------|-----|--------|------|------|---------|-----------|
| 1 | DEBT-SYS-003 | pncp_client sync/async dual pattern | Backend | CRIT | 4h | Yes |
| 2 | DEBT-SYS-002 | schemas.py monolith (2,121 LOC) | Backend | CRIT | 6h | No |
| 3 | DEBT-SYS-001 | filter.py not fully decomposed (3,871 LOC) | Backend | CRIT | 8h | No |
| 4 | DEBT-DB-001 | Dual subscription_status tracking | Database | HIGH | 3-4h | Yes |
| 5 | DEBT-DB-002 | classification_feedback FK to auth.users | Database | HIGH | 1h | Yes |
| 6 | DEBT-FE-001 | react-hook-form in devDependencies | Frontend | HIGH | 0.5h | Yes |
| 7 | DEBT-FE-002 | SearchForm zero ARIA attributes | Frontend | HIGH | 3h | Yes |
| 8 | DEBT-FE-008 | Skip-link broken on protected pages | Frontend | MED | 0.5h | Yes |
| 9 | DEBT-SYS-008 | api-types.generated.ts bundle impact | Frontend | HIGH | 2h | Yes |
| 10 | DEBT-SYS-013 | ComprasGov v3 dead source still active | Backend | MED | 2h | Yes |
| 11 | DEBT-DB-006 | trial_email_log missing RLS policy | Database | MED | 0.5h | Yes |
| 12 | DEBT-DB-005 | user_subscriptions index missing created_at | Database | MED | 0.5h | Yes |
| 13 | DEBT-DB-007 | handle_new_user TOCTOU race | Database | MED | 1h | Yes |
| 14 | DEBT-SYS-009 | quota.py mixed responsibilities (1,622 LOC) | Backend | HIGH | 4h | No |
| 15 | DEBT-SYS-007 | Stripe webhook 1,192 LOC single handler | Backend | HIGH | 6h | No |
| 16 | DEBT-SYS-006 | search_cache.py monolith (2,512 LOC) | Backend | HIGH | 4h | No |
| 17 | DEBT-SYS-005 | job_queue + cron_jobs monoliths | Backend | HIGH | 6h | No |
| 18 | DEBT-SYS-004 | 69 flat top-level files | Backend | HIGH | 12h | No |
| 19 | DEBT-FE-007 | Missing error boundaries (onboarding/signup/login) | Frontend | MED | 3h | Yes |
| 20 | DEBT-SYS-012 | filter module naming ambiguity | Backend | MED | 3h | No |
| 21 | DEBT-SYS-014 | Dead feature flag accumulation | Backend | MED | 3h | No |
| 22 | DEBT-SYS-010 | main.py still has 7 endpoints | Backend | MED | 4h | No |
| 23 | DEBT-DB-004 | pipeline_items.search_id TEXT vs UUID | Database | MED | 1-2h | Yes |
| 24 | DEBT-DB-010 | JSONB columns without size governance | Database | MED | 2h | Yes |
| 25 | DEBT-DB-009 | Stripe price IDs in migrations | Database | MED | 3-4h | No |
| 26 | DEBT-DB-008 | 85 migrations need squash baseline | Database | MED | 4-6h | No |
| 27 | DEBT-FE-003 | Inconsistent form handling patterns | Frontend | MED | 8h | No |
| 28 | DEBT-FE-004 | Framer Motion global load | Frontend | MED | 6h | No |
| 29 | DEBT-SYS-015 | API proxy factory underused | Frontend | MED | 4h | No |
| 30 | DEBT-SYS-016 | Large page files without decomposition | Frontend | MED | 4h | No |
| 31 | DEBT-DB-003 | profiles table too wide (20+ cols) | Database | MED | 8-12h | No |
| 32 | DEBT-FE-006 | Search hooks 3,287 LOC complexity | Frontend | MED | 4-24h | No |
| 33 | DEBT-FE-005 | 6 pages > 500 LOC | Frontend | MED | 16h | No |
| 34 | DEBT-SYS-011 | Test LOC 1.8x source LOC | Backend | MED | 8h | No |
| 35 | DEBT-FE-015 | BottomNav wrong Dashboard icon | Frontend | LOW | 0.5h | Yes |
| 36 | DEBT-DB-012 | organizations.plan_type CHECK permissive | Database | LOW | 0.5h | Yes |
| 37 | DEBT-DB-013 | reconciliation_log no retention | Database | LOW | 0.5h | Yes |
| 38 | DEBT-DB-014 | backend/migrations/ redundant | Database | LOW | 0.5h | Yes |
| 39 | DEBT-DB-015 | Legacy plans ON DELETE RESTRICT | Database | LOW | 0.5h | Yes |
| 40 | DEBT-DB-017 | pg_cron collision at 4:00 UTC | Database | LOW | 0.5h | Yes |
| 41 | DEBT-DB-016 | No CHECK on error_code | Database | LOW | 1h | No |
| 42 | DEBT-FE-012 | Feature-gated pages show broken state | Frontend | LOW | 2h | No |
| 43 | DEBT-FE-011 | Duplicate components across dirs | Frontend | LOW | 2h | No |
| 44 | DEBT-SYS-018 | Stale backend docs | Backend | LOW | 2h | No |
| 45 | DEBT-SYS-019 | Scripts not in CI test suite | Backend | LOW | 2h | No |
| 46 | DEBT-SYS-020 | startup/ module incomplete | Backend | LOW | 3h | No |
| 47 | DEBT-SYS-017 | No shared base class for clients | Backend | LOW | 4h | No |
| 48 | DEBT-FE-009 | Blog TODO placeholders (60+) | Frontend | LOW | 4h | No |
| 49 | DEBT-FE-016 | Raw CSS var() instead of Tailwind classes | Frontend | LOW | 4h | No |
| 50 | DEBT-FE-014 | EnhancedLoadingProgress 452 LOC | Frontend | LOW | 4h | No |
| 51 | DEBT-FE-013 | Missing skeleton loaders (5 pages) | Frontend | LOW | 4h | No |
| 52 | DEBT-DB-011 | search_sessions 24 columns | Database | LOW | 16+h | No |
| 53 | DEBT-FE-010 | No i18n infrastructure | Frontend | LOW | 80+h | No |
| 54 | DEBT-SYS-021 | blog.ts hardcoded content | Frontend | LOW | N/A | No |

**Quick wins total: ~18 items at < 4h, ~25h combined effort** -- these can be shipped in a single sprint with high impact.

---

## 6. Dependencias Entre Debitos

### 6.1 Dependency Chains

```
DEBT-SYS-001 (filter.py decomp)
  --> DEBT-SYS-012 (filter naming cleanup) -- do together as single refactor
  --> DEBT-SYS-004 (package grouping) -- filter/ package is part of broader restructuring

DEBT-SYS-004 (package grouping)
  --> DEBT-SYS-005 (job_queue/cron_jobs split) -- easier after package structure exists
  --> DEBT-SYS-006 (search_cache split) -- easier after search/ package exists
  --> DEBT-SYS-009 (quota.py split) -- easier after billing/ package exists
  --> DEBT-SYS-010 (main.py cleanup) -- easier after startup/ is the real entrypoint
  --> DEBT-SYS-020 (startup/ completion) -- prerequisite for main.py cleanup

DEBT-DB-001 (subscription status)
  --> DEBT-SYS-009 (quota.py) -- quota reads subscription status, must know canonical source
  --> DEBT-SYS-007 (stripe webhook) -- webhook writes subscription status

DEBT-DB-008 (migration squash)
  --> DEBT-DB-002 (classification_feedback FK) -- fix FK before squashing
  --> DEBT-DB-009 (stripe price IDs) -- extract before squashing
```

### 6.2 Recommended Execution Order

**Wave 1 -- Quick wins (week 1):**
All items marked "Quick Win" above. These are independent and can be parallelized across team members.

**Wave 2 -- Database hygiene (week 2):**
DEBT-DB-001 (subscription status) -> DEBT-DB-002 (FK fix) -> DEBT-DB-009 (price IDs) -> DEBT-DB-008 (migration squash)

**Wave 3 -- Backend restructuring (weeks 3-4):**
DEBT-SYS-004 (package grouping) -> DEBT-SYS-001 + DEBT-SYS-012 (filter refactor) -> DEBT-SYS-002 (schemas split) -> DEBT-SYS-005/006/009 (monolith splits)

**Wave 4 -- Frontend quality (weeks 4-5):**
DEBT-FE-003 (form consistency) -> DEBT-FE-004 (framer-motion lazy) -> DEBT-FE-005/SYS-016 (page decomposition) -> DEBT-FE-006 (search hooks docs)

### 6.3 Parallelizable Groups

These groups have no cross-dependencies and can run concurrently:

- **Group A (Backend):** DEBT-SYS-003 (sync/async cleanup), DEBT-SYS-013 (ComprasGov disable)
- **Group B (Database):** DEBT-DB-004 (search_id type), DEBT-DB-010 (JSONB limits)
- **Group C (Frontend):** DEBT-FE-001 (deps fix), DEBT-FE-002 (ARIA), DEBT-FE-008 (skip-link)

---

## 7. Riscos Cruzados

### 7.1 Security Risks (Cross-Stack)

| Risk | Debt Items | Severity | Description |
|------|-----------|----------|-------------|
| **Billing integrity** | DEBT-DB-001, DEBT-SYS-007, DEBT-SYS-009 | HIGH | Subscription status in 3 places (profiles, user_subscriptions, Stripe). Webhook handler is 1,192 LOC monolith. Quota logic reads from yet another cache. A billing bug could grant free access or block paying users. |
| **Disaster recovery** | DEBT-DB-002, DEBT-DB-008 | HIGH | Fresh migration replay may create wrong FK. 85 migrations with 7 handle_new_user redefinitions are fragile. Combined: DR scenario could leave database in inconsistent state. |
| **Staging environment safety** | DEBT-DB-009 | MEDIUM | Hardcoded Stripe production price IDs in migrations. Running migrations against staging could create real charges. |

### 7.2 Performance Risks (Cross-Stack)

| Risk | Debt Items | Severity | Description |
|------|-----------|----------|-------------|
| **Bundle size** | DEBT-SYS-008, DEBT-FE-004 | MEDIUM | api-types.generated.ts (5,177 LOC) + Framer Motion (~50KB) increase initial load. Combined with no lazy-loading strategy, FCP could degrade as app grows. |
| **Search pipeline latency** | DEBT-SYS-001, DEBT-SYS-003, DEBT-SYS-013 | MEDIUM | Monolithic filter.py is hard to profile. Sync requests fallback adds thread pool pressure. Dead ComprasGov source wastes timeout budget (up to 80s). |
| **Database query growth** | DEBT-DB-003, DEBT-DB-011 | LOW | profiles (20+ cols) and search_sessions (24 cols) are wide tables. At current scale this is acceptable, but both grow with every feature addition. |

### 7.3 Reliability Risks (Cross-Stack)

| Risk | Debt Items | Severity | Description |
|------|-----------|----------|-------------|
| **Test maintenance** | DEBT-SYS-011, DEBT-SYS-019 | MEDIUM | 140K test LOC (1.8x source) suggests duplication. Scripts not in CI. As codebase grows, test suite becomes slower and more brittle, reducing confidence in refactoring (which is needed for other debt items). |
| **Frontend error handling** | DEBT-FE-007, DEBT-FE-012 | MEDIUM | Missing error boundaries on onboarding/signup (critical user flows). Feature-gated pages show broken state instead of "coming soon". Combined: new users hitting errors during first experience have no recovery path. |
| **Accessibility compliance** | DEBT-FE-002, DEBT-FE-008 | MEDIUM | Core search form invisible to screen readers. Skip-link broken on all protected pages. If B2G customers have accessibility requirements (common in government-adjacent work), this blocks adoption. |

---

## 8. Perguntas para Especialistas

### Para @data-engineer:

1. **DEBT-DB-001 (subscription status):** The audit recommends documenting the mapping between profiles.subscription_status and user_subscriptions.subscription_status. Would you prefer (a) unifying the enum values to match, (b) adding a sync trigger, or (c) designating user_subscriptions as canonical and deprecating profiles.subscription_status? Option (c) requires changes to quota.py which reads from profiles.
2. **DEBT-DB-003 (profiles wide table):** The audit estimates 8-12h to extract billing/marketing columns. Given current user count (< 1K), is this worth doing now or should we defer until post-revenue? Are there any queries that are measurably slow today?
3. **DEBT-DB-008 (migration squash):** Creating a squash baseline is 4-6h. Is there a risk that the squash file itself becomes stale quickly? Would you recommend a CI check that validates the squash against the actual schema?
4. **DEBT-DB-009 (Stripe price IDs):** Do we have a staging Stripe account with separate price IDs? If not, the migration fix requires creating one first. What is the current staging workflow for billing?
5. **DEBT-DB-010 (JSONB limits):** The audit recommends CHECK constraints on 5 JSONB/TEXT columns. Are there any existing payloads that would violate a 256KB limit on stripe_webhook_events.payload? Should we measure actual payload sizes before setting limits?

### Para @ux-design-expert:

1. **DEBT-FE-002 (SearchForm ARIA):** Beyond role="search" and aria-label, should we implement aria-live="polite" on the results count, or is an aria-live region at the page level more appropriate? What is the priority vs fixing the skip-link (DEBT-FE-008)?
2. **DEBT-FE-003 (form consistency):** The audit estimates 8h to migrate login/recuperar-senha/redefinir-senha to react-hook-form + zod. This was noted as STORY-203 FE-M03 (pending). Should this be prioritized as a UX improvement (consistent validation) or deferred as technical debt?
3. **DEBT-FE-004 (Framer Motion):** Framer Motion is ~50KB gzipped and used in 9 files (mostly landing page). The 8 CSS animations in Tailwind config could replace some usages. Would removing framer-motion from non-landing pages degrade the perceived UX quality?
4. **DEBT-FE-005 (large pages):** Which of the 6 pages > 500 LOC would benefit most from decomposition for UX testing purposes? The onboarding wizard (783 LOC) seems highest priority given it is the first protected experience.
5. **DEBT-FE-012 (feature-gated pages):** Should the "Em breve" component match the existing empty state pattern, or should it be a distinctive "coming soon" design? Should it include a waitlist signup?
6. **DEBT-FE-013 (skeleton loaders):** Which pages have the worst perceived loading experience today? The audit suggests admin, conta, and planos. Do users actually notice, or is this low priority given the user base is small?

### Para @qa:

1. **DEBT-SYS-011 (test LOC ratio):** Before any debt reduction refactoring begins, should we audit for test duplication to reduce the test maintenance burden? A high test-to-source ratio can make refactoring expensive if tests are over-specified (testing implementation details rather than behavior).
2. **Regression risk:** The backend restructuring (Wave 3) touches filter.py, schemas.py, and the package structure. This affects nearly every import path. What is the recommended testing strategy -- snapshot the current test pass count and validate after each restructuring step?
3. **Quick wins validation:** The 18 quick-win items are individually low-risk, but applying all in one sprint creates cumulative change. Should we batch them into 2-3 PRs or ship individually?
4. **DEBT-FE-007 (error boundaries):** Can you confirm whether the existing E2E tests cover error scenarios on onboarding and signup pages? If not, should adding error boundaries also include E2E test coverage for those flows?
5. **Accessibility testing:** DEBT-FE-002 and DEBT-FE-008 are accessibility fixes. The frontend already has 2 axe-core Playwright specs. Should accessibility fixes be validated by extending those E2E specs, or is manual screen reader testing also required?

---

*Document generated 2026-03-21 by @architect (Atlas) during Brownfield Discovery Phase 4.*
*Consolidates findings from: system-architecture.md (21 items), DB-AUDIT.md (18 items), frontend-spec.md (16 items).*
*Next step: Specialist review by @data-engineer, @ux-design-expert, and @qa.*
