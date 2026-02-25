# GTM-STAB-009 — Modelo de Busca Async (POST Retorna Imediato, Resultados via SSE/Polling)

**Status:** Code Complete — Backend (needs frontend migration AC5 + prod validation)
**Priority:** P0 — Reclassified (80% pre-existing, solution to root cause)
**Severity:** Architecture — elimina dependência de request longa
**Created:** 2026-02-24
**Sprint:** GTM Stabilization (pós-P0/P1)
**Relates to:** GTM-STAB-003 (timeout chain), GTM-STAB-004 (partial results), GTM-RESILIENCE-F01 (ARQ jobs)

---

## Problema

O modelo atual é **síncrono**: `POST /buscar` bloqueia até o pipeline completar (30-120s+). Isso é fundamentalmente incompatível com:

- Railway proxy timeout (120s)
- Gunicorn worker timeout
- Browser connection limits
- Mobile network instability
- Escalabilidade (1 worker = 1 busca simultânea)

### Modelo atual:
```
Client → POST /buscar → [30-120s bloqueado] → JSON response
         GET /buscar-progress/{id} → SSE (progress only, no results)
```

### Modelo proposto:
```
Client → POST /buscar → 202 Accepted {search_id, status_url} (< 1s)
         GET /buscar-progress/{id} → SSE (progress + partial results)
         GET /v1/search/{id}/results → Polling (final results when ready)
```

---

## Acceptance Criteria

### AC1: POST /buscar retorna 202 Accepted imediatamente
- [x] POST /buscar: validates, creates search_id, enqueues via ARQ ✅ (routes/search.py:717-815)
- [x] Response: search_id, status, status_url, progress_url, estimated_duration_s ✅ (lines 801-815)
- [x] HTTP 202 when SEARCH_ASYNC_ENABLED=true ✅
- [x] `estimated_duration_s = min(15 + num_ufs * 8, 120)` ✅

### AC2: Pipeline como background job
- [x] `search_job()` in job_queue.py (lines 418-522) ✅
- [x] Executes full pipeline: `executar_busca_completa()` ✅ (line 469)
- [x] Progress via SSE tracker + `emit_search_complete()` ✅ (line 488)
- [x] Result persisted: `persist_job_result()` ✅ (line 482)
- [x] Fallback: asyncio.create_task when ARQ unavailable ✅

### AC3: GET /v1/search/{id}/status — polling endpoint
- [x] Endpoint exists and returns status ✅ (routes/search.py)
- [ ] Retorna status atual da busca:
  ```json
  {
    "search_id": "2328ffbe-...",
    "status": "processing|completed|failed|partial",
    "progress_pct": 70,
    "elapsed_s": 45,
    "ufs_completed": ["SP", "ES"],
    "ufs_pending": ["MG", "RJ"],
    "results_count": 28,
    "results_url": "/v1/search/2328ffbe-.../results"
  }
  ```
- [ ] Quando status=completed: `results_url` contém resultado final
- [ ] Endpoint leve (<50ms) — lê de Redis/Supabase, não do pipeline

### AC4: GET /v1/search/{id}/results — resultado final
- [x] Returns BuscaResponse when ready (200) ✅ (routes/search.py:444-478)
- [x] Se não pronto: 202 with status ✅ (line 466)
- [x] Se falhou: 404 when not found/expired ✅
- [ ] Cache-friendly: `Cache-Control: max-age=300` — ⚠️ needs verification

### AC5: Frontend migration
- [ ] `useSearch` hook:
  1. POST /buscar → recebe search_id + 202
  2. Conecta SSE /buscar-progress/{id} (progress + partial)
  3. Quando SSE `complete`: GET /v1/search/{id}/results
  4. Fallback: se SSE falha, polling /v1/search/{id}/status a cada 5s
- [ ] Transição suave: UI mostra progresso imediatamente (não espera response)
- [ ] Se GET results falha: usar partial results do SSE

### AC6: Backward compatibility
- [x] `X-Sync: true` header forces sync mode ✅ (routes/search.py:722-726)
- [x] `?sync=true` query param forces sync mode ✅
- [x] Flag `SEARCH_ASYNC_ENABLED` (default false) ✅ (config.py:470)
- [x] Frontend antigo continua funcionando (sync by default) ✅

### AC7: Timeout eliminado
- [x] POST retorna em <1s when async enabled ✅ (by design — enqueue + return 202)
- [x] Pipeline job no worker: sem proxy timeout ✅ (job_timeout=300 in WorkerSettings)
- [ ] SSE/polling: reconexão automática — ⚠️ SSE backoff implemented, polling fallback pending
- [x] Resultado: ELIMINA 524, WORKER TIMEOUT, SIGABRT when async active ✅

### AC8: Testes
- [x] Backend: POST 202 with search_id ✅ (test_stab009:TestAsyncEnabledReturns202)
- [x] Backend: /status endpoint ✅ (test_stab009:TestGetSearchStatus)
- [x] Backend: /results endpoint 200/202/404 ✅ (test_stab009:TestGetSearchResultsEndpoint)
- [x] Backend: X-Sync + ?sync=true fallback ✅ (test_stab009:TestXSyncHeaderForcesSyncMode)
- [ ] Frontend: test useSearch com modelo async — ⚠️ frontend not yet migrated to async
- [ ] E2E: busca completa end-to-end no modelo async

---

## Arquivos Envolvidos

| Arquivo | Ação |
|---------|------|
| `backend/routes/search.py` | AC1: POST retorna 202, AC3+AC4: novos endpoints |
| `backend/job_queue.py` | AC2: search_pipeline_job |
| `backend/search_pipeline.py` | AC2: executar como job, salvar resultado |
| `backend/config.py` | AC6: ASYNC_SEARCH_ENABLED flag |
| `frontend/app/buscar/hooks/useSearch.ts` | AC5: async flow + polling fallback |
| `frontend/app/api/buscar/route.ts` | AC5: proxy 202 + new endpoints |

---

## Decisões Técnicas

- **202 Accepted** — HTTP semântica correta para operações async. Client entende que precisa poll/listen.
- **ARQ job** — Pipeline pesado (PNCP fetch + LLM calls) deve rodar no worker, não no web process.
- **Polling fallback** — SSE é ideal mas não 100% confiável (proxies, firewalls). Polling é universal e resiliente.
- **Feature flag** — Mudança arquitetural grande, rollback instantâneo se problemas.
- **Esta é a solução definitiva** — GTM-STAB-003 (timeout fit) é paliativo. Esta story elimina a causa raiz.

## Estimativa
- **Esforço:** 12-16h (mudança arquitetural)
- **Risco:** Alto (toca todo o fluxo de busca)
- **Squad:** @architect (design) + @dev (backend async) + @dev (frontend migration) + @qa (E2E)

## Nota

Esta story é P2 porque GTM-STAB-003 (timeout chain reduction) resolve o problema no curto prazo. Esta é a solução **definitiva** que elimina a causa raiz (request longa = vulnerabilidade a timeout). Implementar após P0+P1 estarem stable.
