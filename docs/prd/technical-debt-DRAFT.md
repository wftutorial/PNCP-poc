# Technical Debt Assessment - DRAFT
## Para Revisao dos Especialistas

**Projeto:** SmartLic v0.5
**Data:** 2026-03-07
**Versao:** DRAFT v3.0
**Autores:** @architect (Atlas), @data-engineer, @ux-design-expert (Uma)
**Fontes:** system-architecture.md v5.0 (Phase 1), DB-AUDIT.md (Phase 2), frontend-spec.md (Phase 3)
**Delta desde v2.0 (2026-03-04):** Phase 1-3 fully re-executed on updated codebase; unified ID scheme; priority scoring formula applied

---

### 1. Executive Summary

| Metrica | Valor |
|---------|-------|
| **Total de debitos consolidados** | 102 |
| **CRITICAL** | 2 |
| **HIGH** | 26 |
| **MEDIUM** | 42 |
| **LOW** | 32 |
| **Areas cobertas** | Sistema (37), Database (39), Frontend (30), Cross-Cutting (5) |
| **Esforco total estimado** | ~660-840 horas |

**Breakdown por Severidade e Area:**

| Area | CRITICAL | HIGH | MEDIUM | LOW | Subtotal | Esforco Est. |
|------|----------|------|--------|-----|----------|--------------|
| Sistema (SYS) | 0 | 8 | 13 | 16 | 37 | ~220-280h |
| Database (DB) | 1 | 10 | 15 | 13 | 39 | ~100-130h |
| Frontend (FE) | 0 | 7 | 12 | 11 | 30 | ~240-310h |
| Cross-Cutting (CROSS) | 1 | 1 | 2 | 2 | 6 | ~50-60h |
| **Total** | **2** | **26** | **42** | **42** | **112** | **~660-840h** |

> Nota: 10 debitos foram identificados como duplicados cross-layer e consolidados, resultando em 102 debitos unicos. Os 6 CROSS-cutting items deduplicam parcialmente de SYS e FE.

---

### 2. Debitos de Sistema (from system-architecture.md)

> PENDENTE: Revisao do @architect (self-review for completeness)

#### 2.1 Arquitetura

| ID | Debito | Severidade | Esforco (h) | Impacto |
|----|--------|------------|-------------|---------|
| SYS-001 | **Rotas montadas em duplicata** (versioned `/v1/` + legacy root) -- 61 `include_router` calls dobram a tabela de rotas. Sunset 2026-06-01 sem plano de migracao. | HIGH | 16 | Performance + manutencao; frontend ja usa versioned paths |
| SYS-002 | **`search_pipeline.py` god module** (800+ linhas) -- Cada stage 50-100+ linhas com try/catch aninhado. Absorveu toda logica de busca apos decomposicao do main.py. | HIGH | 24 | Testabilidade e manutencao severamente impactadas |
| SYS-003 | **Progress tracker in-memory nao escala horizontalmente** -- `_active_trackers` usa asyncio.Queue local. Redis Streams existe como fallback mas in-memory e primario. | HIGH | 16 | Blocker para scale-out; 2 instancias Railway teriam estado dividido |
| SYS-004 | **Dual HTTP client sync+async para PNCP** (1500+ linhas duplicadas) -- PNCPClient (sync/requests) e async httpx duplicam retry, CB, error handling. Sync usado apenas via `asyncio.to_thread()`. | HIGH | 24 | Manutencao duplicada; ~50KB dependencia `requests` para fallback raro |
| SYS-005 | **`main.py` ainda 820+ linhas** apos decomposicao -- Sentry init (100+), exception handlers (80+), middleware config, router registration (60+), lifespan (200+). | HIGH | 12 | Deveria extrair sentry config, exception handlers, lifespan para modulos separados |
| SYS-006 | **10+ background tasks em lifespan sem lifecycle manager** -- Cada task com create/cancel/await manual; 3+ locais para adicionar/remover. | MEDIUM | 8 | Sem abstracao TaskRegistry |
| SYS-007 | **Lead prospecting modules desconectados** -- 5 modulos (`lead_prospecting.py`, `lead_scorer.py`, `lead_deduplicator.py`, `contact_searcher.py`, `cli_acha_leads.py`) aparentemente dead code. | LOW | 2 | Possivelmente dead code de feature exploration |
| SYS-008 | **Frontend proxy route explosion** -- 58 rotas proxy em `frontend/app/api/`, cada backend endpoint requer novo arquivo. Sem `createProxyRoute()` generico. | LOW | 12 | Boilerplate repetitivo; poderia ser ~10 arquivos |

#### 2.2 Qualidade de Codigo

