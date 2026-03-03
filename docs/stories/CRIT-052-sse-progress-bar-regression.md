# CRIT-052: SSE Progress Bar — Barra de Progresso Retrocede e Reconexão Silenciosa

**Status:** 🔴 Pendente
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

- [ ] AC1: Frontend mantém high-water mark do progresso (nunca mostra valor menor que o anterior)
- [ ] AC2: Se SSE reconectar, barra mostra "Reconectando..." ao invés de voltar para 0%
- [ ] AC3: Progress events com `progress=-1` são ignorados pelo cálculo da barra
- [ ] AC4: Se busca completar durante reconexão, resultado é exibido normalmente
- [ ] AC5: Testes E2E validam progresso monotônico (nunca decresce)

## Arquivos Afetados

- `frontend/app/buscar/page.tsx` — SSE handling, progress state
- `frontend/app/api/buscar-progress/[searchId]/route.ts` — SSE proxy
- `backend/progress.py` — progress event generation
