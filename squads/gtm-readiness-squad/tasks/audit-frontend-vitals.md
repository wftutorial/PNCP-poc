---
task: "Audit Frontend Core Web Vitals"
responsavel: "@performance-auditor"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - frontend/next.config.js
  - Lighthouse workflow
  - Production URL
Saida: |
  - Core Web Vitals measurements
  - Bundle size analysis
  - Performance recommendations
Checklist:
  - "[ ] LCP < 2.5s"
  - "[ ] FID < 100ms"
  - "[ ] CLS < 0.1"
  - "[ ] TTFB < 800ms"
  - "[ ] Bundle size reasonable"
  - "[ ] Images optimized"
  - "[ ] Lighthouse >= 80"
---

# *audit-vitals

Measure Core Web Vitals and frontend performance.

## Steps

1. Run Lighthouse on production URL (or check lighthouse.yml results)
2. Check Next.js bundle analysis
3. Verify image optimization (next/image usage)
4. Check font loading strategy
5. Measure TTFB from multiple locations

## Output

Score (0-10) + vitals measurements + recommendations
