---
task: "Audit PCP v2 Client"
responsavel: "@pipeline-auditor"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - backend/portal_compras_client.py
  - backend/clients/ directory
Saida: |
  - PCP v2 client assessment
  - Pagination validation
  - UF filtering check
Checklist:
  - "[ ] No auth required (public API)"
  - "[ ] Fixed 10/page pagination"
  - "[ ] Client-side UF filtering works"
  - "[ ] valor_estimado=0.0 handled"
  - "[ ] Dedup with PNCP correct"
  - "[ ] Circuit breaker independent"
---

# *audit-pcp

Validate PCP v2 client configuration.

## Steps

1. Read `backend/portal_compras_client.py` — check pagination, auth
2. Verify no API key required
3. Check UF filtering (client-side only)
4. Verify dedup priority (PCP=2 loses to PNCP=1)
5. Check circuit breaker independence

## Output

Score (0-10) + findings + recommendations
