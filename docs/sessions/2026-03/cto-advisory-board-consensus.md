# Consenso do Conselho de CTOs -- Auditoria de Promessas SmartLic

**Data:** 2026-03-01
**Metodologia:** Confronto adversarial entre 8 clusters (53 CTOs). Analise baseada em evidencias de codebase, nao em suposicoes.
**Escopo:** Copy user-facing vs. capacidade real do sistema. Identificacao de fragilidades e stories de remediacao.

---

## Veredicto

O SmartLic possui um sistema de governanca de copy (BANNED_PHRASES) que e superior a maioria dos competidores no mercado B2G brasileiro. Porem, **6 promessas quantificadas nao possuem infraestrutura de medicao** e **3 promessas contradizem limitacoes tecnicas documentadas**. O risco principal nao e fraude -- e erosao de confianca quando um usuario sofisticado (consultoria de licitacao) perceber a distancia entre promessa e entrega. A correcao exige tanto ajustes de copy quanto investimento em infraestrutura de medicao e resiliencia.

---

## Promessas em Risco (por impacto de negocio)

### RISCO 1 -- "+98% de cobertura das oportunidades publicas do Brasil"
**Impacto de negocio:** CRITICO. Esta e a promessa mais visivel (landing page, DataSourcesSection, valueProps.ts). Um unico cliente que use Effecti (1.400+ portais) e compare com SmartLic (3 fontes) destruira credibilidade instantaneamente.

**Cadeia de fragilidade:**
- **Copy:** `DataSourcesSection.tsx:31` -- "+98% das oportunidades publicas do Brasil"
- **Realidade backend:** 3 fontes (PNCP, PCP v2, ComprasGov v3). PNCP e a fonte primaria federal mas nao cobre portais municipais proprietarios. PCP v2 cobre ~600 portais. ComprasGov cobre licitacoes federais.
- **Gap:** Nao existe infraestrutura para medir cobertura real. O "+98%" nao tem fonte de dados. Portais municipais de grande volume (BLL, BBMNET, Licitanet) nao estao integrados.
- **Impacto no usuario:** Cliente descobre licitacao em portal municipal que SmartLic nao mostrou. Perde confianca na promessa central.

### RISCO 2 -- "87% dos editais descartados"
**Impacto de negocio:** ALTO. Aparece em 6+ locais (HeroSection, StatsSection, comparisons.ts, valueProps.ts). E o principal badge de confianca visual.

**Cadeia de fragilidade:**
- **Copy:** `valueProps.ts:39` -- "87% descartados", `StatsSection.tsx:78` -- aria-label="87% de editais descartados"
- **Realidade backend:** O pipeline de filtragem funciona (2.549 regras em sectors_data.yaml), mas NAO EXISTE metrica de discard_rate. Nao ha Prometheus counter, nao ha logging estruturado do ratio filtrados/total, nao ha dashboard.
- **Gap:** O numero "87%" nao tem origem mensuravel. Pode ser 60%, pode ser 95%. Ninguem sabe.
- **Impacto no usuario:** Se o usuario real ve 30% de descarte (setor com poucas licitacoes), a promessa parece falsa.

### RISCO 3 -- "Disponivel 24/7" + "Suporte prioritario 24/7"
**Impacto de negocio:** ALTO. Duas promessas separadas, ambas frageis.

**Cadeia de fragilidade:**
- **Copy (disponibilidade):** `comparisons.ts:104` -- "Disponivel 24/7"
- **Copy (suporte):** `TrustSignals.tsx:139` -- "Suporte prioritario 24/7"
- **Realidade backend:** Historico de CRIT-SIGSEGV (crash loop), CRIT-046 (connection pool exhaustion), CRIT-012 (SSE heartbeat gap). Status page existe (`/status`) mas e reativa, nao proativa.
- **Realidade suporte:** Nao existe infraestrutura de SLA (sem ticket tracking, sem response time measurement). "24/7" implica cobertura humana 24 horas -- impossivel para equipe pre-revenue.
- **Impacto no usuario:** Sistema indisponivel em horario comercial = churn imediato para cliente pagante.

