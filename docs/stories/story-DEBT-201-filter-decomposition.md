# Story DEBT-201: Decomposicao do Monolito filter/core.py (4.105 LOC)

## Metadados
- **Epic:** EPIC-DEBT-V2
- **Sprint:** 2 (Semana 3-4)
- **Prioridade:** P0 (Critico)
- **Esforco:** 22h
- **Agente:** @dev + @qa
- **Status:** PLANNED

## Descricao

Como equipe de desenvolvimento, queremos decompor o modulo `filter/core.py` (4.105 linhas) em submodulos coesos e remover codigo legado duplicado, para que alteracoes no pipeline de filtros nao causem regressoes em cascata nos 283 testes dependentes e novos desenvolvedores possam entender e modificar o codigo com seguranca.

## Debitos Incluidos

| ID | Debito | Horas | Dependencia |
|----|--------|-------|-------------|
| DEBT-SYS-007 | Duplicacao `filter_*.py` (raiz vs pacote `filter/`) | 4h | Nenhuma (fazer primeiro) |
| DEBT-SYS-001 | `filter/core.py` monolitico — `aplicar_todos_filtros()` monolitica | 16h | Depende de SYS-007 |
| DEBT-SYS-013 | `portal_transparencia_client.py` dead code (938 LOC) | 1h | Nenhuma (paralelo) |
| DEBT-SYS-014 | Clients experimentais dead code (`querido_diario_client.py`, `qd_extraction.py`) | 1h | Nenhuma (paralelo) |

## Criterios de Aceite

### Fase 1: Resolver Duplicacao (4h)
- [ ] Arquivos legados `filter_*.py` na raiz do backend removidos
- [ ] Todos os imports redirecionados para `filter/` package
- [ ] `filter/__init__.py` exporta todos os simbolos publicos para backward-compat
- [ ] Zero testes quebrados apos remocao

### Fase 2: Decompor filter/core.py (16h)
- [ ] `filter/core.py` decomposto em submodulos:
  - `filter/uf.py` — UF check (fastest)
  - `filter/value.py` — Value range check
  - `filter/keywords.py` — Keyword matching + density scoring
  - `filter/llm_classification.py` — LLM zero-match classification
  - `filter/status.py` — Status/date validation
  - `filter/viability.py` — Viability assessment (post-filter)
  - `filter/pipeline.py` — Orquestracao (aplicar_todos_filtros)
- [ ] `filter/__init__.py` mantem re-exports de TODAS as funcoes publicas (facade pattern)
- [ ] Nenhum arquivo resultante excede 800 LOC
- [ ] `filter/core.py` original excluido (sem arquivo vazio residual)

### Fase 3: Remover Dead Code (2h)
- [ ] `portal_transparencia_client.py` removido (938 LOC)
- [ ] `clients/querido_diario_client.py` e `clients/qd_extraction.py` removidos
- [ ] Nenhuma rota, import ou teste referencia os arquivos removidos

### Qualidade
- [ ] 283 testes em 14 arquivos `test_filter_*.py` passam sem NENHUMA mudanca de import
- [ ] Zero warnings de deprecation nos testes
- [ ] Coverage do modulo `filter/` >= baseline atual
- [ ] `pytest --timeout=30 -q` passa na suite completa (5131+ testes)

## Testes Requeridos

- [ ] `pytest tests/ -k "filter" --timeout=30` — todos os 283 testes passam
- [ ] `pytest --timeout=30 -q` — suite completa sem regressao
- [ ] Verificar que `from filter import aplicar_todos_filtros` continua funcionando (facade)
- [ ] Verificar que `from filter.core import ...` gera ImportError (modulo removido)
- [ ] Grep por imports de `portal_transparencia_client` e `querido_diario_client` retorna zero

## Notas Tecnicas

- **Padrao obrigatorio:** Facade pattern com re-exports em `filter/__init__.py`. Mock pattern existente deve ser preservado.
- **Ordem de execucao:** SYS-007 (duplicacao) ANTES de SYS-001 (decomposicao). SYS-013/014 podem ser feitos em paralelo.
- **Risco de regressao CRITICO:** 283 testes em 14 arquivos dependem deste modulo. Executar suite completa a cada submodulo extraido.
- **Estrategia recomendada:** Extrair um submodulo por vez, rodar testes, confirmar verde, prosseguir.

## Dependencias

- **DEBT-200** (Sprint 1) deve estar completa — shims de `main.py` removidos para evitar conflito
- **DEBT-SYS-007** bloqueia **DEBT-SYS-001** (resolver duplicacao antes de decompor)
