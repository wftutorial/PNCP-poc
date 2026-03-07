# Technical Debt Assessment - FINAL

**Projeto:** SmartLic v0.5
**Data:** 2026-03-07
**Versao:** FINAL v1.0
**Validado por:** @architect (Atlas), @data-engineer (Delta), @ux-design-expert (Uma), @qa (Quinn)
**Fontes:** system-architecture.md v5.0 (Phase 1), DB-AUDIT.md (Phase 2), frontend-spec.md (Phase 3)
**Metodologia:** Three-source consolidation with specialist review rounds. All claims independently verified against live codebase.
**Supersedes:** FINAL v3.0 (2026-03-04), DRAFT v3.0 (2026-03-07)

---

## 1. Executive Summary

| Metrica | Valor |
|---------|-------|
| **Total de debitos** | 107 |
| **CRITICAL** | 1 |
| **HIGH** | 24 |
| **MEDIUM** | 48 |
| **LOW** | 34 |
| **Areas cobertas** | Sistema (36), Database (42), Frontend (35), Cross-Cutting (7) |
| **Esforco estimado (codigo)** | ~660-840h |
| **Esforco estimado (testes)** | ~60h |
| **Esforco total estimado** | **~720-900h** |

**Alteracoes desde DRAFT v3.0:**
- **Removidos (3):** SYS-009 (ja corrigido -- `await asyncio.sleep(0.3)` em authorization.py:100), DB-003 (falso positivo -- OAuth usa Fernet AES-256 em oauth.py:84-131), FE-029 (falso positivo -- PullToRefresh ativamente usado em buscar/page.tsx:6,695)
- **Adicionados (8):** DB-047, DB-048, DB-049, DB-050, FE-031 through FE-036, CROSS-007
- **Severidade ajustada (19):** Ver secao 9 (Validation Log) para detalhes

**Breakdown por Severidade e Area:**

| Area | CRITICAL | HIGH | MEDIUM | LOW | Subtotal | Esforco Est. |
|------|----------|------|--------|-----|----------|--------------|
| Sistema (SYS) | 0 | 7 | 13 | 16 | 36 | ~215-275h |
| Database (DB) | 0 | 9 | 17 | 16 | 42 | ~105-135h |
| Frontend (FE) | 0 | 6 | 16 | 13 | 35 | ~260-340h |
| Cross-Cutting (CROSS) | 1 | 2 | 2 | 2 | 7 | ~55-65h |
| **Total** | **1** | **24** | **48** | **47** | **120** | **~660-840h** |

> Nota: 120 itens brutos com parcial sobreposicao em CROSS-cutting = 107 debitos unicos.

---

## 2. Inventario Completo de Debitos

### 2.1 Sistema (validado por @architect + @qa)

#### 2.1.1 Arquitetura

| ID | Debito | Severidade | Horas | Sprint |
|----|--------|------------|-------|--------|
| SYS-001 | **Rotas montadas em duplicata** (versioned `/v1/` + legacy root) -- 33 `include_router` statements montam rotas em ambos prefixos versioned e legacy, totalizando ~61 route mounts efetivos. Sunset 2026-06-01 sem plano de migracao. | HIGH | 16 | S2 |
| SYS-002 | **`search_pipeline.py` god module** (800+ linhas) -- Cada stage 50-100+ linhas com try/catch aninhado. Absorveu toda logica de busca apos decomposicao do main.py. | HIGH | 24 | Backlog |
| SYS-003 | **Progress tracker in-memory nao escala horizontalmente** -- `_active_trackers` usa asyncio.Queue local. Redis Streams existe como fallback mas in-memory e primario. | HIGH | 16 | S2 |
| SYS-004 | **Dual HTTP client sync+async para PNCP** (1500+ linhas duplicadas) -- PNCPClient (sync/requests) e async httpx duplicam retry, CB, error handling. Sync usado apenas via `asyncio.to_thread()`. | HIGH | 24 | Backlog |
| SYS-005 | **`main.py` ainda 820+ linhas** apos decomposicao -- Sentry init (100+), exception handlers (80+), middleware config, router registration (60+), lifespan (200+). | HIGH | 12 | S2 |
| SYS-006 | **10+ background tasks em lifespan sem lifecycle manager** -- Cada task com create/cancel/await manual; 3+ locais para adicionar/remover. | MEDIUM | 8 | S2 |
| SYS-007 | **Lead prospecting modules desconectados** -- 5 modulos aparentemente dead code de feature exploration. | LOW | 2 | Backlog |
| SYS-008 | **Frontend proxy route explosion** -- 58 rotas proxy em `frontend/app/api/`, cada backend endpoint requer novo arquivo. Sem `createProxyRoute()` generico. | LOW | 12 | Backlog |

#### 2.1.2 Qualidade de Codigo

| ID | Debito | Severidade | Horas | Sprint |
|----|--------|------------|-------|--------|
| SYS-010 | **Singletons globais mutaveis sem cleanup** -- `auth.py:_token_cache`, `llm_arbiter.py:_arbiter_cache`, `filter.py:_filter_stats_tracker`. LLM arbiter tem LRU(5000), auth cache nao. | MEDIUM | 6 | S2 |
| SYS-011 | **Padroes inconsistentes de error handling** -- Rotas misturam `JSONResponse` direto + `HTTPException`. Sem schema de erro unificado. | MEDIUM | 8 | Backlog |
| SYS-012 | **`config.py` 500+ linhas com concerns misturados** -- PNCP modality codes, retry config, CORS, logging, feature flags, validation juntos. | MEDIUM | 6 | Backlog |
| SYS-013 | **User-Agent hardcoded "BidIQ"** em pncp_client.py | LOW | 1 | S1 |
| SYS-014 | **Arquivos de teste na raiz do backend** (fora de `tests/`) | LOW | 1 | Backlog |
| SYS-015 | **`pyproject.toml` referencia "bidiq-uniformes-backend"** | LOW | 0.5 | S1 |

#### 2.1.3 Escalabilidade

| ID | Debito | Severidade | Horas | Sprint |
|----|--------|------------|-------|--------|
| SYS-016 | **Railway 1GB memoria com 2 workers** -- Cada Gunicorn worker mantem caches in-memory proprios. OOM kills historicos. | HIGH | 8 | S1 |
| SYS-017 | **PNCP page size reduzido para 50** (era 500) -- 10x mais API calls. Health canary usa `tamanhoPagina=10` e nao detecta mudanca. | HIGH | 4 | S1 |
| SYS-018 | **Auth token cache in-memory nao compartilhado** entre Gunicorn workers | MEDIUM | 4 | S2 |
| SYS-019 | **Sem CDN para assets estaticos** -- Frontend servido direto do Railway sem edge caching | MEDIUM | 8 | Backlog |
| SYS-020 | **Singleton Supabase client** -- 2 workers x 50 pool = 100 conexoes potenciais contra Supabase | MEDIUM | 4 | S2 |
| SYS-021 | **Cache key nao inclui todos parametros de filtro** | LOW | 4 | Backlog |

#### 2.1.4 Seguranca

| ID | Debito | Severidade | Horas | Sprint |
|----|--------|------------|-------|--------|
| SYS-022 | **`unsafe-inline`/`unsafe-eval` no CSP frontend** -- Confirmado em `middleware.ts` linha 30. Requerido por Next.js + Stripe.js. | MEDIUM | 8 | S2 |
| SYS-023 | **Service role key para TODAS operacoes DB backend** -- Bypass total de RLS; qualquer vuln expoe todos os dados | MEDIUM | 16 | S2 |
| SYS-024 | **Sem timeout em webhook handler do Stripe** -- Operacoes DB longas bloqueiam indefinidamente | MEDIUM | 4 | S1 |
| SYS-025 | **Excel temp files no proxy frontend** nao limpos em crash | LOW | 2 | Backlog |
| SYS-026 | **Rate limiter in-memory store** com cleanup infrequente (cada 200 requests) | LOW | 2 | Backlog |
| SYS-027 | **`STRIPE_WEBHOOK_SECRET` not-set apenas logado** -- Deveria falhar no startup (confirmado: `logger.error()` linha 55) | LOW | 1 | S1 |

