# HARDEN-003: asyncio.Queue Bounded com maxsize no ProgressTracker

**Severidade:** CRITICA
**Esforço:** 10 min
**Quick Win:** Sim
**Origem:** Conselho CTO — Auditoria de Fragilidades (2026-03-06)

## Contexto

`ProgressTracker.queue` em `progress.py:89` é criado com `asyncio.Queue()` sem `maxsize`. Se SSE client desconecta mas generator continua emitindo, a queue cresce infinitamente → OOM.

## Problema

- Queue sem limite = crescimento infinito de memória
- 1000 searches/dia × 100 events/search × 1KB/event = 100MB/dia sem cleanup
- Client disconnect não interrompe emissão de eventos

## Critérios de Aceitação

- [ ] AC1: `asyncio.Queue(maxsize=500)` no ProgressTracker
- [ ] AC2: Drop-oldest quando queue cheia (backpressure)
- [ ] AC3: Metric `smartlic_sse_queue_drops_total` para monitorar drops
- [ ] AC4: Teste unitário valida comportamento com queue cheia
- [ ] AC5: Zero regressions nos testes existentes

## Solução

```python
# progress.py:89
self.queue: asyncio.Queue[ProgressEvent] = asyncio.Queue(maxsize=500)

# Na _emit_event:
if self.queue.full():
    try:
        self.queue.get_nowait()  # drop oldest
    except asyncio.QueueEmpty:
        pass
    # Optional: increment drop metric
await self.queue.put(event)
```

## Arquivos Afetados

- `backend/progress.py` — ProgressTracker.__init__, _emit_event
- `backend/metrics.py` — nova metric (opcional)
- `backend/tests/test_progress.py` — novo teste
