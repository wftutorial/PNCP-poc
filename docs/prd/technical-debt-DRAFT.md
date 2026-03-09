# Technical Debt Assessment - DRAFT

**Data:** 2026-03-09
**Status:** DRAFT — Pendente revisao dos especialistas
**Projeto:** SmartLic v0.5 (POC avancado em producao)
**Autor:** @architect (AIOS Brownfield Discovery Phase 4 — Initial Consolidation)

> **NOTA:** Esta auditoria PREVALECE sobre todas as analises anteriores (incluindo technical-debt-assessment.md de 2026-03-07 e quaisquer auditorias parciais anteriores). Todos os itens de debito foram re-catalogados com IDs unificados a partir das fontes primarias geradas nas Fases 1-3.

---

## Executive Summary

SmartLic is a production-grade B2G SaaS platform with 65+ backend modules, 47 frontend routes, 27 database tables, and comprehensive test suites (5131+ backend tests, 2681+ frontend tests). The codebase demonstrates strong engineering fundamentals — circuit breakers, two-level caching, LLM classification, RLS-protected database, and 11 CI/CD workflows. However, three phases of systematic brownfield discovery have surfaced **93 distinct technical debt items** across system architecture, database, and frontend/UX layers.

The debt profile breaks down as: **6 Critical** (production risk, security vulnerabilities, data integrity), **18 High** (performance, reliability, consistency gaps), **25 Medium** (maintainability, conventions, missing constraints), **22 Low** (cleanup, retention policies, minor inconsistencies), and **22 Informational** (best-practice recommendations and future-proofing). The most urgent cluster involves **database FK inconsistency** (CRIT-01) affecting 12 tables, **missing ON DELETE CASCADE** on 2+ tables blocking user deletion, and **5+ tables with unbounded growth** lacking retention policies. On the frontend, the monolithic `/buscar` page (983 LOC, 30+ imports) and absence of `next/dynamic` for heavy dependencies represent the largest performance and maintainability risks.

**Recommendation:** Address the 6 Critical items within this sprint (estimated 5 days total effort). Schedule the 18 High items for the next 2 sprints. The Medium/Low items should be addressed incrementally during regular feature work. Total estimated effort for all debt: ~45-55 engineering days, best tackled as a phased program over 2-3 months.

---

## 1. Debitos de Sistema (fonte: system-architecture.md)

### Critical

| ID | Descricao | Localizacao | Categoria | Severidade | Esforco |
|----|-----------|-------------|-----------|------------|---------|
| **SYS-001** | faulthandler enabled + uvicorn WITHOUT `[standard]` extra — uvloop crashes on Railway Linux containers (CRIT-SIGSEGV) | `main.py:1`, `requirements.txt:5` | Reliability | CRITICAL | 0.5d |
| **SYS-002** | LLM_STRUCTURED_MAX_TOKENS=300 causes JSON truncation in 20-30% of LLM calls (CRIT-038) | `llm_arbiter.py:61` | Reliability | CRITICAL | 0.5d |
| **SYS-003** | PNCP API reduced max tamanhoPagina 500→50 (Feb 2026); >50 causes silent HTTP 400 (CRIT-PNCP-PAGESIZE) | `pncp_client.py` | Compatibility | CRITICAL | 1d |
| **SYS-004** | Token hash uses partial payload instead of FULL SHA256 — token identity collision risk (CVSS 9.1) (STORY-210 AC3) | `auth.py:306` | Security | CRITICAL | 0.5d |
| **SYS-005** | ES256/JWKS JWT signing support + HS256 backward compat needed for algorithm rotation (STORY-227) | `auth.py:20` | Security | CRITICAL | 1d |

### High

| ID | Descricao | Localizacao | Categoria | Severidade | Esforco |
|----|-----------|-------------|-----------|------------|---------|
| **SYS-006** | Monolith main.py decomposition — extracted Sentry, lifespan, state to 3 modules but incomplete (DEBT-015 SYS-005) | `main.py:7`, `startup/` | Maintainability | HIGH | 2d |
| **SYS-007** | DB long-term optimization — 18 items including index bloat and N+1 queries (DEBT-017) | `backend/migrations/` | Performance | HIGH | 3d |
| **SYS-008** | `requests` library still needed for sync PNCPClient fallback; should fully migrate to httpx (DEBT-018 SYS-029) | `pncp_client.py`, `requirements.txt:19` | Maintainability | HIGH | 2d |
| **SYS-009** | Frontend advanced refactoring — 8 items outstanding (DEBT-016) | `frontend/app/` | Maintainability | HIGH | 2d |
| **SYS-010** | OpenAI client timeout=15s (5x p99) — risk of thread starvation on LLM hangs (HARDEN-001) | `llm_arbiter.py:35` | Performance | HIGH | 0.5d |
| **SYS-011** | Merge-enrichment from lower-priority duplicates not implemented (HARDEN-006) | `consolidation.py:760` | Correctness | HIGH | 1d |
| **SYS-012** | LRU cache unbounded — 5000 entry limit needed to prevent memory growth (HARDEN-009) | `llm_arbiter.py:74` | Performance | HIGH | 0.5d |
| **SYS-013** | Per-future timeout counter for LLM batch classification missing (HARDEN-014 AC4) | `llm_arbiter.py:123` | Observability | HIGH | 0.5d |
| **SYS-014** | Per-UF timeout (30s) + degraded mode (15s) for timeout cascade prevention (GTM-FIX-029) | `pncp_client.py:87-92` | Performance | HIGH | 0.5d |
| **SYS-015** | Phased UF batching (size=5, delay=2s) to reduce PNCP API pressure (GTM-FIX-031) | `pncp_client.py:96` | Performance | HIGH | 0.5d |

