# CRIT-032 — Periodic Cache Refresh via ARQ Worker (Cron)

**Tipo:** Enhancement / Resilience
**Prioridade:** P1 — UX + Dados frescos para usuarios recorrentes
**Criada:** 2026-02-22
**Status:** Concluída
**Origem:** Decisao estrategica — manter cache proativamente quente
**Componentes:** backend/job_queue.py, backend/search_cache.py, backend/config.py, backend/metrics.py
**Research:** `docs/sessions/2026-02/2026-02-22-periodic-cache-refresh-research.md`

---

## Problema

O cache do SmartLic so e atualizado **reativamente**:

| Trigger atual | Quando dispara | Limitacao |
|---------------|----------------|-----------|
| Stale serve (SWR) | Usuario busca + todas fontes falham + cache tem 6-24h | So atualiza se alguem buscar **E** as fontes cairem |
| HOT proactive | Cache HOT acessado com 5.5h+ de idade | So para chaves com >=3 acessos em 24h |

**Gaps identificados:**

1. **Cache envelhece sem uso:** Se nenhum usuario busca nas ultimas 12h, o cache expira (>24h). Proximo usuario pega dado velho ou vazio.
2. **Caches vazios nao sao retentados:** Se a busca original retornou 0 resultados (PNCP fora, timeout, etc.), o cache armazena resultado vazio. Esse cache vazio **nunca e retentado automaticamente** — o usuario vê "0 resultados" ate o cache expirar e alguem buscar de novo.
3. **Primeira experiencia degradada:** Usuarios que acessam fora de horario comercial frequentemente pegam cache stale ou vazio.

### Impacto

- **UX:** Usuarios recorrentes esperam dados frescos; recebem dados de 12-24h atras
- **Conversao:** Trial users que veem "0 resultados" por falha transitoria podem desistir
- **Confiabilidade percebida:** Sistema parece "desatualizado" mesmo com dados disponiveis no PNCP

---

## Solucao

Adicionar um **job ARQ periodico** (cron nativo) que executa a cada 12h no worker existente:

1. Consulta `search_results_cache` — seleciona entries HOT + WARM stale **e entries com 0 resultados** (independente de prioridade)
2. Re-executa cada busca contra PNCP/PCP/ComprasGov usando `trigger_background_revalidation()` existente
3. Salva resultados frescos no cache (3 niveis: Supabase + Redis + Local)
4. Respeita todos os guardrails existentes (circuit breaker, cooldown, budget, rate limiter)

### Decisoes Tecnicas

| Decisao | Escolha | Justificativa |
|---------|---------|---------------|
| Frequencia | 12h (00:00 + 12:00 UTC) | Cobre manha e noite; configuravel via env |
| Fonte de buscas | `search_results_cache` existente | Sem migration nova; search_params ja preservado em JSONB |
| Prioridades | HOT + WARM + **entries vazias** | COLD nao compensa; vazias sao prioridade maxima |
| Datas no replay | Janela fixa `hoje - 10 dias` ate `hoje` | Padrao do sistema; cache key exclui datas intencionalmente |
| Budget por ciclo | 25 entries (configuravel) | Com stagger de 5s entre dispatches |
| Feature flag | `CACHE_REFRESH_ENABLED` (default false) | Ativar em producao apos validacao |
| Deploy | Mesmo worker ARQ existente | `cron_jobs` e feature nativa do ARQ; sem novo servico |
| Frontend | Nenhuma mudanca | Cache e transparente para o FE |

### Fluxo

```
ARQ Worker (cron: 00:00, 12:00 UTC)
│
├─ 1. Check CACHE_REFRESH_ENABLED → false? return skip
│
├─ 2. get_stale_entries_for_refresh()
│      SELECT FROM search_results_cache
│      WHERE (
│        (priority IN ('hot','warm') AND fetched_at < NOW() - 6h)
│        OR total_results = 0  ← NOVO: caches vazios sempre elegíveis
│      )
│      AND (degraded_until IS NULL OR < NOW())
│      ORDER BY
│        total_results ASC,              ← Vazios primeiro
│        CASE priority WHEN 'hot' THEN 0 WHEN 'warm' THEN 1 ELSE 2 END,
│        access_count DESC
│      LIMIT {CACHE_REFRESH_BATCH_SIZE}
│
├─ 3. For each entry (5s stagger):
│      ├─ Build request_data:
│      │    ufs = entry.search_params["ufs"]
│      │    data_inicial = hoje - 10 dias
│      │    data_final = hoje
│      │    modalidades = entry.search_params["modalidades"]
│      │
│      ├─ Call trigger_background_revalidation(
│      │      user_id, params, request_data
│      │  )
│      │  (reusa pre-checks: CB, cooldown 10min, budget max 3)
│      │
│      └─ Wait 5s → next entry
│
└─ 4. Log summary + emit Prometheus metrics
       return {refreshed: N, skipped: N, failed: N, empty_retried: N}
```

---

## Criterios de Aceitacao

### Job ARQ Periodico

