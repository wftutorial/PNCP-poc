# Technical Debt Assessment — FINAL

## SmartLic v0.5

**Data:** 2026-03-30
**Status:** FINAL — Validado por @architect, @data-engineer, @ux-design-expert, @qa
**Versao:** 2.0
**Consolidado por:** @architect (Aria) — Brownfield Discovery Phase 8

**Fontes:**
- `docs/architecture/system-architecture.md` (Phase 1 — @architect)
- `supabase/docs/SCHEMA.md` (Phase 2 — @data-engineer)
- `supabase/docs/DB-AUDIT.md` (Phase 2 — @data-engineer)
- `docs/frontend/frontend-spec.md` (Phase 3 — @ux-design-expert)
- `docs/reviews/db-specialist-review.md` (Phase 5 — @data-engineer)
- `docs/reviews/ux-specialist-review.md` (Phase 6 — @ux-design-expert)
- `docs/reviews/qa-review.md` (Phase 7 — @qa)

---

## Resumo Executivo

| Metrica | Valor |
|---------|-------|
| Total de debitos identificados | 45 |
| Criticos | 2 |
| Altos | 8 |
| Medios | 16 |
| Baixos | 19 |
| Esforco total estimado | ~196h |
| Custo estimado (R$150/h) | R$ 29.400 |
| Debitos resolvidos (excluidos do inventario) | 6 (DB-TD-008, DB-TD-010, DB-TD-011, DEBT-DB-001, DEBT-FE-011, DEBT-FE-014) |

**Distribuicao por area:**
- Backend/Sistema: 15 debitos (~100h)
- Database: 12 debitos (~32h)
- Frontend/UX: 18 debitos (~64h)

**Acuracia do DRAFT original:** 62.5% (5/8 spot-checks confirmados). Os 3 erros foram detectados pelas revisoes de especialistas, validando o processo multi-fase.

---

## Metodologia

Este assessment foi conduzido em 8 fases do workflow brownfield-discovery:

| Fase | Agente | Entregavel |
|------|--------|------------|
| 1 | @architect | Auditoria de arquitetura backend (`system-architecture.md`) |
| 2 | @data-engineer | Auditoria de schema e database (`SCHEMA.md`, `DB-AUDIT.md`) |
| 3 | @ux-design-expert | Auditoria de frontend/UX (`frontend-spec.md`) |
| 4 | @architect | Consolidacao DRAFT com 38 debitos iniciais |
| 5 | @data-engineer | Revisao especializada DB: -1 removido, +5 adicionados, severidades ajustadas |
| 6 | @ux-design-expert | Revisao especializada FE: -2 removidos, +5 adicionados, severidades ajustadas |
| 7 | @qa | Gate de qualidade: 9 correcoes, analise de risco de regressao, testes requeridos |
| 8 | @architect | Consolidacao FINAL (este documento) |

**Criterios de priorizacao:**
- **P0 (Critico):** Risco de producao, estabilidade, ou acessibilidade critica. Resolver em Sprint 1.
- **P1 (Alto):** Modulos monoliticos com alto risco de regressao, resiliencia operacional. Sprints 2-4.
- **P2 (Medio):** Acessibilidade pontual, governance, performance. Sprints 5-6.
- **P3 (Baixo):** Cosmetico, cleanup, otimizacoes nao urgentes. Backlog oportunistico.

---

## Inventario Completo de Debitos

### Sistema (validado por @architect + @qa)

| ID | Debito | Severidade | Horas | Prioridade | Dependencias | Risco Regressao |
|----|--------|------------|-------|------------|--------------|-----------------|
| DEBT-SYS-001 | `filter/core.py` monolitico (4.105 LOC) — funcao `aplicar_todos_filtros()` monolitica, dificulta manutencao e testes isolados | Critica | 16h | P0 | Depende de DEBT-SYS-007 | **CRITICO** — 283 testes em 14 arquivos |
| DEBT-SYS-002 | SIGSEGV intermitente com C extensions (CRIT-SIGSEGV) — restricoes de uvloop, cryptography >= 47.0 pinada por seguranca | Critica | 8h | P0 | Nenhuma | Medio — investigacao periodica |
| DEBT-SYS-003 | `search_cache.py` complexo (2.564 LOC) — logica multi-level (InMemory, Redis, Supabase, Local File) em unico arquivo | Alta | 12h | P1 | Nenhuma | **ALTO** — 186 testes, mock pattern critico |
| DEBT-SYS-004 | `pncp_client.py` sobrecarregado (2.559 LOC) — sync + async client, circuit breaker, retry logic no mesmo modulo | Alta | 10h | P1 | Nenhuma | Medio — 33 testes diretos + 73 indiretos |
| DEBT-SYS-005 | `cron_jobs.py` multiplas responsabilidades (2.251 LOC) — cache cleanup, canary, session cleanup, trial emails | Alta | 8h | P1 | Depende de DEBT-SYS-006 | Medio — 36 testes |
| DEBT-SYS-006 | `job_queue.py` sobrecarregado (2.229 LOC) — config ARQ, pool Redis, definicoes de jobs misturados | Alta | 6h | P1 | Nenhuma | Medio — 48 testes |
| DEBT-SYS-007 | Duplicacao filter_*.py (raiz vs pacote) — legados coexistem com pacote `filter/` | Media | 4h | P2 | Nenhuma (bloqueador de SYS-001) |  Baixo |
| DEBT-SYS-008 | LLM timeout hardcoded em multiplos locais — OpenAI timeout inconsistente entre `llm_arbiter.py` e config | Media | 2h | P2 | Nenhuma | Baixo — 142 testes LLM |
| DEBT-SYS-009 | Feature flag sprawl (30+ flags sem governance) — sem lifecycle ou cleanup | Media | 8h | P2 | Complementa DEBT-FE-008 | Baixo — mas apenas 24 testes para 30+ flags |
| DEBT-SYS-010 | 99 migrations Supabase — volume alto, squash desaconselhado; alternativa: schema snapshot | Media | 4h | P2 | Nenhuma | Baixo |
| DEBT-SYS-011 | Schemas espalhados entre diretorio e raiz — `schemas/` + `schemas_stats.py` + `schema_contract.py` na raiz | Media | 2h | P2 | Nenhuma | Baixo |
| DEBT-SYS-012 | Backward-compat shims em `main.py` — re-exports para testes legados | Baixa | 1h | P3 | Nenhuma | Baixo |
| DEBT-SYS-013 | `portal_transparencia_client.py` sem uso ativo (938 LOC) — dead code | Baixa | 1h | P3 | Nenhuma | Baixo |
| DEBT-SYS-014 | Clients experimentais em clients/ — `querido_diario_client.py`, `qd_extraction.py` sem rota ativa | Baixa | 1h | P3 | Nenhuma | Baixo |
| DEBT-SYS-015 | Dual-hash transition em auth.py — window de 1h para compat de cache keys, pode ser removido | Baixa | 1h | P3 | Nenhuma | Baixo |

