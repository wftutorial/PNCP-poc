# CRIT-052: SSE Progress Bar — Barra de Progresso Retrocede e Reconexão Silenciosa

**Status:** 🟢 Concluído
**Prioridade:** P1 — Importante (UX core)
**Sprint:** Próximo
**Criado:** 2026-03-03

## Contexto

A barra de progresso da busca retrocede repetidamente sem gerar erro visível ao usuário.
Quando o SSE reconecta (após timeout ou erro de rede), o progresso reinicia do zero
causando a impressão de que a busca "voltou" e confundindo o usuário.

### Sintomas

1. Barra de progresso vai de 60% para 0% e recomeça
2. Nenhum erro visível ao usuário
3. Busca pode completar mas com UX degradada

## Root Cause Analysis

1. **SSE proxy timeout**: Frontend proxy tem timeout de 115s, Railway ~120s
2. **Reconexão sem estado**: Nova conexão SSE recebe progresso do zero
3. **Progress events com valor -1**: UF status events usam `progress=-1` que frontend pode interpretar como 0%

## Acceptance Criteria

- [x] AC1: Frontend mantém high-water mark do progresso (nunca mostra valor menor que o anterior)
- [x] AC2: Se SSE reconectar, barra mostra "Reconectando..." ao invés de voltar para 0%
- [x] AC3: Progress events com `progress=-1` são ignorados pelo cálculo da barra
- [x] AC4: Se busca completar durante reconexão, resultado é exibido normalmente
- [x] AC5: Testes E2E validam progresso monotônico (nunca decresce)

## Arquivos Modificados

- `frontend/hooks/useSearchSSE.ts` — AC1: progressHighWaterRef (monotonic progress), AC3: metadata event filtering
- `frontend/components/EnhancedLoadingProgress.tsx` — AC2: isReconnecting prop + "Reconectando..." indicator
- `frontend/app/buscar/components/SearchResults.tsx` — AC2: pass isReconnecting to EnhancedLoadingProgress
- `frontend/__tests__/hooks/crit-052-sse-progress-regression.test.tsx` — AC5: 16 tests (high-water mark, reconnection, metadata filtering, monotonic)
- `frontend/__tests__/components/crit-052-reconnecting-indicator.test.tsx` — AC5: 6 tests (reconnecting UI indicator)