### Medium

| ID | Descricao | Localizacao | Categoria | Severidade | Esforco |
|----|-----------|-------------|-----------|------------|---------|
| **SYS-016** | Feature flag caching with lazy import — circular dependency prevention (STORY-171) | `filter.py:17` | Maintainability | MEDIUM | 1d |
| **SYS-017** | Lazy-load filter stats tracker to prevent circular imports (STORY-248 AC9) | `filter.py:22` | Correctness | MEDIUM | 0.5d |
| **SYS-018** | Circuit breaker pattern tuning (15 failures→60s cooldown) (STORY-252) | `pncp_client.py:38-103` | Reliability | MEDIUM | 1d |
| **SYS-019** | CB integration — when Supabase CB open, skip retries (STORY-291) | `authorization.py:39,91` | Reliability | MEDIUM | 0.5d |
| **SYS-020** | Cache fallback banner + stale banner logic complexity (STORY-293) | `search_cache.py` | Maintainability | MEDIUM | 1d |
| **SYS-021** | Redis L2 cache for cross-worker LLM sharing to reduce redundant calls (STORY-294 AC3) | `llm_arbiter.py:90` | Performance | MEDIUM | 0.5d |
| **SYS-022** | cryptography pin >=46.0.5,<47.0.0 — fork-safe with Gunicorn preload (STORY-303) | `requirements.txt:55` | Reliability | MEDIUM | 1d |
| **SYS-023** | Health canary every 5 min for source health tracking (STORY-316) | `cron_jobs.py:617` | Observability | MEDIUM | 0.5d |
| **SYS-024** | MFA (aal2) requirement + TOTP + recovery codes (STORY-317) | `auth.py:384,434` | Security | MEDIUM | 2d |
| **SYS-025** | Legacy route tracking — non-/v1/ deprecated endpoints still accessible (TD-004) | `main.py:217` | Maintainability | MEDIUM | 0.5d |
| **SYS-026** | Font preload optimization — skip display fonts to avoid blocking critical path (FE-020) | `frontend/app/layout.tsx:31` | Performance | MEDIUM | 0.5d |
| **SYS-027** | chardet<6 pin (requests<=2.32.5 incompatible with chardet 6.0.0) — remove once requests>=2.33.0 ships (CHARDET-PIN) | `requirements.txt:26` | Reliability | MEDIUM | 0.5d |
| **SYS-028** | pytest timeout_method="thread" required for Windows dev compatibility (PYTEST-TIMEOUT-WINDOWS) | `pyproject.toml` | Reliability | MEDIUM | 0.5d |
| **SYS-029** | Three-layer migration defense operational but could fail silently on edge cases (CRIT-050) | `.github/workflows/` | Reliability | MEDIUM | 1d |
| **SYS-030** | Search filter complexity — filter.py is 177KB monolithic file, hard to test | `filter.py` | Maintainability | MEDIUM | 2d |
| **SYS-031** | Database query performance — N+1 patterns in analytics queries | `routes/analytics.py` | Performance | MEDIUM | 1d |
| **SYS-032** | LLM cost optimization — could use cheaper models for low-stakes classifications | `llm_arbiter.py` | Cost | MEDIUM | 1d |

### Low

| ID | Descricao | Localizacao | Categoria | Severidade | Esforco |
|----|-----------|-------------|-----------|------------|---------|
| **SYS-033** | Backward-compatible aliases for quota functions — old imports still work (STORY-226 AC8) | `authorization.py:172` | Maintainability | LOW | 0.5d |
| **SYS-034** | Trial reminder emails — legacy dead code, replaced by STORY-310 sequence (STORY-266) | `cron_jobs.py:736` | Code Quality | LOW | 0.5d |
| **SYS-035** | Per-user Supabase tokens for user-scoped operations — should verify all routes (SYS-023) | `database.py:12` | Security | LOW | 1d |
| **SYS-036** | OpenAPI docs protected by DOCS_ACCESS_TOKEN in production — hardened API docs access (SYS-036) | `main.py:13,91-167` | Security | LOW | 0.5d |
| **SYS-037** | Terms NEVER in both `valid` AND `ignored` — critical invariant with assert on violation | `filter.py:68,138` | Correctness | LOW | 0.5d |

