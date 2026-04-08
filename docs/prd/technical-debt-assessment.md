# Technical Debt Assessment - FINAL

**Project:** SmartLic (smartlic.tech)
**Date:** 2026-04-08
**Version:** 2.0
**Validated by:** @architect (Aria), @data-engineer (Dara), @ux-design-expert (Uma), @qa (Quinn)

**Source Documents:**
- `docs/prd/technical-debt-DRAFT.md` -- Phase 1-3 consolidation (49 items)
- `docs/reviews/db-specialist-review.md` -- Phase 5, @data-engineer adjustments
- `docs/reviews/ux-specialist-review.md` -- Phase 6, @ux-design-expert adjustments (+6 items)
- `docs/reviews/qa-review.md` -- Phase 7, QA gate (+6 items, 3 corrections)

---

## Executive Summary

- **Total de debitos:** 61 (4 resolved/monitoring, 57 active)
- **Criticos (P0):** 4 | **Altos (P1):** 12 | **Medios (P2):** 15 | **Baixos (P3):** 12 | **Backlog (P4):** 14 | **Resolved (monitoring):** 4
- **Esforco total estimado (Phases 1-4):** 100-130h
- **Esforco backlog (Phase 5):** 150-250h
- **Critical path:** ~9h (TD-033 + TD-019 + retention crons + backup + RPC audit)

### QA Blocking Conditions -- Status

| # | Condition | Status |
|---|-----------|--------|
| 1 | Fix TD-007/008/009 phantom file references | FIXED -- replaced with actual oversized files: `quota.py` (1,660 LOC), `consolidation.py` (1,394 LOC), `llm_arbiter.py` (1,362 LOC) |
| 2 | Upgrade TD-033 to P0 | DONE -- Supabase FREE tier is now P0 |
| 3 | Add TD-056 to TD-061 from QA review | DONE -- all 6 items incorporated |
| 4 | Incorporate all severity recalibrations | DONE -- see inventory tables below |

---

## Inventario Completo de Debitos

### 1. Sistema/Backend (validado por @architect + @qa)

#### Resolved (monitoring only)

| ID | Debito | Status | Notas |
|----|--------|--------|-------|
| TD-001 | CRIT-SIGSEGV-v2: Uvicorn single-worker mode | Resolved | Horizontal scaling via Railway. Monitor throughput at peak. |
| TD-002 | CRIT-041: Fork-unsafe C extensions removed | Resolved | No uvloop/httptools in prod. Test on dependency updates. |
| TD-003 | CRIT-033: ARQ worker health + inline fallback | Resolved | Worker monitored; inline fallback if worker down. |
| TD-004 | CRIT-072: Async search deadline + time budget | Resolved | Implemented; monitor timeout metrics. |

#### Active Debts

| ID | Debito | Severidade | Horas | Prioridade | Status |
|----|--------|------------|-------|------------|--------|
| TD-005 | SYS-023: Per-user Supabase tokens -- service_role used for user-scoped ops. RLS mitigates but not ideal. | High | 16 | P1 | Open -- scope depends on TD-059 audit |
| TD-006 | DEBT-325: Exchange rate USD/BRL hardcoded | Medium | 2 | P2 | Open |
| TD-007 | `quota.py` oversized (1,660 LOC) -- quota logic, plan enforcement, atomic operations in single file | Medium | 12 | P2 | Open (corrected: was phantom `Execute.py`) |
| TD-008 | `consolidation.py` oversized (1,394 LOC) -- multi-source result consolidation in single file | Medium | 8 | P2 | Open (corrected: was phantom `Generate.py`) |
| TD-009 | `llm_arbiter.py` oversized (1,362 LOC) -- LLM classification pipeline in single file | Medium | 8 | P2 | Open (corrected: was phantom `Filter_stage.py`) |
| TD-010 | `quota.py` complexity -- high cyclomatic complexity (alias of TD-007 for tracking) | Medium | -- | P2 | Merged into TD-007 |
| TD-011 | Single-worker no auto-scaling -- Railway horizontal scaling manual, no auto-scale | Medium-High | 4 | P2 | Open |
| TD-012 | DEBT-018: Cryptography fork-safe testing not automated in CI | Low | 2 | P3 | Open |
| TD-013 | PNCP API availability 94% (target 95%) -- health canary uses tamanhoPagina=10 | Medium | 2 | P3 | Open |
| TD-014 | Cache hit rate 65-75% (target >70%) -- warming strategy could improve | Medium | 4 | P3 | Open |
| TD-015 | Railway 120s hard timeout vs Gunicorn 180s -- silent request death, no Sentry trace | Medium-High | 2 | P2 | Open (upgraded per QA) |
| TD-016 | 121 migration files sem squash -- fresh env takes 2-3 min | Low | 24 | P3 | Open -- must be LAST after all Phase 1-2 migrations |
| TD-017 | OpenTelemetry HTTP-only (no gRPC) -- fork-safety limitation | Low | 0 | P4 | Accepted limitation |
| TD-018 | Dual migration naming convention (001_ vs 20260326_) | Low | 0 | P4 | Resolved by TD-016 squash |

