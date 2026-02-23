# Periodic Cache Refresh via ARQ Worker — Research Consolidation

**Data:** 2026-02-22
**Objetivo:** Munir o PM com todas as informacoes necessarias para criar a story de refresh periodico do cache via ARQ worker.
**Status:** Pesquisa concluida. Nada foi implementado.

---

## 1. PROBLEMA ATUAL

O sistema SmartLic usa **Stale-While-Revalidate (SWR)** para manter o cache atualizado. O refresh do cache so e disparado **reativamente**:

| Trigger | Quando | Limitacao |
|---------|--------|-----------|
| Stale serve | Usuario faz busca + todas fontes falham + cache tem 6-24h | So atualiza se alguem buscar E as fontes cairem |
| HOT proactive | Cache HOT com 5.5h+ de idade e acessado | So para chaves HOT (>=3 acessos em 24h) |

**Gap:** Se nenhum usuario buscar nas ultimas 12h, o cache envelhece e eventualmente expira (>24h). Quando alguem finalmente busca, pega dados potencialmente velhos ou vazio. Nao ha mecanismo para manter o cache "quente" proativamente.

---

## 2. SOLUCAO PROPOSTA (Visao Geral)

Adicionar um **job ARQ periodico** (cron) que a cada ~12h:
1. Identifica quais buscas merecem refresh (HOT + WARM no cache)
2. Re-executa cada busca contra as fontes (PNCP/PCP/ComprasGov)
3. Salva resultados frescos no cache (3 niveis)
4. Respeita circuit breakers, rate limits, e budget de concorrencia

---

## 3. ESTADO ATUAL DA ARQUITETURA

### 3.1 Cache — 3 Niveis

| Nivel | Storage | TTL | Papel |
|-------|---------|-----|-------|
| L1 | Supabase (`search_results_cache`) | 24h | Persistente, sobrevive a restarts |
| L2 | Redis / InMemoryCache | HOT=2h, WARM=6h, COLD=1h | Rapido, volatil |
| L3 | Arquivo local (JSON) | 24h | Ultimo recurso |

### 3.2 Cache Status

| Status | Idade | Comportamento |
|--------|-------|---------------|
| FRESH | 0-6h | Serve direto |
| STALE | 6-24h | Serve + dispara revalidacao background |
| EXPIRED | >24h | Nao serve |

### 3.3 Prioridade (Hot/Warm/Cold)

| Prioridade | Condicao | Redis TTL | Eviction Order |
|------------|----------|-----------|----------------|
| HOT | >=3 acessos em 24h OU `is_saved_search=true` | 2h | Ultimo |
| WARM | >=1 acesso em 24h | 6h | Segundo |
| COLD | Sem acesso em 24h | 1h | Primeiro |

### 3.4 Background Revalidation (B-01)

Ja existe em `search_cache.py`:

```python
async def trigger_background_revalidation(
    user_id: str,
    params: dict,          # Cache params (setor_id, ufs, status, modalidades, modo_busca)
    request_data: dict,    # Replay params (ufs, data_inicial, data_final, modalidades)
    search_id: Optional[str] = None,
) -> bool:
```

**Pre-checks existentes:**
- Circuit breaker PNCP nao degradado
- Nao ha revalidacao em andamento para o mesmo `params_hash` (cooldown 10min via Redis key `revalidating:{hash}`)
- Budget nao excedido (max 3 concorrentes via `_active_revalidations`)

**Execucao (`_do_revalidation`):**
1. Chama `pncp_client.buscar_todas_ufs_paralelo(ufs, data_inicial, data_final, modalidades)` com timeout 180s
2. Sucesso → `save_to_cache()` (3 niveis) + reset `fail_streak`
3. Falha → `record_cache_fetch_failure()` → incrementa `fail_streak` + backoff exponencial

### 3.5 ARQ Job Queue (F-01)

**Modulo:** `backend/job_queue.py`

**Jobs existentes:**
| Job | Funcao | Timeout |
|-----|--------|---------|
| `llm_summary_job` | Gera resumo executivo com LLM | 60s |
| `excel_generation_job` | Gera Excel + upload storage | 60s |

