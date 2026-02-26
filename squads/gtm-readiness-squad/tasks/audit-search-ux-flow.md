---
task: "Audit Search UX Flow"
responsavel: "@ux-auditor"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - frontend/app/buscar/page.tsx
  - frontend/app/buscar/components/
  - Production URL
Saida: |
  - Search flow UX assessment
  - Friction points identified
  - Improvement recommendations
Checklist:
  - "[ ] UF selection works"
  - "[ ] Date range picker works"
  - "[ ] Sector selection works"
  - "[ ] Search submit triggers correctly"
  - "[ ] Results display properly"
  - "[ ] Excel download works"
  - "[ ] Empty results show helpful message"
  - "[ ] Saved searches work"
---

# *audit-search-ux

Test the complete search user experience flow.

## Steps

1. Navigate to /buscar on production
2. Test UF selection (single, multiple, all)
3. Test date range (default 10 days, custom)
4. Test sector selection (all 15 sectors)
5. Submit search and observe progress
6. Verify results display
7. Test Excel download
8. Test empty results handling

## Use Playwright MCP for browser automation testing.

## Output

Score (0-10) + friction points + recommendations
