# Story DEBT-104: DB Foundation — FK Standardization & Retention

## Metadata
- **Story ID:** DEBT-104
- **Epic:** EPIC-DEBT
- **Batch:** B (Foundation)
- **Sprint:** 2-3 (Semanas 3-6)
- **Estimativa:** 8h
- **Prioridade:** P1
- **Agent:** @data-engineer

## Descricao

Como engenheiro de dados, quero padronizar as 4 tabelas restantes que referenciam `auth.users` para apontar para `profiles(id)` com ON DELETE CASCADE, e configurar retention para `search_results_store`, para que a integridade referencial seja 100% consistente e o crescimento de storage esteja controlado.

## Debt Items Cobertos

| ID | Debito | Severidade | Horas |
|----|--------|:---:|:---:|
| DB-001 | FK Target Inconsistency — 4 tabelas restantes referenciam `auth.users` em vez de `profiles` (`monthly_quota`, `user_oauth_tokens`, `google_sheets_exports`, `search_results_cache`) | HIGH | 6h |
| DB-005 | `search_state_transitions.search_id` no FK — retention ja implementado (30d), falta doc update | LOW | 0.5h |
| DB-017 | `search_results_cache` duplicate size constraints | LOW | 0.5h |
| DB-020 | `google_sheets_exports.last_updated_at` naming inconsistente (unica tabela) sem trigger | LOW | 0.5h |

## Acceptance Criteria

- [ ] AC1: `monthly_quota.user_id` referencia `profiles(id)` com ON DELETE CASCADE
- [ ] AC2: `user_oauth_tokens.user_id` referencia `profiles(id)` com ON DELETE CASCADE
- [ ] AC3: `google_sheets_exports.user_id` referencia `profiles(id)` com ON DELETE CASCADE
- [ ] AC4: `search_results_cache.user_id` referencia `profiles(id)` com ON DELETE CASCADE
- [ ] AC5: Zero orphan rows em todas as 4 tabelas (verificado PRE-migration)
- [ ] AC6: `search_state_transitions` documentacao atualizada sobre ausencia intencional de FK
- [ ] AC7: `search_results_cache` duplicate size constraint removido
- [ ] AC8: `google_sheets_exports.last_updated_at` renomeado para `updated_at` com trigger automatico
- [ ] AC9: Query de verificacao pos-migration confirma 100% FK pointing to `profiles`

## Testes Requeridos

- **PRE-migration:** Orphan detection query para cada tabela:
  ```sql
  SELECT count(*) FROM monthly_quota mq
  LEFT JOIN profiles p ON mq.user_id = p.id
  WHERE p.id IS NULL;
  ```
  (repetir para user_oauth_tokens, google_sheets_exports, search_results_cache)
- **POST-migration:** FK diagnostic query do QA Gate Condicao 1
- Testar user deletion cascade: deletar user de teste e verificar que registros dependentes sao removidos
- Testar que login/signup nao quebra apos migration
- `python scripts/run_tests_safe.py` — 0 failures

## Notas Tecnicas

- Usar pattern NOT VALID + VALIDATE para evitar lock longo em tabelas grandes:
  ```sql
  ALTER TABLE monthly_quota
    DROP CONSTRAINT IF EXISTS fk_monthly_quota_user,
    ADD CONSTRAINT fk_monthly_quota_profiles
      FOREIGN KEY (user_id) REFERENCES profiles(id)
      ON DELETE CASCADE NOT VALID;

  ALTER TABLE monthly_quota VALIDATE CONSTRAINT fk_monthly_quota_profiles;
  ```
- Se DEBT-100 (DB-NEW-01/DB-NEW-04) revelou FKs ja validadas, ajustar escopo
- Rollback migration DEVE estar pre-escrita antes de aplicar
- DB-001 resolve 70% -> 100% de FK consistency (4 tabelas restantes de 14 totais)

## Dependencias

- **Depende de:** DEBT-100 (resultados de DB-NEW-01/DB-NEW-04 informam escopo exato)
- **Bloqueia:** Nenhuma

## Definition of Done

- [ ] Migration SQL implementada e aplicada
- [ ] Orphan detection executada PRE-migration (0 orphans)
- [ ] FK diagnostic query POST-migration (100% profiles)
- [ ] User deletion cascade testado
- [ ] Rollback migration documentada e testada em staging
- [ ] Testes passando
- [ ] Documentacao atualizada