**Nota sobre DEBT-SYS-010:** O DRAFT original estimava 16h para squash completo. @data-engineer desaconselhou squash (riscos de data migrations, triggers, seed data) e recomendou schema snapshot via `pg_dump --schema-only` a 4h. Aceito conforme recomendacao do especialista.

**Nota sobre DEBT-SYS-002:** Risco de seguranca — cryptography pinada em <47.0 requer monitoramento de CVEs na faixa 46.x e testes periodicos com 47.x em staging.

---

### Database (validado por @data-engineer + @qa)

| ID | Debito | Severidade | Horas | Prioridade | Dependencias | Risco Regressao |
|----|--------|------------|-------|------------|--------------|-----------------|
| DEBT-DB-009 | Nenhuma migration com rollback formal — 99 migrations, unica opcao e PITR ou restauracao manual | **Alta** | 12h | P1 | Nenhuma | Baixo ao criar; **ALTO** ao executar |
| DEBT-DB-NEW-003 | `upsert_pncp_raw_bids` usa loop row-by-row — 500 round-trips internos ao planner por batch | Media | 4h | P2 | Depende de benchmark | Medio — edge cases com content_hash dedup |
| DEBT-DB-NEW-005 | Sem monitoring de table bloat para `pncp_raw_bids` — 40K+ rows com hard deletes diarios | Media | 2h | P2 | Nenhuma | Baixo |
| DEBT-DB-005 | Hardcoded Stripe price IDs em migrations — seed script existe e funciona, falta doc de onboarding | **Baixa** | 2h | P3 | Nenhuma | Baixo |
| DEBT-DB-002 | `ingestion_runs.metadata` JSONB sem CHECK constraint — unica coluna critica restante sem governance | Baixa | 0.5h | P3 | Nenhuma | Baixo |
| DEBT-DB-003 | Trigger prefix inconsistente (tr_/trg_/trigger_) — 3 prefixos distintos, cosmetico | Baixa | 2h | P3 | Nenhuma | Baixo |
| DEBT-DB-004 | RLS policy naming inconsistente — mix snake_case e descritivo, ~60+ policies | Baixa | 3h | P3 | Nenhuma | Baixo |
| DEBT-DB-006 | Inconsistencia semantica soft/hard delete em pncp_raw_bids — purge faz hard delete apesar de COMMENT | Baixa | 1h | P3 | Nenhuma | Baixo |
| DEBT-DB-007 | health_checks e incidents sem policies admin — admin precisa service_role | Baixa | 1h | P3 | Nenhuma | Baixo |
| DEBT-DB-NEW-001 | COMMENT incorreto em `pncp_raw_bids.is_active` — doc diz soft delete, comportamento e hard delete | Baixa | 0.5h | P3 | Nenhuma | Baixo |
| DEBT-DB-NEW-002 | `ingestion_checkpoints.crawl_batch_id` FK nao enforced — performance justificada mas risco de orfaos | Baixa | 1h | P3 | Nenhuma | Baixo |
| DEBT-DB-NEW-004 | `search_datalake` calcula `to_tsvector` 2x por row — trade-off storage vs CPU, manter ate benchmark | Baixa | 2h | P3 | Depende de DEBT-DB-NEW-005 | Baixo |

**Debito removido:** DEBT-DB-001 (`alerts.filters` JSONB sem CHECK) — ja resolvido na migration `20260321130100_debt_db010_jsonb_size_governance.sql`. Constraint `chk_alerts_filters_size` existe com limite 512KB.

**Severidades ajustadas vs DRAFT:**
- DEBT-DB-009: Media -> **Alta** (risco operacional mais significativo do banco, sem recovery path formal)
- DEBT-DB-005: Media -> **Baixa** (seed script 80% pronto, esforco restante e documentacao)

