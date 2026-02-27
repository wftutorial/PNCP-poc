# STORY-305: Circuit Breaker Coverage & Threshold Alignment

**Sprint:** CRITICAL — Semana 1 pos-recovery
**Size:** M (4-6h)
**Root Cause:** Diagnostic Report 2026-02-27 — HIGHs H6, H7
**Depends on:** STORY-303 (backend precisa estar de pe)
**Industry Standard:** [Circuit Breaker Pattern — Martin Fowler](https://martinfowler.com/bliki/CircuitBreaker.html), [Resilience4j](https://resilience4j.readme.io/docs/circuitbreaker)

## Contexto

A busca multi-fonte do SmartLic depende de 3 APIs governamentais externas (PNCP, PCP, ComprasGov). Se uma fonte travar, o circuit breaker deve isola-la rapidamente para que as outras continuem servindo resultados. Hoje o ComprasGov NAO TEM circuit breaker e os thresholds entre PNCP e PCP sao inconsistentes sem justificativa tecnica.

**Evidencia da auditoria:**

| Fonte | Circuit Breaker | Threshold | Cooldown | Problema |
|-------|----------------|-----------|----------|----------|
| PNCP | `PNCPCircuitBreaker` | 15 falhas | 60s | OK — threshold adequado |
| PCP | `PNCPCircuitBreaker` (reusado) | 30 falhas | 120s | 2x mais tolerante que PNCP sem justificativa tecnica |
| ComprasGov | **NENHUM** | — | — | Zero protecao — se travar, consome recursos indefinidamente |
| Supabase | `SupabaseCircuitBreaker` | 50% fail rate (janela 10) | 60s | Sistema diferente — CORRETO (DB != API HTTP) |

**Conflitos identificados:**
- `pncp_client.py:48-60`: PNCP threshold=15, PCP threshold=30 — ratio 2:1 sem justificativa
- `clients/compras_gov_client.py`: 839 linhas, NENHUM circuit breaker — usa apenas retry inline (3x com backoff)

**Fundamentacao tecnica:**
- [Circuit Breaker Pattern — Martin Fowler](https://martinfowler.com/bliki/CircuitBreaker.html): Padrao original — 3 estados (Closed/Open/Half-Open), threshold uniforme
- [Resilience4j Best Practices](https://oneuptime.com/blog/post/2026-01-25-circuit-breakers-resilience4j-spring/view): "Start with sensible defaults, monitor your circuit breakers in production, and tune thresholds based on real traffic patterns"
- [Building Resilient Systems 2026](https://dasroot.net/posts/2026/01/building-resilient-systems-circuit-breakers-retry-patterns/): "Place circuit breaker outside your retry logic — retries shouldn't hammer a failing service"
- [Talent500 — CB Pattern Best Practices](https://talent500.com/blog/circuit-breaker-pattern-microservices-design-best-practices/): "When combined with timeouts, retries, bulkheads, and monitoring, circuit breakers form a robust resilience strategy"
- [PyBreaker Implementation](https://thebackenddevelopers.substack.com/p/implementing-the-circuit-breaker): Implementacao Python de referencia com 3 estados

## Acceptance Criteria

### ComprasGov Circuit Breaker (gap principal)

- [x] AC1: ComprasGov protegido por circuit breaker — reusar a classe `PNCPCircuitBreaker` existente (ja funciona, testada, Redis-backed)
- [x] AC2: Instancia separada: `_comprasgov_circuit_breaker` com config propria via env vars (`COMPRASGOV_CIRCUIT_BREAKER_THRESHOLD`, `COMPRASGOV_CIRCUIT_BREAKER_COOLDOWN`)
- [x] AC3: Retry logic do ComprasGov (atualmente inline em `compras_gov_client.py:137-212`) DENTRO do circuit breaker — CB wraps retry, nao o contrario. Se o retry exaure tentativas, conta como 1 failure no CB (nao 3).
- [x] AC4: Health canary para ComprasGov (similar ao existente para PNCP) — probe leve a cada 60s para detectar recovery

### Threshold Alignment

- [x] AC5: PNCP, PCP e ComprasGov com thresholds ALINHADOS e justificados:

| Fonte | Threshold | Cooldown | Justificativa |
|-------|-----------|----------|---------------|
| PNCP | 15 falhas | 60s | Mantido — primario, volume alto, deteccao rapida |
| PCP | 15 falhas | 60s | **Alinhado** (era 30/120s sem justificativa) |
| ComprasGov | 15 falhas | 60s | **Novo** — mesma classe de API governamental |

- [x] AC6: Se no futuro diferentes thresholds forem necessarios, a razao DEVE ser documentada no config.py como comentario

### Supabase CB — Manter Separado

- [x] AC7: `SupabaseCircuitBreaker` NAO e alterado — databases tem semantica de falha diferente de APIs HTTP (sliding window com fail rate e correto para DB). Documentar no config.py: "Supabase CB usa sliding window — databases sao diferentes de APIs HTTP externas"

### Integracao com Pipeline de Busca

- [x] AC8: `search_pipeline.py` usa CB para PNCP, PCP e ComprasGov
- [x] AC9: Se CB OPEN para uma fonte, pipeline SKIP aquela fonte (nao tenta) e continua com as demais
- [x] AC10: Se TODAS as fontes OPEN, retorna cache stale com aviso ao usuario

### Metricas e Observabilidade

- [x] AC11: Prometheus metric `smartlic_circuit_breaker_state` com label `source={pncp,pcp,comprasgov}` — valores `{closed,open,half_open}` (expandir metrica existente que ja cobre pncp/pcp)
- [x] AC12: Log WARN ao transitar para OPEN, INFO ao retornar para CLOSED
- [x] AC13: Sentry breadcrumb em cada transicao de estado

### Testes

- [x] AC14: Teste: ComprasGov CB tripa apos 15 falhas e impede novas chamadas
- [x] AC15: Teste: ComprasGov CB recupera apos cooldown (half-open → closed)
- [x] AC16: Teste: Pipeline funciona com 1 fonte em CB OPEN (resultados parciais)
- [x] AC17: Teste: Pipeline retorna cache stale quando todas as fontes OPEN
- [x] AC18: Testes existentes passando (5131+ backend, 2681+ frontend)

## Technical Notes

### Por que reusar PNCPCircuitBreaker (nao reescrever)

A classe `PNCPCircuitBreaker` (pncp_client.py:154-261) ja funciona, ja e testada, ja tem Redis-backed state sharing (B-06), e ja tem fallback para in-memory. Criar uma nova "SourceCircuitBreaker" universal seria over-engineering para 50 usuarios.

**Abordagem pragmatica:**
1. Criar instancia do mesmo `PNCPCircuitBreaker`/`RedisCircuitBreaker` para ComprasGov
2. Alinhar thresholds
3. Integrar no pipeline
4. Pronto.

Reescrita para sliding window (Resilience4j-style) e trabalho de v2 quando houver dados de producao suficientes para justificar a mudanca. "Start with sensible defaults, monitor in production, and tune based on real traffic patterns."

### ComprasGov: retry DENTRO do CB, nao fora

Atualmente ComprasGov tem retry inline (3 tentativas com backoff). O CB deve envolver o retry:
```python
# CORRETO: CB wraps retry
async with comprasgov_cb:
    result = await comprasgov_client.fetch_with_retry(params)  # 3 retries internos

# ERRADO: retry wraps CB (cada retry conta como failure separado)
for attempt in range(3):
    async with comprasgov_cb:
        result = await comprasgov_client.fetch(params)
```
Se o retry exaure todas as tentativas, conta como 1 failure no CB. Nao como 3.

## Rollback Plan

| Condicao | Acao | Tempo |
|----------|------|-------|
| ComprasGov CB tripa prematuramente (falsos positivos) | Aumentar threshold via env var `COMPRASGOV_CIRCUIT_BREAKER_THRESHOLD=30` | < 2 min (env var) |
| Pipeline nao funciona com novo CB | Desabilitar ComprasGov CB via env var `COMPRASGOV_CB_ENABLED=false` | < 2 min (env var) |
| Threshold alignment causa problemas no PCP | Reverter PCP threshold: `PCP_CIRCUIT_BREAKER_THRESHOLD=30` | < 2 min (env var) |

## Smoke Test Pos-Deploy

```bash
# 1. CB state de todas as fontes
curl -s https://api.smartlic.tech/health | jq '.dependencies.sources'
# Esperado: pncp, pcp, comprasgov todos "healthy" ou "degraded" (nao missing)

# 2. Busca retorna fontes
curl -s -X POST https://api.smartlic.tech/buscar \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"setor_id":"vestuario","ufs":["SP"],"data_inicio":"2026-02-20","data_fim":"2026-02-27"}' \
  | jq '.sources_consulted'
# Esperado: array com pncp, pcp, comprasgov (quando disponiveis)
```

## Files to Change

| File | Mudanca |
|------|---------|
| `backend/pncp_client.py:56-60` | Alinhar PCP threshold para 15/60s |
| `backend/pncp_client.py:505-519` | Adicionar instancia `_comprasgov_circuit_breaker` |
| `backend/clients/compras_gov_client.py` | Integrar CB wrapping retry logic |
| `backend/search_pipeline.py` | Usar CB para ComprasGov no pipeline |
| `backend/config.py` | Adicionar env vars para ComprasGov CB |
| `backend/metrics.py` | Expandir metrica CB para incluir comprasgov |
| `backend/tests/test_comprasgov_circuit_breaker.py` (NOVO) | Testes do ComprasGov CB |

## Definition of Done

- [x] Todas as 3 fontes de dados protegidas por circuit breaker
- [x] Thresholds alinhados e justificados
- [x] ComprasGov com CB (era zero protecao)
- [x] Metricas Prometheus para monitorar estado de cada CB
- [x] Pipeline de busca degrada gracefully quando fontes falham
- [x] Supabase CB mantido separado (decisao documentada)
- [x] Rollback via env vars funcional
- [x] Testes cobrindo ComprasGov CB + pipeline integration
