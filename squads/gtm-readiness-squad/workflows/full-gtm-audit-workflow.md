---
workflow: "Full GTM Readiness Audit"
responsavel: "@gtm-orchestrator"
responsavel_type: agent
atomic_layer: workflow
steps:
  - step: 1
    task: kickoff-gtm-audit.md
    description: "Define scope, assign tracks, set timeline"
  - step: 2
    task: audit-jwt-auth.md
    description: "PRIORITY — Check P0 auth blocker first"
  - step: 3
    task: audit-dns-ssl-csp.md
    description: "PRIORITY — Check P0 CSP blocker"
  - step: 4
    task: checkpoint-blockers-resolved.md
    description: "Gate — All P0s must have fix plans before continuing"
  - step: 5
    task: audit-railway-config.md
    description: "Track 1: Infrastructure parallel start"
  - step: 6
    task: audit-stripe-integration.md
    description: "Track 3: Billing parallel start"
  - step: 7
    task: audit-pncp-client.md
    description: "Track 4: Pipeline parallel start"
  - step: 8
    task: audit-search-ux-flow.md
    description: "Track 5: UX parallel start"
  - step: 9
    task: audit-search-latency.md
    description: "Track 6: Performance parallel start"
  - step: 10
    task: audit-prometheus-metrics.md
    description: "Track 7: Observability parallel start"
  - step: 11
    task: audit-competitive-positioning.md
    description: "Track 8: Market parallel start"
  - step: 12
    task: checkpoint-all-tracks-complete.md
    description: "Gate — All 8 tracks must be complete"
  - step: 13
    task: compile-scorecard.md
    description: "Compile weighted executive scorecard"
  - step: 14
    task: generate-go-nogo-verdict.md
    description: "Issue GO / CONDITIONAL GO / NO-GO verdict"
  - step: 15
    task: create-remediation-plan.md
    description: "Prioritized fix plan for all findings"
---

# Full GTM Readiness Audit Workflow

## Overview

Complete 10-dimension audit of SmartLic production readiness for Go-To-Market launch.

**Duration:** 3-5 days
**Agents:** 9 specialized auditors
**Output:** Executive scorecard + Go/No-Go verdict + Remediation plan

## Execution Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    FULL GTM READINESS AUDIT                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PHASE 1: KICKOFF (Day 0)                                      │
│  ┌───────────────────────────────────┐                          │
│  │ 1. @gtm-orchestrator              │                          │
│  │    *kickoff-gtm-audit             │                          │
│  │    → Scope, assignments, timeline │                          │
│  └───────────────────────────────────┘                          │
│                                                                 │
│  PHASE 2: P0 BLOCKERS (Day 1)                                  │
│  ┌──────────────────┐ ┌──────────────────┐                     │
│  │ 2. @security      │ │ 3. @infra        │                    │
│  │    *audit-jwt     │ │    *audit-dns-ssl│                     │
│  │    → ES256 check  │ │    → CSP check   │                    │
│  └────────┬─────────┘ └────────┬─────────┘                     │
│           └────────┬───────────┘                                │
│                    ▼                                            │
│  ┌───────────────────────────────────┐                          │
│  │ 4. CHECKPOINT: Blockers Resolved  │                          │
│  │    → All P0s fixed or planned     │                          │
│  └───────────────────────────────────┘                          │
│                                                                 │
│  PHASE 3: PARALLEL TRACKS (Days 2-4)                           │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐                  │
│  │Track 1 │ │Track 3 │ │Track 4 │ │Track 5 │                  │
│  │Infra   │ │Billing │ │Pipeline│ │UX      │                  │
│  │6 tasks │ │5 tasks │ │6 tasks │ │5 tasks │                  │
│  └────┬───┘ └────┬───┘ └────┬───┘ └────┬───┘                  │
│  ┌────┴───┐ ┌────┴───┐ ┌────┴───┐ ┌────┴───┐                  │
│  │Track 6 │ │Track 7 │ │Track 8 │ │Track 2 │                  │
│  │Perf    │ │Observ  │ │Market  │ │Security│                  │
│  │4 tasks │ │4 tasks │ │4 tasks │ │6 tasks │                  │
│  └────┬───┘ └────┬───┘ └────┬───┘ └────┬───┘                  │
│       └──────┬───┴─────┬────┴──────┬───┘                       │
│              ▼                                                  │
│  ┌───────────────────────────────────┐                          │
│  │ 12. CHECKPOINT: All Tracks Done   │                          │
│  │     → 8 track reports + scores    │                          │
│  └───────────────────────────────────┘                          │
│                                                                 │
│  PHASE 4: SYNTHESIS (Day 5)                                    │
│  ┌───────────────────────────────────┐                          │
│  │ 13. @gtm-orchestrator             │                          │
│  │     *compile-scorecard            │                          │
│  │     → 10-dimension weighted score │                          │
│  └───────────────┬───────────────────┘                          │
│                  ▼                                              │
│  ┌───────────────────────────────────┐                          │
│  │ 14. @gtm-orchestrator             │                          │
│  │     *verdict                      │                          │
│  │     → GO / CONDITIONAL / NO-GO    │                          │
│  └───────────────┬───────────────────┘                          │
│                  ▼                                              │
│  ┌───────────────────────────────────┐                          │
│  │ 15. @gtm-orchestrator             │                          │
│  │     *remediation                  │                          │
│  │     → Prioritized fix plan        │                          │
│  └───────────────────────────────────┘                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Success Criteria

- All 8 tracks completed with scores
- Executive scorecard generated
- Go/No-Go verdict issued
- Remediation plan created with owners and timelines

## Rollback

If audit reveals critical issues:
1. Pause all marketing/acquisition activities
2. Focus on P0 blocker resolution
3. Re-run affected tracks after fixes
4. Recompile scorecard