**Saude do banco de dados (metricas do @data-engineer):**

| Metrica | Valor | Alvo |
|---------|-------|------|
| RLS Coverage | 100% (28/28 tabelas) | 100% |
| FK Standardization | 100% | 100% |
| JSONB Size Governance | ~93% (falta `ingestion_runs.metadata`) | 100% |
| Retention Policies | 100% (12 pg_cron jobs) | 100% |
| Index Coverage | Excelente (80+ indexes) | Sem missing criticals |
| NOT NULL em timestamps | 100% | 100% |

---

### Frontend/UX (validado por @ux-design-expert + @qa)

| ID | Debito | Severidade | Horas | Prioridade | Dependencias | Risco Regressao |
|----|--------|------------|-------|------------|--------------|-----------------|
| DEBT-FE-002 | ViabilityBadge usa `title` para dados criticos — breakdown de viabilidade inacessivel em mobile/touch | Alta | 4h | P0 | Nenhuma | Baixo |
| DEBT-FE-001 | `useSearchOrchestration` mega-hook (618 LOC) — orquestra 12+ sub-hooks, risco de regressao alto | Alta | 12h | P1 | Nenhuma | **ALTO** — hook central da feature principal |
| DEBT-FE-017 | Landing page com 13 child components "use client" — hydration excessiva, LCP degradado, conversao afetada | Alta | 10h | P1 | Nenhuma | Medio — hydration pode quebrar de formas sutis |
| DEBT-FE-004 | 12 banners na busca — cognitive overload sem sistema de prioridade | Media | 8h | P2 | Nenhuma (bloqueador de FE-003) | Baixo |
| DEBT-FE-005 | /admin usa useState + fetch manual — inconsistente com SWR do resto do app | Media | 4h | P2 | Nenhuma | Baixo |
| DEBT-FE-007 | Campos de busca sem `aria-describedby` — hints nao linkados aos inputs | Media | 2h | P2 | Nenhuma | Baixo |
| DEBT-FE-008 | Feature gates hardcoded — apenas `alertas` e gated, sem feature flag service | Media | 6h | P2 | Complementa DEBT-SYS-009 | Baixo |
| DEBT-FE-016 | IDs duplicados de main-content — skip navigation quebrado em /buscar | Media | 1h | P2 | Nenhuma | Baixo |
| DEBT-FE-018 | Indicadores de viabilidade apenas por cor — WCAG 1.4.1, inacessivel para daltonicos | Media | 3h | P2 | Nenhuma | Baixo |
| DEBT-FE-020 | Pipeline kanban sem anuncios de drag para screen readers — DnD indescoberto | Media | 4h | P2 | Nenhuma | Baixo |
| DEBT-FE-003 | Sem `aria-live` em 6 banners restantes — 28+ usos existem, gap estreito | **Baixa** | 2h | P2 | Depende de DEBT-FE-004 | Baixo |
| DEBT-FE-006 | Landmarks HTML inconsistentes — 25+ paginas com `<main>`, gap em `id` padronizado | **Baixa** | 2h | P2 | Nenhuma | Baixo |
| DEBT-FE-013 | Testes a11y automatizados — axe-core em 5 paginas, expandir para 10 | **Baixa** | 3h | P2 | Apos outros a11y debts | Baixo |
| DEBT-FE-009 | SVGs inline vs lucide-react — MobileDrawer com 10+ SVGs inline | Baixa | 3h | P3 | Nenhuma | Baixo |
| DEBT-FE-010 | Raw hex values vs tokens semanticos — inconsistencias em componentes secundarios | Baixa | 4h | P3 | Nenhuma | Baixo |
| DEBT-FE-012 | Focus order em BuscarModals — modais sobrepostos podem confundir focus | Baixa | 2h | P3 | Nenhuma | Baixo |
| DEBT-FE-015 | SEO pages thin content — paginas `/como-*` com risco de penalidade | Baixa | 4h | P3 | Nenhuma | Baixo |
| DEBT-FE-019 | Shepherd.js carregado eagerly — ~15KB JS desnecessario por pagina | Baixa | 2h | P3 | Nenhuma | Baixo |

**Debitos removidos:**
- DEBT-FE-011 (Tipo `any` em API proxy routes) — busca no codigo retornou zero ocorrencias de `: any` em `frontend/app/api/**/*.ts`. Debito especulativo nao confirmado.
- DEBT-FE-014 (Sem prefers-reduced-motion) — implementacao global ja existe em `globals.css` L349-355 + verificacoes em `AnimateOnScroll.tsx` e `useInView.ts`.

**Severidades ajustadas vs DRAFT:**
- DEBT-FE-003: Media -> **Baixa** (28+ usos de aria-live ja existem, gap estreito)
- DEBT-FE-006: Media -> **Baixa** (25+ paginas com `<main>`, gap em padronizacao de IDs)
- DEBT-FE-013: Media -> **Baixa** (axe-core E2E em 5 paginas ja existe)

**Correcao factual:** DEBT-FE-001 descricao corrigida de "200+ linhas" para "618 LOC" conforme verificacao do @ux-design-expert.

---

## Matriz de Priorizacao Final

