# GTM-INFRA-001: Eliminar Sync PNCPClient Fallback + Ajustar Circuit Breaker

## Epic
Root Cause — Infraestrutura (EPIC-GTM-ROOT)

## Sprint
Sprint 8: GTM Root Cause — Tier 3

## Prioridade
P2

## Estimativa
8h

## Status
COMPLETED (2026-02-23)

## Descricao

O `PNCPClient` tem fallback sincrono usando `requests.Session` + `time.sleep()` que bloqueia o event loop inteiro do asyncio quando acionado. O circuit breaker tem threshold de 50 falhas — demorando 3-5 minutos para tripar, tempo no qual o sistema fica irresponsivo. O Gunicorn timeout esta em 900s (15 min), muito acima do Railway hard timeout de 120s.

### Situacao Atual

| Componente | Comportamento | Problema |
|------------|---------------|----------|
| `PNCPClient` fallback | `requests.Session` sync | Bloqueia event loop asyncio |
| `time.sleep()` | Backoff sincrono | Bloqueia worker inteiro |
| Circuit breaker threshold | 50 falhas | 3-5min para tripar — muito lento |
| Gunicorn timeout | 900s | Dead code — Railway mata em 120s |
| `start.sh` | `--timeout 900` | Nao reflete realidade |

### Evidencia da Investigacao (Squad Root Cause 2026-02-23)

| Finding | Agente | Descricao |
|---------|--------|-----------|
| ARCH-2 | Architect | Sync fallback bloqueia event loop |
| ARCH-4 | Architect | time.sleep() bloqueia worker |
| ARCH-9 | Architect | Gunicorn timeout 900s e dead code |

## Criterios de Aceite

### Eliminar Sync Fallback

- [x] AC1: `PNCPClient` sync removido OU wrappado em `asyncio.to_thread()` (nao bloqueia event loop)
- [x] AC2: `time.sleep()` substituido por `asyncio.sleep()` em TODO o codebase backend
- [x] AC3: `requests.Session` substituido por `httpx.AsyncClient` no fallback

### Circuit Breaker

- [x] AC4: Threshold reduzido: 50 → 15 falhas
- [x] AC5: Recovery timeout reduzido: proporcional ao novo threshold
- [x] AC6: Circuit breaker state reportado via metrica Prometheus (ja existe `circuit_breaker_degraded`)

### Gunicorn/Railway

- [x] AC7: Gunicorn timeout: 900s → 180s (acima de Railway 120s mas realista)
- [x] AC8: `start.sh` atualizado com timeout correto
- [x] AC9: Documentar em CLAUDE.md que Railway hard timeout e ~120s

## Testes Obrigatorios

```bash
cd backend && pytest -k "test_pncp_client or test_circuit_breaker" --no-coverage
```

- [x] T1: Fallback nao bloqueia event loop (mock async test)
- [x] T2: Circuit breaker tripa apos 15 falhas (nao 50)
- [x] T3: Zero `time.sleep()` no codebase (grep test)
- [x] T4: Gunicorn timeout configurado em 180s

## Arquivos Afetados

| Arquivo | Tipo de Mudanca |
|---------|----------------|
| `backend/pncp_client.py` | Modificar — asyncio.to_thread() no PNCPLegacyAdapter, CB threshold 50→15, cooldown 120→60 |
| `backend/search_pipeline.py` | Modificar — asyncio.to_thread() no sync fallback |
| `backend/start.sh` | Modificar — timeout 900→180 |
| `CLAUDE.md` | Modificar — documentar Railway hard timeout ~120s |
| `backend/tests/test_gtm_infra_001.py` | Novo — 13 testes (T1-T4) |
| `backend/tests/test_crit026_worker_timeout.py` | Modificar — atualizar assertions 900→180 |
| `backend/tests/test_crit034_worker_timeout.py` | Modificar — atualizar assertions 900→180 |
| `backend/tests/test_pncp_hardening.py` | Modificar — atualizar assertions threshold 50→15, cooldown 120→60 |

## Implementacao

### AC1/AC3: Sync Fallback → asyncio.to_thread()
- `search_pipeline.py`: Ambos paths (fallback e non-parallel) agora usam `await asyncio.to_thread(lambda: list(client.fetch_all(...)))`
- `pncp_client.py PNCPLegacyAdapter.fetch()`: Single-UF path agora usa `await asyncio.to_thread()`
- `time.sleep()` dentro do sync PNCPClient e seguro pois roda em thread separada

### AC2: time.sleep() em async code
- Verificado via AST parser: zero `time.sleep()` em funcoes `async def` no codebase
- AsyncPNCPClient ja usa `asyncio.sleep()` em todos os pontos
- Sync code (email_service, item_inspector) roda em threads (ThreadPoolExecutor/threading.Thread)

### AC4/AC5: Circuit Breaker
- `PNCP_CIRCUIT_BREAKER_THRESHOLD`: 50 → 15 (trips em ~30s em vez de ~3min)
- `PNCP_CIRCUIT_BREAKER_COOLDOWN`: 120s → 60s (proporcional)

### AC6: Prometheus
- `circuit_breaker_degraded` gauge ja existia e e setado no trip/recovery

### AC7/AC8: Gunicorn
- `GUNICORN_TIMEOUT` default: 900 → 180

### AC9: Documentacao
- CLAUDE.md atualizado com secao "Railway/Gunicorn Critical Notes"

## Dependencias

| Tipo | Story | Motivo |
|------|-------|--------|
| Depende de | GTM-ARCH-001 | Menos critico apos async job pattern |
| Paralela | GTM-INFRA-002 | Config changes complementam |
