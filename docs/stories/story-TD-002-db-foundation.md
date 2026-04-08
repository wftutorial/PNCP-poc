# STORY-TD-002: DB Foundation — Backup, Integridade e Cleanup

**Story ID:** STORY-TD-002
**Epic:** EPIC-TD-2026
**Phase:** 2 (Foundation)
**Priority:** P1
**Estimated Hours:** 10h
**Agents:** @data-engineer (migrations, backup), @devops (GitHub Actions workflow)

## Objetivo

Estabelecer fundacao operacional robusta para o banco de dados: backup independente com PITR, integridade referencial no plan_type, limpeza de soft-deletes, e correcao da funcao purge_old_bids(). Estes itens protegem contra perda de dados e garantem consistencia do schema.

## Acceptance Criteria

- [ ] AC1: GitHub Actions workflow executa `pg_dump` semanal para S3 (ou storage equivalente). Ultimo backup verificavel via log do workflow. Retencao minima de 4 semanas (4 backups).
- [ ] AC2: PITR (Point-in-Time Recovery) habilitado no Supabase Pro. Verificavel via Supabase dashboard ou CLI mostrando PITR ativo.
- [ ] AC3: Resultado de `SELECT count(*) FROM pncp_raw_bids WHERE is_active = false` documentado. Se > 0: cron de cleanup ativo via `cron.schedule()`. Se = 0: decisao documentada sobre manter ou dropar coluna is_active.
- [ ] AC4: `purge_old_bids()` corrigida para limpar rows com `is_active = false` alem do criterio de data. Verificavel via code review do RPC body.
- [ ] AC5: Coluna `profiles.plan_type` tem FK para tabela de referencia de planos (em vez de CHECK constraint). Migracao executada com `NOT VALID` + `VALIDATE CONSTRAINT` em dois steps para zero-downtime.
- [ ] AC6: Nenhum valor orfao em `profiles.plan_type` — query `SELECT DISTINCT plan_type FROM profiles WHERE plan_type NOT IN (SELECT plan_type FROM plans)` retorna 0 rows antes da migracao FK.
- [ ] AC7: Zero regressions nos testes de backend (5131+ tests passing).

## Tasks

### Backup & PITR
- [ ] Task 1: Verificar que Supabase esta no tier Pro (pre-requisito TD-033 da Fase 1).
- [ ] Task 2: Habilitar PITR no Supabase Pro via dashboard/CLI.
- [ ] Task 3: Criar GitHub Actions workflow `.github/workflows/db-backup.yml`:
  - Schedule: weekly (domingo 5 UTC)
  - Steps: connect via `SUPABASE_DB_URL`, run `pg_dump --format=custom`, upload to S3
  - Retention: 4 weeks (delete backups > 28 days)
  - Secrets: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_S3_BUCKET`, `SUPABASE_DB_URL`
- [ ] Task 4: Testar workflow manualmente via `workflow_dispatch`.

### Soft-Delete Cleanup
- [ ] Task 5: Executar `SELECT count(*) FROM pncp_raw_bids WHERE is_active = false` em producao.
- [ ] Task 6: Se count > 0: criar migracao com `cron.schedule('cleanup_inactive_bids', '0 5 * * *', $$DELETE FROM pncp_raw_bids WHERE is_active = false AND updated_at < NOW() - INTERVAL '1 day'$$)`.
- [ ] Task 7: Investigar `purge_old_bids()` — verificar se limpa apenas por data ou tambem por is_active. Se nao limpa is_active=false, adicionar clausula.
- [ ] Task 8: Se count = 0: documentar em PR que coluna is_active pode ser candidata a remocao futura (nao remover agora — usada pelo datalake query).

### plan_type FK Migration
- [ ] Task 9: Verificar valores orfaos: `SELECT DISTINCT plan_type FROM profiles WHERE plan_type NOT IN (SELECT name FROM plans)`. Se existirem, corrigir antes da FK.
- [ ] Task 10: Criar migracao three-step:
  1. `ALTER TABLE profiles DROP CONSTRAINT IF EXISTS profiles_plan_type_check`
  2. `ALTER TABLE profiles ADD CONSTRAINT profiles_plan_type_fk FOREIGN KEY (plan_type) REFERENCES plans(name) NOT VALID`
  3. `ALTER TABLE profiles VALIDATE CONSTRAINT profiles_plan_type_fk`
- [ ] Task 11: Testar migracao em ambiente de staging ou local primeiro.
- [ ] Task 12: Aplicar migracao em producao em horario de baixo trafego (madrugada BRT).

## Definition of Done

- [ ] Todos os ACs met e verificaveis
- [ ] Migracoes aplicadas sem erros
- [ ] Backup workflow testado e executando (pelo menos 1 backup successful)
- [ ] Backend tests passing (5131+ tests, 0 failures)
- [ ] PR reviewed por @architect
- [ ] Documentacao de decisoes (soft-delete cleanup, is_active column) em PR description

## Debt Items Covered

| ID | Item | Hours | Notas |
|----|------|-------|-------|
| TD-034 | Weekly pg_dump to S3 + PITR | 2 | Requer TD-033 (Supabase Pro) da Fase 1 |
| TD-020 | pncp_raw_bids soft-delete bloat cleanup | 2 | Investigacao + cron se necessario |
| TD-NEW-002 | purge_old_bids() ignores is_active=false | 1 | Fix na funcao RPC |
| TD-021 | plan_type CHECK -> FK migration | 4 | Three-step zero-downtime migration |
| TD-022 | content_hash COMMENT fix | 0.5 | Pode ser incluido aqui se nao feito na Fase 1 |
| | **Total** | **9.5h** | |

## Notas Tecnicas

- **TD-034 depende de TD-033:** Sem o tier Pro, PITR nao esta disponivel e pg_dump requer connection string que pode nao estar acessivel no FREE tier com todas features.
- **TD-021 zero-downtime:** A abordagem `NOT VALID` + `VALIDATE` permite que a FK seja criada sem lock exclusivo. O VALIDATE faz uma verificacao em background. Executar em horario de baixo trafego por precaucao.
- **TD-020 e TD-NEW-002 sao relacionados:** A funcao `purge_old_bids()` deveria limpar is_active=false mas pode nao estar fazendo. Investigar primeiro, depois corrigir em conjunto.
- **Ordem de execucao:** Task 5-8 (soft-delete) pode executar em paralelo com Task 9-12 (FK migration). Backup (Task 1-4) depende de TD-033.

---

*Story criada em 2026-04-08 por @pm (Morgan). Fase 2 do EPIC-TD-2026.*