| Prioridade | ID | Debito | Area | Severidade | Horas | Sprint Sugerido |
|------------|-----|--------|------|------------|-------|-----------------|
| P0 | DEBT-SYS-001 | filter/core.py monolitico (4.105 LOC) | Backend | Critica | 16h | Sprint 2 |
| P0 | DEBT-SYS-002 | SIGSEGV C extensions (CRIT-SIGSEGV) | Infra | Critica | 8h | Backlog (periodico) |
| P0 | DEBT-FE-002 | ViabilityBadge title inacessivel | Frontend | Alta | 4h | Sprint 3 |
| P1 | DEBT-SYS-003 | search_cache.py (2.564 LOC) | Backend | Alta | 12h | Sprint 4 |
| P1 | DEBT-SYS-004 | pncp_client.py (2.559 LOC) | Backend | Alta | 10h | Sprint 5 |
| P1 | DEBT-SYS-005 | cron_jobs.py multiplas responsabilidades | Backend | Alta | 8h | Sprint 5 |
| P1 | DEBT-SYS-006 | job_queue.py sobrecarregado | Backend | Alta | 6h | Sprint 5 |
| P1 | DEBT-FE-001 | useSearchOrchestration mega-hook (618 LOC) | Frontend | Alta | 12h | Sprint 3 |
| P1 | DEBT-FE-017 | Landing page hydration excessiva (13 "use client") | Frontend | Alta | 10h | Sprint 3 |
| P1 | DEBT-DB-009 | Nenhuma migration com rollback formal | Database | Alta | 12h | Sprint 4 |
| P2 | DEBT-SYS-007 | Duplicacao filter_*.py (raiz vs pacote) | Backend | Media | 4h | Sprint 2 |
| P2 | DEBT-SYS-008 | LLM timeout hardcoded | Backend | Media | 2h | Sprint 1 |
| P2 | DEBT-SYS-009 | Feature flag sprawl (30+ flags) | Backend | Media | 8h | Sprint 6 |
| P2 | DEBT-SYS-010 | 99 migrations — schema snapshot | Infra | Media | 4h | Backlog |
| P2 | DEBT-SYS-011 | Schemas espalhados | Backend | Media | 2h | Backlog |
| P2 | DEBT-FE-004 | 12 banners na busca — cognitive overload | Frontend | Media | 8h | Sprint 5 |
| P2 | DEBT-FE-005 | /admin sem SWR | Frontend | Media | 4h | Backlog |
| P2 | DEBT-FE-007 | Campos sem aria-describedby | Frontend | Media | 2h | Sprint 1 |
| P2 | DEBT-FE-008 | Feature gates hardcoded | Frontend | Media | 6h | Sprint 6 |
| P2 | DEBT-FE-016 | IDs duplicados main-content | Frontend | Media | 1h | Sprint 1 |
| P2 | DEBT-FE-018 | Indicadores apenas por cor (WCAG 1.4.1) | Frontend | Media | 3h | Sprint 6 |
| P2 | DEBT-FE-020 | Pipeline kanban sem drag announcements | Frontend | Media | 4h | Sprint 6 |
| P2 | DEBT-FE-003 | aria-live em 6 banners faltantes | Frontend | Baixa | 2h | Sprint 1 |
| P2 | DEBT-FE-006 | Landmarks HTML — IDs nao padronizados | Frontend | Baixa | 2h | Sprint 1 |
| P2 | DEBT-FE-013 | Expandir testes a11y (5 -> 10 paginas) | Frontend | Baixa | 3h | Sprint 6 |
| P2 | DEBT-DB-NEW-003 | upsert_pncp_raw_bids loop row-by-row | Database | Media | 4h | Backlog |
| P2 | DEBT-DB-NEW-005 | Sem monitoring bloat pncp_raw_bids | Database | Media | 2h | Sprint 4 |
| P3 | DEBT-SYS-012 | Backward-compat shims main.py | Backend | Baixa | 1h | Sprint 1 |
| P3 | DEBT-SYS-013 | portal_transparencia_client sem uso (dead code) | Backend | Baixa | 1h | Sprint 2 |
| P3 | DEBT-SYS-014 | Clients experimentais (dead code) | Backend | Baixa | 1h | Sprint 2 |
| P3 | DEBT-SYS-015 | Dual-hash transition auth.py | Backend | Baixa | 1h | Sprint 1 |
| P3 | DEBT-DB-002 | ingestion_runs.metadata sem CHECK | Database | Baixa | 0.5h | Sprint 1 |
| P3 | DEBT-DB-003 | Trigger prefix inconsistente | Database | Baixa | 2h | Backlog |
| P3 | DEBT-DB-004 | RLS policy naming inconsistente | Database | Baixa | 3h | Backlog |
| P3 | DEBT-DB-005 | Stripe price IDs — doc de onboarding | Database | Baixa | 2h | Backlog |
| P3 | DEBT-DB-006 | Soft/hard delete semantica | Database | Baixa | 1h | Backlog |
| P3 | DEBT-DB-007 | health_checks sem policy admin | Database | Baixa | 1h | Sprint 1 |
| P3 | DEBT-DB-NEW-001 | COMMENT incorreto pncp_raw_bids.is_active | Database | Baixa | 0.5h | Sprint 1 |
| P3 | DEBT-DB-NEW-002 | FK checkpoint nao enforced | Database | Baixa | 1h | Backlog |
| P3 | DEBT-DB-NEW-004 | search_datalake tsvector 2x | Database | Baixa | 2h | Backlog |
| P3 | DEBT-FE-009 | SVGs inline vs lucide-react | Frontend | Baixa | 3h | Backlog |
| P3 | DEBT-FE-010 | Raw hex vs tokens semanticos | Frontend | Baixa | 4h | Backlog |
| P3 | DEBT-FE-012 | Focus order em modais | Frontend | Baixa | 2h | Backlog |
| P3 | DEBT-FE-015 | SEO pages thin content | Frontend | Baixa | 4h | Backlog |
| P3 | DEBT-FE-019 | Shepherd.js eager loading | Frontend | Baixa | 2h | Sprint 1 |