**WorkerSettings atuais:**
```python
class WorkerSettings:
    functions = [llm_summary_job, excel_generation_job]
    max_jobs = 10
    job_timeout = 60
    max_tries = 3
    health_check_interval = 30
    retry_delay = 2.0
    # cron_jobs = []  ← NÃO USADO AINDA
```

**Worker startup:** `start.sh` com `PROCESS_TYPE=worker` → `exec arq job_queue.WorkerSettings`

**ARQ suporta `cron_jobs` nativamente** — lista de funcoes + schedule tipo crontab. Atualmente **nao utilizado**.

### 3.6 Cron Jobs Existentes (asyncio, NAO ARQ)

**Modulo:** `backend/cron_jobs.py` — 2 tarefas periodicas via `asyncio.create_task`:

| Task | Intervalo | Funcao |
|------|-----------|--------|
| Cache cleanup | 6h | Deleta arquivos locais expirados |
| Session cleanup | 6h | Marca sessoes antigas como `timed_out` |

Estas rodam no processo **web** (nao no worker). Sao fire-and-forget.

---

## 4. O QUE PRECISA SER CONSTRUIDO

### 4.1 Fonte de Dados: "Quais buscas refreshar?"

**Opcao A: Usar `search_results_cache` existente (Recomendado — sem migration)**

```sql
SELECT user_id, params_hash, search_params, priority, access_count, fetched_at
FROM search_results_cache
WHERE priority IN ('hot', 'warm')
  AND fetched_at < NOW() - INTERVAL '6 hours'   -- Ja stale
  AND (degraded_until IS NULL OR degraded_until < NOW())  -- Nao degradado
ORDER BY
  CASE priority WHEN 'hot' THEN 0 WHEN 'warm' THEN 1 ELSE 2 END,
  access_count DESC
LIMIT 50;  -- Budget por ciclo
```

**Vantagem:** Nenhuma tabela nova. Cache ja armazena `search_params` (JSONB).
**Desvantagem:** Nao ha conceito explicito de "busca salva pelo usuario".

**Opcao B: Nova tabela `saved_searches` (Futuro)**

Se quisermos que o usuario marque buscas como "favoritas" para refresh prioritario:

```sql
CREATE TABLE saved_searches (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  search_params JSONB NOT NULL,        -- Normalized params for cache key
  request_data JSONB NOT NULL,          -- Full params for replay (includes date template)
  is_active BOOLEAN DEFAULT true,
  refresh_frequency TEXT DEFAULT '12h', -- '6h', '12h', '24h'
  last_refreshed_at TIMESTAMPTZ,
  next_refresh_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, name)
);
```

**Vantagem:** Controle explicito do usuario.
**Desvantagem:** Requer migration + UI + endpoints novos.

### 4.2 Problema das Datas

**Ponto critico:** O cache key **exclui datas intencionalmente** (`compute_search_hash()` nao inclui `data_inicial/data_final`). Isso e o design "colchao de impacto" — cache serve independente do range de datas.

Porem, para re-executar uma busca, `_do_revalidation()` **precisa** de `data_inicial` e `data_final`:

```python
request_data = {
    "ufs": [...],
    "data_inicial": "2026-02-12",   # ← De onde vem no cron?
    "data_final": "2026-02-22",     # ← De onde vem no cron?
    "modalidades": [...],
}
```

**Opcoes para resolver:**

| Opcao | Como | Complexidade |
|-------|------|-------------|
| **A: Janela fixa** | Sempre usa `hoje - 10 dias` ate `hoje` (padrao do sistema) | Baixa |
| **B: Armazenar datas** | Salvar `request_data` no cache (ja existe campo `search_params`) | Baixa |
| **C: Template de datas** | Salvar "modo_busca=abertas" e derivar datas dinamicamente | Media |

**Recomendacao:** Opcao A (janela fixa de 10 dias) para v1. Simples, alinhado com o padrao existente.

### 4.3 Job ARQ: `cache_refresh_job`

**Funcao nova em `job_queue.py`:**

```python
async def cache_refresh_job(ctx: dict) -> dict:
    """Periodic cache refresh: re-fetch stale HOT+WARM entries."""
    # 1. Query Supabase for stale HOT+WARM cache entries
    # 2. For each entry:
    #    a. Check circuit breaker
    #    b. Check revalidation cooldown
    #    c. Call trigger_background_revalidation() with computed dates
    # 3. Return summary {refreshed: N, skipped: N, failed: N}
```

