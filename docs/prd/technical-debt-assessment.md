# Technical Debt Assessment — FINAL (Consolidado)

**Data:** 2026-03-10
**Status:** FINAL — Validado por @data-engineer, @ux-design-expert, @qa
**Projeto:** SmartLic v0.5
**Objetivo:** Inventário validado de debt real para gerar stories que elevam GTM score de 7.9 para 9+

---

## Executive Summary

Após 3 fases de coleta (architect, data-engineer, ux-expert) e 3 fases de validação (specialist reviews + QA), o inventário de debt foi **reduzido de 93 para 28 itens ativos**.

- **65 itens resolvidos** (DEBT-100 a DEBT-111, migrações 20260304-20260309)
- **28 itens ativos** (~20-25 dias de trabalho)
- **1 GTM-BLOCKER** (error boundaries em páginas autenticadas — 4h)
- **0 P0** (todos os P0 originais resolvidos)
- **Score atual:** 7.9/10 → **Score alvo:** 9.0/10

---

## Inventário Validado (28 itens ativos)

### GTM-BLOCKER (resolver antes de lançar)

| ID | Débito | Área | Horas | Score Impact | Validado por |
|----|--------|------|-------|--------------|-------------|
| **FE-NEW-03** | Error boundaries em dashboard, pipeline, historico — usuário perde estado em exceção não tratada | Frontend | 4h | UX 8→9 | @ux + @qa |

### GTM-RISK (resolver em 30 dias pós-launch)

| ID | Débito | Área | Horas | Score Impact | Validado por |
|----|--------|------|-------|--------------|-------------|
| **DB-001** | Verificar FK state em produção (search_results_cache, classification_feedback) | DB | 1h | Integrity 7→8 | @data-engineer |
| **DB-032** | Fix fresh-install FK ordering para classification_feedback | DB | 1h | Integrity 7→8 | @data-engineer |
| **DB-013** | Migrar billing.py off plans.stripe_price_id legacy column | DB | 4h | Integrity 7→8 | @data-engineer |
| **DB-INFO-03** | Documentar estratégia de backup/PITR em ops runbook | DB | 1h | Integrity 7→8 | @data-engineer |
| **DB-006** | alert_preferences auth.role() → TO service_role | DB | 1h | Security 9→10 | @data-engineer + @qa |
| **ARCH-001** | routes/search.py 2177 LOC decomposição (SSE, state machine, retry) | Backend | 16h | Maint 6→8 | @architect + @qa |
| **FE-006** | Documentar convenção de component directories + mover 3-4 arquivos | Frontend | 4-6h | Maint 6→7 | @ux |
| **FE-011** | Render-smoke tests para dashboard, pipeline, historico, onboarding, conta | Frontend | 12-16h | Tests 9→9 | @ux + @qa |
| **FE-TD-023** | Dynamic-import Framer Motion em páginas autenticadas (~70KB) | Frontend | 4-6h | Perf 7→8 | @ux |
| **ARCH-006** | Split SearchForm.tsx (687 LOC) em sub-componentes | Frontend | 6-8h | Maint 6→7 | @ux |
| **QA-NEW-01** | Integration test para user deletion cascade (LGPD) | QA | 4h | Integrity 7→8 | @qa |
| **QA-NEW-02** | CSP style-src 'unsafe-inline' — documentar como accepted risk ou resolver | Frontend | 2h | Security 9→10 | @qa |

### POST-GTM (resolver incrementalmente)