---

## Plano de Resolucao

### Sprint 1: Quick Wins (Semana 1-2) — ~14h

Todos paralelizaveis. Baixo risco de regressao. Resultados imediatos.

| ID | Debito | Horas | Responsavel |
|----|--------|-------|-------------|
| DEBT-DB-002 | metadata CHECK constraint | 0.5h | @data-engineer |
| DEBT-DB-NEW-001 | fix COMMENT pncp_raw_bids.is_active | 0.5h | @data-engineer |
| DEBT-DB-007 | admin RLS policies | 1h | @data-engineer |
| DEBT-FE-016 | Unificar IDs main-content | 1h | @dev |
| DEBT-FE-007 | aria-describedby em campos de busca | 2h | @dev |
| DEBT-FE-003 | aria-live nos 6 banners faltantes | 2h | @dev |
| DEBT-FE-006 | Padronizar landmark IDs | 2h | @dev |
| DEBT-FE-019 | Lazy-load Shepherd.js | 2h | @dev |
| DEBT-SYS-008 | Centralizar LLM timeout | 2h | @dev |
| DEBT-SYS-012 | Remover backward-compat shims | 1h | @dev |
| DEBT-SYS-015 | Remover dual-hash transition | 1h | @dev |

### Sprint 2: Decomposicao Backend Wave 1 (Semana 3-4) — ~22h

Cadeia sequencial: resolver duplicacao primeiro, depois decompor monolito.

| ID | Debito | Horas | Dependencia | Responsavel |
|----|--------|-------|-------------|-------------|
| DEBT-SYS-007 | Resolver duplicacao filter_*.py | 4h | Nenhuma | @dev |
| DEBT-SYS-001 | Decompor filter/core.py (4.105 LOC) | 16h | DEBT-SYS-007 | @dev + @qa |
| DEBT-SYS-013 + SYS-014 | Remover dead code (portal_transparencia, querido_diario) | 2h | Nenhuma (paralelo) | @dev |

**Requisito QA:** 283 testes filter_*.py devem passar sem mudanca de import. Facade pattern obrigatorio via `filter/__init__.py` com backward-compat re-exports.

### Sprint 3: Frontend Structural (Semana 5-6) — ~26h

| ID | Debito | Horas | Dependencia | Responsavel |
|----|--------|-------|-------------|-------------|
| DEBT-FE-017 | Landing page RSC islands — converter 10/13 components para Server Components | 10h | Nenhuma | @dev + @ux-design-expert |
| DEBT-FE-001 | Decompor useSearchOrchestration (618 LOC) — extrair 4 sub-hooks | 12h | Nenhuma | @dev + @qa |
| DEBT-FE-002 | ViabilityBadge tooltip acessivel — Radix Tooltip + tap-to-expand mobile | 4h | Nenhuma | @dev + @ux-design-expert |

**Requisito QA:** Snapshot tests de `searchResultsProps` antes/depois. E2E `search-flow.spec.ts` 100%. Lighthouse CI para landing (LCP < 2.5s).

### Sprint 4: Resiliencia (Semana 7-8) — ~26h

| ID | Debito | Horas | Dependencia | Responsavel |
|----|--------|-------|-------------|-------------|
| DEBT-DB-009 | Rollback scripts para 5 tabelas criticas | 12h | Nenhuma | @data-engineer + @qa |
| DEBT-SYS-003 | Decompor search_cache.py (2.564 LOC) | 12h | Nenhuma (paralelo) | @dev + @qa |
| DEBT-DB-NEW-005 | Bloat monitoring para pncp_raw_bids | 2h | Nenhuma (paralelo) | @data-engineer |

**Requisito QA:** 186 testes cache passam + helper de mock centralizado criado. Rollback testado em staging com dados sinteticos.

### Sprint 5: Backend Wave 2 + Frontend Wave 2 (Semana 9-10) — ~30h

| ID | Debito | Horas | Dependencia | Responsavel |
|----|--------|-------|-------------|-------------|
| DEBT-SYS-004 | Decompor pncp_client.py (2.559 LOC) | 10h | Nenhuma | @dev |
| DEBT-SYS-005 + SYS-006 | Decompor cron_jobs + job_queue (juntos) | 14h | Nenhuma (paralelo) | @dev + @qa |
| DEBT-FE-004 | BannerStack com sistema de prioridade (maximo 2 simultaneos) | 8h | Nenhuma (paralelo) | @dev + @ux-design-expert |

**Requisito QA:** Worker lifecycle E2E (startup -> jobs -> graceful shutdown). Circuit breaker extraido com canary test. Banner stack nunca exibe >2 banners.

### Sprint 6: Acessibilidade + Governance (Semana 11-12) — ~28h

