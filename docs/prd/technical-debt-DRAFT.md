# Technical Debt Assessment -- DRAFT

## SmartLic v0.5
**Data:** 2026-03-30
**Consolidado por:** @architect (Aria) -- Brownfield Discovery Phase 4
**Status:** DRAFT -- Pendente revisao dos especialistas

**Fontes:**
- `docs/architecture/system-architecture.md` (Phase 1 -- @architect)
- `supabase/docs/SCHEMA.md` (Phase 2 -- @data-engineer)
- `supabase/docs/DB-AUDIT.md` (Phase 2 -- @data-engineer)
- `docs/frontend/frontend-spec.md` (Phase 3 -- @ux-design-expert)

---

## Resumo Executivo

| Metrica | Valor |
|---------|-------|
| Total de debitos identificados | 38 |
| Criticos | 3 |
| Altos | 10 |
| Medios | 14 |
| Baixos | 11 |
| Esforco total estimado | ~180h |
| Debitos resolvidos (excluidos) | 3 (DB-TD-008, DB-TD-010, DB-TD-011) |

---

## 1. Debitos de Sistema (fonte: system-architecture.md)

### DEBT-SYS-001 -- `filter/core.py` monolitico (4.105 LOC)
- **Severidade:** Critica
- **Descricao:** Funcao `aplicar_todos_filtros()` e monolitica com 4.105 LOC. Decomposicao iniciada (filter_*.py) mas core.py continua sendo o maior arquivo do backend. Dificulta manutencao, testes isolados e debug.
- **Esforco estimado:** 16h
- **Area de impacto:** Backend -- pipeline de filtragem, testabilidade

### DEBT-SYS-002 -- SIGSEGV intermitente com C extensions (CRIT-SIGSEGV)
- **Severidade:** Critica
- **Descricao:** Restricoes de C extensions (uvloop, cryptography >= 47.0) por SIGSEGV intermitente em producao. Impede uso de uvloop, limita upgrades de cryptography, requer testes manuais de fork-safety com Gunicorn preload.
- **Esforco estimado:** 8h (investigacao periodica + testes de regressao)
- **Area de impacto:** Infra -- performance, seguranca (cryptography pinada)

### DEBT-SYS-003 -- `search_cache.py` complexo (2.564 LOC)
- **Severidade:** Alta
- **Descricao:** Logica multi-level (InMemory, Redis, Supabase, Local File) em um unico arquivo. Cache key migration (STORY-306) adicionou dual-read complexity. Dificil de testar e manter.
- **Esforco estimado:** 12h
- **Area de impacto:** Backend -- cache, resiliencia

### DEBT-SYS-004 -- `pncp_client.py` sobrecarregado (2.559 LOC)
- **Severidade:** Alta
- **Descricao:** Sync + async client, circuit breaker, retry logic, tudo no mesmo modulo. `pncp_client_resilient.py` existe como tentativa parcial de decomposicao.
- **Esforco estimado:** 10h
- **Area de impacto:** Backend -- data sources, resiliencia

### DEBT-SYS-005 -- `cron_jobs.py` com multiplas responsabilidades (2.251 LOC)
- **Severidade:** Alta
- **Descricao:** Cache cleanup, PNCP canary, session cleanup, cache warming, trial emails -- tudo em um unico modulo.
- **Esforco estimado:** 8h
- **Area de impacto:** Backend -- jobs, manutencao

### DEBT-SYS-006 -- `job_queue.py` sobrecarregado (2.229 LOC)
- **Severidade:** Alta
- **Descricao:** Mistura configuracao ARQ, gerenciamento de pool Redis e definicoes de jobs no mesmo arquivo.
- **Esforco estimado:** 6h
- **Area de impacto:** Backend -- jobs, worker

### DEBT-SYS-007 -- Duplicacao filter_*.py (raiz vs pacote)
- **Severidade:** Media
- **Descricao:** Arquivos legados na raiz (`filter_keywords.py`, `filter_llm.py`, etc.) coexistem com pacote `filter/`. Imports indiretos via `filter/__init__.py`.
- **Esforco estimado:** 4h
- **Area de impacto:** Backend -- organizacao de codigo

