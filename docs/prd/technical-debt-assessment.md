# Technical Debt Assessment - FINAL

**Projeto:** SmartLic (smartlic.tech)
**Data:** 2026-03-09
**Versao:** 1.0 (FINAL -- prevalece sobre todas as analises anteriores)
**Autores:** @architect (lead), @data-engineer, @ux-design-expert, @qa

> **NOTA:** Este documento e a unica fonte de verdade para debito tecnico do SmartLic. Substitui completamente `technical-debt-DRAFT.md` (Phase 4), `technical-debt-assessment.md` (2026-03-07), e todas as auditorias parciais anteriores. Todos os itens foram validados cruzando as revisoes dos especialistas (Phases 5-7) contra o codebase no commit `3c71ce93`.

---

## Executive Summary

SmartLic is a production-grade B2G SaaS platform with 65+ backend modules, 22 frontend pages, 27 database tables, and comprehensive test suites (5131+ backend tests, 2681+ frontend tests, 21 E2E specs). Three phases of systematic brownfield discovery surfaced 93 candidate debt items. After specialist validation by @data-engineer (Phase 5), @ux-design-expert (Phase 6), and @qa (Phase 7):

- **10 DB items confirmed resolved** by recent DEBT migrations (2026-03-04 to 2026-03-09)
- **3 FE items confirmed resolved** by recent accessibility/animation fixes
- **4 new DB items identified** during specialist cross-reference
- **4 new FE items identified** during UX codebase validation
- **5 new QA items identified** during cross-cutting gap analysis
- **5 severity adjustments** applied based on specialist evidence

**Totals ativos:**

| Severidade | Backend/SYS | Database | Frontend/UX | QA | Total |
|:---:|:---:|:---:|:---:|:---:|:---:|
| CRITICAL | 5 | 0 | 0 | 0 | **5** |
| HIGH | 10 | 2 | 5 | 2 | **19** |
| MEDIUM | 17 | 7 | 14 | 3 | **41** |
| LOW | 5 | 9 | 9 | 1 | **24** |
| INFO | 0 | 3 | 0 | 0 | **3** |
| **Subtotal** | **37** | **21** | **28** | **6** | **92** |

- **Debitos ativos:** 80 (excluindo 3 INFO e 9 items resolvidos nao contabilizados acima)
- **Esforco total estimado:** ~340 horas (~42.5 dias de engenharia)
- **Itens ja resolvidos por migracoes recentes:** 16 (13 DB + 3 FE)

---

## Inventario Completo de Debitos

### Sistema/Backend (validado por @architect)

| ID | Debito | Severidade | Horas | Prioridade | Status |
|----|--------|:---:|:---:|:---:|:---:|
| **SYS-001** | faulthandler enabled + uvicorn WITHOUT `[standard]` extra -- uvloop crashes on Railway Linux containers (CRIT-SIGSEGV) | CRITICAL | 4h | P0 | Ativo |
| **SYS-002** | LLM_STRUCTURED_MAX_TOKENS=300 causes JSON truncation in 20-30% of LLM calls (CRIT-038) | CRITICAL | 4h | P0 | Ativo |
| **SYS-003** | PNCP API reduced max tamanhoPagina 500->50 (Feb 2026); >50 causes silent HTTP 400 | CRITICAL | 8h | P1 | Ativo |
| **SYS-004** | Token hash uses partial payload instead of FULL SHA256 -- token identity collision risk (CVSS 9.1) | CRITICAL | 4h | P0 | Ativo |
| **SYS-005** | ES256/JWKS JWT signing support + HS256 backward compat needed for algorithm rotation | CRITICAL | 8h | P1 | Ativo |
| **SYS-006** | Monolith main.py decomposition -- extracted Sentry, lifespan, state to 3 modules but incomplete | HIGH | 16h | P2 | Ativo |
| **SYS-007** | DB long-term optimization -- 18 items including index bloat and N+1 queries (DEBT-017) | HIGH | 24h | P2 | Ativo |
| **SYS-008** | `requests` library still needed for sync PNCPClient fallback; should fully migrate to httpx | HIGH | 16h | P2 | Ativo |
| **SYS-009** | Frontend advanced refactoring -- 8 items outstanding (DEBT-016) | HIGH | 16h | P2 | Ativo |
| **SYS-010** | OpenAI client timeout=15s (5x p99) -- risk of thread starvation on LLM hangs | HIGH | 4h | P1 | Ativo |
| **SYS-011** | Merge-enrichment from lower-priority duplicates not implemented | HIGH | 8h | P2 | Ativo |
| **SYS-012** | LRU cache unbounded -- 5000 entry limit needed to prevent memory growth | HIGH | 4h | P1 | Ativo |
| **SYS-013** | Per-future timeout counter for LLM batch classification missing | HIGH | 4h | P2 | Ativo |
| **SYS-014** | Per-UF timeout (30s) + degraded mode (15s) for timeout cascade prevention | HIGH | 4h | P2 | Ativo |
| **SYS-015** | Phased UF batching (size=5, delay=2s) to reduce PNCP API pressure | HIGH | 4h | P2 | Ativo |
| **SYS-016** | Feature flag caching with lazy import -- circular dependency prevention | MEDIUM | 8h | P3 | Ativo |
| **SYS-017** | Lazy-load filter stats tracker to prevent circular imports | MEDIUM | 4h | P3 | Ativo |
| **SYS-018** | Circuit breaker pattern tuning (15 failures -> 60s cooldown) | MEDIUM | 8h | P3 | Ativo |
| **SYS-019** | CB integration -- when Supabase CB open, skip retries | MEDIUM | 4h | P3 | Ativo |
| **SYS-020** | Cache fallback banner + stale banner logic complexity | MEDIUM | 8h | P3 | Ativo |
| **SYS-021** | Redis L2 cache for cross-worker LLM sharing to reduce redundant calls | MEDIUM | 4h | P3 | Ativo |
| **SYS-022** | cryptography pin >=46.0.5,<47.0.0 -- fork-safe with Gunicorn preload | MEDIUM | 8h | P3 | Ativo |
| **SYS-023** | Health canary every 5 min for source health tracking | MEDIUM | 4h | P3 | Ativo |
| **SYS-024** | MFA (aal2) requirement + TOTP + recovery codes | MEDIUM | 16h | P3 | Ativo |
| **SYS-025** | Legacy route tracking -- non-/v1/ deprecated endpoints still accessible | MEDIUM | 4h | P3 | Ativo |
| **SYS-026** | Font preload optimization -- skip display fonts to avoid blocking critical path | MEDIUM | 4h | P3 | Ativo |
| **SYS-027** | chardet<6 pin (requests<=2.32.5 incompatible with chardet 6.0.0) | MEDIUM | 4h | P3 | Ativo |
| **SYS-028** | pytest timeout_method="thread" required for Windows dev compatibility | MEDIUM | 4h | P3 | Ativo |
| **SYS-029** | Three-layer migration defense could fail silently on edge cases | MEDIUM | 8h | P3 | Ativo |
| **SYS-030** | filter.py is 177KB monolithic file, hard to test | MEDIUM | 16h | P3 | Ativo |
| **SYS-031** | N+1 patterns in analytics queries | MEDIUM | 8h | P3 | Ativo |
| **SYS-032** | LLM cost optimization -- could use cheaper models for low-stakes classifications | MEDIUM | 8h | P3 | Ativo |
| **SYS-033** | Backward-compatible aliases for quota functions -- old imports still work | LOW | 4h | P4 | Ativo |
| **SYS-034** | Trial reminder emails -- legacy dead code, replaced by STORY-310 sequence | LOW | 4h | P4 | Ativo |
| **SYS-035** | Per-user Supabase tokens for user-scoped operations -- should verify all routes | LOW | 8h | P4 | Ativo |
| **SYS-036** | OpenAPI docs protected by DOCS_ACCESS_TOKEN in production | LOW | 4h | P4 | Ativo |
| **SYS-037** | Terms NEVER in both valid AND ignored -- critical invariant with assert | LOW | 4h | P4 | Ativo |