| ID | Debito | Severidade | Esforco (h) | Impacto |
|----|--------|------------|-------------|---------|
| SYS-009 | **`time.sleep(0.3)` em contexto async** (`authorization.py:check_user_roles()`) -- Bloqueia o event loop async. | HIGH | 1 | Deve ser `await asyncio.sleep(0.3)` |
| SYS-010 | **Singletons globais mutaveis sem cleanup** -- `auth.py:_token_cache`, `llm_arbiter.py:_arbiter_cache`, `filter.py:_filter_stats_tracker`. LLM arbiter tem LRU(5000), auth cache nao. | MEDIUM | 6 | Crescem sem limite em processos long-running |
| SYS-011 | **Padroes inconsistentes de error handling** -- Rotas misturam `JSONResponse` direto + `HTTPException`. Sem schema de erro unificado. | MEDIUM | 8 | Experiencia de debug inconsistente |
| SYS-012 | **`config.py` 500+ linhas com concerns misturados** -- PNCP modality codes, retry config, CORS, logging, feature flags, validation juntos. | MEDIUM | 6 | Deveria split em `pncp_config.py`, `cors.py`, `feature_flags.py` |
| SYS-013 | **User-Agent hardcoded "BidIQ"** em pncp_client.py | LOW | 1 | Misleading para provedores de API |
| SYS-014 | **Arquivos de teste na raiz do backend** (fora de `tests/`) | LOW | 1 | 3 arquivos quebram convencao |
| SYS-015 | **`pyproject.toml` referencia "bidiq-uniformes-backend"** | LOW | 0.5 | Branding antigo nao atualizado |

#### 2.3 Escalabilidade

| ID | Debito | Severidade | Esforco (h) | Impacto |
|----|--------|------------|-------------|---------|
| SYS-016 | **Railway 1GB memoria com 2 workers** -- Cada Gunicorn worker mantem caches in-memory proprios. OOM kills historicos. | HIGH | 8 | Estabilidade de producao |
| SYS-017 | **PNCP page size reduzido para 50** (era 500) -- 10x mais API calls. Health canary usa `tamanhoPagina=10` e nao detecta mudanca. | HIGH | 4 | Cobertura de dados e latencia |
| SYS-018 | **Auth token cache in-memory nao compartilhado** entre Gunicorn workers | MEDIUM | 4 | Desperdicio de memoria + chamadas duplicadas Supabase Auth |
| SYS-019 | **Sem CDN para assets estaticos** -- Frontend servido direto do Railway sem edge caching | MEDIUM | 8 | Performance do usuario final |
| SYS-020 | **Singleton Supabase client** -- 2 workers x 50 pool = 100 conexoes potenciais contra Supabase | MEDIUM | 4 | Pode exceder limites de conexao |
| SYS-021 | **Cache key nao inclui todos parametros de filtro** -- Status, modalidades, valor, esferas compartilham mesma entrada | LOW | 4 | Filtros aplicados post-cache; resultados potencialmente imprecisos |

#### 2.4 Seguranca

| ID | Debito | Severidade | Esforco (h) | Impacto |
|----|--------|------------|-------------|---------|
| SYS-022 | **`unsafe-inline`/`unsafe-eval` provavelmente no CSP frontend** -- Requerido por Next.js + Stripe.js | MEDIUM | 8 | Enfraquece Content Security Policy |
| SYS-023 | **Service role key para TODAS operacoes DB backend** -- Bypass total de RLS; qualquer vuln expoe todos os dados | MEDIUM | 16 | Considerar per-user tokens para ops user-scoped |
| SYS-024 | **Sem timeout em webhook handler do Stripe** -- Operacoes DB longas bloqueiam indefinidamente | MEDIUM | 4 | Stripe reenvia webhooks nao-acknowledged |
| SYS-025 | **Excel temp files no proxy frontend** nao limpos em crash | LOW | 2 | Potencial disk exhaustion |
| SYS-026 | **Rate limiter in-memory store** com cleanup infrequente (cada 200 requests) | LOW | 2 | Pode acumular entradas stale sob carga |
| SYS-027 | **`STRIPE_WEBHOOK_SECRET` not-set apenas logado** -- Deveria falhar no startup | LOW | 1 | Validacoes de signature falham silenciosamente |

#### 2.5 Dependencias

| ID | Debito | Severidade | Esforco (h) | Impacto |
|----|--------|------------|-------------|---------|
| SYS-028 | **`cryptography` pinned a 46.0.5** por fork-safety | MEDIUM | 4 | Bloqueado para upgrade sem re-teste Gunicorn |
| SYS-029 | **`requests` lib apenas para sync PNCP fallback** | MEDIUM | 4 | ~50KB dependencia para fallback raro |
| SYS-030 | **`redis_client.py` deprecated mas ainda importavel** -- Shim para `redis_pool` | LOW | 1 | Confusao; confirmar e remover |
| SYS-031 | **`arq` nao instalado localmente** (mocked via `sys.modules` em testes) | LOW | 2 | Fixtures frageis; mascara erros de import |

#### 2.6 Testes e Documentacao

