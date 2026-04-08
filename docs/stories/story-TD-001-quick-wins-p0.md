# STORY-TD-001: Quick Wins P0 — Eliminar Riscos de Parada Operacional

**Story ID:** STORY-TD-001
**Epic:** EPIC-TD-2026
**Phase:** 1 (Quick Wins)
**Priority:** P0 (Critical) + P1 (quick wins bundled)
**Estimated Hours:** 13h (3 parallel tracks, ~4h elapsed if parallelized)
**Agents:** @data-engineer (Track A — DB/Infra), @dev (Track B — Frontend), @qa (Track C — Security audit)

## Objetivo

Eliminar os 4 riscos criticos de parada operacional (banco cheio, busca lenta, tabelas sem retencao, soft-delete bloat) e corrigir problemas de alto impacto com baixo esforco (touch targets, font size, auditoria RPC). Esta story e a mais urgente do epic — o cenario de cascata #1 (banco cheio -> ingesta falha -> busca vazia -> usuarios abandonam) pode ocorrer em semanas.

## Acceptance Criteria

### Track A — DB/Infra (no dependencies)
- [ ] AC1: Supabase esta no tier Pro (ou superior) com limite de storage > 500MB. Verificavel via `pg_database_size()` retornando valor monitorado contra limite do tier.
- [ ] AC2: Indice composto `idx_pncp_raw_bids_dashboard_query` existe em producao. `EXPLAIN ANALYZE` de query tipica de `search_datalake` mostra Index Scan (nao Seq Scan) e reducao >= 40% na latencia p50.
- [ ] AC3: Quatro politicas de retencao ativas via `cron.schedule()`: stripe_webhook_events (90d), alert_sent_items (90d), trial_email_log (1yr), health_checks (30d). Verificavel via `SELECT * FROM cron.job WHERE active = true`.
- [ ] AC4: Coluna `content_hash` de `pncp_raw_bids` tem COMMENT atualizado de MD5 para SHA-256. Verificavel via `SELECT col_description(...)`.
- [ ] AC5: Query `SELECT count(*) FROM pncp_raw_bids WHERE is_active = false` executada e resultado documentado. Se > 0, cron de cleanup criado. Se = 0, documentar para TD-020 na Fase 2.

### Track B — Frontend (parallel)
- [ ] AC6: FeedbackButtons tem area de toque >= 44x44px em todos os breakpoints. Verificavel via DevTools (computed min-width/min-height >= 44px) em mobile viewport (375px).
- [ ] AC7: CompatibilityBadge usa `text-xs` (12px) em vez de `text-[10px]`. Nenhum texto < 12px visivel no componente em qualquer viewport.

### Track C — Security (parallel)
- [ ] AC8: Documento de auditoria RPC criado listando TODAS as Supabase RPCs user-scoped, indicando quais validam `auth.uid()` e quais nao. Formato: tabela com colunas (RPC name, validates auth.uid, risk level, fix needed).
- [ ] AC9: RPCs sem validacao de `auth.uid()` catalogadas com nivel de risco (high/medium/low) e recomendacao de fix. Documento disponivel em `docs/reviews/rpc-auth-audit.md`.

## Tasks

### Track A — DB/Infra (@data-engineer)
- [ ] Task 1: Executar upgrade do Supabase para Pro tier via dashboard ou CLI. Registrar `pg_database_size()` antes e depois.
- [ ] Task 2: Criar migracao com `CREATE INDEX CONCURRENTLY idx_pncp_raw_bids_dashboard_query ON pncp_raw_bids (uf, modalidade_id, data_publicacao DESC) WHERE is_active = true`. Testar com `EXPLAIN ANALYZE` de query tipica.
- [ ] Task 3: Criar migracao com 4 `cron.schedule()` calls para retention policies:
  - `DELETE FROM stripe_webhook_events WHERE created_at < NOW() - INTERVAL '90 days'` (diario, 3 UTC)
  - `DELETE FROM alert_sent_items WHERE created_at < NOW() - INTERVAL '90 days'` (diario, 3 UTC)
  - `DELETE FROM trial_email_log WHERE created_at < NOW() - INTERVAL '1 year'` (semanal, domingo 4 UTC)
  - `DELETE FROM health_checks WHERE created_at < NOW() - INTERVAL '30 days'` (diario, 3 UTC)
