# STORY-305: Circuit Breaker Unification & Full Source Coverage

**Sprint:** CRITICAL — Semana 1 pos-recovery
**Size:** L (8-12h)
**Root Cause:** Diagnostic Report 2026-02-27 — HIGHs H6, H7
**Depends on:** STORY-303 (backend precisa estar de pe)
**Industry Standard:** [Circuit Breaker Pattern — Martin Fowler](https://martinfowler.com/bliki/CircuitBreaker.html), [Resilience4j](https://resilience4j.readme.io/docs/circuitbreaker)

## Contexto

A busca multi-fonte do SmartLic depende de 3 APIs governamentais externas (PNCP, PCP, ComprasGov). Se uma fonte travar, o circuit breaker deve isola-la rapidamente para que as outras continuem servindo resultados. Hoje existem DOIS sistemas de circuit breaker com configuracoes CONFLITANTES e uma fonte (ComprasGov) SEM NENHUMA protecao.

**Evidencia da auditoria:**

| Fonte | Circuit Breaker | Threshold | Cooldown | Problema |
|-------|----------------|-----------|----------|----------|
| PNCP | `PNCPCircuitBreaker` | 15 falhas | 60s | OK — threshold adequado |
| PCP | `PNCPCircuitBreaker` (reusado) | 30 falhas | 120s | 2x mais tolerante que PNCP sem justificativa tecnica |
| ComprasGov | **NENHUM** | — | — | Zero protecao |
| Supabase | `SupabaseCircuitBreaker` | 50% fail rate (janela 10) | 60s | Sistema diferente com modelo diferente |

**Conflitos identificados:**
- `pncp_client.py:48-60`: PNCP threshold=15, PCP threshold=30 — ratio 2:1 sem justificativa
- `supabase_client.py:84-100`: Modelo completamente diferente (sliding window vs consecutive failures)
- `clients/compras_gov_client.py`: 839 linhas, NENHUM circuit breaker — usa apenas retry inline

**Fundamentacao tecnica:**
- [Circuit Breaker Pattern — Martin Fowler](https://martinfowler.com/bliki/CircuitBreaker.html): Padrao original — 3 estados (Closed/Open/Half-Open), threshold uniforme
- [Resilience4j Best Practices](https://oneuptime.com/blog/post/2026-01-25-circuit-breakers-resilience4j-spring/view): "Start with sensible defaults, monitor your circuit breakers in production, and tune thresholds based on real traffic patterns"
- [Building Resilient Systems 2026](https://dasroot.net/posts/2026/01/building-resilient-systems-circuit-breakers-retry-patterns/): "Place circuit breaker outside your retry logic — retries shouldn't hammer a failing service"
- [Talent500 — CB Pattern Best Practices](https://talent500.com/blog/circuit-breaker-pattern-microservices-design-best-practices/): "When combined with timeouts, retries, bulkheads, and monitoring, circuit breakers form a robust resilience strategy"
- [PyBreaker Implementation](https://thebackenddevelopers.substack.com/p/implementing-the-circuit-breaker): Implementacao Python de referencia com 3 estados

## Acceptance Criteria

### Unificacao do Circuit Breaker

- [ ] AC1: Uma UNICA classe `SourceCircuitBreaker` com interface consistente para todas as fontes
- [ ] AC2: Modelo de failure: sliding window (ultimas N requests) com failure rate threshold — nao consecutive failures
- [ ] AC3: Tres estados: CLOSED (normal) → OPEN (isolado) → HALF_OPEN (testando recovery)
- [ ] AC4: Parametros unificados e configuráveis por fonte via env vars:

| Parametro | Default | PNCP | PCP | ComprasGov | Env Var Pattern |
|-----------|---------|------|-----|------------|-----------------|
| window_size | 20 | 20 | 20 | 20 | `{SOURCE}_CB_WINDOW_SIZE` |
| failure_rate_threshold | 0.5 | 0.5 | 0.5 | 0.5 | `{SOURCE}_CB_FAILURE_RATE` |
| cooldown_seconds | 60 | 60 | 60 | 60 | `{SOURCE}_CB_COOLDOWN` |
| half_open_max_calls | 3 | 3 | 3 | 3 | `{SOURCE}_CB_HALF_OPEN_CALLS` |

- [ ] AC5: Redis-backed state sharing entre workers (manter feature B-06)
- [ ] AC6: Fallback graceful para in-memory se Redis indisponivel (manter comportamento atual)

### ComprasGov Circuit Breaker

- [ ] AC7: ComprasGov protegido pelo mesmo `SourceCircuitBreaker`
- [ ] AC8: Retry logic do ComprasGov (atualmente inline em `compras_gov_client.py:137-212`) FORA do circuit breaker — CB wraps retry, nao o contrario
- [ ] AC9: Health canary para ComprasGov (similar ao existente para PNCP)

### Metricas e Observabilidade

- [ ] AC10: Prometheus metric `smartlic_circuit_breaker_state` com labels `source={pncp,pcp,comprasgov}` e valores `{closed,open,half_open}`
- [ ] AC11: Prometheus metric `smartlic_circuit_breaker_transitions_total` com labels `source` e `from_state` → `to_state`
- [ ] AC12: Log WARN ao transitar para OPEN, INFO ao transitar para HALF_OPEN, INFO ao retornar para CLOSED
- [ ] AC13: Sentry breadcrumb em cada transicao de estado

### Integracao com Pipeline de Busca

- [ ] AC14: `search_pipeline.py` usa o novo CB unificado para PNCP, PCP e ComprasGov
- [ ] AC15: Se CB OPEN para uma fonte, pipeline SKIP aquela fonte (nao tenta) e continua com as demais
- [ ] AC16: Se TODAS as fontes OPEN, retorna cache stale com aviso ao usuario

### Testes

- [ ] AC17: Teste: CB transita CLOSED → OPEN apos failure_rate exceder threshold
- [ ] AC18: Teste: CB transita OPEN → HALF_OPEN apos cooldown
- [ ] AC19: Teste: CB transita HALF_OPEN → CLOSED apos calls bem-sucedidos
- [ ] AC20: Teste: CB transita HALF_OPEN → OPEN se call falha durante half-open
- [ ] AC21: Teste: Redis state sync funciona entre 2 instancias
- [ ] AC22: Teste: Fallback para in-memory se Redis down
- [ ] AC23: Teste: ComprasGov CB integrado no pipeline de busca
- [ ] AC24: Testes existentes passando (5131+ backend, 2681+ frontend)

## Technical Notes

### Por que sliding window e nao consecutive failures

O modelo atual (consecutive failures) tem um problema: UMA request bem-sucedida reseta o contador. Se a API esta falhando 80% das vezes mas 1 em cada 5 passa, o CB NUNCA tripa. Sliding window com failure rate (ex: >50% das ultimas 20 requests falharam) detecta degradacao real.

**Referencia Resilience4j:** "COUNT_BASED sliding window aggregates the outcome of the last N calls. The failure rate threshold is used to decide when the CircuitBreaker should transit from CLOSED to OPEN."

### ComprasGov: retry DENTRO do CB, nao fora

Atualmente ComprasGov tem retry inline (3 tentativas com backoff). O CB deve envolver o retry:
```
CB.execute(() => {
    return retry(3, () => comprasGovRequest())
})
```
Se o retry exaure todas as tentativas, conta como 1 failure no CB. Nao como 3.

### Migracaco: manter backward compat

O `PNCPCircuitBreaker` e `RedisCircuitBreaker` atuais devem ser deprecados mas nao removidos imediatamente. A nova `SourceCircuitBreaker` assume, e as classes antigas ficam como alias ate a proxima release.

## Files to Change

| File | Mudanca |
|------|---------|
| `backend/circuit_breaker.py` (NOVO) | Classe unificada `SourceCircuitBreaker` |
| `backend/pncp_client.py:48-60,154-530` | Deprecar `PNCPCircuitBreaker` + `RedisCircuitBreaker`, usar nova classe |
| `backend/clients/compras_gov_client.py` | Integrar CB, mover retry para dentro do CB |
| `backend/supabase_client.py:73-228` | Avaliar migracao ou manter separado (DB vs API) |
| `backend/search_pipeline.py:1562,2560-2561` | Usar novo CB unificado |
| `backend/config.py` | Adicionar config vars para CB por fonte |
| `backend/metrics.py` | Adicionar metricas unificadas |
| `backend/tests/test_circuit_breaker.py` (NOVO) | Testes do CB unificado |

## Definition of Done

- [ ] Todas as 3 fontes de dados protegidas por circuit breaker
- [ ] Configuracao uniforme e consistente entre fontes
- [ ] ComprasGov com CB (era zero protecao)
- [ ] Metricas Prometheus para monitorar estado de cada CB
- [ ] Pipeline de busca degrada gracefully quando fontes falham
- [ ] Testes cobrindo todos os estados e transicoes