### 2. Database (validado por @data-engineer)

| ID | Debito | Severidade | Horas | Prioridade | Status |
|----|--------|------------|-------|------------|--------|
| TD-019 | Missing composite index `pncp_raw_bids (uf, modalidade_id, data_publicacao DESC) WHERE is_active=true` -- 50-70% query speedup | High | 1 | P0 | Open |
| TD-020 | pncp_raw_bids soft-delete bloat -- `is_active=false` rows never cleaned | High | 3 | P0 | Open -- investigate if any rows exist with is_active=false |
| TD-021 | profiles.plan_type CHECK vs FK -- dual definition, no referential integrity | Medium | 4 | P1 | Open (downgraded from High per @data-engineer) |
| TD-022 | pncp_raw_bids.content_hash COMMENT says MD5 but code uses SHA-256 -- stale documentation only | Low | 0.5 | P3 | Open (downgraded from High -- DRAFT was factually wrong) |
| TD-023 | Missing covering index user_subscriptions (user_id, created_at DESC) WHERE is_active | Medium | 1 | P2 | Open |
| TD-024 | Missing index audit_events (target_id_hash) | Medium | 1 | P2 | Open |
| TD-025 | stripe_webhook_events sem retention policy -- unbounded growth | Medium | 0.5 | P1 | Open |
| TD-026 | alert_sent_items sem retention policy -- unbounded growth | Medium | 0.5 | P1 | Open |
| TD-027 | trial_email_log sem retention policy -- low volume, 1yr retention sufficient | Low | 0.5 | P2 | Open (downgraded per @data-engineer) |
| TD-028 | audit_events hash sem versioning column | Low | 0.5 | P3 | Open (downgraded per @data-engineer) |
| TD-029 | Alert cron job sequential (1000 alerts = 60-100s) -- needs asyncio.gather | Medium | 2 | P1 | Open |
| TD-030 | RLS policy docs incompletas -- shared_analyses + pncp_raw_bids gaps | Low | 2 | P2 | Open (downgraded -- migration 20260404 addressed most gaps) |
| TD-031 | Organizations cascade RESTRICT orphan risk | Low | 0.5 | P3 | Open -- zero orgs in prod |
| TD-032 | conversations/messages sem soft-delete -- LGPD compliance future | Low | 4 | P3 | Open |
| TD-033 | **Supabase FREE tier 500MB vs ~3GB datalake -- imminent storage exhaustion** | **High / P0** | 0.5 | **P0** | **URGENT** (upgraded from Low per @data-engineer + QA) |
| TD-034 | Backup: daily only, 1-day retention, no PITR, no independent backup | Medium | 2 | P1 | Open (upgraded from Low per @data-engineer) |
| TD-NEW-001 | health_checks table no retention despite COMMENT saying 30-day -- ~43K rows/month growth | Low | 0.5 | P1 | New (@data-engineer) -- bundle with TD-025/026/027 |
| TD-NEW-002 | purge_old_bids() does not clean is_active=false rows -- may be vestigial pattern | Medium | 1 | P1 | New (@data-engineer) -- investigate first |
| TD-NEW-003 | datalake_query.py in-memory cache has no Prometheus observability | Low | 2 | P3 | New (@data-engineer) |