---

## 2. Debitos de Database (fonte: DB-AUDIT.md)

> ⚠️ **PENDENTE:** Revisao do @data-engineer

### Critical

| ID | Descricao | Tabelas Afetadas | Severidade | Esforco |
|----|-----------|------------------|------------|---------|
| **DB-001** | FK Target Inconsistency — `auth.users` vs `profiles`. 12 tables reference user IDs with mixed targets. If `profiles` row creation fails, partial state results. | 12 of 27 tables | CRITICAL | Medium (careful migration with FK recreation) |
| **DB-002** | `search_results_store.user_id` FK missing ON DELETE CASCADE — user deletion blocked or orphaned rows | `search_results_store` | CRITICAL | Low (single ALTER TABLE) |

### High

| ID | Descricao | Tabelas Afetadas | Severidade | Esforco |
|----|-----------|------------------|------------|---------|
| **DB-003** | `classification_feedback.user_id` missing ON DELETE CASCADE — same impact as DB-002 | `classification_feedback` | HIGH | Low |
| **DB-004** | Duplicate `updated_at` trigger functions — `pipeline_items`, `alert_preferences`, `alerts` still use dedicated functions instead of shared `set_updated_at()` | 3 tables | HIGH | Low |
| **DB-005** | `search_state_transitions.search_id` has no FK constraint — orphaned transitions accumulate indefinitely, no retention cleanup | `search_state_transitions` | HIGH | Low |
| **DB-006** | `alert_preferences` service role policy uses old `auth.role() = 'service_role'` pattern instead of `TO service_role` | `alert_preferences` | HIGH | Low |
| **DB-007** | `organizations` and `organization_members` service role uses old `auth.role()` pattern | `organizations`, `organization_members` | HIGH | Low |
| **DB-008** | `partners` and `partner_referrals` service role uses old `auth.role()` pattern | `partners`, `partner_referrals` | HIGH | Low |
| **DB-009** | `search_results_store` service role uses old `auth.role()` pattern | `search_results_store` | HIGH | Low |
| **DB-010** | `health_checks` and `incidents` missing retention jobs — unbounded table growth (comment says 30-day retention but no pg_cron exists) | `health_checks`, `incidents` | HIGH | Low |

### Medium

| ID | Descricao | Tabelas Afetadas | Severidade | Esforco |
|----|-----------|------------------|------------|---------|
| **DB-011** | Redundant indexes wasting storage and slowing writes on 4 tables (`alert_preferences`, `search_results_store`, `search_sessions`, `partners`) | 4 tables | MEDIUM | Low |
| **DB-012** | `conversations` missing composite index for admin inbox (status + last_message_at DESC) | `conversations` | MEDIUM | Low |
| **DB-013** | `plans.stripe_price_id` legacy column still used as fallback in `billing.py` despite being DEPRECATED | `plans` | MEDIUM | Medium |
| **DB-014** | `search_sessions.status` CHECK constraint mismatch — `consolidating` and `partial` states documented but not in CHECK | `search_sessions` | MEDIUM | Low |
| **DB-015** | `monthly_quota.user_id` references `auth.users` not `profiles` — inconsistency (part of DB-001) | `monthly_quota` | MEDIUM | Low |
| **DB-016** | Missing `updated_at` on mutable tables: `incidents` and `partners` (both have UPDATE operations but no change tracking) | `incidents`, `partners` | MEDIUM | Low |
| **DB-017** | `search_results_cache` duplicate size constraints — verify no duplicate CHECK in production | `search_results_cache` | MEDIUM | Low |
| **DB-018** | `partner_referrals.partner_id` missing ON DELETE CASCADE — partner deletion blocked | `partner_referrals` | MEDIUM | Low |
| **DB-019** | Naming convention inconsistencies — triggers use `tr_`, `trg_`, `trigger_`, or no prefix | Project-wide | MEDIUM | Low |
| **DB-020** | `google_sheets_exports` uses `last_updated_at` instead of `updated_at` convention, no trigger attached | `google_sheets_exports` | MEDIUM | Low |
| **DB-021** | `organizations.plan_type` has no CHECK constraint — accepts any text value | `organizations` | MEDIUM | Low |
| **DB-022** | `pipeline_items` service role policy was overly permissive (fixed in migration 027 but should be verified) | `pipeline_items` | MEDIUM | Low |

### Low

