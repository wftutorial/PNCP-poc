# Technical Debt Assessment - DRAFT

**Data:** 2026-04-08
**Status:** DRAFT -- Pendente revisao dos especialistas (Fases 5, 6, 7)
**Autores:** @architect (Aria) -- consolidacao de Phases 1-3
**Fontes:**
- `docs/architecture/system-architecture.md` (Phase 1 - System Architecture)
- `supabase/docs/SCHEMA.md` (Phase 2 - Database Schema)
- `supabase/docs/DB-AUDIT.md` (Phase 2 - Database Audit)
- `docs/frontend/frontend-spec.md` (Phase 3 - Frontend/UX Spec)

---

## Para Revisao dos Especialistas

Este documento consolida TODOS os debitos tecnicos identificados nas Fases 1-3 do Brownfield Discovery.
Cada item esta numerado TD-001 a TD-042 e classificado por severidade, impacto e esforco estimado.

---

### 1. Debitos de Sistema/Backend

*Fonte: `docs/architecture/system-architecture.md` -- Known Issues & Debt, performance gaps, architecture decisions*

#### Critical (Resolved -- manter monitoramento)

| ID | Debito | Status | Notas |
|----|--------|--------|-------|
| TD-001 | CRIT-SIGSEGV-v2: Uvicorn single-worker mode (no forking) | Resolved | Limita throughput; scaling via horizontal scaling (multiplos Railway services). Monitorar se bottleneck em pico. |
| TD-002 | CRIT-041: Fork-unsafe C extensions removidas (grpcio, httptools, uvloop) | Resolved | Nao usar uvloop/httptools em producao. Testar ao atualizar dependencias. |
| TD-003 | CRIT-033: ARQ worker health detection + inline fallback | Resolved | Worker deve ser monitorado; inline fallback em caso de worker down. |
| TD-004 | CRIT-072: Async search deadline + time budget checks | Resolved | Implementado; monitorar metricas de timeout. |

#### High

| ID | Debito | Descricao |
|----|--------|-----------|
| TD-005 | SYS-023: Per-user Supabase tokens | Operacoes scoped ao usuario usam service_role em vez de token do usuario. Risco de escalacao de privilegio se RPC nao validar auth.uid(). Mitigado por RLS mas nao ideal. |
| TD-006 | DEBT-325: Exchange rate USD/BRL hardcoded | Taxa de cambio estatica em vez de API dinamica. Afeta calculo de valores exibidos ao usuario. |
| TD-007 | Execute.py oversized (58KB) | Modulo de execucao multi-source com alta complexidade ciclomatica. Dificulta manutencao e testes. Candidato a refactoring em submudulos. |
| TD-008 | Generate.py oversized (27KB) | Modulo de geracao de output (Excel/PDF/API response) concentrado em um unico arquivo. |
| TD-009 | Filter_stage.py oversized (20KB) | Pipeline de filtragem com logica densa. |
| TD-010 | Quota.py oversized (65KB+) | Modulo de quotas com alta complexidade. |
| TD-011 | Single-worker horizontal scaling dependency | Railway horizontal scaling necessario para throughput. Sem auto-scaling configurado -- depende de monitoramento manual. |

#### Medium

| ID | Debito | Descricao |
|----|--------|-----------|
| TD-012 | DEBT-018: Cryptography fork-safe testing | Testes de fork-safety para a lib cryptography nao estao automatizados. Risco ao atualizar versao. |
| TD-013 | PNCP API availability 94% (target 95%) | PNCP API below target availability. Health canary usa tamanhoPagina=10 -- nao detecta limites de page size. |
| TD-014 | Cache hit rate 65-75% (target >70%) | Marginal; p75 atinge target mas p25 nao. Warming strategy pode melhorar. |
| TD-015 | Railway hard timeout 120s vs Gunicorn 180s mismatch | Railway mata requests antes do Gunicorn timeout. Potencial para erros silenciosos em requests longos. |
| TD-016 | 121 migration files sem squash | Fresh environments levam 2-3 min para aplicar. Nenhum squash realizado desde o inicio. |

#### Low

| ID | Debito | Descricao |
|----|--------|-----------|
| TD-017 | OpenTelemetry HTTP-only (no gRPC) | Limitacao por fork-safety. Funcional mas gRPC e mais eficiente. |
| TD-018 | Dual migration naming convention | Migrations antigas (001_) e novas (20260326000000_). Inconsistente mas nao bloqueante. |

