# HARDEN-024: Saturation Metrics (Connection Pools, Queue Depth)

**Severidade:** MEDIA
**Esforço:** 30 min
**Quick Win:** Nao
**Origem:** Conselho CTO — Pesquisa de Industria (Transloadit Post-Mortem, Google SRE Book)

## Contexto

Redis connection exhaustion foi invisível no post-mortem da Transloadit (Sept 2025) porque apenas success-path era monitorado. SmartLic precisa de métricas de saturação para prever falhas antes que aconteçam.

## Critérios de Aceitação

- [ ] AC1: Gauge `smartlic_redis_pool_connections_used` (ativo)
- [ ] AC2: Gauge `smartlic_redis_pool_connections_max` (configurado)
- [ ] AC3: Gauge `smartlic_httpx_pool_connections_used` por source
- [ ] AC4: Gauge `smartlic_tracker_active_count` (trackers ativos)
- [ ] AC5: Gauge `smartlic_background_results_count` (results em memória)
- [ ] AC6: Background task reporta métricas a cada 30s
- [ ] AC7: Dashboard Grafana template (opcional)

## Arquivos Afetados

- `backend/metrics.py` — novos gauges
- `backend/redis_pool.py` — expor pool stats
- `backend/progress.py` — tracker count
- `backend/routes/search.py` — background results count