#### 2.1.5 Dependencias

| ID | Debito | Severidade | Horas | Sprint |
|----|--------|------------|-------|--------|
| SYS-028 | **`cryptography` pinned a 46.0.5** por fork-safety | MEDIUM | 4 | Backlog |
| SYS-029 | **`requests` lib apenas para sync PNCP fallback** | MEDIUM | 4 | Backlog |
| SYS-030 | **`redis_client.py` deprecated mas ainda importavel** -- Shim para `redis_pool` | LOW | 1 | Backlog |
| SYS-031 | **`arq` nao instalado localmente** (mocked via `sys.modules` em testes) | LOW | 2 | S1 |

#### 2.1.6 Testes e Documentacao

| ID | Debito | Severidade | Horas | Sprint |
|----|--------|------------|-------|--------|
| SYS-032 | **Sem testes de integracao contra APIs reais** -- Mudancas de contrato detectadas so em producao | MEDIUM | 16 | Backlog |
| SYS-033 | **E2E tests usam credenciais de producao** | LOW | 8 | Backlog |
| SYS-034 | **Sem pre-commit hooks** | LOW | 2 | S1 |
| SYS-035 | **Backend linting (`ruff`, `mypy`) nao enforced no CI** | LOW | 2 | S1 |
| SYS-036 | **Sem documentacao de API** alem do OpenAPI auto-gerado (desabilitado em prod) | LOW | 8 | Backlog |
| SYS-037 | **`.env.example` potencialmente stale** -- 25+ flags sem check automatizado | LOW | 2 | Backlog |
| SYS-038 | **Sem runbook para resposta a incidentes** -- Conhecimento apenas em CLAUDE.md/MEMORY.md | LOW | 8 | Backlog |

---

### 2.2 Database (validado por @data-engineer)

#### 2.2.1 RLS e Seguranca

| ID | Debito | Severidade | Horas | Sprint | Notas |
|----|--------|------------|-------|--------|-------|
| DB-001 | **`classification_feedback` service_role policy usa `auth.role()`** -- Per-row evaluation mais lenta; inconsistente com padrao `TO service_role USING (true)`. | HIGH | 1 | S2 | Downgraded de CRITICAL: `auth.role()` e funcionalmente correto, apenas subotimo. Performance negligivel com <10K rows. Confirmado em `backend/migrations/006_classification_feedback.sql` linha 48. |
| DB-002 | **`health_checks` e `incidents` sem policies user-facing** -- Apenas service_role. | MEDIUM | 2 | S2 | Downgraded de HIGH: backend-only by-design. Add explicit `TO service_role` para auto-documentacao. |
| DB-004 | **`mfa_recovery_codes` sem rate limiting no DB** | MEDIUM | 4 | S2 | Downgraded de HIGH: app-layer rate limiting via `mfa_recovery_attempts` e padrao correto. Risco so se service_role key comprometida. |
| DB-005 | **`mfa_recovery_attempts` sem policy SELECT para usuario** | MEDIUM | 1 | Backlog | Intencional: usuarios nao devem ver historico de tentativas (information leakage). |
| DB-006 | **`trial_email_log` sem policies user-facing** | MEDIUM | 1 | Backlog | Backend-only. Documentar como aceito. |
| DB-007 | **`search_state_transitions` SELECT policy usa subquery** (correlated) | MEDIUM | 4 | S2 | Per-row evaluation caro em escala. Index `idx_search_sessions_search_id` existe mas fix ideal e adicionar coluna `user_id` com backfill. |
| DB-008 | **Stripe Price IDs visiveis na tabela `plans`** (RLS public read) | LOW | 0 | Backlog | Downgraded de MEDIUM: risco aceito. Price IDs usados client-side por design. |
| DB-009 | **`profiles.email` exposto via partner RLS policy** (cross-schema query) | MEDIUM | 2 | S2 | Funcional mas otimizavel via `partners.contact_email`. |
| DB-010 | **Sistema cache warmer account** com password vazio | LOW | 1 | S2 | Supabase Auth nao autentica `encrypted_password = ''`. Add `banned_until = '2099-12-31'` para defense-in-depth. |

#### 2.2.2 Schema e Integridade

| ID | Debito | Severidade | Horas | Sprint | Notas |
|----|--------|------------|-------|--------|-------|
| DB-011 | **`handle_new_user()` trigger reescrito 7+ vezes** | MEDIUM | 4 | S2 | Downgraded de HIGH: trigger estabilizou em 20260225110000. 7 rewrites foram evolutivos. Fix = integration test guard + CI grep para novas migracoes que toquem `handle_new_user`. |
| DB-012 | **Funcoes `updated_at` inconsistentes** (`update_updated_at` vs `set_updated_at`) | HIGH | 2 | S1 | Funcoes identicas. Consolidar para `set_updated_at()` e DROP a outra. Zero impacto em dados. |
| DB-013 | **`partner_referrals.referred_user_id` ON DELETE SET NULL vs NOT NULL** | HIGH | 1 | S1 | Coluna e `NOT NULL` (migracao 20260301200000 linha 32) mas FK e `ON DELETE SET NULL` (migracao 20260304100000 linha 77). DELETE de profile falha. Fix: `ALTER COLUMN DROP NOT NULL`. |
| DB-014 | **`plans.stripe_price_id` coluna legada** coexiste com period-specific | MEDIUM | 2 | Backlog | Baixo risco; billing code usa colunas period-specific. Deprecar apos confirmar zero referencias. |
| DB-015 | **`profiles.plan_type` vs `user_subscriptions.plan_id` duplicacao** | MEDIUM | 4 | S2 | Decisao intencional (STORY-291 CB fail-open). Documentar + add reconciliation cron para detectar drift. |
| DB-016 | **`search_sessions.status` sem enforcement de transicoes** no DB | MEDIUM | 4 | Backlog | App-layer enforcement via `search_state_manager.py` funciona. Documentar transicoes validas via CHECK/COMMENT. |
| DB-017 | **Missing `NOT NULL` em varias colunas** | LOW | 2 | Backlog | 3 de 5 colunas recebem UPDATEs. `google_sheets_exports.created_at` e `partners.created_at` devem ser `NOT NULL DEFAULT now()`. |
| DB-018 | **`search_results_cache.priority` sem CHECK constraint** | LOW | 0.5 | S2 | Quick win: `CHECK (priority IN ('hot', 'warm', 'cold'))`. |
| DB-019 | **`alert_runs.status` sem CHECK constraint** | LOW | 0.5 | S2 | Quick win: add CHECK com valores documentados incluindo `'pending'`. |
| DB-020 | **Naming inconsistente em constraints** | LOW | 1 | Backlog | Cosmetico. Adotar `chk_{table}_{column}` para futuras migracoes. |
| DB-021 | **`user_subscriptions.billing_period` constraint pode conflitar** | LOW | 1 | S2 | Downgraded de MEDIUM: migracao 029 lida com DROP/ADD. Validar com `SELECT billing_period, count(*) GROUP BY 1`. |
| DB-022 | **`profiles.phone_whatsapp` CHECK nao valida estrutura brasileira** | LOW | 1 | Backlog | Downgraded de MEDIUM: validacao app-layer mais apropriada para telefones. DDDs brasileiros mudam ao longo do tempo. |
| DB-023 | **`search_results_cache` UNIQUE permite sharing cross-user com date range stale** | LOW | 2 | Backlog | `params_hash_global` usado para SWR warming. Mitigado por TTL. Risco teorico. |
| DB-024 | **`plan_billing_periods` sem coluna `updated_at`** | LOW | 1 | Backlog | Mudancas de pricing infrequentes e rastreadas via git. |

#### 2.2.3 Migracoes