### Database (validado por @data-engineer)

| ID | Debito | Severidade | Horas | Prioridade | Status |
|----|--------|:---:|:---:|:---:|:---:|
| **DB-001** | FK Target Inconsistency -- 4 tabelas restantes referenciam `auth.users` em vez de `profiles` (`monthly_quota`, `user_oauth_tokens`, `google_sheets_exports`, `search_results_cache`) | HIGH | 6h | P1 | Ativo (70% resolvido) |
| **DB-005** | `search_state_transitions.search_id` no FK -- retention ja implementado (30d), falta apenas doc update | LOW | 0.5h | P4 | Ativo (parcial) |
| **DB-011** | Redundant indexes em 3 tabelas (`search_results_store`, `search_sessions`, `partners`) | MEDIUM | 1h | P3 | Ativo (1 de 4 resolvido) |
| **DB-013** | `plans.stripe_price_id` legacy column still used as fallback in billing.py | MEDIUM | 4h | P3 | Ativo |
| **DB-015** | `monthly_quota.user_id` references `auth.users` not `profiles` (parte de DB-001) | MEDIUM | 1h | P2 | Ativo |
| **DB-016** | Missing `updated_at` on mutable tables: `incidents` e `partners` | MEDIUM | 1h | P3 | Ativo |
| **DB-017** | `search_results_cache` duplicate size constraints | LOW | 0.5h | P4 | Ativo |
| **DB-018** | `partner_referrals.partner_id` missing ON DELETE CASCADE | MEDIUM | 0.5h | P2 | Ativo |
| **DB-019** | Trigger naming convention inconsistencies (4 padroes coexistem) | LOW | 2h | P4 | Ativo |
| **DB-020** | `google_sheets_exports.last_updated_at` naming (unica tabela com naming diferente, sem trigger) | LOW | 0.5h | P4 | Ativo |
| **DB-021** | `organizations.plan_type` no CHECK constraint -- aceita qualquer texto | MEDIUM | 0.5h | P2 | Ativo |
| **DB-023** | `user_oauth_tokens.provider` CHECK allows google/microsoft/dropbox but only Google implemented | LOW | 0.5h | P4 | Ativo |
| **DB-025** | `search_results_cache` 8 indexes -- write amplification (requer pg_stat analysis) | LOW | 2h | P3 | Ativo |
| **DB-026** | `search_sessions` accumulating without retention | LOW | 0.5h | P3 | Ativo |
| **DB-027** | `classification_feedback` accumulating without retention (24 meses recomendado -- valor ML) | LOW | 0.5h | P4 | Ativo |
| **DB-028** | `conversations`/`messages` no retention policy (24+ meses recomendado -- suporte) | LOW | 0.5h | P4 | Ativo |
| **DB-031** | `pipeline_items` missing `search_id` reference -- cannot trace search origin | LOW | 1h | P4 | Ativo |
| **DB-NEW-01** | `search_results_store` FK `NOT VALID` pode nao estar validada em producao | HIGH | 1h | P0 | Ativo (verificar) |
| **DB-NEW-02** | `search_results_store` index duplicado: `idx_search_results_user` e `idx_search_results_store_user_id` | MEDIUM | 0.5h | P3 | Ativo |
| **DB-NEW-03** | `search_results_store` sem retention -- `expires_at` coluna existe mas nenhum pg_cron limpa registros | HIGH | 1h | P1 | Ativo |
| **DB-NEW-04** | `search_results_cache` FK estado incerto -- multiplas migracoes tocaram esta FK | MEDIUM | 1h | P0 | Ativo (verificar) |
| **DB-INFO-01** | Consolidate backend migrations directory (bridge migration ja criada) | INFO | 1h | P4 | Info |
| **DB-INFO-03** | Backup strategy not documented (Supabase Pro: daily + PITR 7d) | INFO | 1h | P3 | Info |
| **DB-INFO-04** | Connection pooling -- backend usa REST (httpx), pgbouncer irrelevante para app layer | INFO | 0.5h | P4 | Info |

### Frontend/UX (validado por @ux-design-expert)

