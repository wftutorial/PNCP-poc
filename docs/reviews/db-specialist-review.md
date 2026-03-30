# Database Specialist Review (v2)

**Revisor:** @data-engineer (Dara)
**Data:** 2026-03-30
**Documento revisado:** docs/prd/technical-debt-DRAFT.md (Secao 2: Debitos de Database)
**Cross-references:** supabase/docs/SCHEMA.md, supabase/docs/DB-AUDIT.md, 99 migration files
**Nota:** Esta revisao v2 substitui a v1 (2026-03-23). O DRAFT foi atualizado desde a v1 e agora reflete corretamente os debitos resolvidos (DB-TD-008, DB-TD-010, DB-TD-011).

---

## Debitos Validados

| ID | Debito | Severidade Original | Severidade Ajustada | Horas | Complexidade | Notas |
|----|--------|---------------------|---------------------|-------|-------------|-------|
| DEBT-DB-002 | `ingestion_runs.metadata` JSONB sem CHECK constraint | Baixa | Baixa | 0.5h | Simples | Confirmado: unica coluna JSONB critica restante sem governance. Migration 20260321130100 adicionou CHECK em 12 colunas mas omitiu esta. Fix trivial: 1 ALTER ADD CONSTRAINT com pattern NOT VALID + VALIDATE. |
| DEBT-DB-003 | Trigger prefix inconsistente (tr_/trg_/trigger_) | Baixa | Baixa | 2h | Simples | Confirmado via SCHEMA.md: `tr_pipeline_items_updated_at`, `trg_pncp_raw_bids_updated_at`, `trigger_alert_preferences_updated_at`. 3 prefixos distintos. Cosmetic, sem impacto funcional. |
| DEBT-DB-004 | RLS policy naming inconsistente | Baixa | Baixa | 3h | Media | Confirmado: mix de snake_case (`profiles_select_own`), descritivo ingles (`Service role can manage subscriptions`), e hibrido. ~60+ policies para renomear. Requer DROP + CREATE para cada (sem ALTER POLICY RENAME no PostgreSQL). |
| DEBT-DB-005 | Hardcoded Stripe price IDs em migrations | Media | **Baixa** | 2h | Simples | Severidade reduzida: migration 20260321130200 documenta o problema extensivamente e recomenda `scripts/seed_stripe_prices.py`. O script existe e funciona. Esforco restante e apenas documentacao no onboarding. |
| DEBT-DB-006 | Inconsistencia soft/hard delete em pncp_raw_bids | Baixa | Baixa | 1h | Simples | Confirmado: `purge_old_bids()` faz `DELETE FROM ... WHERE is_active = true AND data_publicacao < cutoff` (hard delete). O COMMENT na coluna is_active diz incorretamente que purge faz soft delete. O fix principal e corrigir o COMMENT, nao mudar o comportamento. |
| DEBT-DB-007 | health_checks e incidents sem policies admin | Baixa | Baixa | 1h | Simples | Confirmado: nenhuma migration adiciona SELECT policy para admin nestas tabelas. Admin precisa usar service_role key para consultar health data. |
| DEBT-DB-009 | Nenhuma migration com rollback formal | Media | **Alta** | 12h | Complexa | Severidade elevada: com 99 migrations e deploy automatico via CI (`supabase db push --include-all`), a ausencia de rollback e o risco operacional mais significativo do banco. Se uma migration quebrar dados em producao, a unica opcao e PITR do Supabase (se disponivel no plano) ou restauracao manual de backup. |
| DEBT-SYS-010 | 99 migrations Supabase | Media | Media | 16h | Complexa | Confirmado: exatamente 99 migrations. Varias contem seed data (Stripe price IDs), data migrations (FK standardization, RLS fixes), e logica condicional. Squash requer cuidado extremo -- ver resposta detalhada abaixo. |

## Debitos Removidos

### DEBT-DB-001 -- `alerts.filters` JSONB sem CHECK constraint

**Justificativa:** Ja resolvido na migration `20260321130100_debt_db010_jsonb_size_governance.sql` (linhas 88-95). A constraint `chk_alerts_filters_size` ja existe com limite de 512KB (`pg_column_size < 524288`), usando o pattern NOT VALID + VALIDATE para zero-downtime. Este debito deve ser adicionado a lista de "resolvidos" no DRAFT junto com DB-TD-008, DB-TD-010 e DB-TD-011.

**Impacto no DRAFT:** Reduzir total de debitos de 38 para 37. Atualizar resumo executivo. Remover DEBT-DB-001 da matriz de priorizacao (P3).

## Debitos Adicionados

