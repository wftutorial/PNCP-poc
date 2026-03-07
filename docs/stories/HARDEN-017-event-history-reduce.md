# HARDEN-017: Event History Reduzir + Excluir partial_data

**Severidade:** MEDIA
**Esforço:** 10 min
**Quick Win:** Sim
**Origem:** Conselho CTO — Auditoria de Fragilidades (2026-03-06)

## Contexto

`_event_history` em `progress.py:96` acumula até 1000 events × ~10KB/event (detail JSON com licitações) = 10MB por search tracker ativo.

## Critérios de Aceitação

- [ ] AC1: `_REPLAY_MAX_EVENTS` reduzido de 1000 → 200
- [ ] AC2: Events `partial_data` excluídos do history (são os maiores, 10KB+)
- [ ] AC3: Events `partial_data` ainda emitidos via queue (SSE real-time funciona)
- [ ] AC4: Teste valida que partial_data não aparece no replay
- [ ] AC5: Zero regressions nos testes de replay (STORY-297)

## Arquivos Afetados

- `backend/progress.py` — _emit_event(), _REPLAY_MAX_EVENTS
- `backend/tests/test_progress.py`