| ID | Débito | Área | Horas | Validado por |
|----|--------|------|-------|-------------|
| **ARCH-002** | search_pipeline.py 17 noqa:F401 re-exports | Backend | 4h | @architect |
| **ARCH-003** | pncp_client.py 14 env vars → config/ | Backend | 2h | @architect |
| **ARCH-004** | Delete config.py.bak, config_legacy.py.bak | Backend | 0.5h | @architect |
| **SYS-030** | filter.py 2141 LOC facade refinement | Backend | 16h | @architect + @qa |
| **FE-003** | SSE proxy documentação + testes (3 fallback paths) | Frontend | 20-24h | @ux + @qa |
| **FE-004** | Coverage 55% → 60% | Frontend | ongoing | @ux + @qa |
| **FE-TD-008** | 96 raw hex colors → Tailwind tokens | Frontend | 6h | @ux |
| **FE-008** | 6 arquivos com raw localStorage (usar safe wrappers) | Frontend | 3h | @ux |
| **FE-009** | Inline SVGs em conta/layout.tsx → Lucide icons | Frontend | 4h | @ux |
| **DB-025** | Analisar index usage em search_results_cache | DB | 2h | @data-engineer |
| **DB-027** | Retention para classification_feedback (24 meses) | DB | 0.5h | @data-engineer |
| **DB-028** | Retention para conversations/messages (24 meses) | DB | 0.5h | @data-engineer |
| **DB-031** | Add search_id a pipeline_items (traceability) | DB | 1h | @data-engineer |
| **DB-INFO-01** | Deprecar backend/migrations/ directory | DB | 0.5h | @data-engineer |
| **FE-A11Y-01** | Loading spinners sem role="status" (parcialmente fixo) | Frontend | 1h | @ux |
| **FE-A11Y-03** | SVGs em conta sem aria-hidden="true" | Frontend | 0.5h | @ux |

---

## Score Projection

| Dimensão | Atual | Após BLOCKER | Após RISK (30d) | Após POST-GTM |
|----------|-------|--------------|-----------------|----------------|
| Segurança | 9 | 9 | **10** (DB-006, QA-NEW-02) | 10 |
| Confiabilidade | 8 | 8 | 8 | 8 |
| Billing | 8 | 8 | **9** (DB-013) | 9 |
| UX/A11y | 8 | **9** (FE-NEW-03) | 9 | **9.5** |
| Performance | 7 | 7 | **8** (FE-TD-023) | 8 |
| Testes | 9 | 9 | 9 | 9 |
| Observabilidade | 9 | 9 | 9 | 9 |
| Integridade | 7 | 7 | **8** (DB-001, QA-NEW-01) | **9** |
| Manutenibilidade | 6 | 6 | **8** (ARCH-001, FE-006) | **9** |
| **TOTAL** | **7.9** | **8.0** | **8.8** | **9.1** |

---

## Batches Recomendados para Stories

| Story | Items | Horas | Fase |
|-------|-------|-------|------|
| **DEBT-112: Error Boundaries** | FE-NEW-03 | 4h | BLOCKER |
| **DEBT-113: DB Integrity Quick Wins** | DB-001, DB-032, DB-006, DB-INFO-03, DB-027, DB-028 | 5h | RISK |
| **DEBT-114: Billing Legacy Cleanup** | DB-013 | 4h | RISK |
| **DEBT-115: Search Route Decomposition** | ARCH-001 | 16h | RISK |
| **DEBT-116: FE Quality & Performance** | FE-TD-023, FE-006, ARCH-006, QA-NEW-02 | 16-20h | RISK |
| **DEBT-117: Page Smoke Tests + LGPD** | FE-011, QA-NEW-01 | 16-20h | RISK |
| **DEBT-118: BE Cleanup** | ARCH-002, ARCH-003, ARCH-004, SYS-030 | 22h | POST-GTM |
| **DEBT-119: FE Polish** | FE-TD-008, FE-008, FE-009, FE-A11Y-01, FE-A11Y-03 | 15h | POST-GTM |
| **DEBT-120: DB Optimization** | DB-025, DB-031, DB-INFO-01 | 3.5h | POST-GTM |

---

*Assessment consolidado por @aios-master — Brownfield Discovery Workflow v3.1 Phase 8*
*Validado por: @data-engineer (Phase 5), @ux-design-expert (Phase 6), @qa (Phase 7)*
*Próximo passo: Fase 10 — Criar stories detalhadas com acceptance criteria*
