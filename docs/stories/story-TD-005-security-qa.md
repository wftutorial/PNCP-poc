# STORY-TD-005: Security & Backend Hardening — Vulnerability Scanning e Module Decomposition

**Story ID:** STORY-TD-005
**Epic:** EPIC-TD-2026
**Phase:** 3 (Hardening)
**Priority:** P2
**Estimated Hours:** 24h
**Agents:** @dev (backend refactoring), @devops (CI pipeline), @qa (verification)

## Objetivo

Adicionar varredura automatica de vulnerabilidades em dependencias no CI e decompor os dois maiores modulos backend (`quota.py` com 1.660 LOC e `consolidation.py` com 1.394 LOC) em submodulos menores e testaveis. Estes dois arquivos sao os maiores do backend e dificultam code review, onboarding e isolamento de bugs.

## Acceptance Criteria

### Dependency Vulnerability Scanning (TD-058)
- [ ] AC1: `pip-audit` executa no CI para cada PR que modifica `requirements.txt`. Zero vulnerabilidades high/critical no ultimo run. Verificavel via GitHub Actions check status.
- [ ] AC2: `npm audit --audit-level=high` executa no CI para cada PR que modifica `package.json` ou `package-lock.json`. Zero vulnerabilidades high/critical. Verificavel via GitHub Actions check status.
- [ ] AC3: Workflow nao bloqueia PRs com vulnerabilidades low/medium (warning only), mas bloqueia high/critical.

### quota.py Decomposition (TD-007)
- [ ] AC4: `quota.py` (1.660 LOC) decomposto em 3 modulos: `quota/core.py` (quota checking + types), `quota/atomic.py` (atomic increment/decrement operations), `quota/plan_enforcement.py` (plan limits + grace period logic). Nenhum modulo > 600 LOC.
- [ ] AC5: `quota/__init__.py` re-exporta todos os simbolos publicos — NENHUM import externo quebrado (`from quota import check_and_increment_quota_atomic` continua funcionando).
- [ ] AC6: Todos os 5131+ backend tests passando sem modificacao de imports.
- [ ] AC7: Coverage de `quota/` >= coverage anterior de `quota.py` (nao reduzir cobertura).

### consolidation.py Decomposition (TD-008)
- [ ] AC8: `consolidation.py` (1.394 LOC) decomposto em 3 modulos: `consolidation/source_merger.py` (multi-source result merging), `consolidation/dedup.py` (deduplication logic), `consolidation/priority_resolver.py` (source priority + conflict resolution). Nenhum modulo > 500 LOC.
- [ ] AC9: `consolidation/__init__.py` re-exporta todos os simbolos publicos — NENHUM import externo quebrado.
- [ ] AC10: Todos os backend tests passando sem modificacao de imports.
- [ ] AC11: Coverage de `consolidation/` >= coverage anterior.

### Quality Gates
- [ ] AC12: Backend tests passing (5131+ tests, 0 failures).
- [ ] AC13: `ruff check .` sem novos warnings nos modulos refatorados.
- [ ] AC14: OpenAPI schema snapshot inalterado (decomposicao e interna, nao afeta API).

## Tasks

### Dependency Scanning (TD-058) — 4h
- [ ] Task 1: Criar workflow `.github/workflows/dependency-audit.yml`:
  ```yaml
  on:
    pull_request:
      paths:
        - 'backend/requirements.txt'
        - 'frontend/package.json'
        - 'frontend/package-lock.json'
  ```
- [ ] Task 2: Adicionar step Python: `pip install pip-audit && pip-audit -r backend/requirements.txt --desc --severity high,critical`.
- [ ] Task 3: Adicionar step Node: `cd frontend && npm audit --audit-level=high`.
- [ ] Task 4: Configurar para falhar apenas em high/critical (`--fail-on-vuln` para pip-audit, `--audit-level=high` para npm audit).
- [ ] Task 5: Executar manualmente uma vez para verificar baseline. Resolver qualquer high/critical existente.
- [ ] Task 6: Documentar no PR como adicionar excecoes temporarias para false positives.

