# Story DEBT-202: Frontend Estrutural — Landing RSC + useSearchOrchestration + ViabilityBadge

## Metadados
- **Epic:** EPIC-DEBT-V2
- **Sprint:** 3 (Semana 5-6)
- **Prioridade:** P0-P1
- **Esforco:** 26h
- **Agente:** @dev + @qa + @ux-design-expert
- **Status:** PLANNED

## Descricao

Como equipe de produto, queremos otimizar a landing page para carregamento rapido (LCP < 2.5s), decompor o mega-hook de busca para facilitar manutencao, e tornar o ViabilityBadge acessivel em todos os dispositivos, para que a taxa de conversao melhore, o desenvolvimento da feature central seja mais agil, e usuarios com deficiencia visual possam usar a plataforma.

## Debitos Incluidos

| ID | Debito | Horas | Responsavel |
|----|--------|-------|-------------|
| DEBT-FE-017 | Landing page com 13 child components "use client" — hydration excessiva | 10h | @dev + @ux-design-expert |
| DEBT-FE-001 | `useSearchOrchestration` mega-hook (618 LOC) — 12+ sub-hooks | 12h | @dev + @qa |
| DEBT-FE-002 | ViabilityBadge usa `title` para dados criticos — inacessivel em mobile/touch | 4h | @dev + @ux-design-expert |

## Criterios de Aceite

### Landing Page RSC Islands (10h)
- [ ] 10 dos 13 componentes "use client" convertidos para React Server Components
- [ ] Apenas componentes genuinamente interativos (formulario, animacoes on-scroll, contadores) permanecem client-side
- [ ] LCP mobile 4G < 2.5s (Lighthouse CI)
- [ ] TTI mobile 4G < 3.5s
- [ ] Nenhuma funcionalidade da landing page quebrada (CTAs, navegacao, formularios)
- [ ] Visual regression test aprovado (screenshot comparison antes/depois)

### useSearchOrchestration Decomposition (12h)
- [ ] Hook decomposto em 4+ sub-hooks:
  - `useSearchState` — gerenciamento de estado da busca
  - `useSearchSSE` — conexao SSE e progresso
  - `useSearchResults` — processamento e cache de resultados
  - `useSearchFilters` — logica de filtros e parametros
- [ ] Hook principal `useSearchOrchestration` reimplementado como composicao dos sub-hooks
- [ ] Nenhum sub-hook excede 200 LOC
- [ ] Snapshot test de `searchResultsProps` identico antes/depois da decomposicao
- [ ] E2E `search-flow.spec.ts` passa 100%

### ViabilityBadge Acessivel (4h)
- [ ] Breakdown de viabilidade acessivel via Radix Tooltip (desktop hover) + tap-to-expand (mobile)
- [ ] Atributo `title` removido — dados criticos em elementos acessiveis
- [ ] axe-core zero violacoes no componente ViabilityBadge
- [ ] Touch device emulation: breakdown visivel com tap em mobile (iOS Safari, Chrome Android)
- [ ] Conformidade WCAG 2.1 AA para o componente

## Testes Requeridos

- [ ] Lighthouse CI em landing page: LCP < 2.5s, TTI < 3.5s (mobile 4G throttle)
- [ ] Visual regression: screenshot comparison landing page antes/depois
- [ ] Snapshot test de `searchResultsProps` — props identicos pre/pos decomposicao
- [ ] `search-flow.spec.ts` E2E 100% passando
- [ ] axe-core em ViabilityBadge + touch device emulation
- [ ] `npm test` — suite completa frontend (2681+ testes)
- [ ] Testar em branch separada antes de merge

## Notas Tecnicas

- **Landing RSC:** Consultar docs do Next.js 16 sobre RSC boundaries antes de converter. Componentes com `useState`, `useEffect`, event handlers devem permanecer client.
- **useSearchOrchestration:** O hook e o coracao da feature principal (`/buscar`). Decomposicao deve preservar exatamente o mesmo comportamento externo. Usar snapshot tests como safety net.
- **ViabilityBadge:** Radix UI Tooltip ja pode estar disponivel no projeto. Verificar `package.json` antes de adicionar dependencia.
- **Branch separada:** Devido ao risco medio de hydration breaks, trabalhar em feature branch com CI verde obrigatorio antes de merge.

## Dependencias

- Nenhuma dependencia direta de outras stories
- Recomendado: DEBT-200 (Sprint 1) completa para base limpa
