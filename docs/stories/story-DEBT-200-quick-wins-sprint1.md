# Story DEBT-200: Quick Wins — Acessibilidade, Cleanup e Governanca DB

## Metadados
- **Epic:** EPIC-DEBT-V2
- **Sprint:** 1 (Semana 1-2)
- **Prioridade:** P2-P3
- **Esforco:** 14h
- **Agente:** @dev + @data-engineer
- **Status:** PLANNED

## Descricao

Como equipe de desenvolvimento, queremos resolver os debitos de baixo risco e retorno imediato identificados na auditoria tecnica, para que a plataforma fique mais acessivel, o codigo mais limpo, e o banco de dados com governanca completa — tudo sem risco de regressao significativo.

## Debitos Incluidos

| ID | Debito | Horas | Responsavel |
|----|--------|-------|-------------|
| DEBT-DB-002 | `ingestion_runs.metadata` JSONB sem CHECK constraint | 0.5h | @data-engineer |
| DEBT-DB-NEW-001 | COMMENT incorreto em `pncp_raw_bids.is_active` | 0.5h | @data-engineer |
| DEBT-DB-007 | `health_checks` e `incidents` sem RLS policy admin | 1h | @data-engineer |
| DEBT-FE-016 | IDs duplicados de `main-content` — skip navigation quebrado | 1h | @dev |
| DEBT-FE-007 | Campos de busca sem `aria-describedby` | 2h | @dev |
| DEBT-FE-003 | Sem `aria-live` em 6 banners restantes | 2h | @dev |
| DEBT-FE-006 | Landmarks HTML — IDs nao padronizados | 2h | @dev |
| DEBT-FE-019 | Shepherd.js carregado eagerly (~15KB) | 2h | @dev |
| DEBT-SYS-008 | LLM timeout hardcoded em multiplos locais | 2h | @dev |
| DEBT-SYS-012 | Backward-compat shims em `main.py` | 1h | @dev |
| DEBT-SYS-015 | Dual-hash transition em `auth.py` | 1h | @dev |

## Criterios de Aceite

### Database (2h)
- [ ] Migration criada com CHECK constraint para `ingestion_runs.metadata` (limite 512KB, consistente com outras colunas JSONB)
- [ ] COMMENT de `pncp_raw_bids.is_active` corrigido para refletir comportamento real (hard delete pelo purge)
- [ ] RLS policies criadas para `health_checks` e `incidents` permitindo acesso admin sem `service_role`
- [ ] JSONB Size Governance atinge 100% (todas colunas JSONB com CHECK)

### Frontend Acessibilidade (7h)
- [ ] Todos os IDs `main-content` unificados — um unico `<main id="main-content">` por pagina
- [ ] Skip navigation (`#main-content`) funciona em `/buscar` e todas as paginas com header
- [ ] Campos de busca possuem `aria-describedby` linkando hints descritivos
- [ ] 6 banners faltantes possuem `aria-live="polite"` ou `role="alert"` conforme contexto
- [ ] Landmarks HTML usam IDs padronizados (`main-content`, `site-header`, `site-footer`, `site-nav`)
- [ ] Shepherd.js carregado via `dynamic(() => import(...), { ssr: false })` — nao incluso no bundle inicial
- [ ] Bundle size da pagina principal reduzido em pelo menos 15KB

### Backend Cleanup (4h)
- [ ] LLM timeout centralizado em `config.py` como `LLM_TIMEOUT_SECONDS` — removidos hardcodes de `llm_arbiter.py` e `llm.py`
- [ ] Backward-compat shims removidos de `main.py` (re-exports para testes legados)
- [ ] Dual-hash transition removido de `auth.py` (window de compatibilidade expirada)

### Geral
- [ ] Todos os 5131+ testes backend passam sem falhas
- [ ] Todos os 2681+ testes frontend passam sem falhas
- [ ] Zero breaking changes em imports existentes

## Testes Requeridos

- [ ] `pytest -k "test_llm" --timeout=30` — 142 testes LLM passam com timeout centralizado
- [ ] `pytest -k "test_auth" --timeout=30` — testes de auth passam sem dual-hash
- [ ] `npm test` — suite completa frontend passa
- [ ] axe-core audit em `/buscar` confirma zero violacoes de `aria-live` e landmarks
- [ ] Lighthouse check confirma reducao de bundle (Shepherd.js lazy)

## Notas Tecnicas

- Todas as mudancas sao paralelizaveis — nenhuma dependencia interna nesta story
- Database: criar 1 migration unica com as 3 correcoes DB (constraint + comment + policies)
- Frontend: `DEBT-FE-003` pode usar a mesma abordagem dos 28+ `aria-live` ja existentes no codebase
- Backend: verificar que nenhum teste importa diretamente os shims de `main.py` antes de remover

## Dependencias

- Nenhuma — esta story pode iniciar imediatamente
