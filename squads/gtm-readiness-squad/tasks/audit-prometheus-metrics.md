---
task: "Audit Prometheus Metrics"
responsavel: "@observability-auditor"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - backend/metrics.py
  - /metrics endpoint
Saida: |
  - Metrics coverage report
  - Scraper configuration check
  - Dashboard availability
Checklist:
  - "[ ] /metrics endpoint accessible"
  - "[ ] METRICS_TOKEN auth configured"
  - "[ ] 11 metrics defined and emitting"
  - "[ ] Scraper connected (Grafana)"
  - "[ ] Dashboards created"
---

# *audit-prometheus

Validate Prometheus metrics coverage and scraping.

## Steps

1. Read backend/metrics.py — list all defined metrics
2. Check /metrics endpoint accessibility
3. Verify METRICS_TOKEN authentication
4. Check if scraper is connected
5. Verify dashboards exist

## Output

Score (0-10) + metrics coverage + recommendations