| ID | Debito | Severidade | Horas | Complexidade | Notas |
|----|--------|------------|-------|-------------|-------|
| DEBT-DB-NEW-001 | COMMENT incorreto em `pncp_raw_bids.is_active` | Baixa | 0.5h | Simples | COMMENT diz "Set to false by purge_old_bids() instead of hard-delete for audit trail" mas `purge_old_bids()` faz `DELETE FROM` (hard delete). Discrepancia entre doc e comportamento real pode confundir futuros devs. |
| DEBT-DB-NEW-002 | `ingestion_checkpoints.crawl_batch_id` FK nao enforced | Baixa | 1h | Simples | COMMENT documenta "Foreign-key reference to ingestion_runs.crawl_batch_id (not enforced for perf)". A justificativa de performance e valida durante ingestao batch, mas pode causar checkpoints orfaos se ingestion_runs forem deletados. Monitorar. |
| DEBT-DB-NEW-003 | `upsert_pncp_raw_bids` usa loop row-by-row | Media | 4h | Media | A funcao itera `jsonb_array_elements` com FOR LOOP, fazendo SELECT + INSERT/UPDATE por row. Para batches de 500 rows (config atual), isso e 500 round-trips internos ao planner. Pode ser otimizado com CTE + INSERT ON CONFLICT em uma unica query batch. Impacto estimado: ingestao 2-3x mais rapida. |
| DEBT-DB-NEW-004 | `search_datalake` calcula `to_tsvector` 2x por row | Baixa | 2h | Media | A funcao calcula `to_tsvector('portuguese', coalesce(b.objeto_compra, ''))` no WHERE, no SELECT (para ts_rank) e no ORDER BY. O planner do PostgreSQL pode nao consolidar essas avaliacoes em todos os casos. Trade-off: stored tsvector column aumentaria storage (~40MB para 1M rows) vs FREE tier 500MB. Manter como esta ate que benchmarks mostrem necessidade. |
| DEBT-DB-NEW-005 | Sem monitoring de table bloat para `pncp_raw_bids` | Media | 2h | Simples | Com 40K+ rows e hard deletes diarios via `purge_old_bids()`, a tabela e candidata a bloat. Nao ha pg_cron job para VACUUM ANALYZE explicito (depende do autovacuum do Supabase Cloud). Recomendo adicionar monitoring via `pg_stat_user_tables.n_dead_tup` no health check existente. |

## Respostas ao Architect

### Pergunta 1: DEBT-DB-009 (rollback) -- Estrategia atual e 5 tabelas criticas

**Estrategia de rollback atual:** Nao existe procedimento formal. A protecao atual consiste em:
1. **Idempotencia:** Migrations usam `IF NOT EXISTS` / `DROP IF EXISTS` / `ON CONFLICT`, o que permite re-execucao mas nao reversao.
2. **PITR:** Point-in-Time Recovery do Supabase Cloud (disponivel no plano Pro, granularidade de segundos).
3. **Backup automatico:** Supabase faz backup diario. Restauracao e manual e requer interacao com dashboard.
4. **Nenhum procedimento documentado** para rollback de migration especifica.

**5 tabelas que precisam de rollback scripts primeiro (em ordem de criticidade):**

1. **profiles** -- Dados de usuario, plano, subscription_status, context_data. Erro aqui = downgrade involuntario de planos, perda de dados de onboarding. Ponto central do schema (28+ FKs apontam para esta tabela).
2. **user_subscriptions** -- Dados financeiros do Stripe (subscription_id, customer_id, billing_period). Erro = cobranca incorreta, perda de acesso a features pagas.
3. **monthly_quota** -- Contagem de buscas por mes. Erro = usuarios bloqueados (quota zerada) ou com acesso indevido (quota resetada).
4. **pncp_raw_bids** -- Datalake com 40K+ rows. Erro na ingestao pode corromper FTS index ou introduzir duplicatas.
5. **search_results_cache** -- Cache L2 persistente. Menor impacto (pode ser reconstruido via nova busca), mas afeta UX imediata.

### Pergunta 2: DEBT-DB-005 (Stripe IDs) -- Seed script cobre staging?

O seed script (`scripts/seed_stripe_prices.py`) existe e le `STRIPE_PRICE_*` do `.env`. A migration 20260321130200 documenta extensivamente os price IDs de producao e o procedimento para staging.

**O que falta para staging funcional:**
1. **Documentacao no README de onboarding** -- novo dev nao sabe que precisa rodar o script apos `supabase db push`
2. **Validacao automatica no CI** -- verificar que price IDs sao de test mode (`price_1T*` = producao) em ambientes non-prod
3. **Shell wrapper** (`scripts/seed-stripe-prices.sh`) ja existe mas precisa ser referenciado no setup guide

