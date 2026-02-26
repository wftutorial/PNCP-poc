---
task: "Checkpoint: All Tracks Complete"
responsavel: "@gtm-orchestrator"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - Per-track reports (8 tracks)
  - Per-track scores (0-10)
Saida: |
  - Track completion status
  - Ready for scorecard compilation
Checklist:
  - "[ ] Track 1 (Infra) complete"
  - "[ ] Track 2 (Security) complete"
  - "[ ] Track 3 (Billing) complete"
  - "[ ] Track 4 (Pipeline) complete"
  - "[ ] Track 5 (UX) complete"
  - "[ ] Track 6 (Performance) complete"
  - "[ ] Track 7 (Observability) complete"
  - "[ ] Track 8 (Market) complete"
  - "[ ] All tracks submitted scores"
---

# *checkpoint-complete

Synchronization point: verify all 8 audit tracks are complete.

## Steps

1. Collect completion status from all 8 tracks
2. Verify each track submitted a score (0-10)
3. Verify each track submitted findings list
4. Flag any incomplete tracks
5. Trigger scorecard compilation

## Gate Criteria

- All 8 tracks must submit scores and findings
- If any track incomplete → extend timeline or reduce scope

## Output

Track completion matrix + trigger for scorecard compilation
