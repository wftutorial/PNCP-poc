# STORY-282: PNCP Timeout Resilience — Cache-First + Aggressive Timeout

**Priority:** P0 BLOCKER
**Effort:** 2 days
**Squad:** @dev + @qa
**Fundamentacao:** Logs de producao 2026-02-26 (PNCP 180s timeout, 0 records)

## Problema Observado em Producao

```
PNCP SP modalidade=4: 30s timeout × 3 retries = 90s → primeiro success
PNCP SP modalidade=5: 30s timeout × 2 retries = 60s → success (21 items)
PNCP SP modalidade=6: 30s timeout × 3 retries = 90s → 1463 items (30 pages!)
PNCP SP modalidade=7: timeout total

Consolidation total: 180s → TIMEOUT → 0 records from PNCP
PCP sozinho: 53 records brutos → 0 apos filtro vestuario
Resultado final: 0 oportunidades para o usuario
```

**PNCP modalidade 6 (Pregao) para SP tem 1463 records / 30 pages.** A 3s por pagina = 90s so para paginar. Com retries, impossivel caber no timeout.

## Evidencia: Cache Warming tambem falha

```
[CONSOLIDATION] PNCP: timeout after 60003ms — no records
[CONSOLIDATION] PNCP: timeout after 60000ms — no records
Source 'PNCP' transitioned to DEGRADED status after 3 consecutive failures
revalidation_complete: duration_ms=60007, result=empty, new_results_count=0
```

Cache warming roda 25 combinacoes (5 sectors × 5 UFs) e TODAS falham quando PNCP esta lento. Zero cache populado = zero resultados para usuarios.

## Root Causes (3 camadas)

1. **PNCP read timeout = 30s** muito generoso — multiplica com retries (3) e modalidades (4)
2. **Sem page limit** — modalidade 6/SP tem 30 pages, tenta todas
3. **Cache warming concorre com busca real** — 3 revalidations + 25 warmups competem pelas mesmas conexoes

## Acceptance Criteria

### AC1: Reducao agressiva de timeout PNCP
- [ ] `pncp_client.py`: `_CONNECT_TIMEOUT = 10` (era 30)
- [ ] `pncp_client.py`: `_READ_TIMEOUT = 15` (era 30)
- [ ] Max retries: 1 (era 3) — fail fast, nao adianta retry se API esta lenta
- [ ] Configurable via env: `PNCP_CONNECT_TIMEOUT`, `PNCP_READ_TIMEOUT`, `PNCP_MAX_RETRIES`

### AC2: Page limit por modalidade
- [ ] `pncp_client.py`: `MAX_PAGES_PER_MODALIDADE = 5` (250 items max)
- [ ] Se total_records > 250, log warning e truncar (nao buscar 30 pages)
- [ ] Configurable via env: `PNCP_MAX_PAGES`
- [ ] Rational: SP/modalidade=6 tem 1463 items. 250 items (5 pages) ja cobre os mais recentes.

### AC3: Cache-first para buscas de usuario
- [ ] Se cache existe (mesmo stale), retornar IMEDIATAMENTE ao usuario
- [ ] Disparar revalidation em background (ja existe, mas nao esta sendo usado corretamente)
- [ ] Frontend: mostrar badge "dados de Xh atras" se cache stale
- [ ] Timeout para busca "fresh" de usuario: 60s max (nao 180s)

### AC4: Priorizar busca real sobre warming
- [ ] Se ha busca de usuario em andamento, pausar cache warming
- [ ] Semaphore: max 1 concurrent cache warming task quando busca ativa
- [ ] Log: `{"event": "warming_paused", "reason": "user_search_active"}`

### AC5: Fallback PCP com filtro UF corrigido
- [ ] PCP v2 nao filtra por UF server-side. Client filter funciona, mas precisa match exato.
- [ ] Quando PNCP falha, PCP deve retornar resultados util (nao 0)
- [ ] Investigar: por que 53 records PCP → 0 apos filtro vestuario?
  - Hipotese: PCP retorna records sem campo UF, ou UF em formato diferente

## Files to Modify

| File | Change |
|------|--------|
| `backend/pncp_client.py` | Timeout + page limit |
| `backend/config.py` | PNCP_CONNECT_TIMEOUT, PNCP_READ_TIMEOUT, PNCP_MAX_PAGES |
| `backend/search_cache.py` | Cache-first logic for user searches |
| `backend/cron_jobs.py` | Warming priority/pause logic |
| `backend/portal_compras_client.py` | Investigate UF filter behavior |

## Metricas Esperadas

| Antes | Depois |
|-------|--------|
| PNCP timeout 180s → 0 results | PNCP fail fast 15s → cache served |
| Cache warming: 0/25 populados | Warming com backoff inteligente |
| SP/mod6: 30 pages × 3s = 90s | SP/mod6: 5 pages × 3s = 15s |
| User wait: 185s (timeout) | User wait: <5s (cached) ou <60s (fresh) |
