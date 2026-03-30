# Story DEBT-208: Backlog Oportunistico — Backend Schema e Migrations

## Metadados
- **Epic:** EPIC-DEBT-V2
- **Sprint:** Backlog (resolver durante feature work)
- **Prioridade:** P2-P3
- **Esforco:** 6h
- **Agente:** @dev + @data-engineer
- **Status:** PLANNED

## Descricao

Como equipe de desenvolvimento, queremos consolidar schemas espalhados entre diretorio e raiz do backend e criar schema snapshot como alternativa ao squash de migrations, para que a estrutura do projeto seja mais previsivel e novos desenvolvedores possam entender o schema rapidamente.

## Debitos Incluidos

| ID | Debito | Horas | Trigger para Resolver |
|----|--------|-------|-----------------------|
| DEBT-SYS-010 | 99 migrations — schema snapshot via `pg_dump --schema-only` | 4h | Quando migrations > 150 |
| DEBT-SYS-011 | Schemas espalhados (`schemas/` + `schemas_stats.py` + `schema_contract.py` na raiz) | 2h | Durante refactor de schemas |

## Criterios de Aceite

### Schema Snapshot (4h)
- [ ] Script `scripts/create-schema-snapshot.sh` criado
- [ ] Gera `supabase/snapshots/schema_YYYYMMDD.sql` via `pg_dump --schema-only`
- [ ] Snapshot atual gerado e commitado como referencia
- [ ] Documentacao de uso: como gerar, quando gerar, como comparar com versao anterior
- [ ] **NAO fazer squash de migrations** — riscos com data migrations, triggers e seed data

### Consolidacao de Schemas (2h)
- [ ] `schemas_stats.py` movido para `schemas/stats.py`
- [ ] `schema_contract.py` movido para `schemas/contract.py`
- [ ] Imports atualizados em todos os modulos que referenciam
- [ ] Re-exports em modulos originais para backward-compat temporario (1 sprint)
- [ ] Testes passam sem alteracao de import

## Testes Requeridos

- [ ] `pytest -k "test_schema" --timeout=30` — testes de schema passam
- [ ] `pytest --timeout=30 -q` — suite completa
- [ ] Schema snapshot gerado com sucesso em ambiente local

## Notas Tecnicas

- **Squash desaconselhado:** @data-engineer desaconselhou squash de migrations por riscos com data migrations, triggers e seed data. Schema snapshot e alternativa segura.
- **Schemas espalhados:** Problema cosmetico mas confuso para novos desenvolvedores. Consolidar gradualmente.

## Dependencias

- Nenhuma — independente de todas as outras stories
- Resolver quando conveniente durante feature work