### RISCO 4 -- "Resposta em ate 24 horas uteis"
**Impacto de negocio:** MEDIO-ALTO. Promessa de SLA sem infraestrutura de enforcement.

**Cadeia de fragilidade:**
- **Copy:** `comparisons.ts:89`, `comparisons.ts:192`, `comparisons.ts:312`, `ajuda/page.tsx:232`
- **Realidade:** Sistema de mensagens existe (`/mensagens`), mas nao ha: (a) alerta para mensagem nao respondida, (b) metrica de tempo de resposta, (c) escalacao automatica, (d) notification push.
- **Gap:** Nao ha como garantir nem medir o cumprimento.
- **Impacto no usuario:** Cliente envia mensagem sexta 17h, nao recebe resposta segunda 9h, percebe quebra de SLA.

### RISCO 5 -- "Investimento se paga na primeira licitacao ganha"
**Impacto de negocio:** MEDIO. Promessa de ROI agressiva mas semanticamente ambigua.

**Cadeia de fragilidade:**
- **Copy:** `valueProps.ts:216` -- "Investimento se paga na primeira licitacao ganha"
- **Realidade:** SmartLic ENCONTRA licitacoes, nao ajuda a GANHAR. Nao ha acompanhamento de resultado (win/loss tracking), nao ha correlacao entre uso da plataforma e taxa de vitoria.
- **Gap:** Sem win-tracking, a promessa e inverificavel. ROI calculator usa defaults agressivos (8.5h manual vs 0.05h SmartLic = 170x).
- **Impacto no usuario:** Cliente paga R$397/mes, nao ganha licitacao em 3 meses, questiona o ROI prometido.

### RISCO 6 -- "Nenhuma oportunidade invisivel"
**Impacto de negocio:** MEDIO. Promessa absoluta que qualquer falha refuta.

**Cadeia de fragilidade:**
- **Copy:** `valueProps.ts:100` -- "Nenhuma oportunidade invisivel"
- **Realidade backend:** LLM fallback = REJECT em caso de outage OpenAI (`llm_arbiter.py:789-800`). Zero-match bids com keyword density 0% sao REJEITADOS quando LLM esta indisponivel. Isso cria oportunidades "invisiveis" por design.
- **Gap adicional:** PNCP rate limiting + circuit breaker podem impedir coleta completa de UFs em janelas de alta carga. Timeout chain (Pipeline 110s) pode truncar resultados.
- **Impacto no usuario:** Bid relevante rejeitada por LLM outage ou timeout. Cliente descobre depois que competidor encontrou.

---

## Stories de Remediacao

### STORY-350: Substituir "+98% cobertura" por claim verificavel

**Prioridade:** P0
**Tipo:** fix (copy) + feature (metrica)
**Promessa afetada:** "+98% das oportunidades publicas federais e estaduais"
**Causa raiz:** Claim quantificado sem fonte de dados. 3 fontes vs 1400+ portais de competidores torna a promessa refutavel.

**Criterios de aceite:**
- [ ] AC1: Substituir "+98%" por "Fontes oficiais consolidadas" em `DataSourcesSection.tsx` (linhas 31, 57, 59, 73)
- [ ] AC2: Substituir "+98% cobertura" por "Cobertura nacional" em `valueProps.ts:172`
- [ ] AC3: Criar metrica `smartlic_sources_bids_fetched_total` (labels: source, uf) em `metrics.py` -- permite calcular cobertura real no futuro
- [ ] AC4: Adicionar "+98%" ao array BANNED_PHRASES em `valueProps.ts`
- [ ] AC5: Atualizar testes e2e que verificam "+98%" (`landing-page.spec.ts`, `institutional-pages.spec.ts`)
- [ ] AC6: Criar card no `/status` mostrando "Fontes ativas" com status real de cada fonte
- [ ] AC7: Documentar em `proofPoints` (comparisons.ts) a cobertura real: "3 fontes oficiais federais + portal de compras publicas"

**Arquivos afetados:** `frontend/app/components/landing/DataSourcesSection.tsx`, `frontend/lib/copy/valueProps.ts`, `frontend/lib/copy/comparisons.ts`, `backend/metrics.py`, `frontend/e2e-tests/landing-page.spec.ts`, `frontend/e2e-tests/institutional-pages.spec.ts`
**Estimativa:** M

