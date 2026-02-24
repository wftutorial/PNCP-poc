# GTM-POLISH-002: Mobile Error States + Pipeline Tabs

## Epic
Root Cause — Polish (EPIC-GTM-ROOT)

## Sprint
Sprint 9: GTM Root Cause — Tier 4

## Prioridade
P3

## Estimativa
8h

## Status
COMPLETED (2026-02-24)

## Descricao

O card de auto-retry nao stacka corretamente em viewport 375px (sobrepoe outros elementos). O pipeline kanban so funciona com scroll horizontal no mobile, sem opcao de tabs/lista. Erro em mobile tende a ser mais frequente (conexoes instaveIS) e a UX nao esta adaptada.

### Situacao Atual

| Componente | Comportamento em 375px | Problema |
|------------|------------------------|----------|
| Auto-retry card | Overflow, sobrepoe | Layout quebrado |
| Pipeline kanban | Scroll horizontal | Pouco intuitivo em mobile |
| Error detail | Texto truncado | Informacao perdida |
| Countdown SVG | Tamanho fixo | Nao adapta |

### Evidencia da Investigacao (Squad Root Cause 2026-02-23)

| Finding | Agente | Descricao |
|---------|--------|-----------|
| UX-ISSUE-027 | UX | Auto-retry card nao stacka em 375px |
| UX-ISSUE-028 | UX | Pipeline kanban horizontal-scroll-only no mobile |

## Criterios de Aceite

### Mobile Error States

- [x] AC1: Auto-retry card responsivo em 375px — nao sobrepoe outros elementos
- [x] AC2: Countdown simplificado em mobile: numero + texto (sem SVG circular)
- [x] AC3: Error detail scrollavel em mobile (nao truncado)
- [x] AC4: Toast notifications posicionadas corretamente em mobile

### Pipeline Mobile

- [x] AC5: Pipeline com tabs no mobile: "Descoberta | Analise | Proposta | Ganhas" (em vez de kanban horizontal)
- [x] AC6: Cada tab mostra lista vertical dos cards daquela coluna
- [x] AC7: Drag-and-drop substituido por botao "Mover para..." em mobile
- [x] AC8: Badge com contagem em cada tab: "Analise (3)"

### Viewport Testing

- [x] AC9: Testado em 375px (iPhone SE), 390px (iPhone 14), 360px (Android common)
- [x] AC10: Nenhum overflow horizontal em nenhuma pagina em 375px

## Testes Obrigatorios

```bash
cd frontend && npm test -- --testPathPattern="mobile-error|pipeline-tabs" --no-coverage
```

- [x] T1: Auto-retry card renderiza sem overflow em 375px
- [x] T2: Pipeline tabs renderizam em mobile viewport
- [x] T3: "Mover para..." funciona como alternativa a drag-and-drop
- [x] T4: Badge de contagem correto em cada tab

## Arquivos Afetados

| Arquivo | Tipo de Mudanca |
|---------|----------------|
| `frontend/app/pipeline/PipelineMobileTabs.tsx` | Criar — tabs mobile com "Mover para..." |
| `frontend/hooks/useIsMobile.ts` | Criar — hook de deteccao mobile |
| `frontend/app/pipeline/page.tsx` | Modificar — isMobile ? tabs : kanban |
| `frontend/app/buscar/components/SearchResults.tsx` | Modificar — retry card responsivo |
| `frontend/app/buscar/components/ErrorDetail.tsx` | Modificar — scrollavel em mobile |
| `frontend/app/layout.tsx` | Modificar — toast position bottom-center |
| `frontend/__tests__/polish/mobile-error.test.tsx` | Criar — 19 testes |
| `frontend/__tests__/polish/pipeline-tabs.test.tsx` | Criar — 36 testes |

## Dependencias

| Tipo | Story | Motivo |
|------|-------|--------|
| Paralela | GTM-POLISH-001 | Ambas sao polish, independentes |
| Nenhuma bloqueante | — | Pode ser feita apos Tier 1-3 |
