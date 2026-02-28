# STORY-329: Emitir eventos de progresso granular durante a fase de filtragem

**Prioridade:** P1 (UX — barra congelada)
**Complexidade:** M (Medium)
**Sprint:** CRIT-SEARCH

## Problema

A barra de progresso fica **congelada em 70%** por até **197+ segundos** durante a fase de filtragem. O `stage_filter()` emite apenas 2 eventos: início (60%) e fim (70%). Com 1803 items passando por keyword matching + LLM zero-match, essa fase pode ser extremamente longa sem feedback visual.

**Evidência:** Screenshot mostra "Aplicando filtros em 1803 licitacoes..." a 70% com 197s decorridos.

## Causa Raiz

`search_pipeline.py:stage_filter()` executa `aplicar_todos_filtros()` como uma única chamada sem callback de progresso. O LLM zero-match (GPT-4.1-nano batched) é o trecho mais lento e não emite progresso intermediário. O frontend vê silêncio de 30-120s+ entre "filtering started" e "complete".

## Critérios de Aceite

- [x] AC1: `aplicar_todos_filtros()` em `filter.py` aceita callback opcional `on_progress(processed: int, total: int)` chamado a cada 50 items ou 5% do total
- [x] AC2: `stage_filter()` conecta callback ao tracker: `emit("filtering", progress, f"Filtrando: {processed}/{total}")` com progress interpolando de 60→70
- [x] AC3: O LLM zero-match em batch emite progresso: "Classificação IA: {n}/{total} sem keywords" com progress 65-70
- [x] AC4: Se filtragem > 30s, emitir flag `is_long_running=true` → frontend mostra "Volume grande, pode levar até 2 min"
- [x] AC5: Se LLM timeout (skip after 90s per STAB-003), emitir evento `llm_skipped` com motivo
- [x] AC6: Frontend `EnhancedLoadingProgress` anima suavemente entre micro-steps (60→62→64→66→68→70)
- [x] AC7: Teste backend com mock callback verificando chamadas a cada 50 items
- [x] AC8: Teste frontend simulando sequência 60→62→...→70 verificando animação

## Arquivos Afetados

- `backend/filter.py` — Added `on_progress` callback to `aplicar_todos_filtros()`, fires every 50 items/5% during keyword loop + per LLM zero-match completion
- `backend/search_pipeline.py` — `stage_filter()` creates thread-safe callback, runs filter via `asyncio.to_thread()` for real-time SSE, emits `is_long_running` after 30s, emits `llm_skipped` on STAB-003 timeout
- `frontend/components/EnhancedLoadingProgress.tsx` — Capped `ufBasedProgress` at 60% (was 70%), fixed post-fetch progress to use SSE directly, added `is_long_running` banner
- `backend/tests/test_filter_progress_callback.py` (novo) — 9 tests: callback intervals, small/tiny batches, LLM phase, sequential phases
- `frontend/__tests__/story329-filter-progress.test.tsx` (novo) — 11 tests: micro-step animation, long-running message, LLM skipped, UF progress cap
