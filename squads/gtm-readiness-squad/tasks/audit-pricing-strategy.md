---
task: "Audit Pricing Strategy"
responsavel: "@billing-auditor"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - Current pricing (STORY-277 repricing)
  - Competitor pricing data
  - frontend/app/planos/page.tsx
Saida: |
  - Pricing competitiveness assessment
  - Plan display validation
  - Recommendation for pricing adjustments
Checklist:
  - "[ ] Plans page shows R$397 (not R$1.999)"
  - "[ ] Annual discount displayed"
  - "[ ] Feature comparison accurate"
  - "[ ] Price competitive with market (R$45-397)"
  - "[ ] Free tier demonstrates value"
  - "[ ] No broken plan cards"
---

# *audit-pricing

Validate pricing display and competitiveness.

## Steps

1. Check frontend plans page for correct pricing
2. Compare against known competitors (Alerta Licitacao R$45, ConLicitacao R$149, Siga Pregao R$397)
3. Verify STORY-277 repricing deployed correctly
4. Check plan features match actual functionality
5. Verify pricing page loads without auth

## Market Context

| Competitor | Price | Notes |
|-----------|-------|-------|
| Alerta Licitacao | R$45/mo | Basic alerts |
| LicitaIA | R$67-247/mo | AI features |
| Licitei | R$101-393/mo | Q&A AI |
| ConLicitacao | R$149/mo | Search + docs |
| Siga Pregao | R$397/mo | Full suite |
| **SmartLic** | **R$397/mo** | **AI viability + multi-source** |

## Output

Score (0-10) + pricing assessment + recommendations