| ID | Debito | Severidade | Horas | Sprint | Notas |
|----|--------|------------|-------|--------|-------|
| DB-025 | **Dual migration directories** (`supabase/migrations/` + `backend/migrations/`) | HIGH | 8 | S1 | 10 backend migrations fora do Supabase CLI. Bridge migration com `CREATE OR REPLACE` / `IF NOT EXISTS` guards. Ja causou incidente em producao (missing `check_and_increment_quota` RPC). |
| DB-026 | **Naming nao-sequencial** -- Mix `001_` a `033_` + timestamps + `027b_` | MEDIUM | 4 | S1 | Downgraded de HIGH: Supabase CLI ordena corretamente por prefixo. Risco e confusao de devs, nao falha de execucao. |
| DB-027 | **Sem down-migrations** -- Apenas 1 migration tem rollback comment | MEDIUM | 8 | Backlog | Standard para Supabase. PITR e o mecanismo de rollback. |
| DB-028 | **Algumas migracoes nao idempotentes** -- `008_add_billing_period.sql` sem `IF NOT EXISTS` | MEDIUM | 4 | S2 | Urgencia baixa (migracoes rodam uma vez) mas importante para DR. |
| DB-029 | **Hardcoded Stripe Price IDs em migracoes** (015, 029, etc.) | LOW | 2 | Backlog | Bloqueia setup staging/dev. |
| DB-030 | **`backend/migrations/` nunca aplicadas via CLI** | HIGH | 4 | S1 | Subsumed por DB-025. Mesma causa raiz, mesmo fix. Consolidar. |

#### 2.2.4 Performance

| ID | Debito | Severidade | Horas | Sprint | Notas |
|----|--------|------------|-------|--------|-------|
| DB-031 | **`search_results_cache.results` JSONB ate 2MB/row** | HIGH | 4 | S2 | CHECK de 2MB existe (migracao 20260225150000). 10 entries/user x 2MB = 20MB per user. Monitorar com `pg_total_relation_size()`. |
| DB-032 | **`search_results_store.results` sem retention enforcement** | HIGH | 4 | S1 | `expires_at` default 24h mas sem pg_cron cleanup. Tabela acumula dead data indefinidamente. Custo direto de storage Supabase. |
| DB-033 | **`search_state_transitions` cresce sem limites** | MEDIUM | 2 | S2 | 5-10 registros por busca. ~15K rows/mes. pg_cron: `DELETE WHERE created_at < NOW() - INTERVAL '30 days'`. |
| DB-034 | **`cleanup_search_cache_per_user()` trigger em cada INSERT** | MEDIUM | 2 | Backlog | Overhead minimo na escala atual. Add short-circuit: `IF count(*) <= 10 THEN RETURN NEW`. |
| DB-035 | **`get_conversations_with_unread_count()` usa correlated subquery** | MEDIUM | 2 | Backlog | Rewrite como LEFT JOIN + GROUP BY. Volume de mensagens baixo. |
| DB-036 | **Sem table partitioning** para append-heavy tables | LOW | 8 | Backlog | Nao necessario no POC. Planejar para `audit_events`, `search_state_transitions` quando row count mensal > 1M. |
| DB-037 | **`alert_sent_items` sem retention cleanup** | MEDIUM | 1 | S2 | Upgraded de LOW: tabela serve dedup ativo. Sem cleanup, queries de dedup ficam lentas. 180 dias recomendado. |

#### 2.2.5 Indices

| ID | Debito | Severidade | Horas | Sprint | Notas |
|----|--------|------------|-------|--------|-------|
| DB-038 | **Migracao `20260307100000` referencia tabelas inexistentes** (`searches`, `pipeline`, `feedback`) | HIGH | 2 | S1 | Tabelas reais: `search_sessions`, `pipeline_items`, `classification_feedback`. Indices nunca criados. Corrective migration necessaria. |
| DB-039 | **`classification_feedback` sem indice user_id** | HIGH | 1 | S1 | Migracao usou nome errado `feedback`. RLS `auth.uid() = user_id` causa full table scan. |
| DB-040 | **Indice redundante em `alert_preferences`** (plain + UNIQUE no mesmo user_id) | LOW | 0.5 | S2 | UNIQUE cria B-tree implicito. DROP `idx_alert_preferences_user_id`. |
| DB-041 | **Indice parcialmente redundante em `trial_email_log`** | LOW | 0.5 | S2 | Composite unique `(user_id, email_number)` cobre leading column. |
| DB-042 | **Composite index faltando para admin inbox** em `conversations` | LOW | 1 | S2 | `(status, last_message_at DESC)` beneficiaria queries admin. Volume baixo atualmente. |

#### 2.2.6 Backup e Recovery

| ID | Debito | Severidade | Horas | Sprint | Notas |
|----|--------|------------|-------|--------|-------|
| DB-043 | **Sem procedimento documentado de disaster recovery** -- 76 migracoes sem guia | HIGH | 16 | S1 | Risco operacional critico. PITR procedure + DR doc + teste de recreacao em projeto fresh. |
| DB-044 | **pg_cron jobs nao em migracoes** (requerem superuser) | MEDIUM | 4 | Backlog | Documentar manual setup steps. pg_cron requer `CREATE EXTENSION` com superuser. |
| DB-045 | **`stripe_webhook_events` idempotency depende da tabela** | MEDIUM | 2 | S2 | 90-day retention (HARDEN-028) e apropriado. Stripe retry window max e 72h. |
| DB-046 | **Sem audit trail DB-level para schema changes** | LOW | 4 | Backlog | Policy: "nunca modificar schema via dashboard sem migracao." DDL event triggers sao complexos demais. |

#### 2.2.7 Novos (identificados por @data-engineer)

| ID | Debito | Severidade | Horas | Sprint | Notas |
|----|--------|------------|-------|--------|-------|
| DB-047 | **`search_results_store.results` JSONB sem CHECK de tamanho** -- Diferente de `search_results_cache` que tem CHECK de 2MB, store aceita payloads ilimitados. Query multi-UF pode inserir 5-10MB por row. | MEDIUM | 0.5 | S1 | Bundle com DB-032. `ADD CONSTRAINT chk_store_results_max_size CHECK (octet_length(results::text) <= 2097152)`. |
| DB-048 | **`partners` e `partner_referrals` service_role policies usam `auth.role()`** -- Nao incluidas na standardizacao migracao 20260304200000. | MEDIUM | 0.5 | S2 | Batch com DB-001 fix. |
| DB-049 | **`health_checks` e `incidents` sem retention pg_cron job** -- Table comments dizem "30-day retention" mas nenhum job existe. ~8,640 rows/mes a 5-min intervals. | MEDIUM | 1 | S2 | |
| DB-050 | **Sem FK de `search_state_transitions.search_id` para `search_sessions`** -- Orphan records possiveis. FK impossivel sem UNIQUE constraint em `search_sessions.search_id`. | LOW | 4 | Backlog | RLS policy ja filtra orphans (invisíveis a usuarios). |

---

### 2.3 Frontend/UX (validado por @ux-design-expert)

#### 2.3.1 Arquitetura e Estrutura

