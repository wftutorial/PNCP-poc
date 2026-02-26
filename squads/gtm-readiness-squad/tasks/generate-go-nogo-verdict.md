---
task: "Generate Go/No-Go Verdict"
responsavel: "@gtm-orchestrator"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - Executive scorecard
  - Blocker list
  - Remediation estimates
Saida: |
  - GO / CONDITIONAL GO / NO-GO verdict
  - Conditions for CONDITIONAL GO
  - Timeline to resolve conditions
Checklist:
  - "[ ] Review weighted score vs thresholds"
  - "[ ] Count P0 blockers"
  - "[ ] Estimate P0 fix time"
  - "[ ] Determine verdict"
  - "[ ] Document conditions"
  - "[ ] Set re-evaluation date"
---

# *verdict

Generate the final go/no-go verdict for GTM launch.

## Decision Matrix

| Score | P0 Blockers | Fix Time | Verdict |
|-------|-------------|----------|---------|
| >= 80 | 0 | N/A | **GO** |
| >= 80 | >0 | < 3 days | **CONDITIONAL GO** |
| 60-79 | 0 | N/A | **CONDITIONAL GO** |
| 60-79 | >0 | < 5 days | **CONDITIONAL GO** |
| 60-79 | >0 | >= 5 days | **NO-GO** |
| < 60 | any | any | **NO-GO** |

## Verdict Output

For each verdict type:

**GO**: List any P1/P2 items to fix post-launch
**CONDITIONAL GO**: List exact conditions, owners, and deadline
**NO-GO**: List blockers, estimated fix timeline, re-evaluation date