| ID | Debito | Severidade | Horas | Prioridade | Status |
|----|--------|:---:|:---:|:---:|:---:|
| **FE-001** | `/buscar/page.tsx` monolithic 983 LOC -- extrair `useSearchOrchestration` hook + `BuscarModals` | HIGH | 16-20h | P2 | Ativo |
| **FE-002** | `next/dynamic` parcialmente implementado; gaps restantes: Shepherd.js, framer-motion (~95KB) | MEDIUM | 4-6h | P2 | Ativo (parcial) |
| **FE-003** | SSE proxy complexity -- multiplos fallback paths (SSE -> polling -> simulation), hard to maintain | HIGH | 20-24h | P3 | Ativo |
| **FE-004** | Test coverage thresholds 50-55% (target 60%, ideal 80%) | HIGH | Ongoing | P3 | Ativo |
| **FE-006** | Dual component directories -- falta convencao documentada + 5-10 file moves | HIGH | 6-8h | P2 | Ativo |
| **FE-008** | localStorage reads inconsistentes -- writes use safeSetItem mas reads sao raw | MEDIUM | 6h | P3 | Ativo |
| **FE-009** | Inline SVGs coexistem com lucide-react; domain-specific SVGs nao centralizados | MEDIUM | 8h | P3 | Ativo |
| **FE-010** | `unsafe-inline`/`unsafe-eval` in CSP script-src -- security concern real | HIGH | 12-16h | P2 | Ativo |
| **FE-011** | No page-level tests para dashboard, pipeline, historico, onboarding, conta | MEDIUM | 16-20h | P3 | Ativo |
| **FE-012** | `eslint-disable exhaustive-deps` 3 vezes em buscar/page.tsx | MEDIUM | 3h | P3 | Ativo |
| **FE-013** | Hardcoded pricing fallback deve manter sync com Stripe | MEDIUM | Ongoing | P3 | Ativo |
| **FE-014** | Feature-gated dead code (ORGS_ENABLED, alertas, mensagens) shipped em bundles | MEDIUM | 6h | P3 | Ativo |
| **FE-015** | No bundle size monitoring/budget in CI | MEDIUM | 3h | P3 | Ativo |
| **FE-016** | Duplicate footer -- buscar inline + NavigationShell (cria duplicate landmarks) | LOW | 2h | P3 | Ativo |
| **FE-017** | Theme init via dangerouslySetInnerHTML (padrao correto para dark mode, low priority) | LOW | 1h | P4 | Ativo |
| **FE-018** | Raw `var(--*)` CSS alongside Tailwind tokens -- enforcement issue | MEDIUM | Ongoing | P3 | Ativo |
| **FE-019** | `@types/uuid` in dependencies (should be devDependencies) | LOW | 0.5h | P4 | Ativo |
| **FE-020** | `__tests__/e2e/` alongside `e2e-tests/` (two E2E locations) | LOW | 2h | P4 | Ativo |
| **FE-021** | No Storybook -- overkill para escala atual; Ladle quando team 3+ devs | LOW | 20-32h | Backlog | Ativo |
| **FE-022** | `Button.examples.tsx` sem visual regression testing | LOW | 8-12h | Backlog | Ativo |
| **FE-A11Y-01** | Loading spinners sem `role="status"` / `aria-busy` (parcialmente mitigado) | LOW | 2h | P3 | Ativo (parcial) |
| **FE-A11Y-02** | SearchErrorBoundary crash UI nao anunciado a assistive technology | MEDIUM | 1h | P2 | Ativo |
| **FE-A11Y-03** | Inline SVGs em pricing page sem `aria-hidden="true"` (spot audit) | LOW | 0.5h | P4 | Ativo |
| **FE-A11Y-05** | Duplicate `<footer role="contentinfo">` confunde landmark navigation | MEDIUM | 2h | P3 | Ativo |
| **FE-A11Y-07** | Escape key inconsistency em modals (parcialmente mitigado por focus-trap-react) | LOW | 1h | P4 | Ativo |
| **FE-NEW-01** | ProfileCompletionPrompt (651 LOC) importa framer-motion eagerly (~70KB) + zero testes | MEDIUM | 6h | P2 | Ativo |
| **FE-NEW-02** | No error boundaries em dashboard, pipeline, historico, conta -- crash perde contexto | HIGH | 4h | P1 | Ativo |
| **FE-NEW-03** | Direct localStorage reads em buscar/page.tsx sem SSR guard -- hydration mismatch risk | LOW | 2h | P3 | Ativo |
| **FE-NEW-04** | Tour step HTML injetado via raw string (Shepherd.js) -- bypassa React XSS protections | LOW | 3h | P4 | Ativo |

### QA/Testing (adicionado por @qa)

| ID | Debito | Severidade | Horas | Prioridade | Status |
|----|--------|:---:|:---:|:---:|:---:|
| **QA-NEW-01** | Integration conftest.py lacks `_cleanup_pending_async_tasks` e `_isolate_arq_module` -- usa warning suppression em vez de fix | MEDIUM | 4h | P2 | Ativo |
| **QA-NEW-02** | `@axe-core/playwright` instalado mas ZERO specs usam -- zero automated a11y assertions em E2E | HIGH | 8h | P2 | Ativo |
| **QA-NEW-03** | No enforced OpenAPI schema snapshot test -- `openapi_schema.diff.json` com drift ativo | MEDIUM | 4h | P2 | Ativo |
| **QA-NEW-04** | Backend coverage sem per-module minimum thresholds para auth, billing, search_pipeline | MEDIUM | 4h | P3 | Ativo |
| **QA-NEW-05** | Frontend jest.config.js triple-reset (`clearMocks` + `resetMocks` + `restoreMocks`) -- pode causar intermittent failures | LOW | 2h | P4 | Ativo |
| **QA-GAP-01** | Zero E2E para billing/checkout flow, pipeline kanban, SSE failure modes, mobile viewport, dashboard, historico | HIGH | 40h | P3 | Ativo |

---

## Items Resolvidos (para referencia)

Os seguintes itens foram confirmados como resolvidos por migracoes recentes (2026-03-04 a 2026-03-09):

