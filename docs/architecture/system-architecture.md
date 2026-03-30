# SmartLic — System Architecture Assessment

**Data:** 2026-03-30 | **Autor:** @architect (Aria) | **Fase:** Brownfield Discovery Phase 1
**Codebase:** branch `main` HEAD | **Versao:** 6.0

---

## 1. Resumo Executivo

SmartLic e uma plataforma de inteligencia em licitacoes publicas (B2G) que automatiza a descoberta, analise e qualificacao de oportunidades para empresas que participam de compras governamentais no Brasil. Desenvolvida pela CONFENGE Avaliacoes e Inteligencia Artificial LTDA, o sistema agrega dados de 3 fontes governamentais (PNCP, PCP v2, ComprasGov v3), aplica classificacao IA por setor (GPT-4.1-nano), calcula viabilidade em 4 fatores, e oferece um pipeline kanban para gestao de oportunidades.

**Estagio:** POC avancado (v0.5) em producao, beta com trials, pre-revenue.
**URL:** https://smartlic.tech

### Numeros do Codebase

| Metrica | Valor |
|---------|-------|
| Arquivos Python (backend, excl. testes) | ~266 |
| LOC Python (backend, excl. testes) | ~81.800 |
| Arquivos de teste backend | 169 (5.131+ testes) |
| Arquivos de teste frontend | 135 (2.681+ testes) |
| Testes E2E (Playwright) | 60 |
| Migrations Supabase | 99 |
| Feature flags registradas | 30+ |
| Endpoints API | 49+ em 36 route modules |
| Paginas frontend | 22+ |

---

## 2. Analise do Tech Stack

### 2.1 Backend

| Componente | Tecnologia | Versao | Proposito |
|------------|------------|--------|-----------|
| Framework Web | FastAPI | 0.129.0 | API async com Pydantic v2 |
| Runtime | Python | 3.12 | Linguagem principal |
| ASGI Server | Uvicorn | 0.41.0 | Sem extras [standard] (CRIT-SIGSEGV) |
| Process Manager | Gunicorn | 23.0.0 | Multi-worker (timeout 180s) |
| Validacao | Pydantic | 2.12.5 | Schemas tipados, validacao de input |
| HTTP Client | httpx | 0.28.1 | Async HTTP para APIs externas |
| LLM | OpenAI SDK | 1.109.1 | GPT-4.1-nano classificacao + resumos |
| Database Client | Supabase | 2.28.0 | PostgreSQL + Auth + RLS |
| Cache | Redis | 5.3.1 | Cache distribuido + rate limiting |
| Job Queue | ARQ | >=0.26 | Background jobs async |
| Billing | Stripe | 11.4.1 | Subscriptions, checkout, webhooks |
| Email | Resend | >=2.0 | Emails transacionais |
| Excel | openpyxl | 3.1.5 | Geracao de planilhas |
| PDF | ReportLab | 4.4.0 | Relatorios diagnostico |
| Metricas | prometheus_client | >=0.20 | Metricas Prometheus |
| Tracing | OpenTelemetry | >=1.25 | Distributed tracing (OTLP HTTP) |
| Error Tracking | Sentry SDK | >=2.0 | Captura de excecoes |
| JWT | PyJWT | 2.11.0 | Validacao local ES256+JWKS |
| Crypto | cryptography | >=46.0.5,<47.0 | Pinned por fork-safety (CRIT-SIGSEGV) |
| Logging | python-json-logger | >=2.0.4 | JSON structured logs em producao |

**Notas criticas:**
- Uvicorn sem extras `[standard]` pois uvloop causa SIGSEGV intermitente em producao (interacao chardet/hiredis/cryptography).
- cryptography pinada em `>=46.0.5,<47.0` por fork-safety com Gunicorn preload.
- OpenAI client com timeout de 5s (5x p99 do GPT-4.1-nano) para evitar thread starvation.

### 2.2 Frontend

