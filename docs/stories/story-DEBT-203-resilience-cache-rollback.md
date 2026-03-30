# Story DEBT-203: Resiliencia — Cache Decomposition + DB Rollback Scripts

## Metadados
- **Epic:** EPIC-DEBT-V2
- **Sprint:** 4 (Semana 7-8)
- **Prioridade:** P1 (Alta)
- **Esforco:** 26h
- **Agente:** @dev + @data-engineer + @qa
- **Status:** PLANNED

## Descricao

Como equipe de operacoes, queremos decompor o sistema de cache monolitico (2.564 LOC) e criar scripts de rollback para as 5 tabelas criticas do banco de dados, para que incidentes em producao possam ser resolvidos em minutos (em vez de horas de restauracao manual) e o sistema de cache possa evoluir com seguranca.

## Debitos Incluidos

| ID | Debito | Horas | Responsavel |
|----|--------|-------|-------------|
| DEBT-SYS-003 | `search_cache.py` complexo (2.564 LOC) — logica multi-level em arquivo unico | 12h | @dev + @qa |
| DEBT-DB-009 | Nenhuma migration com rollback formal — 99 migrations, restauracao manual unica opcao | 12h | @data-engineer + @qa |
| DEBT-DB-NEW-005 | Sem monitoring de table bloat para `pncp_raw_bids` | 2h | @data-engineer |

## Criterios de Aceite

### Decomposicao search_cache.py (12h)
- [ ] `search_cache.py` decomposto em submodulos:
  - `cache/memory.py` — InMemoryCache (L1, 4h TTL, hot/warm/cold priority)
  - `cache/redis.py` — Redis cache layer
  - `cache/supabase.py` — Supabase `search_results_cache` (L2, 24h TTL)
  - `cache/local_file.py` — Local file cache fallback
  - `cache/swr.py` — SWR revalidation logic
  - `cache/manager.py` — Orquestracao multi-level (entry point)
- [ ] `search_cache.py` redirecionado como facade com re-exports (backward-compat)
- [ ] Nenhum submodulo excede 600 LOC
- [ ] Mock pattern `supabase_client.get_supabase` preservado (NAO `search_cache.get_supabase`)
- [ ] Helper de mock centralizado criado para facilitar testes futuros
- [ ] SWR revalidation overhead <= 200ms (benchmark)

### Rollback Scripts DB (12h)
- [ ] Scripts de rollback criados para 5 tabelas criticas:
  1. `profiles` — rollback de colunas adicionadas/modificadas
  2. `user_subscriptions` — rollback de schema changes
  3. `search_results_cache` — rollback de estrutura
  4. `pncp_raw_bids` — rollback de indexes/constraints
  5. `pipeline_items` — rollback de colunas
- [ ] Scripts armazenados em `supabase/rollbacks/` com nomenclatura `rollback_YYYYMMDD_table_description.sql`
- [ ] Cada script inclui:
  - Verificacao pre-rollback (assert expected state)
  - Operacao de rollback
  - Verificacao pos-rollback (assert reverted state)
  - Instrucoes de uso em comentario SQL
- [ ] Scripts testados em staging com dados sinteticos
- [ ] Integridade de FKs validada pos-rollback

### Bloat Monitoring (2h)
- [ ] pg_cron job configurado para monitorar bloat em `pncp_raw_bids`
- [ ] Alerta quando bloat ratio excede threshold (40K+ rows com hard deletes diarios)
- [ ] Query de diagnostico documentada em `supabase/docs/`

### Qualidade
- [ ] 186 testes de cache passam sem falha
- [ ] Novo teste de integracao multi-level criado (L1 miss → L2 hit → response)
- [ ] Suite completa backend: 5131+ testes passam
- [ ] Rollback scripts validados em ambiente staging (nao executar em producao sem PITR)

## Testes Requeridos

- [ ] `pytest -k "test_cache" --timeout=30` — 186 testes passam
- [ ] `pytest -k "test_search_cache" --timeout=30` — testes especificos de search_cache
- [ ] Novo teste: cache multi-level integration (L1 → L2 → L3)
- [ ] Rollback scripts: executar em staging com dados sinteticos, validar schema reverte e dados preservados
- [ ] Benchmark SWR revalidation: overhead <= 200ms
- [ ] `pytest --timeout=30 -q` — suite completa

## Notas Tecnicas

- **Cache mock pattern CRITICO:** Sempre usar `patch("supabase_client.get_supabase")`, nunca `patch("search_cache.get_supabase")`. Erros de mock causam falhas hard-to-debug.
- **Rollback strategy:** Comecar por `profiles` e `user_subscriptions` (tabelas mais criticas para billing). Nunca executar rollback em producao sem PITR disponivel.
- **Bloat monitoring:** `pncp_raw_bids` tem 40K+ rows com hard deletes diarios pelo purge job. VACUUM ANALYZE deve estar configurado adequadamente.
- **Supabase PITR:** Verificar se o plano atual do Supabase oferece PITR. Se nao, rollback scripts sao AINDA MAIS criticos.

## Dependencias

- Nenhuma dependencia direta de DEBT-200 ou DEBT-201
- Recomendado: completar apos Sprint 2 para base de codigo mais limpa
- DEBT-DB-NEW-005 (bloat monitoring) e independente, pode ser parallelizado
