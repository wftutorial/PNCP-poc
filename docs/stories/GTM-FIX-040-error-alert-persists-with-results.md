# GTM-FIX-040 — Error Alert Persiste ao Lado de Resultados Válidos

**Status:** Done
**Priority:** P1 — High (UX contraditória destrói confiança)
**Severity:** Frontend — estado de erro não é limpo quando resultados chegam
**Created:** 2026-02-25
**Sprint:** GTM Stabilization
**Relates to:** GTM-STAB-006 (SSE resilience), CRIT-008 (frontend resilience), CRIT-009 (structured error observability)
**Found:** Playwright E2E validation 2026-02-25

---

## Problema

Quando uma busca encontra erro transitório (SSE initial failure, timeout no primeiro request) e o auto-retry resolve com sucesso, o **error alert permanece visível** ao lado dos resultados válidos.

### Reprodução (100% reproduzível):

1. Ir para `/buscar`
2. Selecionar setor + UFs
3. Clicar "Buscar"
4. Observar: error alert aparece ("Não foi possível obter os resultados")
5. Auto-retry dispara e retorna resultados
6. **BUG:** Error alert permanece visível acima dos resultados

### O que o usuário vê:

```
┌─────────────────────────────────────────────┐
│ ⚠️ Não foi possível obter os resultados.    │
│    Tente novamente.              [Tentar]   │
├─────────────────────────────────────────────┤
│ 10 oportunidades selecionadas de 132        │
│ analisadas                                  │
│                                             │
│ 📋 AQUISIÇÃO DE MATERIAIS PARA INFRA...     │
│ 📋 Aquisição de material de consumo...      │
│ ...                                         │
└─────────────────────────────────────────────┘
```

### Impacto:

- Usuário vê erro + resultados ao mesmo tempo → confusão
- "O sistema falhou ou funcionou?" → perda de credibilidade
- Botão "Tentar novamente" convida a clicar, potencialmente descartando resultados válidos

---

## Acceptance Criteria

### AC1: Limpar error state quando resultados chegam
- [x] Em `useSearch.ts`: quando `setResultados()` é chamado com dados válidos (length > 0), limpar `error` state
- [x] Se `error` e `resultados` coexistem, `resultados` tem prioridade (error é descartado)
- [x] Transição: error alert faz fade-out quando resultados aparecem

### AC2: Limpar error state quando SSE reconecta com sucesso
- [x] Quando SSE emite primeiro evento de dados após reconexão, limpar error state
- [x] `useSearchSSE.ts`: callback `onReconnectSuccess` → clear error in parent

### AC3: Error alert não deve aparecer durante auto-retry
- [x] Se auto-retry está em andamento (`retryCountdown > 0`), suprimir error alert
- [x] Mostrar apenas o countdown de retry, não o erro completo
- [x] Se retry falha e não há mais tentativas, aí sim mostrar error alert

### AC4: Testes
- [x] Frontend: test que simula error → retry success → error alert desaparece
- [x] Frontend: test que simula error durante countdown → alert suprimido
- [x] Frontend: test que resultados válidos limpam error state

---

## Arquivos Envolvidos

| Arquivo | Ação |
|---------|------|
| `frontend/app/buscar/hooks/useSearch.ts` | AC1+AC3: limpar error em setResultados, suprimir durante retry |
| `frontend/app/buscar/hooks/useSearchSSE.ts` | AC2: callback onReconnectSuccess |
| `frontend/app/buscar/page.tsx` | AC1: lógica de prioridade resultados > error |
| `frontend/app/buscar/components/SearchResults.tsx` | AC3: condição de render do error alert |

---

## Decisões Técnicas

- **Resultados > Error** — Se temos dados, mostramos dados. Erro transitório que se resolveu não deve poluir a UI.
- **Fade-out** — Transição suave evita "piscar" de UI. O error some graciosamente.
- **Suppress durante retry** — O countdown já comunica que o sistema está tentando. Error alert é redundante.

## Estimativa
- **Esforço:** 2-3h
- **Risco:** Baixo (lógica de estado no frontend, não toca backend)
- **Squad:** @dev (frontend state) + @qa (testes)
