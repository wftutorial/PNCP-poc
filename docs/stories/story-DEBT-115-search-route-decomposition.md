# DEBT-115: Search Route Decomposition

**Prioridade:** GTM-RISK (30 dias)
**Estimativa:** 16h
**Fonte:** Brownfield Discovery — @architect (ARCH-001), @qa regression risk HIGH
**Score Impact:** Maint 6→8

## Contexto
`routes/search.py` é o maior arquivo do backend com 2177 LOC. Contém SSE generator, state machine wiring, retry logic, e search orchestration misturados. Dificulta hotfixes e code review. @qa alerta: adicionar contract tests ANTES de decompor.

## Acceptance Criteria

### Fase 1: Contract Tests (4h)
- [ ] AC1: Snapshot tests para response schemas de POST /buscar (JSON response)
- [ ] AC2: Snapshot tests para SSE event format (/buscar-progress/{id})
- [ ] AC3: Contract test para retry endpoint (POST /v1/search/{id}/retry)
- [ ] AC4: Contract test para status endpoint (GET /v1/search/{id}/status)

### Fase 2: Decomposição (12h)
- [ ] AC5: Extrair SSE generator para `routes/search_sse.py` (~400 LOC)
- [ ] AC6: Extrair state machine wiring para `routes/search_state.py` (~300 LOC)
- [ ] AC7: Extrair retry/status endpoints para `routes/search_status.py` (~200 LOC)
- [ ] AC8: `routes/search.py` reduzido para <800 LOC (orchestration + POST /buscar)
- [ ] AC9: Todos os 5131+ backend tests passam, 0 regressions
- [ ] AC10: Todos os contract tests da Fase 1 passam
- [ ] AC11: SSE heartbeat + progress tracking funciona end-to-end (teste manual)

## File List
- [ ] `backend/routes/search.py` (EDIT — reduzir de 2177 para <800 LOC)
- [ ] `backend/routes/search_sse.py` (NEW)
- [ ] `backend/routes/search_state.py` (NEW)
- [ ] `backend/routes/search_status.py` (NEW)
- [ ] `backend/tests/test_search_contracts.py` (NEW)