---

### 2. Debitos de Database

*Fonte: `supabase/docs/DB-AUDIT.md` -- 12 otimizacoes identificadas*
**PENDENTE: Revisao do @data-engineer**

#### High Priority

| ID | Debito | Descricao | Impacto |
|----|--------|-----------|---------|
| TD-019 | Missing composite index pncp_raw_bids (uf, modalidade_id, data_publicacao) | Dashboard queries fazem sequential scan em modalidade_id range. | **50-70% mais rapido** em queries tipicas (5-10 UFs x 3-5 modalidades). ~10MB custo por 500K rows. |
| TD-020 | pncp_raw_bids soft-delete bloat | Rows com is_active=false permanecem na tabela. VACUUM nao reclama espaco. ~1.2M dead rows a qualquer momento. | Bloat de tabela + indices. Degradacao progressiva de performance. |
| TD-021 | profiles.plan_type CHECK vs FK | plan_type definido em 2 lugares (plans table + CHECK constraint). Sem integridade referencial. Adicionar novo plano requer migrar CHECK + tabela. | Risco de inconsistencia de dados. |
| TD-022 | pncp_raw_bids.content_hash usa MD5 | MD5 tem ataques de colisao conhecidos. Campos hasheados nao documentados. | Risco de colisao (baixo em pratica), falta de documentacao. |

#### Medium Priority

| ID | Debito | Descricao | Impacto |
|----|--------|-----------|---------|
| TD-023 | Missing covering index user_subscriptions (user_id, created_at DESC) WHERE is_active | Plan lookup queries nao tem index-only scan. | Elimina table lookups para query frequente. |
| TD-024 | Missing index audit_events (target_id_hash) | Admin dashboards investigando impacto em usuarios fazem seq scan. | Melhora investigacao admin. |
| TD-025 | stripe_webhook_events sem retention policy | Sem limpeza automatica. Crescimento ilimitado (~100K+ rows). | Storage crescente sem necessidade. |
| TD-026 | alert_sent_items sem retention policy | Sem cleanup automatico. | Storage crescente. |
| TD-027 | trial_email_log sem retention policy | Sem cleanup automatico. | Storage crescente. |
| TD-028 | audit_events hash sem versioning | Sem campo para track de mudanca de algoritmo de hash. | Dificuldade de migrar algoritmo no futuro. |
| TD-029 | Alert cron job sequencial (1000 alerts = 60-100s) | Execucao sequencial de RPCs para cada alert. | Latencia de alertas em escala. Solucao: asyncio.gather (10 concurrent). |
| TD-030 | RLS policy docs incompletas | shared_analyses increment_share_view() sem GRANT explicito documentado. pncp_raw_bids sem comment sobre base legal. | Auditoria de seguranca dificultada. |

#### Low Priority

| ID | Debito | Descricao | Impacto |
|----|--------|-----------|---------|
| TD-031 | Organizations cascade RESTRICT orphan risk | Se owner auth.users deletado por admin Supabase, org fica orfao. | Edge case raro. Monitoramento query recomendado. |
| TD-032 | conversations/messages sem soft-delete | Sem audit trail se conversa deletada. | Compliance LGPD futuro. |
| TD-033 | Supabase FREE tier 500MB vs estimated ~3GB datalake | pncp_raw_bids + indices estimados em ~3GB. | Migracao para paid tier necessaria antes de escalar. |
| TD-034 | Backup: daily only, 1-day retention, no PITR | Sem Point-in-Time Recovery. Sem backup externo S3. RTO=1h, RPO=24h nao validados. | Risco de perda de dados em falha catastrofica. |

---

### 3. Debitos de Frontend/UX

*Fonte: `docs/frontend/frontend-spec.md` -- DEBT-FE items, gaps de a11y, features faltantes*
**PENDENTE: Revisao do @ux-expert**

#### High

| ID | Debito | Descricao |
|----|--------|-----------|
| TD-035 | DEBT-FE-001: Search filters hook 600+ lines | useSearchFilters() com 600+ linhas. Complexidade excessiva, dificulta manutencao e testes. |

#### Medium

