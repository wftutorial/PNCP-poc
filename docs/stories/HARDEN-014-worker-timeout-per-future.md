# HARDEN-014: ThreadPoolExecutor Timeout por Future (LLM Batches)

**Severidade:** ALTA
**Esforço:** 30 min
**Quick Win:** Nao
**Origem:** Conselho CTO — Auditoria de Fragilidades (2026-03-06)

## Contexto

`ThreadPoolExecutor(max_workers=3)` em `filter.py:3194` submete batches para classificação LLM. `as_completed()` não tem timeout por future individual. Se OpenAI trava em 1 batch, bloqueia o executor. O budget check (CRIT-057) existe mas age sobre elapsed total, não per-future.

## Critérios de Aceitação

- [ ] AC1: `wait(timeout=20)` com `FIRST_COMPLETED` ao invés de `as_completed()`
- [ ] AC2: Futures que excedem timeout são cancelled
- [ ] AC3: Items não classificados marcados como `pending_review`
- [ ] AC4: Metric `smartlic_llm_batch_timeout_total`
- [ ] AC5: Teste unitário com future que trava
- [ ] AC6: Zero regressions

## Arquivos Afetados

- `backend/filter.py` — filter_licitacoes_parallel() ou seção zero-match
- `backend/tests/test_filter.py`