---

### STORY-351: Instrumentar e validar metrica "87% descartados"

**Prioridade:** P0
**Tipo:** feature (observabilidade) + fix (copy condicional)
**Promessa afetada:** "87% dos editais descartados"
**Causa raiz:** Numero arbitrario exibido como fato. Zero infraestrutura de medicao.

**Criterios de aceite:**
- [ ] AC1: Adicionar Prometheus counter `smartlic_filter_input_total` e `smartlic_filter_output_total` (labels: sector, source) em `filter.py`
- [ ] AC2: Adicionar Prometheus histogram `smartlic_filter_discard_rate` (ratio = 1 - output/input) em `search_pipeline.py` ao final do estagio filter
- [ ] AC3: Criar endpoint `GET /v1/metrics/discard-rate` que retorna a media movel de 30 dias do discard rate por setor
- [ ] AC4: No frontend, substituir "87%" hardcoded por valor dinamico do endpoint (com fallback para "a maioria" se API falhar)
- [ ] AC5: Se discard rate real < 70%, substituir copy por "A maioria dos editais descartados por irrelevancia"
- [ ] AC6: Atualizar `StatsSection.tsx` para renderizar valor dinamico com loading state
- [ ] AC7: Atualizar testes de `StatsSection.test.tsx` para mock do novo endpoint
- [ ] AC8: Adicionar o numero exato ao Grafana dashboard com alerta se discard rate cair abaixo de 70%
- [ ] AC9: Log estruturado: `{"event": "filter_stats", "input": N, "output": M, "discard_rate": X, "sector": "...", "search_id": "..."}`

**Arquivos afetados:** `backend/filter.py`, `backend/filter_stats.py`, `backend/search_pipeline.py`, `backend/metrics.py`, `backend/routes/analytics.py`, `frontend/app/components/landing/StatsSection.tsx`, `frontend/lib/copy/valueProps.ts`, `frontend/__tests__/landing/StatsSection.test.tsx`
**Estimativa:** L

---

### STORY-352: Substituir "24/7" por promessa realista de disponibilidade

**Prioridade:** P0
**Tipo:** fix (copy)
**Promessa afetada:** "Disponivel 24/7" + "Suporte prioritario 24/7"
**Causa raiz:** Promessa de 100% uptime e suporte humano 24h e inverificavel e falsa para startup pre-revenue.

**Criterios de aceite:**
- [ ] AC1: Substituir "Disponivel 24/7" por "Alta disponibilidade com monitoramento continuo" em `comparisons.ts:104`
- [ ] AC2: Substituir "Suporte prioritario 24/7" por "Suporte dedicado para assinantes" em `TrustSignals.tsx:139`
- [ ] AC3: Adicionar "24/7" ao BANNED_PHRASES em `valueProps.ts`
- [ ] AC4: Criar Prometheus gauge `smartlic_uptime_pct_30d` calculado a partir dos health checks existentes
- [ ] AC5: Na pagina `/status`, exibir uptime real dos ultimos 30 dias (ja tem `uptime_pct_30d`)
- [ ] AC6: Atualizar `IMPLEMENTATION-SUMMARY.md` e `README.md` do componente TrustSignals
- [ ] AC7: Atualizar testes e2e que verificam texto "24/7" se existirem

**Arquivos afetados:** `frontend/lib/copy/comparisons.ts`, `frontend/components/subscriptions/TrustSignals.tsx`, `frontend/lib/copy/valueProps.ts`, `frontend/components/subscriptions/IMPLEMENTATION-SUMMARY.md`
**Estimativa:** S

---

### STORY-353: Infraestrutura de SLA para mensagens de suporte

**Prioridade:** P1
**Tipo:** feature
**Promessa afetada:** "Resposta em ate 24 horas uteis"
**Causa raiz:** Promessa de SLA sem medicao, alertas ou enforcement.

