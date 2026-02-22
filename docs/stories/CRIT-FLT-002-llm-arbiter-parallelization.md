# CRIT-FLT-002 — LLM Arbiter Sequential Bottleneck (Zona Cinza 1-5%)

**Prioridade:** P1 — Performance / Timeout Risk
**Estimativa:** 3h
**Origem:** Auditoria de Pipeline 2026-02-22
**Track:** Backend
**Status:** COMPLETED

## Problema

O LLM Arbiter para a zona cinza (densidade 1-5%) roda chamadas **sequencialmente** (for loop, linhas 2795-2865 de `filter.py`). Enquanto isso, o zero-match (0% density) usa `ThreadPoolExecutor(max_workers=10)` para paralelizar (linhas 2572-2612).

### Impacto Medido
- Cada chamada LLM GPT-4.1-nano: ~200-400ms
- Busca típica com 20 bids na zona cinza: **4-8 segundos sequenciais**
- Busca ampla (5+ UFs, 10 dias): pode ter 50+ bids na zona cinza → **10-20 segundos**
- Isso dentro do timeout chain: Pipeline(360s) > Filter stage → contribui para timeouts

### Contraste
- Zero-match: `ThreadPoolExecutor(max_workers=10)` → 10 chamadas paralelas
- Gray-zone arbiter: `for lic in resultado_llm_candidates:` → 1 chamada por vez

## Acceptance Criteria

- [x] **AC1:** Paralelizar chamadas LLM da Camada 3A usando `ThreadPoolExecutor(max_workers=10)` ou `asyncio.gather` (igual ao zero-match)
- [x] **AC2:** Manter QA audit sampling funcional dentro do paralelismo
- [x] **AC3:** Preservar contadores de stats (`aprovadas_llm_arbiter`, `rejeitadas_llm_arbiter`, `llm_arbiter_calls`) com thread-safety
- [x] **AC4:** Fallback on LLM failure = REJECT (manter filosofia zero-noise)
- [x] **AC5:** Log consolidado de tempo total de Camada 3A (antes vs depois)
- [x] **AC6:** Manter cache MD5 de LLM arbiter funcional (thread-safe por design, cache é dict read-heavy)
- [x] **AC7:** Testes unitários validam paralelismo (mock LLM com sleep para simular latência)

## Impacto

- **Performance:** 5-10x speedup na fase de filtragem para buscas amplas
- **Risco de regressão:** MÉDIO (paralelismo pode introduzir race conditions nos stats)
- **Cost:** Mesma quantidade de chamadas LLM, apenas executadas em paralelo

## Implementação

### Mudanças em `backend/filter.py`:
- Added `import time, threading` at module level
- Extracted `_classify_one_arbiter()` inner function for per-bid LLM classification
- Replaced sequential `for lic in resultado_llm_candidates:` with `ThreadPoolExecutor(max_workers=10)`
- Sector name resolved ONCE before dispatching threads (avoids redundant lookups)
- `threading.Lock()` protects all stats counter increments (AC3)
- `time.monotonic()` captures total elapsed time for Camada 3A (AC5)
- Exception handler in `as_completed` loop → REJECT fallback (AC4)
- QA audit sampling preserved inside the `as_completed` loop (AC2)

### Testes em `backend/tests/test_crit_flt_002_arbiter_parallel.py`:
- 10 tests across 6 test classes
- `TestArbiterParallelExecution`: Latency test (10 bids × 100ms sleep < 60% of sequential time)
- `TestArbiterQaAudit`: Verifies audit decision structure in parallel
- `TestArbiterThreadSafeStats`: Mixed/all-approved/all-rejected stat consistency
- `TestArbiterFailureFallback`: Exception → REJECT, partial failure mixed
- `TestArbiterTimingLog`: Log includes `elapsed=`, `parallel`, bid count
- `TestArbiterCacheCompatibility`: Duplicate bids all classified

## Arquivos

- `backend/filter.py` (linhas ~2792-2910, Camada 3A — parallelized)
- `backend/tests/test_crit_flt_002_arbiter_parallel.py` (10 new tests)
