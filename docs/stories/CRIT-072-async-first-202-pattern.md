# CRIT-072: Migracao para HTTP 202 Async-First (Eliminacao do Timeout Cascade)

**Prioridade:** P2 — Refactor arquitetural
**Componente:** Backend (routes/search.py, search_pipeline.py, job_queue.py) + Frontend (useSearchExecution.ts, buscar/route.ts)
**Origem:** Conselho de CTOs — consenso unanime: operacoes >30s devem usar Asynchronous Request-Reply Pattern (HTTP 202)
**Status:** TODO
**Dependencias:** CRIT-071
**Estimativa:** 3-5 dias

## Problema

O `POST /v1/buscar` bloqueia por 115-224s antes de retornar JSON. Isso viola o padrao da industria (max 30-60s para sync) e cria uma cadeia de timeouts fragil onde qualquer elo pode falhar:

```
Client(115s) < Proxy(180s) < Gunicorn(180s) < Pipeline(224s) ← CONFLITO
```

SmartLic ja tem TODOS os building blocks para async-first:
- ARQ job queue funcional (`job_queue.py`)
- SSE streaming funcional (`progress.py` + `buscar-progress/` routes)
- Polling fallback funcional (`useSearchPolling.ts`)
- Async mode parcial (`GTM-ARCH-001`, codigo 202 no proxy)

O que falta e tornar o modo async o **padrao**, nao a excecao.

### Padrao da industria (Asynchronous Request-Reply)

