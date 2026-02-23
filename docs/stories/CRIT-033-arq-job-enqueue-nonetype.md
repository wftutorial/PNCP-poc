# CRIT-033 — ARQ Job Enqueue Falha: NoneType (Worker Não Ativo)

**Status:** Done (code fix + infra deploy)
**Priority:** P1 — High
**Severity:** Error (silencioso — busca completa mas sem LLM summary/Excel)
**Sentry Issues:**
- SMARTLIC-BACKEND-1F (#7284854767) — Failed to enqueue llm_summary_job: 'NoneType' object has no attribute 'job_id'
- SMARTLIC-BACKEND-1E (#7284854756) — Failed to enqueue excel_generation_job: 'NoneType' object has no attribute 'job_id'
**Created:** 2026-02-23
**Relates to:** F-01 (ARQ Job Queue), CRIT-026 (Worker Timeout)

---

## Problema

Após deploy do F-01 (ARQ Job Queue), os jobs de LLM summary e Excel generation falham silenciosamente em produção. O `pool.enqueue_job()` retorna `None` em vez de um objeto `Job`, e o acesso a `.job_id` gera `AttributeError`.

### Cadeia de Falha

```
1. search_pipeline.py: "Queue mode: dispatching LLM + Excel jobs for search_id=..."
2. Redis PING → OK (pool conecta normalmente)
3. pool.enqueue_job('llm_summary_job', ...) → retorna None
4. result.job_id → AttributeError: 'NoneType' object has no attribute 'job_id'
```

### Causa Raiz Confirmada

1. **Worker não está rodando** — `PROCESS_TYPE=worker` nunca foi deployado como serviço separado no Railway
2. **`is_queue_available()` verificava apenas Redis ping** — não verificava presença do worker via `arq:queue:health-check`
3. **`enqueue_job()` não tratava retorno `None`** — crash em `job.job_id` quando pool.enqueue_job retorna None (dedup ou worker ausente)

### Evidência (Sentry Breadcrumbs)

```
02:31:21.380 — Redis PING (OK)
02:31:21.381 — Redis PING (OK)
02:31:21.382 — search_pipeline: "Queue mode: dispatching LLM + Excel jobs"
02:31:21.391 — Redis PING (OK)
02:31:21.395 — ERROR: "Failed to enqueue llm_summary_job: 'NoneType'..."
```

### Impacto

| Feature | Estado | Impacto |
|---------|--------|---------|
| LLM Summary | Fallback inline | Usuário recebe `gerar_resumo_fallback()` (puro Python, genérico) em vez de resumo IA |
| Excel Export | Fallback inline | Excel gerado inline (bloqueia response se pesado) em vez de background |
| SSE events | Nunca emitidos | `llm_ready` e `excel_ready` nunca chegam ao frontend |

**Nota:** O fallback funciona — busca não quebra. Mas o valor agregado de F-01 (background processing) está inativo.

## Acceptance Criteria

- [x] **AC1**: Verificar se `PROCESS_TYPE=worker` está configurado como serviço separado no Railway
  - **Verificado:** Não existe. Apenas `bidiq-backend` (web) está deployado. PROCESS_TYPE não está setado (default=web).
- [x] **AC2**: Se worker não existe, criar Railway service com `PROCESS_TYPE=worker` usando mesmo Dockerfile
  - **Done:** `bidiq-worker` service criado no Railway (same repo, root `/backend`, Dockerfile builder).
  - Env vars: `PROCESS_TYPE=worker`, `REDIS_URL`, `OPENAI_API_KEY`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_ANON_KEY`, `SENTRY_DSN`, `ENVIRONMENT=production`, `ENCRYPTION_KEY`, `ADMIN_USER_IDS`.
  - Config: `backend/railway-worker.toml` (no healthcheck — worker is not HTTP server).
  - Deployment `885d1279` active and Online (Feb 23, 2026 10:06 AM).
- [x] **AC3**: Se worker existe, verificar logs do worker para erros de conexão/startup
  - **N/A** — Worker não existe. Logs do web service confirmam apenas web process rodando.
- [x] **AC4**: `pool.enqueue_job()` deve retornar Job object (não None) — testar com log do job_id
  - **Fix:** `enqueue_job()` agora trata `None` gracefully (sem crash em `.job_id`). Warning log emitido.
  - **Fix:** `is_queue_available()` agora verifica `arq:queue:health-check` — pipeline não entra em queue mode sem worker.
  - **Fix:** `search_pipeline.py` checa retorno do enqueue — se None, marca status como `ready`/`fallback` em vez de `processing`.
- [ ] **AC5**: Após fix, LLM summary via SSE (`llm_ready` event) funciona em produção
  - **Worker deployed.** Requer teste manual em smartlic.tech para confirmar SSE `llm_ready` events.
- [ ] **AC6**: Após fix, Excel via SSE (`excel_ready` event) funciona em produção
  - **Worker deployed.** Requer teste manual em smartlic.tech para confirmar SSE `excel_ready` events.
- [ ] **AC7**: Sentry issues SMARTLIC-BACKEND-1F e 1E marcados como resolved
  - **Worker deployed.** Com o fix + worker ativo, os errors não devem mais ocorrer. Resolver manualmente no Sentry após confirmar.
- [x] **AC8**: Fallback continua funcionando se ARQ/Redis indisponível (zero regression)
  - **Verificado:** 17 novos testes + 42 existentes + 17 integration = 76 testes passando. Full suite: 5022 pass / 14 fail (pre-existing).

## Fix Implementado

### 1. `backend/job_queue.py` — 3 mudanças

**a) `_check_worker_alive(pool)`** — Nova função que verifica presença do worker via `arq:queue:health-check` key no Redis. Cache de 60s para evitar round-trip a cada busca.

**b) `is_queue_available()`** — Agora verifica Redis ping **E** worker alive. Se Redis up mas worker ausente → retorna `False` → pipeline usa inline mode.

**c) `enqueue_job()`** — Trata `pool.enqueue_job()` retornando `None` (dedup ou worker indisponível). Warning log em vez de crash em `.job_id`.

### 2. `backend/search_pipeline.py` — Enqueue return check

Pipeline agora verifica retorno de `enqueue_job()`:
- LLM enqueue → None: `ctx.llm_status="ready"`, `ctx.llm_source="fallback"`
- Excel enqueue → None: `ctx.excel_status="failed"`
- Ambos success: mantém `"processing"` (SSE events chegarão via worker)

### 3. `backend/tests/test_crit033_enqueue_fix.py` — 17 testes

- `TestEnqueueNoneHandling` (4): None from pool, success, no AttributeError, exception handling
- `TestWorkerAliveCheck` (5): Key exists, missing, cached, refreshed, exception
- `TestIsQueueAvailableWithWorker` (3): Redis+worker, Redis only, no Redis
- `TestPipelineEnqueueFallback` (3): LLM fail, Excel fail, both success
- `TestInlineFallbackRegression` (2): Queue unavailable, no search_id

## Infra Deploy (AC2 — Done)

Worker service `bidiq-worker` deployed on Railway:
- **Service ID:** `8de70e9f-df61-455a-8d15-c3948293796a`
- **Config:** `backend/railway-worker.toml` (Dockerfile builder, no healthcheck, ON_FAILURE restart x10)
- **Root directory:** `/backend`
- **Branch:** `main` (auto-deploy)
- **Status:** Online (deployment `885d1279`, Feb 23 2026 10:06 AM)

### Próximos Passos (AC5, AC6, AC7 — Validação Manual)

```bash
# Teste em produção:
# 1. Search no smartlic.tech → verify llm_ready + excel_ready SSE events
# 2. Sentry → resolve SMARTLIC-BACKEND-1F e 1E
```

## Files Envolvidos

- `backend/job_queue.py` — Pool creation, enqueue logic, worker detection
- `backend/start.sh` — PROCESS_TYPE routing (web vs worker)
- `backend/search_pipeline.py` — Job dispatch call site + enqueue return check
- `backend/tests/test_crit033_enqueue_fix.py` — 17 new tests
- `backend/railway-worker.toml` — Worker-specific Railway config (no healthcheck)
- Railway service `bidiq-worker` — PROCESS_TYPE=worker, same Dockerfile
