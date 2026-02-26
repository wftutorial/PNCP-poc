---
task: "Compile Executive Scorecard"
responsavel: "@gtm-orchestrator"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - Per-track audit results (8 track reports)
  - Scoring weights per dimension
  - Blocker list with severity
Saida: |
  - Executive scorecard (10 dimensions, weighted score)
  - Blocker summary with owners
  - Risk register
Checklist:
  - "[ ] Collect all 8 track reports"
  - "[ ] Apply dimension weights"
  - "[ ] Calculate weighted total score"
  - "[ ] List all P0 blockers"
  - "[ ] List all P1 issues"
  - "[ ] Create risk register"
  - "[ ] Generate visual scorecard"
---

# *compile-scorecard

Compile findings from all audit tracks into a weighted executive scorecard.

## Scoring Model

| Dimension | Weight | Source Track |
|-----------|--------|-------------|
| Infrastructure & Platform | 12% | Track 1 |
| Authentication & Security | 15% | Track 2 |
| Billing & Monetization | 12% | Track 3 |
| Search Pipeline Resilience | 15% | Track 4 |
| UX & Product Quality | 12% | Track 5 |
| Performance & Scalability | 10% | Track 6 |
| Observability & Monitoring | 8% | Track 7 |
| Market & Competitive | 8% | Track 8 |
| Content & Communication | 4% | Track 5 (subset) |
| Legal & Compliance | 4% | Track 2 (subset) |

## Calculation

1. Each track reports a score 0-10
2. Multiply by weight, sum all = weighted score (0-100)
3. List all blockers by severity (P0 > P1 > P2)
4. Generate risk register (risk, likelihood, impact, mitigation)

## Output Format

Use the scorecard-template.md from templates/.
