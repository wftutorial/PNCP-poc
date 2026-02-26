# STORY-291: Prometheus Alerting Rules & Grafana Dashboard

**Priority:** P1
**Effort:** M (1-2 days)
**Squad:** @devops
**Fundamentacao:** GTM Readiness Audit Track 7 — 34 metricas sem alerting, sem dashboards
**Status:** TODO
**Sprint:** GTM Sprint 3

---

## Contexto

O SmartLic tem 34 Prometheus metrics definidos em `backend/metrics.py` e expostos em `/metrics`, mas nenhum sistema de scraping, dashboarding ou alerting esta confirmado ativo em producao.

---

## Acceptance Criteria

### AC1: Deploy Grafana Agent ou scraper
- [ ] Configurar Grafana Cloud free tier (ou alternativa)
- [ ] Deploy Grafana Agent para scrape `/metrics` a cada 15s
- [ ] Autenticar com METRICS_TOKEN (configurar se vazio)
- [ ] Confirmar dados aparecendo no Grafana Cloud

### AC2: Dashboard "SmartLic Operations"
- [ ] Panel: Search Latency (P50, P95, P99) — histogram
- [ ] Panel: Cache Hit Rate — counter ratio
- [ ] Panel: Error Rate by Source (PNCP, PCP, ComprasGov) — counter
- [ ] Panel: Circuit Breaker State — gauge
- [ ] Panel: Active Searches — gauge
- [ ] Panel: LLM Call Duration & Cost — histogram + counter
- [ ] Panel: Searches per Hour — counter rate
- [ ] Panel: Filter Decisions (accept/reject by stage) — counter

### AC3: Alerting rules (5 criticos)
- [ ] `HighErrorRate`: `rate(smartlic_api_errors_total[5m]) > 0.05` → email + push
- [ ] `HighLatency`: `histogram_quantile(0.95, smartlic_search_duration_seconds) > 120` → email
- [ ] `CircuitBreakerOpen`: `smartlic_circuit_breaker_degraded > 0` por 5min → email + push
- [ ] `LowCacheHitRate`: cache ratio < 30% por 15min → email
- [ ] `NoSearchesReceived`: `rate(smartlic_searches_total[30m]) == 0` durante business hours → email

### AC4: Notification channels
- [ ] Email: tiago.sasaki@gmail.com (ja configurado)
- [ ] Opcionalmente: Telegram bot ou Slack webhook
- [ ] Documentar em `docs/runbooks/monitoring-alerting-setup.md`

---

## Arquivos Impactados

| Arquivo | Mudanca |
|---------|---------|
| Railway env vars | METRICS_TOKEN |
| Grafana Cloud | Agent config, dashboards, alerts |
| `docs/runbooks/monitoring-alerting-setup.md` | Update with actual config |
| `docs/operations/monitoring.md` | Update status |
