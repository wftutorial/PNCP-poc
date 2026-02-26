---
workflow: "Quick GTM Healthcheck"
responsavel: "@gtm-orchestrator"
responsavel_type: agent
atomic_layer: workflow
steps:
  - step: 1
    task: audit-jwt-auth.md
    description: "Check auth is working"
  - step: 2
    task: audit-dns-ssl-csp.md
    description: "Check CSP and SSL"
  - step: 3
    task: audit-pricing-strategy.md
    description: "Verify pricing display"
  - step: 4
    task: audit-pncp-client.md
    description: "Check primary data source"
  - step: 5
    task: audit-search-ux-flow.md
    description: "Test core search flow"
  - step: 6
    task: audit-sentry-coverage.md
    description: "Check error tracking"
  - step: 7
    task: compile-scorecard.md
    description: "Quick scorecard from 6 checks"
---

# Quick GTM Healthcheck Workflow

## Overview

Abbreviated healthcheck covering the 6 most critical areas. Use when you need a quick assessment, not a full audit.

**Duration:** 4 hours
**Focus:** P0 blockers + core functionality only
**Output:** Quick scorecard + blocker list

## When to Use

- Before a demo or investor meeting
- After a major deployment
- Weekly production health check
- Pre-marketing campaign sanity check

## Execution Flow

```
┌─────────────────────────────────────┐
│       QUICK GTM HEALTHCHECK         │
├─────────────────────────────────────┤
│                                     │
│  1. Auth working? (JWT)         5m  │
│  2. CSP/SSL OK? (DNS)          5m  │
│  3. Pricing correct? (Plans)   10m  │
│  4. PNCP alive? (Pipeline)    10m  │
│  5. Search works? (UX)        30m  │
│  6. Sentry clean? (Errors)     5m  │
│                                     │
│  7. Quick Scorecard            15m  │
│                                     │
│  Total: ~80 minutes                 │
│                                     │
└─────────────────────────────────────┘
```

## Quick Scoring

Score each of 6 areas as:
- PASS (10) — no issues found
- WARN (5) — non-blocking issues
- FAIL (0) — blocking issues

Quick score = average of 6 areas (0-10 scale)