| ID | Debito | Severidade | Esforco (h) | Impacto |
|----|--------|------------|-------------|---------|
| SYS-032 | **Sem testes de integracao contra APIs reais** -- Mudancas de contrato detectadas so em producao | MEDIUM | 16 | Page size 500->50 so detectada em prod |
| SYS-033 | **E2E tests usam credenciais de producao** | LOW | 8 | Sem ambiente de teste isolado |
| SYS-034 | **Sem pre-commit hooks** | LOW | 2 | Devs podem commitar codigo falhando lint |
| SYS-035 | **Backend linting (`ruff`, `mypy`) nao enforced no CI** | LOW | 2 | Type errors podem ser merged |
| SYS-036 | **Sem documentacao de API** alem do OpenAPI auto-gerado (desabilitado em prod) | LOW | 8 | Sem docs publicas para desenvolvedores |
| SYS-037 | **`.env.example` potencialmente stale** -- 25+ flags sem check automatizado | LOW | 2 | Novos devs podem ter setup incompleto |
| SYS-038 | **Sem runbook para resposta a incidentes** -- Conhecimento apenas em CLAUDE.md/MEMORY.md | LOW | 8 | Conhecimento institucional nao formalizado |

---

### 3. Debitos de Database (from DB-AUDIT.md)

> PENDENTE: Revisao do @data-engineer

#### 3.1 RLS e Seguranca

| ID | Debito | Severidade | Esforco (h) | Impacto |
|----|--------|------------|-------------|---------|
| DB-001 | **`classification_feedback` service_role policy usa `auth.role()`** -- Migracao 20260304200000 pulou esta tabela. Per-row evaluation mais lenta; inconsistente com padrao `TO service_role USING (true)`. | CRITICAL | 1 | Performance RLS + inconsistencia de padrao |
| DB-002 | **`health_checks` e `incidents` sem policies user-facing** -- Apenas service_role. Queries de usuarios autenticados retornam vazio. | HIGH | 2 | Se frontend acessar diretamente, falha silenciosa |
| DB-003 | **OAuth tokens armazenados em plaintext no DB** -- Encriptacao AES-256 declarada no app layer mas verificacao necessaria. | HIGH | 8 | Se service_role key comprometida, tokens expostos |
| DB-004 | **`mfa_recovery_codes` sem rate limiting no DB** -- Rate limiting apenas no app code. | HIGH | 4 | Bypass de rate limit possivel via acesso direto |
| DB-005 | **`mfa_recovery_attempts` sem policy SELECT para usuario** | MEDIUM | 1 | Possivelmente intencional; documentar decisao |
| DB-006 | **`trial_email_log` sem policies user-facing** | MEDIUM | 1 | Apenas service_role; documentar |
| DB-007 | **`search_state_transitions` SELECT policy usa subquery** (correlated) | MEDIUM | 4 | Roda para cada row; lento em tabelas grandes |
| DB-008 | **Stripe Price IDs visiveis na tabela `plans`** (RLS public read) | MEDIUM | 2 | Risco baixo; documentar como aceito |
| DB-009 | **`profiles.email` exposto via partner RLS policy** (cross-schema query) | MEDIUM | 2 | Funcional mas otimizavel |
| DB-010 | **Sistema cache warmer account** (`00000000...`) em auth.users com password vazio | LOW | 1 | Garantir que login e impossivel |

#### 3.2 Schema e Integridade

| ID | Debito | Severidade | Esforco (h) | Impacto |
|----|--------|------------|-------------|---------|
| DB-011 | **`handle_new_user()` trigger reescrito 7+ vezes** em migracoes | HIGH | 4 | Churn evolutivo; campos silenciosamente dropped entre versoes |
| DB-012 | **Funcoes `updated_at` inconsistentes** -- `update_updated_at()` vs `set_updated_at()`, funcoes identicas usadas por triggers diferentes | HIGH | 2 | Confusao de manutencao |
| DB-013 | **`partner_referrals.referred_user_id` ON DELETE SET NULL vs NOT NULL** -- DELETE de profile falha com violacao NOT NULL | HIGH | 1 | Operacao DELETE impossivel |
| DB-014 | **`plans.stripe_price_id` coluna legada** coexiste com period-specific columns | MEDIUM | 2 | Confusao e potencial inconsistencia |
| DB-015 | **`profiles.plan_type` vs `user_subscriptions.plan_id` duplicacao** -- Sync apenas no app code; podem divergir | MEDIUM | 4 | Documentar como decisao intencional + add reconciliation cron |
| DB-016 | **`search_sessions.status` sem enforcement de transicoes** no DB | MEDIUM | 4 | Transicoes invalidas possiveis se app code falhar |
| DB-017 | **Missing `NOT NULL` em varias colunas** -- `google_sheets_exports.created_at`, `partners.created_at`, `partner_referrals.signup_at` etc. | LOW | 2 | 5 colunas deveriam ser NOT NULL com default |
| DB-018 | **`search_results_cache.priority` sem CHECK constraint** -- Aceita qualquer texto | LOW | 0.5 | Deveria ser `hot/warm/cold` |
| DB-019 | **`alert_runs.status` sem CHECK constraint** -- Default `pending` nao esta na lista documentada | LOW | 0.5 | Valores nao validados |
| DB-020 | **Naming inconsistente em constraints** -- Mix de `chk_`, descritivos e auto-gerados | LOW | 1 | Cosmetico; padronizar em futuras migracoes |
| DB-021 | **`user_subscriptions.billing_period` constraint pode conflitar** com dados legados | MEDIUM | 1 | Verificar que nenhuma row foi perdida |
| DB-022 | **`profiles.phone_whatsapp` CHECK nao valida estrutura brasileira** -- DDDs invalidos aceitos | MEDIUM | 1 | Validacao apenas de formato, nao conteudo |
| DB-023 | **`search_results_cache` UNIQUE permite sharing cross-user com date range stale** | LOW | 2 | `params_hash_global` pode servir dados antigos |
| DB-024 | **`plan_billing_periods` sem coluna `updated_at`** | LOW | 1 | Impossivel rastrear mudancas de pricing |