### 3. Frontend/UX (validado por @ux-design-expert)

| ID | Debito | Severidade | Horas | Prioridade | Status |
|----|--------|------------|-------|------------|--------|
| TD-035 | useSearchFilters() 607 lines -- extractable into 5 hooks (form, validation, persistence, analytics, sector data) | Medium | 14 | P1 | Open (downgraded from High per QA -- functional, well-structured) |
| TD-036 | Visual regression testing ausente -- no Percy/Chromatic | Medium | 18 | P2 | Open -- recommend Chromatic (free tier 5K snapshots) |
| TD-037 | Saved filter presets ausente -- power users lose time reconfiguring | Medium | 22 | P2 | Open -- user-facing value |
| TD-038 | Modal focus trap edge cases -- DeepAnalysisModal portal conflict, TrialConversion no returnFocus, BottomNav no trap | Medium-Low | 5 | P2 | Open |
| TD-039 | Small touch targets (<44px) in 3 legacy components (FeedbackButtons, CompatibilityBadge, TrialUpsellCTA) | Medium | 3 | P2 | Open |
| TD-040 | /planos e /pricing not true duplicates -- /pricing has ROI calculator | Low | 2.5 | P3 | Open (downgraded -- canonical tag sufficient) |
| TD-041 | Raw hex colors (~89 occurrences) vs design tokens -- mostly in legal/error pages | Low | 9 | P4 | Open |
| TD-042 | CSP unsafe-inline for Tailwind -- accepted industry tradeoff | Low | 0 | P4 | Accepted |
| TD-043 | Component Storybook ausente -- 65+ components without visual catalog | Low | 28 | P4 | Open -- defer unless team grows to 3+ FE devs |
| TD-044 | Icons missing aria-hidden in older components -- 90 usages correct, gap is partial | Low | 3.5 | P4 | Open |
| TD-045 | Sonner toast live regions -- default aria-live="polite" correct, edge case for error toasts | Low | 1.5 | P4 | Open |
| TD-046 | Scroll jank during SSE updates (mobile) -- no debounce/virtualization, use useDeferredValue instead | Medium-Low | 10 | P3 | Open (upgraded from Low per @ux-expert) |
| TD-047 | Bottom nav covers content -- only comparador has pb-20, other pages may clip | Low | 2.5 | P4 | Open |
| TD-048 | i18n ausente -- Brazil-only product, correct to defer | Low | 100 | P4 | Deferred |
| TD-049 | Offline support (Service Worker) ausente -- SaaS web app, low demand | Low | 50 | P4 | Deferred |
| TD-050 | **useSearchExecution.ts 852 lines** -- largest hook, handles API calls + errors + retry + SSE + analytics | Medium-High | 18 | P1 | New (@ux-expert) |
| TD-051 | Search hooks total complexity -- 3,775 lines across 13 hooks, steep onboarding curve | Medium | 16 | P2 | New (@ux-expert) -- 4h docs + 12h simplification |
| TD-052 | FeedbackButtons touch target ~28x28px (needs 44x44px) -- appears on every result card | Medium | 1.5 | P1 | New (@ux-expert) -- quick win |
| TD-053 | CompatibilityBadge text-[10px] below 12px minimum -- mobile readability | Low | 0.5 | P3 | New (@ux-expert) |
| TD-054 | 5 inconsistent error boundary implementations -- varying UI/a11y/recovery patterns | Low | 5 | P3 | New (@ux-expert) |
| TD-055 | Missing bottom padding for BottomNav on multiple pages -- content clipped on mobile | Low | 2.5 | P4 | New (@ux-expert) |