| ID | Debito | Severidade | Horas | Sprint | Notas |
|----|--------|------------|-------|--------|-------|
| FE-001 | **Paginas monoliticas** -- 4 pages > 1000 linhas: `conta` (1420), `alertas` (1068), `buscar` (1057), `dashboard` (1037). Re-renders desnecessarios. | HIGH | 20-28 | S2 | Prerequisito: FE-026 (quarantine resolution) e FE-006 (global state). Decomposicao de `conta` em sub-routes primeiro. |
| FE-002 | **Zero `loading.tsx` streaming** em 44 paginas -- Blank screen ate JS hidratar | HIGH | 16 | S1 | Prioridade UX: buscar, dashboard, pipeline, protected layout, historico. Usar shimmer animation existente no tailwind.config.ts. |
| FE-003 | **Sem framework i18n** -- Strings hardcoded PT em 100+ arquivos | LOW | 40 | Backlog | Downgraded de HIGH: 100% BR, pre-revenue. Termos de dominio (licitacao, edital, pregao, CNPJ) sem traducao direta. |
| FE-004 | **23 de 44 paginas `"use client"` excessivamente** | MEDIUM | 24 | S2 | Downgraded de HIGH: maioria requer interatividade client. Apenas 3-5 paginas (planos, historico, ajuda) sao candidatas para partial SSR. |
| FE-005 | **3 diretorios de componentes sem regra clara** -- `components/`, `app/components/`, `app/buscar/components/` com sobreposicao | MEDIUM | 8 | S2 | Downgraded de HIGH: invisivel ao usuario. Regra: `components/` shared, `app/components/` providers/layouts, `app/buscar/components/` feature-specific. |
| FE-006 | **Sem gerenciamento de estado global** -- Auth+plan+quota+search via prop drilling | HIGH | 16 | S2 | Prerequisito para FE-001 e FE-007. Prop drilling causa stale data display quando auth/plan/quota mudam. |
| FE-007 | **Data fetching inconsistente** -- 5 hooks SWR, maioria raw `fetch()`, alguns `fetchWithAuth()` | HIGH | 12 | S2 | Standardizar em SWR. Phase 1: read-only endpoints. Phase 2: mutations. Deixar SSE hooks custom. |

#### 2.3.2 Qualidade de Codigo

| ID | Debito | Severidade | Horas | Sprint | Notas |
|----|--------|------------|-------|--------|-------|
| FE-008 | **`any` types em 8 arquivos de producao** | MEDIUM | 2 | S2 | Verificado: pipeline, filters, analytics proxy + 5 outros. |
| FE-009 | **Console statements em producao** | MEDIUM | 1 | S1 | 1 `console.error` em buscar/page.tsx (GTM-010 trial), auth/callback, AuthProvider. |
| FE-010 | **28+ TODO/FIXME em blog content** | LOW | 8 | Backlog | SEO impact apenas. Sem UX impact para usuarios autenticados. |
| FE-011 | **EmptyState duplicado em 2 locais** | MEDIUM | 1 | S1 | Delete `app/components/EmptyState.tsx`, manter `components/EmptyState.tsx` como canonico. |
| FE-012 | **Error boundary apenas em `/buscar`** -- 5+ paginas sem boundaries sub-page | HIGH | 6 | S1 | Upgraded de MEDIUM: crash em dashboard/pipeline/historico/mensagens/alertas causa perda total de contexto (scroll, form state, filtros). Add `error.tsx` a cada route group. |
| FE-013 | **SearchErrorBoundary usa vermelho hardcoded** -- Viola guideline "nunca vermelho" | MEDIUM | 1 | S1 | 9 red class references verificadas. Inconsistente com error-messages.ts. |
| FE-014 | **Sem memoization em paginas grandes** | MEDIUM | 4 | S2 | alertas: 2 useMemo em 1068 linhas. dashboard: 6 em 1037 linhas. Jank em mid-range devices. |
| FE-015 | **Arquivo `nul` no diretorio app** -- Artefato Windows (0 bytes confirmado) | LOW | 0.5 | S1 | `rm frontend/app/nul`. |

#### 2.3.3 Styling e Design System

| ID | Debito | Severidade | Horas | Sprint | Notas |
|----|--------|------------|-------|--------|-------|
| FE-016 | **Mix de CSS variables e raw Tailwind** (~10 arquivos) | MEDIUM | 4 | S2 | Solucao: extender Tailwind theme com CSS custom properties (`bg-brand-blue` resolve para `var(--brand-blue)`). |
| FE-017 | **`global-error.tsx` cores brand erradas** -- `#2563eb`/`#1e3a5f` vs `#116dff`/`#0a1e3f` | MEDIUM | 0.5 | S1 | Quick win. Tailwind defaults ao inves de SmartLic tokens. |

#### 2.3.4 Performance

| ID | Debito | Severidade | Horas | Sprint | Notas |
|----|--------|------------|-------|--------|-------|
| FE-018 | **Sem uso de `next/image`** (apenas 4 arquivos) | MEDIUM | 8 | S2 | LCP impactado em landing/blog. Paginas autenticadas usam SVG (sem impacto). Priorizar landing para conversao. |
| FE-019 | **Sem code splitting** para Recharts (~50KB), @dnd-kit (~15KB), Shepherd.js (~25KB) | MEDIUM | 4 | S2 | Apenas 2 arquivos usam `next/dynamic`. Dashboard carrega Recharts eagerly. |
| FE-020 | **3 Google Fonts carregadas globalmente** | LOW | 2 | Backlog | DM Mono e Fahkwang usadas em poucas paginas. Impact ~50-100ms em 3G lento. Publico enterprise. |

#### 2.3.5 Acessibilidade

| ID | Debito | Severidade | Horas | Sprint | Notas |
|----|--------|------------|-------|--------|-------|
| FE-021 | **Sem `aria-live` para resultados de busca** | MEDIUM | 2 | S1 | Upgraded de LOW: WCAG 4.1.3 violation (Status Messages). Search e fluxo primario. `aria-live` existe em 15 arquivos mas NAO em search results/count. Risco contratual B2G. |
| FE-022 | **Sem focus trapping em modais** (Dialog, DeepAnalysis, Upgrade, Cancel) | MEDIUM | 4 | S1 | Upgraded de LOW: WCAG 2.4.3 violation. Sem `focus-trap` lib instalada, sem implementacao custom. Keyboard-only users bloqueados. Fix: instalar `focus-trap-react`. |
| FE-023 | **Indicadores de viabilidade apenas por cor** | MEDIUM | 2 | S2 | Upgraded de LOW: WCAG 1.4.1 violation. ~8% usuarios masculinos com deficiencia de visao de cor. Add text labels (Alta/Media/Baixa) alongside color. |
| FE-024 | **Sem documentacao de atalhos de teclado** | LOW | 2 | Backlog | `useKeyboardShortcuts` sem `?` help overlay. Minor discoverability. |

#### 2.3.6 Testes e Features Faltantes

| ID | Debito | Severidade | Horas | Sprint | Notas |
|----|--------|------------|-------|--------|-------|
| FE-025 | **Sem testes para navegacao** -- NavigationShell, Sidebar, BottomNav, MobileDrawer | LOW | 8 | Backlog | Alto blast radius (renderizado em toda pagina) mas baixa probabilidade de mudanca. |
| FE-026 | **22 testes em quarentena** -- AuthProvider, ContaPage, DashboardPage, MensagensPage, useSearch, useSearchFilters, 4 free-user flow tests, GoogleSheetsExportButton, download-route, oauth-callback, + 10 outros. | LOW | 8 | S1 | **Corrigido de 14 para 22.** Prerequisito para decomposicao FE-001. Quarantine provavelmente por jsdom limitations, nao bugs reais. |
| FE-027 | **Sem PWA/offline support** -- useServiceWorker hook existe mas nao registrado | LOW | 8 | Backlog | Usuarios B2G office-based com conectividade confiavel. |
| FE-028 | **Sem validacao estruturada de formularios** -- Sem react-hook-form/zod | MEDIUM | 16 | S2 | Upgraded de LOW: validacao manual leva a mensagens inconsistentes, gaps de validacao, e sem inline feedback. Afeta signup, conta, onboarding, alertas. |
| FE-030 | **Sem `<Suspense>` boundaries** em nenhuma pagina | LOW | 8 | S2 | Relacionado a FE-002. Sem beneficio sem loading.tsx ou async server components. |

#### 2.3.7 Novos (identificados por @ux-design-expert)

