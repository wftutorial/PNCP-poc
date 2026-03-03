# CRIT-051: Railway Worker Logging — stderr→stdout para Severidade Correta

**Status:** 🔴 Pendente
**Prioridade:** P1 — Importante (observabilidade)
**Sprint:** Atual
**Criado:** 2026-03-03
**Depende de:** CRIT-050 AC4-AC5

## Contexto

O CRIT-044 corrigiu os logs do Gunicorn (processo web) redirecionando de stderr para stdout.
O processo ARQ worker nunca recebeu a mesma correção. Python `logging.StreamHandler()` default usa `sys.stderr`.
Railway classifica TUDO em stderr como severidade "error" (vermelho), causando ruído nos logs.

### Sintomas no Railway

```
00:00:00:   1.01s → cron:cache_refresh_job()
00:00:00:   0.00s ← cron:cache_refresh_job ● {'status': 'disabled', 'cycle_id': '41bc556b'}
```

Estas linhas são INFO mas aparecem como ERROR (vermelho) porque saem em stderr.

## Acceptance Criteria

- [ ] AC1: `_worker_on_startup()` chama `setup_logging()` de config.py
- [ ] AC2: `arq_log_config` dict criado em job_queue.py com `"stream": "ext://sys.stdout"`
- [ ] AC3: `start.sh` passa `--custom-log-dict job_queue.arq_log_config` ao ARQ
- [ ] AC4: `_cache_refresh_loop()` em cron_jobs.py respeita `CACHE_REFRESH_ENABLED`
- [ ] AC5: Logs do worker aparecem como INFO (branco) no Railway após deploy
- [ ] AC6: Teste unitário verifica que `arq_log_config` usa `ext://sys.stdout`

## Referências

- [Railway Log Level Detection](https://docs.railway.com/reference/logging) — stderr = error
- [Python StreamHandler](https://docs.python.org/3/library/logging.handlers.html) — default = stderr
- `backend/gunicorn_conf.py:29-40` — documentação do fix para Gunicorn (CRIT-044)

## Arquivos Afetados

- `backend/job_queue.py` — arq_log_config + setup_logging em _worker_on_startup
- `backend/start.sh` — --custom-log-dict flag
- `backend/cron_jobs.py` — CACHE_REFRESH_ENABLED check