| Componente | Tecnologia | Versao | Proposito |
|------------|------------|--------|-----------|
| Framework | Next.js | 16.1.6 | SSR + routing |
| UI Library | React | 18.3.1 | Componentes |
| Linguagem | TypeScript | 5.9 | Type safety |
| Styling | Tailwind CSS | 3.x | Utility-first CSS |
| Animacoes | Framer Motion | 12.33.0 | Transicoes/animacoes |
| Charts | Recharts | 3.7.0 | Visualizacoes analytics |
| Auth | Supabase SSR | 0.8.0 | Auth client-side |
| Kanban | @dnd-kit | 6.3.1 | Drag-and-drop pipeline |
| Onboarding | Shepherd.js | 14.5.1 | Tours guiados |
| Forms | React Hook Form + Zod | 7.71 / 4.3 | Validacao de formularios |
| Data Fetching | SWR | 2.4.1 | Stale-while-revalidate |
| Analytics | Mixpanel | 2.74.0 | Product analytics |
| Error Tracking | Sentry | 10.38.0 | Error monitoring |
| Testing | Jest + Testing Library | 29.7 | Unit tests |
| E2E | Playwright | 1.58.2 | Testes end-to-end |

### 2.3 Infraestrutura

| Componente | Servico | Detalhes |
|------------|---------|----------|
| Backend Hosting | Railway | Web + Worker (monorepo com `RAILWAY_SERVICE_ROOT_DIRECTORY`) |
| Frontend Hosting | Railway | Standalone Next.js |
| Database | Supabase Cloud | PostgreSQL 17 + RLS + Edge Functions |
| Cache/Queue | Redis (Upstash/Railway) | Cache L1, rate limiting, ARQ broker, SSE Streams |
| CI/CD | GitHub Actions | 6+ workflows (tests, migration gate, deploy, E2E) |
| DNS/CDN | Cloudflare (inferido) | HTTPS + edge caching |

**Limites Railway:**
- Hard timeout: ~120s para requests HTTP.
- Gunicorn timeout: 180s (env `GUNICORN_TIMEOUT`).
- Deploy auto via push em `main`, watch patterns por servico.

### 2.4 Servicos Externos

| Servico | Uso | SLA/Notas |
|---------|-----|-----------|
| PNCP API | Fonte primaria de licitacoes | Max 50 items/pagina, rate limiting ativo |
| PCP v2 API | Fonte secundaria (publica, sem auth) | 10/pagina, sem filtro UF server-side |
| ComprasGov v3 | Fonte terciaria (dados abertos) | Dual-endpoint (legacy + Lei 14.133) |
| OpenAI API | GPT-4.1-nano classificacao + resumos | ~R$0.00007/classificacao, timeout 5s |
| Stripe | Billing, subscriptions, webhooks | Webhook signature verification |
| Resend | Emails transacionais | Trial sequences, alertas |
| Supabase Auth | Autenticacao JWT (ES256+JWKS) | Validacao local, sem API call |
| IBGE API | Dados geograficos (cache) | Usado para contexto de localizacao |

---

## 3. Padroes Arquiteturais

### 3.1 Arquitetura de Dados (3 Camadas)

O SmartLic implementa uma arquitetura de dados em 3 camadas que separa ingestao, busca e cache:

```
┌─────────────────────────────────────────────────────────────────┐
│                    CAMADA 1: INGESTAO (ETL)                     │
│                                                                 │
│  ARQ Cron Jobs ──> PNCP API ──> Transformer ──> Loader         │
│  (full diario 2am BRT, incremental 3x/dia)                     │
│                          ↓                                      │
│               pncp_raw_bids (~40K+ rows)                        │
│        GIN full-text index (Portuguese), 12-dia retention       │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│                  CAMADA 2: SEARCH PIPELINE                      │
│                                                                 │
│  POST /buscar ──> SearchPipeline.run() ──> 7 stages             │
│  VALIDATE → PREPARE → EXECUTE → FILTER → ENRICH →              │
│  POST_FILTER_LLM → GENERATE → PERSIST                          │
│                                                                 │
│  Execute: query_datalake() (tsquery PostgreSQL)                 │
│  Fallback: live API fetch se datalake retorna 0                 │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│                   CAMADA 3: CACHE (SWR)                         │
│                                                                 │
│  L1: InMemory/Redis (4h TTL, hot/warm/cold priority)            │
│  L2: Supabase search_results_cache (24h TTL, persistent)        │
│  L3: Local File (24h TTL, emergency fallback)                   │
│                                                                 │
│  SWR: serve stale + revalidate background                       │
│  (max 3 concurrent, 180s timeout)                               │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Search Pipeline (7 Estagios)

O `SearchPipeline` (em `search_pipeline.py`) e o orquestrador principal. Cada estagio e um modulo isolado em `pipeline/stages/`:

| Estagio | Modulo | Responsabilidade |
|---------|--------|------------------|
| 1. VALIDATE | `validate.py` | Valida request (UFs, datas, setor), normaliza inputs |
| 2. PREPARE | `prepare.py` | Carrega config do setor, keywords, prepara contexto |
| 3. EXECUTE | `execute.py` | Busca dados: datalake query ou multi-source API fetch |
| 4. FILTER | `filter_stage.py` | Aplica filtros: UF, valor, keywords, density scoring |
| 5. ENRICH | `enrich.py` | Viability assessment, status inference, urgencia |
| 6. POST_FILTER_LLM | `post_filter_llm.py` | LLM zero-match classification para density 0% |
| 7. GENERATE | `generate.py` | Gera resumo LLM + Excel (inline ou ARQ background) |
| 8. PERSIST | `persist.py` | Salva resultados no cache + search_results_cache |

**State Machine:** Cada busca tem um state machine (`search_state_manager.py`) que rastreia transicoes e permite SSE progress tracking.

**Timeout Chain (mais restritivo ao mais amplo):**
```
Per-UF fetch: 30s → Per-Source: 80s → Consolidation: 100s → Pipeline: 110s → ARQ Job: 300s
```

### 3.3 Pipeline de Ingestao (ETL)

O modulo `ingestion/` implementa um ETL completo para popular o datalake local:

```
ingestion/
├── config.py        # Feature flags, schedule, rate limits
├── crawler.py       # Orquestra crawl full/incremental por UF x modalidade
├── transformer.py   # Normaliza dados PNCP para formato pncp_raw_bids
├── loader.py        # Bulk upsert via RPC (500 rows/batch, content_hash dedup)
├── checkpoint.py    # Tracking de progresso: ingestion_checkpoints + ingestion_runs
├── scheduler.py     # Registro de cron jobs no ARQ
└── metrics.py       # Prometheus counters especificos de ingestao
```

**Schedule (UTC):**
- Full crawl: 05:00 diario (2am BRT) — 27 UFs x 6 modalidades, 10 dias
- Incremental: 11:00, 17:00, 23:00 (8am, 2pm, 8pm BRT) — 3 dias + 1 dia overlap
- Purge: 07:00 diario (soft-delete, 12 dias retention)

**Concurrency:** 5 UFs paralelas, 2s delay entre batches, max 50 paginas por (UF, modalidade).

### 3.4 Classificacao LLM

A classificacao IA opera em 4 niveis no `llm_arbiter.py`:

| Nivel | Densidade Keywords | Fonte | Acao |
|-------|-------------------|-------|------|
| Alta | >5% | "keyword" | ACCEPT direto |
| Media | 2-5% | "llm_standard" | LLM arbiter SIM/NAO |
| Baixa | 1-2% | "llm_conservative" | LLM arbiter conservador |
| Zero | 0% | "llm_zero_match" | LLM zero-match YES/NO |

**Modelo:** GPT-4.1-nano (33% mais barato que gpt-4o-mini)
- Custo: ~R$0.00007/classificacao (structured output)
- Latencia: ~60ms/chamada
- Timeout: 5s (5x p99)
- Max tokens structured: 800 (evita JSON truncation)
- Cache: LRU in-memory MD5-based (evita chamadas duplicadas)

**Fallback:** Quando LLM falha:
- `LLM_FALLBACK_PENDING_ENABLED=true`: PENDING_REVIEW (gray zone + zero-match)
- `LLM_FALLBACK_PENDING_ENABLED=false`: REJECT hard

**Item Inspection (D-01):** Para items na "gray zone", o sistema inspeciona items individuais da licitacao via API PNCP de itens, com concurrency 5 e timeout 5s/item.

### 3.5 Estrategia de Cache (SWR)

Implementada em `search_cache.py` (2.564 LOC), a estrategia usa 3 niveis com Stale-While-Revalidate:

```
┌───────────┬──────┬─────────────┬──────────────────────────────────┐
│ Camada    │ TTL  │ Status      │ Comportamento                    │
├───────────┼──────┼─────────────┼──────────────────────────────────┤
│ L1 Memory │ 4h   │ Fresh 0-4h  │ Serve direto, mais rapido        │
│ L2 Supa   │ 24h  │ Stale 4-24h │ Serve + revalidacao background   │
│ L3 File   │ 24h  │ Emergency   │ Serve apenas se Supabase down    │
└───────────┴──────┴─────────────┴──────────────────────────────────┘
```

**Cache Key:** Inclui setor, UFs, date_from, date_to, modalidades, filtros. STORY-306 adicionou datas ao key para evitar resultados de periodos diferentes.

**Dual-read:** Exact key + legacy key (sem datas) para mitigar thundering herd durante migracao.

**Prioridade:** Hot/warm/cold tiering para otimizar eviction.

### 3.6 SSE Progress Tracking

O modulo `progress.py` (888 LOC) implementa tracking em tempo real com dois modos:

1. **Redis Streams** (producao, multi-worker): Append-only log com replay para cross-worker SSE. Migrado de Pub/Sub (STORY-276) que perdia eventos fire-and-forget.

2. **In-memory fallback** (single instance): `asyncio.Queue` quando Redis indisponivel.

**Fluxo:**
```
POST /buscar → SearchPipeline emite ProgressEvents → Redis Streams
GET /buscar-progress/{id} (SSE) → Le do Redis Stream → Server-Sent Events
```

**Resiliencia SSE:**
- `bodyTimeout(0)` + heartbeat 15s > Railway idle 60s
- Inactivity timeout: 120s
- Last-Event-ID resumption (STORY-297): replay ate 200 eventos
- Frontend fallback: simulacao baseada em tempo se SSE falhar

### 3.7 Background Jobs (ARQ)

O sistema usa ARQ para processamento assincrono via `job_queue.py` (2.229 LOC):

**Separacao Web/Worker:** Controlada por `PROCESS_TYPE` em `start.sh`:
- Web: `gunicorn main:app` — atende requests HTTP
- Worker: `arq job_queue.WorkerSettings` — executa background jobs

**Jobs registrados:**
- `llm_summary_job`: Gera resumo executivo LLM (post-search)
- `excel_generation_job`: Gera planilha Excel estilizada
- `ingestion_full_crawl_job`: ETL completo diario
- `ingestion_incremental_job`: ETL incremental 3x/dia
- `ingestion_purge_job`: Limpeza de registros expirados
- `cache_warming_job`: Pre-aquecimento de cache (STORY-226)
- `trial_email_sequence_job`: Sequencia de emails trial

**Fallback:** Se Redis/ARQ indisponivel, `is_queue_available()` retorna False e LLM/Excel executam inline (zero regressao).

---

## 4. Superficie API

### 4.1 Rotas de Busca

| Metodo | Rota | Modulo | Proposito |
|--------|------|--------|-----------|
| POST | `/buscar` | `search.py` | Busca principal de licitacoes |
| GET | `/buscar-progress/{id}` | `search_sse.py` | SSE stream de progresso |
| GET | `/v1/search/{id}/status` | `search_status.py` | Status da busca (polling) |
| GET | `/v1/search/{id}/results` | `search_status.py` | Resultados da busca |
| POST | `/v1/search/{id}/retry` | `search_status.py` | Retry de busca falha |
| POST | `/v1/search/{id}/cancel` | `search_status.py` | Cancela busca ativa |

### 4.2 Pipeline (Kanban)

| Metodo | Rota | Modulo | Proposito |
|--------|------|--------|-----------|
| POST | `/pipeline` | `pipeline.py` | Adiciona oportunidade ao pipeline |
| GET | `/pipeline` | `pipeline.py` | Lista items do pipeline |
| PATCH | `/pipeline/{id}` | `pipeline.py` | Move/atualiza item |
| DELETE | `/pipeline/{id}` | `pipeline.py` | Remove item |
| GET | `/pipeline/alerts` | `alerts.py` | Alertas de prazo/atualizacao |

### 4.3 Billing & Subscriptions

| Metodo | Rota | Modulo | Proposito |
|--------|------|--------|-----------|
| GET | `/plans` | `plans.py` | Lista planos disponiveis |
| POST | `/checkout` | `billing.py` | Cria sessao Stripe Checkout |
| POST | `/billing-portal` | `billing.py` | Porta para billing portal Stripe |
| GET | `/subscription/status` | `subscriptions.py` | Status da subscription ativa |
| POST | `/webhooks/stripe` | `stripe.py` | Webhook handler Stripe |

### 4.4 User & Auth

| Metodo | Rota | Modulo | Proposito |
|--------|------|--------|-----------|
| GET | `/me` | `user.py` | Perfil do usuario autenticado |
| POST | `/change-password` | `user.py` | Alterar senha |
| GET | `/trial-status` | `user.py` | Status do trial (dias restantes) |
| PUT | `/profile/context` | `user.py` | Atualizar contexto (setor, UFs) |
| GET | `/auth/google` | `auth_oauth.py` | Inicio OAuth Google |
| GET | `/auth/google/callback` | `auth_oauth.py` | Callback OAuth |
| POST | `/auth/email/login` | `auth_email.py` | Login por email |
| POST | `/auth/email/signup` | `auth_email.py` | Cadastro por email |
| POST | `/auth/mfa/setup` | `mfa.py` | Setup MFA TOTP |

### 4.5 Analytics & Feedback

| Metodo | Rota | Modulo | Proposito |
|--------|------|--------|-----------|
| GET | `/analytics/summary` | `analytics.py` | Resumo de uso |
| GET | `/analytics/searches-over-time` | `analytics.py` | Historico de buscas |
| GET | `/analytics/top-dimensions` | `analytics.py` | Top UFs/setores |
| POST | `/feedback` | `feedback.py` | Feedback de relevancia |
| DELETE | `/feedback/{id}` | `feedback.py` | Remove feedback |
| GET | `/admin/feedback/patterns` | `feedback.py` | Analise de padroes |

### 4.6 Outros

| Metodo | Rota | Modulo | Proposito |
|--------|------|--------|-----------|
| GET | `/health` | `health_core.py` | Health check (dependencias) |
| GET | `/health/cache` | `health.py` | Status do cache |
| GET | `/metrics` | middleware | Prometheus metrics (token auth) |
| GET | `/sessions` | `sessions.py` | Historico de buscas |
| POST | `/conversations` | `messages.py` | Criar conversa |
| GET | `/setores` | `sectors_public.py` | Lista setores disponiveis |
| POST | `/onboarding/first-analysis` | `onboarding.py` | Primeira analise trial |
| GET | `/admin/search-trace/{id}` | `admin_trace.py` | Trace de busca (admin) |
| GET | `/admin/feature-flags` | `feature_flags.py` | Lista feature flags |

---

## 5. Diagramas de Fluxo de Dados

### 5.1 Fluxo de Busca Principal

```
Usuario (Frontend)
    │
    ├── POST /buscar ──────────────────────────┐
    │                                           ▼
    │   ┌─────────── SearchPipeline ───────────────────────┐
    │   │ 1. VALIDATE: UFs, datas, setor, rate limit       │
    │   │ 2. PREPARE: keywords do setor, config            │
    │   │ 3. EXECUTE:                                      │
    │   │    ├── Cache hit? → serve + SWR background       │
    │   │    ├── DATALAKE_QUERY? → query_datalake() (SQL)  │
    │   │    └── Fallback → multi-source API fetch         │
    │   │        ├── PNCP (priority 1)                     │
    │   │        ├── PCP v2 (priority 2)                   │
    │   │        └── ComprasGov (priority 3)               │
    │   │ 4. FILTER: UF → valor → keywords → density      │
    │   │ 5. ENRICH: viability, status, urgencia           │
    │   │ 6. POST_FILTER_LLM: zero-match classification   │
    │   │ 7. GENERATE: LLM resumo + Excel (ou ARQ job)    │
    │   │ 8. PERSIST: cache + DB                           │
    │   └──────────────────────────────────────────────────┘
    │                    │
    │                    ▼
    │              BuscaResponse (JSON)
    │
    └── GET /buscar-progress/{id} (SSE) ──> ProgressEvents