| ID | Debito | Horas | Dependencia | Responsavel |
|----|--------|-------|-------------|-------------|
| DEBT-SYS-009 + DEBT-FE-008 | Feature flag governance unificada (backend + frontend) | 14h | Nenhuma | @architect + @dev |
| DEBT-FE-018 | Auditoria cor-only nos badges (WCAG 1.4.1) | 3h | Nenhuma (paralelo) | @dev |
| DEBT-FE-020 | Pipeline drag announcements para screen readers | 4h | Nenhuma (paralelo) | @dev |
| DEBT-FE-013 | Expandir testes a11y de 5 para 10 paginas | 3h | Apos FE-018 e FE-020 | @qa |
| DEBT-SYS-002 | Investigacao periodica SIGSEGV — testar cryptography 47.x em staging | 4h | Nenhuma | @devops |

### Backlog: Low Priority (~50h)

Resolver oportunisticamente durante feature work. Nao justificam sprint dedicado.

| ID | Debito | Horas | Trigger para Resolver |
|----|--------|-------|-----------------------|
| DEBT-DB-003 | Trigger prefix padronizacao | 2h | Quando tocar nas tabelas afetadas |
| DEBT-DB-004 | RLS policy naming | 3h | Durante auditoria de seguranca |
| DEBT-DB-005 | Stripe seed doc onboarding | 2h | Quando onboarding novo dev |
| DEBT-DB-006 | Soft/hard delete documentacao | 1h | Junto com DEBT-DB-NEW-001 |
| DEBT-DB-NEW-002 | FK checkpoint monitoring | 1h | Quando ingestion escalar |
| DEBT-DB-NEW-003 | Otimizar upsert para batch | 4h | Quando ingestao > 1000 rows/batch |
| DEBT-DB-NEW-004 | tsvector 2x optimization | 2h | Quando pncp_raw_bids > 100K rows |
| DEBT-SYS-010 | Schema snapshot (alternativa a squash) | 4h | Quando migrations > 150 |
| DEBT-SYS-011 | Schemas espalhados consolidar | 2h | Durante refactor de schemas |
| DEBT-FE-005 | /admin migrar para SWR | 4h | Durante feature work em admin |
| DEBT-FE-009 | SVGs inline migrar para lucide-react | 3h | Durante refactor de MobileDrawer |
| DEBT-FE-010 | Raw hex substituir por tokens | 4h | Durante refactor visual |
| DEBT-FE-012 | Focus order em modais | 2h | Durante work em BuscarModals |
| DEBT-FE-015 | SEO pages thin content | 4h | Antes de campanha SEO |
| DEBT-SYS-002 | SIGSEGV restante (4h adicionais) | 4h | Quando cryptography 47.x estavel |

---

## Dependencias e Cadeia de Resolucao

### Cadeia 1: Decomposicao de Modulos Backend

```
DEBT-SYS-007 (resolver duplicacao filter_*.py, 4h)
    |
    v
DEBT-SYS-001 (decompor filter/core.py, 16h) — BLOQUEADO por SYS-007
    |
    (paralelo)
    |
DEBT-SYS-004 (decompor pncp_client.py, 10h) — independente
    |
DEBT-SYS-005 ←→ DEBT-SYS-006 (decompor juntos — compartilham ARQ + Redis pool, 14h)
    |
DEBT-SYS-003 (decompor search_cache.py, 12h) — independente
```

**Padrao obrigatorio:** Toda decomposicao deve usar facade pattern com re-exports em `__init__.py` para backward-compat. Mock pattern `supabase_client.get_supabase` preservado.

### Cadeia 2: Acessibilidade Frontend

```
DEBT-FE-002 (ViabilityBadge tooltip, 4h) — independente, P0
    |
DEBT-FE-004 (consolidar banners, 8h) — independente
    |
    v
DEBT-FE-003 (aria-live nos banners consolidados, 2h) — BLOQUEADO por FE-004
    |
DEBT-FE-016 (IDs main-content, 1h) — independente
DEBT-FE-007 (aria-describedby, 2h) — independente
DEBT-FE-018 (cor-only audit, 3h) — independente
DEBT-FE-020 (pipeline drag, 4h) — independente
    |
    v
DEBT-FE-013 (testes a11y automatizados, 3h) — APOS todos os outros a11y debts
```

### Cadeia 3: Database Governance

```
DEBT-DB-002 (metadata CHECK, 0.5h) — independente, quick win
DEBT-DB-NEW-001 (fix COMMENT, 0.5h) — independente, quick win
DEBT-DB-007 (admin RLS, 1h) — independente, quick win
    |
    (podem ser 1 migration)
    |
DEBT-DB-009 (rollback scripts, 12h) — independente
    |
    (comecar por profiles e user_subscriptions)
    |
DEBT-DB-NEW-005 (bloat monitoring, 2h) — independente
    |
    v
DEBT-DB-NEW-003 (otimizar upsert, 4h) — depende de benchmark
DEBT-DB-NEW-004 (tsvector, 2h) — depende de DEBT-DB-NEW-005 para medir impacto
```

### Cadeia 4: Feature Flag Governance (cross-cutting)

```
DEBT-SYS-009 (backend flag sprawl, 8h) ←→ DEBT-FE-008 (frontend gates, 6h)
    |
    Resolver juntos para criar sistema unificado com API endpoint /feature-flags
    |
    Total combinado: 14h
```

