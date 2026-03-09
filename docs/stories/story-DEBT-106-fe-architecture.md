# Story DEBT-106: Frontend Architecture — Buscar Decomposition & Component Consolidation

## Metadata
- **Story ID:** DEBT-106
- **Epic:** EPIC-DEBT
- **Batch:** C (Optimization)
- **Sprint:** 4-6 (Semanas 7-10)
- **Estimativa:** 46h
- **Prioridade:** P2
- **Agent:** @dev + @ux-design-expert

## Descricao

Como desenvolvedor frontend, quero decompor a pagina monolitica de busca (983 LOC) em hooks e componentes menores, consolidar os dois diretorios de componentes com convencao documentada, e resolver pendencias de refatoracao avancada (DEBT-016 outstanding), para que a codebase seja maintainable e novas funcionalidades possam ser adicionadas com confianca.

## Debt Items Cobertos

| ID | Debito | Severidade | Horas |
|----|--------|:---:|:---:|
| FE-001 | `/buscar/page.tsx` monolitico 983 LOC — extrair `useSearchOrchestration` hook + `BuscarModals` | HIGH | 18h |
| FE-006 | Dual component directories — falta convencao documentada + 5-10 file moves | HIGH | 7h |
| FE-002 | `next/dynamic` parcialmente implementado; gaps: Shepherd.js, framer-motion (~95KB) | MEDIUM | 5h |
| SYS-009 | Frontend advanced refactoring — 8 items outstanding (DEBT-016) | HIGH | 16h |

## Acceptance Criteria

- [ ] AC1: `useSearchOrchestration` hook extraido de buscar/page.tsx — contém state machine, SSE, polling
- [ ] AC2: `BuscarModals` componente extraido — contém todos os modals da pagina de busca
- [ ] AC3: `buscar/page.tsx` reduzido para <300 LOC (orquestrador puro)
- [ ] AC4: Convencao de diretorios documentada: `components/` = shared, `app/X/components/` = page-specific
- [ ] AC5: 5-10 componentes movidos para diretorio correto conforme convencao
- [ ] AC6: ESLint import restriction rule para enforce de convencao
- [ ] AC7: Shepherd.js lazy loaded via next/dynamic
- [ ] AC8: framer-motion restante lazy loaded (95KB savings)
- [ ] AC9: Todos os 8 items de DEBT-016 outstanding resolvidos ou documentados como deferred
- [ ] AC10: Full E2E search flow pass (search-flow.spec.ts) antes E depois
- [ ] AC11: Bundle size equal or smaller que baseline

## Testes Requeridos

- **FE-001:** Full E2E search flow (`search-flow.spec.ts`); todos 35 sub-componentes renderizam; `npm test` 0 failures
- **FE-006:** ESLint rule passa em CI; nenhum import quebrado apos moves
- **FE-002:** `npm run build` — chunk sizes menores que baseline
- **SYS-009:** Tests especificos por item de DEBT-016
- Bundle size comparison: antes vs depois

## Notas Tecnicas

- **FE-001 (Buscar Decomposition):**
  - Extrair incrementalmente: 1 hook per PR
  - Sequencia: useSearchOrchestration -> BuscarModals -> BuscarFilters -> BuscarResults
  - Manter backward compat dos exports
  - FE-012 (eslint-disable exhaustive-deps) sera naturalmente resolvido pela extracao

- **FE-006 (Component Directory):**
  - Documentar convencao ANTES de mover arquivos
  - `components/` = shared across pages (Button, Input, Badge, etc.)
  - `app/buscar/components/` = search-specific (SearchForm, FilterPanel, etc.)
  - Atualizar imports com find-and-replace + verificar build

- **FE-002 (Dynamic Imports):**
  - Shepherd.js: `dynamic(() => import('shepherd.js'), { ssr: false })`
  - framer-motion: wrap components que usam AnimatePresence com dynamic
  - Cuidado: framer-motion com SSR requer handling especial

- **SYS-009:** Verificar `DEBT-016` story para lista de 8 items outstanding

## Dependencias

- **Depende de:** Nenhuma (mas beneficia de DEBT-105 error boundaries ja estar em place)
- **Bloqueia:** DEBT-111 (FE-001 enables FE-012 exhaustive-deps fix, FE-016 footer dedup)

## Definition of Done

- [ ] buscar/page.tsx < 300 LOC
- [ ] Convencao de componentes documentada
- [ ] ESLint import rule em CI
- [ ] Dynamic imports para Shepherd + framer-motion
- [ ] E2E search flow passing
- [ ] Bundle size <= baseline
- [ ] Code review aprovado
- [ ] Documentacao atualizada