Documentado formalmente por:
- [Azure: Asynchronous Request-Reply Pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/asynchronous-request-reply)
- [Google SRE: Deadline Propagation](https://sre.google/sre-book/addressing-cascading-failures/)
- Stripe, Vercel, ChatGPT, Claude API — todos usam 202 + SSE/webhooks para operacoes longas

### Fluxo atual vs desejado

```
ATUAL:
  POST /buscar → blocks 115-224s → JSON response
  GET  /buscar-progress/{id} → SSE (progress only)

DESEJADO:
  POST /buscar → 202 Accepted { search_id, status_url } em <2s
  GET  /buscar-progress/{id} → SSE (progress + partial_data + search_complete)
  GET  /search/{id}/results → JSON (final results, para polling fallback)
```

## Acceptance Criteria

### AC1: Backend — POST retorna 202 imediatamente
- [ ] `POST /v1/buscar` valida request, cria search session, enfileira job no ARQ, retorna:
  ```json
  { "search_id": "uuid", "status": "queued", "status_url": "/v1/search/{id}/status" }
  ```
- [ ] Tempo de resposta <2s (validacao + enqueue apenas)
- [ ] Quota check permanece sincrono (antes do enqueue)

### AC2: Backend — Search job no ARQ worker
- [ ] Nova funcao `search_job()` no `job_queue.py` que executa o pipeline completo
- [ ] Reutiliza `_run_stages()` existente do `search_pipeline.py`
- [ ] Job timeout: 300s (`SEARCH_JOB_TIMEOUT` em config.py)
- [ ] Em caso de falha: emite SSE event `error` + persiste status "failed" na session

### AC3: Backend — Endpoint de resultados
- [ ] `GET /v1/search/{id}/results` retorna resultados completos do cache L1/L2
- [ ] Se busca ainda em andamento: retorna `{ "status": "processing", "progress": {...} }`
- [ ] Se busca completa: retorna `BuscaResponse` completo
- [ ] Se busca falhou: retorna `{ "status": "failed", "error": {...} }`

### AC4: Backend — SSE `search_complete` com results_url
- [ ] Evento `search_complete` inclui `{ results_ready: true, results_url: "/v1/search/{id}/results" }`
- [ ] Frontend usa essa URL para buscar resultado final

### AC5: Frontend — Fluxo 202 no useSearchExecution
- [ ] `buscar()` faz POST, recebe 202, conecta SSE, aguarda `search_complete` → fetch results
- [ ] Se POST retorna 200 (fallback sync): processar como hoje (backwards-compatible)
- [ ] Logica: `if (response.status === 202) { setAsyncSearchActive(true); return; }`

### AC6: Frontend — Proxy 202 handling
- [ ] `buscar/route.ts`: se backend retorna 202, forward imediatamente (ja existe parcialmente)
- [ ] Remover retry logic para 202 (nao faz sentido retryar accepted)

### AC7: Frontend — Client timeout desnecessario com 202
- [ ] Com 202, o POST retorna em <2s — timeout de 185s nao e atingido
- [ ] Manter timeout como safety net (nao remover), mas na pratica nunca dispara
- [ ] Adicionar timeout de **SSE inactivity**: se nenhum evento SSE em 120s, mostrar erro

### AC8: Backend — Deadline propagation
- [ ] Incluir `X-Deadline` header com timestamp de expiracao no job
- [ ] Pipeline stages checam deadline restante e fazem graceful skip (reaproveitar STAB-003)
- [ ] Se deadline expirou: emitir `partial_data` com resultados ate o momento + `search_complete` com `is_partial: true`

### AC9: Metricas
- [ ] `smartlic_search_queue_time_seconds` — tempo na fila antes de worker pegar
- [ ] `smartlic_search_total_time_seconds` — tempo total incluindo fila
- [ ] `smartlic_search_mode_total{mode="async|sync"}` — contagem por modo

### AC10: Feature flag
- [ ] `ASYNC_SEARCH_DEFAULT` em config.py (default `True`)
- [ ] Se desabilitado: POST bloqueia como hoje (fallback completo)
- [ ] Permite rollback sem deploy

### AC11: Testes
- [ ] Backend: POST retorna 202 com search_id em <2s
- [ ] Backend: ARQ job executa pipeline e emite SSE events
- [ ] Backend: GET /search/{id}/results retorna dados apos conclusao
- [ ] Frontend: recebe 202 e ativa modo async
- [ ] Frontend: SSE search_complete → fetch results → mostra resultados
- [ ] Frontend: fallback sync (200) funciona como antes
- [ ] E2E: busca completa via 202+SSE flow

### AC12: Documentar cadeia de timeouts final
- [ ] Atualizar CLAUDE.md:
  ```
  POST /buscar → 202 em <2s (sem timeout concern)
  ARQ Job: 300s (SEARCH_JOB_TIMEOUT)
  Pipeline: 110s (PIPELINE_TIMEOUT)
  Per-source: 80s | Per-UF: 30s
  SSE inactivity timeout (client): 120s
  SSE heartbeat: 15s (keeps Railway idle 60s alive)
  ```

## File List

| Arquivo | Mudanca |
|---------|---------|
| `backend/routes/search.py` | 202 response, results endpoint |
| `backend/search_pipeline.py` | Refactor para rodar via ARQ job |
| `backend/job_queue.py` | search_job definition |
| `backend/config.py` | ASYNC_SEARCH_DEFAULT, SEARCH_JOB_TIMEOUT |
| `backend/progress.py` | SSE events com results_url |
| `backend/metrics.py` | Novas metricas queue/total time |
| `frontend/app/buscar/hooks/useSearchExecution.ts` | 202 flow, SSE inactivity timeout |
| `frontend/app/api/buscar/route.ts` | Proxy 202 handling |
| `frontend/app/buscar/hooks/useSearchSSEHandler.ts` | search_complete → fetch results |
| `frontend/__tests__/` | Testes unitarios |
| `backend/tests/` | Testes unitarios |

## Referencia

- [Azure: Asynchronous Request-Reply Pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/asynchronous-request-reply)
- [Google SRE: Addressing Cascading Failures](https://sre.google/sre-book/addressing-cascading-failures/)
- [SSE's Glorious Comeback 2025](https://portalzine.de/sses-glorious-comeback-why-2025-is-the-year-of-server-sent-events/)
- [REST API Design for Long-Running Tasks](https://restfulapi.net/rest-api-design-for-long-running-tasks/)
- [Stripe Webhook Timeout Guide](https://www.hookrelay.io/guides/stripe-webhook-timeout)

## Sequencia de Execucao

```
CRIT-070 (hotfix, 30min)  →  Deploy  →  Problema imediato resolvido
     |
CRIT-071 (1-2 dias)       →  Deploy  →  Partial data = timeout nunca = tela vazia
     |
CRIT-072 (3-5 dias)       →  Deploy  →  Timeout cascade eliminado na raiz
```

Apos CRIT-072:
```
Antes: Client(115s) < Proxy(180s) < Gunicorn(180s) < Pipeline(224s) ← CONFLITO
Depois: POST(<2s) → SSE(heartbeat 15s) → Worker(300s) → Pipeline(110s) ← ALINHADO
```
