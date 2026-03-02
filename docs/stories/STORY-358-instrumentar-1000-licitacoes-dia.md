# STORY-358: Instrumentar e validar claim "1000+ licitações/dia"

**Prioridade:** P2
**Tipo:** feature (observabilidade)
**Sprint:** Sprint 3
**Estimativa:** M
**Origem:** Conselho CTO Advisory Board — Auditoria de Promessas (2026-03-01)
**Dependências:** Nenhuma
**Bloqueado por:** —
**Bloqueia:** —
**Paralelo com:** STORY-353, STORY-359, STORY-360

---

## Contexto

A InstitutionalSidebar exibe "1000+ licitações/dia" sem fonte de dados. PNCP publica milhares/dia, mas o volume processado pelo SmartLic nunca foi medido.

## Promessa Afetada

> "1000+ licitações/dia"

## Causa Raiz

Número exibido na sidebar sem fonte de dados. Pode ser verdade (PNCP publica milhares/dia), mas não é medido.

## Critérios de Aceite

- [x] AC1: Criar Prometheus counter `smartlic_bids_processed_total` (labels: source) incrementado no pipeline de busca
- [x] AC2: Criar cron job diário que registra contagem de bids processados nas últimas 24h
- [x] AC3: Criar endpoint `GET /v1/metrics/daily-volume` retornando média de bids/dia dos últimos 30 dias
- [x] AC4: No frontend, substituir "1000+" hardcoded por valor dinâmico (com fallback "centenas" se API falhar)
- [x] AC5: Volume depende do uso real — endpoint retorna "centenas" como fallback seguro quando dados insuficientes. À medida que a base cresce, o display_value atualiza automaticamente. Prometheus counter permite monitorar tendência em tempo real.
- [x] AC6: Testes do endpoint e do cron job (18 backend + 4 frontend = 22 novos testes)

## Arquivos Afetados

- `backend/metrics.py` — AC1: BIDS_PROCESSED_TOTAL counter
- `backend/search_pipeline.py` — AC1: Increment counter after consolidation
- `backend/cron_jobs.py` — AC2: record_daily_volume() + start_daily_volume_task()
- `backend/main.py` — AC2: Register daily_volume_task in lifespan
- `backend/routes/metrics_api.py` — AC3: GET /metrics/daily-volume endpoint
- `frontend/app/components/InstitutionalSidebar.tsx` — AC4: Dynamic daily volume
- `frontend/app/api/metrics/daily-volume/route.ts` — AC4: Public API proxy
- `backend/tests/test_story358_daily_volume.py` — AC6: 18 backend tests
- `frontend/__tests__/components/InstitutionalSidebar.test.tsx` — AC6: 4 new + updated tests

## Validação

| Métrica | Threshold | Onde medir |
|---------|-----------|------------|
| `smartlic_bids_processed_total` / dia | >500 para claim "centenas/dia" | Prometheus |
