# GTM Readiness Squad

Ultra-comprehensive Go-To-Market readiness audit for SmartLic.

## Quick Start

```bash
# Full audit (3-5 days)
@gtm-orchestrator *kickoff

# Quick healthcheck (4 hours)
@gtm-orchestrator *quick-check
```

## What It Audits

| Track | Agent | Tasks | Focus |
|-------|-------|:-----:|-------|
| 0. Orchestration | @gtm-orchestrator | 4 | Scorecard, verdict, remediation |
| 1. Infrastructure | @infra-auditor | 6 | Railway, Supabase, Redis, DNS/SSL, CI/CD |
| 2. Security | @security-auditor | 6 | JWT, RLS, CVEs, LGPD, validation, secrets |
| 3. Billing | @billing-auditor | 5 | Stripe, payments, trial, pricing, webhooks |
| 4. Pipeline | @pipeline-auditor | 6 | PNCP, PCP, ComprasGov, breakers, cache, LLM |
| 5. UX/Product | @ux-auditor | 5 | Search flow, progress, errors, onboarding, mobile |
| 6. Performance | @performance-auditor | 4 | Latency, load, LLM throughput, Web Vitals |
| 7. Observability | @observability-auditor | 4 | Prometheus, Sentry, OTEL, alerting |
| 8. Market | @market-analyst | 4 | Positioning, gaps, social proof, acquisition |

**Total: 9 agents, 43 tasks, 2 workflows, 3 checklists**

## Scoring Model

10 weighted dimensions, 100-point scale:

- **GO**: Score >= 80, zero P0 blockers
- **CONDITIONAL GO**: Score 60-79 or P0s with <5 day fix
- **NO-GO**: Score < 60 or P0s with >5 day fix

## Deliverables

1. Executive Scorecard (10-dimension weighted)
2. Go/No-Go Verdict with conditions
3. Prioritized Remediation Plan
4. Risk Register
