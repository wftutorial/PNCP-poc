# Story DEBT-205: Acessibilidade Avancada + Feature Flag Governance

## Metadados
- **Epic:** EPIC-DEBT-V2
- **Sprint:** 6 (Semana 11-12)
- **Prioridade:** P2
- **Esforco:** 28h
- **Agente:** @architect + @dev + @qa
- **Status:** PLANNED

## Descricao

Como equipe de produto, queremos implementar governanca unificada de feature flags (backend + frontend) e resolver os debitos de acessibilidade avancados (indicadores por cor, pipeline kanban, testes a11y), para que o controle de features seja centralizado e auditavel, e a plataforma atinja conformidade WCAG 2.1 AA em 15 de 22 paginas.

## Debitos Incluidos

| ID | Debito | Horas | Responsavel |
|----|--------|-------|-------------|
| DEBT-SYS-009 | Feature flag sprawl — 30+ flags sem governance | 8h | @architect + @dev |
| DEBT-FE-008 | Feature gates hardcoded — apenas `alertas` gated | 6h | @dev |
| DEBT-FE-018 | Indicadores de viabilidade apenas por cor (WCAG 1.4.1) | 3h | @dev |
| DEBT-FE-020 | Pipeline kanban sem anuncios de drag para screen readers | 4h | @dev |
| DEBT-FE-013 | Expandir testes a11y de 5 para 10 paginas | 3h | @qa |
| DEBT-SYS-002 | Investigacao periodica SIGSEGV — testar cryptography 47.x | 4h | @devops |

## Criterios de Aceite

### Feature Flag Governance (14h — SYS-009 + FE-008)
- [ ] Inventario completo de 30+ feature flags com documentacao (nome, descricao, owner, data de criacao)
- [ ] Endpoint API `/feature-flags` criado para consulta de flags ativas
- [ ] Frontend consome flags via API (nao mais hardcoded)
- [ ] Lifecycle definido: cada flag tem data de expiracao ou condicao de remocao
- [ ] `test_feature_flag_matrix.py` criado com 10 flags criticas testadas em on/off
- [ ] 5 combinacoes criticas de flags testadas
- [ ] Config centralizada em `config.py` (backend) + API consumer (frontend)
- [ ] Flags "fantasma" (existem em um lado mas nao no outro) eliminadas
- [ ] 100% das flags com pelo menos 1 teste on e 1 teste off

### Acessibilidade — Indicadores por Cor (3h — FE-018)
- [ ] ViabilityBadge e outros badges usam icones/texto alem de cor
- [ ] Padroes: verde + checkmark, amarelo + warning icon, vermelho + X icon
- [ ] Daltonismo simulado (Chromatic) confirma distinguibilidade
- [ ] Conformidade WCAG 1.4.1 (Use of Color)

### Acessibilidade — Pipeline Kanban (4h — FE-020)
- [ ] `@dnd-kit` configurado com `aria-roledescription` para drag items
- [ ] Anuncios de drag: `onDragStart` ("Movendo item X"), `onDragEnd` ("Item X movido para coluna Y")
- [ ] Screen reader (NVDA/VoiceOver) anuncia acoes de drag corretamente
- [ ] axe-core zero violacoes na pagina `/pipeline`

### Expandir Testes A11y (3h — FE-013)
- [ ] axe-core E2E expandido de 5 para 10 paginas:
  - Existentes: `/`, `/login`, `/signup`, `/buscar`, `/dashboard`
  - Novos: `/pipeline`, `/historico`, `/conta`, `/planos`, `/ajuda`
- [ ] Zero violacoes criticas em todas as 10 paginas
- [ ] Relatorio de violacoes menores documentado para backlog futuro

### Investigacao SIGSEGV (4h — SYS-002)
- [ ] cryptography 47.x testado em staging environment
- [ ] Resultado documentado: funciona sem SIGSEGV? Quais versoes?
- [ ] CVEs na faixa 46.x verificados e documentados
- [ ] Recomendacao de acao: upgrade, manter pin, ou aguardar

## Testes Requeridos

- [ ] `test_feature_flag_matrix.py` — 10 flags criticas em on/off
- [ ] 5 combinacoes de flags testadas (ex: DATALAKE_ENABLED=false + LLM_ZERO_MATCH_ENABLED=true)
- [ ] axe-core E2E em 10 paginas
- [ ] Screen reader test manual em `/pipeline` (drag announcements)
- [ ] Simulacao de daltonismo em badges de viabilidade
- [ ] `pytest --timeout=30 -q` — suite completa backend
- [ ] `npm test` — suite completa frontend

## Notas Tecnicas

- **Feature flags cross-cutting:** DEBT-SYS-009 e DEBT-FE-008 devem ser resolvidos JUNTOS. Criar API endpoint `/feature-flags` que retorna todas as flags ativas com metadata. Frontend consome esse endpoint via SWR com cache de 5 min.
- **30+ flags existentes:** `DATALAKE_ENABLED`, `DATALAKE_QUERY_ENABLED`, `LLM_ZERO_MATCH_ENABLED`, `LLM_ARBITER_ENABLED`, `VIABILITY_ASSESSMENT_ENABLED`, `SYNONYM_MATCHING_ENABLED`, etc. Listar todas em `config.py`.
- **Pipeline kanban:** `@dnd-kit` suporta accessibility nativo. Verificar docs para `DndContext` props de accessibility.
- **SIGSEGV:** Investigacao periodica. Nao bloquear a story se cryptography 47.x ainda falhar — documentar e agendar proxima verificacao.

## Dependencias

- DEBT-FE-013 (testes a11y) depende de DEBT-FE-018 e DEBT-FE-020 estarem completos primeiro
- DEBT-FE-008 (frontend gates) complementa DEBT-SYS-009 (backend flags) — fazer juntos
- Recomendado: todas as stories anteriores (Sprint 1-5) completas
