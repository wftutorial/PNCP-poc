# SmartLic - System Architecture: GTM Readiness Assessment

**Data:** 2026-03-12 | **Auditor:** @architect | **Foco:** Prontidao para Go-To-Market
**Codebase:** commit main HEAD | **Versao:** 2.0 (sobrescreve auditoria 2026-03-10)

---

## 1. Resumo Executivo - Prontidao do Sistema

O SmartLic esta em estagio **POC avancado (v0.5)** com infraestrutura de producao funcional. A avaliacao abaixo classifica cada area critica para GTM em: PRONTO, PARCIAL, ou BLOQUEADOR.

| Area | Status GTM | Justificativa |
|------|-----------|---------------|
| Search Pipeline | PRONTO | 7 estagios funcionais, timeout chain validado, fallback cascade operacional |
| Data Sources | PARCIAL | PNCP (pri 1) + PCP v2 (pri 2) ativos; ComprasGov v3 DESABILITADO em prod |
| AI/LLM Classification | PRONTO | GPT-4.1-nano com cache L1+L2, fallback = REJECT (zero noise) |
| Cache Layer | PRONTO | 3 niveis (InMemory + Redis + Supabase), SWR implementado |
| Auth & Billing | PRONTO | Supabase Auth + Stripe + trial 14d + quotas atomicas |
| Background Jobs | PRONTO | ARQ worker separado, fallback inline quando Redis indisponivel |
| Monitoring | PARCIAL | Sentry + Prometheus + OTEL configurados, mas SLOs sao ephemeral (reset no restart) |
| API Routes | PRONTO | 49 endpoints, 19 modulos, versionamento parcial (/v1/ em alguns) |
| Infrastructure | PRONTO | Railway (web+worker+frontend), CI/CD com 18 workflows GitHub Actions |
| Tests | PRONTO | 5131+ backend, 2681+ frontend, 60 E2E, zero-failure policy |

**Veredito Global: PRONTO PARA GTM** com 3 items de atencao (nenhum bloqueador hard).

---

## 2. Items de Atencao GTM

### ATT-01: ComprasGov v3 Desabilitado (Cobertura de Dados)
- `COMPRASGOV_ENABLED=false` em producao
- Terceira fonte de dados nao contribui para redundancia
- **Impacto GTM:** Clientes podem questionar cobertura. Nao e bloqueador — PNCP + PCP cobrem as necessidades core
- **Recomendacao:** Documentar como "roadmap" ou habilitar com feature flag para beta users

### ATT-02: SLO Tracking Ephemeral
- `slo.py` calcula metricas a partir do Prometheus in-memory — reset a cada deploy/restart
- **Impacto GTM:** Sem historico de SLA para apresentar a clientes enterprise. Nao afeta clientes SMB/trial
- **Recomendacao:** Conectar a Prometheus server externo ou Grafana Cloud (4h)

### ATT-03: Endpoint /metrics sem Auth por Default
- `METRICS_TOKEN` vazio = endpoint aberto
- **Impacto GTM:** Information disclosure. Correcao trivial
- **Recomendacao:** Exigir token nao-vazio em producao (1h)

---

## 3. Pontos Fortes para GTM (Selling Points)

### 3.1 Resiliencia de Pipeline
- Circuit breaker per-source com Redis persistence
- Fallback cascade: Live -> Partial -> Stale cache -> Empty (nunca falha silenciosamente)
- Timeout chain validado no startup: Job(300s) > Pipeline(110s) > Consolidation(100s) > PerSource(80s) > PerUF(30s)
- SSE progress tracking com heartbeat 15s + fallback time-based simulation
- State machine persiste transicoes async (zero latency impact)

### 3.2 Billing & Trial Ready
- Stripe integrado: checkout, portal, webhooks idempotentes (7 event types)
- Trial 14 dias sem cartao
- 3 planos: SmartLic Pro R$397/mes, Consultoria R$997/mes + periodos semestral/anual com desconto
- Grace period 3 dias, atomic quota increment, localStorage plan cache 1h
- "Fail to last known plan": nunca downgrade por erro de DB