**Conclusao:** Problema 80% resolvido. Esforco restante e documentacao, nao codigo. Severidade reduzida para Baixa.

### Pergunta 3: DEBT-DB-006 (soft/hard delete) -- Causa problemas reais?

**Nao causa problemas operacionais.** A inconsistencia e puramente semantica/documentacional:

- `is_active = false`: Usado como soft delete logico -- registros marcados nao aparecem em buscas (`WHERE is_active = true` no `search_datalake`)
- `purge_old_bids()`: Faz hard DELETE de registros com `data_publicacao` anterior ao cutoff de retencao (12 dias) E que sao `is_active = true`

**Nota importante:** A funcao `purge_old_bids()` nao deleta registros com `is_active = false` (a clausula WHERE filtra `AND is_active = true`). Isso significa que registros soft-deleted ficam indefinidamente na tabela, ocupando storage. Isso pode ser intencional (audit trail) ou um bug sutil. Se for intencional, a retencao de soft-deleted records deveria ter seu proprio cleanup.

**Fix recomendado:**
1. Corrigir o COMMENT na coluna `is_active` (0.5h)
2. Decidir se soft-deleted records devem ter purge separado (decisao de produto, nao de DB)

### Pergunta 4: DEBT-SYS-010 (99 migrations) -- Riscos de squash

**Ha riscos significativos que desaconselham squash completo:**

1. **Data migrations com INSERT/UPDATE:** Migrations 015, 021, 029, 20260226120000, 20260301300000 contem INSERT de Stripe price IDs de producao. Migration 20260308330000 faz ban de cache warmer system account. Squash precisa preservar todos esses INSERTs.

2. **Funcoes referenciadas por triggers:** Varias migrations fazem `CREATE OR REPLACE FUNCTION` seguido de `CREATE TRIGGER`. A ordem de execucao importa.

3. **Verificacoes de integridade:** Migration 20260311100000 (DEBT-113) contem loops DO $$ que levantam EXCEPTION se invariantes forem violadas. Squash perderia essa camada de verificacao.

4. **Unica migration com rollback:** Migration 010 tem rollback documentado. Squash perderia essa referencia.

5. **Naming transition:** Migrations 001-033 usam numeracao sequencial; 20260220+ usam timestamp. Squash unificaria mas perderia historico de quando cada mudanca foi feita.

**Recomendacao:** Em vez de squash completo:
- Criar schema snapshot via `pg_dump --schema-only` como referencia canonica
- Documentar migrations pre-20260308 como "legacy wave" (schema estavel)
- Continuar com migrations incrementais
- Reavaliar squash apenas ao ultrapassar 200 migrations ou quando deploy time de `supabase db push` exceder 5 minutos

### Pergunta 5: DEBT-DB-001/002 (JSONB) -- Tamanho maximo

- **`alerts.filters`:** Ja tem CHECK de 512KB (migration 20260321130100). Debito removido.
- **`ingestion_runs.metadata`:** Recomendo **512KB** (`pg_column_size < 524288`) para consistencia com as demais colunas. Conteudo tipico < 10KB (config snapshot do worker, lista de UFs, versao). O limite de 512KB serve como safety net contra bugs de serializacao, nao como limite operacional.

## Analise de Dependencias

```
Fase 1 — Quick Wins (podem ser feitos em paralelo, 1 migration):
  DEBT-DB-002 (metadata CHECK)           — 0.5h, independente
  DEBT-DB-NEW-001 (fix COMMENT)          — 0.5h, independente
  DEBT-DB-007 (admin RLS policies)       — 1h, independente
  DEBT-DB-005 (documentacao seed)         — 2h, independente (nao requer migration)

Fase 2 — Resiliencia (1-2 sprints):
  DEBT-DB-009 (rollback scripts)          — 12h, depende de definir prioridade das tabelas
    -> Comecar por profiles e user_subscriptions (dados financeiros)
    -> Depois monthly_quota e pncp_raw_bids
    -> search_results_cache por ultimo (reconstruivel)
  DEBT-DB-NEW-005 (bloat monitoring)      — 2h, independente

Fase 3 — Performance (quando ingestao escalar):
  DEBT-DB-NEW-003 (otimizar upsert loop)  — 4h, requer testes E2E de ingestao
    -> Depende de benchmark antes/depois
  DEBT-DB-NEW-004 (tsvector 2x)           — 2h, trade-off storage vs CPU
    -> Depende de DEBT-DB-NEW-005 para medir impacto real

Fase 4 — Cosmetic (backlog, fazer oportunisticamente):
  DEBT-DB-003 (trigger prefix)            — 2h, downtime minimo
  DEBT-DB-004 (RLS naming)                — 3h, requer DROP+CREATE por policy
  DEBT-DB-006 (soft/hard delete semant.)  — 1h, apenas documentacao
  DEBT-DB-NEW-002 (FK checkpoint)         — 1h, apenas monitoring

DEBT-SYS-010 (squash migrations):
  Independente mas desaconselhado — ver resposta acima.
  Alternativa recomendada: schema snapshot (4h) em vez de squash (16h).
```

