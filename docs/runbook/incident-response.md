# Runbook de Resposta a Incidentes — SmartLic

**Versão:** 1.0
**Última atualização:** 2026-03-09
**Responsável:** Equipe SmartLic / CONFENGE
**Produto:** SmartLic (https://smartlic.tech)

---

## Índice

1. [Níveis de Severidade](#níveis-de-severidade)
2. [Endpoints de Monitoramento](#endpoints-de-monitoramento)
3. [Feature Flags para Mitigação](#feature-flags-para-mitigação)
4. [Incidentes Comuns](#incidentes-comuns)
   - [INC-01: Indisponibilidade da API PNCP](#inc-01-indisponibilidade-da-api-pncp)
   - [INC-02: Timeout / Exaustão do Pool de Conexões Supabase](#inc-02-timeout--exaustão-do-pool-de-conexões-supabase)
   - [INC-03: Redis Indisponível](#inc-03-redis-indisponível)
   - [INC-04: Alta Taxa de Erros (Alertas Sentry)](#inc-04-alta-taxa-de-erros-alertas-sentry)
   - [INC-05: Timeout do Search Pipeline (>120s Railway)](#inc-05-timeout-do-search-pipeline-120s-railway)
   - [INC-06: Quota/Rate Limit da OpenAI (LLM)](#inc-06-quotarate-limit-da-openai-llm)
   - [INC-07: Falhas de Webhook Stripe](#inc-07-falhas-de-webhook-stripe)
   - [INC-08: Pico de Memória/CPU no Railway](#inc-08-pico-de-memóriacpu-no-railway)
   - [INC-09: Frontend 504 Timeout](#inc-09-frontend-504-timeout)
   - [INC-10: Falha de Migração de Banco](#inc-10-falha-de-migração-de-banco)
5. [Contatos e Dashboards](#contatos-e-dashboards)
6. [Template Pós-Incidente](#template-pós-incidente)

---

## Níveis de Severidade

| Nível | Nome | Descrição | Tempo de Resposta | Exemplos |
|-------|------|-----------|-------------------|----------|
| **P0** | Indisponibilidade Total | Sistema completamente inacessível ou dados corrompidos | **Imediato** (< 15 min) | Supabase fora, Railway deploy quebrado, dados de billing corrompidos |
| **P1** | Degradação Maior | Funcionalidade core comprometida, maioria dos usuários afetada | **< 30 min** | PNCP circuit breaker aberto, Redis fora, pipeline de busca falhando |
| **P2** | Degradação Menor | Funcionalidade secundária comprometida, poucos usuários afetados | **< 2 horas** | LLM classificação falhando (fallback ativo), uma fonte secundária fora |
| **P3** | Cosmético / Baixo Impacto | Problema visual, log excessivo, métricas inconsistentes | **< 24 horas** | Banner de cache exibido indevidamente, Sentry ruído excessivo |

### Critérios de Escalonamento

- P2 sem resolução em 4h → escalar para P1
- P1 sem resolução em 2h → escalar para P0
- Qualquer incidente afetando billing/pagamentos → automaticamente P0

---

## Endpoints de Monitoramento

| Endpoint | Método | Propósito | Auth |
|----------|--------|-----------|------|
| `GET /health/live` | GET | Liveness probe — sempre retorna 200 | Nenhuma |
| `GET /health/ready` | GET | Readiness probe — verifica Redis + Supabase | Nenhuma |
| `GET /health` | GET | Health completo com componentes (Redis, Supabase, ARQ, circuit breakers) | Nenhuma |
| `GET /health/cache` | GET | Status do cache (L1 InMemory + L2 Supabase) | Auth |
| `GET /health/tasks` | GET | Status de tarefas background (ARQ) | Auth |
| `GET /sources/health` | GET | Health individual de cada fonte (PNCP, Portal, ComprasGov) com latência | Nenhuma |
| `GET /metrics` | GET | Métricas Prometheus (requer `METRICS_TOKEN`) | Token |
| `GET /status` | GET | Status page público (uptime, incidentes recentes) | Nenhuma |

### Comandos de Diagnóstico Rápido

```bash
# Health check completo
curl -s https://api.smartlic.tech/health | python -m json.tool

# Verificar liveness
curl -s https://api.smartlic.tech/health/live

# Verificar readiness (Redis + Supabase)
curl -s https://api.smartlic.tech/health/ready

# Health das fontes de dados
curl -s https://api.smartlic.tech/sources/health | python -m json.tool

# Logs em tempo real no Railway
railway logs --tail

# Status do deploy
railway status

# Variáveis de ambiente
railway variables
```

---

## Feature Flags para Mitigação

Feature flags são a forma mais rápida de mitigar incidentes sem deploy. Altere via `railway variables set FLAG=value`.

| Flag | Default | Propósito de Mitigação |
|------|---------|----------------------|
| `LLM_ARBITER_ENABLED` | `true` | Desabilitar classificação LLM (usa apenas keywords) |
| `LLM_ZERO_MATCH_ENABLED` | `true` | Desabilitar zero-match LLM (rejeita itens sem match) |
| `LLM_ZERO_MATCH_BATCH_ENABLED` | `true` | Desabilitar batching de zero-match |
| `SYNONYM_MATCHING_ENABLED` | `true` | Desabilitar matching por sinônimos |
| `VIABILITY_ASSESSMENT_ENABLED` | `true` | Desabilitar avaliação de viabilidade |
| `ITEM_INSPECTION_ENABLED` | `true` | Desabilitar inspeção de itens (gray zone) |
| `COMPRASGOV_ENABLED` | `false` | Habilitar/desabilitar fonte ComprasGov |
| `PCP_ENABLED` | `true` | Habilitar/desabilitar fonte PCP v2 |
| `HEALTH_CANARY_ENABLED` | `true` | Desabilitar canary de health check |
| `CACHE_WARMING_ENABLED` | `false` | Habilitar/desabilitar warming de cache |
| `SEARCH_ASYNC_ENABLED` | `false` | Habilitar busca assíncrona (ARQ) |
| `RATE_LIMITING_ENABLED` | `true` | Desabilitar rate limiting |
| `TRIAL_PAYWALL_ENABLED` | `true` | Desabilitar paywall de trial |
| `SHOW_CACHE_FALLBACK_BANNER` | `true` | Ocultar banner de fallback de cache |
| `LLM_FALLBACK_PENDING_ENABLED` | `true` | Desabilitar fallback pending para LLM |
| `PARTIAL_DATA_SSE_ENABLED` | `true` | Desabilitar SSE de dados parciais |

### Como alterar feature flags em produção

```bash
# Via Railway CLI (requer redeploy)
railway variables set LLM_ARBITER_ENABLED=false

# Feature flags com TTL de 60s são re-lidos automaticamente do ambiente
# Mas variáveis de ambiente no Railway exigem redeploy para tomar efeito
railway up
```

---

## Incidentes Comuns

---

### INC-01: Indisponibilidade da API PNCP

**Severidade:** P1 (PNCP é a fonte primária, priority=1)

#### Sintomas

- **Usuários veem:** Resultados de busca reduzidos ou apenas de fontes secundárias (PCP, ComprasGov). Banner de degradação no frontend.
- **Logs mostram:**
  ```
  Supabase circuit breaker: CLOSED → OPEN
  PNCP circuit breaker is in degraded state
  PNCPDegradedError
  ```
- **Health check:** `GET /sources/health` retorna `status: "unhealthy"` para PNCP
- **Métricas:** `circuit_breaker_state{source="pncp"}` = 1 (OPEN)

#### Diagnóstico

```bash
# 1. Verificar status do circuit breaker
curl -s https://api.smartlic.tech/health | python -m json.tool | grep -A5 pncp

# 2. Verificar se a API PNCP responde diretamente
curl -s -o /dev/null -w "%{http_code}" \
  "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao?dataInicial=20260301&dataFinal=20260301&codigoModalidadeContratacao=6&pagina=1&tamanhoPagina=10"

# 3. Verificar logs de erro no Railway
railway logs --tail | grep -i "pncp\|circuit_breaker"

# 4. Verificar métricas de latência
curl -s https://api.smartlic.tech/metrics -H "Authorization: Bearer $METRICS_TOKEN" | grep pncp
```

#### Resolução

1. **Se a API PNCP está fora do ar** (confirmado pelo curl direto):
   - **Ação:** Aguardar. O circuit breaker tem cooldown de 60s (`PNCP_CIRCUIT_BREAKER_COOLDOWN`). Após o cooldown, 3 chamadas de teste (HALF_OPEN) serão feitas automaticamente.
   - O sistema já serve resultados das fontes secundárias (PCP v2, ComprasGov) + cache stale.
   - **Nenhuma ação necessária** — o fallback cascade é automático.

2. **Se a API PNCP responde mas o circuit breaker está aberto** (falso positivo):
   - Provavelmente a API retornou muitos erros transitórios.
   - **Ação:** Aguardar o cooldown de 60s para auto-recovery via HALF_OPEN.
   - Se persistir, verificar se `tamanhoPagina` mudou (PNCP já reduziu silenciosamente de 500→50):
     ```bash
     curl -s -o /dev/null -w "%{http_code}" \
       "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao?dataInicial=20260301&dataFinal=20260301&codigoModalidadeContratacao=6&pagina=1&tamanhoPagina=50"
     ```

3. **Se a API PNCP retorna HTTP 400 para `tamanhoPagina=50`**:
   - O PNCP reduziu o limite de página novamente.
   - **Ação:** Atualizar `PNCP_BATCH_SIZE` no config e fazer deploy.

#### Feature Flags de Mitigação

```bash
# Nenhum flag necessário — fallback cascade é automático
# Se quiser forçar apenas fontes secundárias temporariamente:
railway variables set PNCP_CIRCUIT_BREAKER_THRESHOLD=1
railway up
```

#### Configurações do Circuit Breaker

| Variável | Default | Descrição |
|----------|---------|-----------|
| `PNCP_CIRCUIT_BREAKER_THRESHOLD` | 15 | Falhas para abrir o CB |
| `PNCP_CIRCUIT_BREAKER_COOLDOWN` | 60s | Tempo em OPEN antes de testar HALF_OPEN |
| `PCP_CIRCUIT_BREAKER_THRESHOLD` | 15 | Mesmo para PCP v2 |
| `PCP_CIRCUIT_BREAKER_COOLDOWN` | 60s | Mesmo para PCP v2 |
| `COMPRASGOV_CIRCUIT_BREAKER_THRESHOLD` | 15 | Mesmo para ComprasGov |
| `COMPRASGOV_CIRCUIT_BREAKER_COOLDOWN` | 60s | Mesmo para ComprasGov |

---

### INC-02: Timeout / Exaustão do Pool de Conexões Supabase

**Severidade:** P0 (afeta todo o sistema — auth, cache, pipeline, billing)

#### Sintomas

- **Usuários veem:** Erros 500, login falhando, buscas retornando erro, pipeline inacessível.
- **Logs mostram:**
  ```
  CRIT-046: Supabase pool > 80% utilization: 22/25 active
  Supabase circuit breaker: CLOSED → OPEN
  CircuitBreakerOpenError: Supabase circuit breaker is OPEN
  ConnectionError in sb_execute, retrying
  ```
- **Health check:** `GET /health/ready` retorna HTTP 503 com `supabase: { status: "down" }`
- **Métricas:** `supabase_pool_active` próximo de `SUPABASE_POOL_MAX_CONNECTIONS` (25)

#### Diagnóstico

```bash
# 1. Verificar readiness
curl -s https://api.smartlic.tech/health/ready | python -m json.tool

# 2. Verificar pool utilization nas métricas
curl -s https://api.smartlic.tech/metrics -H "Authorization: Bearer $METRICS_TOKEN" \
  | grep -E "supabase_pool_active|supabase_execute_duration|supabase_cb_state"

# 3. Verificar estado do circuit breaker Supabase
curl -s https://api.smartlic.tech/health | python -m json.tool | grep -A3 supabase

# 4. Verificar conexões no Supabase Dashboard
# → Dashboard > Database > Connections

# 5. Logs do Railway
railway logs --tail | grep -i "supabase\|pool\|circuit"
```

#### Resolução

1. **Pool esgotado temporariamente (pico de tráfego):**
   - O circuit breaker do Supabase abre automaticamente (window=10, threshold=50% falhas).
   - Cooldown de 60s, depois HALF_OPEN com 3 chamadas de teste.
   - **Ação imediata:** Aumentar pool se necessário:
     ```bash
     railway variables set SUPABASE_POOL_MAX_CONNECTIONS=40
     railway variables set SUPABASE_POOL_MAX_KEEPALIVE=15
     railway up
     ```

2. **Supabase fora do ar:**
   - Verificar [status.supabase.com](https://status.supabase.com)
   - **Ação:** Aguardar recovery. O sistema usa cache L1 (InMemory) para buscas recentes.
   - Auth ficará indisponível (sem workaround local).

3. **Connection pool leak (conexões não são devolvidas):**
   - Sintoma: pool fica em 100% mesmo sem tráfego.
   - **Ação:** Restart do serviço:
     ```bash
     railway up  # Redeploy força restart do processo
     ```

#### Feature Flags de Mitigação

```bash
# Reduzir carga no Supabase desabilitando funcionalidades que fazem queries
railway variables set CACHE_WARMING_ENABLED=false
railway variables set HEALTH_CANARY_ENABLED=false  # Canary usa sb_execute_direct
railway up
```

#### Configurações Relevantes

| Variável | Default | Descrição |
|----------|---------|-----------|
| `SUPABASE_POOL_MAX_CONNECTIONS` | 25 | Conexões máximas por worker |
| `SUPABASE_POOL_MAX_KEEPALIVE` | 10 | Keep-alive connections |
| `SUPABASE_POOL_TIMEOUT` | 30s | Timeout total da query |

---

### INC-03: Redis Indisponível

**Severidade:** P1

#### Sintomas

- **Usuários veem:** Buscas mais lentas (sem cache L1), rate limiting pode não funcionar. Resultados ainda retornam via fontes ao vivo + cache L2 (Supabase).
- **Logs mostram:**
  ```
  Redis pool unavailable
  ConnectionError: Redis connection refused
  ```
- **Health check:** `GET /health/ready` retorna `redis: { status: "down" }`

#### Diagnóstico

```bash
# 1. Verificar readiness
curl -s https://api.smartlic.tech/health/ready | python -m json.tool

# 2. Verificar logs de Redis
railway logs --tail | grep -i redis

# 3. Verificar variável REDIS_URL
railway variables | grep REDIS

# 4. Testar conexão Redis diretamente (se tiver acesso)
railway run python -c "import redis; r = redis.from_url('$REDIS_URL'); print(r.ping())"
```

#### Resolução

1. **Redis do Upstash/Railway fora:**
   - Verificar status do provedor (Upstash dashboard ou Railway dashboard).
   - O sistema degrada graciosamente — cache L1 InMemory ainda funciona (por worker, 4h TTL).
   - Cache L2 Supabase ainda funciona para persistência.
   - Rate limiting fica sem efeito (permite todas as requests).

2. **REDIS_URL incorreta ou expirada:**
   ```bash
   # Verificar e atualizar URL
   railway variables | grep REDIS_URL
   # Se usando Upstash, gerar nova URL no dashboard
   railway variables set REDIS_URL="redis://..."
   railway up
   ```

3. **Redis com memória cheia:**
   - Verificar no dashboard do provedor.
   - Redis com `maxmemory-policy: allkeys-lru` evicta chaves automaticamente.

#### Feature Flags de Mitigação

```bash
# Desabilitar funcionalidades que dependem fortemente de Redis
railway variables set RATE_LIMITING_ENABLED=false
railway variables set CACHE_WARMING_ENABLED=false
railway up
```

---

### INC-04: Alta Taxa de Erros (Alertas Sentry)

**Severidade:** P1 ou P2 (depende do tipo de erro)

#### Sintomas

- **Sentry:** Alerta de spike de erros ou novo issue com alto volume.
- **Métricas:** `http_requests_total{status="5xx"}` crescendo.
- **Usuários:** Podem ou não perceber, dependendo se os erros são em background (cron, worker) ou em requests.

#### Diagnóstico

```bash
# 1. Verificar Sentry (via browser — link abaixo)
# Analisar: error type, stack trace, breadcrumbs, tags (source, endpoint)

# 2. Verificar logs no Railway
railway logs --tail | grep -i "error\|exception\|traceback"

# 3. Verificar métricas de erro
curl -s https://api.smartlic.tech/metrics -H "Authorization: Bearer $METRICS_TOKEN" \
  | grep -E "http_requests_total.*5xx|errors_total"

# 4. Verificar health geral
curl -s https://api.smartlic.tech/health | python -m json.tool
```

#### Resolução

1. **Identificar a raiz pelo stack trace no Sentry:**
   - Filtrar por tag `source` para identificar se é PNCP, PCP, ComprasGov, LLM, etc.
   - Verificar se é um erro novo (regressão de deploy) ou recorrente.

2. **Se for regressão de deploy:**
   ```bash
   # Rollback para o commit anterior
   git log --oneline -5  # Identificar commit anterior
   git revert HEAD
   git push origin main  # Trigger CI/CD
   ```

3. **Se for erro de API externa (PNCP, OpenAI, Stripe):**
   - Verificar o incidente específico (INC-01, INC-06, INC-07).
   - Circuit breakers devem mitigar automaticamente.

4. **Se for erro de schema/migração:**
   - Erros `PGRST205` (tabela não encontrada) ou `PGRST204` (coluna não encontrada).
   - Esses erros **não** disparam o circuit breaker do Supabase (excluídos via `_is_schema_error`).
   - **Ação:** Aplicar migração pendente (ver INC-10).

#### Feature Flags de Mitigação

Depende do tipo de erro. Desabilitar a feature que está causando erros:

```bash
# Exemplo: se LLM arbiter está causando erros
railway variables set LLM_ARBITER_ENABLED=false
railway up
```

---

### INC-05: Timeout do Search Pipeline (>120s Railway)

**Severidade:** P1

#### Sintomas

- **Usuários veem:** Busca trava e retorna erro 504 ou resultado vazio após longa espera.
- **Logs mostram:**
  ```
  search pipeline timeout
  asyncio.TimeoutError
  # Ou simplesmente — Railway mata o request sem log
  ```
- **Railway:** Request cortado pelo proxy em ~120s (hard timeout).
- **Nota:** O timeout chain do sistema é: Pipeline(360s) > Consolidation(300s) > PerSource(180s) > PerUF(30s) > PerModality(20s) > HTTP(10s). Porém o Railway proxy corta em ~120s.

#### Diagnóstico

```bash
# 1. Verificar logs de timeout
railway logs --tail | grep -i "timeout\|TimeoutError\|504"

# 2. Verificar latência das fontes
curl -s https://api.smartlic.tech/sources/health | python -m json.tool
# Verificar response_time_ms de cada fonte

# 3. Verificar métricas de duração de busca
curl -s https://api.smartlic.tech/metrics -H "Authorization: Bearer $METRICS_TOKEN" \
  | grep -E "search_duration|pipeline_duration"

# 4. Verificar se é busca com muitas UFs (causa batching demorado)
railway logs --tail | grep "batch\|UF"
```

#### Resolução

1. **Buscas com muitas UFs (>10 UFs):**
   - O sistema faz batching de UFs (PNCP_BATCH_SIZE=5, delay=2s entre batches).
   - Com 27 UFs: 6 batches × 2s delay + tempo de request = pode exceder 120s.
   - **Mitigação imediata:**
     ```bash
     railway variables set PNCP_BATCH_SIZE=8  # Reduz batches
     railway variables set PNCP_BATCH_DELAY_S=1.0  # Reduz delay
     railway up
     ```

2. **PNCP respondendo lento (>10s por request):**
   - Verificar `/sources/health` — se PNCP latency > 5000ms, a API está sobrecarregada.
   - O per-modality timeout (20s) e per-UF timeout (30s) devem limitar.
   - **Ação:** Reduzir timeout para falhar mais rápido:
     ```bash
     railway variables set PNCP_TIMEOUT_PER_MODALITY=10
     railway up
     ```

3. **Busca assíncrona (recomendado para buscas grandes):**
   - O sistema suporta POST `/buscar` → 202 + SSE via `GET /buscar-progress/{id}`.
   - Frontend já usa esse pattern. Verificar se SSE está funcionando.

4. **Gunicorn timeout:**
   ```bash
   # Aumentar timeout do Gunicorn (default 180s, deve ser > Railway 120s)
   railway variables set GUNICORN_TIMEOUT=180
   railway up
   ```

#### Feature Flags de Mitigação

```bash
# Desabilitar funcionalidades que adicionam tempo ao pipeline
railway variables set LLM_ZERO_MATCH_ENABLED=false  # Economiza até 30s
railway variables set ITEM_INSPECTION_ENABLED=false  # Economiza até 15s
railway variables set VIABILITY_ASSESSMENT_ENABLED=false  # Economiza tempo
railway up
```

---

### INC-06: Quota/Rate Limit da OpenAI (LLM)

**Severidade:** P2 (fallback automático para keywords-only)

#### Sintomas

- **Usuários veem:** Resultados sem classificação LLM (apenas keyword match). Resumos com fallback genérico.
- **Logs mostram:**
  ```
  OpenAI rate limit exceeded
  openai.RateLimitError
  openai.APIError: 429
  Quota exceeded for model gpt-4.1-nano
  ```
- **Métricas:** `llm_errors_total{type="rate_limit"}` crescendo.

#### Diagnóstico

```bash
# 1. Verificar logs de LLM
railway logs --tail | grep -i "openai\|llm\|rate.limit\|quota"

# 2. Verificar uso na OpenAI Dashboard
# https://platform.openai.com/usage

# 3. Verificar métricas
curl -s https://api.smartlic.tech/metrics -H "Authorization: Bearer $METRICS_TOKEN" \
  | grep llm
```

#### Resolução

1. **Rate limit temporário (muitas requests simultâneas):**
   - O sistema tem fallback: `LLM failure → REJECT` (zero noise philosophy).
   - Classificação via keywords continua funcionando.
   - Resumos usam `gerar_resumo_fallback()` (texto genérico).
   - **Ação:** Aguardar rate limit resetar (geralmente 1 minuto).

2. **Quota mensal esgotada:**
   - Verificar usage na dashboard da OpenAI.
   - **Ação:** Aumentar quota ou desabilitar LLM temporariamente:
     ```bash
     railway variables set LLM_ARBITER_ENABLED=false
     railway variables set LLM_ZERO_MATCH_ENABLED=false
     railway up
     ```

3. **API key inválida ou expirada:**
   ```bash
   railway variables | grep OPENAI_API_KEY
   # Gerar nova key em https://platform.openai.com/api-keys
   railway variables set OPENAI_API_KEY=sk-...
   railway up
   ```

#### Feature Flags de Mitigação

```bash
# Desabilitar toda classificação LLM (sistema opera apenas com keywords)
railway variables set LLM_ARBITER_ENABLED=false
railway variables set LLM_ZERO_MATCH_ENABLED=false
railway variables set LLM_ZERO_MATCH_BATCH_ENABLED=false
railway up
# O sistema continua funcional — keywords match é o fallback padrão
```

---

### INC-07: Falhas de Webhook Stripe

**Severidade:** P0 (afeta billing — pode causar downgrade incorreto de planos)

#### Sintomas

- **Usuários reportam:** Plano não atualizado após pagamento. Acesso bloqueado mesmo com assinatura ativa.
- **Stripe Dashboard:** Webhooks com status failed/pending.
- **Logs mostram:**
  ```
  Stripe webhook signature verification failed
  Webhook handler error
  ```
- **Banco:** `profiles.plan_type` desatualizado em relação ao Stripe.

#### Diagnóstico

```bash
# 1. Verificar logs de webhook
railway logs --tail | grep -i "stripe\|webhook\|billing"

# 2. Verificar status dos webhooks no Stripe Dashboard
# https://dashboard.stripe.com/webhooks

# 3. Verificar se STRIPE_WEBHOOK_SECRET está correto
railway variables | grep STRIPE

# 4. Verificar plano do usuário afetado
railway run python -c "
from supabase_client import get_supabase
sb = get_supabase()
r = sb.table('profiles').select('plan_type, email').eq('email', 'user@example.com').execute()
print(r.data)
"
```

#### Resolução

1. **Webhook secret incorreto:**
   ```bash
   # Obter secret correto do Stripe Dashboard > Webhooks > Signing secret
   railway variables set STRIPE_WEBHOOK_SECRET=whsec_...
   railway up
   ```

2. **Webhook URL incorreta após mudança de domínio:**
   - Atualizar no Stripe Dashboard > Webhooks > Endpoint URL.
   - URL deve ser: `https://api.smartlic.tech/webhooks/stripe`

3. **Plano do usuário dessincronizado:**
   - Verificar assinatura no Stripe Dashboard.
   - Atualizar manualmente no banco se necessário:
     ```bash
     railway run python -c "
     from supabase_client import get_supabase
     sb = get_supabase()
     sb.table('profiles').update({'plan_type': 'smartlic_pro'}).eq('email', 'user@example.com').execute()
     "
     ```
   - **IMPORTANTE:** Stripe tem proration automática — nunca implementar código de prorata customizado.

4. **Reprocessar webhooks falhados:**
   - No Stripe Dashboard > Webhooks > selecionar endpoint > Attempted events > Retry.

#### Proteções Existentes

- **Grace period:** 3 dias (`SUBSCRIPTION_GRACE_DAYS`) para gaps de assinatura.
- **Fail to last known plan:** Em caso de erro de DB, nunca faz downgrade para `free_trial`.
- **Frontend cache:** localStorage com TTL de 1h evita UI downgrades temporários.

---

### INC-08: Pico de Memória/CPU no Railway

**Severidade:** P1 se causando OOM kills, P2 se apenas lentidão

#### Sintomas

- **Railway Dashboard:** Gráficos de memória/CPU em vermelho. Container restartando (OOM kill).
- **Usuários veem:** Requests lentos ou 502 Bad Gateway.
- **Logs mostram:**
  ```
  Worker [PID] was killed (SIGKILL) — possible OOM
  ```

#### Diagnóstico

```bash
# 1. Verificar Railway dashboard — gráficos de recursos
railway status

# 2. Verificar métricas de memória (se o endpoint estiver acessível)
curl -s https://api.smartlic.tech/health | python -m json.tool

# 3. Verificar logs de OOM
railway logs --tail | grep -i "kill\|oom\|memory\|signal"

# 4. Verificar se há muitas buscas simultâneas
curl -s https://api.smartlic.tech/metrics -H "Authorization: Bearer $METRICS_TOKEN" \
  | grep -E "concurrent_searches|active_requests"
```

#### Resolução

1. **Pico temporário (muitas buscas simultâneas):**
   - O InMemoryCache pode crescer com muitos resultados.
   - ThreadPoolExecutor(max_workers=10) para LLM pode consumir memória.
   - **Ação:** Reduzir concorrência:
     ```bash
     railway variables set PNCP_BATCH_SIZE=3
     railway variables set ITEM_INSPECTION_CONCURRENCY=3
     railway up
     ```

2. **Memory leak (crescimento contínuo):**
   - Restart resolve temporariamente:
     ```bash
     railway up  # Redeploy
     ```
   - Investigar com profiling em staging.

3. **Escalar o serviço:**
   - No Railway Dashboard, aumentar o plano ou recursos do serviço.

#### Feature Flags de Mitigação

```bash
# Reduzir funcionalidades que consomem memória
railway variables set LLM_ZERO_MATCH_ENABLED=false
railway variables set ITEM_INSPECTION_ENABLED=false
railway variables set CACHE_WARMING_ENABLED=false
railway variables set MAX_ZERO_MATCH_ITEMS=50  # Reduzir de 200
railway up
```

---

### INC-09: Frontend 504 Timeout

**Severidade:** P1

#### Sintomas

- **Usuários veem:** Página de busca trava, loading infinito, erro 504 Gateway Timeout.
- **Browser console:** `504 Gateway Time-out` em `/api/buscar` ou `/api/buscar-progress/`.
- **Nota:** O frontend Next.js faz proxy para o backend. O timeout chain é: FE Proxy(480s) > Railway(~120s).

#### Diagnóstico

```bash
# 1. Verificar se o backend está respondendo
curl -s -o /dev/null -w "%{http_code} %{time_total}s" https://api.smartlic.tech/health/live

# 2. Verificar se é timeout no proxy do frontend ou no backend
# Se /health/live retorna 200 rápido → problema é no pipeline de busca
# Se /health/live também está lento → problema é no backend inteiro

# 3. Verificar SSE stream
curl -s -N https://api.smartlic.tech/buscar-progress/test-id \
  -H "Accept: text/event-stream" --max-time 10

# 4. Verificar logs do frontend (Railway/Vercel)
railway logs --tail  # No serviço do frontend
```

#### Resolução

1. **Backend respondendo mas busca é lenta (>120s):**
   - Ver INC-05 (Timeout do Search Pipeline).
   - SSE heartbeat a cada 15s mantém a conexão viva.
   - Railway idle timeout é 60s — SSE heartbeat deve prevenir isso.

2. **SSE não está funcionando:**
   - Verificar se `bodyTimeout: 0` está configurado no proxy do frontend.
   - SSE inactivity timeout é 120s.
   - **Fallback:** Frontend tem simulação time-based se SSE falhar.

3. **Backend completamente travado:**
   ```bash
   # Restart forçado
   railway up
   ```

4. **Gunicorn keep-alive muito baixo:**
   ```bash
   # Keep-alive deve ser > Railway proxy (60s)
   # Default é 75s — verificar se foi alterado
   railway variables | grep GUNICORN
   railway variables set GUNICORN_KEEPALIVE=75
   railway up
   ```

---

### INC-10: Falha de Migração de Banco

**Severidade:** P1 (pode causar erros PGRST205 e funcionalidades quebradas)

#### Sintomas

- **CI/CD:** Job `migration-check.yml` falhando (exit 1).
- **Logs mostram:**
  ```
  PGRST205: Could not find the relation
  PGRST204: Column not found
  migration pending
  ```
- **Sentry:** Erros `PGRST205` em vários endpoints.
- **Nota:** Erros de schema (`PGRST205`, `PGRST204`, `42703`, `42P01`) são **excluídos** do circuit breaker do Supabase — não causam cascata.

#### Diagnóstico

```bash
# 1. Verificar migrações pendentes
export SUPABASE_ACCESS_TOKEN=$(grep SUPABASE_ACCESS_TOKEN .env | cut -d '=' -f2)
npx supabase db push --dry-run

# 2. Verificar diff de schema
npx supabase db diff

# 3. Listar migrações locais vs remotas
ls -la supabase/migrations/
npx supabase migration list

# 4. Verificar logs de erro de schema
railway logs --tail | grep -i "PGRST205\|PGRST204\|migration"
```

#### Resolução

1. **Migração não foi aplicada (esquecida no deploy):**
   ```bash
   # Aplicar migrações pendentes
   npx supabase link --project-ref fqqyovlzdzimiwfofdjk
   npx supabase db push --include-all

   # Forçar reload do cache do PostgREST
   # (automático via deploy.yml, mas pode ser feito manualmente)
   psql $SUPABASE_DB_URL -c "NOTIFY pgrst, 'reload schema'"
   ```

2. **Migração com erro de SQL:**
   - Verificar o arquivo SQL da migração que falhou.
   - Corrigir o SQL e re-aplicar.
   - Migrações são em `supabase/migrations/` (35 arquivos) e `backend/migrations/` (7 arquivos).

3. **Schema cache do PostgREST desatualizado:**
   ```bash
   # Forçar reload sem re-aplicar migração
   psql $SUPABASE_DB_URL -c "NOTIFY pgrst, 'reload schema'"
   ```

4. **Rollback de migração (último recurso):**
   - Supabase não tem rollback nativo — criar migração reversa manualmente.
   ```bash
   npx supabase migration new rollback_<nome_da_migracao>
   # Editar o arquivo com comandos DROP/ALTER reversos
   npx supabase db push
   ```

#### Proteções Existentes

- **CI de 3 camadas (CRIT-050):**
  1. PR Warning (`migration-gate.yml`) — aviso em PRs com migrações
  2. Push Alert (`migration-check.yml`) — bloqueia se há migrações pendentes
  3. Auto-Apply no Deploy (`deploy.yml`) — aplica automaticamente + reload PostgREST

---

## Contatos e Dashboards

| Recurso | URL/Acesso |
|---------|------------|
| **Railway Dashboard** | [railway.app](https://railway.app) — projeto SmartLic |
| **Supabase Dashboard** | [supabase.com/dashboard](https://supabase.com/dashboard) — projeto `fqqyovlzdzimiwfofdjk` |
| **Sentry** | [sentry.io](https://sentry.io) — projeto SmartLic |
| **Stripe Dashboard** | [dashboard.stripe.com](https://dashboard.stripe.com) |
| **Upstash (Redis)** | [console.upstash.com](https://console.upstash.com) |
| **OpenAI Usage** | [platform.openai.com/usage](https://platform.openai.com/usage) |
| **GitHub Repo** | Repositório PNCP-poc |
| **Status Page** | [smartlic.tech/status](https://smartlic.tech/status) |
| **Health Endpoint** | `https://api.smartlic.tech/health` |
| **Métricas Prometheus** | `https://api.smartlic.tech/metrics` (requer `METRICS_TOKEN`) |

### Responsáveis

| Papel | Contato |
|-------|---------|
| Admin/Engenharia | tiago.sasaki@gmail.com |
| Alertas automáticos | Email via Resend (incidentes), Sentry (erros) |

---

## Template Pós-Incidente

Após cada incidente P0 ou P1 (e opcionalmente P2), documentar em `docs/sessions/YYYY-MM/`:

```markdown
# Post-Mortem: [Título do Incidente]

**Data:** YYYY-MM-DD HH:MM - HH:MM (UTC-3)
**Severidade:** P0/P1/P2
**Duração:** X horas Y minutos
**Impacto:** [Descrição do impacto para usuários]
**Responsável:** [Nome]

## Timeline

| Hora | Evento |
|------|--------|
| HH:MM | Incidente detectado via [Sentry/Health Check/Usuário] |
| HH:MM | Investigação iniciada |
| HH:MM | Causa raiz identificada: [descrição] |
| HH:MM | Mitigação aplicada: [feature flag / rollback / fix] |
| HH:MM | Incidente resolvido. Confirmado por [health check / teste manual] |

## Causa Raiz

[Descrição técnica detalhada da causa raiz]

## Mitigação Aplicada

[O que foi feito para resolver — feature flags, rollback, hotfix, etc.]

## Ações Preventivas

| Ação | Responsável | Prazo | Story |
|------|-------------|-------|-------|
| [Ação 1] | [Nome] | [Data] | STORY-XXX |
| [Ação 2] | [Nome] | [Data] | STORY-XXX |

## Métricas de Impacto

- Requests afetados: X
- Usuários afetados: Y
- Tempo de indisponibilidade: Z min
- Erros no Sentry: N eventos

## Lições Aprendidas

1. [O que funcionou bem]
2. [O que poderia ter sido melhor]
3. [O que faltou em monitoramento/alertas]
```

---

## Checklist Rápido de Resposta

Ao receber um alerta ou report de incidente:

- [ ] Classificar severidade (P0-P3)
- [ ] Verificar `/health` e `/health/ready`
- [ ] Verificar `/sources/health` (se relacionado a busca)
- [ ] Verificar logs no Railway (`railway logs --tail`)
- [ ] Verificar Sentry para stack traces
- [ ] Identificar se há feature flag para mitigação rápida
- [ ] Aplicar mitigação (flag / rollback / restart)
- [ ] Confirmar resolução via health checks
- [ ] Comunicar status aos usuários (se P0/P1)
- [ ] Documentar post-mortem (se P0/P1)
