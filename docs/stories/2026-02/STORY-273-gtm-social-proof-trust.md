# STORY-273: Add Social Proof + Trust Signals

**GTM Audit Ref:** H1 (zero social proof) + B3 (pricing page) + M16 (/sobre 404) + L1 (LGPD badge)
**Priority:** P1
**Effort:** 2-3 days
**Squad:** @ux-design-expert + @dev + @po
**Source:** `docs/audits/gtm-validation-2026-02-25.md`, Track B + Track E

## Context

SmartLic has ZERO social proof anywhere on the site:
- 0 testimonials
- 0 customer logos
- 0 case studies
- 0 user count
- 0 reviews on B2B Stack or similar

At R$1,999/month (or whatever the repriced amount is), buyers NEED validation from peers. ConLicitação has 16K+ clients, Siga Pregão has 217 reviews at 4.9★. SmartLic has nothing.

The `/sobre` page is linked from the landing page credibility badge but returns 404.

## Acceptance Criteria

### AC1: Testimonial Section on Landing Page
- [ ] New component: `TestimonialSection.tsx`
- [ ] Displays 3-6 testimonial cards with:
  - Quote text (2-3 sentences)
  - Name + role + company (or "Empresa do setor X" if anonymous)
  - Star rating (optional)
  - Company sector badge
- [ ] Initially populated with beta user feedback or PO-curated content
- [ ] Positioned between `BeforeAfter` and `ComparisonTable` sections
- [ ] **File:** `frontend/app/page.tsx`, new component

### AC2: Testimonials on Pricing Page
- [ ] Add 2-3 testimonials to `/planos` page
- [ ] Position below plan card, above FAQ
- [ ] "Empresas que já usam SmartLic" heading
- [ ] **File:** `frontend/app/planos/page.tsx`

### AC3: "Empresas em Beta" Counter
- [ ] Add "X empresas já testaram" counter on landing page
- [ ] Dynamic: fetch from backend or hardcode initial number
- [ ] Position near FinalCTA section
- [ ] Even "5 empresas do setor de uniformes já testaram" is better than nothing

### AC4: Create /sobre Page
- [ ] Create `frontend/app/sobre/page.tsx`
- [ ] Content:
  - CONFENGE company description
  - Team (even if small — "fundadores com X anos de experiência em Y")
  - Mission/vision related to B2G market
  - Methodology section (how SmartLic evaluates opportunities)
  - Contact information
- [ ] Fix credibility badge link (currently goes to 404)
- [ ] **File:** `frontend/app/sobre/page.tsx` (**NEW**)

### AC5: Fix LGPD Badge Language
- [ ] Change "LGPD Compliant" to "Em conformidade com a LGPD" in footer
- [ ] **File:** Footer component

### AC6: Stripe/Security Badge on Pricing
- [ ] Add Stripe logo/badge on pricing page checkout area
- [ ] "Pagamento seguro" with lock icon + Stripe wordmark
- [ ] **File:** `frontend/app/planos/page.tsx`

## Content Required (from PO)

The PO must provide or approve:
- [ ] 3-6 testimonial quotes (from beta users, early testers, or curated)
- [ ] Company descriptions for testimonials (can be anonymized by sector)
- [ ] /sobre page content (company history, team, methodology)
- [ ] "Empresas em beta" count (real number)

## Testing Strategy

- [ ] Unit tests: TestimonialSection renders with 0, 3, 6 testimonials
- [ ] Unit tests: /sobre page renders without error
- [ ] Snapshot test: landing page with testimonials section
- [ ] Manual: verify /sobre link works from credibility badge
- [ ] Manual: verify LGPD badge is in Portuguese
- [ ] Regression: existing landing page tests pass

## Files to Create/Modify

| File | Change |
|------|--------|
| `frontend/components/TestimonialSection.tsx` | **NEW** — Testimonial cards |
| `frontend/app/page.tsx` | Add TestimonialSection import |
| `frontend/app/planos/page.tsx` | Add testimonials + Stripe badge |
| `frontend/app/sobre/page.tsx` | **NEW** — About page |
| `frontend/components/Footer.tsx` | Fix LGPD badge language |
| `frontend/__tests__/` | Tests for new components |

## Dependencies

- PO must provide testimonial content (can be placeholder → replace with real)
- Does NOT depend on pricing decision (STORY-269)
