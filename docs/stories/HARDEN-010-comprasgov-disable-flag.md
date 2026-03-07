# HARDEN-010: ComprasGov v3 Feature Flag Disable

**Severidade:** ALTA
**Esforço:** 5 min
**Quick Win:** Sim
**Origem:** Conselho CTO — Auditoria de Fragilidades (2026-03-06)

## Contexto

ComprasGov v3 está completamente fora do ar (confirmado 2026-03-03). API retorna 404 na homepage. Circuit breaker trata como transient e tenta recovery a cada 60s — desperdício de recursos.

## Critérios de Aceitação

- [ ] AC1: Feature flag `COMPRASGOV_ENABLED` em config.py (default=false)
- [ ] AC2: Consolidation skip source quando disabled
- [ ] AC3: Log warning na startup se disabled
- [ ] AC4: Fácil reativar via env var quando API voltar
- [ ] AC5: Teste unitário valida skip

## Arquivos Afetados

- `backend/config.py` — COMPRASGOV_ENABLED
- `backend/consolidation.py` — skip logic
