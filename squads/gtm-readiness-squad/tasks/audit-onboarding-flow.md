---
task: "Audit Onboarding Flow"
responsavel: "@ux-auditor"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - frontend/app/onboarding/page.tsx
  - Onboarding components
Saida: |
  - Onboarding friction analysis
  - Step completion rate estimation
  - Improvement recommendations
Checklist:
  - "[ ] Signup → onboarding redirect works"
  - "[ ] CNAE step has helper text or is optional"
  - "[ ] UF selection allows multiple"
  - "[ ] Confirmation shows summary"
  - "[ ] Skip option available"
  - "[ ] Phone field: optional?"
---

# *audit-onboarding

Test the onboarding wizard for friction points.

## Steps

1. Read onboarding page component
2. Walk through each step
3. Identify friction points (CNAE knowledge required? Phone required?)
4. Check skip/later options
5. Verify first-search guided experience

## Output

Score (0-10) + friction analysis + recommendations
