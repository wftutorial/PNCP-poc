---
task: "Audit Circuit Breakers"
responsavel: "@pipeline-auditor"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - Circuit breaker implementations in all clients
  - backend/redis_client.py
Saida: |
  - Circuit breaker configuration report
  - Per-source isolation validation
  - State transition correctness
Checklist:
  - "[ ] Per-source isolation (PNCP/PCP/ComprasGov)"
  - "[ ] Threshold values appropriate"
  - "[ ] Cooldown period reasonable (60s)"
  - "[ ] Half-open state transitions correct"
  - "[ ] Metrics emitted on state changes"
  - "[ ] Redis-backed state (survives restart)"
---

# *audit-breakers

Validate circuit breaker configuration and isolation.

## Steps

1. Find circuit breaker implementation in each client
2. Verify per-source isolation (failure in one doesn't affect others)
3. Check threshold values (PNCP: 15 failures)
4. Verify cooldown period (60s)
5. Test half-open → closed transition

## Output

Score (0-10) + configuration report + recommendations
