# Epic: Resolucao de Debitos Tecnicos — SmartLic v0.5

## Metadata
- **Epic ID:** EPIC-DEBT
- **Status:** Draft
- **Prioridade:** Alta
- **Estimativa Total:** ~340 horas (~42.5 dias de engenharia)
- **Orcamento:** R$ 51.000 (R$150/h)
- **Timeline:** 8-12 semanas (4 fases)
- **Assessment base:** `docs/prd/technical-debt-assessment.md` FINAL v1.0 (2026-03-09)
- **Executive report:** `docs/reports/TECHNICAL-DEBT-REPORT.md`
- **Owner:** @pm
- **Supersedes:** Epic anterior (2026-03-07, baseado em assessment com 107 debitos e IDs DB-0xx/FE-0xx/SYS-0xx antigos)

> **NOTA:** Este epic esta alinhado com o assessment FINAL v1.0 que usa IDs SYS-001..037, DB-001..NEW-04, FE-001..NEW-04, QA-NEW-01..GAP-01. Os IDs antigos (DB-013/DB-038 etc) do epic anterior sao obsoletos.

## Objetivo

Eliminar os 80 debitos tecnicos ativos identificados no Brownfield Discovery de 10 fases, priorizando seguranca (CVSS 9.1 token collision, JWT modernization), estabilidade (PNCP silent 400, LLM truncation, SIGSEGV crashes), e integridade de dados (FK inconsistencies, retention gaps). O resultado e um SmartLic enterprise-ready para conversao de trials e escala B2G, com zero debitos CRITICAL/HIGH, cobertura de testes expandida, e arquitetura sustentavel.

## Escopo

### Incluido
- **Batch A (Quick Wins):** 12 items de <2h cada — verificacoes DB, retention jobs, a11y fixes, dependency hygiene (~7h)
- **Batch B (Foundation):** 8 items P0/P1 — security fixes, PNCP compliance, LLM resilience, error boundaries (~46h)
- **Batch C (Optimization):** 12 items P2 — CSP hardening, buscar decomposition, httpx migration, QA automation (~134h)
- **Batch D (Long-term):** 39+ items P3/P4 — SSE simplification, filter decomposition, test coverage, MFA (~224h)

### Excluido
- Features novas (alertas, organizacoes multi-tenant, novos setores)
- Storybook/visual regression testing (FE-021/FE-022 — backlog quando team 3+ devs)
- Items INFO-only (DB-INFO-01, DB-INFO-03, DB-INFO-04 — 2.5h, documentacao)
- Rewrite completo de SSE architecture (FE-003 e simplificacao, nao rewrite)
- Greenfield alternatives para qualquer modulo

## Criterios de Sucesso

| Metrica | Baseline Atual | Target Pos-Batch B | Target Pos-Batch D | Prazo |
|---------|:---:|:---:|:---:|:---:|
| Debitos CRITICAL ativos | 5 | 0 | 0 | Batch B |
| Debitos HIGH ativos | 19 | <10 | 0 | Batch C/D |
| Backend test pass rate | 5131+ | 5131+ (0 fail) | 5500+ | Continuous |
| Backend coverage (global) | 70% | 70% | 80% | Batch D |
| Backend coverage (auth, billing, search_pipeline) | Desconhecido | 60% min | 70% min | Batch D |
| Frontend test pass rate | 2681+ | 2681+ (0 fail) | 3000+ | Continuous |
| Frontend coverage (branches) | ~50% | 55% | 60% | Batch D |
| E2E a11y audits (axe-core) | 0 specs | 5 core flows | 10+ flows | Batch C |
| LLM JSON parse success rate | ~70-80% | >99% | >99.5% | Batch B |
| DB FK consistency (profiles) | ~70% | 100% | 100% | Batch B |
| Zero CSP unsafe-inline | No | No | Yes | Batch C |

## Stories

| Story ID | Titulo | Batch | Prioridade | Horas | Dependencias |
|----------|--------|:---:|:---:|:---:|-------------|
| DEBT-100 | DB Quick Wins — Integrity, Retention & Indexes | A | P0-P2 | 7h | Nenhuma |
| DEBT-101 | Security Critical — Token Hash, SIGSEGV & LLM Truncation | B | P0 | 12h | Nenhuma |
| DEBT-102 | Security & Auth — JWT Rotation & PNCP Compliance | B | P1 | 16h | DEBT-101 (SYS-004 before SYS-005) |
| DEBT-103 | LLM & Search Resilience — Timeouts, Cache Bounds & UF Batching | B | P1-P2 | 24h | Nenhuma |
| DEBT-104 | DB Foundation — FK Standardization & Retention | B | P1 | 8h | DEBT-100 (query results inform scope) |
| DEBT-105 | Frontend Error Boundaries & A11Y Quick Wins | A/B | P1-P2 | 8h | Nenhuma |
| DEBT-106 | Frontend Architecture — Buscar Decomposition & Component Consolidation | C | P2 | 46h | Nenhuma |
| DEBT-107 | Backend Architecture — main.py Decomposition & httpx Migration | C | P2 | 48h | Nenhuma |
| DEBT-108 | Frontend Security & Performance — CSP Nonce & Dynamic Imports | C | P2 | 24h | Nenhuma |
| DEBT-109 | QA Automation — axe-core, OpenAPI Snapshot & Conftest Cleanup | C | P2 | 16h | Nenhuma |
| DEBT-110 | Backend Resilience & Observability — Circuit Breakers, Caching & Monitoring | D | P3 | 80h | DEBT-107 (SYS-008 enables SYS-027) |
| DEBT-111 | Frontend Quality & Long-term — Test Coverage, SSE, SVGs & Cleanup | D | P3-P4 | 120h+ | DEBT-106 (FE-001 enables FE-012/016) |

