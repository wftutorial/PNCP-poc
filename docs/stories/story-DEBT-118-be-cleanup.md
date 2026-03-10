# DEBT-118: Backend Cleanup — Re-exports, Config, Dead Files, Filter Facade

**Prioridade:** POST-GTM
**Estimativa:** 22h
**Fonte:** Brownfield Discovery — @architect (ARCH-002, ARCH-003, ARCH-004, SYS-030)
**Score Impact:** Maint 8→9

## Contexto
4 backend items de manutenibilidade: search_pipeline.py tem 17 noqa:F401 re-exports para backward compat de testes, pncp_client.py lê 14 env vars diretamente em vez de usar config/, 2 arquivos .bak mortos no repo, e filter.py facade com 2141 LOC.

## Acceptance Criteria

### Dead Files (0.5h)
- [ ] AC1: Deletar config.py.bak
- [ ] AC2: Deletar config_legacy.py.bak

### Config Migration (2h)
- [ ] AC3: Mover 14 os.environ.get() de pncp_client.py para config/pncp.py
- [ ] AC4: pncp_client.py importa todas configurações de config/pncp.py
- [ ] AC5: Testes existentes de pncp_client passam sem alteração (ou com mock atualizado)

### Re-export Cleanup (4h)
- [ ] AC6: Identificar todos os 17 noqa:F401 em search_pipeline.py
- [ ] AC7: Atualizar tests para patchar módulos fonte (não via search_pipeline)
- [ ] AC8: Remover re-exports desnecessários de search_pipeline.py
- [ ] AC9: Todos os 5131+ backend tests passam

### Filter Facade (16h) — pode ser story separada
- [ ] AC10: Documentar responsabilidade de cada filter_*.py sub-módulo
- [ ] AC11: Mover lógica restante de filter.py para sub-módulos apropriados
- [ ] AC12: filter.py reduzido para <500 LOC (puro orchestration/delegation)
- [ ] AC13: Testes de filtro passam sem regressão

## File List
- [ ] `backend/config.py.bak` (DELETE)
- [ ] `backend/config_legacy.py.bak` (DELETE)
- [ ] `backend/config/pncp.py` (EDIT — add env vars)
- [ ] `backend/pncp_client.py` (EDIT — import from config)
- [ ] `backend/search_pipeline.py` (EDIT — remove re-exports)
- [ ] `backend/filter.py` (EDIT — reduce to orchestration)
- [ ] Various test files (EDIT — update patches)
