# jornada-admin-oversight

## Metadata
- agent: admin-operador
- elicit: false
- priority: high
- estimated_time: 25min
- tools: [Supabase CLI, Railway CLI, Sentry, Bash, Read, Grep, Playwright MCP]

## Objetivo
Validar que o operador do sistema tem visibilidade total sobre o que acontece.
Com 50 usuarios pagantes, voce PRECISA saber antes do cliente que algo quebrou.

## Pre-requisitos
- Acesso admin ao SmartLic (tiago.sasaki@gmail.com)
- Acesso ao Sentry project
- Acesso ao Railway dashboard/CLI
- Acesso ao Supabase dashboard/CLI

## Steps

### Step 1: Health Check de Producao
**Acao:** Verificar status atual do sistema
**Verificar:**
- [ ] `GET /health` retorna 200 com detalhes uteis
- [ ] Railway service status: running, sem restarts recentes
- [ ] Worker process (ARQ) rodando separadamente
- [ ] Redis conectado e responsivo
- [ ] Supabase acessivel
- [ ] Circuit breakers: todos CLOSED (nenhuma fonte em falha)
**Evidencia:** Health response + Railway status + Redis PING

### Step 2: Billing Sync Integrity
**Acao:** Verificar que Stripe e Supabase estao sincronizados
**Verificar:**
- [ ] Query: todos os profiles com `plan_type != 'free_trial'` tem subscription ativa no Stripe
- [ ] Nenhum profile com `plan_type = 'free_trial'` que deveria ter expirado (trial_ends_at < now)
- [ ] Grace period (3 dias) respeitado corretamente
- [ ] Webhook handlers funcionando (ultimo evento processado recentemente)
**Evidencia:** SQL query cross-referencing profiles + Stripe subscriptions list

### Step 3: Error Monitoring (Sentry)
**Acao:** Verificar Sentry para erros em producao
**Verificar:**
- [ ] Sentry esta recebendo eventos (nao silenciado)
- [ ] Erros recentes (ultimas 24h) triados
- [ ] Nenhum erro CRITICAL nao resolvido
- [ ] Stack traces nao expoe dados sensiveis (log_sanitizer)
- [ ] Source maps configurados (frontend errors legives)
- [ ] Alert rules configuradas para erros criticos
**Evidencia:** Sentry dashboard screenshot + alert rules list

### Step 4: SLO Dashboard
**Acao:** Verificar SLOs definidos no STORY-299
**Verificar:**
- [ ] Dashboard admin carrega sem erro
- [ ] Metricas exibidas sao atuais (nao stale)
- [ ] SLOs definidos: availability, latency, error rate
- [ ] Se SLO violado, alerta e disparado
- [ ] Dados Prometheus/OpenTelemetry chegando
**Evidencia:** Screenshot dashboard SLO + metricas recentes

### Step 5: Email Alerts (STORY-301)
**Acao:** Verificar sistema de alertas por email
**Verificar:**
- [ ] CRUD de alertas funciona (criar, editar, deletar)
- [ ] Cron job de alertas configurado e executando
- [ ] Dedup de emails funciona (nao manda duplicatas)
- [ ] Unsubscribe link funciona
- [ ] Resend integration ativa e com quota
**Evidencia:** Alert config + cron job status + email delivery log

### Step 6: Cenario de Deteccao de Problema
**Acao:** Simular uma situacao problematica e verificar deteccao
**Verificar:**
- [ ] Se um endpoint retornar 500, Sentry captura em < 1min
- [ ] Se billing desync acontecer, admin teria como detectar
- [ ] Se uma data source cair, circuit breaker tripa e health reflete
- [ ] Existe runbook ou procedimento para cada cenario?
**Evidencia:** Teste de deteccao real ou analise de gaps

## Output
Documento com:
- Status de cada step: PASS | FAIL | DEGRADED
- Visibilidade operacional: COMPLETA | PARCIAL | INSUFICIENTE
- Gaps de monitoramento encontrados
- "Saberia antes do cliente reclamar?" → SIM | NAO | DEPENDE DO CENARIO