## Recomendacoes

### Imediatas (Sprint atual)

1. **DEBT-DB-002:** Adicionar CHECK em `ingestion_runs.metadata`. Migration de 5 linhas. Pattern: `ALTER TABLE ADD CONSTRAINT ... NOT VALID; VALIDATE CONSTRAINT ...` **0.5h**

2. **DEBT-DB-NEW-001:** Corrigir COMMENT em `pncp_raw_bids.is_active`. Uma linha de SQL. **0.5h**

3. **DEBT-DB-007:** Adicionar RLS SELECT policy para admin em health_checks e incidents. 2 policies, padrao estabelecido no codebase. **1h**

4. **Remover DEBT-DB-001 do DRAFT** -- ja resolvido em migration 20260321130100.

### Curto prazo (1-2 sprints)

5. **DEBT-DB-009:** Criar rollback scripts para 5 tabelas criticas. Comecar com profiles e user_subscriptions. Cada script deve: (a) reverter schema changes, (b) restaurar dados via backup parcial, (c) verificar integridade pos-rollback. **12h total, 4h para as 2 primeiras tabelas.**

6. **DEBT-DB-NEW-005:** Adicionar monitoring de dead tuples em pncp_raw_bids ao health check existente. Pode ser feito via RPC function que consulta `pg_stat_user_tables`. **2h**

7. **DEBT-DB-005:** Completar documentacao de onboarding para seed script. Adicionar passo no README. **2h**

### Medio prazo (3+ sprints)

8. **DEBT-DB-NEW-003:** Otimizar `upsert_pncp_raw_bids` para batch processing. Substituir FOR LOOP por CTE + INSERT ON CONFLICT. Requer benchmark antes/depois e testes de ingestao completos. **4h**

9. **DEBT-SYS-010:** Criar schema snapshot (`pg_dump --schema-only`) em vez de squash completo. Documentar migrations legacy. **4h** (vs 16h do squash completo).

10. **DEBT-DB-003 + DEBT-DB-004:** Padronizacao de naming. Fazer incrementalmente quando tocar nas tabelas afetadas. Nao justifica sprint dedicado. **5h total se feito de uma vez.**

## Parecer

O banco de dados do SmartLic esta em **excelente estado de saude**. As waves de debt cleanup (DEBT-001 a DEBT-120, 15+ migrations corretivas) resolveram todos os problemas criticos de seguranca:

| Metrica | Valor | Alvo |
|---------|-------|------|
| RLS Coverage | 100% (28/28 tabelas) | 100% |
| FK Standardization | 100% (todas para profiles(id)) | 100% |
| JSONB Size Governance | ~93% (falta apenas `ingestion_runs.metadata`) | 100% |
| Retention Policies | 100% (12 pg_cron jobs) | 100% |
| Index Coverage | Excelente (80+ indexes) | Sem missing criticals |
| NOT NULL em timestamps | 100% (corrigido em DEBT-017/100) | 100% |

**Unico risco operacional significativo:** DEBT-DB-009 (ausencia de rollback scripts). Com deploy automatico e 99 migrations, este e o calcanhar de Aquiles. Recomendo prioridade P1 e elevacao de severidade para Alta.

**Resumo de ajustes ao DRAFT:**
- **1 debito removido:** DEBT-DB-001 (ja resolvido em migration 20260321130100)
- **1 severidade elevada:** DEBT-DB-009 (Media -> Alta)
- **1 severidade reduzida:** DEBT-DB-005 (Media -> Baixa)
- **5 debitos adicionados:** COMMENT incorreto, FK nao enforced, upsert row-by-row, tsvector 2x, bloat monitoring
- **Total de debitos DB:** 12 (era 8 no DRAFT, -1 removido, +5 adicionados)
- **Esforco total DB revisado:** ~38h (vs ~22h original, aumento principal pelo rollback scripts a 12h e otimizacao de upsert a 4h)