**Registro no WorkerSettings:**

```python
from arq.cron import cron

class WorkerSettings:
    functions = [llm_summary_job, excel_generation_job, cache_refresh_job]
    cron_jobs = [
        cron(cache_refresh_job, hour={0, 12}, minute=0),  # Executa 00:00 e 12:00 UTC
    ]
```

### 4.4 Integracao com Infraestrutura Existente

| Componente | Impacto | Mudanca |
|-----------|---------|---------|
| `job_queue.py` | Nova funcao + registro em cron_jobs | Adicionar job + WorkerSettings.cron_jobs |
| `search_cache.py` | Funcao de query "stale entries" | Nova funcao `get_stale_entries_for_refresh()` |
| `config.py` | Novos env vars | `CACHE_REFRESH_ENABLED`, `CACHE_REFRESH_INTERVAL_HOURS`, `CACHE_REFRESH_BATCH_SIZE` |
| `metrics.py` | Contadores de refresh | `cache_refresh_total`, `cache_refresh_errors_total` |
| `start.sh` | Nenhuma | Worker ja roda ARQ, cron_jobs e nativo |
| Frontend | Nenhuma (v1) | Cache e transparente para o FE |

---

## 5. PARAMETROS E CONSTANTES EXISTENTES

### 5.1 Limites de Concorrencia

| Parametro | Valor | Env Var | Arquivo |
|-----------|-------|---------|---------|
| Max revalidacoes concorrentes | 3 | `MAX_CONCURRENT_REVALIDATIONS` | config.py:373 |
| Timeout por revalidacao | 180s | `REVALIDATION_TIMEOUT` | config.py:370 |
| Cooldown entre revalidacoes (mesma key) | 600s (10min) | `REVALIDATION_COOLDOWN_S` | config.py:376 |
| Max jobs ARQ concorrentes | 10 | (hardcoded) | job_queue.py |
| Max conexoes Redis pool | 20 | (hardcoded) | redis_pool.py:32 |

### 5.2 TTLs do Cache

| Parametro | Valor | Arquivo |
|-----------|-------|---------|
| Fresh threshold | 6h | `CACHE_FRESH_HOURS` em search_cache.py |
| Stale threshold | 24h | `CACHE_STALE_HOURS` em search_cache.py |
| Redis TTL HOT | 2h (7200s) | `REDIS_TTL_BY_PRIORITY` |
| Redis TTL WARM | 6h (21600s) | `REDIS_TTL_BY_PRIORITY` |
| Redis TTL COLD | 1h (3600s) | `REDIS_TTL_BY_PRIORITY` |
| Local file TTL | 24h | `LOCAL_CACHE_TTL_HOURS` |

### 5.3 PNCP API Constraints

| Parametro | Valor | Impacto |
|-----------|-------|---------|
| Max tamanhoPagina | 50 | Cada UF retorna max 50 por pagina |
| Batch size (UFs) | 5 | Max 5 UFs em paralelo |
| Batch delay | 2.0s | Delay entre batches |
| Rate limit | ~10 req/s | Token bucket compartilhado |

---

## 6. RISCOS E MITIGACOES

| Risco | Severidade | Mitigacao |
|-------|------------|-----------|
| Cron sobrecarrega PNCP API | Alta | Respeitar rate limiter existente + stagger entre entries |
| Cron e SWR colidem na mesma key | Baixa | Cooldown de 10min ja existe via `revalidating:{hash}` |
| Redis fica cheio com mais dados | Baixa | Footprint estimado <300MB; Railway Redis suporta |
| Worker fica ocupado (LLM + Excel + Refresh) | Media | `max_jobs=10` distribui; refresh e I/O-bound, nao CPU |
| Circuit breaker aberto durante cron | Baixa | Pre-check ja existe em `trigger_background_revalidation()` |
| Datas incorretas no replay | Media | Usar janela fixa `hoje - 10d` (Opcao A) |

---

## 7. METRICAS E OBSERVABILIDADE

