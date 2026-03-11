# Epic: GTM Readiness Sprint
**ID:** EPIC-GTM-001
**Date:** 2026-03-10
**Owner:** Engineering Team
**Source:** Brownfield Discovery Assessment v1.0

## Objective

Ship the remaining security verifications, conversion quick wins, CI hardening, and reliability improvements that separate SmartLic from a polished POC and a product worthy of paying customers at R$397-997/month. The assessment scored the platform at 8.0/10 (GREEN) with zero confirmed P0 blockers, but identified 9 P1 items and 19 P2 items that collectively represent the gap between "works" and "trustworthy." This sprint closes that gap in 8 weeks, front-loading the highest-ROI items into Week 1.

## Success Criteria

- [ ] All P0 items verified/resolved (RLS production state confirmed)
- [ ] All quick wins shipped (9 items, estimated +20-35% signup improvement)
- [ ] All P1 items resolved within 30 days
- [ ] Test coverage maintained at baseline (7332 backend / 5583 frontend)
- [ ] CI security scans (pip-audit, npm audit) running as blocking gates
- [ ] Zero-downtime deploy capability verified

## Stories

### Week 1: Quick Wins + P0 Verification
| Story ID | Title | Effort | Priority |
|----------|-------|--------|----------|
| DEBT-121 | Verify P0 RLS in Production | 10min | P0-verify |
| DEBT-122 | Ship Conversion Quick Wins (testimonials, annual default, CTA button) | 3h | P1 |
| DEBT-123 | Make CI Security Scans Blocking | 4-8h | P1 |
| DEBT-125 | Landing Page Product Screenshot | 6h | P1 |
| DEBT-126 | WhatsApp CTA on Pricing Page | 2h | P1 |
| DEBT-130 | E2E Python Version Fix | 5min | P2 |

### Weeks 2-4: P1 High Priority
| Story ID | Title | Effort | Priority |
|----------|-------|--------|----------|
| DEBT-124 | Graceful Shutdown / Zero-Downtime Deploys | 4h | P1 |
| DEBT-127 | Dashboard Actionable Insights | 8h | P1 |
| DEBT-129 | Capacity Limits Documentation + Alerting | 4h | P1 |

### Weeks 5-8: P2 Medium Priority
| Story ID | Title | Effort | Priority |
|----------|-------|--------|----------|
| DEBT-128 | Feature Flag Cleanup | 8h | P2 |

## Timeline

```
Week 1  [===========] P0 verify + quick wins + screenshot + CI scans
Week 2  [=====]        Graceful shutdown (DEBT-124)
Week 3  [========]     Dashboard insights (DEBT-127) + alerting (DEBT-129)
Week 4  [===]          Buffer / overflow from weeks 2-3
Week 5  [========]     Feature flag cleanup (DEBT-128)
Week 6-8 [...]         P2 items from assessment (not in this epic's stories)
```

## Dependencies

```
DEBT-121 (RLS verify)
  |
  v (if not applied -> deploy migration 027 immediately)

DEBT-123 (CI hardening) --- ship BEFORE other code fixes to ensure pipeline is secure
  |
  v
DEBT-124 (graceful shutdown) --> future P1-009 (horizontal scaling)
  |    scaling without shutdown = more deploy failures
  |
DEBT-125 (product screenshot) --> future P2-005 (next/image infra)
  |    needs image optimization before adding many visuals
  |
DEBT-122 (conversion quick wins) --- no blockers, ship immediately
DEBT-126 (WhatsApp CTA) --- no blockers
DEBT-127 (dashboard insights) --- no blockers, but benefits from DEBT-124
DEBT-128 (feature flags) --- no blockers
DEBT-129 (alerting) --- no blockers
DEBT-130 (E2E Python) --- no blockers, 5-minute fix
```

## Risk Mitigation

1. **If DEBT-121 fails (RLS not applied):** Deploy migration 027 immediately via `supabase db push --include-all`. Migration is idempotent and tested. Estimated recovery: 15 minutes.

2. **If DEBT-123 takes longer (CI audit findings):** Phase the rollout. Day 1: make pip-audit and npm audit blocking. Week 2: tackle pr-validation.yml. Deferred items do not block other stories.

3. **If DEBT-125 takes longer (screenshot design iteration):** Ship text-only hero improvement first (adjust layout/copy). Add screenshot as follow-up. Core conversion win is the testimonials import (DEBT-122), which is independent.

4. **If DEBT-124 is complex (Gunicorn lifecycle):** Start with FastAPI lifespan `shutdown` event for new-request rejection. Full drain behavior can be a follow-up. Partial fix still reduces deploy-time failures.

5. **If any story exceeds estimate by 2x:** Escalate to PM for scope cut. Every story has ACs that can be partially shipped (minimum viable improvement).