| ID | Debito | Descricao |
|----|--------|-----------|
| TD-036 | Visual regression testing ausente | Sem Percy/Chromatic. Regressoes visuais detectadas manualmente. |
| TD-037 | Saved filter presets ausente | Feature solicitada: usuarios nao conseguem salvar combinacoes de filtro frequentes. |
| TD-038 | Modal focus trap edge cases | FocusTrap em modais tem edge cases nao cobertos. a11y gap. |
| TD-039 | Small touch targets (<44px) em componentes legacy | Componentes antigos nao atendem WCAG 2.5.5 (min 44x44px). Novos componentes ja atendem. |
| TD-040 | /planos e /pricing duplicados (SEO variant) | Duas rotas servindo conteudo similar. Potencial canibalizacao SEO. |

#### Low

| ID | Debito | Descricao |
|----|--------|-----------|
| TD-041 | DEBT-012: Raw hex colors em vez de design tokens | Alguns componentes usam cores hardcoded em vez de variaveis CSS. |
| TD-042 | DEBT-116: style-src unsafe-inline para Tailwind | CSP relaxado para Tailwind funcionar. Risco aceito. |
| TD-043 | Component Storybook ausente | Sem Storybook para documentacao visual de componentes. |
| TD-044 | Icons missing aria-hidden em alguns casos | Icones decorativos sem aria-hidden. |
| TD-045 | Live region config em Sonner toasts | Configuracao de aria-live em toasts pode nao estar correta em todos os cenarios. |
| TD-046 | Scroll jank durante SSE updates (mobile) | Debounce mitiga mas nao resolve completamente. |
| TD-047 | Bottom nav covers content | Padding adjustment necessario em algumas paginas. |
| TD-048 | Multi-language (i18n) ausente | App 100% portugues. Sem suporte a outros idiomas. |
| TD-049 | Offline support (Service Worker) ausente | Sem modo offline. |

---

### 4. Debitos Cross-Cutting

*Debitos que atravessam multiplas areas*

#### Security

| ID | Debito | Area | Descricao |
|----|--------|------|-----------|
| TD-005 | Per-user Supabase tokens | Backend/DB | Service role usado para operacoes user-scoped. RLS mitiga mas nao e ideal. |
| TD-030 | RLS policy docs incompletas | DB/Security | Falta documentacao explicita de GRANTs e base legal. |
| TD-042 | CSP unsafe-inline | Frontend/Security | Necessario para Tailwind. Risco aceito. |
| TD-022 | MD5 content hash | DB/Security | Algoritmo com colisoes conhecidas. |

#### Monitoring/Observability

| ID | Debito | Area | Descricao |
|----|--------|------|-----------|
| TD-013 | PNCP health canary limitado | Backend | Canary usa tamanhoPagina=10 -- nao detecta mudancas em limites de pagina. |
| TD-017 | OpenTelemetry HTTP-only | Backend | Sem gRPC exporter (fork-safety limitation). |
| TD-034 | Backup sem PITR e sem teste de restore | DB/Infra | Sem validacao de restore. RPO/RTO nao testados. |

#### CI/CD

| ID | Debito | Area | Descricao |
|----|--------|------|-----------|
| TD-016 | 121 migrations sem squash | DB/CI | Fresh environments lentos (2-3 min). |
| TD-018 | Dual migration naming | DB/CI | Inconsistencia em naming. |
| TD-036 | Visual regression testing ausente | Frontend/CI | Sem gate de regressao visual no CI. |

#### Documentation

| ID | Debito | Area | Descricao |
|----|--------|------|-----------|
| TD-030 | RLS docs incompletas | DB | Falta comments SQL em politicas RLS. |
| TD-022 | Content hash nao documentado | DB | Campos incluidos no hash MD5 nao documentados. |

---

### 5. Matriz Preliminar de Priorizacao

