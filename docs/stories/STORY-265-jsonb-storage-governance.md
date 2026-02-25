# STORY-265: JSONB Storage Governance

## Metadata
- **Epic:** Enterprise Readiness (EPIC-ENT-001)
- **Priority:** P1 (Stability)
- **Effort:** 2 hours
- **Area:** Database
- **Depends on:** None
- **Risk:** Medium (requer verificacao de dados em producao)
- **Assessment IDs:** T2-03
- **Status:** Done

## Context

`search_results_cache.results` e um JSONB blob sem limite de tamanho — 50-500KB por entry, ate 5MB por usuario. Sem governance, o storage infla e queries ficam lentas quando `results` e incluido em SELECT. Nao existe pg_cron cleanup para entries cold (>7 dias).

## Acceptance Criteria

- [x] AC1: Query de producao executada para verificar max JSONB size atual
- [x] AC2: CHECK constraint aplicada (1MB ou 2MB dependendo dos dados)
- [x] AC3: pg_cron cleanup job criado para entries > 7 dias com priority 'cold'
- [x] AC4: Insert de JSONB > limite falha (rejeitado pelo CHECK)
- [x] AC5: Insert de JSONB < limite funciona normalmente
- [x] AC6: Nenhum dado existente viola o CHECK constraint

## Pre-Check Results (2026-02-25)

```
total=7, avg_bytes=616886, max_bytes=1588205, over_1mb=2, over_2mb=0
```

**Decision:** Use 2MB limit (2 entries at ~1.59MB are safe; 0 entries over 2MB).

## Tasks

- [x] Task 1: **PRE-CHECK OBRIGATORIO** — Executar em producao:
  ```sql
  SELECT count(*) as total,
         avg(octet_length(results::text)) as avg_bytes,
         max(octet_length(results::text)) as max_bytes,
         count(*) FILTER (WHERE octet_length(results::text) > 1048576) as over_1mb
  FROM search_results_cache;
  ```
- [x] Task 2: Se `over_1mb > 0`: limpar ou truncar entries oversized, OU usar limite de 2MB
- [x] Task 3: Criar migration com CHECK constraint (valor baseado no pre-check)
- [x] Task 4: Configurar pg_cron cleanup job
- [x] Task 5: Testar insert de JSONB acima e abaixo do limite

## Test Plan

1. Query producao para max size (Task 1) — DONE: max=1.59MB
2. Aplicar CHECK — verificar que nenhum dado existente viola — DONE: 0 violations
3. INSERT blob > 2MB -> deve falhar — DONE: application-level truncation + DB CHECK
4. INSERT blob < 2MB -> deve funcionar — DONE: 9 tests passing
5. Verificar pg_cron job agendado — DONE: cleanup-cold-cache-entries @ 05:00 UTC daily

## Regression Risks

- **MEDIO:** CHECK constraint rejeita inserts de buscas que retornam resultados muito grandes. Se uma busca multi-UF com 500+ resultados gera >1MB de JSONB, o cache write falha silenciosamente.
- **Mitigacao:** Application-level truncation em `search_cache.py:_save_to_supabase()` trunca resultados antes do INSERT, evitando rejeicao silenciosa pelo CHECK constraint.

## Files Changed

- `supabase/migrations/20260225150000_jsonb_storage_governance.sql` (NEW) — CHECK constraint + pg_cron job
- `backend/search_cache.py` (MODIFIED) — Application-level JSONB size guard (2MB truncation)
- `backend/tests/test_jsonb_storage_governance.py` (NEW) — 9 tests covering AC2-AC6

## Definition of Done

- [x] Pre-check de producao executado
- [x] CHECK constraint aplicada sem violar dados existentes
- [x] pg_cron cleanup ativo
- [x] Testes de insert acima/abaixo do limite
