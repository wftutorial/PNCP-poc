---
task: "Audit Cache Cascade"
responsavel: "@pipeline-auditor"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - backend/cache.py
  - backend/search_cache.py
  - backend/redis_client.py
Saida: |
  - Cache strategy validation
  - SWR behavior check
  - TTL configuration report
Checklist:
  - "[ ] L1 InMemoryCache: 4h TTL"
  - "[ ] L2 Supabase: 24h TTL"
  - "[ ] Fresh (0-6h) served directly"
  - "[ ] Stale (6-24h) served + background revalidation"
  - "[ ] Expired (>24h) not served"
  - "[ ] Max 3 concurrent background revalidations"
  - "[ ] Cache survives restart (L2)"
  - "[ ] Cache key includes all params"
---

# *audit-cache

Validate two-level cache with Stale-While-Revalidate.

## Steps

1. Read `backend/cache.py` — check InMemoryCache config
2. Read `backend/search_cache.py` — check Supabase cache
3. Verify TTL values (L1: 4h, L2: 24h)
4. Check SWR logic (stale served + background refresh)
5. Verify background revalidation limits (max 3 concurrent)

## Output

Score (0-10) + cache strategy assessment + recommendations
