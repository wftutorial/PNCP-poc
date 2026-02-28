# SAB-003: Dark mode ilegível na área logada

**Origem:** UX Premium Audit P0-03
**Prioridade:** P0 — BLOQUEADOR
**Complexidade:** L (Large)
**Sprint:** SAB-P0 (imediato)
**Owner:** @dev + @ux-design-expert
**Screenshots:** `ux-audit/30-dark-mode.png`, `ux-audit/31-mobile-busca.png`

---

## Problema

O dark mode está ilegível em múltiplas páginas da área logada:

| Área | Problema |
|------|----------|
| Sidebar | Texto legível mas sem separação visual entre itens |
| Logo | "SmartLic.tech" cortada/parcialmente visível no canto superior esquerdo |
| Footer | Links e texto com contraste insuficiente |
| Busca | Campos de formulário e dropdown com bordas quase invisíveis |
| Pipeline/Histórico/Alertas | Texto com Unicode (P0-02) + dark mode = completamente ilegível |

**Impacto:** 40-60% dos usuários de SaaS B2B preferem dark mode. Eles não conseguem usar o produto.

---

## Critérios de Aceite

### Audit de Variáveis CSS

- [ ] **AC1:** Mapear TODAS as variáveis CSS do dark mode (`dark:` classes no Tailwind + CSS custom properties)
- [ ] **AC2:** Testar contraste WCAG AA em cada combinação text/background: mínimo 4.5:1 para texto normal, 3:1 para texto grande e elementos UI

### Fixes por Área

- [ ] **AC3:** Sidebar — adicionar `border-b` ou `divide-y` entre itens no dark mode. Garantir separação visual clara.
- [ ] **AC4:** Logo — garantir que "SmartLic.tech" é 100% visível no dark mode (ajustar cor ou usar versão white do logo)
- [ ] **AC5:** Footer — ajustar cor dos links para contraste mínimo 4.5:1 contra background dark (sugestão: `text-gray-400` → `text-gray-300`)
- [ ] **AC6:** Busca — bordas dos inputs/selects/dropdowns visíveis no dark mode (`dark:border-gray-600` mínimo)
- [ ] **AC7:** Cards de resultado — background, texto e badges legíveis no dark mode
- [ ] **AC8:** Pipeline columns — headers e cards com contraste adequado
- [ ] **AC9:** Histórico cards — timestamps, valores e labels legíveis

### Validação

- [ ] **AC10:** Capturar screenshots de TODAS as 7 páginas principais em dark mode após fix (Buscar, Dashboard, Pipeline, Histórico, Alertas, Conta, Planos)
- [ ] **AC11:** Nenhum texto com ratio de contraste < 4.5:1 em dark mode
- [ ] **AC12:** Mobile 375px dark mode — verificar que bottom nav e cards são legíveis

---

## Arquivos Prováveis

- `frontend/app/globals.css` ou `tailwind.config.ts` — variáveis de tema dark
- `frontend/components/Sidebar.tsx` — separação de itens
- `frontend/components/Footer.tsx` — contraste de links
- Todos os componentes de `/buscar`, `/pipeline`, `/historico`

## Dependência

- SAB-002 (P0-02) — Unicode fix deve ser aplicado ANTES do dark mode audit, pois textos ilegíveis mascaram problemas de contraste

## Notas

- Usar ferramenta de contraste (ex: WebAIM Contrast Checker) para validar ratios.
- Considerar usar `@media (prefers-color-scheme: dark)` como base e permitir toggle manual.
