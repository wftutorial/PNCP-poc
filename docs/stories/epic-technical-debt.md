# Epic: Resolucao de Debito Tecnico — SmartLic

**Epic ID:** EPIC-TD-001
**Owner:** @pm (Parker)
**Created:** 2026-03-07
**Status:** Draft
**Assessment base:** `docs/prd/technical-debt-assessment.md` FINAL v1.0
**Executive report:** `docs/reports/TECHNICAL-DEBT-REPORT.md` v5.0
**Supersedes:** Epic anterior (2026-03-04, baseado em assessment v3.0 com 69 debitos)

## Objetivo

Resolver os 107 debitos tecnicos identificados no Brownfield Discovery (Phases 1-8), tornando o SmartLic enterprise-ready para conversao de trials e escala B2G. O assessment foi validado por 4 especialistas (@architect, @data-engineer, @ux-design-expert, @qa) com 3 falsos positivos removidos, 8 novos debitos adicionados, e 19 ajustes de severidade.

## Escopo

| Dimensao | Valor |
|----------|-------|
| Total de debitos | 107 (unicos) |
| CRITICAL | 1 |
| HIGH | 24 |
| MEDIUM | 48 |
| LOW | 34 |
| Areas | Sistema (36), Database (42), Frontend (35), Cross-Cutting (7) |
| Esforco estimado | 720-900h (codigo 660-840h + testes 60h) |
| Budget | R$108-135K (R$150/h) |
| Timeline | 8-12 semanas (3 fases) |

## Criterios de Sucesso

| Metrica | Baseline Atual | Meta Final |
|---------|---------------|------------|
| Backend tests | 5774 pass / 0 fail | 5900+ pass / 0 fail |
| Frontend tests | 2681 pass / 0 fail | 2800+ pass / 0 fail |
| E2E tests | 60 pass | 75+ pass |
| Quarantined tests | 22 | 0 |
| CRITICAL debts | 1 | 0 |
| HIGH debts | 24 | 0 |
| loading.tsx coverage | 0/44 pages | 15+/44 pages |
| Error boundaries | 1 page (/buscar) | All authenticated pages |
| RLS full table scans | 3+ | 0 |
| Tables without retention | 6+ | 0 |
| WCAG AA violations | 4+ | 0 |
| Design system primitives | 0 | 6+ (Button, Input, Label, Badge, ...) |
| DR procedure | Undocumented | Documented + quarterly test |
| API contract CI | Not enforced | Enforced (semantic diff) |
| Dep vulnerability scanning | None | CI-enforced, 0 high+ |
| Legacy route hits | Untracked | Tracked, analyzed, zero-hit removed |

## Timeline

### Fase 1: Quick Wins + Fundacao Critica (Semana 1-2) — ~93-101h / ~R$15K

Foco: eliminar riscos imediatos, melhorar experiencia de trial, fundacao de qualidade.

| Story | Titulo | Esforco | Priority |
|-------|--------|---------|----------|
| DEBT-001 | Database Integrity Critical Fixes | 10h | HIGH |
| DEBT-002 | Migration Consolidation & Disaster Recovery | 24h | CRITICAL |
| DEBT-003 | Frontend Loading States & Error Boundaries | 18-20h | HIGH |
| DEBT-004 | Accessibility Quick Wins (WCAG AA) | 7.5h | HIGH |
| DEBT-005 | Frontend Code Hygiene & Quarantine Resolution | 12.5h | MEDIUM |
| DEBT-006 | Design System Foundation (Shared Button) | 4-6h | HIGH |
| DEBT-007 | CI Quality Gates & Test Infrastructure | 14h | HIGH |
| DEBT-008 | Backend Stability & Security Quick Fixes | 19.5h | HIGH |

### Fase 2: Melhorias Estruturais (Semana 3-4) — ~108-120h / ~R$17K

Foco: qualidade, consistencia, preparacao para escala.

| Story | Titulo | Esforco | Priority |
|-------|--------|---------|----------|
| DEBT-009 | Database RLS & Retention Hardening | 18h | HIGH |
| DEBT-010 | Database Schema Guards & Monitoring | 15h | MEDIUM |
| DEBT-011 | Frontend Component Architecture | 24-28h | HIGH |
| DEBT-012 | Frontend Forms, Tokens & Accessibility | 14-16h | MEDIUM |
| DEBT-013 | Frontend Performance Optimization | 16-20h | MEDIUM |
| DEBT-014 | Backend Service Layer & Lifecycle | 19h | MEDIUM |

