# STORY-303: Backend Crash Recovery & Startup Resilience

**Sprint:** EMERGENCY — Pre-requisite for all other stories
**Size:** M (4-6h)
**Root Cause:** Diagnostic Report 2026-02-27 — BLOCKER B1 (SIGSEGV crash loop)
**Depends on:** None (blocker — must be first)
**Blocks:** STORY-304, STORY-305, STORY-306, STORY-307

## Contexto

O backend SmartLic esta em crash loop (SIGSEGV) em producao desde 2026-02-27. Workers Gunicorn completam startup e crasham imediatamente ao processar o primeiro request. Nenhuma funcionalidade do sistema esta acessivel — busca, login, billing, pipeline, tudo morto.

**Causa raiz identificada:** `cryptography>=46.0.5` + Gunicorn `--preload` causa inicializacao do OpenSSL no processo master (pre-fork). Quando workers sao forked, o estado OpenSSL no processo filho e invalido — resultando em SIGSEGV no primeiro uso de crypto (JWT validation, HTTPS, Stripe).

**Evidencia:**
- Railway logs: Workers PID 4-249+ ciclando, `SIGSEGV` imediatamente apos "startup complete"
- `backend/start.sh:24`: `GUNICORN_PRELOAD` defaults to `true`
- `backend/requirements.txt:38`: `cryptography>=46.0.5`
- Health check: `{"backend":"unreachable","latency_ms":5001}`

**Fundamentacao tecnica:**
- [Gunicorn Issue #2761](https://github.com/benoitc/gunicorn/issues/2761): Fork-without-exec causa SIGSEGV quando bibliotecas C sao inicializadas no master pre-fork
- [Gunicorn Issue #2890](https://github.com/benoitc/gunicorn/issues/2890): Discussao explicita sobre fork-before-preload e problemas de fork safety
- [Python Issue #42891](https://bugs.python.org/issue42891): Segfault com Gunicorn e bibliotecas com Cython bindings (mesmo padrao)
- [CVE-2026-26007](https://www.openwall.com/lists/oss-security/2026/02/10/4): Fix de seguranca que motivou upgrade para cryptography 46.0.5
- [Gunicorn Docs](https://docs.gunicorn.org/en/stable/2010-news.html): "preload loads application code before workers are forked"

**Principio violado:** Gunicorn preload e um trade-off memoria/estabilidade. Com `--preload`, o app e carregado no master e forked para workers — economiza RAM mas assume que TODAS as bibliotecas sao fork-safe. OpenSSL (via cryptography) NAO e fork-safe quando inicializado antes do fork.

## Acceptance Criteria

### Fix Imediato (Restore Service)
- [ ] AC1: Desabilitar `--preload` como default — `start.sh` deve usar `GUNICORN_PRELOAD=false` como default em vez de `true`
- [ ] AC2: Workers inicializam OpenSSL APOS o fork (no proprio worker process, nao no master)
- [ ] AC3: Health check retorna `{"status":"healthy"}` com latencia < 1000ms apos deploy
- [ ] AC4: Busca funcional — `POST /buscar` retorna resultados (nao 502)

### Pin de Seguranca
- [ ] AC5: `cryptography` pinado em versao exata compativel com fork: `cryptography==46.0.5` (pin exato, nao `>=`)
- [ ] AC6: Comentario no `requirements.txt` documentando: "Pin exato — upgrade requer teste de fork-safety com Gunicorn"

### Monitoramento Externo (Crash Detection)
- [ ] AC7: Health check externo configurado (UptimeRobot, Better Stack, ou similar) monitorando `https://api.smartlic.tech/health` a cada 60 segundos
- [ ] AC8: Alerta via email + SMS quando health check falha por 2 checks consecutivos (2 minutos)
- [ ] AC9: Status page publica acessivel (opcional mas recomendado)

### Worker Crash Logging
- [ ] AC10: `gunicorn_conf.py:worker_exit()` loga SIGSEGV (exit code -11) com severidade CRITICAL e captura Sentry
- [ ] AC11: Nenhum worker exit com codigo != 0 passa sem log

### Testes
- [ ] AC12: Teste: Gunicorn inicia sem `--preload` e workers respondem a health check
- [ ] AC13: Teste: `cryptography` import funciona em worker process (JWT decode, HTTPS request)
- [ ] AC14: Testes existentes passando (backend 5131+, frontend 2681+)

## Technical Notes

### Por que desabilitar preload (nao downgrade cryptography)

A tentacao e fazer downgrade de `cryptography` para 43.0.3. Isso resolve o sintoma mas nao a doenca:
1. `cryptography` 43.0.3 tem CVE-2026-26007 (EC Subgroup Attack) — HIGH severity
2. O problema e o `--preload`, nao a versao do cryptography
3. QUALQUER biblioteca C inicializada no master pode causar o mesmo problema no futuro
4. Sem `--preload`, cada worker inicializa suas proprias dependencias — mais seguro, minimal RAM overhead com 2 workers

**Trade-off de memoria:** Com 2 workers (config atual `WEB_CONCURRENCY=2`), desabilitar preload adiciona ~50-80MB de uso de RAM (app carregado 2x em vez de shared). Railway 1GB suporta isso. Se escalar para 4+ workers, reconsiderar.

### Monitoramento externo

O sistema atual nao tem NENHUMA forma de detectar que o backend caiu exceto usuario reportando. Isso e inaceitavel para qualquer SaaS em producao.

**Referencia:** [Better Stack Health Checks Guide](https://betterstack.com/community/guides/monitoring/health-checks/) — "External Synthetic Monitoring provides an outside-in perspective [...] to uncover performance bottlenecks invisible to internal metrics."

**Referencia:** [UptimeRobot 2026 Guide](https://uptimerobot.com/knowledge-hub/monitoring/ultimate-guide-to-server-monitoring-metrics-tools-and-best-practices/) — "If targeting 99.9% annual uptime for an API, probing more than once a minute is probably unnecessary."

## Files to Change

| File | Mudanca |
|------|---------|
| `backend/start.sh:24` | Mudar default de `GUNICORN_PRELOAD` de `true` para `false` |
| `backend/requirements.txt:38` | Pin exato: `cryptography==46.0.5` |
| `backend/gunicorn_conf.py:57-77` | Adicionar SIGSEGV (code -11) handling em `worker_exit()` |
| Railway env vars | Adicionar `GUNICORN_PRELOAD=false` (imediato, antes do deploy) |
| Externo | Configurar UptimeRobot/Better Stack para health check |

## Definition of Done

- [ ] Backend acessivel em producao (health check OK)
- [ ] Busca retorna resultados (core value restaurado)
- [ ] Monitoramento externo ativo e alertando
- [ ] Zero SIGSEGV nos logs por 24h apos deploy
- [ ] Testes passando