### quota.py Decomposition (TD-007) — 12h
- [ ] Task 7: Mapear responsabilidades de `quota.py`: quota checking/types, atomic operations (Supabase RPCs), plan enforcement (limits, grace period, trial logic).
- [ ] Task 8: Criar diretorio `backend/quota/` com `__init__.py`.
- [ ] Task 9: Extrair `quota/core.py` — tipos, constantes, funcoes de verificacao de quota (is_within_quota, get_remaining_quota, QuotaResult, etc.).
- [ ] Task 10: Extrair `quota/atomic.py` — operacoes atomicas (`check_and_increment_quota_atomic`, `decrement_quota`, Supabase RPC calls).
- [ ] Task 11: Extrair `quota/plan_enforcement.py` — logica de limites por plano, grace period, trial enforcement, plan-specific rules.
- [ ] Task 12: Criar `quota/__init__.py` com re-exports: `from quota.core import *; from quota.atomic import *; from quota.plan_enforcement import *`.
- [ ] Task 13: Rodar `pytest -k quota` — todos os testes de quota devem passar SEM mudanca de imports.
- [ ] Task 14: Rodar full suite `pytest --timeout=30 -q` para confirmar zero regressions.
- [ ] Task 15: Verificar coverage: `pytest --cov=quota -k quota`.

### consolidation.py Decomposition (TD-008) — 8h
- [ ] Task 16: Mapear responsabilidades de `consolidation.py`: source merging, deduplication, priority resolution.
- [ ] Task 17: Criar diretorio `backend/consolidation/` com `__init__.py`.
- [ ] Task 18: Extrair `consolidation/source_merger.py` — logica de merge de resultados de multiplas fontes (PNCP, PCP, ComprasGov).
- [ ] Task 19: Extrair `consolidation/dedup.py` — deduplicacao por content_hash, titulo, CNPJ.
- [ ] Task 20: Extrair `consolidation/priority_resolver.py` — priority scoring (PNCP=1 > PCP=2 > ComprasGov=3), conflict resolution quando mesmo edital aparece em fontes diferentes.
- [ ] Task 21: Criar `consolidation/__init__.py` com re-exports.
- [ ] Task 22: Rodar testes relevantes e full suite.
- [ ] Task 23: Verificar coverage.

## Definition of Done

- [ ] Todos os ACs met e verificaveis
- [ ] Backend tests passing (5131+ tests, 0 failures)
- [ ] CI workflow de dependency scanning ativo e verde
- [ ] Nenhum modulo > 600 LOC
- [ ] Nenhum import externo quebrado (facade pattern)
- [ ] Coverage nao reduzida
- [ ] PR reviewed por @architect
- [ ] `ruff check .` limpo

## Debt Items Covered

| ID | Item | Hours | Notas |
|----|------|-------|-------|
| TD-058 | Dependency vulnerability scanning in CI | 4 | pip-audit + npm audit |
| TD-007 | quota.py oversized (1,660 LOC) -> 3 modules | 12 | Refactor into quota/ package |
| TD-008 | consolidation.py oversized (1,394 LOC) -> 3 modules | 8 | Refactor into consolidation/ package |
| | **Total** | **24h** | |

## Notas Tecnicas

- **Facade pattern (CRITICAL):** O `__init__.py` de cada package DEVE re-exportar todos os simbolos publicos. Testes existentes fazem `from quota import check_and_increment_quota_atomic` — isso DEVE continuar funcionando. Rodar full suite apos cada decomposicao.
- **TD-007 e o maior risco:** `quota.py` com 1.660 LOC tem alta complexidade ciclomatica e e importado por muitos modulos (routes, billing, search). A decomposicao deve ser feita incrementalmente: extrair 1 modulo por vez, rodar testes, repetir.
- **TD-008 padrao similar:** `consolidation.py` segue o mesmo padrao. A dedup logic e a parte mais delicada — manter testes de dedup rodando a cada passo.
- **TD-058 baseline:** E possivel que existam vulnerabilidades medium/low ja. O workflow deve ser configurado para nao bloquear essas, apenas high/critical. Documentar excecoes no PR.
- **Mocking em testes:** Conforme CLAUDE.md, testes que mockam quota devem mockar `check_and_increment_quota_atomic`. O facade garante que o mock path nao muda.

---

*Story criada em 2026-04-08 por @pm (Morgan). Fase 3 do EPIC-TD-2026.*