#### 3.3 Migracoes

| ID | Debito | Severidade | Esforco (h) | Impacto |
|----|--------|------------|-------------|---------|
| DB-025 | **Dual migration directories** (`supabase/migrations/` + `backend/migrations/`) -- Backend migrations nunca aplicadas via Supabase CLI; funcoes criticas faltando | HIGH | 8 | Recreacao de DB a partir de `supabase/` faltaria tabelas/funcoes |
| DB-026 | **Naming nao-sequencial** -- Mix `001_` a `033_` + timestamps `20260220*`; `027b_` pode nao ordenar | HIGH | 4 | Ambiguidade de ordem de execucao |
| DB-027 | **Sem down-migrations** -- Apenas 1 migration tem rollback comment | MEDIUM | 8 | Rollback em desastre requer SQL manual |
| DB-028 | **Algumas migracoes nao idempotentes** -- `008_add_billing_period.sql` sem `IF NOT EXISTS` | MEDIUM | 4 | Falha em re-run |
| DB-029 | **Hardcoded Stripe Price IDs em migracoes** (015, 029, etc.) | LOW | 2 | Nao funciona para staging/dev |
| DB-030 | **`backend/migrations/` nunca aplicadas via CLI** -- Tabelas/funcoes criticas faltariam em recreacao | HIGH | 4 | Combinado com DB-025 |

#### 3.4 Performance

| ID | Debito | Severidade | Esforco (h) | Impacto |
|----|--------|------------|-------------|---------|
| DB-031 | **`search_results_cache.results` JSONB ate 2MB/row** -- 10 entries/user = 20MB potencial | HIGH | 4 | Tabela cresce rapido com muitos usuarios |
| DB-032 | **`search_results_store.results` sem retention enforcement** -- Rows expiradas ficam 7 dias sem uso | HIGH | 4 | Acumulo significativo de dead data |
| DB-033 | **`search_state_transitions` cresce sem limites** -- 5-10 registros por busca; sem pg_cron cleanup | MEDIUM | 2 | Crescimento proporcional a total de buscas |
| DB-034 | **`cleanup_search_cache_per_user()` trigger em cada INSERT** | MEDIUM | 2 | Overhead de eviction em cada cache write |
| DB-035 | **`get_conversations_with_unread_count()` usa correlated subquery** | MEDIUM | 2 | COUNT subquery por conversa |
| DB-036 | **Sem table partitioning** para append-heavy tables | LOW | 8 | Nao necessario no POC; planejar para scale |
| DB-037 | **`alert_sent_items` sem retention cleanup** | LOW | 1 | Acumula indefinidamente |

#### 3.5 Indices

| ID | Debito | Severidade | Esforco (h) | Impacto |
|----|--------|------------|-------------|---------|
| DB-038 | **Migracao `20260307100000` referencia tabelas inexistentes** (`searches`, `pipeline`, `feedback`) -- Indices RLS nunca criados | HIGH | 2 | Full table scan em RLS policies |
| DB-039 | **`classification_feedback` sem indice user_id** -- Nome incorreto na migracao | HIGH | 1 | Full table scan em RLS |
| DB-040 | **Indice redundante em `alert_preferences`** (plain + UNIQUE no mesmo user_id) | LOW | 0.5 | Write overhead desnecessario |
| DB-041 | **Indice parcialmente redundante em `trial_email_log`** | LOW | 0.5 | Composite unique cobre leading column |
| DB-042 | **Composite index faltando para admin inbox** em `conversations` | LOW | 1 | `(status, last_message_at DESC)` seria mais eficiente |

#### 3.6 Backup e Recovery

| ID | Debito | Severidade | Esforco (h) | Impacto |
|----|--------|------------|-------------|---------|
| DB-043 | **Sem procedimento documentado de disaster recovery** -- 76 migracoes sem guia | HIGH | 16 | Nao ha como recriar DB de forma confiavel |
| DB-044 | **pg_cron jobs nao em migracoes** (requerem superuser) | MEDIUM | 4 | Fresh project precisa habilitar manualmente |
| DB-045 | **`stripe_webhook_events` idempotency depende da tabela** | MEDIUM | 2 | Perda = processamento duplicado |
| DB-046 | **Sem audit trail DB-level para schema changes** | LOW | 4 | ALTER via Dashboard nao capturado em git |

---

### 4. Debitos de Frontend/UX (from frontend-spec.md)

> PENDENTE: Revisao do @ux-expert

#### 4.1 Arquitetura e Estrutura