**Criterios de aceite:**
- [ ] AC1: Adicionar coluna `first_response_at` na tabela `conversations` (migracao Supabase)
- [ ] AC2: Calcular `response_time_hours` no backend ao registrar reply do admin
- [ ] AC3: Criar cron job `check_unanswered_messages()` em `cron_jobs.py` que executa a cada 4h
- [ ] AC4: Enviar email de alerta ao admin quando mensagem sem resposta completar 20h uteis
- [ ] AC5: Criar Prometheus gauge `smartlic_support_pending_messages` e histogram `smartlic_support_response_time_hours`
- [ ] AC6: Criar endpoint `GET /v1/admin/support-sla` retornando: { avg_response_hours, pending_count, breached_count }
- [ ] AC7: No admin dashboard, exibir card de SLA com metricas de resposta
- [ ] AC8: Definir "horas uteis" como seg-sex 8h-18h BRT (configuravel via env var)
- [ ] AC9: Testes: mock de horarios uteis vs finais de semana

**Arquivos afetados:** `supabase/migrations/`, `backend/routes/messages.py`, `backend/cron_jobs.py`, `backend/metrics.py`, `backend/routes/admin.py`, `frontend/app/admin/page.tsx`
**Estimativa:** L

---

### STORY-354: LLM graceful degradation -- eliminar "oportunidades invisiveis" por outage

**Prioridade:** P0
**Tipo:** fix
**Promessa afetada:** "Nenhuma oportunidade invisivel"
**Causa raiz:** LLM fallback = REJECT (`llm_arbiter.py:792`) significa que durante outage OpenAI, bids com 0% keyword density sao silenciosamente descartadas. O usuario nao sabe que perdeu oportunidades.

**Criterios de aceite:**
- [ ] AC1: Quando LLM falhar, classificar bids zero-match como `PENDING_REVIEW` (novo status) em vez de REJECT
- [ ] AC2: Adicionar campo `pending_review_count` ao response schema (`BuscaResponse`)
- [ ] AC3: No frontend, exibir banner: "X oportunidades aguardam reclassificacao (fontes de IA temporariamente indisponiveis)"
- [ ] AC4: Criar ARQ job `reclassify_pending_bids(search_id)` que re-processa bids pendentes quando LLM voltar
- [ ] AC5: Prometheus counter `smartlic_llm_fallback_pending_total` para medir frequencia de fallback
- [ ] AC6: SSE event `pending_review` para atualizar frontend em tempo real quando reclassificacao completar
- [ ] AC7: Limite de retencao: bids PENDING_REVIEW expiram em 24h (nao poluir resultados indefinidamente)
- [ ] AC8: Feature flag `LLM_FALLBACK_PENDING_ENABLED` (default: true) para rollback seguro
- [ ] AC9: Testes: mock OpenAI down, verificar que bids nao sao perdidas

**Arquivos afetados:** `backend/llm_arbiter.py`, `backend/schemas.py`, `backend/search_pipeline.py`, `backend/job_queue.py`, `backend/progress.py`, `frontend/app/buscar/components/SearchResults.tsx`, `frontend/app/buscar/hooks/useSearch.ts`
**Estimativa:** XL

---

### STORY-355: ROI calculator -- defaults honestos e disclaimers

**Prioridade:** P1
**Tipo:** fix (copy + logica)
**Promessa afetada:** "Investimento se paga na primeira licitacao ganha"
**Causa raiz:** ROI calculator usa 8.5h manual vs 0.05h SmartLic (170x) como default. SmartLic encontra licitacoes mas nao ajuda a ganhar. "Paga na primeira licitacao" implica causalidade.

**Criterios de aceite:**
- [ ] AC1: Adicionar disclaimer ao ROI calculator: "* Valores estimados. SmartLic auxilia na descoberta e priorizacao de oportunidades, nao garante vitoria em licitacoes."
- [ ] AC2: Substituir `timeSavedPerSearch: 8.5` por `timeSavedPerSearch: 4.0` em `roi.ts` (default mais conservador -- manual inclui analise, nao so busca)
- [ ] AC3: Substituir "Investimento se paga na primeira licitacao ganha" por "Economize horas de analise manual desde o primeiro uso" em `valueProps.ts:216`
- [ ] AC4: Renomear `potentialReturn: "500x"` para valor calculado dinamicamente baseado nos inputs reais
- [ ] AC5: Adicionar cenario "pessimista" ao lado do "otimista" na UI do calculator
- [ ] AC6: Adicionar "Investimento se paga na primeira licitacao ganha" ao BANNED_PHRASES
- [ ] AC7: Testes: verificar que disclaimer aparece em todos os cenarios