### 4. Cross-Cutting / QA (validado por @qa)

| ID | Debito | Severidade | Horas | Prioridade | Status |
|----|--------|------------|-------|------------|--------|
| TD-056 | Frontend a11y testing ausente -- no jest-axe in CI for top 10 components | Medium | 14 | P2 | New (@qa) |
| TD-057 | Flaky test tracking/quarantine mechanism absent for 5,131+ backend tests | Low | 8 | P3 | New (@qa) |
| TD-058 | Dependency vulnerability scanning absent -- no pip-audit or npm audit in CI | Medium | 4 | P2 | New (@qa) |
| TD-059 | **RPC auth.uid() validation audit** -- unknown how many user-scoped RPCs lack validation | Medium | 4 | P1 | New (@qa) -- informs TD-005 scope |
| TD-060 | GitHub secret scanning + SAST absent in CI | Low | 6 | P3 | New (@qa) |
| TD-061 | **Ingestion pipeline failure alerting absent** -- no Slack/PagerDuty notification when daily crawl fails | Medium | 3 | P1 | New (@qa) |

---

## Matriz de Priorizacao Final

Sorted by priority, then by estimated hours (quick wins first within each tier).

| Prio | ID | Debito | Area | Horas | Notas |
|------|----|--------|------|-------|-------|
| **P0** | TD-033 | Supabase FREE tier storage exhaustion | DB/Infra | 0.5 | URGENT -- may already exceed 500MB. Budget decision. |
| **P0** | TD-019 | Missing composite index pncp_raw_bids | DB | 1 | CREATE INDEX CONCURRENTLY -- 50-70% query speedup |
| **P0** | TD-020 | pncp_raw_bids soft-delete bloat | DB | 3 | Investigate is_active=false existence first |
| **P0** | TD-025/026/027 + TD-NEW-001 | 4 retention policies missing (stripe_webhook, alert_sent, trial_email, health_checks) | DB | 2 | Bundle in 1 migration with 4 cron.schedule() calls |
| **P1** | TD-052 | FeedbackButtons touch target 28px -> 44px | Frontend | 1.5 | Quick win, a11y compliance, every result card |
| **P1** | TD-034 | Weekly pg_dump to S3 + PITR via Pro tier | DB/Infra | 2 | Requires TD-033 first |
| **P1** | TD-029 | Alert cron sequential -> asyncio.gather(10) | Backend | 2 | Independent, backend-only |
| **P1** | TD-061 | Ingestion failure alerting (Slack webhook) | Infra | 3 | Independent, no code dependencies |
| **P1** | TD-021 | plan_type CHECK -> FK migration (NOT VALID + VALIDATE) | DB | 4 | Off-peak execution, verify no orphan values first |
| **P1** | TD-059 | RPC auth.uid() validation audit | Security | 4 | Informs TD-005 scope |
| **P1** | TD-050 | useSearchExecution 852 lines -> 3 hooks | Frontend | 18 | Before TD-035 (shared patterns) |
| **P1** | TD-035 | useSearchFilters 607 lines -> 5 hooks | Frontend | 14 | After TD-050 |
| **P1** | TD-NEW-002 | purge_old_bids() ignores is_active=false | DB | 1 | Investigate vestigial pattern |
| **P1** | TD-005 | Per-user Supabase tokens (SYS-023) | Backend | 16 | After TD-059 audit defines scope |
| **P2** | TD-015 | Railway 120s vs Gunicorn 180s timeout mismatch | Backend | 2 | Silent request death, no Sentry trace |
| **P2** | TD-006 | Exchange rate USD/BRL hardcoded | Backend | 2 | Low user impact |
| **P2** | TD-011 | Single-worker no auto-scaling | Backend/Infra | 4 | Latency cliff under load |
| **P2** | TD-023 | Missing covering index user_subscriptions | DB | 1 | Small optimization |
| **P2** | TD-024 | Missing index audit_events target_id_hash | DB | 1 | Admin investigation improvement |
| **P2** | TD-027 | trial_email_log retention (1yr) | DB | 0.5 | Low volume, non-urgent |
| **P2** | TD-030 | RLS policy documentation gaps | DB | 2 | Documentation-only changes |
| **P2** | TD-039 | Touch targets <44px (3 components) | Frontend | 3 | a11y compliance |
| **P2** | TD-058 | Dependency vulnerability scanning in CI | Security | 4 | pip-audit + npm audit |
| **P2** | TD-038 | Modal focus trap edge cases | Frontend | 5 | a11y, low frequency |
| **P2** | TD-007 | quota.py oversized (1,660 LOC) | Backend | 12 | Refactor into submodules |
| **P2** | TD-008 | consolidation.py oversized (1,394 LOC) | Backend | 8 | Refactor into submodules |
| **P2** | TD-009 | llm_arbiter.py oversized (1,362 LOC) | Backend | 8 | Refactor into submodules |
| **P2** | TD-056 | jest-axe a11y testing in CI | Frontend | 14 | Top 10 components |
| **P2** | TD-051 | Search hooks total complexity documentation + simplification | Frontend | 16 | Architecture docs + state machine |
| **P2** | TD-036 | Visual regression testing (Chromatic) | Frontend | 18 | 10 critical screens |
| **P2** | TD-037 | Saved filter presets feature | Frontend | 22 | User-facing value for consultancies |
| **P3** | TD-022 | content_hash COMMENT fix (MD5 -> SHA-256) | DB | 0.5 | Documentation-only |
| **P3** | TD-028 | audit_events hash versioning column | DB | 0.5 | Theoretical, low value |
| **P3** | TD-031 | Organizations cascade orphan risk | DB | 0.5 | Zero orgs in production |
| **P3** | TD-053 | CompatibilityBadge text-[10px] readability | Frontend | 0.5 | Quick fix |
| **P3** | TD-012 | Cryptography fork-safe testing in CI | Backend | 2 | Risk only on dep upgrade |
| **P3** | TD-013 | PNCP health canary limited detection | Backend | 2 | Canary update |
| **P3** | TD-040 | /planos vs /pricing canonical tag | Frontend | 2.5 | SEO-only |
| **P3** | TD-014 | Cache hit rate marginal (65-75%) | Backend | 4 | Warming strategy |
| **P3** | TD-032 | conversations sem soft-delete (LGPD future) | DB | 4 | Only if compliance mandates |
| **P3** | TD-054 | 5 inconsistent error boundary patterns | Frontend | 5 | Shared BaseErrorBoundary |
| **P3** | TD-060 | GitHub secret scanning + SAST in CI | Security | 6 | Long-term improvement |
| **P3** | TD-057 | Flaky test tracking/quarantine | Testing | 8 | Development velocity |
| **P3** | TD-046 | Scroll jank SSE mobile (useDeferredValue) | Frontend | 10 | Effective > virtualization |
| **P3** | TD-016 | 121 migrations squash -> ~10 files | DB | 24 | MUST be LAST after all other migrations |
| **P3** | TD-NEW-003 | datalake_query cache Prometheus observability | Backend | 2 | Metrics for hit/miss/size |
| **P4** | TD-017 | OpenTelemetry HTTP-only | Backend | 0 | Accepted limitation |
| **P4** | TD-018 | Dual migration naming | DB | 0 | Resolved by TD-016 |
| **P4** | TD-042 | CSP unsafe-inline for Tailwind | Frontend | 0 | Accepted risk |
| **P4** | TD-045 | Sonner toast live regions edge case | Frontend | 1.5 | Minor a11y |
| **P4** | TD-047 | Bottom nav covers content | Frontend | 2.5 | CSS fix |
| **P4** | TD-055 | Missing bottom padding multiple pages | Frontend | 2.5 | Global CSS fix |
| **P4** | TD-044 | Icons missing aria-hidden (partial) | Frontend | 3.5 | Minor a11y |
| **P4** | TD-041 | Raw hex colors vs design tokens (~89 occurrences) | Frontend | 9 | Mostly legal/error pages |
| **P4** | TD-043 | Storybook ausente (65+ components) | Frontend | 28 | Defer unless team grows |
| **P4** | TD-049 | Offline support (Service Worker) | Frontend | 50 | No user demand |
| **P4** | TD-048 | i18n ausente | Frontend | 100 | Brazil-only product |

