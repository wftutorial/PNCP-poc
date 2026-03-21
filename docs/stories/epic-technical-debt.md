# Epic: Resolucao de Debitos Tecnicos -- SmartLic v2.0

**Epic ID:** DEBT-EPIC-001
**Data:** 2026-03-21
**Owner:** @architect (Atlas)
**Status:** PLANNED
**Source:** `docs/prd/technical-debt-assessment.md` (FINAL v2.0, 76 items)

---

## Objetivo

Eliminar todos os debitos tecnicos CRITICAL e HIGH do SmartLic antes do scale-up de clientes (meta: 10K usuarios). O debito acumulado durante o POC (v0.1-v0.5) impede a velocidade de entrega de features, aumenta o risco de bugs em billing/auth, e viola WCAG 2.1 AA na pagina principal (/buscar). Esta epic resolve 69 itens acionaveis em 5 waves progressivas, partindo de uma safety net de testes ate polish final.

**Conexao com objetivos de negocio:**
- **Confiabilidade:** Account deletion atomica, subscription status unificado, RLS policies completas
- **Acessibilidade:** WCAG 2.1 AA compliance nas paginas core (buscar, login, onboarding, planos)
- **Velocidade de desenvolvimento:** Backend monolitos decompostos (filter.py 3,871 LOC -> <500 LOC), schemas.py split por dominio
- **Escalabilidade:** Migration squash, composite indexes, dead source removal

## Escopo

- **Total:** 76 debt items across 5 categories (SYS, DB, FE, QA, CI)
- **Actionable:** 69 items (excluding 2 design choices + 1 informational + 4 deferred/scale-dependent)
- **Estimated effort:** ~259h
- **Timeline:** 13 weeks (5 waves)
- **Severities:** 4 CRITICAL, 14 HIGH, 25 MEDIUM, 27 LOW, 1 INFO, 2 N/A

## Criterios de Sucesso

- [ ] All CRITICAL items resolved (4/4: SYS-001, SYS-002, SYS-003, FE-002)
- [ ] All HIGH items resolved (14/14: SYS-004/005/006/007/009, DB-001/002/018, FE-001/007/008/017/022, QA-001/002)
- [ ] Backend test coverage >= 70% (existing CI gate)
- [ ] Frontend test coverage >= 60% (existing CI gate)
- [ ] Backend test count >= 7,500 (baseline 7,332 + Wave 0 safety net)
- [ ] No untested production-critical modules (cron_jobs, supabase_client, filter_*, webhooks)
- [ ] WCAG 2.1 AA: 0 critical axe-core violations on /buscar, /login, /onboarding
- [ ] Skip-link functional on all protected pages
- [ ] filter.py reduced to < 500 LOC (orchestration/re-export only)
- [ ] schemas.py split into domain-specific files with backward-compat re-exports
- [ ] No restructured backend file exceeds 1,000 LOC
- [ ] Account deletion is fully transactional (integration test proves atomicity)
- [ ] ComprasGov v3 disabled, pipeline source count = 2 (PNCP + PCP)
- [ ] Migration squash replays cleanly on fresh PostgreSQL 17

## Waves

| Wave | Nome | Story | Items | Esforco | Timeline | Parallelizable |
|------|------|-------|-------|---------|----------|----------------|
| 0 | Safety Net | DEBT-W0 | 6 | ~24h | Week 1 | Yes, with Wave 1 |
| 1 | Quick Wins + Critical | DEBT-W1 | 15 | ~26.25h | Weeks 2-3 | Yes, with Wave 0 |
| 2 | High Priority | DEBT-W2 | 12 | ~35.5h | Weeks 4-5 | FE/DB in parallel |
| 3 | Structural Refactoring | DEBT-W3 | 11 | ~76h | Weeks 6-9 | FE/BE parallel, BE sequential |
| 4 | Polish + Optimization | DEBT-W4 | ~25 | ~97h | Weeks 10-13 (interleaved) | All items independent |
| **Total** | | | **69** | **~258.75h** | **~13 weeks** | |

## Stories Index

