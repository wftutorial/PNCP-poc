---
task: "Audit PNCP Client"
responsavel: "@pipeline-auditor"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - backend/pncp_client.py
  - backend/config.py (PNCP settings)
Saida: |
  - PNCP client health assessment
  - Pagination/retry/batching validation
  - Circuit breaker config check
Checklist:
  - "[ ] tamanhoPagina=50 enforced"
  - "[ ] Retry with exponential backoff"
  - "[ ] HTTP 422 retried (max 1)"
  - "[ ] HTTP 429 respects Retry-After"
  - "[ ] Circuit breaker: 15 failures, 60s cooldown"
  - "[ ] Phased batching: 5 UFs, 2s delay"
  - "[ ] Health canary uses tamanhoPagina >= 10"
  - "[ ] requests.ConnectionError caught (CRIT-038)"
---

# *audit-pncp

Validate PNCP client configuration and resilience.

## Steps

1. Read `backend/pncp_client.py` — check pagination, retry, batching
2. Read `backend/config.py` — check PNCP_BATCH_SIZE, PNCP_BATCH_DELAY_S
3. Verify tamanhoPagina=50 (not >50, API returns 400 silently)
4. Check health canary parameter (must be >=10, not 1)
5. Verify CRIT-038 fix: requests.ConnectionError in retry handler

## Known Issues

- Health canary may use tamanhoPagina=1 (API requires >=10)
- tamanhoPagina was silently reduced from 500 to 50 by PNCP

## Output

Score (0-10) + findings + recommendations