- [x] **AC1:** Nova funcao `cache_refresh_job(ctx)` registrada em `WorkerSettings.functions` e `WorkerSettings.cron_jobs`
- [x] **AC2:** Job executa a cada 12h (configuravel via `CACHE_REFRESH_INTERVAL_HOURS`); usa `arq.cron()` nativo
- [x] **AC3:** Feature flag `CACHE_REFRESH_ENABLED` (default `false`) controla ativacao; se `false`, job retorna imediatamente com log.info

### Query de Entries Candidatas

- [x] **AC4:** Nova funcao `get_stale_entries_for_refresh(batch_size)` em `search_cache.py`
- [x] **AC5:** Query seleciona entries HOT + WARM com `fetched_at` anterior a `CACHE_FRESH_HOURS` (6h)
- [x] **AC6:** Query **tambem** seleciona entries com `total_results = 0` (caches vazios), **independente de prioridade**, como candidatas prioritarias
- [x] **AC7:** Entries vazias aparecem **antes** de entries stale no ordenamento (vazios primeiro, depois HOT, depois WARM)
- [x] **AC8:** Entries com `degraded_until > NOW()` sao excluidas (respeita backoff existente)
- [x] **AC9:** Limite de entries por ciclo configuravel via `CACHE_REFRESH_BATCH_SIZE` (default 25)

### Replay de Buscas

- [x] **AC10:** Para cada entry, constroi `request_data` com datas `date.today() - 10 dias` ate `date.today()`
- [x] **AC11:** Chama `trigger_background_revalidation()` existente (reusa todos pre-checks: circuit breaker, cooldown 10min, budget max 3 concorrentes)
- [x] **AC12:** Stagger de 5s (`asyncio.sleep(5)`) entre dispatches de entries consecutivas para evitar burst no PNCP
- [x] **AC13:** Se circuit breaker PNCP degradado, job para o ciclo imediatamente (nao tenta proximas entries) com log.warning

### Graceful Degradation

- [x] **AC14:** Se Redis indisponivel, job faz log.warning e retorna sem erro (nao crasheia o worker)
- [x] **AC15:** Se Supabase indisponivel (query falha), job faz log.error e retorna sem erro
- [x] **AC16:** Job timeout adequado ao batch size: `job_timeout = max(300, CACHE_REFRESH_BATCH_SIZE * 10)` segundos

### Observabilidade

- [x] **AC17:** Log estruturado ao final de cada ciclo:
  ```json
  {
    "event": "cache_refresh_cycle",
    "cycle_id": "uuid",
    "total_candidates": 25,
    "refreshed": 12,
    "skipped_cooldown": 5,
    "skipped_degraded": 2,
    "skipped_cb_open": 1,
    "failed": 1,
    "empty_retried": 4,
    "duration_ms": 45000
  }
  ```
- [x] **AC18:** Metricas Prometheus:
  - `cache_refresh_total` (Counter, labels: `result={success,skipped,failed,empty_retry}`)
  - `cache_refresh_duration_seconds` (Histogram)
- [x] **AC19:** Metricas usam pattern existente de `metrics.py` (NoopMetric fallback se prometheus_client indisponivel)

### Configuracao

- [x] **AC20:** Env vars em `config.py`:
  - `CACHE_REFRESH_ENABLED` (bool, default `false`)
  - `CACHE_REFRESH_INTERVAL_HOURS` (int, default `12`)
  - `CACHE_REFRESH_BATCH_SIZE` (int, default `25`)
  - `CACHE_REFRESH_STAGGER_SECONDS` (int, default `5`)
- [x] **AC21:** Env vars documentadas em `.env.example`

### Testes

- [x] **AC22:** Teste: `get_stale_entries_for_refresh()` retorna entries HOT+WARM stale ordenadas por prioridade
- [x] **AC23:** Teste: entries com `total_results=0` aparecem na query independente de prioridade, e **antes** de entries stale
- [x] **AC24:** Teste: entries com `degraded_until` no futuro sao excluidas
- [x] **AC25:** Teste: `cache_refresh_job` com feature flag `false` retorna imediatamente
- [x] **AC26:** Teste: `cache_refresh_job` chama `trigger_background_revalidation()` para cada entry com datas corretas (hoje-10d, hoje)
- [x] **AC27:** Teste: job para ciclo se circuit breaker PNCP degradado (AC13)
- [x] **AC28:** Teste: job graceful quando Redis indisponivel (AC14) e Supabase indisponivel (AC15)
- [x] **AC29:** Teste: stagger de 5s entre dispatches (mock asyncio.sleep)
- [x] **AC30:** Teste: metricas Prometheus emitidas corretamente (success, skipped, failed, empty_retry)
- [x] **AC31:** Zero regressoes nos testes existentes (baseline: ~10 fail backend / ~4300 pass)

### Nao-Escopo (v1)

- [x] **AC32:** Nenhuma mudanca no frontend (cache e transparente)
- [x] **AC33:** Nenhuma migration de banco (usa tabela existente `search_results_cache`)
- [x] **AC34:** Nenhuma notificacao ao usuario sobre refresh (silencioso)

