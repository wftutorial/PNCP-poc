---
task: "Audit Search Latency"
responsavel: "@performance-auditor"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - backend/search_pipeline.py
  - backend/config.py (timeout chain)
  - Production metrics
Saida: |
  - Latency measurements P50/P95/P99
  - Timeout chain validation
  - Bottleneck identification
Checklist:
  - "[ ] 1-3 UFs < 30s (P95)"
  - "[ ] 5-10 UFs < 60s (P95)"
  - "[ ] 27 UFs < 180s (P95)"
  - "[ ] Timeout chain enforced correctly"
  - "[ ] Railway 120s proxy limit considered"
---

# *audit-latency

Measure search latency and validate timeout chain.

## Steps

1. Read search_pipeline.py — check timeout configuration
2. Read config.py — verify timeout chain values
3. Run test searches (3 UFs, 10 UFs, 27 UFs)
4. Measure end-to-end latency
5. Identify bottleneck in pipeline

## Timeout Chain (expected)

FE(480s) > Pipeline(360s) > Global(300s) > Source(180s) > UF(90s)

## Output

Score (0-10) + latency measurements + bottlenecks
