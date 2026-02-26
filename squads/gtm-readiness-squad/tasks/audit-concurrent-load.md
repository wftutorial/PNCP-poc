---
task: "Audit Concurrent Load"
responsavel: "@performance-auditor"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - .github/workflows/load-test.yml
  - k6 test scripts (if any)
  - Connection pool configs
Saida: |
  - Concurrent load test results
  - Connection pool assessment
  - Scaling recommendations
Checklist:
  - "[ ] 10 concurrent: all succeed"
  - "[ ] 50 concurrent: <5% error"
  - "[ ] 100 concurrent: graceful degradation"
  - "[ ] Redis pool sized correctly"
  - "[ ] Supabase pool sized correctly"
  - "[ ] InMemoryCache thread-safe"
---

# *audit-load

Test system behavior under concurrent load.

## Steps

1. Check if k6 load test scripts exist
2. Review connection pool configurations
3. Check load-test.yml workflow config
4. Analyze results from any previous load tests
5. Recommend load test plan if none exists

## Output

Score (0-10) + load capacity assessment + recommendations