### Metricas novas sugeridas (Prometheus via `metrics.py`)

| Metrica | Tipo | Labels |
|---------|------|--------|
| `cache_refresh_total` | Counter | `result={success,skipped,failed,degraded}` |
| `cache_refresh_duration_seconds` | Histogram | — |
| `cache_refresh_entries_processed` | Gauge | — |

### Logs estruturados

```json
{
  "event": "cache_refresh_cycle",
  "total_candidates": 45,
  "refreshed": 12,
  "skipped_cooldown": 8,
  "skipped_degraded": 3,
  "skipped_cb_open": 2,
  "failed": 1,
  "duration_ms": 45000,
  "cycle_id": "uuid"
}
```

---

## 8. DECISOES PARA O PM TOMAR

| # | Decisao | Opcoes | Recomendacao |
|---|---------|--------|--------------|
| 1 | Frequencia do cron | 6h / 12h / 24h | **12h** (2x/dia — manha e noite) |
| 2 | Fonte de buscas para refresh | A: Cache existente / B: Nova tabela `saved_searches` | **A** para v1 (sem migration) |
| 3 | Quais prioridades refreshar | HOT only / HOT+WARM / Todas | **HOT+WARM** (COLD nao vale o custo) |
| 4 | Datas no replay | A: Janela fixa / B: Armazenar / C: Template | **A: `hoje-10d` ate `hoje`** |
| 5 | Budget por ciclo (max entries) | 10 / 25 / 50 | **25** (com stagger de 5s entre cada) |
| 6 | Feature flag | Sim / Nao | **Sim** (`CACHE_REFRESH_ENABLED`, default false) |
| 7 | Notificacao ao usuario | Nenhuma / Badge "atualizado" / Email | **Nenhuma** para v1 |
| 8 | Scope do deploy | Novo servico / Mesmo worker | **Mesmo worker ARQ** (ja existe) |

---

## 9. DEPENDENCIAS E PRE-REQUISITOS

| Dependencia | Status | Notas |
|------------|--------|-------|
| ARQ worker rodando em prod | OK | `PROCESS_TYPE=worker` no Railway |
| Redis disponivel | OK | Railway addon ativo |
| `trigger_background_revalidation()` | OK | Testado e estavel (B-01) |
| `search_results_cache` com `search_params` JSONB | OK | Campo ja existe |
| `search_results_cache` com `priority` | OK | B-02 ja implementou |
| `search_results_cache` com `degraded_until` | OK | B-03 ja implementou |
| `pncp_client.buscar_todas_ufs_paralelo()` | OK | Funcao de replay ja existe |
| Circuit breaker checks | OK | Integrado em `trigger_background_revalidation()` |
| Prometheus metrics endpoint | OK | E-03 ja implementou `/metrics` |

---

## 10. ESTIMATIVA DE COMPLEXIDADE

| Componente | Esforco | Arquivos |
|-----------|---------|----------|
| `cache_refresh_job` em job_queue.py | Pequeno | 1 arquivo |
| `get_stale_entries_for_refresh()` em search_cache.py | Pequeno | 1 arquivo |
| Config vars em config.py | Trivial | 1 arquivo |
| Feature flag em config.py | Trivial | 1 arquivo |
| Metricas em metrics.py | Pequeno | 1 arquivo |
| Testes (backend) | Medio | 1 arquivo novo |
| **Total estimado** | **~6-8h dev** | **5-6 arquivos** |

---

## 11. ACCEPTANCE CRITERIA SUGERIDOS

```
AC1: Job ARQ `cache_refresh_job` executa a cada 12h (configuravel via env)
AC2: Job consulta `search_results_cache` e seleciona entries HOT+WARM com `fetched_at` > 6h
AC3: Para cada entry, chama `trigger_background_revalidation()` com datas `hoje-10d` ate `hoje`
AC4: Respeita budget existente (max 3 concorrentes, cooldown 10min, circuit breaker check)
AC5: Stagger de 5s entre dispatches (evita burst no PNCP)
AC6: Feature flag `CACHE_REFRESH_ENABLED` (default false) controla ativacao
AC7: Log estruturado ao final de cada ciclo (total, refreshed, skipped, failed, duration_ms)
AC8: Metricas Prometheus: `cache_refresh_total{result}`, `cache_refresh_duration_seconds`
AC9: Se Redis indisponivel, job faz log.warning e retorna sem erro (graceful skip)
AC10: Testes unitarios para: query de entries, dispatch com mocks, feature flag off, Redis down
AC11: Env vars: CACHE_REFRESH_ENABLED, CACHE_REFRESH_INTERVAL_HOURS, CACHE_REFRESH_BATCH_SIZE
AC12: Nenhuma mudanca no frontend (cache e transparente)
```