### DEBT-SYS-008 -- LLM timeout hardcoded em multiplos locais (DEBT-103)
- **Severidade:** Media
- **Descricao:** OpenAI timeout em `llm_arbiter.py` e config separado, nem sempre consistente.
- **Esforco estimado:** 2h
- **Area de impacto:** Backend -- LLM, configuracao

### DEBT-SYS-009 -- Feature flag sprawl (30+ flags sem governance)
- **Severidade:** Media
- **Descricao:** Flags acumuladas ao longo do tempo sem processo de lifecycle (create -> active -> deprecated -> removed) ou cleanup.
- **Esforco estimado:** 8h (implementar governance + audit inicial)
- **Area de impacto:** Backend -- config, manutencao

### DEBT-SYS-010 -- 99 migrations Supabase
- **Severidade:** Media
- **Descricao:** Volume alto de migrations sugere schema evolving rapidamente. Pode impactar deploy time e dificultar onboarding de devs.
- **Esforco estimado:** 16h (squash plan)
- **Area de impacto:** Infra -- deploy, DX

### DEBT-SYS-011 -- Schemas espalhados entre diretorio e raiz
- **Severidade:** Media
- **Descricao:** `schemas/` directory com 12 files + `schemas_stats.py` + `schema_contract.py` na raiz do backend.
- **Esforco estimado:** 2h
- **Area de impacto:** Backend -- organizacao

### DEBT-SYS-012 -- Backward-compat shims em `main.py`
- **Severidade:** Baixa
- **Descricao:** Re-exports para testes legados. Funcional mas adiciona indiracao desnecessaria.
- **Esforco estimado:** 1h
- **Area de impacto:** Backend -- DX

### DEBT-SYS-013 -- `portal_transparencia_client.py` sem uso ativo (938 LOC)
- **Severidade:** Baixa
- **Descricao:** Client parece ser preparacao futura ou experimental. Sem evidencia de uso em rotas ativas.
- **Esforco estimado:** 1h (remover ou mover para branch experimental)
- **Area de impacto:** Backend -- dead code

### DEBT-SYS-014 -- Clients experimentais em clients/
- **Severidade:** Baixa
- **Descricao:** `querido_diario_client.py` e `qd_extraction.py` aparentam ser experimentais. Sem rota ativa que os consuma.
- **Esforco estimado:** 1h
- **Area de impacto:** Backend -- dead code

### DEBT-SYS-015 -- Dual-hash transition em auth.py
- **Severidade:** Baixa
- **Descricao:** Window de 1h para compatibilidade de cache keys durante migracao. Pode ser removido apos estabilizacao.
- **Esforco estimado:** 1h
- **Area de impacto:** Backend -- auth, cache

> PENDENTE: Validacao final do @architect

---

## 2. Debitos de Database (fonte: DB-AUDIT.md)

### DEBT-DB-001 -- `alerts.filters` JSONB sem CHECK constraint de tamanho
- **Severidade:** Baixa
- **Descricao:** Coluna JSONB sem governance de tamanho. Possivel bloat se filtros crescerem sem limite.
- **Esforco estimado:** 1h
- **Area de impacto:** Database -- storage, performance

### DEBT-DB-002 -- `ingestion_runs.metadata` JSONB sem CHECK constraint
- **Severidade:** Baixa
- **Descricao:** Metadata pode crescer sem limite. 85% das colunas JSONB criticas tem CHECK, estas 2 faltam.
- **Esforco estimado:** 1h
- **Area de impacto:** Database -- storage

### DEBT-DB-003 -- Trigger prefix inconsistente (tr_/trg_/trigger_)
- **Severidade:** Baixa
- **Descricao:** 3 prefixos diferentes para triggers. Consolidado parcialmente em DEBT-001 mas nao completamente padronizado.
- **Esforco estimado:** 2h
- **Area de impacto:** Database -- manutencao, convencoes

### DEBT-DB-004 -- RLS policy naming inconsistente
- **Severidade:** Baixa
- **Descricao:** Mix de snake_case e descritivo em ingles para nomes de RLS policies. Dificulta auditoria.
- **Esforco estimado:** 3h
- **Area de impacto:** Database -- governanca, auditoria

### DEBT-DB-005 -- Hardcoded Stripe price IDs em migrations
- **Severidade:** Media
- **Descricao:** Stripe price IDs hardcoded em migrations. Impede staging/dev automatico. Seed script existe mas IDs em producao estao embutidos.
- **Esforco estimado:** 4h
- **Area de impacto:** Database -- billing, ambientes dev/staging

