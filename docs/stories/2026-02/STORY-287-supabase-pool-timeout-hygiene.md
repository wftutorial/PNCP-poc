# STORY-287: Supabase Connection Pool & Timeout Hygiene

**Priority:** P1
**Effort:** S (0.5 day)
**Squad:** @dev
**Fundamentacao:** GTM Readiness Audit Track 6 (Performance) — sem connection pool config, timeout inconsistente
**Status:** TODO
**Sprint:** GTM Sprint 1

---

## Contexto

O audit identificou dois gaps de performance:

1. **Supabase connection pool** nao configurado explicitamente — usa defaults do supabase-py. Sob carga concorrente, risco de connection exhaustion.
2. **SEARCH_FETCH_TIMEOUT** em 360s (6 min) para background async fetch e excessivo e consome recursos desnecessariamente.
3. **CONSOLIDATION_TIMEOUT** inconsistente entre `config.py` (100s) e `source_config/sources.py` (300s).

---

## Acceptance Criteria

### AC1: Configure Supabase connection pool
- [ ] Investigar se `supabase-py` expone configuracao de pool (httpx pool limits)
- [ ] Se sim: configurar `max_connections=50`, `max_keepalive_connections=20` via env vars
- [ ] Se nao: documentar limitacao e considerar usar httpx diretamente para operacoes criticas
- [ ] Teste de carga: 10 buscas concorrentes sem connection errors

### AC2: Reduce SEARCH_FETCH_TIMEOUT
- [ ] Reduzir `SEARCH_FETCH_TIMEOUT` de 360s para 180s em `config.py`
- [ ] Manter como env-configurable para override em producao se necessario
- [ ] Documentar razao da mudanca

### AC3: Reconcile CONSOLIDATION_TIMEOUT values
- [ ] Investigar se `CONSOLIDATION_TIMEOUT_GLOBAL` (300s em sources.py) e `CONSOLIDATION_TIMEOUT` (100s em config.py) sao para code paths diferentes
- [ ] Se sao o mesmo conceito: unificar em config.py
- [ ] Se sao diferentes: renomear para clarificar e documentar

### AC4: Documentation cleanup
- [ ] Atualizar CLAUDE.md timeout chain se valores mudaram
- [ ] Atualizar docs/summaries/gtm-resilience-summary.md se aplicavel

---

## Arquivos Impactados

| Arquivo | Mudanca |
|---------|---------|
| `backend/config.py` | SEARCH_FETCH_TIMEOUT, pool config |
| `backend/source_config/sources.py` | CONSOLIDATION_TIMEOUT_GLOBAL clarification |
| `backend/supabase_client.py` | Connection pool config |
