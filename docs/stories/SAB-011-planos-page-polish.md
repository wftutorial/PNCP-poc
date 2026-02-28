# SAB-011: Planos — remover badge BETA e melhorar heading

**Origem:** UX Premium Audit P2-03, P2-04
**Prioridade:** P2 — Médio
**Complexidade:** S (Small)
**Sprint:** SAB-P2
**Owner:** @dev + @po
**Screenshots:** `ux-audit/28-planos.png`, `ux-audit/29-planos-bottom.png`

---

## Problema

### P2-03: Badge "BETA" no produto pago
Card de pricing mostra "SmartLic Pro **BETA**" com badge azul. Cobrar R$397/mês por um produto em "BETA" gera desconfiança.

### P2-04: Heading questionável
Título "Escolha Seu Nível de Compromisso" — "Compromisso" tem conotação negativa em português ("obrigação").

---

## Critérios de Aceite

### Badge BETA (P2-03)

- [ ] **AC1:** Opção A: Remover badge "BETA" completamente. Opção B: Substituir por "Early Adopter" com benefício (preço lock-in). **Decisão do PO necessária.**
- [ ] **AC2:** Se opção B: adicionar tooltip "Preço garantido para early adopters. Sem reajuste por 12 meses."
- [ ] **AC3:** Verificar se há outros lugares no app com badge "BETA" (grep global)

### Heading (P2-04)

- [ ] **AC4:** Alterar "Escolha Seu Nível de Compromisso" para copy aprovada pelo PO. Sugestões:
  - "Escolha o melhor para sua empresa"
  - "Invista na inteligência competitiva"
  - "Comece a vencer licitações"

---

## Arquivos Prováveis

- `frontend/app/planos/page.tsx` — página de planos/pricing
- `frontend/components/PlanCard.tsx` — card de plano

## Notas

- Decisão de copy precisa de aprovação do PO/Marketing antes de implementar.
- Não alterar preços ou estrutura de planos — apenas visual e copy.