---

## Plano de Resolucao (5 Fases)

### Phase 1: Quick Wins (Week 1-2) -- ~8h

**Objective:** Eliminate immediate operational risks and ship low-effort/high-value fixes.

**Track A -- DB/Infra (no dependencies):**
| Item | Hours | Action |
|------|-------|--------|
| TD-033 | 0.5 | Upgrade Supabase to Pro tier. Run `pg_database_size()` before/after. |
| TD-019 | 1 | `CREATE INDEX CONCURRENTLY idx_pncp_raw_bids_dashboard_query ON pncp_raw_bids (uf, modalidade_id, data_publicacao DESC) WHERE is_active = true` |
| TD-025/026/027 + TD-NEW-001 | 2 | Single migration with 4 `cron.schedule()` retention jobs (90d webhooks, 90d alerts, 1yr trial emails, 30d health_checks) |
| TD-022 | 0.5 | Update `COMMENT ON COLUMN content_hash` from MD5 to SHA-256 |

**Track B -- Frontend (parallel):**
| Item | Hours | Action |
|------|-------|--------|
| TD-052 | 1.5 | Add `min-w-[44px] min-h-[44px]` to FeedbackButtons |
| TD-053 | 0.5 | Change CompatibilityBadge `text-[10px]` to `text-xs` |

