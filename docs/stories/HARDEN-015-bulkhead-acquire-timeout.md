# HARDEN-015: Bulkhead Semaphore Acquire Timeout

**Severidade:** ALTA
**Esforço:** 45 min
**Quick Win:** Nao
**Origem:** Conselho CTO — Auditoria de Fragilidades (2026-03-06)

## Contexto

Bulkhead wraps source fetch com semaphore em `consolidation.py:654-656`. Com 27 UFs competindo pelo mesmo bulkhead com limite de 5, 22 UFs esperam. UFs no final da fila esgotam timeout antes de executar.

## Critérios de Aceitação

- [ ] AC1: Bulkhead.execute() divide timeout: 50% para acquire, 50% para execução
- [ ] AC2: BulkheadTimeoutError exception para acquire timeout
- [ ] AC3: UF marcada como `skipped` (não `error`) quando acquire timeout
- [ ] AC4: Metric `smartlic_bulkhead_acquire_timeout_total`
- [ ] AC5: Teste com cenário de 27 UFs e bulkhead size=5

## Arquivos Afetados

- `backend/bulkhead.py` — SourceBulkhead.execute()
- `backend/consolidation.py` — error handling
- `backend/tests/test_bulkhead.py`