## Timeline

### Sprint 1 (Semanas 1-2): Quick Wins + Security Critical
- **DEBT-100** — DB Quick Wins (7h) — @data-engineer
- **DEBT-101** — Security Critical P0 (12h) — @dev
- **DEBT-105** — FE Error Boundaries + A11Y (8h) — @dev + @ux-design-expert

**Esforco Sprint 1: ~27h | Pre-requisito: Executar SQL diagnostics (Condicao 1 do QA Gate) e baselines de testes (Condicao 2)**

### Sprint 2-3 (Semanas 3-6): Foundation
- **DEBT-102** — JWT Rotation + PNCP (16h) — @dev
- **DEBT-103** — LLM & Search Resilience (24h) — @dev
- **DEBT-104** — DB FK Standardization (8h) — @data-engineer

**Esforco Sprint 2-3: ~48h**

### Sprint 4-6 (Semanas 7-10): Optimization
- **DEBT-106** — FE Architecture (46h) — @dev + @ux-design-expert
- **DEBT-107** — Backend Architecture (48h) — @architect + @dev
- **DEBT-108** — FE Security & Performance (24h) — @dev
- **DEBT-109** — QA Automation (16h) — @qa + @devops

**Esforco Sprint 4-6: ~134h**

### Sprint 7+ (Semanas 11-12+): Excellence
- **DEBT-110** — Backend Resilience (80h) — @dev + @architect
- **DEBT-111** — Frontend Quality (120h+) — @dev + @qa

**Esforco Sprint 7+: ~200h+**

## Riscos

| # | Risco | Prob. | Impacto | Mitigacao |
|---|-------|:---:|:---:|-----------|
| R-01 | SYS-004 token hash fix invalida cached sessions | Alta | HIGH | Deploy em 2-4 AM BRT; dual-hash lookup (old+new) por 1h transicao; monitorar p99 latency |
| R-02 | FE-010 CSP nonce breaks third-party scripts (Stripe, Sentry, Mixpanel, Clarity) | Alta | CRITICAL | Feature flag; testar cada 3rd-party individualmente; rollback = revert single middleware line |
| R-03 | DB-001 FK migration breaks auth flow | Media | CRITICAL | NOT VALID + VALIDATE pattern; orphan detection PRE-migration; rollback migration ready |
| R-04 | FE-001 buscar refactor introduces state bugs | Media | HIGH | Extract incrementally (1 hook per PR); full E2E pass before AND after |
| R-05 | SYS-002 LLM token fix changes classification behavior | Media | HIGH | Golden samples test before/after; compare acceptance rates; gradual rollout |
| R-06 | Retention jobs delete debugging evidence | Baixa | MEDIUM | Retention jobs check for open incidents before purging |

## Pre-requisitos (QA Gate Conditions)

Antes de iniciar qualquer fix:

1. **MUST:** Executar 5 SQL diagnostics em producao (ver assessment secao "Condicoes do QA Gate")
2. **MUST:** Estabelecer baselines de testes (backend, frontend, E2E, coverage, bundle size, LLM golden samples)
3. **Aplicado:** FE-010 movido de P1 para P2 (risco de regressao alto demais para sprint com P0 fixes)
4. **Aplicado:** DB-NEW-03 incluido no Batch A como quick win de retention

## Definition of Done (Epic)

- [ ] Zero debitos CRITICAL ativos
- [ ] Zero debitos HIGH ativos
- [ ] Backend coverage >= 80%
- [ ] Frontend coverage >= 65% (lines), >= 60% (branches)
- [ ] E2E axe-core audits em 10+ flows
- [ ] Todos os testes passando (0 failures em backend, frontend, E2E)
- [ ] OpenAPI schema snapshot enforced em CI
- [ ] DB FK consistency 100% (todas tabelas referenciam profiles, nao auth.users)
- [ ] Retention policies em todas tabelas de alta volumetria
- [ ] Documentacao atualizada (CLAUDE.md, PRD.md, CHANGELOG.md)

---

*Epic criado por @pm durante Brownfield Discovery Phase 10 — Planning*
*Baseado no Technical Debt Assessment FINAL v1.0 (2026-03-09)*
*Validado por @architect, @data-engineer, @ux-design-expert, @qa*
