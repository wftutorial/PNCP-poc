---
task: "Audit Alerting & Runbooks"
responsavel: "@observability-auditor"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - Alerting configuration
  - docs/ directory (runbooks)
Saida: |
  - Alerting rules inventory
  - Runbook coverage
  - Incident response readiness
Checklist:
  - "[ ] Alert on error rate > 5%"
  - "[ ] Alert on latency P95 > 120s"
  - "[ ] Alert on circuit breaker OPEN"
  - "[ ] Alert on Redis failure"
  - "[ ] Alert on Stripe webhook failure"
  - "[ ] Runbook: incident response"
  - "[ ] Runbook: source outage"
  - "[ ] On-call defined"
---

# *audit-alerting

Check alerting rules and incident response runbooks.

## Steps

1. Check Sentry alert rules
2. Check Prometheus alerting rules (if Grafana configured)
3. Search docs/ for runbooks or incident response docs
4. Verify on-call rotation (even if single person)
5. Check escalation paths

## Output

Score (0-10) + alerting inventory + runbook gaps