| ID | Descricao | Tabelas Afetadas | Severidade | Esforco |
|----|-----------|------------------|------------|---------|
| **DB-023** | `user_oauth_tokens.provider` CHECK allows `google, microsoft, dropbox` but only Google implemented | `user_oauth_tokens` | LOW | Low |
| **DB-024** | `audit_events` no index on `details` JSONB — future-proofing concern only | `audit_events` | LOW | Low |
| **DB-025** | `search_results_cache` has 8 indexes — write amplification on INSERT/UPDATE | `search_results_cache` | LOW | Low-Medium |
| **DB-026** | `search_sessions` accumulating without retention — unbounded growth | `search_sessions` | LOW | Low |
| **DB-027** | `classification_feedback` accumulating without retention | `classification_feedback` | LOW | Low |
| **DB-028** | `conversations` and `messages` no retention policy — indefinite accumulation | `conversations`, `messages` | LOW | Low |
| **DB-029** | `alert_sent_items` missing retention — dedup records grow with active alerts | `alert_sent_items` | LOW | Low |
| **DB-030** | `stripe_webhook_events` no automated retention (comment says 90 days but no pg_cron) | `stripe_webhook_events` | LOW | Low |
| **DB-031** | `pipeline_items` missing `search_id` reference — cannot trace which search led to pipeline addition | `pipeline_items` | LOW | Low |

### Info

| ID | Descricao | Severidade |
|----|-----------|------------|
| **DB-INFO-01** | Consolidate backend migrations directory (fully redundant after DEBT-002 bridge) | INFO |
| **DB-INFO-02** | No schema version table — consider adding independent tracking | INFO |
| **DB-INFO-03** | Backup strategy not documented (Supabase daily backups exist but PITR window undocumented) | INFO |
| **DB-INFO-04** | Connection pooling — verify pgbouncer (port 6543) is correctly configured | INFO |
| **DB-INFO-05** | Consider partitioning for high-volume tables when they exceed 10M rows | INFO |
| **DB-INFO-06** | JSONB columns lack database-level schema validation (app-level Pydantic handles it) | INFO |

---

## 3. Debitos de Frontend/UX (fonte: frontend-spec.md)

> ⚠️ **PENDENTE:** Revisao do @ux-expert

### Critical

| ID | Descricao | Localizacao | Severidade | Esforco |
|----|-----------|-------------|------------|---------|
| **FE-001** | `/buscar/page.tsx` is ~983 lines with 30+ imports — monolithic client component, no sub-component splitting | `app/buscar/page.tsx` | CRITICAL | Large (2-3d) |
| **FE-002** | No `next/dynamic` usage for heavy dependencies (Recharts ~50KB, @dnd-kit ~30KB, Shepherd.js ~25KB, framer-motion ~70KB) | Multiple pages | CRITICAL | Medium (1d) |
| **FE-003** | SSE proxy complexity — custom SSE handling with fallback simulation, multiple retry strategies, hard to maintain | `hooks/useSearchSSE.ts`, `app/api/buscar-progress/route.ts` | CRITICAL | Large (3-5d) |

### High

| ID | Descricao | Localizacao | Severidade | Esforco |
|----|-----------|-------------|------------|---------|
| **FE-004** | Test coverage thresholds at 50-55% (target 60%, ideal 80%) | `jest.config.js` | HIGH | Ongoing |
| **FE-005** | No `prefers-reduced-motion` media query for 8 custom animations | `tailwind.config.ts`, `globals.css` | HIGH | 0.5d |
| **FE-006** | Dual component directories (`app/components/` 46 files + `components/` 49 files) with unclear ownership boundaries | Project-wide | HIGH | 1-2d |
| **FE-007** | `aria-live` missing on dynamic content updates (search results, SSE progress) — screen readers not notified | `app/buscar/components/SearchResults.tsx`, progress components | HIGH | 0.5d |
| **FE-008** | localStorage used directly in many places without centralized abstraction (despite `lib/storage.ts` existing) | Multiple hooks/components | HIGH | 1d |
| **FE-009** | Inline SVGs throughout codebase instead of centralized icon system | `app/planos/page.tsx`, `components/Sidebar.tsx` | HIGH | 1d |
| **FE-010** | `'unsafe-inline'` and `'unsafe-eval'` in CSP script-src — security risk | `middleware.ts` | HIGH | 1-2d |

### Medium

| ID | Descricao | Localizacao | Severidade | Esforco |
|----|-----------|-------------|------------|---------|
| **FE-011** | No page-level tests for dashboard, pipeline, historico, onboarding, conta sub-pages | `__tests__/` | MEDIUM | 2-3d |
| **FE-012** | `eslint-disable-next-line react-hooks/exhaustive-deps` used 5+ times in buscar | `app/buscar/page.tsx` | MEDIUM | 0.5d |
| **FE-013** | Hardcoded pricing fallback in `planos/page.tsx` must be kept in sync with Stripe | `app/planos/page.tsx` | MEDIUM | Ongoing |
| **FE-014** | Feature-gated code (ORGS_ENABLED, alertas, mensagens) still shipped in production bundles | Multiple files | MEDIUM | 1d |
| **FE-015** | No bundle size monitoring/budget in CI (Lighthouse CI configured but not enforced) | `.lighthouserc.js` (missing?) | MEDIUM | 0.5d |
| **FE-016** | Multiple footer implementations (buscar page inline + NavigationShell footer) | `app/buscar/page.tsx`, `components/NavigationShell.tsx` | MEDIUM | 0.5d |
| **FE-017** | Theme initialization script in `<head>` via `dangerouslySetInnerHTML` | `app/layout.tsx` | MEDIUM | Low priority |
| **FE-018** | Raw `var(--*)` CSS usage alongside Tailwind tokens in many components | Project-wide | MEDIUM | Ongoing |