---

## Riscos e Mitigacoes

| Risco | Probabilidade | Impacto | Mitigacao |
|-------|---------------|---------|-----------|
| Regressao em filter/core.py (283 testes dependentes) | Media | Alto | Facade pattern + backward-compat imports. Suite completa antes/depois. |
| Regressao em search_cache.py (186 testes com mock pattern) | Media | Alto | Criar helper de mock centralizado antes de decompor. Canary deploy + monitoring cache hit rate. |
| Regressao em useSearchOrchestration (618 LOC, 12+ sub-hooks) | Media | Alto | Snapshot tests de props. E2E search-flow.spec.ts como safety net. |
| Landing RSC hydration quebrada | Baixa | Medio | Branch separada. Lighthouse CI + visual regression. Consultar docs Next.js 16. |
| Rollback scripts mal escritos corrompem dados | Baixa | Critico | Testar em staging com dados sinteticos. Validar integridade pos-rollback. Nunca executar em producao sem PITR. |
| PNCP API instavel durante testes de decomposicao | Media | Baixo | Mocks para unitarios. Canary test em horario de baixo trafego. |
| Railway deploy timeout durante rollback testing | Baixa | Baixo | Testar localmente com Supabase CLI + `supabase db reset`. |
| Supabase PITR indisponivel no plano atual | Baixa | Alto | Verificar plano. Se sem PITR, rollback scripts sao ainda mais criticos. |
| Breaking changes no Next.js 16 RSC behavior | Baixa | Medio | Consultar docs antes de converter. Branch separada. |
| ARQ mock isolation em testes | Media | Medio | Usar conftest `_isolate_arq_module`. Nunca `sys.modules["arq"] = MagicMock()` sem cleanup. |
| Combinacoes de feature flags nao testadas | Alta | Medio | Criar `test_feature_flag_matrix.py` com 10 flags criticas em on/off (4h estimada). |
| Cryptography CVE na faixa 46.x | Baixa | Alto | Monitorar CVEs. Testar periodicamente com 47.x em staging. |

---

## Testes Requeridos

| Debito | Testes Necessarios | Tipo | Criterio de Aceite |
|--------|-------------------|------|-------------------|
| DEBT-SYS-001 | 283 testes filter_*.py passam sem mudanca de import | Regressao | 0 falhas, 0 warnings deprecation |
| DEBT-SYS-003 | 186 testes cache passam + novo teste integracao multi-level | Regressao + Integracao | SWR revalidation <= 200ms overhead |
| DEBT-SYS-004 | 33 testes unitarios + canary PNCP real | Regressao + Canary | Circuit breaker abre/fecha corretamente |
| DEBT-SYS-005+006 | Worker lifecycle: startup -> jobs -> graceful shutdown | Integracao | Zero jobs perdidos em shutdown |
| DEBT-SYS-009+FE-008 | Cada flag em on/off + 5 combinacoes criticas | Unitario + Integracao | Nenhuma flag sem teste |
| DEBT-FE-001 | Snapshot de searchResultsProps antes/depois | Snapshot + E2E | Props identicos. search-flow.spec.ts 100% |
| DEBT-FE-002 | axe-core em ViabilityBadge + touch device emulation | A11y + E2E | Breakdown acessivel sem hover. WCAG 2.1 AA |
| DEBT-FE-004 | Prioridade de banners: 3+ ativos -> exibe top 2 | Unitario | BannerStack nunca exibe >2 simultaneos |
| DEBT-FE-017 | Lighthouse CI em landing | Performance | LCP < 2.5s, TTI < 3.5s mobile 4G |
| DEBT-FE-020 | axe-core aria assertions para drag | A11y | Announcements presentes em onDragStart/End |
| DEBT-DB-009 | Rollback em staging com dados sinteticos | Integracao | Schema reverte. Dados preservados. FKs validos |
| DEBT-DB-NEW-003 | Benchmark ingestao 500 rows antes/depois | Performance | Sem duplicatas. Tempo >= 30% menor |

---

## Metricas de Sucesso

| Metrica | Baseline Atual | Alvo Pos-Resolution | Como Medir |
|---------|---------------|---------------------|------------|
| Testes backend passando | 5131+ / 0 falhas | 5300+ / 0 falhas | `pytest --timeout=30 -q` |
| Testes frontend passando | 2681+ / 0 falhas | 2750+ / 0 falhas | `npm test` |
| Maior arquivo backend (LOC) | filter/core.py 4105 | < 1500 LOC | `wc -l` top 5 |
| Modulos > 2000 LOC | 5 | <= 2 | Script de auditoria |
| Feature flags com teste on/off | ~24/30+ (~80%) | 100% | Grep por flags sem teste |
| WCAG 2.1 AA paginas auditadas | 5/22 | 15/22 | Expandir accessibility-audit.spec.ts |
| Landing LCP (mobile 4G) | ~3.5s (estimado) | < 2.5s | Lighthouse CI |
| Landing TTI (mobile 4G) | ~4.5s (estimado) | < 2.5s | Lighthouse CI |
| Tabelas criticas com rollback | 0/5 | 5/5 | Inventario em supabase/rollbacks/ |
| Cobertura pytest | ~70% | >= 75% | `pytest --cov` |
| Cognitive load score (busca) | 7/10 (alto) | 4/10 (medio) | Audit UX pos BannerStack |
| WCAG 2.1 AA compliance | ~85% | ~95% | axe-core audit |
| JSONB Size Governance | ~93% | 100% | Audit de constraints |