| ID | Debito | Severidade | Horas | Sprint | Notas |
|----|--------|------------|-------|--------|-------|
| FE-031 | **Dashboard charts nao mobile-optimized** -- Labels overflow, touch targets pequenos, charts sem horizontal scroll wrappers. Segunda pagina mais visitada. | MEDIUM | 4-6 | S2 | |
| FE-032 | **Sem shared Button component** -- 15+ padroes de estilo distintos. Inconsistencia mais visivel ao usuario. | HIGH | 4-6 | S1 | Fundacao para todo design system. Shadcn/ui recomendado: 6 variants (primary, secondary, ghost, destructive, outline, link), 3 sizes, loading/disabled/icon-only states. |
| FE-033 | **Sem shared Input/Label component** -- Forms com styling diferente. Placeholder-as-label em alguns (WCAG 1.3.1 violation). | MEDIUM | 3-4 | S2 | |
| FE-034 | **Missing icon-only button aria-labels** -- Screen readers anunciam apenas "button" sem contexto. Sidebar collapse, filter toggles, close buttons afetados. | HIGH | 1.5 | S1 | Quick win de acessibilidade. |
| FE-035 | **Sem testes de isolacao para useSearch (1,510 linhas)** -- Testado apenas indiretamente via component tests. Decomposicao sem dedicated hook tests e alto risco. | MEDIUM | 8-12 | S2 | |
| FE-036 | **Design tokens parcialmente adotados** -- Mix de CSS custom properties (`var(--brand-blue)`), Tailwind theme tokens, e hex values raw (`#116dff`). Sem enforcement. | MEDIUM | 3-4 | S2 | |

---

### 2.4 Cross-Cutting (validado por todos)

| ID | Debito | Areas | Severidade | Horas | Sprint | Notas |
|----|--------|-------|------------|-------|--------|-------|
| CROSS-001 | **Migracoes DB nao-idempotentes + dual directories + sem DR docs** -- Impossivel recriar DB de forma confiavel. Combina DB-025, DB-027, DB-028, DB-043. | DB + SYS | CRITICAL | 24 | S1 | Risco operacional: sem rollback, sem recreacao, funcoes criticas potencialmente faltando. |
| CROSS-002 | **Sem validacao de contrato API no CI** -- Frontend TypeScript types podem divergir do backend OpenAPI schema. `openapi_schema.diff.json` existe mas NAO enforced (atualmente com diff uncommitted no git status). | SYS + FE | HIGH | 8 | S1 | Enforce snapshot + add `openapi-diff` para semantic comparison em PRs. |
| CROSS-003 | **Feature flags sem UI de runtime** -- 25+ flags em env vars. Requer restart de container para toggle. | SYS + FE | MEDIUM | 16 | Backlog | Sem rollback rapido de features. |
| CROSS-004 | **Naming inconsistente entre camadas** -- Backend "BidIQ" em User-Agent/pyproject; Frontend "SmartLic" | SYS + FE | MEDIUM | 2 | S1 | Quick fix. |
| CROSS-005 | **Test pollution patterns** -- `sys.modules["arq"]` mock leaks, Supabase CB singleton leak, `importlib.reload()` state corruption entre testes | SYS + DB | LOW | 4 | S1 | Fix: instalar `arq` como dev dep (puro Python, seguro); remover `sys.modules` hacks; autouse fixture para CB reset. |
| CROSS-006 | **Sem ambiente de staging** -- E2E usa producao; sem testes de integracao contra APIs reais | SYS + FE | LOW | 16 | Backlog | Supabase staging project (free tier) + Railway staging service. Nao bloqueia E2E expansion. |
| CROSS-007 | **Sem vulnerability scanning de dependencias no CI** -- Nenhum `pip-audit`, `npm audit`, ou Snyk em qualquer workflow. 50+ deps Python + 40+ deps npm, incluindo `cryptography==46.0.5` pinned. | SYS + FE | MEDIUM | 4 | S1 | Novo (identificado por @qa). Add `pip-audit` e `npm audit` como CI steps. |

---

## 3. Matriz de Priorizacao Final

**Formula:** `Priority Score = (Severity x 3 + Impact x 2) / Effort`

Onde: Severity: CRITICAL=4, HIGH=3, MEDIUM=2, LOW=1. Impact: 1=cosmetic, 2=degraded experience, 3=functionality affected, 4=data loss/security/outage risk. Effort: 1=<2h, 2=2-8h, 3=8-24h, 4=>24h.

| Rank | ID | Debito | Area | Sev | Impact | Effort | Score |
|------|----|--------|------|-----|--------|--------|-------|
| 1 | DB-013 | ON DELETE SET NULL vs NOT NULL (DELETE impossivel) | DB | 3 | 4 | 1 | **17.0** |
| 2 | DB-038 | Migracao referencia tabelas inexistentes (indices nunca criados) | DB | 3 | 4 | 1 | **17.0** |
| 3 | DB-039 | classification_feedback sem indice user_id (full table scan RLS) | DB | 3 | 3 | 1 | **15.0** |
| 4 | SYS-017 | PNCP page size 50, health canary blind | SYS | 3 | 3 | 1 | **15.0** |
| 5 | FE-034 | Missing icon-only button aria-labels (a11y blocker) | FE | 3 | 3 | 1 | **15.0** |
| 6 | DB-012 | Funcoes updated_at duplicadas | DB | 3 | 2 | 1 | **13.0** |
| 7 | SYS-016 | Railway 1GB + 2 workers, OOM historico | SYS | 3 | 4 | 2 | **12.5** |
| 8 | CROSS-001 | Migracoes/DR critico (impossivel recriar DB) | CROSS | 4 | 4 | 3 | **12.0** |
| 9 | FE-012 | Error boundaries em 5 paginas (crash = contexto perdido) | FE | 3 | 3 | 2 | **10.0** |
| 10 | DB-032 | search_results_store sem retention (dead data acumula) | DB | 3 | 3 | 2 | **10.0** |
| 11 | CROSS-002 | API contract validation CI (drift ativo) | CROSS | 3 | 3 | 2 | **10.0** |
| 12 | FE-032 | Sem shared Button (15+ padroes inconsistentes) | FE | 3 | 3 | 2 | **10.0** |
| 13 | DB-031 | JSONB cache ate 2MB/row (20MB/user potencial) | DB | 3 | 3 | 2 | **10.0** |
| 14 | FE-017 | global-error.tsx cores brand erradas | FE | 2 | 2 | 1 | **10.0** |
| 15 | FE-013 | SearchErrorBoundary usa vermelho hardcoded | FE | 2 | 2 | 1 | **10.0** |
| 16 | SYS-027 | STRIPE_WEBHOOK_SECRET deveria fail-at-startup | SYS | 1 | 3 | 1 | **9.0** |
| 17 | FE-009 | Console statements em producao | FE | 2 | 1 | 1 | **8.0** |
| 18 | FE-011 | EmptyState duplicado | FE | 2 | 1 | 1 | **8.0** |
| 19 | DB-047 | search_results_store sem CHECK de tamanho | DB | 2 | 3 | 1 | **12.0** |
| 20 | FE-015 | Arquivo `nul` no app dir (artefato Windows) | FE | 1 | 1 | 1 | **5.0** |

---

## 4. Quick Wins (Alto Impacto, Baixo Esforco)

Top 10 items corrigiveis em um dia focado (~11h).