### Low

| ID | Descricao | Localizacao | Severidade | Esforco |
|----|-----------|-------------|------------|---------|
| **FE-019** | `@types/uuid` in dependencies (should be devDependencies) | `package.json` | LOW | Trivial |
| **FE-020** | `__tests__/e2e/` directory exists alongside `e2e-tests/` (two E2E locations) | Test directories | LOW | 0.5d |
| **FE-021** | No Storybook or component documentation system | Project-wide | LOW | 3-5d |
| **FE-022** | `Button.examples.tsx` exists but no visual regression testing framework | `components/ui/Button.examples.tsx` | LOW | 1-2d |

### Accessibility Gaps (from frontend-spec.md Section 8)

| ID | Descricao | Localizacao | Severidade | Esforco |
|----|-----------|-------------|------------|---------|
| **FE-A11Y-01** | Loading announcements — spinners use visual-only indicators without `aria-busy` or `role="status"` | Multiple loading components | MEDIUM | 0.5d |
| **FE-A11Y-02** | `SearchErrorBoundary` catches errors but does not announce to assistive technology | `app/buscar/components/SearchErrorBoundary.tsx` | MEDIUM | 0.5d |
| **FE-A11Y-03** | Some inline SVGs (pricing page) lack `aria-hidden="true"` | `app/planos/page.tsx` | LOW | Trivial |
| **FE-A11Y-04** | Dialog focus trap (`focus-trap-react` installed but usage consistency unconfirmed across all modals) | Multiple modals | MEDIUM | 1d |
| **FE-A11Y-05** | Landmark duplication — multiple `<footer>` elements may confuse landmark navigation | `app/buscar/page.tsx`, `NavigationShell.tsx` | LOW | 0.5d |
| **FE-A11Y-06** | Color-only indicators — some viability/source badges rely partially on color alone | Badge components | MEDIUM | 1d |
| **FE-A11Y-07** | Keyboard navigation — not all modal closures respond to Escape key consistently | Multiple modals | MEDIUM | 0.5d |

---

## 4. Matriz Preliminar de Priorizacao

Items ranked by: (Severity weight x Impact) / Effort. Severity weights: CRITICAL=4, HIGH=3, MEDIUM=2, LOW=1.

