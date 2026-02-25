# STORY-265: JSONB Storage Governance

## Metadata
- **Epic:** Enterprise Readiness (EPIC-ENT-001)
- **Priority:** P1 (Stability)
- **Effort:** 2 hours
- **Area:** Database
- **Depends on:** None
- **Risk:** Medium (requer verificacao de dados em producao)
- **Assessment IDs:** T2-03

## Context

`search_results_cache.results` e um JSONB blob sem limite de tamanho — 50-500KB por entry, ate 5MB por usuario. Sem governance, o storage infla e queries ficam lentas quando `results` e incluido em SELECT. Nao existe pg_cron cleanup para entries cold (>7 dias).

## Acceptance Criteria

- [ ] AC1: Query de producao executada para verificar max JSONB size atual
- [ ] AC2: CHECK constraint aplicada (1MB ou 2MB dependendo dos dados)
- [ ] AC3: pg_cron cleanup job criado para entries > 7 dias com priority 'cold'
- [ ] AC4: Insert de JSONB > limite falha (rejeitado pelo CHECK)
- [ ] AC5: Insert de JSONB < limite funciona normalmente
- [ ] AC6: Nenhum dado existente viola o CHECK constraint

## Tasks

- [ ] Task 1: **PRE-CHECK OBRIGATORIO** — Executar em producao:
  ```sql
  SELECT count(*) as total,
         avg(octet_length(results::text)) as avg_bytes,
         max(octet_length(results::text)) as max_bytes,
         count(*) FILTER (WHERE octet_length(results::text) > 1048576) as over_1mb
  FROM search_results_cache;
  ```
- [ ] Task 2: Se `over_1mb > 0`: limpar ou truncar entries oversized, OU usar limite de 2MB
- [ ] Task 3: Criar migration com CHECK constraint (valor baseado no pre-check)
- [ ] Task 4: Configurar pg_cron cleanup job
- [ ] Task 5: Testar insert de JSONB acima e abaixo do limite

## Test Plan

1. Query producao para max size (Task 1)
2. Aplicar CHECK — verificar que nenhum dado existente viola
3. INSERT blob 1.1MB (ou acima do limite) -> deve falhar
4. INSERT blob 500KB -> deve funcionar
5. Verificar pg_cron job agendado

## Regression Risks

- **MEDIO:** CHECK constraint rejeita inserts de buscas que retornam resultados muito grandes. Se uma busca multi-UF com 500+ resultados gera >1MB de JSONB, o cache write falha silenciosamente.
- **Mitigacao:** Verificar max size atual. Considerar 2MB em vez de 1MB. Adicionar application-level truncation antes do INSERT como fallback.

## Files Changed

- `supabase/migrations/20260225150000_jsonb_storage_governance.sql` (NEW)

## Definition of Done

- [ ] Pre-check de producao executado
- [ ] CHECK constraint aplicada sem violar dados existentes
- [ ] pg_cron cleanup ativo
- [ ] Testes de insert acima/abaixo do limite
