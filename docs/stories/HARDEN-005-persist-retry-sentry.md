# HARDEN-005: Retry + Sentry Alert para Persist Results

**Severidade:** CRITICA
**Esforço:** 30 min
**Quick Win:** Nao
**Origem:** Conselho CTO — Auditoria de Fragilidades (2026-03-06)

## Contexto

`_persist_results_to_supabase()` em `routes/search.py:224-274` é fire-and-forget via `asyncio.create_task()` sem exception handler. Se Supabase falha, resultados são perdidos silenciosamente. Usuário recebeu 202 mas dados nunca persistiram.

## Problema

- Perda silenciosa de dados de busca
- Sem retry, sem dead letter, sem alerta
- Usuário vê resultados, recarrega página, dados desapareceram

## Critérios de Aceitação

- [x] AC1: Wrapper `_safe_persist_results()` com retry 3× (backoff exponencial)
- [x] AC2: `sentry_sdk.capture_exception()` na falha final
- [x] AC3: Metric `smartlic_persist_failures_total` com label `store`
- [x] AC4: `task.add_done_callback()` para capturar exceções não tratadas
- [x] AC5: Teste unitário valida retry e métrica de falha
- [x] AC6: Zero regressions

## Solução

```python
async def _safe_persist_results(search_id, user_id, response):
    for attempt in range(3):
        try:
            await _persist_results_to_supabase(search_id, user_id, response)
            return
        except Exception as e:
            if attempt == 2:
                sentry_sdk.capture_exception(e)
                PERSIST_FAILURES.labels(store="supabase").inc()
            else:
                await asyncio.sleep(2 ** attempt)
```

## Arquivos Afetados

- `backend/routes/search.py` — _safe_persist_results()
- `backend/metrics.py` — PERSIST_FAILURES counter