### Fase 3: Otimizacao (Mes 2-3) — ~230-290h / ~R$39-44K

Foco: medio/baixo impacto com valor de longo prazo.

| Story | Titulo | Esforco | Priority |
|-------|--------|---------|----------|
| DEBT-015 | Backend Architecture Decomposition | 90h | MEDIUM |
| DEBT-016 | Frontend Advanced Refactoring | 82-104h | MEDIUM |
| DEBT-017 | Database Long-Term Optimization | 47h | LOW |
| DEBT-018 | Infrastructure, Security & Observability | 82h | LOW |

## Stories

### Sprint 1 — Semana 1-2

1. **DEBT-001** — Database Integrity Critical Fixes
   - Debts: DB-013, DB-038, DB-039, DB-012, DB-032, DB-047
   - Agent: @data-engineer

2. **DEBT-002** — Migration Consolidation & Disaster Recovery
   - Debts: CROSS-001, DB-025, DB-030, DB-043, DB-026
   - Agent: @data-engineer + @devops

3. **DEBT-003** — Frontend Loading States & Error Boundaries
   - Debts: FE-002, FE-012
   - Agent: @dev + @ux-design-expert

4. **DEBT-004** — Accessibility Quick Wins (WCAG AA)
   - Debts: FE-034, FE-022, FE-021
   - Agent: @ux-design-expert

5. **DEBT-005** — Frontend Code Hygiene & Quarantine Resolution
   - Debts: FE-015, FE-009, FE-011, FE-017, FE-013, FE-026
   - Agent: @dev + @qa

6. **DEBT-006** — Design System Foundation (Shared Button)
   - Debts: FE-032
   - Agent: @ux-design-expert + @dev

7. **DEBT-007** — CI Quality Gates & Test Infrastructure
   - Debts: CROSS-002, CROSS-007, CROSS-005, SYS-031, SYS-034, SYS-035
   - Agent: @devops + @qa

8. **DEBT-008** — Backend Stability & Security Quick Fixes
   - Debts: SYS-016, SYS-017, SYS-024, SYS-027, CROSS-004, SYS-013, SYS-015
   - Agent: @dev

### Sprint 2 — Semana 3-4

9. **DEBT-009** — Database RLS & Retention Hardening
   - Debts: DB-001, DB-048, DB-033, DB-037, DB-049, DB-007, DB-002, DB-010
   - Agent: @data-engineer

10. **DEBT-010** — Database Schema Guards & Monitoring
    - Debts: DB-011, DB-015, DB-028, DB-018, DB-019, DB-040, DB-041, DB-042, DB-021, DB-045, DB-031
    - Agent: @data-engineer

11. **DEBT-011** — Frontend Component Architecture
    - Debts: FE-001 (partial: conta), FE-006, FE-008, FE-030
    - Agent: @dev + @ux-design-expert

12. **DEBT-012** — Frontend Forms, Tokens & Accessibility
    - Debts: FE-033, FE-036, FE-028, FE-023
    - Agent: @ux-design-expert + @dev

13. **DEBT-013** — Frontend Performance Optimization
    - Debts: FE-019, FE-014, FE-031, FE-018, FE-016
    - Agent: @dev

14. **DEBT-014** — Backend Service Layer & Lifecycle
    - Debts: SYS-001, SYS-006, SYS-010, SYS-018, SYS-022
    - Agent: @architect + @dev

### Backlog — Mes 2-3

15. **DEBT-015** — Backend Architecture Decomposition
    - Debts: SYS-002, SYS-003, SYS-004, SYS-005, SYS-012, SYS-011
    - Agent: @architect + @dev

16. **DEBT-016** — Frontend Advanced Refactoring
    - Debts: FE-001 (restante), FE-004, FE-005, FE-007, FE-035, FE-010, FE-003, FE-024, FE-025, FE-027, FE-020
    - Agent: @dev + @ux-design-expert

17. **DEBT-017** — Database Long-Term Optimization
    - Debts: DB-004, DB-005, DB-006, DB-008, DB-009, DB-014, DB-016, DB-017, DB-020, DB-022, DB-023, DB-024, DB-027, DB-029, DB-034, DB-035, DB-036, DB-044, DB-046, DB-050
    - Agent: @data-engineer