### DEBT-DB-006 -- Inconsistencia semantica soft/hard delete em pncp_raw_bids
- **Severidade:** Baixa
- **Descricao:** `pncp_raw_bids` usa soft delete (is_active=false) mas `purge_old_bids` faz hard delete em registros antigos. Semantica mista.
- **Esforco estimado:** 2h
- **Area de impacto:** Database -- datalake, retencao

### DEBT-DB-007 -- health_checks e incidents sem policies de usuario admin
- **Severidade:** Baixa
- **Descricao:** Admin nao pode ver dados via dashboard -- precisa de service_role. Falta policy SELECT para admin.
- **Esforco estimado:** 1h
- **Area de impacto:** Database -- admin, observabilidade

### DEBT-DB-009 -- Nenhuma migration tem rollback formal
- **Severidade:** Media
- **Descricao:** Apenas migration 010 tem rollback documentado. 99 migrations sem rollback script dificultam reversao em emergencia.
- **Esforco estimado:** 8h+ (rollback para 5 tabelas criticas)
- **Area de impacto:** Database -- resiliencia, deploy

> PENDENTE: Revisao do @data-engineer (Fase 5)

---

## 3. Debitos de Frontend/UX (fonte: frontend-spec.md)

### DEBT-FE-001 -- `useSearchOrchestration` mega-hook (TD-001)
- **Severidade:** Alta
- **Descricao:** Mega-hook com 200+ linhas que orquestra 9+ sub-hooks, estado de trial, modais, tours e mais. Risco de regressao alto. Dificil de testar unitariamente.
- **Esforco estimado:** 12h
- **Impacto UX:** Risco de regressao em feature principal

### DEBT-FE-002 -- ViabilityBadge usa `title` para dados criticos (TD-008 + A11Y-002)
- **Severidade:** Alta
- **Descricao:** Breakdown de fatores de viabilidade (informacao critica para decisao do usuario) depende de `title` tooltip, que nao funciona em mobile/touch e nao e acessivel.
- **Esforco estimado:** 4h
- **Impacto UX:** Acessibilidade -- usuarios mobile e screen readers nao acessam dados de viabilidade

### DEBT-FE-003 -- Sem `aria-live` para resultados de busca (TD-009 + A11Y-004)
- **Severidade:** Media
- **Descricao:** Resultados de busca nao anunciam dinamicamente numero de resultados via `aria-live`. 12 banners de status nao usam `role="alert"` ou `aria-live` consistentemente.
- **Esforco estimado:** 4h
- **Impacto UX:** Acessibilidade -- screen readers nao recebem feedback de busca

### DEBT-FE-004 -- 12 banners na busca -- cognitive overload (TD-002)
- **Severidade:** Media
- **Descricao:** 12 tipos de banners contextuais na pagina de busca. Excesso de informacao para usuario medio. Sem sistema de prioridade entre banners.
- **Esforco estimado:** 8h
- **Impacto UX:** Sobrecarga cognitiva, confusao

### DEBT-FE-005 -- /admin usa useState + fetch manual (TD-003)
- **Severidade:** Media
- **Descricao:** Inconsistente com resto do app que usa SWR. Risco de stale data e falta de revalidation automatica.
- **Esforco estimado:** 4h
- **Impacto UX:** Dados desatualizados para admin

### DEBT-FE-006 -- Landmarks HTML inconsistentes (A11Y-003)
- **Severidade:** Media
- **Descricao:** Nem todas as paginas protegidas tem `<main>`, `<nav>` e `<footer>` marcados corretamente. `/buscar` usa `<main id="buscar-content">` mas padrao nao e consistente.
- **Esforco estimado:** 3h
- **Impacto UX:** Acessibilidade -- navegacao por landmarks prejudicada

### DEBT-FE-007 -- Campos de busca sem `aria-describedby` (A11Y-008)
- **Severidade:** Media
- **Descricao:** Hints como "Selecione um setor para iniciar" e "Minimo 3 caracteres" nao estao linkados via `aria-describedby` aos inputs.
- **Esforco estimado:** 2h
- **Impacto UX:** Acessibilidade -- falta de contexto para screen readers

