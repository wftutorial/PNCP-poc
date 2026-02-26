# GTM Validation Sprint Plan V2 — "Root Cause, Not Symptom"

**Created:** 2026-02-26
**Replaces:** GTM-VAL-SPRINT-PLAN.md (v1 tinha 8 stories baseadas em especulacao)
**Principio:** Cada story fundamentada com pesquisa web, CVE databases, docs oficiais, e precos reais de concorrentes.

---

## O que mudou de V1 para V2

### Fixes ja aplicados (commit `7bf0f19`)
- [x] FK violation (search_cache.py skip L1 para WARMING_USER_ID)
- [x] Progress bar (batch_progress events passam para currentEvent)
- [x] 3 migrations pendentes aplicadas (120000, 130000, 140000)

### Stories descartadas/substituidas
| V1 | Problema | V2 |
|----|---------|-----|
| STORY-268 (progress bar) | Tratava sintoma, nao causa raiz (pub/sub perde mensagens) | **STORY-276** (Redis Streams) |
| STORY-269 (pricing) | Sem dados de mercado | **STORY-277** (precos reais de 8 concorrentes) |
| STORY-270 (email alerts) | Arquitetura especulativa | **STORY-278** (Resend batch API + ARQ cron validados) |
| STORY-272 AC2 (CVEs) | Versoes imprecisas | **STORY-279** (CVEs exatos com IDs e versoes) |
| STORY-275 (Boleto/PIX) | Afirmava que PIX suporta subscriptions (NAO suporta) | **STORY-280** (restricoes Stripe documentadas) |

### Stories mantidas (nao dependem de pesquisa tecnica)
- **STORY-271** (Sentry Zero) — parcialmente resolvido pelo fix de FK
- **STORY-272** AC1/AC3/AC4/AC5 — seguranca (passwords, ToS, Mercado Pago, npm audit)
- **STORY-273** (Social Proof) — conteudo PO, nao tecnico
- **STORY-274** (Infra Observability) — polish, P2

---

## Sprint Overview

| Story | Title | Priority | Effort | Week | Fundamento |
|-------|-------|----------|--------|------|------------|
| **STORY-276** | Redis Streams Progress | P0 BLOCKER | 2-3d | 1 | Redis docs + community patterns |
| **STORY-277** | Pricing Realignment | P0 BLOCKER | 1+1d | 1 | 8 concorrentes com precos reais |
| **STORY-278** | Email Digest Alerts | P0 BLOCKER | 3-4d | 2 | Resend API + ARQ cron validados |
| **STORY-279** | CVE Remediation | P1 | 0.5d | 1 | NVD + GitHub Advisory Database |
| **STORY-280** | Boleto/PIX Stripe | P2 | 2d | 3 | Stripe docs oficiais |
| **STORY-272** | Security Hygiene (restante) | P1 | 1d | 1 | — |
| **STORY-273** | Social Proof + Trust | P1 | 2-3d | 2 | — |
| **STORY-274** | Infra Observability | P2 | 1-2d | 3 | — |

---

## Execution Order

```
Week 1 (ROOT CAUSES)
├── STORY-276: Redis Streams (Day 1-3) ← FIX REAL da barra de progresso
├── STORY-277: Pricing Decision (Day 1) ← PO decide, dev implementa Day 2
├── STORY-279: CVE Update (Day 1) ← 30 min, pip install + test
└── STORY-272: Security (Day 2) ← passwords, ToS, npm audit

Week 2 (TABLE STAKES)
├── STORY-278: Email Digest (Day 4-7) ← Feature que todo concorrente tem
├── STORY-273: Social Proof (Day 4-6) ← PO fornece conteudo
└── STORY-276: QA validation (Day 5) ← E2E do Streams

Week 3 (POLISH + LAUNCH)
├── STORY-274: Infra Observability (Day 8-9)
├── STORY-280: Boleto/PIX (Day 8-10)
├── GTM LAUNCH: Beta com invite (Day 11)
└── Monitor: 10 trial signups, 0 Sentry errors
```

---

## Gate Criteria

### Gate 1: End of Week 1 — "Engine Fixed"
- [ ] STORY-276 AC1+AC2 merged (progress via Streams, zero message loss)
- [ ] STORY-277 AC1 completed (pricing decision made, with market data)
- [ ] STORY-279 AC1+AC2 merged (cryptography 46.0.5, python-multipart 0.0.22)
- [ ] STORY-272 AC1+AC3+AC4+AC5 merged
- [ ] Sentry: ≤1 unresolved (FK violation fix + Streams devem zerar)
- [ ] Backend tests: 0 failures
- [ ] Frontend tests: 0 failures

### Gate 2: End of Week 2 — "GTM Minimum"
- [ ] STORY-278 AC1-AC5 merged (digest working, Resend batch)
- [ ] STORY-273 AC1+AC4 merged (testimonials + /sobre)
- [ ] STORY-277 AC2+AC3 merged (pricing implemented)
- [ ] 10 buscas consecutivas com progress bar funcional (0→100%, sem travar)
- [ ] Sentry: 0 unresolved por 48h

### Gate 3: End of Week 3 — "GTM Launch"
- [ ] Todos stories completed
- [ ] Smoke test: login → busca → progresso → resultado → download
- [ ] Primeiro digest email enviado para beta testers
- [ ] 5-10 beta invites sent
- [ ] Pricing page com precos reais e metodos de pagamento

---

## Risk Register

| Risco | Prob | Impacto | Mitigacao | Fonte |
|-------|------|---------|----------|-------|
| Redis nao suporta Streams | Baixa | Alto | Verificar Redis version (5.0+). Upstash e Railway suportam. | [Redis Streams docs](https://redis.io/docs/latest/develop/data-types/streams/) |
| cryptography 46.x quebra JWT | Media | Alto | Full test suite antes de merge. Pin 44.0.1 se 46.x falhar. | [GHSA-r6ph-v2qm-q3c2](https://github.com/pyca/cryptography/security/advisories/GHSA-r6ph-v2qm-q3c2) |
| Resend free tier insuficiente | Baixa | Medio | Pro = $20/mes. Ligar apenas quando >50 usuarios. | [Resend pricing](https://resend.com/pricing) |
| PO atrasa decisao de pricing | Media | Critico | Timebox 24h. Default = Opcao 1 (beta gratuito + R$297-397). | Benchmark: Siga Pregao R$397, Licitei R$393 |
| PIX nao funciona para subscription | Zero | Zero | Ja documentado: Boleto only para recurring. PIX optional para avulso. | [Stripe PIX docs](https://docs.stripe.com/payments/pix) |
| ARQ nao processa search_job | Media | Alto | Verificar `queued=0` pos-deploy. Se persistir, investigar re-enqueue bug ([Issue #432](https://github.com/python-arq/arq/issues/432)). | [ARQ GitHub Issues](https://github.com/python-arq/arq/issues) |