**Arquivos afetados:** `frontend/lib/copy/roi.ts`, `frontend/lib/copy/valueProps.ts`, `frontend/app/pricing/page.tsx`, `frontend/app/planos/page.tsx`
**Estimativa:** M

---

### STORY-356: Pipeline limit enforcement no backend

**Prioridade:** P1
**Tipo:** fix (seguranca)
**Promessa afetada:** Integridade da restricao trial (afeta confianca no modelo freemium)
**Causa raiz:** Limite de pipeline e aplicado apenas no frontend (`PIPELINE_LIMIT` em `pipeline/page.tsx`). Qualquer chamada direta a API bypassa o limite.

**Criterios de aceite:**
- [ ] AC1: Adicionar validacao em `POST /pipeline` que verifica contagem atual vs limite do plano do usuario
- [ ] AC2: Trial: max 5 items (configuravel via `TRIAL_PAYWALL_MAX_PIPELINE` em config.py -- ja existe)
- [ ] AC3: Retornar HTTP 403 com `error_code: "PIPELINE_LIMIT_EXCEEDED"` e `limit: N` no body
- [ ] AC4: Frontend exibe modal de upgrade ao receber 403 (ja existe modal, ligar ao novo error code)
- [ ] AC5: Paid users: sem limite (ou limite alto configuravel)
- [ ] AC6: Testes: trial user tenta adicionar item #6, recebe 403
- [ ] AC7: Testes: paid user adiciona item sem limite

**Arquivos afetados:** `backend/routes/pipeline.py`, `backend/config.py`, `frontend/app/pipeline/page.tsx`
**Estimativa:** S

---

### STORY-357: Auth token refresh durante busca longa

**Prioridade:** P1
**Tipo:** fix
**Promessa afetada:** "Produtivo desde a primeira sessao" (UX), "Alta disponibilidade"
**Causa raiz:** Buscas podem levar 60-110s. Se token Supabase expira durante a busca (default 1h), o usuario ve "Autenticacao necessaria" sem possibilidade de retry automatico. Sessao perdida.

**Criterios de aceite:**
- [ ] AC1: No proxy `/api/buscar/route.ts`, implementar refresh-and-retry: se backend retorna 401, chamar `supabase.auth.refreshSession()` e reenviar request
- [ ] AC2: Limite de 1 retry por request (evitar loop infinito)
- [ ] AC3: Se refresh falhar, redirecionar para `/login` com query param `?returnTo=/buscar`
- [ ] AC4: No `useSearch.ts`, detectar 401 e mostrar mensagem amigavel: "Sua sessao expirou. Reconectando..." (em vez de erro generico)
- [ ] AC5: Implementar pre-emptive refresh: se token expira em < 5min, refreshar antes de iniciar busca
- [ ] AC6: Testes: mock de token expirado durante busca, verificar refresh automatico

**Arquivos afetados:** `frontend/app/api/buscar/route.ts`, `frontend/app/buscar/hooks/useSearch.ts`, `frontend/lib/supabase-browser.ts`
**Estimativa:** M

---

### STORY-358: "1000+ licitacoes/dia" -- instrumentar e validar claim

**Prioridade:** P2
**Tipo:** feature (observabilidade)
**Promessa afetada:** "1000+ licitacoes/dia" (InstitutionalSidebar)
**Causa raiz:** Numero exibido na sidebar sem fonte de dados. Pode ser verdade (PNCP publica milhares/dia), mas nao e medido.

**Criterios de aceite:**
- [ ] AC1: Criar Prometheus counter `smartlic_bids_processed_total` (labels: source, date) incrementado no pipeline de busca
- [ ] AC2: Criar cron job diario que registra contagem de bids processados nas ultimas 24h
- [ ] AC3: Criar endpoint `GET /v1/metrics/daily-volume` retornando media de bids/dia dos ultimos 30 dias
- [ ] AC4: No frontend, substituir "1000+" hardcoded por valor dinamico (com fallback "1000+" se API falhar)
- [ ] AC5: Se volume real < 500/dia, ajustar copy para "centenas de licitacoes/dia"
- [ ] AC6: Testes do endpoint e do cron job