| ID | Debito | Area | Severidade | Impacto | Esforco | Prioridade |
|----|--------|------|------------|---------|---------|------------|
| TD-019 | Missing composite index pncp_raw_bids | DB | High | Alto (50-70% query speedup) | Baixo (1 migration) | **P0** |
| TD-020 | Soft-delete bloat pncp_raw_bids | DB | High | Alto (storage + performance) | Medio (cron + migration) | **P0** |
| TD-005 | Per-user Supabase tokens (SYS-023) | Backend | High | Alto (security posture) | Alto (refactor auth layer) | **P1** |
| TD-021 | profiles.plan_type CHECK vs FK | DB | High | Medio (data integrity) | Medio (migration + code changes) | **P1** |
| TD-025 | stripe_webhook_events sem retention | DB | Medium | Medio (storage) | Baixo (1 cron job) | **P1** |
| TD-026 | alert_sent_items sem retention | DB | Medium | Medio (storage) | Baixo (1 cron job) | **P1** |
| TD-027 | trial_email_log sem retention | DB | Medium | Medio (storage) | Baixo (1 cron job) | **P1** |
| TD-029 | Alert cron job sequencial | DB/Backend | Medium | Medio (latencia alertas) | Baixo (asyncio.gather) | **P1** |
| TD-034 | Backup sem PITR | DB/Infra | Medium | Alto (risco de dados) | Medio (paid tier + config) | **P1** |
| TD-035 | Search filters hook 600+ lines | Frontend | High | Medio (maintainability) | Medio (refactor) | **P1** |
| TD-022 | MD5 content hash | DB | High | Baixo (colisao rara) | Medio (migration + code) | **P2** |
| TD-023 | Missing covering index user_subscriptions | DB | Medium | Baixo (query optimization) | Baixo (1 migration) | **P2** |
| TD-024 | Missing index audit_events target_hash | DB | Medium | Baixo (admin queries) | Baixo (1 migration) | **P2** |
| TD-030 | RLS policy docs incompletas | DB | Medium | Medio (auditoria) | Baixo (SQL comments) | **P2** |
| TD-006 | Exchange rate USD/BRL hardcoded | Backend | Medium | Baixo (afeta poucos usuarios) | Baixo (API integration) | **P2** |
| TD-007 | Execute.py oversized (58KB) | Backend | Medium | Medio (maintainability) | Alto (refactor) | **P2** |
| TD-008 | Generate.py oversized (27KB) | Backend | Medium | Medio (maintainability) | Medio (refactor) | **P2** |
| TD-009 | Filter_stage.py oversized (20KB) | Backend | Medium | Medio (maintainability) | Medio (refactor) | **P2** |
| TD-010 | Quota.py oversized (65KB) | Backend | Medium | Medio (maintainability) | Alto (refactor) | **P2** |
| TD-036 | Visual regression testing ausente | Frontend | Medium | Medio (quality gate) | Medio (Percy setup) | **P2** |
| TD-037 | Saved filter presets | Frontend | Medium | Medio (UX) | Medio (feature dev) | **P2** |
| TD-038 | Modal focus trap edge cases | Frontend | Medium | Baixo (a11y) | Baixo (fix) | **P2** |
| TD-039 | Touch targets <44px legacy | Frontend | Medium | Baixo (a11y mobile) | Medio (audit + fix) | **P2** |
| TD-012 | Cryptography fork-safe testing | Backend | Medium | Baixo (risco em upgrade) | Baixo (CI test) | **P3** |
| TD-013 | PNCP health canary limitado | Backend | Medium | Baixo (deteccao) | Baixo (canary update) | **P3** |
| TD-014 | Cache hit rate marginal | Backend | Medium | Baixo (performance) | Medio (warming strategy) | **P3** |
| TD-015 | Railway 120s vs Gunicorn 180s timeout | Backend | Medium | Baixo (edge case) | Baixo (config align) | **P3** |
| TD-016 | 121 migrations sem squash | DB | Low | Baixo (dev velocity) | Medio (squash migration) | **P3** |
| TD-018 | Dual migration naming | DB | Low | Baixo (consistency) | Baixo (convention only) | **P3** |
| TD-028 | Audit hash sem versioning | DB | Medium | Baixo (futuro) | Baixo (1 column) | **P3** |
| TD-031 | Org ownership orphan risk | DB | Low | Baixo (edge case) | Baixo (monitoring query) | **P3** |
| TD-032 | conversations sem soft-delete | DB | Low | Baixo (compliance futuro) | Medio (schema change) | **P3** |
| TD-033 | Supabase FREE tier vs datalake size | DB/Infra | Low | Alto (blocker em escala) | Baixo (upgrade tier) | **P3** |
| TD-040 | /planos e /pricing duplicados | Frontend | Medium | Baixo (SEO) | Baixo (redirect) | **P3** |
| TD-011 | Single-worker no auto-scaling | Backend/Infra | Medium | Medio (throughput) | Medio (Railway config) | **P3** |
| TD-017 | OpenTelemetry HTTP-only | Backend | Low | Baixo | N/A (limitation) | **P4** |
| TD-041 | Raw hex colors vs tokens | Frontend | Low | Baixo (consistency) | Baixo (refactor) | **P4** |
| TD-042 | CSP unsafe-inline | Frontend | Low | Baixo (aceito) | N/A (Tailwind req) | **P4** |
| TD-043 | Storybook ausente | Frontend | Low | Baixo (dev experience) | Medio (setup) | **P4** |
| TD-044 | Icons missing aria-hidden | Frontend | Low | Baixo (a11y) | Baixo (audit) | **P4** |
| TD-045 | Sonner toast live regions | Frontend | Low | Baixo (a11y) | Baixo (config) | **P4** |
| TD-046 | Scroll jank SSE (mobile) | Frontend | Low | Baixo (UX mobile) | Medio (optimization) | **P4** |
| TD-047 | Bottom nav covers content | Frontend | Low | Baixo (UX mobile) | Baixo (CSS fix) | **P4** |
| TD-048 | i18n ausente | Frontend | Low | Baixo (BR-only product) | Alto (full i18n) | **P4** |
| TD-049 | Offline support ausente | Frontend | Low | Baixo (SaaS web app) | Alto (SW implementation) | **P4** |