| # | ID | Debito | Area | Severidade | Esforco | Prioridade Preliminar |
|---|-----|--------|------|------------|---------|----------------------|
| 1 | SYS-004 | Token hash uses partial payload — CVSS 9.1 collision risk | Backend/Security | CRITICAL | 0.5d | **P0 — Immediate** |
| 2 | DB-002 | `search_results_store` missing ON DELETE CASCADE | Database | CRITICAL | Low | **P0 — Immediate** |
| 3 | DB-003 | `classification_feedback` missing ON DELETE CASCADE | Database | HIGH | Low | **P0 — Immediate** |
| 4 | SYS-001 | faulthandler + uvicorn crash on Railway (SIGSEGV) | Backend/Infra | CRITICAL | 0.5d | **P0 — Immediate** |
| 5 | SYS-002 | LLM JSON truncation in 20-30% of calls | Backend/AI | CRITICAL | 0.5d | **P0 — Immediate** |
| 6 | DB-010 | `health_checks`/`incidents` missing retention jobs | Database | HIGH | Low | **P0 — Immediate** |
| 7 | DB-005 | `search_state_transitions` no retention cleanup | Database | HIGH | Low | **P0 — Immediate** |
| 8 | DB-030 | `stripe_webhook_events` no automated retention | Database | LOW | Low | **P0 — Immediate** |
| 9 | SYS-005 | JWT ES256/JWKS algorithm rotation needed | Backend/Security | CRITICAL | 1d | **P1 — This Sprint** |
| 10 | SYS-003 | PNCP API silent 400 on >50 page size | Backend/Integration | CRITICAL | 1d | **P1 — This Sprint** |
| 11 | DB-001 | FK target inconsistency (auth.users vs profiles) across 12 tables | Database | CRITICAL | Medium | **P1 — This Sprint** |
| 12 | FE-010 | `unsafe-inline`/`unsafe-eval` in CSP script-src | Frontend/Security | HIGH | 1-2d | **P1 — This Sprint** |
| 13 | FE-005 | No `prefers-reduced-motion` for animations | Frontend/A11Y | HIGH | 0.5d | **P1 — This Sprint** |
| 14 | FE-007 | `aria-live` missing on dynamic updates | Frontend/A11Y | HIGH | 0.5d | **P1 — This Sprint** |
| 15 | SYS-010 | OpenAI client timeout thread starvation risk | Backend/Performance | HIGH | 0.5d | **P1 — This Sprint** |
| 16 | SYS-012 | LRU cache unbounded memory growth | Backend/Performance | HIGH | 0.5d | **P1 — This Sprint** |
| 17 | DB-006 | `alert_preferences` auth.role() pattern | Database | HIGH | Low | **P2 — Next Sprint** |
| 18 | DB-007 | `organizations`/`organization_members` auth.role() pattern | Database | HIGH | Low | **P2 — Next Sprint** |
| 19 | DB-008 | `partners`/`partner_referrals` auth.role() pattern | Database | HIGH | Low | **P2 — Next Sprint** |
| 20 | DB-009 | `search_results_store` auth.role() pattern | Database | HIGH | Low | **P2 — Next Sprint** |
| 21 | DB-004 | Duplicate updated_at trigger functions (3 tables) | Database | HIGH | Low | **P2 — Next Sprint** |
| 22 | DB-011 | Redundant indexes on 4 tables | Database | MEDIUM | Low | **P2 — Next Sprint** |
| 23 | DB-018 | `partner_referrals.partner_id` missing ON DELETE | Database | MEDIUM | Low | **P2 — Next Sprint** |
| 24 | SYS-008 | requests library → httpx migration (DEBT-018) | Backend/Maintainability | HIGH | 2d | **P2 — Next Sprint** |
| 25 | FE-001 | `/buscar` monolithic 983 LOC page | Frontend/Maintainability | CRITICAL | 2-3d | **P2 — Next Sprint** |
| 26 | FE-002 | No `next/dynamic` for heavy deps (~175KB) | Frontend/Performance | CRITICAL | 1d | **P2 — Next Sprint** |
| 27 | FE-006 | Dual component directories unclear ownership | Frontend/Architecture | HIGH | 1-2d | **P2 — Next Sprint** |
| 28 | SYS-006 | main.py monolith decomposition incomplete | Backend/Maintainability | HIGH | 2d | **P2 — Next Sprint** |
| 29 | SYS-011 | Merge-enrichment from lower-priority duplicates | Backend/Correctness | HIGH | 1d | **P2 — Next Sprint** |
| 30 | SYS-013 | Per-future timeout counter missing for LLM batch | Backend/Observability | HIGH | 0.5d | **P2 — Next Sprint** |
| 31 | SYS-014 | Per-UF timeout + degraded mode | Backend/Performance | HIGH | 0.5d | **P2 — Next Sprint** |
| 32 | SYS-015 | Phased UF batching | Backend/Performance | HIGH | 0.5d | **P2 — Next Sprint** |
| 33 | FE-003 | SSE proxy complexity | Frontend/Maintainability | CRITICAL | 3-5d | **P3 — Planned** |
| 34 | FE-004 | Test coverage 50-55% (target 60%) | Frontend/Quality | HIGH | Ongoing | **P3 — Planned** |
| 35 | FE-008 | localStorage not centralized | Frontend/Maintainability | HIGH | 1d | **P3 — Planned** |
| 36 | FE-009 | Inline SVGs instead of icon system | Frontend/Maintainability | HIGH | 1d | **P3 — Planned** |
| 37 | DB-013 | plans.stripe_price_id legacy column | Database | MEDIUM | Medium | **P3 — Planned** |
| 38 | DB-014 | search_sessions.status CHECK mismatch | Database | MEDIUM | Low | **P3 — Planned** |
| 39 | DB-019 | Trigger naming convention inconsistencies | Database | MEDIUM | Low | **P3 — Planned** |
| 40 | DB-020 | google_sheets_exports.last_updated_at naming | Database | MEDIUM | Low | **P3 — Planned** |
| 41 | DB-021 | organizations.plan_type no CHECK constraint | Database | MEDIUM | Low | **P3 — Planned** |
| 42 | DB-016 | Missing updated_at on incidents/partners | Database | MEDIUM | Low | **P3 — Planned** |
| 43 | SYS-016 | Feature flag caching circular deps | Backend | MEDIUM | 1d | **P3 — Planned** |
| 44 | SYS-018 | Circuit breaker tuning | Backend | MEDIUM | 1d | **P3 — Planned** |
| 45 | SYS-024 | MFA implementation completion | Backend/Security | MEDIUM | 2d | **P3 — Planned** |
| 46 | SYS-030 | filter.py 177KB monolith | Backend | MEDIUM | 2d | **P3 — Planned** |
| 47 | SYS-031 | Analytics N+1 queries | Backend | MEDIUM | 1d | **P3 — Planned** |
| 48 | SYS-032 | LLM cost optimization | Backend | MEDIUM | 1d | **P3 — Planned** |
| 49 | FE-011 | Missing page-level tests (5 pages) | Frontend | MEDIUM | 2-3d | **P3 — Planned** |
| 50 | FE-012 | eslint-disable exhaustive-deps (5+) | Frontend | MEDIUM | 0.5d | **P3 — Planned** |
| 51 | FE-014 | Feature-gated dead code in bundles | Frontend | MEDIUM | 1d | **P3 — Planned** |
| 52 | FE-015 | No bundle size budget in CI | Frontend | MEDIUM | 0.5d | **P3 — Planned** |
| 53 | FE-016 | Duplicate footer implementations | Frontend | MEDIUM | 0.5d | **P3 — Planned** |
| 54 | FE-A11Y-01 | Loading: no aria-busy/role="status" | Frontend/A11Y | MEDIUM | 0.5d | **P3 — Planned** |
| 55 | FE-A11Y-02 | Error boundary not announced to AT | Frontend/A11Y | MEDIUM | 0.5d | **P3 — Planned** |
| 56 | FE-A11Y-04 | Focus trap consistency across modals | Frontend/A11Y | MEDIUM | 1d | **P3 — Planned** |
| 57 | FE-A11Y-06 | Color-only status indicators | Frontend/A11Y | MEDIUM | 1d | **P3 — Planned** |
| 58 | FE-A11Y-07 | Escape key inconsistency in modals | Frontend/A11Y | MEDIUM | 0.5d | **P3 — Planned** |
| 59-93 | All LOW/INFO items | Various minor cleanup, retention policies, conventions | All | LOW/INFO | Varies | **P4 — Backlog** |