**Arquivos afetados:** `backend/metrics.py`, `backend/cron_jobs.py`, `backend/routes/analytics.py`, `frontend/app/components/InstitutionalSidebar.tsx`
**Estimativa:** M

---

### STORY-359: Transparencia de degradacao SSE para o usuario

**Prioridade:** P2
**Tipo:** fix (UX)
**Promessa afetada:** Confianca geral do usuario no sistema
**Causa raiz:** Quando SSE falha, frontend cai silenciosamente para progress simulado baseado em tempo (`EnhancedLoadingProgress.tsx:134`). Usuario ve barra de progresso avancando mas nao sabe que e simulacao -- se busca falhar, a barra "mentiu".

**Criterios de aceite:**
- [ ] AC1: Quando SSE cai para fallback simulado, exibir indicador discreto: icone de info + tooltip "Progresso estimado (conexao em tempo real indisponivel)"
- [ ] AC2: Se SSE reconectar com sucesso, remover indicador e mostrar progresso real
- [ ] AC3: Nao bloquear UX -- indicador e informativo, nao alarme
- [ ] AC4: Prometheus counter `smartlic_sse_fallback_simulated_total` no frontend (via telemetry endpoint)
- [ ] AC5: Testes: SSE fail -> indicador aparece -> SSE reconnect -> indicador some

**Arquivos afetados:** `frontend/components/EnhancedLoadingProgress.tsx`, `frontend/hooks/useSearchSSE.ts`, `frontend/hooks/useSearchProgress.ts`
**Estimativa:** S

---

### STORY-360: Inconsistencia de desconto entre planos e copy

**Prioridade:** P2
**Tipo:** fix (copy)
**Promessa afetada:** Confianca na transparencia de precos
**Causa raiz:** `planos/page.tsx:25` mostra annual com `discount: 25` (25%) resultando em R$297/mes. Mas `CLAUDE.md` documenta R$317/mes anual. FAQ diz "25% de economia" para anual. Consultoria usa 20% anual. Inconsistencia confunde usuario e suporte.

**Criterios de aceite:**
- [ ] AC1: Definir fonte unica de verdade para precos: `backend/services/billing.py` (Stripe e o master)
- [ ] AC2: Frontend busca precos do backend (`GET /plans`) em vez de hardcoded
- [ ] AC3: Verificar que Stripe price IDs correspondem aos valores exibidos
- [ ] AC4: Atualizar CLAUDE.md com precos corretos apos verificacao no Stripe
- [ ] AC5: FAQ de precos deve referenciar valores do mesmo objeto de dados
- [ ] AC6: Testes: verificar que `PRICING` e `CONSULTORIA_PRICING` sao consistentes com backend

**Arquivos afetados:** `frontend/app/planos/page.tsx`, `backend/services/billing.py`, `CLAUDE.md`
**Estimativa:** S

---

## Metricas de Validacao

Para verificar que cada promessa esta sustentada apos as correcoes:

| Promessa | Metrica | Threshold | Onde medir |
|----------|---------|-----------|------------|
| Cobertura de fontes | `smartlic_sources_bids_fetched_total` por source | >0 para todas as 3 fontes em 24h | Prometheus/Grafana |
| Taxa de descarte | `smartlic_filter_discard_rate` media 30d | >70% para claim "a maioria" | Prometheus/Grafana |
| Disponibilidade | `uptime_pct_30d` na pagina /status | >99% para claim "alta disponibilidade" | /status page |
| SLA suporte | `smartlic_support_response_time_hours` p95 | <24h uteis | Admin dashboard |
| Volume diario | `smartlic_bids_processed_total` / dia | >500 para claim "centenas/dia" | Prometheus |
| LLM fallback | `smartlic_llm_fallback_pending_total` / semana | <5% do total de classificacoes | Prometheus |
| Pipeline enforcement | 403 em POST /pipeline para trial excedido | 100% enforcement | Integration tests |
| Auth refresh | Taxa de 401 nao-recuperados | <0.1% das buscas | Sentry/logs |