**Legenda Prioridade:**
- **P0** -- Proximo sprint (impacto imediato, esforco baixo-medio)
- **P1** -- 1-2 meses (impacto alto, esforco variado)
- **P2** -- 2-4 meses (impacto medio, melhorias incrementais)
- **P3** -- 4-6 meses (baixo impacto, nice-to-have)
- **P4** -- Backlog (limitacoes aceitas ou baixa prioridade)

---

### 6. Perguntas para Especialistas

#### @data-engineer (Dara)

1. **TD-019 (composite index):** Qual o query plan atual do `search_datalake` RPC? Confirma que o composite index (uf, modalidade_id, data_publicacao) e a melhor estrategia vs partial indexes separados?
2. **TD-020 (soft-delete bloat):** Qual o tamanho atual de `pg_total_relation_size('pncp_raw_bids')`? O hybrid approach (hard-delete >3 dias) e seguro considerando que o crawler pode revisitar bids?
3. **TD-021 (plan_type FK):** Existe algum caso de uso que depende do CHECK constraint ser inline (e.g., migrations de rollback)? Ou podemos migrar para FK com seguranca?
4. **TD-022 (MD5 -> SHA-256):** Quais campos exatos sao incluidos no content_hash? A migracao para SHA-256 invalida todos os hashes existentes -- qual a estrategia de transicao?
5. **TD-025/026/027 (retention):** Confirma os periodos de retencao: stripe_webhook_events=90d, alert_sent_items=90d, trial_email_log=1y? Existe dependencia de relatorios que consulta dados antigos?
6. **TD-033 (FREE tier):** Quando estimamos ultrapassar 500MB? Devemos migrar para paid tier agora preventivamente?
7. **TD-034 (backup):** Qual o RTO/RPO aceitavel para o negocio? Weekly pg_dump para S3 e suficiente ou precisamos de PITR?
8. **TD-029 (alert cron):** Qual o numero atual de alertas ativos? O asyncio.gather com 10 concurrent e seguro considerando rate limits do Supabase?

#### @ux-design-expert (Uma)

1. **TD-035 (search filters 600+ lines):** Quais responsabilidades podem ser extraidas do useSearchFilters()? Sugestao de split: form state, validation, persistence, analytics?
2. **TD-036 (visual regression):** Percy ou Chromatic? Qual coverage minimo recomendado para o primeiro setup (top 10 componentes? todas as paginas?)?
3. **TD-037 (saved filters):** Qual o UX pattern recomendado? Dropdown com presets + "salvar atual"? Limite de presets por usuario?
4. **TD-038 (focus trap):** Quais edge cases especificos estao documentados? Nested modals? Portals?
5. **TD-039 (touch targets):** Quantos componentes legacy estao abaixo de 44px? Existe inventario?
6. **TD-040 (/planos vs /pricing):** Redirect 301 de /pricing -> /planos, ou manter ambos com canonical?
7. **TD-043 (Storybook):** Prioridade real considerando que temos 65+ componentes? Recomendacao de scope minimo?
8. **TD-046 (scroll jank SSE):** O debounce atual e de quantos ms? Virtualized list (react-window) seria mais efetivo?

---

**Proximo passo:** Revisao por @data-engineer (Phase 5) e @ux-design-expert (Phase 6), seguido de priorizacao final (Phase 7).
