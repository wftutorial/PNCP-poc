# GTM Validation Sprint Plan — "Ship or Fix"

**Created:** 2026-02-25 by @pm (Morgan)
**Source:** `docs/audits/gtm-validation-2026-02-25.md`
**Verdict:** CONDITIONAL-GO → 8 stories, 3 weeks to GTM
**Exit Criteria:** Zero BLOCKERs + Zero unresolved Sentry issues + 10 successful trial signups

---

## Sprint Overview

| Story | Title | Priority | Effort | Week | Squad |
|-------|-------|----------|--------|------|-------|
| **STORY-268** | Search Progress UX Fix | P0 BLOCKER | 3d | 1 | dev + ux + qa |
| **STORY-269** | Pricing Strategy Decision | P0 BLOCKER | 1d+2d | 1 | po + pm + dev |
| **STORY-270** | Email Alert Digests | P0 BLOCKER | 3-5d | 2 | dev + data-eng + qa |
| **STORY-271** | Sentry Issues → Zero | P0 | 1-2d | 1 | dev + devops |
| **STORY-272** | Security Hygiene | P1 | 1d | 1 | dev + devops |
| **STORY-273** | Social Proof + Trust | P1 | 2-3d | 2 | ux + dev + po |
| **STORY-274** | Infra Observability Polish | P2 | 1-2d | 3 | dev + devops |
| **STORY-275** | Boleto/PIX Payment | P2 | 2d | 3 | dev + qa |

**Total effort:** ~15-21 days across 3 weeks (parallelizable)

---

## Execution Order (Dependency Graph)

```
Week 1 (BLOCKERS + Quick Wins)
├── STORY-271: Sentry Zero (Day 1-2) ← FIRST, unblocks monitoring
├── STORY-272: Security Hygiene (Day 1) ← Quick, parallel with 271
├── STORY-268: Search Progress UX (Day 1-3) ← BLOCKER, longest
└── STORY-269: Pricing Decision (Day 1) ← PO decision, then implement

Week 2 (Table-Stakes + Trust)
├── STORY-270: Email Alerts (Day 4-8) ← BLOCKER, needs backend work
├── STORY-273: Social Proof (Day 4-6) ← PO provides content, dev implements
└── STORY-268: QA validation (Day 4-5) ← E2E testing of search fixes

Week 3 (Polish + Launch Prep)
├── STORY-274: Infra Observability (Day 9-10)
├── STORY-275: Boleto/PIX (Day 9-11)
├── GTM LAUNCH: Beta with invite (Day 12-15)
└── Monitor: 10 trial signups, 0 Sentry errors
```

---

## Gate Criteria

### Gate 1: End of Week 1 — "Core Fixed"
- [ ] STORY-268 AC1+AC2 merged (progress bar + error consolidation)
- [ ] STORY-271 AC1-AC5 merged (Sentry zero)
- [ ] STORY-272 AC1-AC5 merged (security hygiene)
- [ ] STORY-269 AC1 completed (pricing decision made)
- [ ] Sentry: 0 unresolved issues
- [ ] Backend tests: 0 failures
- [ ] Frontend tests: 0 failures

### Gate 2: End of Week 2 — "GTM Minimum"
- [ ] STORY-270 AC1-AC6 merged (email digests working)
- [ ] STORY-273 AC1-AC4 merged (social proof on landing + pricing)
- [ ] STORY-269 implementation complete
- [ ] 10 buscas consecutivas sem erro visível
- [ ] Sentry: 0 unresolved for 48h

### Gate 3: End of Week 3 — "GTM Launch"
- [ ] All 8 stories completed
- [ ] Production smoke test (Playwright): login → busca → resultado → download
- [ ] First 5-10 beta invites sent
- [ ] Monitoring dashboard active (Sentry + UptimeRobot + optionally Grafana)
- [ ] All content pages exist (/sobre, /blog, /ajuda)
- [ ] NPS survey mechanism in place

---

## Risk Register

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Starlette update breaks FastAPI | Medium | High | Pin version, run full test suite before merge |
| PO delays pricing decision | Medium | Critical | Timebox: 24h or default to Option 1 (beta gratuito) |
| Email alerts overload Resend free tier | Low | Medium | Start with DIGEST_EMAILS_ENABLED=false, manual batch |
| Beta users find new critical bugs | High | Medium | Sentry monitoring + 24h response SLA |
| Social proof content not ready | Medium | High | Use anonymized testimonials: "Empresa do setor X" |

---

## Success Metrics (30 days post-GTM)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Trial signups | 20+ | Supabase profiles count |
| Search success rate | >95% | Prometheus `smartlic_search_success_total` |
| Trial → paid conversion | >5% | Stripe subscriptions / signups |
| NPS | >30 | In-app survey |
| Sentry unresolved | 0 | Sentry dashboard |
| Churn (month 1) | <20% | Stripe cancellations |
