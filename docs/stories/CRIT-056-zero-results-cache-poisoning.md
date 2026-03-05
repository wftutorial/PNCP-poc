# CRIT-056: Cache Quality Score — Evitar Servir Dados Degradados Quando Fonte Recuperou

**Prioridade:** MEDIUM
**Componente:** Backend — search_pipeline.py, search_cache.py, cron_jobs.py
**Origem:** Analise pos-incidente 2026-03-05 — cache persiste resultados parciais mesmo apos fonte primaria recuperar
**Status:** TODO
**Dependencias:** CRIT-053 (sources_degraded ja existe no pipeline)
**Estimativa:** 4-6h

## Problema

O pipeline salva resultados no cache (L1 InMemory 4h + L2 Supabase 24h) sem nenhuma metadata de qualidade. Quando uma fonte esta degraded, os resultados parciais sao cacheados com o mesmo TTL de resultados completos.

Cenario real:
1. 14:00 — PNCP degraded, busca retorna 104 resultados (so PCP v2)
2. 14:05 — PNCP volta ao normal
3. 14:10 — Mesma busca retorna dados cacheados (104 parciais) em vez de fazer fetch completo (potencialmente 500+ com PNCP)
4. Ate 18:00 (TTL L1) ou 14:00+1 (TTL L2) — usuario recebe dados incompletos

**Nota pos-CRIT-054:** PCP v2 agora retorna dados validos (status mapping corrigido), entao resultados parciais nao sao "lixo" — mas sao INCOMPLETOS. O problema nao e poisoning de dados inuteis, e servir subset quando o full set ja esta disponivel.

### Evidencia no Codigo

```python
# search_pipeline.py:793 — salva sem checar sources_degraded
if ctx.licitacoes_raw and len(ctx.licitacoes_raw) > 0:
    cache_data = {
        "licitacoes": ctx.licitacoes_raw,
        "total": len(ctx.licitacoes_raw),
        "cached_at": datetime.now(_tz.utc).isoformat(),
        "search_params": {...},
        # NENHUM campo de quality/sources_degraded
    }
    _write_cache(cache_key, cache_data)
```

## Acceptance Criteria

### AC1: Quality score na escrita do cache
- [ ] Adicionar `quality_score` ao cache_data em `search_pipeline.py:794`:
  - `1.0` — todas as fontes succeeded (PNCP + PCP v2 + ComprasGov)
  - `0.7` — fonte primaria ok, secundarias falharam
  - `0.3` — fonte primaria degraded/failed, so secundarias
  - `0.0` — nenhuma fonte retornou dados
- [ ] Adicionar `sources_succeeded: List[str]` ao cache_data
- [ ] Adicionar `sources_degraded: List[str]` ao cache_data
- [ ] Aplicar em ambos: `_write_cache()` (L1) e `save_to_cache_per_uf()` (L2 Supabase)

### AC2: Na leitura, preferir refresh se quality < 1.0 e fontes saudaveis
- [ ] Em `_read_cache()` e `_read_cache_composed()`:
  - Se `quality_score < 1.0` E cron canary diz PNCP healthy → tratar como STALE (nao FRESH)
  - SWR behavior: servir dados cacheados E disparar background revalidation
  - Log: `"Cache HIT (quality={qs}) but primary source recovered — triggering revalidation"`
- [ ] Se `quality_score >= 1.0` → comportamento normal (FRESH ate TTL)
- [ ] Se cron canary diz PNCP degraded → servir cache parcial normalmente (melhor que nada)

### AC3: Nao cachear resultados vazios de fonte degradada
- [ ] Se `ctx.sources_degraded` nao e vazio E `len(ctx.licitacoes_raw) == 0`:
  - NAO salvar no cache (nem L1 nem L2)
  - Log: `"Cache SKIP: all sources degraded and zero results"`
- [ ] Se `len(ctx.licitacoes_raw) > 0` mesmo com degradacao → salvar com quality_score baixo
  (dados parciais sao melhores que nenhum dado no cache)

