# DEBT-07: Backend Module Split (4400 LOC -> submodulos)

**Epic:** EPIC-TD-2026
**Fase:** 3-4 (Hardening/Polish)
**Horas:** 28h
**Agente:** @dev
**Prioridade:** P2

## Debitos Cobertos

| TD | Item | Horas |
|----|------|-------|
| TD-007 | quota.py 1660 LOC -> quota_core, quota_atomic, plan_enforcement | 12h |
| TD-008 | consolidation.py 1394 LOC -> source_merger, dedup, priority_resolver | 8h |
| TD-009 | llm_arbiter.py 1362 LOC -> classification, zero_match, prompt_builder | 8h |

## Acceptance Criteria

- [ ] AC1: Cada modulo splitado em 3 submodulos com `__init__.py` re-export (facade pattern)
- [ ] AC2: Zero imports quebrados — `from quota import X` continua funcionando
- [ ] AC3: Nenhum modulo > 600 LOC
- [ ] AC4: Testes existentes passando sem modificacao
- [ ] AC5: Coverage mantida >= 70%

## Notas

Ordem sugerida: TD-007 (quota, mais complexo) -> TD-008 (consolidation) -> TD-009 (llm_arbiter).
Podem ser feitos em paralelo se 2+ devs disponiveis.
