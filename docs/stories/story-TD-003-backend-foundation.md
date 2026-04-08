# STORY-TD-003: Backend Foundation — Alertas, Timeouts e Async

**Story ID:** STORY-TD-003
**Epic:** EPIC-TD-2026
**Phase:** 2 (Foundation)
**Priority:** P1
**Estimated Hours:** 7h
**Agents:** @dev (backend implementation), @devops (Slack webhook setup)

## Objetivo

Corrigir tres problemas operacionais independentes no backend: (1) falha silenciosa do crawler de ingesta sem notificacao, (2) requests morrendo silenciosamente por mismatch de timeout Railway/Gunicorn, (3) envio sequencial de alertas demorando 60-100s para 1000 usuarios. Cada item e independente e pode ser executado em paralelo.

## Acceptance Criteria

- [ ] AC1: Quando `ingestion_runs` registra um run com `status = 'failed'`, uma notificacao e enviada via Slack webhook (ou Sentry alert rule) em ate 5 minutos. Verificavel via registro de teste com `status = 'failed'` e checagem do canal Slack.
- [ ] AC2: `GUNICORN_TIMEOUT` configurado para 110s (< Railway 120s hard limit). Verificavel via `railway variables` mostrando `GUNICORN_TIMEOUT=110`.
- [ ] AC3: Middleware de deteccao de timeout adicionado que registra warning no Sentry quando request atinge 100s (90% do Railway limit). Verificavel via log/metric emitido quando request demora > 100s.
- [ ] AC4: Alert cron usa `asyncio.gather()` com `Semaphore(10)` para envio paralelo de emails. Tempo de processamento de 1000 alertas reduzido de 60-100s para < 15s. Verificavel via metric/log de duracao do cron.
- [ ] AC5: Zero regressions nos testes de backend (5131+ tests passing).

## Tasks

### Ingestion Failure Alerting (TD-061)
- [ ] Task 1: Criar Slack webhook URL para canal de operacoes (ou usar Sentry alert rule se ja configurado).
- [ ] Task 2: Adicionar hook no `ingestion/scheduler.py` ou `cron_jobs.py`: apos cada `ingestion_run` completar, se `status = 'failed'`, enviar POST para Slack webhook com payload contendo: run_id, timestamp, error_message, UFs afetadas.
- [ ] Task 3: Adicionar env var `SLACK_OPS_WEBHOOK_URL` ao `.env.example` e Railway variables.
- [ ] Task 4: Testar com run simulado de falha. Verificar que mensagem chega no Slack.
- [ ] Task 5: Escrever teste unitario mockando httpx.post para o webhook.

### Timeout Alignment (TD-015)
- [ ] Task 6: Alterar `GUNICORN_TIMEOUT` de 180 para 110 no `backend/start.sh` (ou via env var default).
- [ ] Task 7: Criar middleware `TimeoutDetectionMiddleware` em `backend/middleware/` que:
  - Registra timestamp de inicio do request
  - Em background task apos response, se elapsed > 100s, emite warning para Sentry com contexto (endpoint, elapsed_time, user_id)
  - Adiciona header `X-Request-Duration-Ms` no response
- [ ] Task 8: Registrar middleware no `main.py`.
- [ ] Task 9: Atualizar `GUNICORN_TIMEOUT=110` no Railway via `railway variables set`.
- [ ] Task 10: Escrever teste para o middleware (mock request com delay, verificar que warning e emitido > 100s e nao emitido < 100s).

### Alert Cron Async (TD-029)
- [ ] Task 11: Refatorar `send_pipeline_alerts()` (ou funcao equivalente de alert cron) para usar `asyncio.gather()` com `asyncio.Semaphore(10)` em vez de loop sequencial.
- [ ] Task 12: Manter fallback: se gather falhar para um alert individual, logar erro e continuar (nao abortar batch).
- [ ] Task 13: Adicionar metric de duracao do cron (`smartlic_alert_cron_duration_seconds` histogram).
- [ ] Task 14: Escrever teste com 20 mock alerts verificando que sao enviados em paralelo (elapsed time < sequential time).

## Definition of Done

- [ ] Todos os ACs met e verificaveis
- [ ] Backend tests passing (5131+ tests, 0 failures)
- [ ] Novos testes adicionados para cada item (minimo 3 tests)
- [ ] PR reviewed por @architect
- [ ] Slack webhook testado em ambiente real
- [ ] `GUNICORN_TIMEOUT=110` ativo no Railway

## Debt Items Covered

| ID | Item | Hours | Notas |
|----|------|-------|-------|
| TD-061 | Ingestion failure alerting (Slack webhook) | 3 | Independente, no code dependencies |
| TD-015 | Railway 120s vs Gunicorn 180s timeout mismatch | 2 | Silent request death, no Sentry trace |
| TD-029 | Alert cron sequential -> asyncio.gather(10) | 2 | Performance, independent |
| | **Total** | **7h** | |

## Notas Tecnicas

- **TD-061:** Preferir Slack webhook por simplicidade. Alternativa: Sentry alert rule em cima de log pattern `ingestion_run failed`. O webhook e mais confiavel porque nao depende de Sentry estar operacional.
- **TD-015:** O Railway mata requests em 120s sem trace no Sentry. Com `GUNICORN_TIMEOUT=110`, o Gunicorn mata primeiro e registra o timeout. O middleware de deteccao em 100s permite alertar ANTES do timeout real.
- **TD-029:** O `Semaphore(10)` limita a 10 emails simultancos para nao estourar rate limit do Resend (ou outro provider). O `asyncio.gather(*tasks, return_exceptions=True)` permite que falhas individuais nao abortem o batch.
- **Independencia:** Os 3 itens podem ser implementados em PRs separados e mergeados em qualquer ordem.

---

*Story criada em 2026-04-08 por @pm (Morgan). Fase 2 do EPIC-TD-2026.*