### DEBT-FE-008 -- Feature gates hardcoded (DEBT-FE-012)
- **Severidade:** Media
- **Descricao:** Apenas `alertas` e gated. Sem feature flag service para controle dinamico no frontend.
- **Esforco estimado:** 6h
- **Impacto UX:** Nenhum direto (impacto em DX e flexibilidade)

### DEBT-FE-009 -- SVGs inline vs icon library (TD-004)
- **Severidade:** Baixa
- **Descricao:** SVGs inline em MobileDrawer, BottomNav, ErrorStates ao inves de lucide-react (ja e dependencia).
- **Esforco estimado:** 3h
- **Impacto UX:** Bundle size, manutencao

### DEBT-FE-010 -- Raw hex values ao inves de tokens semanticos (DEBT-012)
- **Severidade:** Baixa
- **Descricao:** Alguns componentes usam raw hex ao inves dos tokens semanticos definidos no tailwind.config.ts.
- **Esforco estimado:** 4h
- **Impacto UX:** Inconsistencia visual sutil

### DEBT-FE-011 -- Tipo `any` em API proxy routes (TD-005)
- **Severidade:** Media
- **Descricao:** Potencial uso de `any` em rotas de proxy API, quebrando type safety.
- **Esforco estimado:** 4h
- **Impacto UX:** Nenhum direto (impacto em seguranca de tipos)

### DEBT-FE-012 -- Focus order em BuscarModals (A11Y-006)
- **Severidade:** Baixa
- **Descricao:** Multiplos modais potencialmente sobrepostos podem confundir focus management.
- **Esforco estimado:** 2h
- **Impacto UX:** Acessibilidade -- foco perdido em cenarios edge

### DEBT-FE-013 -- Sem testes de acessibilidade automatizados
- **Severidade:** Media
- **Descricao:** `@axe-core/playwright` e devDependency mas nao ha evidencia de uso sistematico nos E2E tests. Gaps de a11y nao sao detectados automaticamente.
- **Esforco estimado:** 6h (integrar em testes criticos)
- **Impacto UX:** Regressoes de acessibilidade nao detectadas

### DEBT-FE-014 -- Sem suporte a prefers-reduced-motion
- **Severidade:** Baixa
- **Descricao:** Animacoes Framer Motion e CSS nao verificam `prefers-reduced-motion` sistematicamente. Usuarios com sensibilidade a movimento afetados.
- **Esforco estimado:** 3h
- **Impacto UX:** Acessibilidade -- desconforto para usuarios sensiveis

### DEBT-FE-015 -- SEO pages programaticas com conteudo thin (TD-006)
- **Severidade:** Baixa
- **Descricao:** Paginas `/como-*` podem ter conteudo duplicado ou thin, arriscando penalidade de SEO.
- **Esforco estimado:** 4h
- **Impacto UX:** SEO

> PENDENTE: Revisao do @ux-design-expert (Fase 6)

---

## 4. Matriz Preliminar de Priorizacao

