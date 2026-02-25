# STORY-263: Trial Stats Bug Fix — pipeline_items

## Metadata
- **Epic:** Enterprise Readiness (EPIC-ENT-001)
- **Priority:** P0 (Blocking)
- **Effort:** 0.5 hours
- **Area:** Backend
- **Depends on:** None
- **Risk:** Low (1-line code fix + test update)
- **Assessment IDs:** T1-04, MISSED-03

## Context

`backend/services/trial_stats.py` linha 78 referencia a tabela `user_pipeline` que nao existe — o nome correto e `pipeline_items`. O teste correspondente (`test_trial_usage_stats.py`) mocka `user_pipeline`, mascarando o bug. Todo trial user que acessa o pipeline trial value ve um erro.

## Acceptance Criteria

- [ ] AC1: `trial_stats.py` referencia `pipeline_items` (nao `user_pipeline`)
- [ ] AC2: `test_trial_usage_stats.py` mocka `pipeline_items` (nao `user_pipeline`)
- [ ] AC3: `pytest tests/test_trial_usage_stats.py -v` passa com o nome correto
- [ ] AC4: Nenhum arquivo no codebase referencia `user_pipeline`
- [ ] AC5: Full backend test suite passa

## Tasks

- [ ] Task 1: Em `backend/services/trial_stats.py` linha 78: mudar `sb.table("user_pipeline")` para `sb.table("pipeline_items")`
- [ ] Task 2: Em `backend/tests/test_trial_usage_stats.py` linhas 70, 79, 151, 188: mudar mock de `user_pipeline` para `pipeline_items`
- [ ] Task 3: Grep por `user_pipeline` no codebase inteiro — garantir zero resultados
- [ ] Task 4: Rodar `pytest tests/test_trial_usage_stats.py -v`
- [ ] Task 5: Rodar full `pytest`

## Test Plan

1. `pytest tests/test_trial_usage_stats.py -v` — todos os testes passam com nome correto
2. `grep -r "user_pipeline" backend/` — zero resultados
3. Full `pytest` — 0 regressions

## Regression Risks

- **Baixo:** Fix isolado ao modulo trial stats. Nenhum outro modulo referencia `user_pipeline`.
- **Cuidado:** Se teste ainda mocka `user_pipeline` apos o fix, testes passam falsamente. Atualizar teste SIMULTANEAMENTE.

## Files Changed

- `backend/services/trial_stats.py` (EDIT — line 78)
- `backend/tests/test_trial_usage_stats.py` (EDIT — lines 70, 79, 151, 188)

## Definition of Done

- [ ] Code fix aplicado
- [ ] Testes atualizados
- [ ] Zero referencias a `user_pipeline` no codebase
- [ ] Full pytest suite passing