- [ ] Task 4: Atualizar COMMENT da coluna content_hash: `COMMENT ON COLUMN pncp_raw_bids.content_hash IS 'SHA-256 hash of normalized content for dedup'`.
- [ ] Task 5: Executar `SELECT count(*) FROM pncp_raw_bids WHERE is_active = false` e documentar resultado. Se > 0, criar cron cleanup.
- [ ] Task 6: Executar `supabase db push --include-all` para aplicar migracoes.

### Track B — Frontend (@dev)
- [ ] Task 7: Editar `FeedbackButtons` component — adicionar `min-w-[44px] min-h-[44px]` aos botoes de feedback. Garantir padding adequado para area de toque.
- [ ] Task 8: Editar `CompatibilityBadge` component — substituir `text-[10px]` por `text-xs`. Verificar que layout nao quebra em cards de resultado.
- [ ] Task 9: Rodar `npm test` e `npm run build` para confirmar zero regressions.

### Track C — Security (@qa)
- [ ] Task 10: Listar todas as Supabase RPCs via `SELECT routine_name FROM information_schema.routines WHERE routine_schema = 'public' AND routine_type = 'FUNCTION'`.
- [ ] Task 11: Para cada RPC user-scoped, verificar se o body contém `auth.uid()` validation. Catalogar em tabela.
- [ ] Task 12: Classificar risco de cada RPC sem validacao (high = acessa dados de outros usuarios, medium = side effect sem scope, low = read-only public data).
- [ ] Task 13: Criar documento `docs/reviews/rpc-auth-audit.md` com findings e recomendacoes.

## Definition of Done

- [ ] Todos os ACs met e verificaveis
- [ ] Migracoes aplicadas em producao sem erros
- [ ] Backend tests passing (`pytest --timeout=30 -q` — 5131+ tests, 0 failures)
- [ ] Frontend tests passing (`npm test` — 2681+ tests, 0 failures)
- [ ] No regression no OpenAPI schema (snapshot test)
- [ ] `EXPLAIN ANALYZE` mostra Index Scan para query de datalake
- [ ] `cron.job` mostra 4 retention jobs ativos
- [ ] RPC audit document reviewed por @architect

## Debt Items Covered

| ID | Item | Hours | Track |
|----|------|-------|-------|
| TD-033 | Supabase FREE tier storage exhaustion | 0.5 | A |
| TD-019 | Missing composite index pncp_raw_bids | 1 | A |
| TD-020 | pncp_raw_bids soft-delete bloat (investigation) | 1 | A |
| TD-025 | stripe_webhook_events retention | 0.5 | A |
| TD-026 | alert_sent_items retention | 0.5 | A |
| TD-027 | trial_email_log retention | 0.5 | A |
| TD-NEW-001 | health_checks retention | 0.5 | A |
| TD-022 | content_hash COMMENT fix | 0.5 | A |
| TD-052 | FeedbackButtons touch target 28px -> 44px | 1.5 | B |
| TD-053 | CompatibilityBadge text-[10px] -> text-xs | 0.5 | B |
| TD-059 | RPC auth.uid() validation audit | 4 | C |
| | **Total** | **11.5h** | |

## Notas Tecnicas

- **TD-033:** Decisao de negocio (R$25/mes para Supabase Pro). Sem essa decisao, nenhum outro item de DB faz sentido — o banco pode encher antes das correcoes serem aplicadas.
- **TD-019:** Usar `CREATE INDEX CONCURRENTLY` para nao bloquear writes durante criacao. Indice partial (`WHERE is_active = true`) reduz tamanho e melhora performance.
- **TD-025/026/027/NEW-001:** Bundlar em 1 migracao com 4 `cron.schedule()`. Usar `pg_cron` extension (ja habilitada no Supabase). Horarios escalonados para nao coincidir com ingestion (2 UTC) ou purge (7 UTC).
- **TD-052:** FeedbackButtons aparece em TODOS os cards de resultado — impacto visual imediato. Usar `min-w-[44px] min-h-[44px]` com `inline-flex items-center justify-center` para nao afetar layout.
- **TD-059:** Auditoria informa o escopo real de TD-005 (per-user tokens, Fase 5). Sem essa auditoria, nao sabemos quantas RPCs precisam de correcao.

---

*Story criada em 2026-04-08 por @pm (Morgan). Fase 1 do EPIC-TD-2026.*