| ID | Debito | Area | Severidade | Impacto | Esforco (h) | Prioridade |
|----|--------|------|------------|---------|-------------|------------|
| DEBT-SYS-001 | filter/core.py monolitico (4.105 LOC) | Backend | Critica | Manutencao, testes | 16 | P0 |
| DEBT-SYS-002 | SIGSEGV C extensions (CRIT-SIGSEGV) | Infra | Critica | Estabilidade producao | 8 | P0 |
| DEBT-FE-002 | ViabilityBadge title inacessivel | Frontend | Alta | A11y critica | 4 | P0 |
| DEBT-SYS-003 | search_cache.py (2.564 LOC) | Backend | Alta | Cache, resiliencia | 12 | P1 |
| DEBT-SYS-004 | pncp_client.py (2.559 LOC) | Backend | Alta | Data sources | 10 | P1 |
| DEBT-FE-001 | useSearchOrchestration mega-hook | Frontend | Alta | Regressao busca | 12 | P1 |
| DEBT-SYS-005 | cron_jobs.py multiplas responsabilidades | Backend | Alta | Jobs | 8 | P1 |
| DEBT-SYS-006 | job_queue.py sobrecarregado | Backend | Alta | Worker | 6 | P1 |
| DEBT-DB-009 | Nenhuma migration com rollback | Database | Media | Resiliencia deploy | 8 | P1 |
| DEBT-DB-005 | Stripe price IDs hardcoded | Database | Media | Ambientes dev | 4 | P1 |
| DEBT-FE-003 | Sem aria-live para resultados busca | Frontend | Media | A11y | 4 | P2 |
| DEBT-FE-004 | 12 banners na busca | Frontend | Media | Cognitive overload | 8 | P2 |
| DEBT-FE-005 | /admin sem SWR | Frontend | Media | Stale data | 4 | P2 |
| DEBT-FE-006 | Landmarks HTML inconsistentes | Frontend | Media | A11y | 3 | P2 |
| DEBT-FE-007 | Campos sem aria-describedby | Frontend | Media | A11y | 2 | P2 |
| DEBT-FE-008 | Feature gates hardcoded | Frontend | Media | DX | 6 | P2 |
| DEBT-FE-011 | Tipo any em API proxies | Frontend | Media | Type safety | 4 | P2 |
| DEBT-FE-013 | Sem testes a11y automatizados | Frontend | Media | Regressao a11y | 6 | P2 |
| DEBT-SYS-007 | Duplicacao filter_*.py | Backend | Media | Organizacao | 4 | P2 |
| DEBT-SYS-008 | LLM timeout hardcoded | Backend | Media | Config | 2 | P2 |
| DEBT-SYS-009 | Feature flag sprawl | Backend | Media | Manutencao | 8 | P2 |
| DEBT-SYS-010 | 99 migrations Supabase | Infra | Media | Deploy, DX | 16 | P2 |
| DEBT-SYS-011 | Schemas espalhados | Backend | Media | Organizacao | 2 | P2 |
| DEBT-DB-001 | alerts.filters JSONB sem CHECK | Database | Baixa | Storage | 1 | P3 |
| DEBT-DB-002 | ingestion_runs.metadata sem CHECK | Database | Baixa | Storage | 1 | P3 |
| DEBT-DB-003 | Trigger prefix inconsistente | Database | Baixa | Convencoes | 2 | P3 |
| DEBT-DB-004 | RLS policy naming inconsistente | Database | Baixa | Auditoria | 3 | P3 |
| DEBT-DB-006 | Soft/hard delete inconsistente | Database | Baixa | Semantica | 2 | P3 |
| DEBT-DB-007 | health_checks sem policy admin | Database | Baixa | Admin | 1 | P3 |
| DEBT-FE-009 | SVGs inline vs lucide-react | Frontend | Baixa | Bundle | 3 | P3 |
| DEBT-FE-010 | Raw hex vs tokens semanticos | Frontend | Baixa | Consistencia visual | 4 | P3 |
| DEBT-FE-012 | Focus order em modais | Frontend | Baixa | A11y edge case | 2 | P3 |
| DEBT-FE-014 | Sem prefers-reduced-motion | Frontend | Baixa | A11y | 3 | P3 |
| DEBT-FE-015 | SEO pages thin content | Frontend | Baixa | SEO | 4 | P3 |
| DEBT-SYS-012 | Backward-compat shims main.py | Backend | Baixa | DX | 1 | P3 |
| DEBT-SYS-013 | portal_transparencia_client sem uso | Backend | Baixa | Dead code | 1 | P3 |
| DEBT-SYS-014 | Clients experimentais | Backend | Baixa | Dead code | 1 | P3 |
| DEBT-SYS-015 | Dual-hash transition auth.py | Backend | Baixa | Cleanup | 1 | P3 |

---

## 5. Dependencias entre Debitos

### Cadeia 1: Decomposicao de Modulos Backend
```
DEBT-SYS-001 (filter/core.py) ──depende de──> DEBT-SYS-007 (resolver duplicacao filter_*.py primeiro)
DEBT-SYS-004 (pncp_client.py) ──independente── (pode ser feito em paralelo)
DEBT-SYS-005 (cron_jobs.py) ──depende de──> DEBT-SYS-006 (job_queue.py -- ambos compartilham logica ARQ)
```

### Cadeia 2: Acessibilidade Frontend
```
DEBT-FE-002 (ViabilityBadge) ──independente──
DEBT-FE-003 (aria-live) ──depende de──> DEBT-FE-004 (consolidar banners antes de adicionar aria-live)
DEBT-FE-006 (landmarks) ──independente──
DEBT-FE-013 (testes a11y) ──deve ser feito APOS todos os outros a11y debts──
```

