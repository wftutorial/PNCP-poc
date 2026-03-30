# Story DEBT-210: Backlog Oportunistico — Database Performance Optimization

## Metadados
- **Epic:** EPIC-DEBT-V2
- **Sprint:** Backlog (resolver quando metricas justificarem)
- **Prioridade:** P2-P3
- **Esforco:** 10h
- **Agente:** @data-engineer
- **Status:** PLANNED

## Descricao

Como equipe de dados, queremos otimizar operacoes de banco de dados que atualmente funcionam mas podem se tornar gargalos com o crescimento (upsert row-by-row, tsvector duplicado), para que a plataforma escale sem degradacao de performance no pipeline de ingestao.

## Debitos Incluidos

| ID | Debito | Horas | Trigger para Resolver |
|----|--------|-------|-----------------------|
| DEBT-DB-NEW-003 | `upsert_pncp_raw_bids` usa loop row-by-row — 500 round-trips por batch | 4h | Quando ingestao > 1000 rows/batch |
| DEBT-DB-NEW-004 | `search_datalake` calcula `to_tsvector` 2x por row | 2h | Quando `pncp_raw_bids` > 100K rows |
| DEBT-SYS-002 | SIGSEGV — 4h adicionais de backlog (upgrade quando estavel) | 4h | Quando cryptography 47.x estavel |

## Criterios de Aceite

### Otimizar Upsert (4h — DB-NEW-003)
- [ ] `upsert_pncp_raw_bids` RPC reescrito para operacao em bloco (batch INSERT ... ON CONFLICT)
- [ ] Sem round-trips individuais ao planner por cada row
- [ ] content_hash dedup preservado (nao duplicar registros)
- [ ] Benchmark: tempo de ingestao de 500 rows >= 30% menor
- [ ] Edge cases: rows com content_hash duplicado dentro do mesmo batch

### Otimizar tsvector (2h — DB-NEW-004)
- [ ] Benchmark de CPU antes da otimizacao (`EXPLAIN ANALYZE` em `search_datalake`)
- [ ] Opcao A: Coluna `tsv` pre-computada com trigger de atualizacao (trade-off: +storage)
- [ ] Opcao B: Manter 2x se benchmark mostrar impacto < 5% (decisao documentada)
- [ ] Se Opcao A: indice GIN atualizado para usar coluna pre-computada

### Upgrade cryptography (4h — SYS-002 backlog)
- [ ] Executar quando DEBT-206 confirmar que 47.x e estavel
- [ ] Pin de versao removido de `requirements.txt`
- [ ] Restricoes de uvloop removidas
- [ ] Suite completa de testes em staging
- [ ] Monitoramento de SIGSEGV por 48h pos-upgrade

## Testes Requeridos

- [ ] Benchmark upsert: 500 rows antes/depois — sem duplicatas, tempo >= 30% menor
- [ ] `EXPLAIN ANALYZE` em `search_datalake` — documentar custo de tsvector
- [ ] `pytest -k "test_ingestion" --timeout=60` — testes de ingestao passam
- [ ] `pytest -k "test_datalake" --timeout=30` — testes de datalake query passam
- [ ] Se upgrade cryptography: `pytest --timeout=30 -q` + monitoramento 48h

## Notas Tecnicas

- **Upsert row-by-row:** O RPC atual faz 500 round-trips internos ao planner. PostgreSQL suporta `INSERT ... ON CONFLICT DO UPDATE` em batch. A RPC deve receber array de rows e fazer upsert unico.
- **tsvector 2x:** Trade-off entre storage (coluna pre-computada) e CPU (calcular 2x por query). Benchmark primeiro antes de decidir.
- **Dependencia de DEBT-DB-NEW-005:** O bloat monitoring (resolvido no Sprint 4) fornece dados que ajudam a decidir prioridade destes itens.
- **NAO resolver proativamente:** Estes itens so devem ser trabalhados quando metricas de producao mostrarem degradacao real.

## Dependencias

- DEBT-203 (Sprint 4) resolve DEBT-DB-NEW-005 (bloat monitoring) que fornece dados para priorizar
- DEBT-206 (Sprint 6) investiga SIGSEGV — resultado determina timing do upgrade
- Sem bloqueadores — pode ser feito a qualquer momento quando trigger justificar