---

## 12. DIAGRAMA DE FLUXO

```
┌─────────────────────────────────────────────────────────────────┐
│ ARQ Worker (PROCESS_TYPE=worker)                                 │
│                                                                  │
│  WorkerSettings.cron_jobs:                                       │
│    cache_refresh_job → every 12h (00:00, 12:00 UTC)             │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ cache_refresh_job(ctx)                                    │   │
│  │                                                           │   │
│  │  1. Check CACHE_REFRESH_ENABLED flag                      │   │
│  │     └── False? → return {skipped: "disabled"}             │   │
│  │                                                           │   │
│  │  2. Query Supabase: get_stale_entries_for_refresh()       │   │
│  │     SELECT * FROM search_results_cache                    │   │
│  │     WHERE priority IN ('hot','warm')                      │   │
│  │       AND fetched_at < NOW() - INTERVAL '6h'             │   │
│  │       AND (degraded_until IS NULL OR < NOW())             │   │
│  │     ORDER BY priority, access_count DESC                  │   │
│  │     LIMIT 25                                              │   │
│  │                                                           │   │
│  │  3. For each entry (with 5s stagger):                     │   │
│  │     ┌─────────────────────────────────────────────────┐   │   │
│  │     │ a. Build request_data:                           │   │   │
│  │     │    ufs = entry.search_params["ufs"]             │   │   │
│  │     │    data_inicial = hoje - 10 dias                │   │   │
│  │     │    data_final = hoje                            │   │   │
│  │     │    modalidades = entry.search_params[...]       │   │   │
│  │     │                                                 │   │   │
│  │     │ b. Call trigger_background_revalidation(         │   │   │
│  │     │      user_id = entry.user_id,                   │   │   │
│  │     │      params = entry.search_params,              │   │   │
│  │     │      request_data = {...},                      │   │   │
│  │     │    )                                            │   │   │
│  │     │                                                 │   │   │
│  │     │ c. Wait 5s (stagger)                            │   │   │
│  │     └─────────────────────────────────────────────────┘   │   │
│  │                                                           │   │
│  │  4. Log summary + emit metrics                            │   │
│  │     return {refreshed: 12, skipped: 8, failed: 1}         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  Existing functions reused:                                      │
│  ├── trigger_background_revalidation() [search_cache.py]         │
│  ├── _do_revalidation()                [search_cache.py]         │
│  ├── save_to_cache()                   [search_cache.py]         │
│  ├── buscar_todas_ufs_paralelo()       [pncp_client.py]          │
│  ├── get_circuit_breaker()             [pncp_client.py]          │
│  └── record_cache_fetch_failure()      [search_cache.py]         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 13. ARQUIVOS-CHAVE PARA REFERENCIA

| Arquivo | Relevancia |
|---------|-----------|
| `backend/job_queue.py` | Onde adicionar o novo job + cron_jobs |
| `backend/search_cache.py` | Funcoes de revalidacao + nova query |
| `backend/config.py` | Novos env vars |
| `backend/metrics.py` | Novas metricas |
| `backend/cron_jobs.py` | Referencia de pattern existente (asyncio cron) |
| `backend/start.sh` | Worker startup (nenhuma mudanca necessaria) |
| `backend/pncp_client.py` | `buscar_todas_ufs_paralelo()` — funcao de fetch |
| `supabase/migrations/026_search_results_cache.sql` | Schema da tabela de cache |
| `supabase/migrations/032_cache_priority_fields.sql` | Campos de prioridade |

---

*Documento gerado por squad de pesquisa (architect + data-engineer + dev + qa) em 2026-02-22.*
*Nenhum codigo foi modificado. Pronto para o PM criar a story.*
