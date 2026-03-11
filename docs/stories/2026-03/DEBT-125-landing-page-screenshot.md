# DEBT-125: Landing Page Product Screenshot
**Priority:** P1
**Effort:** 6h
**Owner:** @ux + @dev
**Sprint:** Week 1, Day 3-4

## Context

The landing page has 6 sections (Hero, OpportunityCost, BeforeAfter, HowItWorks, Stats, CTA) but zero product visuals. B2G buyers are risk-averse and need to see what they are paying for before creating an account. The UX specialist identified this as the single highest-ROI conversion improvement, estimating +15-25% signup rate improvement. A static annotated screenshot is preferred over video (faster to load, easier to maintain, higher trust for B2G audience).

## Acceptance Criteria

- [ ] AC1: Hero section displays an annotated product screenshot on desktop in a 50/50 layout (text left, screenshot right)
- [ ] AC2: Mobile layout stacks the screenshot below the headline (full-width)
- [ ] AC3: Screenshot shows the `/buscar` results page (1280x800, cropped to filter panel + 3-4 result cards)
- [ ] AC4: 3 callout annotations visible on the screenshot: "Classificacao por IA", "Viabilidade 4 fatores", "Pipeline integrado"
- [ ] AC5: Image uses `next/image` with `priority={true}` for LCP optimization
- [ ] AC6: Image has descriptive Portuguese `alt` text (e.g., "Tela de resultados do SmartLic mostrando classificacao por IA e analise de viabilidade")
- [ ] AC7: Page loads in under 3 seconds on simulated 3G throttle (Chrome DevTools)
- [ ] AC8: Dark mode support -- either separate screenshot or CSS `filter` for automatic darkening

## Technical Notes

**Screenshot creation:**
1. Take screenshot of `/buscar` with realistic data (use production or seed data)
2. Crop to 1280x800 focusing on filter panel + result cards
3. Add 3 annotation callouts using Figma, Canva, or similar tool
4. Export as WebP (primary) + PNG (fallback) at 2x resolution for retina
5. Optimize: target under 150KB for WebP version

**Implementation:**
- File: `frontend/app/(landing)/HeroSection.tsx`
- Assets: `frontend/public/images/hero-screenshot.webp` + `hero-screenshot.png`
- Use `next/image` with `sizes` prop for responsive loading
- Consider `placeholder="blur"` with a low-res blur data URL

**Layout (desktop):**
```
[Headline + subtitle + CTA]  |  [Annotated Screenshot]
        50%                  |         50%
```

**Layout (mobile):**
```
[Headline + subtitle + CTA]
[Annotated Screenshot - full width]
```

## Test Requirements

- [ ] Existing landing page tests pass
- [ ] Image loads with `priority` attribute (check rendered HTML)
- [ ] Alt text is present and descriptive
- [ ] No CLS (Cumulative Layout Shift) on page load

## Files to Modify

- `frontend/app/(landing)/HeroSection.tsx` -- 50/50 layout with screenshot
- `frontend/public/images/` -- screenshot assets (WebP + PNG)

## Definition of Done

- [ ] All ACs pass
- [ ] Tests pass (existing + new)
- [ ] No regressions in CI
- [ ] Lighthouse performance score does not decrease
- [ ] Code reviewed