---

## 5. Dependencias entre Debitos

### Dependency Chains

```
DB-001 (FK standardization) ──blocks──> DB-015 (monthly_quota FK)
                             ──blocks──> DB-002 (search_results_store cascade)
                             ──blocks──> DB-003 (classification_feedback cascade)
  Note: DB-002 and DB-003 can be fixed independently of DB-001 by adding
  CASCADE to existing auth.users FKs, but full standardization requires DB-001 first.

SYS-008 (httpx migration) ──enables──> SYS-027 (chardet pin removal)
                           ──enables──> SYS-001 (uvloop fix, if requests removed)

FE-001 (buscar split) ──enables──> FE-002 (dynamic imports per sub-component)
                       ──enables──> FE-012 (fix exhaustive-deps after extraction)
                       ──enables──> FE-016 (footer dedup after extraction)

FE-006 (component directory consolidation) ──enables──> FE-009 (centralized icons)
                                            ──enables──> FE-021 (Storybook)

DB-006 + DB-007 + DB-008 + DB-009 (auth.role() standardization)
  All independent, can be done in a single migration batch.

DB-005 + DB-010 + DB-026 + DB-027 + DB-028 + DB-029 + DB-030 (retention jobs)
  All independent, can be done in a single pg_cron setup migration.

SYS-010 (OpenAI timeout) ──related──> SYS-012 (LRU cache bounds)
                          ──related──> SYS-013 (timeout metrics)
  All three address LLM subsystem resilience — best done together.

FE-005 (reduced-motion) ──independent
FE-007 (aria-live) ──independent
FE-010 (CSP nonces) ──independent (but complex)
```

### Recommended Batches

| Batch | Items | Theme | Combined Effort |
|-------|-------|-------|-----------------|
| **Batch A: User Deletion** | DB-002, DB-003 | Fix FK cascades blocking user deletion | 0.5d |
| **Batch B: Retention** | DB-005, DB-010, DB-026, DB-027, DB-028, DB-029, DB-030 | Add pg_cron retention for 7 tables | 1d |
| **Batch C: auth.role() Standardization** | DB-006, DB-007, DB-008, DB-009 | Single migration for 6 tables | 0.5d |
| **Batch D: LLM Resilience** | SYS-010, SYS-012, SYS-013 | OpenAI timeout + cache bounds + metrics | 1.5d |
| **Batch E: A11Y Quick Wins** | FE-005, FE-007, FE-A11Y-01, FE-A11Y-03 | Accessibility improvements | 1.5d |
| **Batch F: Buscar Refactor** | FE-001, FE-002, FE-012, FE-016 | Split monolith + dynamic imports | 3-4d |

---

## 6. Perguntas para Especialistas

### Para @data-engineer:

1. **DB-001 (FK Standardization):** Should all FKs target `auth.users(id)` or `profiles(id)`? The partial migration in `20260304100000_fk_standardization_to_profiles.sql` chose `profiles`. Is this the confirmed direction, and which of the 12 tables have NOT been migrated yet?