### AC4: Auto-revalidacao quando PNCP recupera
- [ ] No cron canary (`cron_jobs.py`), quando PNCP transiciona de degraded → healthy:
  - Incrementar counter global `_pncp_recovery_epoch` (int, thread-safe)
  - Log: `"PNCP recovered (epoch={N}) — degraded cache entries will be revalidated on next read"`
- [ ] Em `_read_cache()`: comparar `cache_entry.epoch` com `_pncp_recovery_epoch`
  - Se epoch do cache < recovery epoch → tratar como STALE (forcar revalidation)
- [ ] Abordagem lazy (nao invalida ativamente, revalida no proximo acesso) — mais simples e seguro

### AC5: Metricas
- [ ] Counter: `smartlic_cache_quality_write_total` (labels: quality_bucket=full|partial|empty)
- [ ] Counter: `smartlic_cache_quality_revalidation_total` (revalidacoes disparadas por quality)
- [ ] Histogram: `smartlic_cache_quality_score` (observar score em cada write)

### AC6: Testes
- [ ] `test_crit056_cache_quality.py`:
  - Write com todas fontes ok → quality_score=1.0
  - Write com PNCP degraded + PCP ok → quality_score=0.3
  - Write com zero results + degraded → NAO salva no cache
  - Read com quality<1.0 + PNCP healthy → retorna STALE (dispara revalidation)
  - Read com quality<1.0 + PNCP degraded → retorna normalmente (melhor que nada)
  - PNCP recovery epoch increment → cache entries antigas forçam revalidation
  - quality_score propagado corretamente para L1 e L2
- [ ] Zero regressoes em testes existentes de cache (search_cache, search_pipeline)

## Notas de Implementacao

### Ponto de insercao — escrita (search_pipeline.py:793)

```python
# CRIT-056: Compute quality score based on source status
_sources_ok = [ds.source for ds in ctx.data_sources if ds.status == "succeeded"] if ctx.data_sources else []
_sources_deg = list(ctx.sources_degraded or [])
if "PNCP" in _sources_ok:
    _quality = 1.0 if not _sources_deg else 0.7
elif _sources_ok:
    _quality = 0.3  # No primary, but secondary ok
else:
    _quality = 0.0

# Skip cache for empty degraded results
if _quality < 0.5 and not ctx.licitacoes_raw:
    logger.info("Cache SKIP: sources degraded and zero results")
else:
    cache_data = {
        "licitacoes": ctx.licitacoes_raw,
        ...
        "quality_score": _quality,
        "sources_succeeded": _sources_ok,
        "sources_degraded": _sources_deg,
        "recovery_epoch": get_pncp_recovery_epoch(),
    }
    _write_cache(cache_key, cache_data)
```

### Ponto de insercao — leitura (pipeline/cache_manager.py ou search_cache.py)

```python
# CRIT-056: Check quality vs current source health
cached = _read_cache(cache_key)
if cached:
    qs = cached.get("quality_score", 1.0)  # backward compat: assume full if missing
    epoch = cached.get("recovery_epoch", 0)
    if qs < 1.0 and get_pncp_cron_status().get("status") == "healthy":
        # Source recovered — treat as stale, trigger background revalidation
        cached["_swr_stale"] = True
    if epoch < get_pncp_recovery_epoch():
        cached["_swr_stale"] = True
```

## File List

| Arquivo | Mudanca |
|---------|---------|
| `backend/search_pipeline.py` | quality_score + sources na escrita do cache |
| `backend/search_cache.py` | quality check na leitura, skip para empty degraded |
| `backend/pipeline/cache_manager.py` | `_read_cache` e `_write_cache` com quality metadata |
| `backend/cron_jobs.py` | `_pncp_recovery_epoch` counter, transition detection |
| `backend/metrics.py` | 3 novas metricas de cache quality |
| `backend/tests/test_crit056_cache_quality.py` | Testes |
