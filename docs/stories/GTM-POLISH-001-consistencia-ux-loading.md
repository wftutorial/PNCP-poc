# GTM-POLISH-001: Consistencia de UX — Loading States Across Pages

## Epic
Root Cause — Polish (EPIC-GTM-ROOT)

## Sprint
Sprint 9: GTM Root Cause — Tier 4

## Prioridade
P3

## Estimativa
6h

## Status
COMPLETED (2026-02-24)

## Descricao

O sistema tem 5 padroes diferentes de auth loading, pipeline sem skeleton, footer escondido ate ter resultados, e mensagens com empty state minimal. Falta consistencia visual entre paginas durante carregamento.

### Situacao Atual

| Pagina | Loading Pattern | Problema |
|--------|----------------|----------|
| `/buscar` | Skeleton cards + progress bar | Bom (referencia) |
| `/dashboard` | Spinner central | Inconsistente com buscar |
| `/pipeline` | Nenhum skeleton | Jump visual quando dados carregam |
| `/historico` | Spinner generico | Sem skeleton |
| `/mensagens` | Texto "Carregando..." | Minimal |
| Auth check | 5 padroes diferentes | Nenhuma consistencia |

### Evidencia da Investigacao (Squad Root Cause 2026-02-23)

| Finding | Agente | Descricao |
|---------|--------|-----------|
| UX-ISSUE-009 | UX | Auth loading: 5 padroes diferentes entre paginas |
| UX-ISSUE-017 | UX | Pipeline sem skeleton — jump visual |
| UX-ISSUE-018 | UX | Footer escondido sem resultados — pagina parece incompleta |
| UX-ISSUE-025 | UX | Mensagens empty state muito minimal |

## Criterios de Aceite

### Auth Loading Padronizado

- [x] AC1: Componente `AuthLoadingScreen.tsx` unico usado em TODAS as paginas protegidas
- [x] AC2: Visual consistente: logo + skeleton da pagina (nao spinner generico)
- [x] AC3: Transicao suave auth loading → pagina carregada (fade, nao flash)

### Skeleton Screens

- [x] AC4: Pipeline: skeleton cards nas colunas do kanban durante loading
- [x] AC5: Historico: skeleton rows na tabela durante loading
- [x] AC6: Dashboard: skeleton cards nos graficos durante loading
- [x] AC7: Mensagens: skeleton rows na lista de conversas

### Footer e Empty States

- [x] AC8: Footer sempre visivel (nao esconder quando sem resultados)
- [x] AC9: Mensagens empty state: icone + "Nenhuma conversa ainda" + acao sugerida
- [x] AC10: Pipeline empty state: "Arraste licitacoes para ca" com visual de dica

## Testes Obrigatorios

```bash
cd frontend && npm test -- --testPathPattern="loading-consistency" --no-coverage
```

- [x] T1: AuthLoadingScreen renderiza com logo + skeleton
- [x] T2: Pipeline mostra skeleton durante loading
- [x] T3: Footer visivel mesmo sem resultados

## Arquivos Afetados

| Arquivo | Tipo de Mudanca |
|---------|----------------|
| `frontend/components/AuthLoadingScreen.tsx` | Criar — loading padronizado |
| `frontend/hooks/useIsMobile.ts` | Criar — hook de deteccao mobile |
| `frontend/app/pipeline/page.tsx` | Modificar — skeleton loading + AuthLoadingScreen |
| `frontend/app/historico/page.tsx` | Modificar — AuthLoadingScreen |
| `frontend/app/dashboard/page.tsx` | Modificar — AuthLoadingScreen |
| `frontend/app/mensagens/page.tsx` | Modificar — skeleton + empty state + AuthLoadingScreen |
| `frontend/app/buscar/page.tsx` | Modificar — footer sempre visivel |
| `frontend/__tests__/polish/loading-consistency.test.tsx` | Criar — 15 testes |
| `frontend/__tests__/dashboard.test.tsx` | Modificar — atualizar expectativa auth loading |
| `frontend/__tests__/pages/HistoricoPage.test.tsx` | Modificar — atualizar expectativa auth loading |
| `frontend/__tests__/gtm-ux-002-error-states.test.tsx` | Modificar — atualizar expectativa empty state |
| `frontend/__tests__/search-first-use.test.tsx` | Modificar — atualizar expectativa footer |

## Dependencias

| Tipo | Story | Motivo |
|------|-------|--------|
| Paralela | GTM-POLISH-002 | Ambas sao polish, independentes |
| Nenhuma bloqueante | — | Pode ser feita apos Tier 1-3 |
