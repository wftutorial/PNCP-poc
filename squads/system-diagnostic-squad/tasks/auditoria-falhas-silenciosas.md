# auditoria-falhas-silenciosas

## Metadata
- agent: auditor-tecnico
- elicit: false
- priority: critical
- estimated_time: 40min
- tools: [Read, Grep, Bash, Supabase CLI, Railway CLI, Backend API]

## Objetivo
Encontrar tudo que esta quebrando sem ninguem saber. Erros engolidos, fallbacks
nao testados, dados inconsistentes, mecanismos de resiliencia que nunca foram acionados.
Se voce nao encontrar nada, desconfie de si mesmo.

## Pre-requisitos
- Acesso ao codebase completo
- Acesso ao Supabase para queries de integridade
- Acesso ao Railway logs
- Acesso ao Redis (cache/circuit state)

## Steps

### Step 1: Exception Handling Audit
**Acao:** Revisar try/except blocks em fluxos criticos
**Arquivos foco:**
- `backend/search_pipeline.py` — orquestracao de busca
- `backend/llm_arbiter.py` — classificacao IA
- `backend/pncp_client.py` — API PNCP
- `backend/pcp_client.py` — API PCP
- `backend/comprasgov_client.py` — API ComprasGov
- `backend/routes/search.py` — endpoint /buscar
- `backend/routes/billing.py` — Stripe webhooks
- `backend/routes/export_sheets.py` — export Excel
**Verificar:**
- [ ] Nenhum `except Exception: pass` ou `except: pass`
- [ ] Todos os except fazem log do erro (logger.error/warning)
- [ ] Nenhum erro critico logado como WARNING (deveria ser ERROR)
- [ ] Fallbacks documentados no except (nao so silenciam)
- [ ] Erros de rede (httpx) tem retry ou fallback explicito
**Evidencia:** Lista de try/except suspeitos com arquivo:linha

### Step 2: Circuit Breaker Integrity
**Acao:** Verificar estado e comportamento dos circuit breakers
**Verificar:**
- [ ] Circuit breaker existe para PNCP, PCP, ComprasGov
- [ ] Estado atual: CLOSED (verificar via Redis ou in-memory)
- [ ] Threshold configurado (15 failures)
- [ ] Cooldown configurado (60s)
- [ ] Se o circuit breaker tripasse agora, o sistema degrada gracefully?
- [ ] Health canary respeita o estado do circuit breaker
**Evidencia:** Config dos circuit breakers + estado atual

### Step 3: Cache Integrity
**Acao:** Verificar L1 (InMemory) e L2 (Supabase) cache
**Verificar:**
- [ ] Cache L1 TTL = 4h (nao servindo dados de ontem)
- [ ] Cache L2 TTL = 24h no Supabase
- [ ] SWR funciona: stale e servido E revalidacao em background dispara
- [ ] Cache key inclui todos os parametros relevantes (setor, UFs, periodo)
- [ ] Cache invalidation funciona (dados frescos substituem stale)
- [ ] Nenhum cenario onde cache serve dados de outro usuario
**Evidencia:** Cache config + key format + TTL verification

### Step 4: Data Integrity (Supabase)
**Acao:** Verificar consistencia dos dados no banco
**Verificar:**
- [ ] Nenhum `search_sessions` sem `user_id` (orfao)
- [ ] Nenhum `pipeline_items` sem `search_session` valido
- [ ] Nenhum `profiles` com `plan_type` NULL
- [ ] `trial_ends_at` coerente com `created_at` para trials
- [ ] RLS ativo em todas as tabelas criticas (profiles, search_sessions, pipeline_items)
- [ ] Nenhum usuario consegue ver dados de outro (RLS test)
**Evidencia:** SQL queries com contagens de anomalias

### Step 5: Webhook Reliability
**Acao:** Verificar Stripe webhooks e email webhooks
**Verificar:**
- [ ] Stripe webhook endpoint configurado e ativo
- [ ] Webhook signature verification implementado
- [ ] Handlers para: checkout.session.completed, customer.subscription.updated/deleted
- [ ] Idempotencia: mesmo webhook 2x nao causa efeito duplicado
- [ ] Se webhook falhar, Stripe retenta e o handler aceita retry
**Evidencia:** Webhook config + handler code review

### Step 6: Race Conditions
**Acao:** Identificar pontos de race condition potencial
**Verificar:**
- [ ] `check_and_increment_quota_atomic` e realmente atomico (SELECT FOR UPDATE ou similar)
- [ ] SSE stream + POST response: e possivel o POST retornar antes do SSE conectar?
- [ ] Duas buscas simultaneas do mesmo usuario: resultados nao se misturam?
- [ ] Pipeline drag-drop rapido: 2 moves em < 1s causa estado inconsistente?
**Evidencia:** Code review dos pontos criticos + analise

### Step 7: Fallback Paths
**Acao:** Verificar que cada fallback declarado funciona
**Verificar:**
- [ ] LLM falha → classificacao defaults para REJECT (zero noise)
- [ ] PNCP down → PCP + ComprasGov compensam
- [ ] ARQ job falha → `gerar_resumo_fallback()` funciona
- [ ] SSE falha → frontend usa time-based simulation
- [ ] Supabase L2 cache falha → sistema continua com L1 only
- [ ] Redis down → sistema continua (degraded mas funcional)
**Evidencia:** Code trace de cada fallback path

## Output
Documento com:
- Findings por severidade: BLOCKER | HIGH | MEDIUM | LOW
- Cada finding: arquivo, linha, descricao, impacto, reproducao
- Fallbacks validados vs nao validados
- Risk score geral: 1-10
- Top 3 riscos para 50 usuarios pagantes