### 3.3 Seguranca Production-Grade
- Supabase Auth com RLS em TODAS as 32 tabelas (3 rounds de audit + runtime assertion)
- Input validation: Pydantic v2 (backend) + Zod v4 (frontend)
- Log sanitization PII, audit trail com hash LGPD
- Redis rate limiting, Stripe webhook signature verification
- JWT dual-algorithm: HS256 + ES256/JWKS (future-proof Supabase key rotation)

### 3.4 Observabilidade
- Structured JSON logging com request_id/search_id/trace_id correlation
- Sentry error tracking com PII scrubbing e noise filtering
- Health endpoints per-source com response time tracking
- 18 CI/CD workflows cobrindo tests, migrations, deploy, E2E, Lighthouse

### 3.5 App Factory Architecture (DEBT-107)
- `main.py` thin (80 LOC) com `create_app()` limpo
- Config modularizada: `config/base.py`, `config/features.py`, `config/pncp.py`, `config/pipeline.py`
- 28 feature flags com cache 60s TTL (hot-reload sem restart)
- Environment validation: hard-fail apenas em producao

---

## 4. Riscos Operacionais para GTM

| Risco | Probabilidade | Impacto | Mitigacao Existente | Status |
|-------|--------------|---------|---------------------|--------|
| PNCP API degradation | Alta (historico) | Alto | Circuit breaker + cache SWR + recovery epoch | MITIGADO |
| Redis outage | Baixa | Medio | InMemoryCache fallback (10K entries per worker) | MITIGADO |
| Supabase outage | Baixa | Alto | L3 filesystem cache (/tmp, 200MB max) | MITIGADO |
| Railway timeout (120s) | Media | Medio | Timeout chain validado no startup | MITIGADO |
| LLM API failure | Media | Baixo | Fallback = REJECT (zero noise philosophy) | MITIGADO |
| Stripe webhook miss | Baixa | Medio | Idempotency + 3-day grace period | MITIGADO |
| Worker crash loop | Baixa | Medio | Restart wrapper (max 10, 5s delay) | MITIGADO |

---

## 5. Debitos Tecnicos (Nao Bloqueiam GTM)

| ID | Issue | LOC | Prioridade Pos-GTM |
|----|-------|-----|---------------------|
| DEBT-SYS-01 | `pncp_client.py` monolito (2541 LOC) | 2541 | Alta — decomposicao |
| DEBT-SYS-02 | `search_cache.py` monolito (2512 LOC) | 2512 | Alta — decomposicao |
| DEBT-SYS-03 | `SearchContext` campos `Any` (deveria ser tipado) | - | Media |
| DEBT-SYS-04 | Re-exports backward compat em main/filter/search | - | Baixa |
| DEBT-SYS-05 | `pncp_client_resilient.py` possivelmente dead code | ~300 | Baixa |
| DEBT-SYS-06 | 232 test files com naming incident-specific | - | Baixa |
| DEBT-SYS-07 | `asyncio.create_task()` fire-and-forget sem error handling | - | Media |
| DEBT-SYS-08 | Redis `socket_timeout=30s` pode bloquear async worker | - | Media |

---

## 6. Checklist GTM - Sistema

- [x] Pipeline de busca funcional em producao
- [x] 2+ fontes de dados ativas (PNCP + PCP v2)
- [x] Classificacao IA operacional com fallback
- [x] Cache multi-nivel com SWR
- [x] Auth + Billing + Trial integrados
- [x] CI/CD automatizado com 18 workflows
- [x] Testes: 5131 backend + 2681 frontend + 60 E2E
- [x] Zero-failure policy mantida
- [x] Monitoring: Sentry + Prometheus + OTEL
- [x] Rate limiting configurado
- [x] Seguranca: RLS 100%, JWT, PII sanitization
- [x] Feature flags (28) com hot-reload
- [x] Worker com restart wrapper e fallback inline
- [ ] SLO tracking persistente (ephemeral hoje) — nao bloqueia
- [ ] /metrics endpoint protegido — fix trivial
- [ ] ComprasGov v3 habilitado — opcional
