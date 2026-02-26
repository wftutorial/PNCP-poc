---
task: "Kickoff GTM Readiness Audit"
responsavel: "@gtm-orchestrator"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - Production URL (https://smartlic.tech)
  - Backend API URL (https://api.smartlic.tech)
  - Repository root directory
  - Target launch date (optional)
Saida: |
  - Audit scope document
  - Track assignments to agents
  - Timeline with checkpoints
Checklist:
  - "[ ] Define audit scope (full vs quick)"
  - "[ ] Verify production access"
  - "[ ] Verify API access"
  - "[ ] Assign tracks to agents"
  - "[ ] Set checkpoint timeline"
  - "[ ] Create shared findings document"
---

# *kickoff-gtm-audit

Launch the full GTM readiness audit across all 10 tracks.

## Steps

1. **Verify Access**: Confirm production URL and API are accessible
2. **Define Scope**: Full audit (3-5 days) or Quick healthcheck (4h)
3. **Assign Tracks**: Each of 9 agents gets their designated tracks
4. **Set Timeline**: Checkpoints at Day 1 (blockers), Day 3 (all tracks), Day 5 (scorecard)
5. **Create Findings Doc**: Shared document where all agents post per-track results

## Execution

Run Tracks 1-8 in parallel. Track 0 (orchestration) coordinates.

Tracks can be run independently — each agent audits their domain and reports:
- Score (0-10) per dimension
- Blockers found (P0/P1/P2)
- Remediation recommendations

## Output

Audit kickoff document with scope, assignments, and timeline.
