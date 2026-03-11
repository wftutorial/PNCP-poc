# Capacity Limits & Scaling Path — SmartLic

> Documentacao de limites de capacidade, gargalos conhecidos e plano de escala.
> Ultima atualizacao: 2026-03-11 | Story: DEBT-129

---

## 1. Limites Atuais de Capacidade

### Resumo Executivo

| Dimensao | Limite Atual | Observacao |
|----------|-------------|------------|
| Usuarios concorrentes | ~30 | Single instance, 1 Gunicorn worker |
| Buscas ativas simultaneas | ~10-15 | Limitado por ThreadPoolExecutor + asyncio |
| SSE connections simultaneas | ~50 | asyncio.Queue(maxsize=500) per tracker |
| Railway request timeout | ~120s | Hard limit do proxy Railway |
| Gunicorn worker timeout | 180s | `GUNICORN_TIMEOUT` env var |
| Memory (Railway) | 512MB-8GB | Depende do plano Railway |
| L1 cache entries | Configuravel | InMemoryCache per-worker |

### Detalhes por Componente

#### Gunicorn / Workers

- **Workers:** Configurado via `WEB_CONCURRENCY` (default: 1 no Railway starter)
- **Timeout:** 180s (env `GUNICORN_TIMEOUT`), mas Railway proxy mata em ~120s
- **Keep-alive:** 75s (> Railway proxy 60s, previne 502s intermitentes)
- **Preload:** Habilitado — reduz memory footprint por worker

#### ThreadPoolExecutor (LLM Calls)

- **filter_llm.py:** `ThreadPoolExecutor(max_workers=10)` para arbiter + zero-match
- **filter_llm.py:** `ThreadPoolExecutor(max_workers=3)` para arbiter batch
- **item_inspector.py:** `ThreadPoolExecutor(max_workers=ITEM_INSPECTION_CONCURRENCY)`
- **job_queue.py:** `ThreadPoolExecutor(max_workers=5)` para LLM summaries

**Impacto:** Com 10 workers de LLM por busca, 3 buscas simultaneas = 30 threads + API calls OpenAI. Pode saturar conexoes de rede e latencia de LLM.

#### asyncio.Queue (SSE Progress)

- **maxsize=500** eventos por tracker
- Cada busca ativa cria 1 tracker com 1 queue
- Queue drops quando cheia (backpressure, metrica: `smartlic_sse_queue_drops_total`)
- **Limitacao:** In-memory apenas — nao sobrevive restart, nao compartilha entre workers

#### InMemoryCache (L1)

- **TTL:** 4 horas
- **Per-worker:** Cada worker tem sua propria cache L1 — sem sharing
- **Implicacao:** Com N workers, cache L1 diverge entre workers
- **Fallback:** InMemoryCache e usado quando Redis esta indisponivel

#### Redis (Cache + State)

- **Pool connections:** Configuravel via `REDIS_POOL_MAX`
- **Metricas:** `smartlic_redis_pool_connections_used` / `smartlic_redis_pool_connections_max`
- **Fallback:** InMemoryCache automatico quando Redis cai

#### Supabase (PostgreSQL)

- **Connection pool:** Gerenciado pelo Supabase Cloud
- **Metricas:** `smartlic_supabase_pool_active_connections`
- **Circuit breaker:** `smartlic_supabase_cb_state` (0=closed, 1=open, 2=half_open)
- **Retry:** ConnectionError retry automatico (`smartlic_supabase_retry_total`)

#### Data Sources (PNCP, PCP, ComprasGov)

- **Per-source bulkhead:** Semaphore limita requests concorrentes por fonte
- **Circuit breaker:** 15 falhas threshold, 60s cooldown
- **Metricas:** `smartlic_source_active_requests`, `smartlic_source_pool_exhausted_total`

---

## 2. Gargalos Conhecidos

### G1: ThreadPoolExecutor(10) para LLM Calls

**Problema:** Cada busca pode spawnar ate 10 threads para classificacao LLM. Com multiplas buscas simultaneas, o numero de threads cresce linearmente.

**Sintomas:**
- Alta latencia de busca (p99 > 10s)
- `smartlic_llm_call_duration_seconds` elevado
- `smartlic_llm_batch_timeout_total` incrementando

**Mitigacao atual:** Budget timeout no zero-match, cap de itens (`MAX_ZERO_MATCH_ITEMS`)

### G2: asyncio.Queue para SSE (Single Instance)

**Problema:** Progress tracking usa asyncio.Queue in-memory. Com 1 worker, funciona bem. Com N workers, SSE connection pode conectar em worker diferente do que esta executando a busca.

**Sintomas:**
- SSE nao recebe updates (cliente vê progress parado)
- `smartlic_sse_connection_errors_total` elevado