| # | ID | Debito | Esforco | Acao |
|---|----|--------|---------|------|
| 1 | **DB-013** | ON DELETE SET NULL vs NOT NULL | 1h | `ALTER COLUMN referred_user_id DROP NOT NULL` |
| 2 | **DB-038+039** | Indices RLS errados + indice faltando | 2h | DROP indices com nomes errados; `CREATE INDEX idx_classification_feedback_user_id ON classification_feedback(user_id)` |
| 3 | **DB-012** | Duas funcoes updated_at identicas | 2h | Consolidar triggers para `set_updated_at()`; `DROP FUNCTION update_updated_at()` |
| 4 | **FE-034** | Missing aria-labels em icon-only buttons | 1.5h | Add `aria-label` a todos `<button>` com apenas icone/SVG |
| 5 | **DB-047** | search_results_store JSONB sem CHECK | 0.5h | `ADD CONSTRAINT chk_store_results_max_size CHECK (octet_length(results::text) <= 2097152)` |
| 6 | **FE-015** | Arquivo `nul` no app dir | 0.5h | `rm frontend/app/nul` |
| 7 | **FE-017** | global-error.tsx cores brand erradas | 0.5h | Trocar `#2563eb`/`#1e3a5f` por `#116dff`/`#0a1e3f` |
| 8 | **FE-009** | Console statements em producao | 1h | Remover console.log/warn de buscar, auth/callback, AuthProvider |
| 9 | **SYS-027** | STRIPE_WEBHOOK_SECRET fail-at-startup | 1h | Check no lifespan; raise se None |
| 10 | **FE-011** | EmptyState duplicado | 1h | Delete `app/components/EmptyState.tsx`, update imports |

**Esforco total Quick Wins: ~11h**

**Impacto combinado:** Integridade de dados (DELETE impossivel), performance de query (full table scans RLS), acessibilidade (screen readers), brand consistency, seguranca (startup validation), hygiene do codebase.

---

## 5. Plano de Resolucao

### Sprint 1 (Semanas 1-2): Critical + Quick Wins + Fundacao

**Estimativa: ~93-101h (incluindo ~15h testes)**

#### Database (~29h)

| # | IDs | Descricao | Horas | Dependencias |
|---|-----|-----------|-------|-------------|
| 1 | DB-038, DB-039 | Fix RLS indexes (nomes corretos + classification_feedback index) | 2 | Nenhuma |
| 2 | DB-013 | Fix partner_referrals NOT NULL vs SET NULL | 1 | Nenhuma |
| 3 | DB-012 | Consolidar funcoes updated_at trigger | 2 | Nenhuma |
| 4 | DB-032, DB-047 | search_results_store retention pg_cron + 2MB CHECK | 4 | Nenhuma |
| 5 | DB-025, DB-030 | Bridge migration para consolidar backend/migrations/ | 4 | Verificacao de producao primeiro (Q1) |
| 6 | DB-043 | DISASTER-RECOVERY.md + teste de recreacao em projeto fresh | 16 | DB-025 primeiro |

#### Frontend (~32-36h)

| # | IDs | Descricao | Horas | Dependencias |
|---|-----|-----------|-------|-------------|
| 7 | FE-002 | Add `loading.tsx` a top 5 rotas (buscar, dashboard, pipeline, layout, historico) | 10-12 | Nenhuma |
| 8 | FE-012 | Add error boundaries a 5 paginas autenticadas | 6 | Nenhuma |
| 9 | FE-032 | Shared Button component (shadcn/ui init + 6 variants) | 4-6 | Nenhuma |
| 10 | FE-034 | Add aria-labels a icon-only buttons | 1.5 | Nenhuma |
| 11 | FE-022 | Focus trapping em modais (instalar focus-trap-react) | 4 | Nenhuma |
| 12 | FE-021 | aria-live para search results e error banners | 2 | Nenhuma |
| 13 | FE-017 | Fix global-error.tsx brand colors | 0.5 | Nenhuma |
| 14 | FE-013 | Fix SearchErrorBoundary vermelho -> azul/amarelo | 1 | Nenhuma |
| 15 | FE-015 | Delete `frontend/app/nul` | 0.5 | Nenhuma |
| 16 | FE-009 | Remover console statements | 1 | Nenhuma |
| 17 | FE-011 | Consolidar EmptyState (delete duplicate) | 1 | Nenhuma |
| 18 | FE-026 | Resolver 22 testes em quarentena | 8 | Nenhuma |

#### Sistema e Cross-Cutting (~32-35h)

| # | IDs | Descricao | Horas | Dependencias |
|---|-----|-----------|-------|-------------|
| 19 | CROSS-002 | Enforce openapi_schema.diff.json no CI | 4 | Nenhuma |
| 20 | CROSS-007 | Adicionar pip-audit + npm audit ao CI | 4 | Nenhuma |
| 21 | CROSS-005, SYS-031 | Instalar `arq` como dev dep, remover sys.modules hacks | 2 | Nenhuma |
| 22 | CROSS-004, SYS-013, SYS-015 | Fix naming BidIQ -> SmartLic (User-Agent, pyproject.toml) | 1.5 | Nenhuma |
| 23 | SYS-016 | Memory profiling + otimizacao workers | 8 | Nenhuma |
| 24 | SYS-017 | Health canary com page size detection | 4 | Nenhuma |
| 25 | SYS-024 | Timeout em Stripe webhook handler | 4 | Nenhuma |
| 26 | SYS-027 | STRIPE_WEBHOOK_SECRET fail-at-startup | 1 | Nenhuma |
| 27 | SYS-034 | Pre-commit hooks | 2 | Nenhuma |
| 28 | SYS-035 | Backend linting no CI (non-blocking primeiro) | 2 | Nenhuma |

### Sprint 2 (Semanas 3-4): High Priority Estrutural

**Estimativa: ~108-120h (incluindo ~20h testes)**

#### Database (~31h)

| # | IDs | Descricao | Horas | Dependencias |
|---|-----|-----------|-------|-------------|
| 1 | DB-001, DB-048 | Standardize auth.role() policies (classification_feedback + partners + partner_referrals) | 2 | Nenhuma |
| 2 | DB-033, DB-037, DB-049 | Retention pg_cron jobs (state_transitions 30d, alert_sent_items 180d, health_checks 30d, incidents 90d, mfa_attempts 30d, alert_runs 90d) | 4 | Nenhuma |
| 3 | DB-007 | Otimizar search_state_transitions RLS subquery | 4 | Nenhuma |
| 4 | DB-011 | Integration test para handle_new_user() + CI guard | 4 | Nenhuma |
| 5 | DB-015 | Documentar plan_type duplication + add reconciliation cron | 4 | Nenhuma |
| 6 | DB-002 | Explicit service_role policies health_checks/incidents | 1 | Nenhuma |
| 7 | DB-010 | Ban system cache warmer account | 1 | Nenhuma |
| 8 | DB-040, DB-041 | Drop indices redundantes | 1 | Nenhuma |
| 9 | DB-018, DB-019 | Add CHECK constraints (cache priority, alert_runs status) | 1 | Nenhuma |
| 10 | DB-028 | Add IF NOT EXISTS guards a migracoes nao-idempotentes | 4 | Nenhuma |
| 11 | DB-042 | Composite index para admin inbox conversations | 1 | Nenhuma |
| 12 | DB-045 | Documentar stripe_webhook_events retention | 1 | Nenhuma |
| 13 | DB-021 | Validar billing_period constraint vs dados legados | 1 | Nenhuma |
| 14 | DB-031 | Prometheus gauge para JSONB table sizes | 2 | Nenhuma |

#### Frontend (~46-52h)

| # | IDs | Descricao | Horas | Dependencias |
|---|-----|-----------|-------|-------------|
| 15 | FE-001 (parcial) | Decompose conta/page.tsx em sub-routes (/perfil, /seguranca, /plano, /dados) | 8-10 | FE-026 (S1) |
| 16 | FE-006 | Adopt SWR para read-only endpoints (Phase 1: /me, /plans, /analytics) | 8 | Nenhuma |
| 17 | FE-033 | Shared Input/Label component | 3-4 | FE-032 (S1) |
| 18 | FE-036 | Extend Tailwind theme com CSS custom properties | 3-4 | Nenhuma |
| 19 | FE-023 | Add text labels a ViabilityBadge (Alta/Media/Baixa) | 2 | Nenhuma |
| 20 | FE-019 | Dynamic imports para Recharts, @dnd-kit, Shepherd.js | 4 | Nenhuma |
| 21 | FE-014 | Memoization em alertas e dashboard | 4 | Nenhuma |
| 22 | FE-031 | Mobile-optimize dashboard charts | 4-6 | Nenhuma |
| 23 | FE-028 | React-hook-form + zod para top 3 forms (signup, conta, onboarding) | 8 | FE-033 |
| 24 | FE-008 | Fix `any` types em 8 arquivos | 2 | Nenhuma |

