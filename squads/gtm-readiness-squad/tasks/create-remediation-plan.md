---
task: "Create Remediation Plan"
responsavel: "@gtm-orchestrator"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - All findings from tracks 1-8
  - Blocker list with severity
  - Resource availability
Saida: |
  - Prioritized remediation plan
  - Sprint backlog (stories + tasks)
  - Timeline with milestones
Checklist:
  - "[ ] Prioritize by impact: P0 → P1 → P2"
  - "[ ] Estimate effort per item (XS/S/M/L/XL)"
  - "[ ] Assign owners to each item"
  - "[ ] Create sprint plan (6-day cycles)"
  - "[ ] Define milestones"
  - "[ ] Set re-audit date"
---

# *remediation

Create prioritized remediation plan from all audit findings.

## Priority Framework

**P0 (Blocker)** — Must fix before ANY GTM activity
- Fix within: 1-3 days
- Examples: JWT auth broken, CSP blocks API, plans page empty

**P1 (High)** — Must fix before paid acquisition
- Fix within: 1 week
- Examples: Progress UX, email alerts, double error messages

**P2 (Medium)** — Should fix within 30 days
- Fix within: 1 month
- Examples: OTEL endpoint, metrics auth, onboarding friction

**P3 (Low)** — Roadmap items
- Fix within: quarter
- Examples: Mobile app, proposal generation, document management

## Output

Remediation plan using remediation-plan-template.md from templates/.
