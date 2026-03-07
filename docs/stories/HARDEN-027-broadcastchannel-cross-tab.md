# HARDEN-027: BroadcastChannel para Sync Cross-Tab

**Severidade:** BAIXA
**Esforço:** 15 min
**Quick Win:** Nao
**Origem:** Conselho CTO — Auditoria de Fragilidades (2026-03-06)

## Contexto

Se usuário abre search em duas tabs, ambas fazem POST /buscar independentemente. Não há sincronização de estado entre tabs — possível confusão de resultados.

## Critérios de Aceitação

- [ ] AC1: `BroadcastChannel('smartlic-search')` para comunicação cross-tab
- [ ] AC2: Evento `search_complete` notifica outras tabs
- [ ] AC3: Tab inativa pode atualizar resultados sem re-fetch
- [ ] AC4: Graceful degradation se BroadcastChannel não suportado
- [ ] AC5: Teste unitário

## Arquivos Afetados

- `frontend/hooks/useBroadcastChannel.ts` — novo hook
- `frontend/app/buscar/page.tsx` — integração
