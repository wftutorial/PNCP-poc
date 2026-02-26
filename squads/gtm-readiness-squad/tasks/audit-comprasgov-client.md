---
task: "Audit ComprasGov v3 Client"
responsavel: "@pipeline-auditor"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - backend/compras_gov_client.py
  - backend/clients/ directory
Saida: |
  - ComprasGov v3 assessment
  - Dual-endpoint validation
  - Fallback behavior check
Checklist:
  - "[ ] Dual-endpoint: legacy + Lei 14.133"
  - "[ ] Base URL: dadosabertos.compras.gov.br"
  - "[ ] Timeout appropriate"
  - "[ ] Dedup with PNCP and PCP"
  - "[ ] Graceful timeout (low priority)"
---

# *audit-comprasgov

Validate ComprasGov v3 client configuration.

## Steps

1. Read ComprasGov client — check dual-endpoint setup
2. Verify base URL
3. Check timeout configuration (can be shorter, priority 3)
4. Verify dedup with other sources
5. Check error handling

## Output

Score (0-10) + findings + recommendations