| ID | Debito | Severidade | Esforco (h) | Impacto |
|----|--------|------------|-------------|---------|
| FE-001 | **Paginas monoliticas** -- 4 pages > 1000 linhas: `conta` (1420), `alertas` (1068), `buscar` (1057), `dashboard` (1037). Re-renders desnecessarios. | HIGH | 24 | Performance + manutencao |
| FE-002 | **Zero `loading.tsx` streaming** em 44 paginas -- Toda transicao de rota mostra blank ate JS hidratar | HIGH | 16 | UX e perceived performance |
| FE-003 | **Sem framework i18n** -- Strings hardcoded PT em 100+ arquivos | HIGH | 40 | Localizacao futura requer tocar cada arquivo |
| FE-004 | **23 de 44 paginas `"use client"` excessivamente** -- Muitas poderiam ser parcialmente server components | HIGH | 24 | Bundle JS inflado; TTI elevado |
| FE-005 | **3 diretorios de componentes sem regra clara** -- `components/`, `app/components/`, `app/buscar/components/` com sobreposicao | HIGH | 8 | Confusao de dev; EmptyState duplicado |
| FE-006 | **Sem gerenciamento de estado global** -- Auth+plan+quota+search+pipeline via prop drilling e context | HIGH | 16 | Nao escala para features futuras |
| FE-007 | **Data fetching inconsistente** -- 5 hooks SWR, maioria raw `fetch()`, alguns `fetchWithAuth()` | HIGH | 12 | Sem padrao unificado; error handling inconsistente |

#### 4.2 Qualidade de Codigo

| ID | Debito | Severidade | Esforco (h) | Impacto |
|----|--------|------------|-------------|---------|
| FE-008 | **`any` types em 5 arquivos de producao** | MEDIUM | 2 | Type safety comprometida |
| FE-009 | **Console statements em producao** (buscar, auth/callback, AuthProvider) | MEDIUM | 1 | Ruido em logs de producao |
| FE-010 | **28+ TODO/FIXME em blog content** -- Links programaticos nao implementados | MEDIUM | 8 | SEO linking incompleto |
| FE-011 | **EmptyState duplicado em 2 locais** | MEDIUM | 1 | Confusao sobre canonico |
| FE-012 | **Error boundary apenas em `/buscar`** -- 5+ paginas sem boundaries sub-page | MEDIUM | 6 | Dashboard, pipeline, historico, mensagens desprotegidos |
| FE-013 | **SearchErrorBoundary usa vermelho hardcoded** -- Viola guideline "nunca vermelho" | MEDIUM | 1 | Inconsistente com error-messages.ts |
| FE-014 | **Sem memoization em paginas grandes** -- `alertas` tem apenas 2 useMemo em 1068 linhas | MEDIUM | 4 | Re-renders de UI complexa |
| FE-015 | **Arquivo `nul` no diretorio app** -- Artefato Windows | MEDIUM | 0.5 | Lixo no codebase |

#### 4.3 Styling e Design System

| ID | Debito | Severidade | Esforco (h) | Impacto |
|----|--------|------------|-------------|---------|
| FE-016 | **Mix de CSS variables e raw Tailwind** (~10 arquivos) -- `bg-[var(--surface-1)]` vs `bg-red-50` | MEDIUM | 4 | Inconsistencia visual |
| FE-017 | **`global-error.tsx` cores brand erradas** -- `#2563eb`/`#1e3a5f` vs tokens `#116dff`/`#0a1e3f` | MEDIUM | 0.5 | Tailwind defaults ao inves de SmartLic tokens |

#### 4.4 Performance

| ID | Debito | Severidade | Esforco (h) | Impacto |
|----|--------|------------|-------------|---------|
| FE-018 | **Sem uso de `next/image`** (apenas 4 arquivos) -- Sem otimizacao, lazy loading ou responsive sizing | MEDIUM | 8 | Core Web Vitals (LCP) |
| FE-019 | **Sem code splitting** para Recharts (~50KB), @dnd-kit (~15KB), Shepherd.js (~25KB) | MEDIUM | 4 | Bundle size elevado |
| FE-020 | **3 Google Fonts carregadas globalmente** -- DM Sans, Fahkwang, DM Mono em todas paginas | MEDIUM | 2 | Fahkwang e DM Mono usadas em poucas paginas |

#### 4.5 Acessibilidade

| ID | Debito | Severidade | Esforco (h) | Impacto |
|----|--------|------------|-------------|---------|
| FE-021 | **Sem `aria-live` para resultados de busca** | LOW | 2 | Mudancas nao anunciadas a screen readers |
| FE-022 | **Sem focus trapping em modais** (Dialog, DeepAnalysis, Upgrade, Cancel) | LOW | 4 | Tab key alcanca elementos atras do modal |
| FE-023 | **Indicadores de viabilidade apenas por cor** | LOW | 2 | Sem indicador secundario para daltonicos |
| FE-024 | **Sem documentacao de atalhos de teclado** | LOW | 2 | `useKeyboardShortcuts` sem help visivel |

#### 4.6 Testes e Features Faltantes

