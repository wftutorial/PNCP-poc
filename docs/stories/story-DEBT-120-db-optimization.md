# DEBT-120: DB Optimization — Index Analysis, Traceability, Cleanup

**Prioridade:** POST-GTM
**Estimativa:** 3.5h
**Fonte:** Brownfield Discovery — @data-engineer (DB-025, DB-031, DB-INFO-01)
**Score Impact:** Integrity 8→9

## Contexto
3 items de otimização de database: analisar usage dos 6 indexes em search_results_cache (potencial remoção de redundantes), adicionar search_id a pipeline_items para rastreabilidade, e deprecar o diretório backend/migrations/.

## Acceptance Criteria

### Index Analysis (2h)
- [ ] AC1: Executar pg_stat_user_indexes em produção para search_results_cache
- [ ] AC2: Identificar indexes com idx_scan = 0 (candidatos a remoção)
- [ ] AC3: Se idx_search_cache_params_hash redundante com UNIQUE: DROP INDEX
- [ ] AC4: Documentar decisão sobre cada index

### Pipeline Traceability (1h)
- [ ] AC5: Migration: ADD COLUMN search_id TEXT a pipeline_items
- [ ] AC6: Atualizar routes/pipeline.py para salvar search_id ao adicionar item ao pipeline
- [ ] AC7: Teste unitário para novo campo

### Migrations Cleanup (0.5h)
- [ ] AC8: Adicionar README.md em backend/migrations/ marcando como DEPRECATED
- [ ] AC9: Ou deletar o diretório inteiro (se confirmado que nenhum script usa)

## File List
- [ ] `supabase/migrations/20260315100000_debt120_db_optimization.sql` (NEW)
- [ ] `backend/routes/pipeline.py` (EDIT — search_id)
- [ ] `backend/migrations/README.md` (NEW — DEPRECATED notice)