### Cadeia 3: Database Governance
```
DEBT-DB-001/002 (JSONB CHECK) ──independentes── (podem ser feitos juntos em 1 migration)
DEBT-DB-009 (rollback scripts) ──depende de──> DEBT-SYS-010 (squash migrations -- mais facil criar rollbacks apos squash)
DEBT-DB-005 (Stripe IDs) ──independente──
```

### Cadeia 4: Feature Flag Governance
```
DEBT-SYS-009 (backend flag sprawl) ──complementa──> DEBT-FE-008 (frontend feature gates)
```
Idealmente resolvidos juntos para criar um sistema unificado de feature flags.

---

## 6. Perguntas para Especialistas

### Para @data-engineer (Fase 5):

1. **DEBT-DB-009 (rollback):** Qual e a estrategia de rollback atual para emergencias? Ha algum procedimento manual documentado? Quais sao as 5 tabelas mais criticas que precisam de rollback first?

2. **DEBT-DB-005 (Stripe IDs):** O seed script existente cobre todos os cenarios de staging? O que falta para que um ambiente de dev tenha precos Stripe funcionais sem hardcode?

3. **DEBT-DB-006 (soft/hard delete):** A inconsistencia entre is_active=false (soft) e hard delete via purge causa algum problema real em queries ou metricas de observabilidade? Ou e apenas incoerencia semantica?

4. **DEBT-SYS-010 (99 migrations):** Ha algum risco em fazer squash de migrations? Alguma migration tem side-effects (data migration, seed data) que seriam perdidos?

5. **DEBT-DB-001/002 (JSONB):** Qual tamanho maximo razoavel para `alerts.filters` e `ingestion_runs.metadata`? 512 KB como as outras colunas ou valor diferente?

### Para @ux-design-expert (Fase 6):

1. **DEBT-FE-004 (12 banners):** Qual e a hierarquia de prioridade recomendada para os banners? Quais podem ser consolidados? Algum pode ser removido sem perda de valor?

2. **DEBT-FE-002 (ViabilityBadge):** Qual padrao de tooltip acessivel recomendado? Radix Tooltip, popover customizado, ou expandir inline? O breakdown precisa estar visivel sem interacao?

3. **DEBT-FE-001 (useSearchOrchestration):** A decomposicao sugerida (useSearchModals, useSearchTours, useTrialOrchestration) faz sentido do ponto de vista de UX? Algum estado compartilhado entre essas areas impede a separacao?

4. **DEBT-FE-014 (prefers-reduced-motion):** Quais animacoes sao essenciais para feedback de interacao e quais sao puramente decorativas? Desabilitar TODAS com reduced-motion ou manter animacoes funcionais?

5. **DEBT-FE-010 (tokens semanticos):** Quais componentes tem as maiores inconsistencias visuais por usar raw hex? Existe um inventory dos offenders?

### Para @qa (Fase 7):

1. **Cobertura de testes dos modulos grandes:** `filter/core.py` (4.105 LOC), `search_cache.py` (2.564 LOC) e `pncp_client.py` (2.559 LOC) tem cobertura adequada? A decomposicao pode ser feita com seguranca?

2. **Feature flags em testes:** Os 30+ feature flags sao testados em ambos os estados (on/off)? Ha risco de combinacoes nao testadas?

3. **Testes de acessibilidade:** `@axe-core/playwright` esta instalado mas sem uso sistematico. Qual seria o subconjunto minimo de paginas para adicionar assertions de a11y?

4. **Rollback testing:** Se criarmos rollback scripts (DEBT-DB-009), como validamos que o rollback funciona sem afetar dados de producao?

5. **Regression risk:** Quais dos 38 debitos tem maior risco de causar regressao ao serem corrigidos? Que testes adicionais seriam necessarios?

---

**Proximo passo:** Este DRAFT sera revisado por cada especialista em suas respectivas fases:
- Fase 5: @data-engineer valida debitos de database
- Fase 6: @ux-design-expert valida debitos de frontend/UX
- Fase 7: @qa avalia risco de regressao e prioriza testes
- Fase 8: @analyst + @pm consolidam versao final com ROI estimado
