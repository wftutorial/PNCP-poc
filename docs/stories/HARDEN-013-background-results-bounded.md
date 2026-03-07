# HARDEN-013: Background Results Dict Bounded (max 200)

**Severidade:** ALTA
**Esforço:** 15 min
**Quick Win:** Nao
**Origem:** Conselho CTO — Auditoria de Fragilidades (2026-03-06)

## Contexto

`_background_results` dict em `routes/search.py:158` cresce sem limite. Cleanup só roda durante handler de busca. Em baixo tráfego, dict acumula indefinidamente.

## Critérios de Aceitação

- [ ] AC1: `_MAX_BACKGROUND_RESULTS = 200` aplicado no `store_background_results()`
- [ ] AC2: Eviction do mais antigo quando excede max
- [ ] AC3: Integrado com cleanup periódico (HARDEN-004)
- [ ] AC4: Teste unitário valida eviction

## Arquivos Afetados

- `backend/routes/search.py` — store_background_results()
