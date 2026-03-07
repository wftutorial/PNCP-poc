# HARDEN-023: Índices nas Colunas user_id (RLS Performance)

**Severidade:** MEDIA
**Esforço:** 10 min
**Quick Win:** Sim
**Origem:** Conselho CTO — Pesquisa de Industria (Supabase Docs)

## Contexto

Supabase docs documentam melhorias de 100×+ quando colunas usadas em RLS policies têm índice. Sem índice, full table scan em cada query com RLS. Impacto cresce conforme tabelas crescem.

## Critérios de Aceitação

- [ ] AC1: Migration cria índices em `user_id` para tabelas principais
- [ ] AC2: Tabelas: searches, pipeline, feedback, search_results_store, search_sessions
- [ ] AC3: `CREATE INDEX IF NOT EXISTS` (idempotente)
- [ ] AC4: Migration aplicada sem erro

## Solução

```sql
CREATE INDEX IF NOT EXISTS idx_searches_user_id ON searches(user_id);
CREATE INDEX IF NOT EXISTS idx_pipeline_user_id ON pipeline(user_id);
CREATE INDEX IF NOT EXISTS idx_feedback_user_id ON feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_search_results_store_user_id ON search_results_store(user_id);
CREATE INDEX IF NOT EXISTS idx_search_sessions_user_id ON search_sessions(user_id);
```

## Arquivos Afetados

- `supabase/migrations/` — nova migration