**Track C -- Security (parallel):**
| Item | Hours | Action |
|------|-------|--------|
| TD-059 | 4 | Audit all Supabase RPCs for auth.uid() validation. Document findings. |

**Subtotal: ~10h across 3 parallel tracks. Elapsed: ~4h if all tracks run in parallel.**

### Phase 2: Foundation (Weeks 3-6) -- ~16h

| Item | Hours | Dependencies | Action |
|------|-------|-------------|--------|
| TD-034 | 2 | TD-033 (Pro tier) | GitHub Actions workflow for weekly pg_dump to S3. Enable PITR on Pro. |
| TD-020 + TD-NEW-002 | 3 | None | Verify `SELECT count(*) FROM pncp_raw_bids WHERE is_active=false`. If >0, add cleanup cron. If 0, consider dropping is_active column. |
| TD-021 | 4 | Verify no orphan plan_types | Three-step FK migration: drop CHECK, add FK NOT VALID, VALIDATE. |
| TD-029 | 2 | None | asyncio.gather with Semaphore(10) for alert cron. Separate email batching. |
| TD-061 | 3 | None | Sentry alert rule or Slack webhook on ingestion_runs failure. |
| TD-015 | 2 | None | Align timeouts: set `GUNICORN_TIMEOUT=110` (< Railway 120s). Add Railway timeout detection middleware. |

### Phase 3: Hardening (Weeks 5-8) -- ~54h

**Track A -- Frontend Refactoring:**
| Item | Hours | Dependencies | Action |
|------|-------|-------------|--------|
| TD-050 | 18 | None | Split useSearchExecution into useSearchAPI, useSearchErrorHandling, useSearchPartialResults |
| TD-035 | 14 | TD-050 (shared patterns) | Split useSearchFilters into 5 hooks: FormState, Validation, Persistence, Analytics, SectorData |
| TD-037 | 22 | TD-035 (cleaner hook surface) | Implement saved filter presets: Supabase table + dropdown UX + 10 preset limit |

**Track B -- Backend Refactoring (parallel):**
| Item | Hours | Dependencies | Action |
|------|-------|-------------|--------|
| TD-007 | 12 | None | Split quota.py into quota_core, quota_atomic, plan_enforcement |
| TD-008 | 8 | None | Split consolidation.py into source_merger, dedup, priority_resolver |

