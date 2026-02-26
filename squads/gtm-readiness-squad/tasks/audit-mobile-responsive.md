---
task: "Audit Mobile Responsiveness"
responsavel: "@ux-auditor"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - All frontend pages
  - Tailwind responsive classes
Saida: |
  - Mobile responsiveness report
  - Broken layouts identified
  - Touch target assessment
Checklist:
  - "[ ] Landing page mobile OK"
  - "[ ] Login/signup mobile OK"
  - "[ ] Search form mobile OK"
  - "[ ] Results mobile OK"
  - "[ ] Pipeline kanban mobile alternative"
  - "[ ] Navigation menu works"
  - "[ ] Touch targets >= 44px"
  - "[ ] No horizontal scroll"
---

# *audit-mobile

Test responsive design across mobile viewports.

## Steps

1. Test all key pages at 375px width (iPhone SE)
2. Test at 390px (iPhone 13)
3. Check navigation (hamburger menu)
4. Verify touch targets (minimum 44px)
5. Check for horizontal overflow

## Use Playwright MCP with mobile viewport for testing.

## Output

Score (0-10) + broken layouts + recommendations
