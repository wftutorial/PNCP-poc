# SAB-006: Landing page excessivamente longa e repetitiva

**Origem:** UX Premium Audit P1-03
**Prioridade:** P1 — Alto
**Complexidade:** M (Medium)
**Sprint:** SAB-P1
**Owner:** @dev + @ux-design-expert
**Screenshots:** `ux-audit/01-landing-hero.png` → `ux-audit/09-landing-footer.png`

---

## Problema

A landing page tem múltiplos problemas de extensão e repetição:

| Problema | Detalhe |
|----------|---------|
| Seção duplicada | "Como Funciona" aparece **duas vezes** (screenshots 03 e 08) |
| Dados repetidos | "87% filtrados" e "27 UFs" aparecem em seções diferentes |
| Whitespace excessivo | Seção de dor ("Sua empresa perde R$..") muito longa |
| Scroll total | ~8x viewport height (benchmark premium: 3-5x max) |
| CTA enterrado | Botão de signup requer scroll excessivo para ser encontrado |

**Impacto:** Taxa de bounce alta. Usuário não encontra o CTA de signup sem scroll excessivo.

---

## Critérios de Aceite

### Deduplicação

- [ ] **AC1:** Remover a segunda instância de "Como Funciona" (manter apenas uma)
- [ ] **AC2:** Consolidar menções a "87% filtrados" e "27 UFs" em uma única seção de stats

### Condensação

- [ ] **AC3:** Reduzir scroll total para máximo 5x viewport height (de ~8x atual)
- [ ] **AC4:** Seção de dor ("Sua empresa perde R$...") — reduzir whitespace e compactar copy
- [ ] **AC5:** CTA principal ("Começar Grátis") visível above-the-fold ou no máximo 1 scroll

### Stats Counter

- [ ] **AC6:** Stats counter inicia com `opacity: 0` → fade-in com animação de contagem (fix FOUC de "0%") — absorve P3-01

### Validação

- [ ] **AC7:** Lighthouse mobile performance score ≥ 80 após mudanças
- [ ] **AC8:** Teste visual: gravar scroll da página inteira e confirmar que fluxo é: Hero → Problema → Solução → Como Funciona → Stats → CTA → Footer

---

## Arquivos Prováveis

- `frontend/app/page.tsx` — landing page completa
- `frontend/components/` — seções da landing (Hero, HowItWorks, Stats, etc.)

## Notas

- Esta story absorve P3-01 (stats counter FOUC) pois o fix é na mesma seção.
- Não alterar copy de marketing sem aprovação do PO — foco é em estrutura e deduplicação.