### Phase 4: Polish (Weeks 9-12) -- ~40h

| Item | Hours | Dependencies | Action |
|------|-------|-------------|--------|
| TD-036 | 18 | None | Chromatic setup with 10 critical screen snapshots. CI integration. |
| TD-056 | 14 | None | jest-axe for top 10 components. CI gate. |
| TD-058 | 4 | None | pip-audit + npm audit in CI workflow. |
| TD-009 | 8 | None | Split llm_arbiter.py into classification, zero_match, prompt_builder |

### Phase 5: Long-term (Weeks 13-20+) -- ongoing

| Item | Hours | Notes |
|------|-------|-------|
| TD-016 | 24 | Migration squash -- MUST be after all Phase 1-4 migrations merged |
| TD-005 | 16 | Per-user tokens -- scope defined by TD-059 audit results |
| TD-051 | 16 | Search hooks architecture docs + state machine (XState) |
| TD-011 | 4 | Railway auto-scaling configuration |
| TD-046 | 10 | useDeferredValue for SSE streaming + React.memo on ResultCard |
| TD-043 | 28 | Storybook -- only if team grows to 3+ FE devs |
| TD-048/049 | 150 | i18n + offline -- deferred, no current demand |
| Others | ~30 | P3/P4 items addressed opportunistically |

---

## Riscos Cruzados

From @qa Phase 7 review -- cross-area risks where debts compound:

| # | Risco | Areas | Severidade | Mitigacao |
|---|-------|-------|------------|-----------|
| 1 | **DB storage exhaustion cascade:** TD-033 + TD-020 + TD-025/026/027 = storage fills, ingestion fails, search returns stale/empty results | DB, Backend, Frontend | Critical | TD-033 (Pro tier) FIRST, then retention crons. **Execute this week.** |
| 2 | **Silent request death:** TD-015 (Railway 120s kills) + TD-011 (single worker blocks) = long searches die with no Sentry trace, users see generic 504 | Backend, Infra | High | Align timeouts (TD-015), add timeout detection middleware |
| 3 | **Data loss without recovery:** TD-034 (no PITR) + TD-033 (FREE tier) = if Supabase incident, no independent recovery path | DB, Infra | High | Pro upgrade enables PITR. Add pg_dump to S3. |
| 4 | **Search page maintainability cliff:** TD-035 (607 LOC) + TD-050 (852 LOC) + TD-051 (3,775 total) = any search feature change requires understanding 3,775 lines of interconnected hooks | Frontend | Medium | Planned refactoring order: TD-050 first, then TD-035 |
| 5 | **Security audit readiness:** TD-005 (service_role) + TD-030 (incomplete RLS docs) + TD-059 (no RPC audit) = cannot pass security audit | Backend, DB | Medium | RPC audit (TD-059) first, document (TD-030), then migrate tokens (TD-005) |
| 6 | **Mobile UX degradation:** TD-046 (SSE jank) + TD-052 (touch targets) + TD-047/055 (BottomNav padding) = mobile experience materially worse than desktop | Frontend | Medium | Bundle mobile fixes into single sprint (4-6h total) |

---

## Criterios de Sucesso

### Performance Benchmarks

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| `search_datalake` RPC latency (p50) | Needs baseline | 50-70% reduction after TD-019 | `EXPLAIN ANALYZE` before/after |
| PNCP API availability | 94% | >= 95% | Prometheus `smartlic_pncp_health_*` |
| Cache hit rate | 65-75% | >= 75% sustained | Prometheus `smartlic_cache_hit_rate` |
| DB size | ~500MB (estimate) | Monitored, < 80% of tier limit | `pg_database_size()` weekly |
| Search page hooks total lines | 3,775 | < 2,500 after refactoring | `wc -l frontend/app/buscar/hooks/*.ts` |

### Coverage Thresholds