2. **DB-005 (search_state_transitions):** Is 90 days the right retention window for state transitions? Are any analytics or debugging queries dependent on older transitions?

3. **DB-010 (health_checks retention):** The 30-day retention was commented but never implemented. Is there a compliance or operational reason this was deferred?

4. **DB-013 (plans.stripe_price_id legacy):** What is the migration path for `billing.py` to stop using this column? Does the billing service have a rollback path if we drop it?

5. **DB-014 (search_sessions status CHECK):** Are `consolidating` and `partial` actually used as database values, or are they only in-memory states? If in-memory only, the CHECK is correct as-is and the documentation should be updated.

6. **DB-025 (search_results_cache 8 indexes):** Which indexes are actually hit by production queries? Can we get query plans from production to identify redundant indexes?

7. **DB-INFO-04 (Connection pooling):** Is the backend connecting through pgbouncer (port 6543) or directly (port 5432)? What is the current max connections setting?

8. **Retention batch (DB-005, DB-010, DB-026-030):** Can all 7 retention jobs be consolidated into a single migration? What are the appropriate retention windows per table?

### Para @ux-expert:

1. **FE-001 (buscar page 983 LOC):** From a UX perspective, which sub-sections of the search page should be independently loadable? Is there a natural "above the fold" split that would benefit perceived performance?

2. **FE-005 (prefers-reduced-motion):** Which of the 8 animations are essential to the UX (should still animate, just simplified) vs. purely decorative (should be disabled entirely)?

3. **FE-006 (dual component directories):** What is the intended ownership boundary? Proposed rule: `components/` = truly global (3+ pages), `app/components/` = app-shared (2+ authenticated pages), page-local = 1 page only. Does this align with UX patterns?

4. **FE-007 (aria-live):** What is the expected screen reader experience during a search? Should progress updates be announced individually, or only the final "X results found" message?

5. **FE-A11Y-06 (color-only indicators):** Which badges/indicators need redesign? ViabilityBadge, LlmSourceBadge, ReliabilityBadge — should they all include text labels or icon-based alternatives?

6. **FE-016 (duplicate footers):** Should the buscar page have its own footer, or should it use the global NavigationShell footer exclusively?

7. **FE-021 (Storybook):** Is Storybook the right tool for this project size, or would a lighter solution (e.g., Ladle, Histoire) be more appropriate for the current scale (~130 components)?

### Para @qa:

1. **FE-004 (coverage 50-55%):** Which modules have the lowest coverage? Are there any critical paths (billing, auth, search) below 40% that should be prioritized?

2. **FE-011 (missing page tests):** What is the minimum viable test suite for `/dashboard`, `/pipeline`, `/historico`? Should we focus on render tests or interaction tests?

3. **FE-003 (SSE complexity):** The SSE proxy has multiple fallback paths. What is the current E2E test coverage for SSE failure modes (timeout, disconnect, invalid data)?

4. **Backend test anti-hang:** Have there been any recent test hang incidents on Windows? Is the `timeout_method="thread"` sufficient, or do we need additional safeguards?

5. **Integration test gaps:** The backend has 30 integration test files. Are there any API contracts (especially billing webhooks, OAuth flows) that lack integration coverage?

6. **FE-A11Y testing:** The `@axe-core/playwright` dependency exists but is it actively used in the 21 E2E specs? How many specs run accessibility audits?

7. **Regression risk:** Which of the P0/P1 debt items have the highest risk of introducing regressions when fixed? Should we add targeted regression tests before fixing them?

---

## Appendix: Previously Fixed Items (for reference)

These were identified in earlier audits and resolved in recent DEBT migrations:

| ID | Issue | Fixed In |
|----|-------|----------|
| DB-013 (old) | `partner_referrals.referred_user_id` NOT NULL vs ON DELETE SET NULL | `20260308100000_debt001` |
| DB-038 (old) | Wrong table names in index migration | `20260308100000_debt001` |
| DB-012 (old) | Duplicate `updated_at` trigger functions (partial fix) | `20260308100000_debt001` |
| DB-001 (old) | `classification_feedback` auth.role() pattern | `20260308300000_debt009` |
| DB-002 (old) | `health_checks`/`incidents` missing service_role policies | `20260308300000_debt009` |
| DB-014 (old) | `plans.stripe_price_id` deprecated column (documented) | `20260309100000_debt017` |
| DB-034 (old) | Cache cleanup trigger performance | `20260309100000_debt017` |
| DB-035 (old) | Conversations correlated subquery | `20260309100000_debt017` |

---

*Generated by @architect during Brownfield Discovery Phase 4 — Initial Consolidation*
*Sources: system-architecture.md (Phase 1), DB-AUDIT.md (Phase 2), frontend-spec.md (Phase 3)*
*Next step: Specialist review by @data-engineer, @ux-expert, and @qa*
