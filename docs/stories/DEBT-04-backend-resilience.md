# DEBT-04: Backend Resilience (Timeouts + Alerts + Async)

**Epic:** EPIC-TD-2026
**Fase:** 2 (Foundation)
**Horas:** 7h
**Agente:** @dev + @devops
**Prioridade:** P1

## Debitos Cobertos

| TD | Item | Horas |
|----|------|-------|
| TD-015 | Railway 120s vs Gunicorn 180s timeout mismatch — silent request death | 2h |
| TD-029 | Alert cron sequential -> asyncio.gather(10) | 2h |
| TD-061 | Ingestion failure alerting (Slack webhook) | 3h |

## Acceptance Criteria

- [ ] AC1: `GUNICORN_TIMEOUT=110` (< Railway 120s) configurado
- [ ] AC2: Middleware de timeout detection logando requests que excedem 100s
- [ ] AC3: Alert cron usa `asyncio.gather` com `Semaphore(10)` — 10x mais rapido
- [ ] AC4: Falha em `ingestion_runs` envia notificacao Slack/Sentry
- [ ] AC5: Testes de integracao para alert cron async

## Notas

- TD-015: Requests que excedem Railway 120s morrem sem trace no Sentry. Alinhar timeout previne isso.
- TD-029: Para 1000 alertas, reduz de 60-100s (sequencial) para ~10s (paralelo).
- TD-061: Hoje se o crawl diario falha, ninguem percebe ate usuario reclamar.