---

## Arquivos Impactados

| Arquivo | Mudanca |
|---------|---------|
| `backend/job_queue.py` | Nova funcao `cache_refresh_job` + registro em `WorkerSettings.functions` + `WorkerSettings.cron_jobs` |
| `backend/search_cache.py` | Nova funcao `get_stale_entries_for_refresh(batch_size)` |
| `backend/config.py` | 4 novos env vars (`CACHE_REFRESH_*`) |
| `backend/metrics.py` | 2 novas metricas (`cache_refresh_total`, `cache_refresh_duration_seconds`) |
| `backend/.env.example` | Documentacao dos novos env vars |
| `backend/tests/test_cache_refresh.py` | **Novo** — ~10 testes (AC22-AC31) |

**Nenhuma mudanca em:** start.sh, frontend, migrations, routes

---

## Contexto Tecnico (Referencia)

### Infraestrutura Existente Reutilizada

| Componente | Funcao | Arquivo |
|-----------|--------|---------|
| `trigger_background_revalidation()` | Orquestra pre-checks + dispatch | search_cache.py |
| `_do_revalidation()` | Executa fetch + save | search_cache.py |
| `save_to_cache()` | Salva em 3 niveis | search_cache.py |
| `buscar_todas_ufs_paralelo()` | Fetch multi-UF | pncp_client.py |
| `get_circuit_breaker()` | Estado do CB | pncp_client.py |
| `record_cache_fetch_failure()` | Backoff exponencial | search_cache.py |
| ARQ WorkerSettings | Cron nativo | job_queue.py |
| Prometheus metrics | NoopMetric fallback | metrics.py |

### Limites Existentes

| Parametro | Valor | Env Var |
|-----------|-------|---------|
| Max revalidacoes concorrentes | 3 | `MAX_CONCURRENT_REVALIDATIONS` |
| Timeout por revalidacao | 180s | `REVALIDATION_TIMEOUT` |
| Cooldown mesma key | 600s (10min) | `REVALIDATION_COOLDOWN_S` |
| Max jobs ARQ concorrentes | 10 | Hardcoded |
| Max conexoes Redis | 20 | Hardcoded |
| PNCP max page size | 50 | Hardcoded API limit |
| PNCP batch UFs | 5 por batch, 2s delay | Config |

### Cache Key

```python
# compute_search_hash() — EXCLUI datas intencionalmente
normalized = {
    "setor_id": "vestuario",
    "ufs": ["MG", "RJ", "SP"],      # sorted
    "status": "abertas",
    "modalidades": [4, 5, 6, 7],     # sorted
    "modo_busca": "abertas",
}
→ SHA256 → 64-char hex string
```

### Tabela search_results_cache (Schema Relevante)

```sql
-- Campos usados pela query:
user_id         UUID
params_hash     TEXT        -- SHA256 do search_params
search_params   JSONB       -- Params originais (setor_id, ufs, status, modalidades, modo_busca)
total_results   INT         -- 0 = cache vazio (candidato prioritario)
fetched_at      TIMESTAMPTZ -- Quando os dados foram buscados
priority        TEXT        -- 'hot', 'warm', 'cold'
access_count    INT         -- Numero de acessos
degraded_until  TIMESTAMPTZ -- Se != NULL e > NOW(), entry esta degradada (backoff)
```

---

## Riscos e Mitigacoes

| Risco | Severidade | Mitigacao |
|-------|------------|-----------|
| Cron sobrecarrega PNCP API | Alta | Stagger 5s + rate limiter existente + budget 3 concorrentes |
| Colisao cron vs SWR (mesma key) | Baixa | Cooldown 10min via `revalidating:{hash}` ja existe |
| Worker ocupado (LLM + Excel + Refresh) | Media | Refresh e I/O-bound; max_jobs=10 distribui |
| Circuit breaker abre durante cron | Baixa | AC13: para ciclo imediatamente |
| Redis cheio | Baixa | Footprint <300MB; sem dados novos (substitui existentes) |
| Caches vazios em loop de retry infinito | Media | `degraded_until` com backoff exponencial impede retries excessivos |

---

## Estimativa

| Componente | Esforco |
|-----------|---------|
| `cache_refresh_job` + cron registration | 1-2h |
| `get_stale_entries_for_refresh()` | 1-2h |
| Config + metrics | 1h |
| Testes (~10 casos) | 2-3h |
| **Total** | **~6-8h** |

---

## Definicao de Pronto

1. Feature flag `CACHE_REFRESH_ENABLED=true` ativa o cron no worker
2. Worker executa refresh a cada 12h
3. Caches vazios (0 resultados) sao retentados com prioridade
4. Caches stale HOT+WARM sao atualizados proativamente
5. Metricas Prometheus confirmam execucao
6. Testes passam sem regressao
7. Nenhuma mudanca no frontend ou banco

---

*Story baseada no research doc: `docs/sessions/2026-02/2026-02-22-periodic-cache-refresh-research.md`*
*Gerada por @pm (Morgan) em 2026-02-22.*