18. **DEBT-018** — Infrastructure, Security & Observability
    - Debts: SYS-007, SYS-008, SYS-014, SYS-019, SYS-020, SYS-021, SYS-023, SYS-025, SYS-026, SYS-028, SYS-029, SYS-030, SYS-032, SYS-033, SYS-036, SYS-037, SYS-038, CROSS-003, CROSS-006
    - Agent: @devops + @dev

## Dependency Map

```
Sprint 1 (parallelizable):
  DEBT-001 (DB integrity)     -- independent
  DEBT-002 (migrations/DR)    -- independent (but DEBT-001 quick fixes first)
  DEBT-003 (loading/errors)   -- independent
  DEBT-004 (accessibility)    -- independent
  DEBT-005 (code hygiene)     -- independent (FE-026 quarantine prerequisite for Sprint 2)
  DEBT-006 (Button component) -- independent (prerequisite for DEBT-012)
  DEBT-007 (CI gates)         -- independent (prerequisite for DEBT-011/016)
  DEBT-008 (backend fixes)    -- independent

Sprint 2 (sequenced):
  DEBT-005.FE-026 (quarantine) --> DEBT-011.FE-001 (page decomposition)
  DEBT-006.FE-032 (Button)     --> DEBT-012.FE-033 (Input/Label)
  DEBT-007.CROSS-002 (API CI)  --> DEBT-016.FE-007 (data fetching refactor)
  DEBT-011.FE-006 (state)      --> DEBT-011.FE-001 (page decomposition)
  DEBT-011.FE-006 (state)      --> DEBT-016.FE-007 (data fetching)

Backlog:
  DEBT-014.SYS-001 (deprecation metric, 2 weeks data) --> DEBT-015.SYS-005 (main.py decomp)
  DEBT-011.FE-006 (state) --> DEBT-016.FE-001 (remaining pages)
  DEBT-015.SYS-003 (Redis Streams) --> horizontal scaling
```

## Riscos

| # | Risco | Severidade | Mitigacao |
|---|-------|------------|-----------|
| R-01 | Migration consolidation breaks production DB | CRITICAL | Verificar cada objeto via pg_tables/pg_proc/pg_indexes. Nunca mover arquivos — criar bridge migration. |
| R-02 | Service role compound exposure (SYS-023) | HIGH | Per-user tokens para ops user-scoped; service role restrito a admin ops. Backlog item. |
| R-03 | FE-001 + FE-006 decomposition cascade | HIGH | Sequencia obrigatoria: FE-026 -> FE-006 -> FE-001 (uma pagina por vez, comecando por conta). |
| R-04 | Legacy route removal breaks unknown consumers | MEDIUM | Deprecation counter metric. 2+ semanas de dados. Remover apenas rotas com zero hits. |
| R-05 | In-memory progress tracker blocks horizontal scaling | HIGH | Resolver SYS-003 (Redis Streams) antes de scaling. |
| R-06 | API contract drift during FE refactoring | MEDIUM | Implementar CROSS-002 (Sprint 1) ANTES de FE-007 (Backlog). |
| R-07 | CSP tightening breaks Stripe checkout | MEDIUM | Testar nonce-based CSP em staging. Stripe tem guidance especifica. |

## Definition of Done

- [ ] All CRITICAL and HIGH debts resolved (25/25)
- [ ] Test coverage: Backend >= 5900 pass, Frontend >= 2800 pass
- [ ] Zero quarantined tests
- [ ] Zero WCAG AA violations in authenticated pages
- [ ] All tables with retention policies (0 unbounded growth)
- [ ] DR procedure documented and tested
- [ ] API contract validation enforced in CI
- [ ] Dependency vulnerability scanning in CI (0 high+)
- [ ] Design system primitives: Button, Input, Label, Badge (minimum)
- [ ] Performance: P95 search <5s, page load <3s

---

*Epic criado por @pm (Parker) em 2026-03-07*
*Baseado no Technical Debt Assessment FINAL v1.0 (validado por @architect, @data-engineer, @ux-design-expert, @qa)*
*Executive report: TECHNICAL-DEBT-REPORT v5.0*