---

## Riscos Aceitos

O conselho aceita os seguintes trade-offs como racionais para o estagio atual (POC avancado, pre-revenue):

1. **PNCP page size validation nao implementada em startup.** Risco: mudanca silenciosa do PNCP. Mitigacao existente: health canary com tamanhoPagina=50. Aceito porque canary ja detecta.

2. **ARQ sem dead-letter queue.** Risco: jobs de summary/excel perdidos silenciosamente apos 3 retries. Mitigacao existente: `gerar_resumo_fallback()` garante que usuario sempre recebe algo. Aceito porque impacto e cosmetico (summary generico vs LLM).

3. **Cache key growth unbounded.** Risco: memoria. Mitigacao: L1 InMemoryCache tem TTL de 4h com eviction. Aceito para volume atual (<100 usuarios).

4. **Viability score neutro (50) para bids sem valor.** Ja corrigido em CRIT-FLT-003. Score 50 e honesto. Aceito.

5. **Competitors (Effecti, Zionn) com mais fontes.** Aceito como gap de produto, nao como defeito. Roadmap deve priorizar integracao de portais municipais no Q3.

6. **ROI calculator e ferramenta de persuasao, nao predicao.** Aceito desde que disclaimers estejam claros (STORY-355).

7. **Stripe webhook signature verification ja implementada.** Confirmado em `webhooks/stripe.py:96` com `construct_event()`. Nao e risco.

8. **Quota race condition e mitigada.** `check_and_increment_quota_atomic()` usa RPC atomico no Supabase. O fallback para asyncio.Lock so se aplica se RPC falhar, o que e raro. Aceito.

---

## Priorizacao Consolidada

| Sprint | Story | Prioridade | Estimativa | Justificativa |
|--------|-------|-----------|------------|---------------|
| Imediato | STORY-350 | P0 | M | Copy "+98%" e refutavel e visivel na landing page |
| Imediato | STORY-352 | P0 | S | "24/7" e promessa falsa verificavel |
| Sprint 1 | STORY-351 | P0 | L | "87%" sem metrica e bomba-relogio de credibilidade |
| Sprint 1 | STORY-354 | P0 | XL | LLM REJECT silencioso contradiz "nenhuma invisivel" |
| Sprint 2 | STORY-355 | P1 | M | ROI agressivo erodir confianca de consultorias |
| Sprint 2 | STORY-356 | P1 | S | Pipeline bypass e falha de seguranca |
| Sprint 2 | STORY-357 | P1 | M | Auth expiry durante busca = UX quebrado |
| Sprint 3 | STORY-353 | P1 | L | SLA sem enforcement nao e SLA |
| Sprint 3 | STORY-358 | P2 | M | "1000+/dia" sem medicao |
| Sprint 3 | STORY-359 | P2 | S | SSE silencioso e trust gap menor |
| Sprint 3 | STORY-360 | P2 | S | Inconsistencia de precos confunde suporte |

**Esforco total estimado:** 2 XL + 2 L + 4 M + 3 S = ~8-10 semanas com 1 dev

---

_Consenso unanime: 8/8 clusters (53 CTOs)_

**Clusters representados:**
- Cluster 1 (SaaS B2B/B2G): Validou riscos de copy quantificada sem metrica
- Cluster 2 (Fintech/Billing): Confirmou Stripe webhook seguro, questionou inconsistencia de precos
- Cluster 3 (AI/ML): Flagou LLM REJECT como anti-padrao para "zero oportunidades invisiveis"
- Cluster 4 (Infra/DevOps): Validou que 24/7 e insustentavel pre-revenue, sugeriu SLO em vez de SLA
- Cluster 5 (Growth/PLG): ROI calculator agressivo pode funcionar para SMB mas destruir credibilidade com consultorias
- Cluster 6 (Data/Analytics): Sem metricas de cobertura e discard rate, claims sao marketing ficcional
- Cluster 7 (Security): Pipeline frontend-only e vulnerabilidade; auth refresh e hygiene basica
- Cluster 8 (UX/Product): SSE fallback silencioso e anti-padrao de confianca; transparencia > perfeicao
