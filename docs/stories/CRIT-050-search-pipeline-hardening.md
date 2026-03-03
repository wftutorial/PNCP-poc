# CRIT-050: Search Pipeline Hardening — Eliminar Fragilidades Estruturais

**Status:** 🟡 Em Progresso
**Prioridade:** P0 — Bloqueante (funcionalidade core)
**Sprint:** Atual
**Criado:** 2026-03-03

## Contexto

A busca é a funcionalidade core do SmartLic. Commits recentes introduziram fragilidades não detectadas pelos testes (ctx.search_id inexistente, BuscaResponse parcial sem campos obrigatórios). A causa raiz é falta de contratos entre estágios do pipeline e ausência de validação em caminhos de erro.

## Correções Já Aplicadas (commit `e6026a3`)

- [x] AC1: `ctx.search_id` → `ctx.request.search_id` em 4 lugares (search_pipeline.py)
- [x] AC2: Partial response handler com todos campos obrigatórios (routes/search.py:1690)
- [x] AC3: Removido log per-item `filter_rejection` (~1760 linhas/busca → 0)

## Itens Pendentes

### Hardening do Pipeline (P0)

- [ ] AC4: Adicionar `setup_logging()` no ARQ worker `_worker_on_startup()` (logs stderr→stdout no Railway)
- [ ] AC5: Criar `arq_log_config` com `ext://sys.stdout` e `--custom-log-dict` em start.sh
- [ ] AC6: Adicionar check de `CACHE_REFRESH_ENABLED` no asyncio `_cache_refresh_loop()` (cron_jobs.py)
- [ ] AC7: `ctx.quota_info.capabilities["allow_excel"]` → `.get("allow_excel", False)` em 3 lugares (search_pipeline.py)
- [ ] AC8: Garantir `ctx.resumo` sempre definido antes de stage_persist (fallback se None)
- [ ] AC9: Extrair helper `get_correlation_id()` para eliminar padrão repetido 10+ vezes

### Validação entre Estágios (P1)

- [ ] AC10: Adicionar `_validate_stage_outputs()` após cada stage no pipeline
- [ ] AC11: Type check: `ctx.filter_stats` sempre dict (nunca None) após Stage 4
- [ ] AC12: Type check: `ctx.data_sources` sempre list (pode ser vazia) após Stage 3

### Logging & Observability (P1)

- [ ] AC13: ARQ cron job `cache_refresh_job` logando como ERROR no Railway (stderr → stdout fix)
- [ ] AC14: `filter_rejection` summary — garantir que `filter_complete` JSON cobre todos reason codes

### Testes de Resiliência (P1)

- [ ] AC15: Teste: Stage 4 crash → partial response retorna resultados com fallback resumo
- [ ] AC16: Teste: ctx.quota_info = None → partial response com defaults (0, 999)
- [ ] AC17: Teste: ctx.resumo = None no stage_persist → fallback automático

## Critérios de Aceite

1. ZERO crashes no pipeline de busca em qualquer cenário de erro
2. Partial results SEMPRE entregues quando há dados filtrados
3. Log volume reduzido ≥90% (sem per-item logs)
4. Worker logs aparecem como INFO (não ERROR) no Railway

## Arquivos Afetados

- `backend/search_pipeline.py`
- `backend/routes/search.py`
- `backend/filter_stats.py`
- `backend/job_queue.py`
- `backend/cron_jobs.py`
- `backend/start.sh`
- `backend/config.py`