| Area | Current | Target | Gate |
|------|---------|--------|------|
| Backend test coverage | >= 70% (CI gate) | Maintain >= 70% | `pytest --cov` |
| Frontend test coverage | >= 60% (CI gate) | Maintain >= 60% | `npm run test:coverage` |
| a11y automated coverage | 0% | >= 80% of top 10 components | jest-axe after TD-056 |
| Visual regression | 0% | 10 critical screens | Chromatic after TD-036 |
| Dependency vulnerability scan | Not in CI | 0 high/critical findings | pip-audit + npm audit after TD-058 |

### Security Targets

| Check | Current | Target |
|-------|---------|--------|
| RPCs with auth.uid() validation | Unknown | 100% of user-scoped RPCs (after TD-059) |
| Dependencies with known CVEs | Unknown | 0 high/critical (after TD-058) |
| Secrets in git history | Unknown | 0 (after TD-060) |

---

## Dependencias

### Resolution Order (DAG -- no circular dependencies)

```
PHASE 1 (Week 1-2, parallel tracks):
  TD-033 Supabase Pro ────────> unblocks TD-034 (PITR + backup)
  TD-019 composite index ────> no dependencies, ship immediately
  TD-025/026/027 + NEW-001 ──> retention crons, bundle in 1 migration
  TD-022 COMMENT fix ────────> ship with retention migration
  TD-052 FeedbackButtons ───> ship independently (1.5h)
  TD-059 RPC audit ─────────> informs TD-005 scope

PHASE 2 (Weeks 3-6):
  TD-034 pg_dump to S3 ─────> requires TD-033
  TD-020 + NEW-002 investigate > must precede TD-016 (squash)
  TD-021 plan_type FK ──────> must precede TD-016 (squash)
  TD-029 alert cron async ──> independent
  TD-061 ingestion alerting > independent
  TD-015 timeout alignment ─> independent

PHASE 3 (Weeks 7-12):
  TD-050 useSearchExecution split ──> before TD-035
  TD-035 useSearchFilters split ───> after TD-050, before TD-037
  TD-037 saved filter presets ─────> after TD-035
  TD-007/008/009 backend splits ──> independent, parallel with FE

PHASE 4 (Weeks 9-12):
  TD-036 visual regression ────> parallel with Phase 3
  TD-056 jest-axe ─────────────> independent
  TD-058 dep scanning ────────> independent

PHASE 5 (Weeks 13-20+):
  TD-016 migration squash ────> AFTER all Phase 1-4 migrations merged
  TD-005 per-user tokens ─────> after TD-059 defines scope
  Remaining P3/P4 items ──────> opportunistic
```

### Parallelization Tracks

| Track A (DB/Infra) | Track B (Frontend) | Track C (Security/CI) |
|--------------------|--------------------|-----------------------|
| TD-033 Pro upgrade | TD-052 touch targets | TD-059 RPC audit |
| TD-019 composite index | TD-050 hook split | TD-058 dep scanning |
| TD-025/026/027 retention | TD-035 hook split | TD-061 alerting |
| TD-034 pg_dump backup | TD-037 saved presets | TD-060 secret scanning |
| TD-020 bloat cleanup | TD-036 visual regression | |
| TD-021 FK migration | TD-056 jest-axe | |

Three parallel tracks can execute simultaneously if staffed.

---

## Legenda

- **P0** -- Proximo sprint, impacto imediato (blocker ou risk)
- **P1** -- 1-2 meses, alto impacto
- **P2** -- 2-4 meses, melhorias incrementais
- **P3** -- 4-6 meses, nice-to-have
- **P4** -- Backlog, limitacoes aceitas ou baixa prioridade

---

*Phase 8 Final Assessment compiled 2026-04-08 by @architect (Aria).*
*Incorporates all feedback from @data-engineer (Phase 5), @ux-design-expert (Phase 6), and @qa (Phase 7).*
*This document supersedes `technical-debt-DRAFT.md` and the previous v1.0 (2026-03-31).*
*Next step: Story creation from P0/P1 items for sprint planning.*