#### Sistema (~20h)

| # | IDs | Descricao | Horas | Dependencias |
|---|-----|-----------|-------|-------------|
| 25 | SYS-001 | Add deprecation counter metric + plan legacy route sunset | 4 | Nenhuma (remocao efetiva so apos 2 semanas de dados) |
| 26 | SYS-022 | Investigar nonce-based CSP com Stripe.js | 4 | Testar em staging |
| 27 | SYS-006 | TaskRegistry para background tasks em lifespan | 4 | Nenhuma |
| 28 | SYS-010 | Bounded caches com TTL (auth, LLM arbiter) | 3 | Nenhuma |
| 29 | SYS-018 | Auth token cache compartilhado (Redis) | 4 | Nenhuma |

### Backlog (Mes 2+): Medium/Low

**Estimativa: ~230-290h (incluindo ~25h testes)**

#### Database (~47h)
DB-005/006/008 (documentar decisoes aceitas, 2h), DB-009 (otimizar partner RLS, 2h), DB-014 (deprecar stripe_price_id legado, 2h), DB-016 (documentar transicoes de status, 4h), DB-017 (NOT NULL em created_at, 2h), DB-020 (naming convention, 1h), DB-022 (phone validation, 1h), DB-023 (cache UNIQUE review, 2h), DB-024 (updated_at plan_billing_periods, 1h), DB-026 (doc naming convention, 1h), DB-027 (down-migration strategy, 8h), DB-029 (Stripe IDs env-driven, 2h), DB-034 (otimizar cleanup trigger, 2h), DB-035 (rewrite conversations query, 2h), DB-036 (planejar partitioning, 8h), DB-044 (doc pg_cron manual setup, 4h), DB-046 (policy "no dashboard changes", 1h), DB-050 (FK search_state_transitions, 4h).

#### Frontend (~130-160h)
FE-001 restante (alertas, dashboard decomposition, 12-18h), FE-004 (reduzir CSR em 3-5 paginas, 12-16h), FE-005 (enforce component directory + eslint restriction, 4h), FE-007 Phase 2 (SWR mutations, 8h), FE-010 (blog programmatic links, 8h), FE-018 (next/image em landing/blog, 8h), FE-020 (lazy-load fonts, 2h), FE-024 (keyboard shortcut help overlay, 2h), FE-025 (navigation component tests, 8h), FE-027 (PWA investigation, 8h), FE-030 (Suspense boundaries, 8h), FE-003 (i18n framework, 40h -- apenas se expansao internacional), FE-035 (useSearch hook isolation tests, 8-12h).

#### Sistema (~53-83h)
SYS-002 (decompose search_pipeline, 24h), SYS-003 (Redis Streams progress tracker, 16h), SYS-004 (unify PNCP HTTP clients, 24h), SYS-005 (decompose main.py, 12h), SYS-007 (audit dead code, 2h), SYS-008 (createProxyRoute utility, 12h), SYS-011 (unified error schema, 8h), SYS-012 (split config.py, 6h), SYS-014 (move test files, 1h), SYS-019 (CDN, 8h), SYS-020 (connection pool sizing, 4h), SYS-023 (per-user tokens, 16h), SYS-025/026 (temp files + rate limiter, 4h), SYS-028/029 (dep upgrades, 8h), SYS-030 (remove redis_client shim, 1h), SYS-032/033 (integration tests + staging, 24h), SYS-036 (API docs, 8h), SYS-037 (.env validation, 2h), SYS-038 (runbook, 8h), CROSS-003 (feature flags UI, 16h), CROSS-006 (staging environment, 16h).

---

## 6. Riscos e Mitigacoes

| # | Risco | Areas | Severidade | Mitigacao |
|---|-------|-------|------------|-----------|
| R-01 | **CROSS-001 migration consolidation breaks production DB** -- Bridge migration pode re-aplicar DDL se `IF NOT EXISTS` guards faltarem em alguma statement | DB + SYS + Prod | CRITICAL | Verificar cada objeto via `pg_tables`, `pg_proc`, `pg_indexes` ANTES de criar bridge migration. Nunca mover arquivos -- criar bridge que wraps content. |
| R-02 | **SYS-023 service role compound exposure** -- Service role key bypass RLS + qualquer vuln backend (SSRF, injection) expoe todos os dados de todos usuarios | DB + SYS + Sec | HIGH | Resolver como epic de seguranca coordenado. Per-user tokens para ops user-scoped; service role restrito a admin ops. |
| R-03 | **FE-001 + FE-006 decomposition cascade** -- Splitting 4 paginas + estado global muda rendering model de toda pagina autenticada simultaneamente | Frontend + E2E | HIGH | Sequencia obrigatoria: FE-026 (quarantine) -> FE-006 (state) -> FE-001 (pages, uma por vez comecando por conta). Nunca em paralelo. |
| R-04 | **SYS-001 legacy route removal breaks unknown consumers** -- 33 statements montam ~61 routes; remocao assume nenhum consumidor externo usa paths legados | Backend + External | MEDIUM | Add deprecation counter metric (`smartlic_legacy_route_hits_total`). Monitorar 2+ semanas. Remover apenas rotas com zero hits. |
| R-05 | **SYS-003 + SYS-016 horizontal scaling blocked** -- In-memory progress tracker previne multiplas instancias Railway; 1GB limita scaling vertical | SYS + Infra | HIGH | Resolver SYS-003 (Redis Streams) antes de scaling horizontal. SYS-016 (memory optimization) e alternativa vertical com ceiling menor. |
| R-06 | **CROSS-002 API contract drift during frontend refactoring** -- FE-007 toca 30+ arquivos sem safety net; diff ativo no git status demonstra drift ja em curso | Frontend + Backend | MEDIUM | Implementar CROSS-002 (API contract CI) ANTES de iniciar FE-007 refactoring. |
| R-07 | **SYS-022 CSP tightening breaks Stripe checkout** -- Remover unsafe-inline/unsafe-eval pode quebrar Stripe.js checkout flow | Frontend + Billing | MEDIUM | Testar nonce-based CSP com Stripe.js em staging. Stripe tem guidance especifica para CSP que deve ser seguida. |

---

## 7. Dependency Map

```
CROSS-001 (Migracoes/DR) --> DB-025 (Dual dirs) --> DB-030 (backend/ nunca aplicadas)
                         --> DB-027 (Sem down-migrations)
                         --> DB-043 (Sem DR docs)

SYS-001 (Dual routes) --> SYS-005 (main.py 820+ lines)
                       --> SYS-008 (58 proxy routes)
                       --> CROSS-002 (API contract validation)
                       PREREQUISITO: Deprecation metrics (2 semanas de dados)

SYS-002 (God module) --> SYS-006 (Sem task lifecycle)
                     --> SYS-012 (config.py mixed concerns)

SYS-003 (In-memory progress) --> SYS-016 (Railway 1GB + 2 workers)
                              --> SYS-018 (Auth cache per-worker)
                              PREREQUISITO para horizontal scaling

FE-026 (Quarantine 22 tests) --> FE-001 (Monolithic pages)
FE-006 (Global state) --> FE-001 (Monolithic pages)
                       --> FE-007 (Data fetching)
CROSS-002 (API contract CI) --> FE-007 (Data fetching refactor)

FE-001 (Monolithic pages) --> FE-014 (Sem memoization)
                          --> FE-004 (Excessive CSR)
                          --> FE-002 (Sem loading.tsx)

DB-001 (RLS auth.role()) --> DB-038 (Indices tabelas erradas)
                         --> DB-039 (classification_feedback sem indice)
                         --> DB-048 (partners/partner_referrals auth.role())

DB-011 (Trigger churn) --> DB-012 (updated_at inconsistente)
                       --> DB-025 (Dual migration dirs)
```

