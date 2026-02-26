---
task: "Audit Railway Configuration"
responsavel: "@infra-auditor"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - Railway project access
  - backend/start.sh
  - backend/config.py
Saida: |
  - Railway config assessment
  - Issues found
  - Recommendations
Checklist:
  - "[ ] Check GUNICORN_TIMEOUT value"
  - "[ ] Check PROCESS_TYPE (web vs worker)"
  - "[ ] Check worker count and memory allocation"
  - "[ ] Verify health check endpoint"
  - "[ ] Check auto-restart configuration"
  - "[ ] Verify deploy hooks"
  - "[ ] Check resource limits vs actual usage"
---

# *audit-railway

Validate Railway service configuration for production readiness.

## Steps

1. Read `backend/start.sh` — check Gunicorn config, timeout, workers
2. Read `backend/config.py` — check all Railway-related env vars
3. Run `railway status` — check service health
4. Run `railway variables` — verify all required vars present
5. Check Railway dashboard for resource usage (if CLI insufficient)

## Key Validations

- Gunicorn timeout >= 180s (Railway hard limit ~120s)
- Worker count appropriate for available RAM
- PROCESS_TYPE=web for API, PROCESS_TYPE=worker for ARQ
- Health endpoint at / or /health returns 200
- Auto-restart enabled
- No deployment failures in last 7 days

## Output

Score (0-10) + findings list + recommendations
