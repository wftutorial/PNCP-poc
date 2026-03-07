# HARDEN-012: SSE Client Disconnect Detection via request.is_disconnected()

**Severidade:** ALTA
**Esforço:** 15 min
**Quick Win:** Nao
**Origem:** Conselho CTO — Auditoria de Fragilidades (2026-03-06)

## Contexto

Loop de polling XREAD em `routes/search.py` roda a cada 1s sem verificar se client HTTP ainda está conectado. Consome Redis bandwidth desnecessariamente após client disconnect.

## Critérios de Aceitação

- [x] AC1: `request.is_disconnected()` verificado a cada iteração do event_generator
- [x] AC2: Log debug no disconnect detectado
- [x] AC3: `release_sse_connection()` chamado no disconnect
- [x] AC4: Metric `smartlic_sse_disconnects_total` incrementada
- [x] AC5: Teste valida cleanup no disconnect

## Arquivos Afetados

- `backend/routes/search.py` — event_generator() — 4 disconnect checks (wait, Redis, Supabase, in-memory)
- `backend/metrics.py` — SSE_DISCONNECTS_TOTAL counter
- `backend/tests/test_harden012_sse_disconnect.py` — 5 tests (wait, Redis, in-memory, Supabase, negative)