| ID | Debito | Resolvido em | Confirmado por |
|----|--------|-------------|----------------|
| **DB-002** | `search_results_store` missing ON DELETE CASCADE | `20260304100000` (FK reaponta profiles + CASCADE) | @data-engineer |
| **DB-003** | `classification_feedback` missing ON DELETE CASCADE | `20260225120000` (FK para profiles + CASCADE) | @data-engineer |
| **DB-004** | Duplicate `updated_at` trigger functions (3 tables) | `20260304120000_rls_policies_trigger_consolidation.sql` | @data-engineer |
| **DB-006** | `alert_preferences` auth.role() pattern | `20260304200000_rls_standardize_service_role.sql` | @data-engineer |
| **DB-007** | `organizations`/`org_members` auth.role() pattern | `20260304200000` | @data-engineer |
| **DB-008** | `partners`/`partner_referrals` auth.role() pattern | `20260304200000` | @data-engineer |
| **DB-009** | `search_results_store` auth.role() pattern | `20260304200000` | @data-engineer |
| **DB-010** | `health_checks`/`incidents` missing retention jobs | `20260308310000_debt009_retention_pgcron_jobs.sql` | @data-engineer |
| **DB-012** | `conversations` missing composite index admin inbox | `20260308400000_debt010_schema_guards.sql` | @data-engineer |
| **DB-022** | `pipeline_items` service role overly permissive | Migration 027 + verified in `20260304200000` | @data-engineer |
| **DB-029** | `alert_sent_items` missing retention | `20260308310000` (180 days) | @data-engineer |
| **DB-030** | `stripe_webhook_events` no automated retention | `022_retention_cleanup.sql` (90 days) | @data-engineer |
| **FE-005** | No `prefers-reduced-motion` for 8 custom animations | `globals.css:331-337` comprehensive rule | @ux-design-expert |
| **FE-007** | `aria-live` missing on dynamic content updates | 15+ components now have aria-live | @ux-design-expert |
| **FE-A11Y-04** | Focus trap inconsistency across modals | `focus-trap-react` v12 in 6 modal components | @ux-design-expert |
| **FE-A11Y-06** | Color-only indicators on badges | All badges now have text + icon + color | @ux-design-expert |

**Items rejeitados por especialistas:**

| ID | Debito | Motivo | Decidido por |
|----|--------|--------|-------------|
| **DB-INFO-02** | Schema version table independente | Redundante -- Supabase ja rastreia via `supabase_migrations.schema_migrations` | @data-engineer |
| **DB-INFO-06** | JSONB columns lack DB-level validation | Pydantic no app layer e suficiente; CHECK em JSONB e fragil e lento | @data-engineer |
| **DB-024** | `audit_events` no index on JSONB | Nenhuma query atual; premature optimization. Downgraded to INFO | @data-engineer |

---

## Matriz de Priorizacao Final

### P0 -- Imediato (Sprint 1, primeira semana)

Items de seguranca, producao, e verificacao que devem ser resolvidos antes de qualquer outro trabalho.

| # | ID | Debito | Area | Horas | Risco |
|---|-----|--------|------|:---:|-------|
| 1 | **SYS-004** | Token hash parcial -- CVSS 9.1 collision risk | Security | 4h | Thundering herd on cache invalidation |
| 2 | **SYS-001** | faulthandler + uvicorn SIGSEGV em Railway | Reliability | 4h | Baixo risco de regressao |
| 3 | **SYS-002** | LLM JSON truncation 20-30% das chamadas | AI/Quality | 4h | Mudanca no comportamento de classificacao |
| 4 | **DB-NEW-01** | FK NOT VALID pode nao estar enforced em producao | Data Integrity | 1h | Zero risco (query de verificacao) |
| 5 | **DB-NEW-04** | search_results_cache FK estado incerto | Data Integrity | 1h | Zero risco (query de verificacao) |

**Esforco P0: ~14 horas**

### P1 -- Curto Prazo (Sprint 1-2)

Items de alta prioridade com impacto direto em producao, performance, ou receita.

| # | ID | Debito | Area | Horas | Dependencia |
|---|-----|--------|------|:---:|-------------|
| 1 | **SYS-005** | ES256/JWKS JWT algorithm rotation | Security | 8h | Apos SYS-004 |
| 2 | **SYS-003** | PNCP API silent 400 on >50 page size | Integration | 8h | Nenhuma |
| 3 | **SYS-010** | OpenAI client timeout thread starvation | Performance | 4h | Nenhuma |
| 4 | **SYS-012** | LRU cache unbounded memory growth | Performance | 4h | Nenhuma |
| 5 | **DB-001** | FK padronizacao (4 tabelas restantes) | Data Integrity | 6h | Apos DB-NEW-01/DB-NEW-04 |
| 6 | **DB-NEW-03** | search_results_store retention (expires_at cleanup) | Storage | 1h | Nenhuma |
| 7 | **FE-NEW-02** | Error boundaries em dashboard, pipeline, historico, conta | UX/Reliability | 4h | Nenhuma |

**Esforco P1: ~35 horas**

### P2 -- Medio Prazo (Sprint 2-4)

Items de media prioridade que melhoram maintainability, performance, e seguranca.

| # | ID | Debito | Area | Horas |
|---|-----|--------|------|:---:|
| 1 | **FE-010** | CSP nonce implementation (unsafe-inline/eval removal) | Security | 12-16h |
| 2 | **FE-001** | buscar page orchestration extraction (useSearchOrchestration) | Maintainability | 16-20h |
| 3 | **FE-002** | next/dynamic para Shepherd.js + framer-motion restantes | Performance | 4-6h |
| 4 | **FE-006** | Component directory consolidation + convencao documentada | Architecture | 6-8h |
| 5 | **FE-A11Y-02** | SearchErrorBoundary role="alert" | Accessibility | 1h |
| 6 | **FE-NEW-01** | ProfileCompletionPrompt: next/dynamic + testes | Performance | 6h |
| 7 | **DB-015** | monthly_quota FK para profiles(id) | Data Integrity | 1h |
| 8 | **DB-018** | partner_referrals ON DELETE CASCADE | Data Integrity | 0.5h |
| 9 | **DB-021** | organizations.plan_type CHECK constraint | Data Integrity | 0.5h |
| 10 | **QA-NEW-01** | Integration conftest.py proper async cleanup | Test Reliability | 4h |
| 11 | **QA-NEW-02** | Enable @axe-core/playwright em 5 core E2E flows | Accessibility | 8h |
| 12 | **QA-NEW-03** | Enforce OpenAPI schema snapshot em CI | API Contract | 4h |
| 13 | **SYS-006** | main.py monolith decomposition | Maintainability | 16h |
| 14 | **SYS-011** | Merge-enrichment from lower-priority duplicates | Correctness | 8h |
| 15 | **SYS-013** | Per-future timeout counter for LLM batch | Observability | 4h |
| 16 | **SYS-014** | Per-UF timeout + degraded mode | Performance | 4h |
| 17 | **SYS-015** | Phased UF batching | Performance | 4h |
| 18 | **SYS-008** | requests library -> httpx full migration | Maintainability | 16h |
| 19 | **SYS-009** | Frontend advanced refactoring (DEBT-016 outstanding) | Maintainability | 16h |