| ID | Debito | Severidade | Esforco (h) | Impacto |
|----|--------|------------|-------------|---------|
| FE-025 | **Sem testes para navegacao** -- NavigationShell, Sidebar, BottomNav, MobileDrawer sem nenhum teste | LOW | 8 | Componentes renderizados em toda pagina autenticada |
| FE-026 | **14 testes em quarentena** -- AuthProvider, ContaPage, LicitacaoCard etc. | LOW | 8 | Componentes importantes com testes bypassados |
| FE-027 | **Sem PWA/offline support** -- useServiceWorker hook existe mas unclear se registrado | LOW | 8 | Sem manifest.json; capacidade offline ausente |
| FE-028 | **Sem validacao estruturada de formularios** -- Sem react-hook-form/zod (FE-M03 pendente) | LOW | 16 | Validacao manual em multiplos forms |
| FE-029 | **`react-simple-pull-to-refresh` instalado mas nao usado** | LOW | 0.5 | Dependencia morta |
| FE-030 | **Sem `<Suspense>` boundaries** em nenhuma pagina | LOW | 8 | Sem streaming de secoes data-dependent |

---

### 5. Debitos Cross-Cutting

Debitos que impactam multiplas camadas simultaneamente.

| ID | Debito | Areas | Severidade | Esforco (h) | Impacto |
|----|--------|-------|------------|-------------|---------|
| CROSS-001 | **Migracoes DB nao-idempotentes + dual directories + sem DR docs** -- Impossivel recriar DB de forma confiavel. Combina DB-025, DB-027, DB-028, DB-043. | DB + SYS | CRITICAL | 24 | Risco operacional: sem rollback, sem recreacao, funcoes criticas potencialmente faltando |
| CROSS-002 | **Sem validacao de contrato API no CI** -- Frontend TypeScript types podem divergir do backend OpenAPI schema. Apenas snapshot diff existe. | SYS + FE | HIGH | 8 | Breakage silencioso entre camadas |
| CROSS-003 | **Feature flags sem UI de runtime** -- 25+ flags em env vars. Requer restart de container. | SYS + FE | MEDIUM | 16 | Sem rollback rapido de features |
| CROSS-004 | **Naming inconsistente entre camadas** -- Backend "BidIQ" em User-Agent/pyproject; Frontend "SmartLic" | SYS + FE | MEDIUM | 2 | Confusao de branding |
| CROSS-005 | **Test pollution patterns** -- `sys.modules["arq"]` mock, Supabase CB singleton leak, `importlib.reload()` state corruption entre testes | SYS + DB | LOW | 4 | Falhas intermitentes em CI |
| CROSS-006 | **Sem ambiente de staging** -- E2E usa producao; sem testes de integracao contra APIs reais | SYS + FE | LOW | 16 | Mudancas de contrato so detectadas em prod |

---

### 6. Dependency Map

```
CROSS-001 (Migracoes/DR) ──> DB-025 (Dual dirs) ──> DB-030 (backend/ nunca aplicadas)
                         ──> DB-027 (Sem down-migrations)
                         ──> DB-043 (Sem DR docs)

SYS-001 (Dual routes) ──> SYS-005 (main.py 820+ lines)
                       ──> SYS-008 (58 proxy routes)
                       ──> CROSS-002 (API contract validation)

SYS-002 (God module) ──> SYS-006 (Sem task lifecycle)
                     ──> SYS-012 (config.py mixed concerns)

SYS-003 (In-memory progress) ──> SYS-016 (Railway 1GB + 2 workers)
                              ──> SYS-018 (Auth cache per-worker)

FE-001 (Monolithic pages) ──> FE-014 (Sem memoization)
                          ──> FE-004 (Excessive CSR)
                          ──> FE-002 (Sem loading.tsx)

FE-007 (Inconsistent fetching) ──> CROSS-002 (API contract validation)
                               ──> FE-006 (Sem global state)

DB-001 (RLS auth.role()) ──> DB-038 (Indices tabelas erradas)
                         ──> DB-039 (classification_feedback sem indice)

DB-003 (OAuth plaintext) ──> DB-004 (MFA sem rate limiting DB)
                         ──> SYS-023 (Service role key bypass)

DB-011 (Trigger churn) ──> DB-012 (updated_at inconsistente)
                       ──> DB-025 (Dual migration dirs)
```

**Cadeia de dependencias criticas (resolver nesta ordem):**

1. **DB-025 + DB-030** -- Consolidar migracoes (prerequisito para tudo DB)
2. **DB-043** -- Documentar DR (seguranca operacional basica)
3. **CROSS-001** -- Idempotencia de migracoes (depende de DB-025)
4. **DB-001 + DB-038 + DB-039** -- RLS + indices (quick fixes independentes)
5. **DB-013** -- SET NULL vs NOT NULL (fix trivial, blocker para DELETE)
6. **SYS-009** -- time.sleep async (fix trivial, alto impacto)
7. **SYS-001** -- Sunset legacy routes (prerequisito para SYS-005)
8. **FE-001 + FE-006** -- Decomposicao + estado global (prerequisito para FE-007)

---

### 7. Matriz Preliminar de Priorizacao