| Story ID | Title | Wave | Effort | File |
|----------|-------|------|--------|------|
| DEBT-W0 | Safety Net -- Testes para Modulos Descobertos | 0 | ~24h | [story-DEBT-W0-safety-net.md](story-DEBT-W0-safety-net.md) |
| DEBT-W1 | Quick Wins + Critical Fixes | 1 | ~26.25h | [story-DEBT-W1-quick-wins-critical.md](story-DEBT-W1-quick-wins-critical.md) |
| DEBT-W2 | High Priority -- DB Hygiene + Accessibility | 2 | ~35.5h | [story-DEBT-W2-high-priority.md](story-DEBT-W2-high-priority.md) |
| DEBT-W3 | Structural Refactoring | 3 | ~76h | [story-DEBT-W3-structural-refactoring.md](story-DEBT-W3-structural-refactoring.md) |
| DEBT-W4 | Polish + Optimization | 4 | ~97h | [story-DEBT-W4-polish-optimization.md](story-DEBT-W4-polish-optimization.md) |

## Dependency Graph

```
Wave 0 (Safety Net) ──────────────────────────────> Wave 3 (Structural)
    |                                                     |
    | (runs in parallel)                                  |
    v                                                     v
Wave 1 (Quick Wins) ───> Wave 2 (High Priority) ───> Wave 4 (Polish)

Critical paths within Waves:
  Wave 1: DB-002 (FK fix) ──────────────────────────> feeds Wave 2
  Wave 2: DB-001 (from W1) ──> DB-009 (price IDs) ──> DB-008 (squash, LAST)
  Wave 3: SYS-020 ──> SYS-004 ──> SYS-001/002/005/006/009/010

Key blockers:
  Wave 0 incomplete ──> ALL of Wave 3 BLOCKED
  QA-DEBT-005 (filter tests) ──> SYS-001 (filter decomposition)
  QA-DEBT-001 (cron tests) ──> SYS-005 (job split)
  QA-DEBT-006 (webhook tests) ──> SYS-007 (webhook split)
  DB-022 (quota fix) ──> SYS-009 (quota split)
  CI-001 (CI clarity) ──> Wave 3 confidence
```

## Riscos (Top 5)

| # | Risco | Probabilidade | Impacto | Mitigacao |
|---|-------|---------------|---------|-----------|
| 1 | **Backend restructuring breaks 344 test files** (Wave 3) | HIGH during W3 | HIGH | Wave 0 safety net. Per-step test count validation. Separate PRs. Backward-compat re-exports. Import path CI guard. |
| 2 | **Billing status drift causes access bugs** (DB-001 + SYS-007 + QA-006) | MEDIUM | CRITICAL | Unify enums in Wave 1. Complete webhook test matrix in Wave 0. Integration test for sync trigger. |
| 3 | **Account deletion leaves partial state** (DB-018) | LOW | HIGH | Transaction wrap in Wave 1 PR 1. Integration test with simulated auth.users delete failure. |
| 4 | **Filter decomposition without submodule tests** (SYS-001 + QA-005) | HIGH if W0 skipped | MEDIUM | Hard gate: no SYS-001 PR without QA-005 complete. |
| 5 | **Feature work blocked by debt resolution** (Wave 3 = 4 weeks dedicated) | MEDIUM | MEDIUM | Waves 0+1 parallel. Wave 4 interleaves with features. Only Wave 3 requires feature freeze. |

## Definition of Done (Epic Level)

- [ ] All 5 stories completed and accepted
- [ ] All backend tests passing: `python scripts/run_tests_safe.py --parallel 4` (0 failures)
- [ ] All frontend tests passing: `npm test` (0 failures, excluding 3 pre-existing)
- [ ] E2E tests passing: `npm run test:e2e`
- [ ] No regression in existing functionality (manual smoke test on smartlic.tech)
- [ ] Documentation updated (CLAUDE.md architecture section, CHANGELOG.md)
- [ ] No CRITICAL or HIGH debt items remaining in assessment
- [ ] CI run time < 15 minutes
- [ ] Bundle size stable or improved vs pre-epic baseline

---

*Gerado 2026-03-21 por @pm durante Brownfield Discovery Phase 10.*
*Baseado no Technical Debt Assessment FINAL v2.0 (76 items, ~259h, 5 waves, 13 weeks).*
*Supersedes previous epic (81 items / 4 sprints / ~280h) based on specialist-reviewed assessment.*
