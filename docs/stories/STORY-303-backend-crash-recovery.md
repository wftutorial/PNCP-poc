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

**ATENCAO — Regressao CRIT-010:** O `--preload` foi adicionado em CRIT-010 (2026-02-20) para resolver 404s durante startup: sem preload, workers aceitam trafego antes de completar o import de 65+ modulos Python (~5-15s), causando 404 intermitentes em endpoints validos. **Esta story DEVE resolver o SIGSEGV SEM reintroduzir os 404s de startup.**

## Acceptance Criteria

### Fix Imediato (Restore Service)
- [ ] AC1: Desabilitar `--preload` como default — `start.sh` deve usar `GUNICORN_PRELOAD=false` como default em vez de `true`
- [ ] AC2: Workers inicializam OpenSSL APOS o fork (no proprio worker process, nao no master)
- [ ] AC3: Health check retorna `{"status":"healthy"}` com latencia < 1000ms apos deploy
- [ ] AC4: Busca funcional — `POST /buscar` retorna resultados (nao 502)

### Mitigacao da Regressao CRIT-010 (404s no Startup)
- [ ] AC5: `gunicorn_conf.py` — hook `post_fork` ou `when_ready` que aguarda o primeiro worker registrar rotas antes de aceitar trafego. Alternativas aceitaveis (escolher 1):
  - **Opcao A (recomendada):** `when_ready` hook no gunicorn_conf.py que loga "All workers ready" — combinado com Railway health check grace period de 30s (`backend/railway.toml`) para tolerar 404s transitorios durante boot
  - **Opcao B:** Lazy import do `cryptography` — mover imports de `cryptography` para dentro das funcoes que usam (nao module-level), permitindo manter `--preload` sem SIGSEGV
  - **Opcao C:** `post_fork` hook que re-inicializa OpenSSL no worker context (chamar `cryptography.hazmat.backends.default_backend()` explicitamente pos-fork)
- [ ] AC6: Railway health check grace period configurado: `healthcheckTimeout` >= 30s no `backend/railway.toml` para tolerar startup sem preload
- [ ] AC7: Teste de startup: deploy em ambiente de teste confirma ZERO 404s em health check apos boot completo (validar que CRIT-010 nao regride)

### Validacao da Hipotese
- [ ] AC8: Antes de aplicar em producao, validar o fix via UMA das seguintes formas:
  - Deploy com `GUNICORN_PRELOAD=false` em staging/preview environment no Railway
  - OU: Teste local com `gunicorn main:app -k uvicorn.workers.UvicornWorker -w 2 --timeout 120` (sem --preload) + curl health check
- [ ] AC9: Se o fix nao resolver o SIGSEGV, investigar alternativas (stack trace completo via `faulthandler.enable()`)

### Pin de Seguranca
- [ ] AC10: `cryptography` pinado em versao exata: `cryptography==46.0.5` (pin exato, nao `>=`)
- [ ] AC11: Comentario no `requirements.txt` documentando: "Pin exato — upgrade requer teste de fork-safety com Gunicorn"

### Monitoramento Externo (Crash Detection)
- [ ] AC12: Health check externo configurado (UptimeRobot, Better Stack, ou similar) monitorando `https://api.smartlic.tech/health` a cada 60 segundos
- [ ] AC13: Alerta via email + SMS quando health check falha por 2 checks consecutivos (2 minutos)
- [ ] AC14: Status page publica acessivel (opcional mas recomendado)

### Worker Crash Logging
- [ ] AC15: `gunicorn_conf.py:worker_exit()` loga SIGSEGV (exit code -11) com severidade CRITICAL e captura Sentry
- [ ] AC16: Nenhum worker exit com codigo != 0 passa sem log

### Testes
- [ ] AC17: Teste: Gunicorn inicia sem `--preload` e workers respondem a health check
- [ ] AC18: Teste: `cryptography` import funciona em worker process (JWT decode, HTTPS request)
- [ ] AC19: Testes existentes passando (backend 5131+, frontend 2681+)

## Technical Notes

### Por que desabilitar preload (nao downgrade cryptography)

A tentacao e fazer downgrade de `cryptography` para 43.0.3. Isso resolve o sintoma mas nao a doenca:
1. `cryptography` 43.0.3 tem CVE-2026-26007 (EC Subgroup Attack) — HIGH severity
2. O problema e o `--preload`, nao a versao do cryptography
3. QUALQUER biblioteca C inicializada no master pode causar o mesmo problema no futuro
4. Sem `--preload`, cada worker inicializa suas proprias dependencias — mais seguro, minimal RAM overhead com 2 workers

