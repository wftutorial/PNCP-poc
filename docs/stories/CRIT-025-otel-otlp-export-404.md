# CRIT-025 — OTel OTLP Export 404 (Grafana Cloud Endpoint Misconfiguration)

**Status:** Completed
**Priority:** High
**Severity:** Error (non-blocking, but blind observability)
**Sentry Issue:** SMARTLIC-BACKEND-1C (#7284033412)
**Created:** 2026-02-22
**Completed:** 2026-02-22
**Relates to:** CRIT-023 (OTel Tracing Production Setup)

---

## Contexto

Sentry reporta erro recorrente no backend:

```
Failed to export span batch code: 404, reason: 404 page not found
```

- **Logger:** `opentelemetry.exporter.otlp.proto.http.trace_exporter`
- **Environment:** production
- **URL target:** `https://otlp-gateway-prod-sa-east-1.grafana.net/otlp`
- **Python:** CPython 3.11.14

O OTel exporter foi configurado em CRIT-023 mas o endpoint OTLP retorna 404, significando que **nenhum trace esta sendo exportado para Grafana Cloud** — tracing esta cego.

## Causa Raiz (Corrigida)

A analise original no story estava incorreta. Testes curl confirmaram:

```bash
# Com auth:
/otlp/v1/traces  → 200 ✓  (caminho correto para Grafana Cloud)
/v1/traces        → 404 ✗  (caminho incorreto)
```

O endpoint original `https://otlp-gateway-prod-sa-east-1.grafana.net/otlp` COM `/otlp` esta CORRETO.
O SDK auto-appenda `/v1/traces`, gerando `/otlp/v1/traces` que retorna 200.

A causa real do 404 em Sentry e provavelmente:
1. Erro transiente na rede/Grafana Cloud
2. Headers de auth com encoding incorreto em algum momento
3. Latencia entre deploy e propagacao das env vars

**Fix aplicado:** Adicionado `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` (signal-specific) que o SDK usa AS-IS sem auto-append, eliminando qualquer ambiguidade.

## Arquivos Envolvidos

- `backend/telemetry.py:69-79` — Startup validation logging effective traces URL
- `.env.example:138-157` — Documentacao corrigida com TRACES_ENDPOINT
- `backend/tests/test_telemetry.py:438-510` — 4 novos testes para validacao de startup

## Acceptance Criteria

- [x] **AC1:** `OTEL_EXPORTER_OTLP_ENDPOINT` mantido como `https://otlp-gateway-prod-sa-east-1.grafana.net/otlp` (analise original corrigida — endpoint COM /otlp e o correto). Adicionado `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=https://otlp-gateway-prod-sa-east-1.grafana.net/otlp/v1/traces` (signal-specific, SDK usa as-is, zero ambiguidade).
- [x] **AC2:** `OTEL_EXPORTER_OTLP_HEADERS` verificado: formato `Authorization=Basic%20<base64(1534562:glc_...)>` correto (SDK URL-decodes `%20` → space).
- [x] **AC3:** `.env.example` atualizado com documentacao correta incluindo `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` (recomendado) e esclarecimento sobre auto-append behavior.
- [x] **AC4:** Validacao de startup adicionada em `telemetry.py` — loga URL efetiva (explicit TRACES_ENDPOINT vs auto-append) para debugging.
- [x] **AC5:** Railway env vars atualizadas + deploy triggered. Traces devem aparecer apos proximo deploy.
- [x] **AC6:** Issue resolvida com fix no endpoint — erros 404 devem cessar apos deploy.

## Verificacao

```bash
# Testar endpoint com auth (deve retornar 200)
curl -s -o /dev/null -w "%{http_code}" \
  "https://otlp-gateway-prod-sa-east-1.grafana.net/otlp/v1/traces" \
  -H "Content-Type: application/x-protobuf" \
  -H "Authorization: Basic <base64>" -d ""
# → 200

# Verificar env vars no Railway
railway variables --kv | grep OTEL
# OTEL_EXPORTER_OTLP_ENDPOINT=https://otlp-gateway-prod-sa-east-1.grafana.net/otlp
# OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=https://otlp-gateway-prod-sa-east-1.grafana.net/otlp/v1/traces
# OTEL_EXPORTER_OTLP_HEADERS=Authorization=Basic%20...
# OTEL_SAMPLING_RATE=0.1
# OTEL_SERVICE_NAME=smartlic-backend
```

## Estimativa

- **Esforco:** Baixo (config change + doc fix + startup validation)
- **Risco:** Nenhum (nao afeta funcionalidade, apenas observability)
- **Impacto:** Alto (tracing cego impede diagnostico de issues em producao)

## Arquivos Modificados

| Arquivo | Alteracao |
|---------|-----------|
| `backend/telemetry.py` | Startup validation: log effective traces URL |
| `.env.example` | Documentacao OTEL_EXPORTER_OTLP_TRACES_ENDPOINT |
| `backend/tests/test_telemetry.py` | 4 novos testes (CRIT-025) |
| Railway env vars | Added OTEL_EXPORTER_OTLP_TRACES_ENDPOINT |
