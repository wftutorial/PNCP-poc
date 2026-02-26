---
task: "Audit Progress Feedback"
responsavel: "@ux-auditor"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - frontend/app/buscar/components/EnhancedLoadingProgress.tsx
  - backend/progress.py
  - SSE implementation
Saida: |
  - Progress UX assessment
  - SSE reliability check
  - User perception analysis
Checklist:
  - "[ ] Progress starts immediately (not stuck at 0%)"
  - "[ ] Bar advances smoothly (not frozen at 10%)"
  - "[ ] Per-UF progress visible"
  - "[ ] Source badges show API status"
  - "[ ] SSE connects within 2s"
  - "[ ] SSE fallback works"
  - "[ ] Messaging is encouraging"
---

# *audit-progress

Validate progress feedback during search operations.

## P1 KNOWN ISSUE

Progress bar freezes at 10% for 90+ seconds. Users think the product is broken.

## Steps

1. Read EnhancedLoadingProgress.tsx — check progress logic
2. Read backend/progress.py — check SSE events
3. Test search with 3-5 UFs — observe progress bar
4. Test search with 27 UFs — observe long wait experience
5. Kill SSE connection mid-search — verify fallback

## Output

Score (0-10) + P1 status + UX recommendations
