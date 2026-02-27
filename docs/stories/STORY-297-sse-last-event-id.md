# STORY-297: SSE Last-Event-ID Resumption

**Sprint:** 1 — Make It Reliable
**Size:** M (4-8h)
**Root Cause:** Track B (UX Audit)
**Depends on:** STORY-294
**Industry Standard:** [WHATWG — Server-Sent Events Spec](https://html.spec.whatwg.org/multipage/server-sent-events.html#the-last-event-id-header)

## Contexto

SSE connections drop por vários motivos: mobile network switch, laptop sleep, Railway proxy reset (60s idle). Hoje quando SSE desconecta, o frontend perde todo o contexto e não tem como reconectar sem perder eventos.

A spec WHATWG define `Last-Event-ID`: cada evento SSE tem um `id:` field, e quando o browser reconecta, envia `Last-Event-ID` header. O servidor reenvia apenas os eventos após aquele ID.

## Acceptance Criteria

### Backend
- [x] AC1: Cada evento SSE inclui `id:` field (monotonic counter por search_id)
- [x] AC2: Eventos armazenados em Redis list com TTL 10min: `sse_events:{search_id}`
- [x] AC3: Endpoint SSE lê `Last-Event-ID` header e reenvia eventos após esse ID
- [x] AC4: Se `Last-Event-ID` presente e search já completou, envia evento `completed` imediatamente
- [x] AC5: Máximo 1000 eventos por search_id (ring buffer)

### Frontend
- [x] AC6: EventSource reconecta automaticamente (browser nativo)
- [x] AC7: Se reconexão falha 3x, fallback para polling `/v1/search/{id}/status`
- [x] AC8: UI não reseta estado durante reconexão — mantém resultados parciais
- [x] AC9: Indicador visual: "Reconectando..." durante gap

### Quality
- [x] AC10: Teste: desconexão simulada → reconexão → eventos não perdidos
- [x] AC11: Teste: reconnect após search completo → recebe `completed` imediatamente
- [x] AC12: Testes existentes passando

## Technical Notes

```
SSE Event Format (com id):
  id: 42
  event: partial_results
  data: {"source": "pncp", "uf": "SP", "items": [...]}

Reconnect Request:
  GET /buscar-progress/{id}
  Last-Event-ID: 42

Server Response:
  → replay events 43, 44, 45, ...
```

## Files to Change

- `backend/progress.py` — add event ID tracking + Redis storage
- `backend/routes/search.py` — read Last-Event-ID header, replay events
- `frontend/hooks/useSearch.ts` — handle reconnection state
- `frontend/app/buscar/page.tsx` — reconnection UI indicator

## Files Changed

### Backend
- `backend/progress.py` — event ID tracking (`_event_counter`, `_event_history`), `_emit_event()` common dispatch, `_store_replay_event()` Redis list, `get_replay_events()`, `is_search_terminal()`
- `backend/routes/search.py` — `Last-Event-ID` header/query param reading, replay logic, `id:` prefix on all SSE events
- `backend/tests/test_sse_last_event_id.py` — 53 tests covering all ACs
- `backend/tests/test_progress.py` — Updated expire assertions for replay list
- `backend/tests/test_progress_streams.py` — Updated expire assertions for replay list
- `backend/tests/test_state_externalization.py` — Updated expire assertions for replay list

### Frontend
- `frontend/hooks/useSearchSSE.ts` — `lastEventIdRef` tracking, `isReconnecting` state, `last_event_id` in retry URL
- `frontend/app/buscar/hooks/useSearch.ts` — Pass through `isReconnecting`
- `frontend/app/api/buscar-progress/route.ts` — Forward `last_event_id` as `Last-Event-ID` header
- `frontend/app/buscar/components/SearchResults.tsx` — "Reconectando..." amber banner
- `frontend/app/buscar/page.tsx` — Pass `isReconnecting` prop
- `frontend/__tests__/sse-last-event-id.test.tsx` — 14 tests covering AC6-AC11

## Definition of Done

- [x] SSE reconnect após 5s disconnect: zero eventos perdidos
- [x] Mobile network switch: busca continua sem restart
- [x] Todos os testes passando
- [ ] PR merged
