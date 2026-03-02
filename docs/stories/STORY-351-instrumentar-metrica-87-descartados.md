# STORY-351: Instrumentar e validar métrica "87% descartados"

**Prioridade:** P0
**Tipo:** feature (observabilidade) + fix (copy condicional)
**Sprint:** Sprint 1
**Estimativa:** L
**Origem:** Conselho CTO Advisory Board — Auditoria de Promessas (2026-03-01)
**Dependências:** Nenhuma
**Bloqueado por:** —
**Bloqueia:** —
**Paralelo com:** STORY-354

---

## Contexto

O número "87% dos editais descartados" aparece em 6+ locais na UI (HeroSection, StatsSection, comparisons.ts, valueProps.ts). Não existe nenhum Prometheus counter, logging estruturado, ou dashboard que meça o discard rate real. O número não tem origem.

## Promessa Afetada

> "87% dos editais descartados antes de chegar até você"

## Causa Raiz

Número arbitrário exibido como fato. Zero infraestrutura de medição. O pipeline de filtragem funciona (2.549 regras em sectors_data.yaml), mas o ratio real nunca foi medido.

## Critérios de Aceite

- [x] AC1: Adicionar Prometheus counter `smartlic_filter_input_total` e `smartlic_filter_output_total` (labels: sector, source) em `metrics.py` — instrumentado em `search_pipeline.py:stage_filter`
- [x] AC2: Adicionar Prometheus histogram `smartlic_filter_discard_rate` (ratio = 1 - output/input) em `search_pipeline.py` ao final do estágio filter
- [x] AC3: Criar endpoint `GET /v1/metrics/discard-rate` que retorna a média móvel de 30 dias do discard rate por setor — `routes/metrics_api.py`
- [x] AC4: No frontend, substituir "87%" hardcoded por valor dinâmico do endpoint (com fallback para "a maioria" se API falhar) — `StatsSection.tsx`, `valueProps.ts`, `comparisons.ts`
- [x] AC5: Se discard rate real < 87%, tunar pipeline de filtragem — copy agora usa "a maioria" como fallback seguro; número exato exibido apenas quando endpoint retorna dados com sample_size > 0
- [x] AC6: Atualizar `StatsSection.tsx` para renderizar valor dinâmico com loading state (animate-pulse skeleton)
- [x] AC7: Atualizar testes de `StatsSection.test.tsx` para mock do novo endpoint — 13 tests (was 8), +16 backend tests
- [x] AC8: Adicionar o número exato ao Grafana dashboard com alerta se discard rate cair abaixo de 70% — `docs/operations/grafana/discard-rate-dashboard.json`
- [x] AC9: Log estruturado: `{"event": "filter_stats", "input": N, "output": M, "discard_rate": X, "sector": "...", "search_id": "..."}` — via `DiscardRateTracker.record()` in `filter_stats.py`

## Arquivos Afetados

### Backend (Modified)
- `backend/metrics.py` — AC1: FILTER_INPUT_TOTAL, FILTER_OUTPUT_TOTAL, FILTER_DISCARD_RATE
- `backend/filter_stats.py` — AC3/AC9: DiscardRateTracker class + structured logging
- `backend/search_pipeline.py` — AC1/AC2/AC9: instrumentation in stage_filter
- `backend/main.py` — AC3: register metrics_api_router

### Backend (New)
- `backend/routes/metrics_api.py` — AC3: GET /v1/metrics/discard-rate endpoint
- `backend/tests/test_story351_discard_rate.py` — AC7: 16 tests

### Frontend (Modified)
- `frontend/app/components/landing/StatsSection.tsx` — AC4/AC6: dynamic fetch + loading + fallback
- `frontend/lib/copy/valueProps.ts` — AC4: "87%" → "a maioria"
- `frontend/lib/copy/comparisons.ts` — AC4: "87%" → "a maioria"
- `frontend/__tests__/landing/StatsSection.test.tsx` — AC7: 13 tests (was 8)
- `frontend/__tests__/landing-accessibility.test.tsx` — AC7: updated for dynamic aria-label
- `frontend/e2e-tests/landing-page.spec.ts` — Updated for dynamic discard value

### Frontend (New)
- `frontend/app/api/metrics/discard-rate/route.ts` — AC4: public API proxy

### Docs (New)
- `docs/operations/grafana/discard-rate-dashboard.json` — AC8: Grafana dashboard + alert rule

## Validação

| Métrica | Threshold | Onde medir |
|---------|-----------|------------|
| `smartlic_filter_discard_rate` média 30d | >70% para claim "a maioria" | Prometheus/Grafana |
| Log estruturado `filter_stats` | Emitido para cada busca | Railway logs |

## Notas

- Após 30 dias de coleta, revisar se "87%" é próximo da realidade e atualizar copy de acordo.
- Se rate real for >85%, pode voltar a usar número exato (agora verificável).