**Esforco P2: ~132-142 horas**

### P3 -- Backlog Planejado (Sprint 5+)

Items de media/baixa prioridade para melhoria continua.

| # | ID | Debito | Area | Horas |
|---|-----|--------|------|:---:|
| 1 | FE-003 | SSE proxy complexity simplification | Maintainability | 20-24h |
| 2 | FE-004 | Test coverage 50-55% -> 60% target | Quality | Ongoing |
| 3 | FE-008 | localStorage centralization | Maintainability | 6h |
| 4 | FE-009 | Inline SVGs -> lucide-react migration | Maintainability | 8h |
| 5 | FE-011 | Page-level tests (5 pages) | Quality | 16-20h |
| 6 | FE-012 | Fix eslint-disable exhaustive-deps | Code Quality | 3h |
| 7 | FE-013 | Pricing fallback sync process | Ongoing | Ongoing |
| 8 | FE-014 | Feature-gated dead code tree-shaking | Performance | 6h |
| 9 | FE-015 | Bundle size budget in CI | Quality | 3h |
| 10 | FE-016 | Duplicate footer -> NavigationShell unification | UX/A11Y | 2h |
| 11 | FE-018 | Tailwind token enforcement (lint rule) | Consistency | Ongoing |
| 12 | FE-A11Y-01 | Loading spinners role="status" / aria-busy | A11Y | 2h |
| 13 | FE-A11Y-05 | Duplicate footer landmarks fix | A11Y | 2h |
| 14 | FE-NEW-03 | localStorage SSR guard in buscar | Correctness | 2h |
| 15 | SYS-016 | Feature flag caching circular deps | Maintainability | 8h |
| 16 | SYS-017 | Lazy-load filter stats tracker | Correctness | 4h |
| 17 | SYS-018 | Circuit breaker tuning | Reliability | 8h |
| 18 | SYS-019 | CB integration -- skip retries when open | Reliability | 4h |
| 19 | SYS-020 | Cache fallback/stale banner logic | Maintainability | 8h |
| 20 | SYS-021 | Redis L2 cache for LLM sharing | Performance | 4h |
| 21 | SYS-022 | cryptography pin fork-safety | Reliability | 8h |
| 22 | SYS-023 | Health canary 5-min schedule | Observability | 4h |
| 23 | SYS-024 | MFA completion | Security | 16h |
| 24 | SYS-025 | Legacy route deprecation tracking | Maintainability | 4h |
| 25 | SYS-026 | Font preload optimization | Performance | 4h |
| 26 | SYS-027 | chardet pin removal (needs SYS-008) | Reliability | 4h |
| 27 | SYS-028 | pytest timeout_method="thread" | Reliability | 4h |
| 28 | SYS-029 | Migration defense edge cases | Reliability | 8h |
| 29 | SYS-030 | filter.py 177KB decomposition | Maintainability | 16h |
| 30 | SYS-031 | Analytics N+1 queries | Performance | 8h |
| 31 | SYS-032 | LLM cost optimization | Cost | 8h |
| 32 | DB-011 | Redundant indexes (3 restantes) | Performance | 1h |
| 33 | DB-013 | plans.stripe_price_id legacy migration | Billing | 4h |
| 34 | DB-016 | Missing updated_at on incidents/partners | Observability | 1h |
| 35 | DB-025 | search_results_cache index optimization | Performance | 2h |
| 36 | DB-026 | search_sessions retention (12 meses) | Storage | 0.5h |
| 37 | DB-INFO-03 | Backup strategy documentation | Ops | 1h |
| 38 | QA-NEW-04 | Per-module coverage thresholds | Quality | 4h |
| 39 | QA-GAP-01 | E2E gaps (billing, pipeline, SSE, mobile, dashboard) | Quality | 40h |

### P4 -- Backlog Oportunistico

| # | IDs | Tema | Horas |
|---|-----|------|:---:|
| 1 | DB-005, DB-017, DB-019, DB-020, DB-023, DB-027, DB-028, DB-031 | DB cosmetic/naming/retention (baixo volume) | ~6h |
| 2 | FE-017, FE-019, FE-020, FE-A11Y-03, FE-A11Y-07, FE-NEW-04 | FE minor cleanup | ~9.5h |
| 3 | SYS-033, SYS-034, SYS-035, SYS-036, SYS-037 | Backend cleanup/aliases/dead code | ~24h |
| 4 | QA-NEW-05 | Jest triple-reset investigation | 2h |
| 5 | FE-021, FE-022 | Storybook/visual regression (future) | 28-44h |
| 6 | DB-INFO-01, DB-INFO-04 | DB docs | 1.5h |

---

## Plano de Resolucao

### Batch A: Quick Wins (< 2h cada)

Items que podem ser resolvidos rapidamente com alto impacto relativo.

| # | ID | Acao | Horas | Impacto |
|---|-----|------|:---:|---------|
| 1 | **DB-NEW-01** | Executar query de verificacao FK validation em producao | 0.5h | Confirma estado de DB-001 |
| 2 | **DB-NEW-04** | Executar query FK target em search_results_cache | 0.5h | Confirma estado de DB-001 |
| 3 | **DB-NEW-03** | Criar pg_cron: `DELETE FROM search_results_store WHERE expires_at < now()` | 0.5h | Previne growth ilimitado; billing |
| 4 | **DB-021** | ALTER TABLE organizations ADD CONSTRAINT chk_org_plan_type | 0.5h | Data integrity |
| 5 | **DB-018** | ALTER TABLE partner_referrals ON DELETE CASCADE | 0.5h | Data integrity |
| 6 | **DB-015** | Migrar monthly_quota FK para profiles(id) | 1h | FK consistency |
| 7 | **DB-NEW-02** | DROP INDEX idx_search_results_store_user_id (duplicata) | 0.5h | Write performance |
| 8 | **DB-026** | Criar pg_cron para search_sessions (12 meses) | 0.5h | Storage growth |
| 9 | **FE-A11Y-02** | Add role="alert" to SearchErrorBoundary fallback | 0.5h | A11Y compliance |
| 10 | **FE-019** | Move @types/uuid to devDependencies | 0.5h | Dependency hygiene |
| 11 | **FE-NEW-01** (parcial) | Wrap ProfileCompletionPrompt with next/dynamic | 0.5h | -70KB dashboard bundle |
| 12 | **DB-016** | Adicionar updated_at em incidents e partners + trigger | 1h | Change tracking |

