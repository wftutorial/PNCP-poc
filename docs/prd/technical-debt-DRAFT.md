# GTM Readiness Assessment — DRAFT

**Project:** SmartLic | **Date:** 2026-03-12 | **Status:** CONSOLIDATED
**Versao:** 2.0 (sobrescreve auditoria 2026-03-10)

---

## Objetivo

Avaliar a prontidao do SmartLic v0.5 para Go-To-Market, identificando bloqueadores, riscos e selling points. Este documento consolida as analises de @architect, @data-engineer e @ux-design-expert.

---

## 1. Veredito Consolidado

### STATUS GERAL: PRONTO PARA GTM

O sistema esta operacional em producao com:
- Pipeline de busca multi-fonte funcional (PNCP + PCP v2)
- Classificacao IA com GPT-4.1-nano e fallback robusto
- Billing completo (Stripe + Trial 14d + 3 planos)
- Seguranca production-grade (RLS 100%, Pydantic, Zod, rate limiting)
- 7873+ testes automatizados (5131 backend + 2681 frontend + 60 E2E)
- CI/CD com 18 GitHub Actions workflows
- Observabilidade: Sentry + Prometheus + OTEL

---

## 2. Bloqueadores GTM (Esforco Total: < 30 minutos)

| # | Bloqueador | Area | Esforco | Risco |
|---|-----------|------|---------|-------|
| 1 | CNPJ placeholder na pagina de privacidade | Legal/Frontend | 5min | Juridico |
| 2 | /pipeline ausente do middleware auth | Seguranca/Frontend | 5min | Acesso nao-auth |

**Ambos sao fixes triviais que devem ser feitos ANTES do lancamento.**

---

## 3. Fixes Rapidos Pre-GTM (< 4h total)

| # | Item | Area | Esforco |
|---|------|------|---------|
| 1 | CNPJ na privacidade | Frontend | 5min |
| 2 | /pipeline no middleware | Frontend | 5min |
| 3 | Icone Dashboard no BottomNav | Frontend | 5min |
| 4 | /metrics com token obrigatorio | Backend | 1h |
| 5 | useReducedMotion em 9 arquivos | Frontend | 2h |
| 6 | aria-expanded no FAQ pricing | Frontend | 30min |

---

## 4. Selling Points Tecnicos para GTM

### 4.1 Resiliencia (Diferencial #1)
- Circuit breaker per-source com Redis persistence
- Fallback cascade: Live -> Partial -> Stale -> Empty
- Timeout chain validado no startup
- 17 banners de estado para transparencia total ao usuario
- SSE progress tracking com fallback automatico

### 4.2 IA Zero-Noise
- GPT-4.1-nano para classificacao setorial
- Cache L1 (in-memory 5K entries) + L2 (Redis 1h TTL)
- Fallback = REJECT (nunca mostra ruido)
- Viability assessment deterministico (4 fatores, sem LLM)

### 4.3 Cache Inteligente
- 3 niveis: InMemory (4h) + Redis + Supabase (24h)
- SWR: serve stale enquanto revalida em background
- Priority tiering: hot/warm/cold com TTLs diferentes
- Recovery epoch para invalidar cache de degradacao

### 4.4 Billing Production-Ready
- Stripe: checkout, portal, webhooks (7 events), idempotency
- Trial 14d sem cartao
- 3 planos x 3 periodos com desconto progressivo
- Atomic quota, grace period 3d, "fail to last known plan"

### 4.5 Seguranca B2G-Grade
- RLS em 100% das tabelas (32/32), runtime assertion
- JWT dual-algorithm (HS256 + ES256/JWKS)
- Audit trail LGPD com hash de PII
- Rate limiting Redis, Stripe webhook signature
- MFA com TOTP + recovery codes (bcrypt hash)

---

## 5. Riscos Operacionais Mitigados

| Risco | Mitigacao | Status |
|-------|----------|--------|
| PNCP degradation | Circuit breaker + cache SWR + recovery epoch | MITIGADO |
| Redis outage | InMemoryCache fallback 10K entries | MITIGADO |
| Supabase outage | L3 filesystem cache 200MB | MITIGADO |
| Railway timeout 120s | Timeout chain validado | MITIGADO |
| LLM failure | REJECT fallback (zero noise) | MITIGADO |
| Stripe webhook miss | Idempotency + 3d grace | MITIGADO |
| Worker crash | Restart wrapper max 10 + inline fallback | MITIGADO |

---

## 6. Debitos Tecnicos (Nao Bloqueiam GTM)

### Sistema
| ID | Issue | Severidade | Acao |
|----|-------|-----------|------|
| SYS-01 | pncp_client.py 2541 LOC | Alta | Decomposicao pos-GTM |
| SYS-02 | search_cache.py 2512 LOC | Alta | Decomposicao pos-GTM |
| SYS-03 | SearchContext campos Any | Media | Tipar pos-GTM |
| SYS-04 | asyncio fire-and-forget | Media | Error handling pos-GTM |
| SYS-05 | Redis socket_timeout 30s | Media | Per-command timeout pos-GTM |

### Database
| ID | Issue | Severidade | Acao |
|----|-------|-----------|------|
| DB-01 | N+1 alerts sent_counts | Media | RPC pos-GTM (2h) |
| DB-02 | Python aggregation analytics | Media | SQL UNNEST pos-GTM (4h) |
| DB-03 | stripe_webhook_events sem cleanup | Baixa | pg_cron pos-GTM (1h) |
| DB-04 | 90 migrations 3 naming conventions | Baixa | Squash pos-v1.0 |

### Frontend
| ID | Issue | Severidade | Acao |
|----|-------|-----------|------|
| UX-01 | CSS tokens 3 sintaxes | Media | Unificar pos-GTM |
| UX-02 | next/image em 1 pagina | Media | Expandir pos-GTM |
| UX-03 | God hook 40+ valores | Media | Refactor pos-GTM |
| UX-04 | 20+ any em producao | Baixa | Tipar pos-GTM |
| UX-05 | /planos + /pricing duplicados | Baixa | Canonical pos-GTM |

---

## 7. Perguntas para Especialistas

### @data-engineer
1. N+1 em alerts: confirma que e baixo impacto para < 100 usuarios ativos?
2. stripe_webhook_events: volume esperado no primeiro mes?

### @ux-design-expert
1. BottomNav icone errado: confirma fix trivial?
2. Framer Motion reduced-motion: prioridade pre ou pos-GTM?

---

## 8. Proximos Passos

1. **IMEDIATO (< 30min):** Fixes bloqueadores (CNPJ + /pipeline middleware)
2. **PRE-GTM (< 4h):** Fixes rapidos (icone, /metrics, a11y)
3. **POS-GTM Sprint 1:** Debitos de severidade Alta (decomposicao monolitos)
4. **POS-GTM Sprint 2:** Debitos de severidade Media (N+1, typing, cache)