**Cadeia de resolucao critica (ordem obrigatoria):**

1. **DB-025 + DB-030** -- Consolidar migracoes (prerequisito para tudo DB)
2. **DB-043** -- Documentar DR (seguranca operacional basica)
3. **CROSS-001** -- Idempotencia de migracoes (depende de #1)
4. **DB-013 + DB-038/039 + DB-012** -- RLS + indices + integridade (quick fixes independentes)
5. **CROSS-002** -- API contract CI (safety net antes de refatoracao FE)
6. **FE-026** -- Resolver quarantine (prerequisito para decomposicao FE)
7. **FE-006** -- Estado global (prerequisito para FE-001 e FE-007)
8. **FE-001** -- Decomposicao de paginas (uma por vez, comecando por `conta`)
9. **Deprecation metrics 2+ semanas** -- Dados para SYS-001 (legacy route removal)

---

## 8. Criterios de Sucesso

| Metrica | Baseline Atual | Meta Sprint 1 | Meta Sprint 2 | Meta Backlog |
|---------|---------------|---------------|---------------|--------------|
| Backend tests | 5774 pass / 0 fail | 5774+ / 0 fail | 5800+ / 0 fail | 5900+ / 0 fail |
| Frontend tests | 2681 pass / 0 fail | 2700+ / 0 fail (quarantine resolved) | 2750+ / 0 fail | 2800+ / 0 fail |
| E2E tests | 60 pass | 60 pass | 65+ pass | 75+ pass |
| Quarantined tests | 22 | 0 | 0 | 0 |
| `loading.tsx` coverage | 0/44 pages | 5/44 pages | 10/44 pages | 15+/44 pages |
| Error boundaries | 1 page (/buscar) | 6 pages | 6 pages | all authenticated |
| RLS full table scans | 3+ (classification_feedback, broken indexes) | 0 | 0 | 0 |
| Tables without retention | 6+ | 1 (store fixed) | 0 | 0 |
| Dep vulnerabilities | unknown (not scanned) | scanned, 0 critical | scanned, 0 high+ | scanned, 0 medium+ |
| WCAG AA violations | 4+ (FE-021/022/023/034) | 1 (FE-023 in S2) | 0 | 0 |
| Design system primitives | 0 | 1 (Button) | 4 (Button, Input, Label, Badge) | 6+ |
| DR procedure | undocumented | documented + tested | quarterly test | quarterly test |
| API contract CI | not enforced | enforced (snapshot) | enforced (semantic diff) | enforced |
| Legacy route hits | untracked | tracked (metric) | data analyzed | removed if zero |

---

## 9. Validation Log

| Phase | Agent | Status | Key Changes |
|-------|-------|--------|-------------|
| Phase 1-3 | @architect (Atlas) | COMPLETE | System architecture, DB audit, frontend spec analyzed. 102 debts identified. Unified ID scheme (SYS/DB/FE/CROSS). Priority scoring formula applied. |
| Phase 4 | @data-engineer (Delta) | APPROVED | 38 confirmed, 6 severity-adjusted, 1 removed (DB-003: OAuth uses Fernet AES-256 -- false positive), 4 added (DB-047/048/049/050). DB-001 CRITICAL->HIGH. Roadmap: S1 29h, S2 31h, Backlog 47h. |
| Phase 5 | @ux-design-expert (Uma) | APPROVED | 23 confirmed, 5 severity-adjusted, 1 removed (FE-029: PullToRefresh actively used -- false positive), 6 added (FE-031-036). FE-003 HIGH->LOW, FE-012 MEDIUM->HIGH, FE-021/022/023 LOW->MEDIUM. Roadmap: S1 32-36h, S2 46-52h, Backlog 130-160h. |
| Phase 7 | @qa (Quinn) | APPROVED WITH CONDITIONS | 5 conditions all applied: (1) SYS-009 removed (already fixed -- `await asyncio.sleep(0.3)` at authorization.py:100), (2) FE-026 count corrected 14->22, (3) CROSS-007 added (dep vulnerability scanning), (4) SYS-001 clarified (33 statements, ~61 mounts), (5) Testing effort ~60h added to total. 7 cross-cutting risks documented. 6 gaps identified. |
| Phase 8 | @architect (Atlas) | **FINAL** | All specialist changes incorporated. 3 false positives removed. 8 new debts added. 19 severity adjustments applied. Totals recalculated: 107 unique debts, 720-900h total effort. Document is self-contained. |

### Severity Adjustments Applied (19 total)

| ID | From | To | Justification |
|----|------|----|---------------|
| DB-001 | CRITICAL | HIGH | `auth.role()` funcionalmente correto; performance negligivel <10K rows (@data-engineer) |
| DB-002 | HIGH | MEDIUM | Backend-only by-design; nao e gap (@data-engineer) |
| DB-004 | HIGH | MEDIUM | App-layer rate limiting e padrao correto (@data-engineer) |
| DB-008 | MEDIUM | LOW | Risco aceito; Price IDs usados client-side by design (@data-engineer) |
| DB-011 | HIGH | MEDIUM | Trigger estabilizou; rewrites foram evolutivos (@data-engineer) |
| DB-021 | MEDIUM | LOW | Migracao 029 lida corretamente (@data-engineer) |
| DB-022 | MEDIUM | LOW | App-layer validation mais apropriada (@data-engineer) |
| DB-026 | HIGH | MEDIUM | CLI ordena corretamente; risco e confusao, nao falha (@data-engineer) |
| DB-037 | LOW | MEDIUM | Serve dedup ativo; queries degradam sem cleanup (@data-engineer) |
| FE-003 | HIGH | LOW | 100% BR, pre-revenue, termos sem traducao (@ux-design-expert) |
| FE-004 | HIGH | MEDIUM | Maioria requer interatividade; poucos candidatos SSR (@ux-design-expert) |
| FE-005 | HIGH | MEDIUM | Invisivel ao usuario; slows dev velocity only (@ux-design-expert) |
| FE-010 | MEDIUM | LOW | SEO only; sem UX impact para usuarios autenticados (@ux-design-expert) |
| FE-012 | MEDIUM | HIGH | Crash em 5 paginas = perda total de contexto (@ux-design-expert) |
| FE-015 | MEDIUM | LOW | Zero UX impact; codebase hygiene only (@ux-design-expert) |
| FE-021 | LOW | MEDIUM | WCAG 4.1.3 violation; search e fluxo primario; risco B2G (@ux-design-expert) |
| FE-022 | LOW | MEDIUM | WCAG 2.4.3 violation; keyboard users bloqueados (@ux-design-expert) |
| FE-023 | LOW | MEDIUM | WCAG 1.4.1 violation; ~8% daltonismo masculino (@ux-design-expert) |
| FE-028 | LOW | MEDIUM | Validacao manual = mensagens inconsistentes, gaps (@ux-design-expert) |

---

## Anexos

- `docs/architecture/system-architecture.md` -- Arquitetura completa (Phase 1)
- `supabase/docs/SCHEMA.md` -- Schema de 32 tabelas (Phase 2)
- `supabase/docs/DB-AUDIT.md` -- Audit de database (Phase 2)
- `docs/frontend/frontend-spec.md` -- Especificacao frontend (Phase 3)
- `docs/prd/technical-debt-DRAFT.md` -- DRAFT consolidado (Phase 4)
- `docs/reviews/db-specialist-review.md` -- Revisao @data-engineer (Phase 4)
- `docs/reviews/ux-specialist-review.md` -- Revisao @ux-design-expert (Phase 5)
- `docs/reviews/qa-review.md` -- QA review com 5 condicoes (Phase 7)

---

*Technical Debt Assessment FINAL v1.0*
*SmartLic v0.5 -- 2026-03-07*
*Validated by: @architect (Atlas), @data-engineer (Delta), @ux-design-expert (Uma), @qa (Quinn)*
*Pronto para: Sprint Planning e execucao.*
