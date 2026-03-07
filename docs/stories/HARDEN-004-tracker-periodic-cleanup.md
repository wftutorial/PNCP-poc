# HARDEN-004: Cleanup Periódico de _active_trackers

**Severidade:** CRITICA
**Esforço:** 30 min
**Quick Win:** Nao
**Origem:** Conselho CTO — Auditoria de Fragilidades (2026-03-06)

## Contexto

`_active_trackers` dict em `progress.py` cresce com cada search. `remove_tracker()` só é chamado se SSE generator termina normalmente. Client disconnect abrupto (crash, network) = tracker fica para sempre. `_cleanup_stale()` só roda quando chamado por funções públicas — não há cron periódico.

## Problema

- Memory leak de ~1KB/tracker × 1000 searches/dia = 1MB/dia crescendo
- Cleanup dependente de chamadas públicas (pode nunca rodar em baixo tráfego)
- `_background_results` dict tem o mesmo problema

## Critérios de Aceitação

- [ ] AC1: Background task `_periodic_tracker_cleanup()` roda a cada 120s
- [ ] AC2: Task criada no lifespan handler do FastAPI
- [ ] AC3: Task cancelada no shutdown
- [ ] AC4: Cleanup inclui `_background_results` e `_active_background_tasks`
- [ ] AC5: Metric `smartlic_tracker_cleanup_count` registra quantos trackers removidos
- [ ] AC6: Teste unitário valida cleanup periódico

## Solução

```python
# progress.py
_TRACKER_CLEANUP_INTERVAL = 120

async def _periodic_tracker_cleanup():
    while True:
        await asyncio.sleep(_TRACKER_CLEANUP_INTERVAL)
        try:
            _cleanup_stale()
        except Exception as e:
            logger.warning(f"Tracker cleanup error: {e}")

# main.py lifespan:
@asynccontextmanager
async def lifespan(app: FastAPI):
    cleanup_task = asyncio.create_task(_periodic_tracker_cleanup())
    yield
    cleanup_task.cancel()
```

## Arquivos Afetados

- `backend/progress.py` — _periodic_tracker_cleanup()
- `backend/main.py` — lifespan handler
- `backend/routes/search.py` — _cleanup_stale_results() integration
