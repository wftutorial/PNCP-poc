---
task: "Audit Sentry Coverage"
responsavel: "@observability-auditor"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - Sentry DSN configuration
  - backend/telemetry.py
  - frontend Sentry config
Saida: |
  - Sentry coverage assessment
  - Unresolved issues count
  - Alert configuration check
Checklist:
  - "[ ] Sentry DSN in backend production"
  - "[ ] Sentry DSN in frontend production"
  - "[ ] Unresolved issues: 0 target"
  - "[ ] PII scrubbing enabled"
  - "[ ] Source maps uploaded"
  - "[ ] Alert rules configured"
---

# *audit-sentry

Check Sentry error tracking coverage and configuration.

## Steps

1. Check Sentry DSN in backend config
2. Check Sentry DSN in frontend config
3. Review unresolved issue count (STORY-271 target: 0)
4. Verify PII scrubbing settings
5. Check alert rules

## Output

Score (0-10) + coverage report + recommendations
