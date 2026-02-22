# CRIT-023 — OpenTelemetry Tracing Nunca Ativado em Producao (trace_id = "-")

**Tipo:** Observabilidade / Debt
**Prioridade:** P1 (Sem tracing fim-a-fim, debug de incidentes e cego)
**Criada:** 2026-02-22
**Status:** Concluído
**Origem:** Investigacao P0 — trace_id e span_id aparecem como "-" em todos os logs
**Dependencias:** Nenhuma
**Estimativa:** S (configuracao + verificacao)
**Commits:** `0798453`, `d5be97d`, `f2c770e`, `e88e991`, `73c8819`, `b426ed9`, `7e0dfb7`, `8c2e221`

---

## Problema

O codigo de tracing OpenTelemetry esta implementado (`telemetry.py`, `middleware.py`) mas **nunca foi ativado em producao**.

### Cadeia Causal

1. `config.py:62-66`: `OTEL_EXPORTER_OTLP_ENDPOINT` nao esta setado em producao
2. `telemetry.py:64-66`: Sem endpoint, `_noop = True` — tracing fica em modo noop
3. `telemetry.py:191-204` (`get_trace_id()`): Retorna `None` quando `_noop = True`
4. `telemetry.py:207-217` (`get_span_id()`): Retorna `None` quando `_noop = True`
5. `middleware.py:38-45`: `record.trace_id = get_trace_id() or "-"` — sempre "-"

### Impacto

- **Sem tracing fim-a-fim** — impossivel correlacionar request → fetch → filter → LLM
- **Debug de incidentes** depende apenas de `correlation_id` (gerado por request, sem propagacao cross-service)
- **PNCP latency** invisivel — nao ha spans para medir tempo de cada chamada API
- **LLM calls** nao rastreadas — impossivel ver tempo de resposta do GPT-4.1-nano por classificacao

### Infra Existente

- Prometheus metrics ja ativo (CRIT-E03, commit `056e5dd`)
- Grafana Cloud Free Tier documentado em `docs/guides/metrics-setup.md`
- Railway suporta env vars via `railway variables set`

---

## Solucao

### Abordagem: Configurar OTEL_EXPORTER_OTLP_ENDPOINT no Railway

### Criterios de Aceitacao

- [x] **AC1:** `OTEL_EXPORTER_OTLP_ENDPOINT` configurado no Railway para backend service — `https://otlp-gateway-prod-sa-east-1.grafana.net/otlp` + `OTEL_EXPORTER_OTLP_HEADERS` com Basic auth (instanceId 1534562, token `smartlic-backend-otel`)
- [x] **AC2:** `OTEL_SERVICE_NAME=smartlic-backend` configurado
- [x] **AC3:** `.env.example` documentado com as variaveis OTEL
- [x] **AC4:** Logs em producao mostram `trace_id` e `span_id` reais (nao "-") — validado 2026-02-22 (`trace_id="c14c624189d1913254eb24f01c5e73ec"`)
- [x] **AC5:** Grafana Cloud recebendo traces — zero erros de export OTLP, BatchSpanProcessor ativo
- [x] **AC6:** Verificar que tracing nao degrada performance (sampling rate adequado) — OTEL_SAMPLING_RATE=0.1 configurado

### Verificacao Pos-Deploy

- [x] `railway logs` mostra trace_id != "-" nos logs — confirmado 2026-02-22
- [x] Grafana Cloud recebendo traces (zero export errors) — confirmado 2026-02-22
- [ ] Latencia do endpoint `/buscar` nao aumenta com tracing ativo — monitorar proximo dias

---

## Arquivos Envolvidos

| Arquivo | Mudanca |
|---|---|
| `.env.example` | Documentar OTEL_EXPORTER_OTLP_ENDPOINT, OTEL_EXPORTER_OTLP_HEADERS, OTEL_SERVICE_NAME, OTEL_SAMPLING_RATE |
| `backend/telemetry.py` | HTTP/protobuf exporter (was gRPC), SDK auto-read env vars, `instrument_fastapi_app()` (was class-level `instrument()`) |
| `backend/middleware.py` | CorrelationIDMiddleware convertido de BaseHTTPMiddleware → pure ASGI (preserva contextvar OTel) |
| `backend/main.py` | `init_tracing()` antes de app creation + `instrument_fastapi_app(app)` apos todos middleware |
| `backend/tests/test_telemetry.py` | Fix mock: gRPC exporter paths → HTTP/protobuf paths |
| `backend/requirements.txt` | Switch `opentelemetry-exporter-otlp-proto-grpc` → `opentelemetry-exporter-otlp-proto-http` |
| Railway env vars | 4 OTEL vars configuradas (ENDPOINT, HEADERS, SERVICE_NAME, SAMPLING_RATE) |

---

## Notas de Implementacao

- Grafana Cloud Free Tier inclui 50GB traces/mes — suficiente para volume atual
- Sampling rate 10% (`OTEL_SAMPLING_RATE=0.1`) para controlar volume
- **Middleware ordering critico:** OTel ASGI middleware deve ser outermost (adicionado por ultimo via `instrument_app(app)` apos todos `add_middleware()`) para que o span context esteja ativo quando CorrelationIDMiddleware loga requests
- **BaseHTTPMiddleware quebra OTel:** Starlette's BaseHTTPMiddleware cria novo asyncio.Task para dispatch(), que nao herda contextvars do OTel. Pure ASGI middleware roda no mesmo task.
- `FastAPIInstrumentor().instrument()` (class-level) adiciona middleware como innermost — span morre antes do log. `instrument_app(app)` (instance-level, chamado por ultimo) adiciona como outermost — span vive durante todo o request lifecycle.