**Mitigacao atual:** Redis-backed progress (STORY-294) quando Redis esta disponivel

### G3: InMemoryCache Per-Worker

**Problema:** Cache L1 nao e compartilhada entre workers. Cada worker rebuilda cache independentemente, multiplicando uso de memoria e requests duplicados.

**Sintomas:**
- Cache miss rate elevado com multiplos workers
- Uso de memoria cresce linearmente com workers

**Mitigacao atual:** Redis como L2 cache compartilhada

### G4: Single Instance Ceiling (~30 usuarios)

**Problema:** Combinacao de G1+G2+G3 limita capacidade a ~30 usuarios concorrentes com single instance.

**Base do calculo:**
- ~10 buscas ativas simultaneas (media de 3 buscas/usuario em sessao)
- 10 threads LLM por busca = 100 threads
- 10 SSE connections = 10 asyncio queues
- Memory: ~200-400MB com cache L1 quente

---

## 3. Plano de Escala (Scaling Checklist)

### Fase 1: Quick Wins (0-50 usuarios)

- [ ] **Aumentar WEB_CONCURRENCY para 2-3 workers** no Railway
  - Requer Redis como backend de SSE progress (ja implementado STORY-294)
  - Monitorar `smartlic_process_memory_rss_bytes` para nao estourar memoria
- [ ] **Habilitar Redis cache warming** para pre-popular L1 cache
  - Reduz cold start por worker
- [ ] **Configurar Railway auto-scaling** (se disponivel no plano)
  - Threshold: CPU > 80% por 2 min

### Fase 2: Horizontal Scaling (50-200 usuarios)

- [ ] **Migrar SSE progress para Redis Pub/Sub** (se ainda nao feito)
  - Permite SSE funcionar com qualquer worker
- [ ] **Adicionar segundo servico Railway** (load-balanced)
  - Separar web (API) de worker (ARQ jobs)
  - Ja implementado via `PROCESS_TYPE` em `start.sh`
- [ ] **Redis connection pool sizing**
  - Aumentar `REDIS_POOL_MAX` proporcional ao numero de workers
  - Monitorar `smartlic_redis_pool_connections_used`
- [ ] **Revisar ThreadPoolExecutor limits**
  - Reduzir max_workers por busca se muitas buscas concorrentes
  - Considerar queue-based approach vs thread-per-call

### Fase 3: Production Grade (200+ usuarios)

- [ ] **Supabase connection pooler** (PgBouncer)
  - Necessario com > 50 conexoes simultaneas
- [ ] **Redis cluster ou Upstash Pro**
  - Para alta disponibilidade e throughput
- [ ] **CDN para frontend** (ja no Vercel/Railway)
- [ ] **LLM call batching** com queue dedicada
  - Consolidar requests LLM em batches maiores
  - Reduzir overhead de conexao por chamada
- [ ] **Rate limiting por usuario** (ja implementado via Redis token bucket)
  - Ajustar limites conforme base cresce
- [ ] **Observabilidade:** Conectar Prometheus a Grafana Cloud
  - Dashboards de capacidade em tempo real
  - Alertas baseados em metricas customizadas

---

## 4. Metricas-Chave para Monitorar Capacidade

| Metrica | Threshold Warning | Threshold Critical | Acao |
|---------|-------------------|-------------------|------|
| `smartlic_active_searches` | > 8 | > 15 | Verificar se buscas estao acumulando |
| `smartlic_process_memory_rss_bytes` | > 400MB | > 700MB | Escalar ou investigar leak |
| `smartlic_search_duration_seconds` p99 | > 30s | > 60s | Verificar LLM latency + source timeout |
| `smartlic_supabase_pool_active_connections` | > 15 | > 25 | Considerar connection pooler |
| `smartlic_redis_pool_connections_used` | > 80% do max | > 95% do max | Aumentar pool max |
| `smartlic_source_pool_exhausted_total` rate | > 1/min | > 5/min | Aumentar bulkhead limit |
| `smartlic_tracker_active_count` | > 20 | > 40 | Verificar cleanup de trackers |
| `smartlic_inmemory_cache_entries` | > 80% do max | > 95% do max | Ajustar max ou TTL |

---

## 5. Referencia Rapida de Limites por Plano Railway

| Plano | vCPU | RAM | Bandwidth | Observacao |
|-------|------|-----|-----------|------------|
| Starter | 0.5 | 512MB | 5GB/mo | Suficiente para POC/beta |
| Pro | 2 | 2GB | 25GB/mo | Recomendado para 30-100 usuarios |
| Team | 4+ | 8GB+ | Custom | Para 100+ usuarios |

**Nota:** Railway cobra por uso. Auto-scaling pode aumentar custos significativamente.