**Total Batch A: ~7h para resolver 12 items.**

### Batch B: Foundation (requer planejamento, 1-2 sprints)

Correcoes estruturais que fundamentam melhorias futuras.

| # | IDs | Tema | Horas | Pre-requisitos |
|---|-----|------|:---:|----------------|
| 1 | **SYS-004** | Token hash full SHA256 | 4h | Deploy em low-traffic window; dual-hash transition |
| 2 | **SYS-001** | uvicorn[standard] + faulthandler fix | 4h | Railway staging test |
| 3 | **SYS-002** | LLM MAX_TOKENS increase | 4h | Golden samples baseline antes |
| 4 | **SYS-005** | ES256/JWKS + HS256 backward compat | 8h | Apos SYS-004 |
| 5 | **SYS-003** | PNCP page size enforcement | 8h | Health canary test |
| 6 | **DB-001** | FK standardization (4 tabelas) | 6h | Apos Batch A queries |
| 7 | **SYS-010 + SYS-012** | LLM resilience (timeout + cache bounds) | 8h | Concurrent |
| 8 | **FE-NEW-02** | Error boundaries em 4 pages | 4h | Nenhuma |

**Total Batch B: ~46h**

### Batch C: Optimization (sprints 3-4)

Performance, UX, e security improvements.

| # | IDs | Tema | Horas | Pre-requisitos |
|---|-----|------|:---:|----------------|
| 1 | **FE-010** | CSP nonce implementation | 12-16h | Feature flag; test all 3rd-party scripts |
| 2 | **FE-001** | buscar page extraction | 16-20h | Incremental (1 hook per PR) |
| 3 | **FE-006** | Component directory consolidation | 6-8h | Document convention first |
| 4 | **FE-002** | Remaining next/dynamic (Shepherd, framer-motion) | 4-6h | Nenhuma |
| 5 | **QA-NEW-02** | Enable axe-core in 5 E2E specs | 8h | Nenhuma |
| 6 | **QA-NEW-03** | OpenAPI snapshot CI enforcement | 4h | Nenhuma |
| 7 | **SYS-006** | main.py decomposition | 16h | Nenhuma |
| 8 | **SYS-008** | requests -> httpx migration | 16h | Enables SYS-027 |
| 9 | **SYS-011** | Merge-enrichment from duplicates | 8h | Nenhuma |
| 10 | **SYS-013 + SYS-014 + SYS-015** | LLM observability + UF timeout + batching | 12h | Nenhuma |
| 11 | **SYS-009** | Frontend advanced refactoring (DEBT-016) | 16h | Nenhuma |
| 12 | **QA-NEW-01** | Integration conftest.py async cleanup | 4h | Nenhuma |

**Total Batch C: ~122-142h**

### Batch D: Long-term (sprints 5+)

Architecture, design system, e comprehensive quality.

| # | Tema | IDs | Horas |
|---|------|-----|:---:|
| 1 | SSE proxy simplification | FE-003 | 20-24h |
| 2 | filter.py decomposition | SYS-030 | 16h |
| 3 | Frontend test coverage -> 60% | FE-004, FE-011 | 36-40h |
| 4 | E2E gap coverage | QA-GAP-01 | 40h |
| 5 | Billing legacy migration | DB-013 | 4h |
| 6 | Circuit breaker + CB tuning | SYS-018, SYS-019 | 12h |
| 7 | MFA completion | SYS-024 | 16h |
| 8 | Remaining P3/P4 items | Various | ~80h |

**Total Batch D: ~224+ horas**

---

## Dependencias entre Batches

```
Batch A (Quick Wins, ~7h)
  |
  |-- DB-NEW-01/DB-NEW-04 results ──> inform scope of DB-001 in Batch B
  |-- DB-NEW-03 (retention) ──> independent, can run immediately
  |-- All DB items can be a single migration
  |
  v
Batch B (Foundation, ~46h)
  |
  |-- SYS-004 ──must precede──> SYS-005 (token hash before JWT rotation)
  |-- SYS-002 golden samples ──must precede──> SYS-002 fix deployment
  |-- DB-001 completion ──blocked by──> Batch A query results
  |-- FE-NEW-02 (error boundaries) ──independent of──> all other Batch B items
  |
  v
Batch C (Optimization, ~132h)
  |
  |-- FE-001 extraction ──enables──> FE-012 (fix exhaustive-deps, P3)
  |                      ──enables──> FE-016 (footer dedup, P3)
  |-- FE-006 consolidation ──enables──> FE-009 (centralized icons, P3)
  |-- SYS-008 (httpx) ──enables──> SYS-027 (chardet pin removal, P3)
  |-- FE-010 (CSP) ──must be──> behind feature flag, independent sprint
  |-- QA items (QA-NEW-01/02/03) ──parallelizable with──> all FE/SYS items
  |
  v
Batch D (Long-term, ~224h)
  |
  |-- FE-003 (SSE) ──should follow──> FE-001 (cleaner codebase)
  |-- DB-013 (billing) ──requires──> 1 week monitoring after billing.py change
  |-- QA-GAP-01 (E2E) ──independent but benefits from──> Batch C stability
```

**Critical path:** Batch A (7h) -> Batch B P0 items (12h) -> Batch B P1 items (34h) -> Batch C

**Parallelizable:** DB items in Batch A can all be done in a single migration. FE quick wins are independent of DB work. QA items (QA-NEW-02, QA-NEW-03) can start during Batch B without blocking.

---

## Riscos e Mitigacoes

### Riscos de Alta Severidade (da analise cruzada @qa)