---

## Pontos Fortes do Sistema

O assessment identificou debitos, mas e importante registrar o que esta funcionando bem:

### Backend
- **Cobertura de testes excelente:** 5131+ testes, 0 falhas. Modulos criticos (filter, cache, LLM) com centenas de testes.
- **Resiliencia multi-camada:** Circuit breakers, retry com backoff, timeout chain documentada, fallback gracioso.
- **Pipeline de ingestao robusto:** Checkpoint tracking, dedup por content_hash, retention automatica.
- **Observabilidade:** Prometheus counters, OpenTelemetry traces, Sentry, health checks.

### Database
- **RLS coverage 100%** em 28/28 tabelas.
- **FK standardization 100%** — todas apontando para profiles(id).
- **JSONB governance 93%** — 12 colunas com CHECK constraints de tamanho.
- **Retention policies ativas** com 12 pg_cron jobs.
- **80+ indexes** sem missing criticals.

### Frontend
- **Acessibilidade progressiva:** 28+ usos de aria-live/role="alert", prefers-reduced-motion global, axe-core em 5 paginas.
- **Resilience UX:** Loading states robustos, error handling multi-nivel, degradation banners.
- **Onboarding completo:** Tour Shepherd.js, onboarding 3 passos, first-use tips.
- **Responsividade mobile:** MobileDrawer, BottomNav, layout adaptativo.

### Processo
- **Workflow multi-fase validado:** 3 erros factuais no DRAFT detectados por especialistas antes da consolidacao final.
- **Zero-failure policy:** 0 falhas e baseline obrigatoria, nunca "pre-existing".

---

## Areas de Observacao Futura

Identificadas pelo @qa como gaps nao criticos o suficiente para debitos formais:

| Area | Observacao | Severidade do Gap |
|------|-----------|-------------------|
| **Observabilidade/Monitoring** | 30+ Prometheus counters, OpenTelemetry traces — nenhum debito avalia calibracao ou alertas configurados | Media |
| **Worker Health Check** | Separacao web/worker via PROCESS_TYPE. Se worker crashar, recovery depende apenas do Railway restart. Sem health endpoint dedicado para worker | Media |
| **Rate Limiting** | Redis token bucket mencionado na arquitetura mas sem avaliacao de calibracao dos limites | Baixa |
| **Email Service** | `email_service.py` + templates sem testes de renderizacao cross-client | Baixa |
| **Dependency Pinning** | `requirements.txt` com mix de pins exatos e ranges `>=X`. Vulnerabilidades podem entrar via ranges abertas | Baixa |

---

## Debitos Cross-Cutting

| Debito Cross-Cutting | Areas Afetadas | Debitos Relacionados | Recomendacao |
|----------------------|----------------|---------------------|--------------|
| Feature Flag Governance | Backend (30+ flags) + Frontend (gates hardcoded) | DEBT-SYS-009 + DEBT-FE-008 | Resolver juntos com API endpoint `/feature-flags`. Divergencia entre backend e frontend cria flags "fantasma". |
| Timeout Chain Consistency | Backend (5 niveis), Railway (120s), Gunicorn (180s) | DEBT-SYS-008 | Cadeia documentada mas sem teste E2E da cadeia inteira. |
| Modulo Monolitico Pattern | 5 modulos backend com 2000+ LOC | DEBT-SYS-001, 003, 004, 005, 006 | Decomposicao deve seguir padrao consistente (facade + re-exports). |
| Dead Code | portal_transparencia 938 LOC + querido_diario + qd_extraction | DEBT-SYS-013 + DEBT-SYS-014 | Quick win: 2h para remover. Reduz superficie de ataque. |

---

## Anexos

| Documento | Localizacao | Fase |
|-----------|-------------|------|
| Auditoria de Arquitetura | `docs/architecture/system-architecture.md` | Phase 1 |
| Schema Database | `supabase/docs/SCHEMA.md` | Phase 2 |
| Auditoria Database | `supabase/docs/DB-AUDIT.md` | Phase 2 |
| Frontend Spec | `docs/frontend/frontend-spec.md` | Phase 3 |
| Technical Debt DRAFT | `docs/prd/technical-debt-DRAFT.md` | Phase 4 |
| DB Specialist Review | `docs/reviews/db-specialist-review.md` | Phase 5 |
| UX Specialist Review | `docs/reviews/ux-specialist-review.md` | Phase 6 |
| QA Review | `docs/reviews/qa-review.md` | Phase 7 |

---

## Changelog

| Versao | Data | Mudancas |
|--------|------|---------|
| DRAFT | 2026-03-30 | 38 debitos iniciais consolidados de 3 fontes |
| 1.0 | 2026-03-30 | Incorporacao de revisoes DB + UX + QA. 45 debitos finais. |
| 2.0 | 2026-03-30 | Consolidacao FINAL Phase 8: todas as 9 correcoes QA aplicadas, priorizacao recalculada, plano de resolucao com 6 sprints, metricas de sucesso definidas. |

---

*Documento FINAL consolidado por @architect (Aria). Validado por @data-engineer (Dara), @ux-design-expert (Uma), @qa (Quinn). Pronto para execucao.*