**Trade-off de memoria:** Com 2 workers (config atual `WEB_CONCURRENCY=2`), desabilitar preload adiciona ~50-80MB de uso de RAM (app carregado 2x em vez de shared). Railway 1GB suporta isso. Se escalar para 4+ workers, reconsiderar.

### CRIT-010 e o risco de regressao

CRIT-010 resolveu 404s intermitentes durante startup causados por workers aceitando trafego antes de registrar rotas (5-15s de import chain com 65+ modulos). O `--preload` foi a solucao: carregar tudo no master antes de forkar.

Sem preload, o risco de 404s retorna. Mitigacoes:
1. **Railway health check grace period (30s)** — Railway nao roteia trafego para o container ate o health check passar. Se o boot completa em 15s e o health check grace e 30s, trafego so chega DEPOIS das rotas estarem registradas.
2. **`ready: false` no /health** — CRIT-010 ja adicionou o campo `ready` ao /health (main.py:938-940). Enquanto `_startup_time is None`, retorna `ready: false`. O frontend ja trata isso (frontend/app/api/health/route.ts:101-103).
3. **Lifespan startup gate** — O app ja tem um lifespan startup (main.py:449-459) que seta `_startup_time` apos completar inicializacao. Workers so reportam "ready" DEPOIS disso.

A combinacao dessas 3 camadas (health check grace + ready flag + lifespan gate) torna o `--preload` dispensavel para o proposito de evitar 404s.

### Monitoramento externo

O sistema atual nao tem NENHUMA forma de detectar que o backend caiu exceto usuario reportando. Isso e inaceitavel para qualquer SaaS em producao.

**Referencia:** [Better Stack Health Checks Guide](https://betterstack.com/community/guides/monitoring/health-checks/) — "External Synthetic Monitoring provides an outside-in perspective [...] to uncover performance bottlenecks invisible to internal metrics."

**Referencia:** [UptimeRobot 2026 Guide](https://uptimerobot.com/knowledge-hub/monitoring/ultimate-guide-to-server-monitoring-metrics-tools-and-best-practices/) — "If targeting 99.9% annual uptime for an API, probing more than once a minute is probably unnecessary."

## Rollback Plan

| Condicao | Acao | Tempo |
|----------|------|-------|
| Fix nao resolve SIGSEGV | Reverter `GUNICORN_PRELOAD=true` no Railway + investigar com `faulthandler.enable()` | < 5 min (env var) |
| Fix causa 404s persistentes no startup | Aumentar Railway health check grace period para 60s; se insuficiente, reverter preload + aplicar Opcao B (lazy import) | < 10 min |
| Health check externo falso-positivo | Ajustar threshold de alerta de 2 para 3 checks consecutivos | < 2 min |

## Smoke Test Pos-Deploy

```bash
# 1. Health check basico
curl -s https://api.smartlic.tech/health | jq '.status, .ready'
# Esperado: "healthy", true

# 2. Busca funcional (core value)
curl -s -X POST https://api.smartlic.tech/buscar \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"setor_id":"vestuario","ufs":["SP"],"data_inicio":"2026-02-20","data_fim":"2026-02-27"}' \
  | jq '.total_results'
# Esperado: numero > 0

# 3. Zero SIGSEGV nos ultimos 10 minutos
railway logs --filter "SIGSEGV" | head -5
# Esperado: vazio
```

## Files to Change

| File | Mudanca |
|------|---------|
| `backend/start.sh:24` | Mudar default de `GUNICORN_PRELOAD` de `true` para `false` |
| `backend/requirements.txt:38` | Pin exato: `cryptography==46.0.5` |
| `backend/gunicorn_conf.py` | Adicionar SIGSEGV (code -11) handling em `worker_exit()` + `when_ready` hook |
| `backend/railway.toml` | Health check grace period >= 30s |
| Railway env vars | Set `GUNICORN_PRELOAD=false` (imediato, antes do deploy de codigo) |
| Externo | Configurar UptimeRobot/Better Stack para health check |

## Definition of Done

- [ ] Backend acessivel em producao (health check OK)
- [ ] Busca retorna resultados (core value restaurado)
- [ ] Zero 404s intermitentes durante startup (CRIT-010 nao regride)
- [ ] Monitoramento externo ativo e alertando
- [ ] Zero SIGSEGV nos logs por 24h apos deploy
- [ ] Hipotese validada em staging/local antes de producao
- [ ] Rollback plan documentado e testavel
- [ ] Testes passando