```

### 5.2 Fluxo de Ingestao

```
ARQ Cron Scheduler
    │
    ├── 05:00 UTC (diario) ──> ingestion_full_crawl_job
    │   │
    │   ▼
    │   crawl_full()
    │   ├── Para cada UF (5 paralelas):
    │   │   └── Para cada modalidade (6):
    │   │       └── crawl_uf_modalidade()
    │   │           ├── AsyncPNCPClient._fetch_page_async() (ate 50 paginas)
    │   │           ├── transform_batch() → normaliza para schema pncp_raw_bids
    │   │           └── bulk_upsert() → RPC upsert_pncp_raw_bids (500 rows/batch)
    │   └── save_checkpoint() + complete_ingestion_run()
    │
    ├── 11/17/23 UTC ──> ingestion_incremental_job
    │   └── crawl_incremental() (mesma logica, 3 dias + overlap)
    │
    └── 07:00 UTC ──> ingestion_purge_job
        └── purge_old_bids() (soft-delete >12 dias)
```

### 5.3 Fluxo de Classificacao LLM

```
Lista de licitacoes (pos-fetch)
    │
    ▼
filter/core.py: aplicar_todos_filtros()
    │
    ├── UF check (fail-fast)
    ├── Value range check
    ├── Keyword matching + density scoring
    │   │
    │   ├── density > 5% → ACCEPT (source: "keyword")
    │   ├── density 2-5% → LLM arbiter standard
    │   ├── density 1-2% → LLM arbiter conservative
    │   └── density 0% → LLM zero-match (se habilitado)
    │       │
    │       ▼
    │   llm_arbiter.py: classify_bid()
    │   ├── Check MD5 cache (in-memory)
    │   ├── GPT-4.1-nano API call (5s timeout)
    │   │   └── Structured output: {classe, confianca, evidencias, motivo_exclusao}
    │   ├── Sucesso: SIM/NAO com score
    │   └── Falha: PENDING_REVIEW ou REJECT (config)
    │
    ├── Status/date validation
    └── Viability assessment (4 fatores, post-filter)