**Formula:** `Priority Score = (Severity x 3 + Impact x 2) / Effort`

Onde:
- Severity: CRITICAL=4, HIGH=3, MEDIUM=2, LOW=1
- Impact: 1=cosmetic, 2=degraded experience, 3=functionality affected, 4=data loss/security/outage risk
- Effort: 1=<2h, 2=2-8h, 3=8-24h, 4=>24h

| Rank | ID | Debito | Area | Sev | Impact | Effort | Score |
|------|----|--------|------|-----|--------|--------|-------|
| 1 | DB-001 | RLS `auth.role()` em classification_feedback | DB | 4 | 3 | 1 | **18.0** |
| 2 | SYS-009 | `time.sleep(0.3)` em async context | SYS | 3 | 4 | 1 | **17.0** |
| 3 | DB-013 | ON DELETE SET NULL vs NOT NULL | DB | 3 | 4 | 1 | **17.0** |
| 4 | DB-038 | Migracao referencia tabelas inexistentes | DB | 3 | 4 | 1 | **17.0** |
| 5 | DB-039 | classification_feedback sem indice user_id | DB | 3 | 3 | 1 | **15.0** |
| 6 | SYS-017 | PNCP page size 50 (health canary blind) | SYS | 3 | 3 | 1 | **15.0** |
| 7 | DB-012 | Funcoes updated_at inconsistentes | DB | 3 | 2 | 1 | **13.0** |
| 8 | CROSS-001 | Migracoes/DR critico | CROSS | 4 | 4 | 3 | **12.0** |
| 9 | DB-002 | health_checks/incidents sem user policies | DB | 3 | 3 | 1 | **15.0** |
| 10 | DB-003 | OAuth tokens plaintext | DB | 3 | 4 | 2 | **12.5** |
| 11 | FE-017 | global-error.tsx cores erradas | FE | 2 | 2 | 1 | **10.0** |
| 12 | FE-013 | SearchErrorBoundary usa vermelho | FE | 2 | 2 | 1 | **10.0** |
| 13 | SYS-027 | STRIPE_WEBHOOK_SECRET fail-at-startup | SYS | 1 | 3 | 1 | **9.0** |
| 14 | DB-004 | MFA sem rate limiting DB | DB | 3 | 3 | 2 | **10.0** |
| 15 | DB-031 | JSONB cache ate 2MB/row | DB | 3 | 3 | 2 | **10.0** |
| 16 | SYS-016 | Railway 1GB + 2 workers OOM | SYS | 3 | 4 | 2 | **12.5** |
| 17 | CROSS-002 | API contract validation CI | CROSS | 3 | 3 | 2 | **10.0** |
| 18 | FE-015 | Arquivo `nul` no app dir | FE | 2 | 1 | 1 | **8.0** |
| 19 | FE-009 | Console statements em producao | FE | 2 | 1 | 1 | **8.0** |
| 20 | FE-011 | EmptyState duplicado | FE | 2 | 1 | 1 | **8.0** |

---

### 8. Quick Wins (High Impact, Low Effort)

Top 10 items que podem ser corrigidos rapidamente com alto retorno.

| # | ID | Debito | Esforco | Acao |
|---|----|--------|---------|------|
| 1 | **SYS-009** | `time.sleep(0.3)` em async context | 1h | Trocar por `await asyncio.sleep(0.3)` em `authorization.py` |
| 2 | **DB-001** | RLS `auth.role()` em classification_feedback | 1h | DROP + CREATE policy com `TO service_role USING (true) WITH CHECK (true)` |
| 3 | **DB-013** | ON DELETE SET NULL vs NOT NULL | 1h | ALTER COLUMN DROP NOT NULL ou mudar para CASCADE |
| 4 | **DB-038+039** | Indices RLS com nomes errados + indice faltando | 2h | Re-criar com nomes corretos + CREATE INDEX classification_feedback(user_id) |
| 5 | **DB-012** | Duas funcoes updated_at identicas | 2h | Consolidar triggers para usar apenas `set_updated_at()`; DROP `update_updated_at()` |
| 6 | **FE-015** | Arquivo `nul` no app dir | 0.5h | `rm frontend/app/nul` |
| 7 | **FE-017** | global-error.tsx cores brand erradas | 0.5h | Trocar `#2563eb`/`#1e3a5f` por `#116dff`/`#0a1e3f` |
| 8 | **FE-009** | Console statements em producao | 1h | Remover console.log/warn de buscar, auth/callback, AuthProvider |
| 9 | **FE-029** | Dependencia morta react-simple-pull-to-refresh | 0.5h | `npm uninstall react-simple-pull-to-refresh` |
| 10 | **SYS-027** | STRIPE_WEBHOOK_SECRET deveria falhar no startup | 1h | Adicionar check no lifespan; raise se None |

**Esforco total Quick Wins: ~10-11 horas**

**Impacto combinado:** Fix de event loop blocking, seguranca RLS, integridade de dados (DELETE impossivel), performance de query, brand consistency, e hygiene geral do codebase.

---

### 9. Perguntas para Especialistas

#### Para @data-engineer:

1. **Estrategia de consolidacao de migracoes (DB-025/030):** Recomendamos mover `backend/migrations/` para `supabase/migrations/` com timestamps. Qual e a melhor abordagem para garantir que funcoes/tabelas de `backend/migrations/` (especialmente `classification_feedback` e `check_and_increment_quota`) ja existem em producao? Voce sugere uma migracao "bridge" com `IF NOT EXISTS` guards?

2. **Validacao de indices em producao (DB-038/039):** A migracao `20260307100000` referenciou tabelas inexistentes (`searches`, `pipeline`, `feedback`). Como validar quais indices realmente existem? Devemos rodar `SELECT indexname FROM pg_indexes WHERE tablename IN ('classification_feedback', 'search_sessions', 'pipeline_items')` em producao?

3. **Retention policies (DB-033/037):** Sugerimos pg_cron cleanup de 30 dias para `search_state_transitions` e `alert_sent_items`. Existe use case de analytics/auditoria que precise de dados mais antigos? Qual retention period voce recomenda para cada tabela?

4. **OAuth token encryption (DB-003):** O documento menciona "AES-256 encrypted" no app layer. Voce pode confirmar se a encriptacao esta implementada em `oauth.py` ou se tokens estao plaintext? Se plaintext, qual prioridade de correcao?

5. **JSONB size monitoring (DB-031/032):** Com `search_results_cache` permitindo 2MB/row e `search_results_store` com retention ineficaz, qual e o tamanho atual dessas tabelas em producao? Devemos adicionar monitoring Prometheus via `pg_total_relation_size()`?

6. **Disaster Recovery (DB-043):** Voce tem acesso ao Supabase PITR? Qual e o RPO/RTO atual? A recreacao do DB a partir de migracoes ja foi testada?

7. **`handle_new_user()` trigger (DB-011):** Este trigger foi reescrito 7+ vezes. Vale migrar para application layer (backend Python) para reduzir risco de regressao silenciosa?

#### Para @ux-design-expert:

1. **Decomposicao de paginas (FE-001):** `conta/page.tsx` tem 1420 linhas. Recomendacao: extrair ProfileSection, PlanSection, DataSection. Voce tem wireframes ou design specs que definam os boundaries visuais? Ou inferimos da UI atual?

2. **loading.tsx streaming (FE-002):** Nenhuma pagina tem `loading.tsx`. Para percepcao de performance, quais paginas priorizar? Sugestao: `/buscar` (critica), `/dashboard` (data-heavy), `/pipeline` (DnD).

3. **Consolidacao de componentes (FE-005):** Existem 3 diretorios com sobreposicao. Regra sugerida: `components/` (shared/reusable), `app/components/` (app-wide providers/layouts), `app/buscar/components/` (feature-specific). O `EmptyState` duplicado (FE-011) e sintoma. Concorda?

4. **Design tokens vs Tailwind raw (FE-016):** ~10 arquivos misturam CSS variables com raw Tailwind. Migrar tudo para CSS variables (design system puro) ou criar Tailwind theme que mapeie tokens? Qual reduz mais risco de inconsistencia?

5. **Acessibilidade (FE-021/022/023):** Focus trapping em modais, aria-live para resultados, indicadores nao-cor para viabilidade -- qual priorizar para WCAG AA? Algum e blocker para lancamento formal?

6. **SWR vs fetch (FE-007):** Apenas 5 hooks usam SWR. Vale migrar tudo para SWR (ou TanStack Query), ou manter approach misto e documentar? Dado os SSE patterns customizados, qual se integra melhor?

#### Para @qa:

1. **14 testes em quarentena (FE-026):** Quais sao mais criticos para reativar? AuthProvider e ContaPage parecem alto risco. Voce sabe por que entraram em quarentena?

2. **Coverage gaps em navegacao (FE-025):** NavigationShell, Sidebar, BottomNav, MobileDrawer sem nenhum teste mas renderizados em toda pagina autenticada. Risco de regressao? Priorizar testes de renderizacao basica ou interacao completa?

3. **Test pollution (CROSS-005):** O mock de `arq` via `sys.modules` causa falhas intermitentes. Recomendar instalar `arq` como dev dependency ou criar stub package mais robusto?

4. **API contract validation (CROSS-002):** O snapshot diff `openapi_schema.diff.json` nao esta enforced no CI. Adicionar step que falha se diff mudar? Ou usar `openapi-diff` para validacao mais sofisticada?

5. **Backend linting (SYS-035):** `ruff` e `mypy` configurados mas nao enforced. Qual esforco para fazer codebase passar em ambos? Adicionar como warning (nao-blocking) primeiro?

6. **E2E em producao (SYS-033/CROSS-006):** Playwright roda contra producao. Qual plano para staging isolado? Isso bloqueia expansao de E2E?

---

*Fim do Technical Debt Assessment DRAFT v3.0*
*Proximo passo: Revisao pelos especialistas (@data-engineer, @ux-design-expert, @qa) para validar severidades, esforcos e prioridades.*
*Apos revisao: gerar versao FINAL com sprint planning, epics de remediacao e OKRs de qualidade.*
