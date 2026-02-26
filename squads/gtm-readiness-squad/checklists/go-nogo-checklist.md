# Go/No-Go Checklist

Use this checklist for the final go/no-go decision before GTM launch.

## P0 Blockers (ALL must pass)

- [ ] **AUTH**: JWT authentication works (ES256 compatible)
- [ ] **CSP**: Frontend can communicate with API (connect-src)
- [ ] **PLANS**: Plans page shows correct pricing and plan cards
- [ ] **SEARCH**: Core search flow works end-to-end
- [ ] **BILLING**: At least one payment method works (card)
- [ ] **DATA**: PNCP returns results (primary source alive)

## P1 Critical (80% must pass)

- [ ] **PROGRESS**: Progress bar doesn't freeze for >30s
- [ ] **ERRORS**: No overlapping error messages
- [ ] **TRIAL**: Trial creation and quota enforcement work
- [ ] **CACHE**: Stale cache serves when sources fail
- [ ] **SENTRY**: Zero unresolved critical errors
- [ ] **PRICING**: R$397 displayed (not R$1.999)
- [ ] **SSL**: Valid certificate, HSTS enabled
- [ ] **CI/CD**: All quality gates passing on main
- [ ] **WEBHOOKS**: Stripe webhooks processing correctly
- [ ] **METRICS**: /metrics endpoint accessible

## P2 Important (50% should pass)

- [ ] **OTEL**: Tracing exported to backend
- [ ] **ALERTS**: At least error rate alert configured
- [ ] **SOCIAL**: Testimonials on landing page
- [ ] **MOBILE**: Core pages usable on mobile
- [ ] **ONBOARDING**: New user wizard functional
- [ ] **SEO**: Meta tags and sitemap present
- [ ] **EMAIL**: Welcome email sends
- [ ] **LGPD**: Cookie consent and privacy policy
- [ ] **CVE**: No critical/high unpatched vulnerabilities
- [ ] **LOAD**: Handles 10 concurrent searches

## Verdict Rules

| P0 Pass | P1 Pass | P2 Pass | Verdict |
|---------|---------|---------|---------|
| 6/6 | 8+/10 | 5+/10 | **GO** |
| 6/6 | 6-7/10 | any | **CONDITIONAL GO** |
| 6/6 | <6/10 | any | **NO-GO** |
| <6/6 | any | any | **NO-GO** |