| Risco | Areas | Prob. | Impacto | Mitigacao |
|-------|-------|:---:|:---:|-----------|
| **SYS-004 token hash fix invalida cached sessions** | Auth + All routes | Alta | HIGH | Deploy em 2-4 AM BRT; dual-hash lookup (old + new) por 1h de transicao; monitorar p99 latency |
| **FE-010 CSP nonce breaks third-party scripts** | Frontend + Stripe + Sentry + Mixpanel + Clarity | Alta | CRITICAL | Deploy behind feature flag; testar cada 3rd-party individualmente; rollback = revert single middleware line |
| **DB-001 FK migration breaks auth flow** | Database + Auth + Registration | Media | CRITICAL | NOT VALID + VALIDATE pattern; orphan detection query PRE-migration; rollback migration ready |
| **FE-001 buscar refactor state bugs** | Search + SSE + Filters | Media | HIGH | Extract incrementally (1 hook per PR); full E2E pass before AND after; A/B test staging |
| **SYS-002 LLM token fix changes classification behavior** | LLM + Result Quality | Media | HIGH | Golden samples test before/after; compare acceptance rates; gradual rollout |
| **Retention jobs delete debugging evidence** | DB + Observability | Baixa | MEDIUM | Retention jobs check for open incidents before purging |

### Areas Nao Cobertas (identificadas por @qa)

Estas areas foram identificadas como gaps no assessment e devem ser consideradas para auditorias futuras:

| Area | Descricao | Severidade |
|------|-----------|:---:|
| Billing/Stripe end-to-end | Falta integration test para checkout -> webhook -> plan_type sync | HIGH |
| Cron job reliability | Error handling, retry logic, overlap protection em cron_jobs.py | MEDIUM |
| Redis failure modes | Comportamento quando Redis totalmente indisponivel no startup | MEDIUM |
| Email delivery reliability | Failed delivery em Resend downtime (trial reminders, password resets) | LOW |
| Worker process isolation | Memory leaks, ThreadPoolExecutor exhaustion em ARQ worker | MEDIUM |
| API versioning debt | Catalogo de rotas deprecated vs ativas, sem deprecation telemetry | LOW |

---

## Condicoes do QA Gate

O QA Gate foi **APPROVED com 5 condicoes**. Status e plano de cada:

### Condicao 1 (MUST): Executar SQL diagnostics em producao

**Status:** Pendente
**Acao:** Executar as 5 queries SQL do `db-specialist-review.md` Section "Validacao Pendente em Producao":

```sql
-- 1. Estado final das FKs (DB-001, DB-NEW-01, DB-NEW-04)
SELECT tc.table_name, tc.constraint_name,
       ccu.table_name AS references_table,
       rc.delete_rule,
       pc.convalidated
FROM information_schema.table_constraints tc
JOIN information_schema.constraint_column_usage ccu
  ON tc.constraint_name = ccu.constraint_name
JOIN information_schema.referential_constraints rc
  ON tc.constraint_name = rc.constraint_name
LEFT JOIN pg_constraint pc
  ON pc.conname = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_schema = 'public'
ORDER BY tc.table_name;

-- 2. auth.role() residual (deve retornar 0 rows)
SELECT schemaname, tablename, policyname, qual
FROM pg_policies
WHERE schemaname = 'public' AND qual LIKE '%auth.role()%';

-- 3. pg_cron jobs ativos (deve retornar 8+ jobs)
SELECT jobname, schedule FROM cron.job ORDER BY jobname;

-- 4. Indexes redundantes -- scan frequency
SELECT indexrelname, idx_scan, idx_tup_read, pg_size_pretty(pg_relation_size(indexrelid))
FROM pg_stat_user_indexes
WHERE relname IN ('search_results_cache', 'search_results_store', 'search_sessions', 'partners')
ORDER BY relname, idx_scan ASC;

-- 5. search_results_store growth (DB-NEW-03)
SELECT count(*) AS total_rows,
       count(*) FILTER (WHERE expires_at < now()) AS expired_rows,
       pg_size_pretty(pg_total_relation_size('search_results_store')) AS total_size
FROM search_results_store;
```

**Prazo:** Antes de iniciar Batch B.
**Responsavel:** @data-engineer ou @devops via Supabase CLI.

### Condicao 2 (MUST): Estabelecer baselines de testes

**Status:** Pendente
**Acao:**
1. `python scripts/run_tests_safe.py` -- record pass/fail/skip counts
2. `npm test` -- record pass/fail/skip counts
3. `npm run test:e2e` -- record results + identify flaky tests
4. `pytest --cov` -- per-module coverage breakdown
5. `npm run test:coverage` -- per-page/hook coverage breakdown
6. `npx next build` -- chunk sizes baseline for FE-001/FE-002
7. `pytest -k test_golden_samples` -- LLM classification baseline for SYS-002

**Prazo:** Antes de iniciar qualquer fix de P0/P1.
**Responsavel:** @qa.

### Condicao 3 (MUST): Mover FE-010 de P1 para P2

**Status:** Aplicado neste documento.
**Justificativa:** Regression risk alto demais para sprint com P0 security fixes. CSP nonce com 5+ third-party scripts (Stripe.js, Sentry, Mixpanel, Clarity, Cloudflare) precisa de esforco dedicado. `unsafe-inline`/`unsafe-eval` e defense-in-depth, nao barreira primaria de auth.

### Condicao 4 (SHOULD): Adicionar DB-NEW-03 ao Batch de Retention

**Status:** Aplicado neste documento.
**Justificativa:** Quick win de 0.5h com impacto direto em storage billing. Incluido no Batch A como item #3.

### Condicao 5 (SHOULD): Criar regression test plan para items P0

**Status:** Documentado na secao "Testes de Validacao por Batch" abaixo.
**Plano:** Cada item P0 tem rollback plan + testes especificos identificados.

---

## Criterios de Sucesso

### Metricas

| Metrica | Baseline Atual | Target Pos-Batch A/B | Target Pos-Batch C/D | Prazo |
|---------|:---:|:---:|:---:|:---:|
| Backend test pass rate | 5131+ (a verificar) | 5131+ (0 failures) | 5500+ | Continuous |
| Backend coverage (global) | 70% threshold | 70% | 80% | P3 |
| Backend coverage (critical modules) | Desconhecido | 60% min (auth, billing, search_pipeline) | 70% min | P3 |
| Frontend test pass rate | 2681+ (a verificar) | 2681+ (0 failures) | 3000+ | Continuous |
| Frontend coverage (branches) | 50% | 55% | 60% | P3 |
| Frontend coverage (lines) | 55% | 60% | 65% | P3 |
| E2E pass rate | Unknown (21 specs) | >95% | >98% | Continuous |
| E2E a11y audits (axe-core) | 0 specs | 5 core flows | 10+ flows | P2 |
| Bundle size (JS first load) | Unknown | Measure baseline | <250KB gzipped | P2 |
| LLM JSON parse success rate | ~70-80% | >99% | >99.5% | P0 |
| Zero CRITICAL debts | 5 ativos | 0 | 0 | Batch B |
| Zero HIGH debts | 19 ativos | <10 | 0 | Batch C |
| DB FK consistency | ~70% on profiles | 100% | 100% | Batch B |