```

---

## 6. Arquitetura de Seguranca

### 6.1 Autenticacao & Autorizacao

- **Supabase Auth** com JWT (ES256+JWKS): validacao local sem API call (rapida e confiavel)
- **Token cache L1/L2**: OrderedDict LRU (1000 entries, 60s TTL) + Redis (5min TTL, shared entre workers)
- **RLS (Row Level Security)**: Ativo em todas as tabelas Supabase — dados isolados por usuario
- **Role check**: `is_admin` e `is_master` para endpoints administrativos
- **OAuth**: Google login + Google Sheets export
- **MFA**: TOTP com bcrypt hashing de recovery codes (STORY-317)

### 6.2 Rate Limiting

- **Token bucket** via Redis + in-memory fallback:
  - Search: 10 req/min por usuario
  - Auth: 5 req/5min por IP
  - Signup: 3 req/10min por IP
  - SSE: max 3 conexoes simultaneas, 10 reconnects/60s

### 6.3 Input Validation

- **Pydantic v2** em todos os endpoints: validacao tipada com pattern matching para datas
- **Zod** no frontend: validacao client-side de formularios
- **CORS**: Configuravel via `CORS_ORIGINS`
- **Log sanitization**: `log_sanitizer.py` mascara tokens, user IDs, e dados sensiveis

### 6.4 Protecao de APIs Externas

- **Circuit breakers**: 15 failures threshold, 60s cooldown (PNCP, PCP, ComprasGov)
- **Bulkhead pattern**: Semaforos por fonte (concurrency isolation) — evita que uma fonte degradada afete as outras
- **Stripe webhook verification**: Signature check em todos os webhooks
- **API keys em env vars**: Nunca commitados no codigo

### 6.5 Quota & Billing

- **Atomic quota check**: `check_and_increment_quota_atomic()` — single DB transaction (TOCTOU prevention)
- **Fail-open on CB**: Se circuit breaker aberto, permite busca e loga para reconciliacao
- **Grace period**: 3 dias apos expiracao de subscription
- **Trial paywall**: Apos dia 7, limita a 10 resultados e 5 pipeline items

---

## 7. Observabilidade

### 7.1 Metricas (Prometheus)

Definidas em `metrics.py` (1.037 LOC) com graceful degradation (no-op se prometheus_client ausente):

| Categoria | Metricas Exemplares |
|-----------|-------------------|
| Search | `SEARCH_DURATION`, `ACTIVE_SEARCHES`, `SEARCHES`, `BIDS_PROCESSED_TOTAL` |
| Cache | `CACHE_HITS`, `CACHE_MISSES`, `ARBITER_CACHE_SIZE` |
| LLM | `LLM_CALLS`, `LLM_DURATION`, `LLM_FALLBACK_REJECTS_TOTAL` |
| Sources | `FETCH_DURATION`, `API_ERRORS`, `SOURCES_BIDS_FETCHED`, `SOURCE_DEGRADATION_TOTAL` |
| Bulkhead | `BULKHEAD_ACQUIRE_TIMEOUT`, `SOURCE_ACTIVE_REQUESTS`, `SOURCE_POOL_EXHAUSTED` |
| Ingestion | `INGESTION_RECORDS_FETCHED`, `INGESTION_RECORDS_UPSERTED`, `INGESTION_RUN_DURATION` |
| Auth | `AUTH_CACHE_EVICTIONS` |
| Rate Limit | Counters por endpoint |

Endpoint: `GET /metrics` (protegido por `METRICS_TOKEN`).

### 7.2 Logging Estruturado

- **Producao**: JSON format via `python-json-logger` com campos: timestamp, level, logger_name, request_id, search_id, correlation_id
- **Desenvolvimento**: Text format com request_id
- **Request ID**: `RequestIDFilter` middleware injeta UUID em todos os logs
- **Sanitizacao**: `log_sanitizer.py` mascara tokens e PII automaticamente
- **SECURITY**: DEBUG logs suprimidos em producao (Issue #168)

### 7.3 Distributed Tracing (OpenTelemetry)

- **Tracer**: `telemetry.py` com init no startup (antes da criacao do FastAPI app)
- **Sampling**: 10% default (configuravel via `OTEL_SAMPLING_RATE`)
- **Instrumentacao**: FastAPI + httpx automaticos
- **Spans customizados**: `pipeline.validate`, `pipeline.fetch`, `pipeline.filter`, etc.
- **No-op mode**: Zero overhead quando `OTEL_EXPORTER_OTLP_ENDPOINT` nao configurado

### 7.4 Error Tracking (Sentry)

- **SDK**: `sentry-sdk[fastapi]` com integracao automatica
- **Centralized error reporting**: `utils/error_reporting.py` padroniza emissao de erros
- **Environment-aware**: DSN configuravel, sampling em producao

### 7.5 Health Checks

- `GET /health`: Status geral com checks de: database, cache, Redis, PNCP API canary
- **PNCP cron canary**: Task periodica que testa conectividade com PNCP API
- **Recovery epoch**: Incrementa quando PNCP transiciona degraded/down → healthy (CRIT-056)
- **3 estados**: `healthy`, `degraded`, `unhealthy`

---

## 8. Divida Tecnica Identificada

### 8.1 Critica

| ID | Descricao | Impacto | Arquivo |
|----|-----------|---------|---------|
| DEBT-301 | `filter/core.py` com 4.105 LOC — funcao `aplicar_todos_filtros()` monolitica | Dificulta manutencao, testes isolados, e debug. Decomposicao iniciada (filter_*.py) mas core.py ainda e o maior arquivo. | `filter/core.py` |
| CRIT-SIGSEGV | Restricoes de C extensions por SIGSEGV intermitente em producao | Impede uso de uvloop, limita upgrades de cryptography, requer testes manuais de fork-safety | `requirements.txt`, `gunicorn_conf.py` |

### 8.2 Alta

| ID | Descricao | Impacto | Arquivo |
|----|-----------|---------|---------|
| DEBT-115 | `search_cache.py` com 2.564 LOC — logica multi-level complexa | Dificil de testar e manter. Cache key migration (STORY-306) adicionou dual-read complexity | `search_cache.py` |
| DEBT-015 | `pncp_client.py` com 2.559 LOC — sync + async em um arquivo | Client legado com sync fallback, circuit breaker, retry logic, tudo no mesmo modulo | `pncp_client.py` |
| -- | `cron_jobs.py` com 2.251 LOC — multiplas responsabilidades | Cache cleanup, PNCP canary, session cleanup, cache warming, trial emails — tudo junto | `cron_jobs.py` |
| -- | `job_queue.py` com 2.229 LOC — pool management + worker settings + jobs | Mistura configuracao ARQ, gerenciamento de pool Redis, e definicoes de jobs | `job_queue.py` |

### 8.3 Media

| ID | Descricao | Impacto | Arquivo |
|----|-----------|---------|---------|
| -- | Duplicacao filter_*.py (raiz) vs filter/ (pacote) | Arquivos legados na raiz (`filter_keywords.py`, `filter_llm.py`, etc.) coexistem com pacote `filter/`. Imports indiretos via `filter/__init__.py` | Raiz backend |
| DEBT-103 | LLM timeout hardcoded em multiplos locais | OpenAI timeout em llm_arbiter.py + config separado. Nem sempre consistente | `llm_arbiter.py`, `config/features.py` |
| -- | 99 migrations Supabase | Volume alto de migrations sugere schema evolving rapidamente. Pode impactar deploy time | `supabase/migrations/` |
| -- | Feature flag sprawl: 30+ flags sem governance | Flags acumuladas ao longo do tempo. Sem processo de deprecacao ou cleanup | `config/features.py` |
| -- | `schemas/` directory com 12 files + `schemas_stats.py` + `schema_contract.py` na raiz | Schemas espalhados entre diretorio e raiz | Backend raiz |

### 8.4 Baixa

| ID | Descricao | Impacto | Arquivo |
|----|-----------|---------|---------|
| -- | Backward-compat shims em `main.py` | Re-exports para testes legados. Funcional mas adiciona indiracao | `main.py` |
| -- | `portal_transparencia_client.py` (938 LOC) sem evidencia de uso ativo | Client parece ser preparacao futura ou experimental | `clients/portal_transparencia_client.py` |
| -- | `querido_diario_client.py` e `qd_extraction.py` em clients/ | Integracao com Querido Diario aparenta ser experimental | `clients/` |
| -- | Dual-hash transition em auth.py | Window de 1h para compatibilidade de cache keys. Pode ser removido apos estabilizacao | `auth.py` |

---

## 9. Pontos Fortes da Arquitetura

### 9.1 Resiliencia Exemplar

O sistema demonstra maturidade significativa em resiliencia:
- **Circuit breakers** em todas as fontes externas com cooldown configuravel
- **Bulkhead pattern** isola fontes de dados com semaforos independentes
- **Graceful degradation** em todos os niveis: cache fallback, LLM fallback, source fallback
- **Fail-open policy** para billing (CB open permite busca com log para reconciliacao)
- **Multi-level cache** com SWR impede que falhas transientes impactem usuarios

### 9.2 Pipeline Bem Estruturado

- 7 estagios claros com separacao de responsabilidades
- State machine para rastreamento de progresso
- SSE real-time com Redis Streams (at-least-once delivery)
- Timeout chain hierarquico que previne cascading failures

### 9.3 Observabilidade Completa

- Stack completa: Prometheus + OpenTelemetry + Sentry + structured logging
- Request ID propagado em todos os logs
- Metricas granulares por fonte, por estagio, por operacao LLM
- Health checks com canary proativo

### 9.4 Datalake Strategy

- Ingestao periodica desacopla busca de APIs externas instáveis
- Full-text search PostgreSQL com GIN index elimina dependencia de APIs para buscas comuns
- Checkpoint tracking permite crawls resumiveis
- Fallback transparente para live API quando datalake vazio

### 9.5 Seguranca Robusta

- JWT validation local (sem API call) com suporte ES256+JWKS
- RLS em todas as tabelas
- Atomic quota operations (TOCTOU prevention)
- Rate limiting multi-camada (Redis + in-memory fallback)
- Log sanitization automatica

### 9.6 Test Coverage Solida

- 5.131+ testes backend, 2.681+ testes frontend, 60 testes E2E
- Zero-failure policy estrita
- Anti-hang rules com pytest-timeout em todos os testes
- Snapshot testing para contratos API

---

## 10. Recomendacoes

### 10.1 Prioridade Alta

1. **Decompor `filter/core.py` (4.105 LOC):** A funcao `aplicar_todos_filtros()` e o maior gargalo de manutencao. Continuar a decomposicao iniciada com DEBT-301, movendo logica para sub-modulos tematicos. Target: nenhum modulo acima de 500 LOC.

2. **Refatorar `search_cache.py` (2.564 LOC):** Separar logica por camada (L1, L2, L3) em modulos distintos. O modulo mistura logica de InMemory, Redis, Supabase e Local File em um unico arquivo.

3. **Decompor `pncp_client.py` (2.559 LOC):** Separar sync client (legado), async client, circuit breaker, e retry logic em modulos distintos. O `pncp_client_resilient.py` ja existe como tentativa parcial.

### 10.2 Prioridade Media

4. **Governance de feature flags:** Implementar processo de lifecycle (create → active → deprecated → removed) com datas de expiracao. 30+ flags sem cleanup cria "flag debt".

5. **Consolidar filter_*.py:** Resolver a duplicacao entre arquivos na raiz (`filter_keywords.py`, `filter_llm.py`, etc.) e o pacote `filter/`. Os arquivos raiz devem ser removidos ou transformados em re-exports puros.

6. **Decompor `cron_jobs.py` e `job_queue.py`:** Cada cron job e cada tipo de job background deveria estar em seu proprio modulo dentro de `jobs/` (diretorio ja existe).

### 10.3 Prioridade Baixa

7. **Audit de clients/ experimentais:** Avaliar se `portal_transparencia_client.py`, `querido_diario_client.py` e `licitaja_client.py` devem ser mantidos ou movidos para uma branch experimental.

8. **Compactar migrations:** 99 migrations Supabase podem ser squashed em batches para reduzir overhead de deploy. Manter historico original em archive.

9. **Remover dual-hash transition em auth.py:** Apos periodo de estabilizacao, remover logica de compatibilidade que suporta dois formatos de cache key.

10. **Padronizar schemas:** Mover `schemas_stats.py` e `schema_contract.py` da raiz para o diretorio `schemas/`.
