# STORY-286: Observability Production Activation

**Priority:** P1
**Effort:** M (1-2 days)
**Squad:** @devops + @dev
**Fundamentacao:** GTM Readiness Audit Track 7 — OTEL desabilitado, metricas sem scraper, alerting ausente
**Status:** TODO
**Sprint:** GTM Sprint 1

---

## Contexto

O audit revelou que apesar de ter 34 Prometheus metrics definidos, 7 pipeline spans instrumentados, e Sentry configurado, a observabilidade esta efetivamente inativa em producao:

- OTEL_EXPORTER_OTLP_ENDPOINT provavelmente vazio
- Nenhum Prometheus scraper confirmado ativo
- 34 metricas coletadas mas sem dashboards ou alerting
- METRICS_TOKEN possivelmente vazio (endpoint publico)
- On-call unico com email-only

---

## Acceptance Criteria

### AC1: Confirm and fix OTEL endpoint
- [ ] Verificar `railway variables` se OTEL_EXPORTER_OTLP_ENDPOINT esta configurado
- [ ] Se vazio: configurar Grafana Cloud OTLP endpoint (free tier) ou similar
- [ ] Verificar que traces aparecem no backend de tracing
- [ ] Se nao for prioridade, documentar como "disabled by design" e remover do health check

### AC2: Activate Prometheus scraping
- [ ] Configurar Grafana Agent ou Prometheus scraper apontando para `/metrics`
- [ ] Definir METRICS_TOKEN em Railway para autenticar o endpoint
- [ ] Criar dashboard basico no Grafana com:
  - Search latency P50/P95/P99
  - Cache hit rate
  - Error rate por source
  - Circuit breaker state
  - Active searches gauge
  - LLM call duration e cost

### AC3: Configure basic alerting rules
- [ ] Alert: `smartlic_api_errors_total` rate > 5% por 5min
- [ ] Alert: `smartlic_search_duration_seconds` P95 > 120s por 10min
- [ ] Alert: `smartlic_circuit_breaker_degraded == 1` por qualquer source por 5min
- [ ] Alert: `smartlic_cache_hits_total / (hits + misses) < 30%` por 15min
- [ ] Alerts enviados para email + (opcionalmente) Slack ou Telegram

### AC4: Set up basic on-call
- [ ] Configurar PagerDuty free tier ou Grafana OnCall
- [ ] SMS/push notification para alertas P0
- [ ] Documentar escalation path (mesmo que single-person)
- [ ] Atualizar `docs/runbooks/monitoring-alerting-setup.md`

### AC5: Fix stale Vercel references in runbooks
- [ ] `docs/runbooks/monitoring-alerting-setup.md`: substituir referencias a Vercel por Railway
- [ ] Verificar outros runbooks por referencias desatualizadas

---

## Arquivos Impactados

| Arquivo | Mudanca |
|---------|---------|
| Railway env vars | OTEL_EXPORTER_OTLP_ENDPOINT, METRICS_TOKEN |
| Grafana Cloud | Dashboard + alert rules |
| `docs/runbooks/monitoring-alerting-setup.md` | Fix Vercel refs |
| `docs/operations/monitoring.md` | Update with actual scraper config |