### Testes de Validacao por Batch

**Batch A (Quick Wins):**
- Execute 5 production SQL queries from Condicao 1 -- record results
- Verify pg_cron jobs created: `SELECT jobname, schedule FROM cron.job`
- Verify FK state after DB-015 migration
- Run `npm run build` to confirm no bundle regressions from FE-NEW-01 dynamic import

**Batch B (Foundation):**

| ID | Testes Necessarios | Rollback Plan |
|----|-------------------|---------------|
| SYS-004 | Run `test_security_story210.py` + test two concurrent requests with different tokens must not cross-pollinate | Revert to partial hash (single line in auth.py) |
| SYS-001 | Deploy to Railway staging, verify no SIGSEGV for 1h. Test faulthandler disabled. | Remove `[standard]` extra from requirements.txt |
| SYS-002 | Run golden_samples test before/after. Compare classification acceptance rates. Verify JSON parse success >99% with new MAX_TOKENS. | Revert MAX_TOKENS to 300 (single config line) |
| SYS-005 | Verify HS256 backward compat + ES256 new tokens work simultaneously. Test JWKS rotation with 2 active keys. | Disable ES256 in config; HS256 continues working |
| SYS-003 | Test tamanhoPagina=50 (success) and tamanhoPagina=51 (graceful fail). Add canary test with real API. | Revert page size constant |
| DB-001 | Run FK diagnostic query post-migration. Test user deletion cascade through all dependent tables. Run orphan detection pre-migration. | Pre-written rollback migration reverting FK targets |
| SYS-010/012 | Test 16s delay timeout at 15s. Test LRU eviction at 5000 entries. | Revert timeout/cache config |
| FE-NEW-02 | Error in child component caught by boundary. Fallback UI renders with recovery action. | Remove error boundary wrappers (harmless) |

**Batch C (Optimization):**
- FE-010: Test Stripe.js, Sentry, Mixpanel, Clarity, Cloudflare all load with nonce-based CSP. Rollback: revert single CSP header line in middleware.
- FE-001: Full E2E search flow pass (search-flow.spec.ts). All 35 sub-components render. Bundle size equal or smaller.
- FE-006: ESLint import restriction rule passes on CI. No broken imports.
- QA-NEW-02: 5 E2E specs run axe audits with 0 critical violations.
- QA-NEW-03: CI fails on OpenAPI schema drift.

**Batch D (Long-term):**
- FE-003: SSE fallback cascade still works end-to-end (SSE -> polling -> simulation).
- SYS-030: filter.py split into modules; all 170+ filter tests pass.
- FE-004/FE-011: Coverage thresholds hit 60% branches, 65% lines.
- QA-GAP-01: E2E exists for billing checkout, pipeline drag-and-drop, SSE failure modes, mobile viewport, dashboard rendering.

---

## Apendice: Metodologia

### Processo de Brownfield Discovery (10 fases)

Este assessment foi produzido atraves do processo AIOS Brownfield Discovery de 10 fases:

| Fase | Agente | Entregavel | Status |
|:---:|--------|-----------|:---:|
| 1 | @architect | `system-architecture.md` -- Backend architecture audit | Completo |
| 2 | @data-engineer | `DB-AUDIT.md` -- Database schema audit (76 migrations) | Completo |
| 3 | @ux-design-expert | `frontend-spec.md` -- Frontend/UX audit | Completo |
| 4 | @architect | `technical-debt-DRAFT.md` -- Initial consolidation (93 items) | Completo |
| 5 | @data-engineer | `db-specialist-review.md` -- DB specialist review (10 resolved, 4 new, 4 adjusted) | Completo |
| 6 | @ux-design-expert | `ux-specialist-review.md` -- UX specialist review (3 resolved, 4 new, 5 adjusted) | Completo |
| 7 | @qa | `qa-review.md` -- QA cross-cutting review (6 new, 5 conditions, 6 risks) | Completo |
| 8 | @architect | **Este documento** -- Final consolidated assessment | Completo |
| 9 | -- | Execucao de Condicoes 1-2 do QA Gate (SQL queries + test baselines) | Pendente |
| 10 | -- | Inicio da execucao (Batch A -> B -> C -> D) | Pendente |

### Criterios de Avaliacao

- **Severidade:** Baseada em impacto em producao (CRITICAL = downtime/security/data loss, HIGH = performance/reliability/correctness, MEDIUM = maintainability/conventions, LOW = cleanup/cosmetic, INFO = documentation/future-proofing)
- **Esforco:** Estimado em horas por especialista da area (DB items por @data-engineer, FE items por @ux-design-expert, SYS items por @architect, QA items por @qa)
- **Prioridade:** Calculada como (Severity weight x Impact) / Effort, ajustada por dependencias e risco de regressao. P0 = imediato, P1 = sprint atual, P2 = sprints 2-4, P3 = backlog planejado, P4 = oportunistico
- **Status:** Validado cruzando codigo-fonte no commit `3c71ce93`, 76 arquivos de migracao, e 631+ arquivos de teste

### Fontes Primarias

| Documento | Localizacao |
|-----------|------------|
| System Architecture Audit | `docs/reviews/system-architecture.md` |
| Database Audit | `docs/reviews/DB-AUDIT.md` |
| Frontend Specification | `docs/frontend/frontend-spec.md` |
| Technical Debt DRAFT | `docs/prd/technical-debt-DRAFT.md` |
| DB Specialist Review | `docs/reviews/db-specialist-review.md` |
| UX Specialist Review | `docs/reviews/ux-specialist-review.md` |
| QA Review | `docs/reviews/qa-review.md` |

---

*Generated by @architect during Brownfield Discovery Phase 8 -- Final Assessment*
*Consolidates inputs from @data-engineer (Phase 5), @ux-design-expert (Phase 6), @qa (Phase 7)*
*This document is the SINGLE SOURCE OF TRUTH for SmartLic technical debt as of 2026-03-09.*
