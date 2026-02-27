# STORY-294: Externalize State to Redis

**Sprint:** 1 — Make It Reliable
**Size:** L (8-16h)
**Root Cause:** RC-3
**Depends on:** STORY-292
**Industry Standard:** [State Externalization Pattern](https://12factor.net/processes), [Microsoft — External Configuration Store](https://learn.microsoft.com/en-us/azure/architecture/patterns/external-configuration-store)

## Contexto

O backend roda com `WEB_CONCURRENCY=2` (2 workers Gunicorn). Três estruturas in-memory são compartilhadas APENAS dentro de um worker:

1. `_active_trackers: dict[str, ProgressTracker]` em `progress.py` — SSE streams
2. `_background_results: dict[str, BuscaResponse]` em `routes/search.py` — resultados async
3. `_arbiter_cache: dict[str, LLMClassification]` em `llm_arbiter.py` — cache LLM

Se o POST /buscar roda no worker 1 e o GET /buscar-progress/{id} cai no worker 2, o tracker não existe. Resultado: SSE fica em espera infinita ou retorna 404.

## Acceptance Criteria

- [x] AC1: `_active_trackers` substituído por Redis Streams (STORY-276) — tracker publica eventos via XADD, SSE consome via XREAD; metadata stored in Redis hash for cross-worker discovery; STATE_STORE_ERRORS metric on failures
- [x] AC2: `_background_results` substituído por Redis string com TTL 30min (`smartlic:results:{id}`); L1=in-memory, L2=Redis; `_persist_results_to_redis()` async fire-and-forget
- [x] AC3: `_arbiter_cache` substituído por Redis string com TTL 1h (`smartlic:arbiter:{hash}`); L1=in-memory, L2=Redis via sync client (`get_sync_redis()` for ThreadPoolExecutor compat)
- [x] AC4: SSE endpoint funciona independente de worker — Redis Streams (STORY-276) + tracker metadata in Redis enables cross-worker SSE
- [x] AC5: `get_background_results_async()` agora tem 3 níveis: L1 in-memory → L2 Redis → L3 ARQ Worker; resultado disponível via endpoint independente de worker
- [x] AC6: Graceful fallback: se Redis indisponível, in-memory como fallback (não crash); all Redis ops wrapped in try/except with metric increment
- [x] AC7: Prometheus metric: `smartlic_state_store_errors_total` (labels: store=[tracker,results,arbiter], operation=[read,write,delete])
- [x] AC8: TTL cleanup: Redis EXPIRE em todas as chaves — results=1800s, arbiter=3600s, tracker_metadata=420s, stream=300s
- [x] AC9: Testes existentes continuam passando — 27 new tests + full suite regression verified
- [x] AC10: Load test: 10 buscas simultâneas simuladas — 100% armazenadas e recuperadas via Redis (TestConcurrentSearches)

## Technical Design

```python
# Redis pub/sub for progress events
class RedisProgressTracker:
    def __init__(self, search_id: str, redis: Redis):
        self._channel = f"progress:{search_id}"
        self._redis = redis

    async def emit(self, event: dict):
        await self._redis.publish(self._channel, json.dumps(event))

    async def subscribe(self) -> AsyncIterator[dict]:
        pubsub = self._redis.pubsub()
        await pubsub.subscribe(self._channel)
        async for message in pubsub.listen():
            if message["type"] == "message":
                yield json.loads(message["data"])
```

## Files Changed

- `backend/progress.py` — STATE_STORE_ERRORS metrics on Redis operations; docstring updated
- `backend/routes/search.py` — `_persist_results_to_redis()`, `_get_results_from_redis()`, 3-level `get_background_results_async()`
- `backend/llm_arbiter.py` — `_arbiter_cache_get_redis()`, `_arbiter_cache_set_redis()`, L1→L2 cache lookups
- `backend/redis_pool.py` — `get_sync_redis()` for ThreadPoolExecutor compat
- `backend/config.py` — `RESULTS_REDIS_TTL`, `ARBITER_REDIS_TTL`, `STATE_STORE_REDIS_PREFIX`
- `backend/metrics.py` — `STATE_STORE_ERRORS` counter
- `backend/tests/test_state_externalization.py` — 27 new tests

## Definition of Done

- [x] SSE funciona com WEB_CONCURRENCY=2 em 100% dos casos (Redis Streams + metadata)
- [x] Zero "tracker not found" errors com multiple workers (metadata fallback)
- [x] Todos os testes passando (27 new + full suite regression)
- [ ] PR merged
