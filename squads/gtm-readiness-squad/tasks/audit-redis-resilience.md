---
task: "Audit Redis Resilience"
responsavel: "@infra-auditor"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - backend/redis_client.py
  - backend/redis_pool.py
  - backend/cache.py
  - backend/search_cache.py
Saida: |
  - Redis health assessment
  - Connection pool analysis
  - Cache strategy validation
Checklist:
  - "[ ] Check Redis connection stability"
  - "[ ] Verify connection pool sizing"
  - "[ ] Check memory usage vs limits"
  - "[ ] Validate circuit breaker Redis keys"
  - "[ ] Verify SSE streams (XREAD/XADD) working"
  - "[ ] Check TTL configuration (L1: 4h, L2: 24h)"
---

# *audit-redis

Validate Redis connectivity, pool config, and cache strategy.

## Steps

1. Read `backend/redis_client.py` + `redis_pool.py` — pool config
2. Read `backend/cache.py` + `search_cache.py` — cache strategy
3. Check Redis connection (via railway run or health endpoint)
4. Verify circuit breaker keys exist and function
5. Check memory usage vs plan limits

## Output

Score (0-10) + findings list + recommendations
