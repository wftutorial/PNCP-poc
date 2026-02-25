# STORY-269: GTM Pricing Strategy Decision — Reposition for Market Entry

**GTM Audit Ref:** B1 (BLOCKER) + H1 (social proof) + E-HIGH-003 (entry tier)
**Priority:** P0 — BLOCKER for GTM (strategic decision, not code)
**Effort:** 1 day (decision) + 2 days (implementation)
**Squad:** @po + @pm + @dev
**Source:** `docs/audits/gtm-validation-2026-02-25.md`, Track A

## Context

The GTM validation market research (Track A) revealed a critical pricing misalignment:

| Platform | Price | Clients | Features |
|----------|-------|---------|----------|
| ConLicitação | R$149/mês | 16,000-20,000+ | Busca + alertas + docs + suporte legal |
| Siga Pregão | R$397/mês | 2,700+ (4.9★) | 19 portais + robô de lance + IA |
| Effecti | Não público | 1,000+ | 1,400 portais + propostas auto |
| Licitei | R$101-393/mês | N/A | IA Q&A + robô + gestão docs |
| LicitaIA | R$67-247/mês | N/A | IA nativa (via Hotmart) |
| **SmartLic** | **R$1.999/mês** | **0 (pré-revenue)** | Busca IA + viabilidade (sem alertas, sem robô) |

**SmartLic cobra 5-13x mais que o mercado com MENOS features que competidores na faixa R$149-397.**

At R$1,999/month with zero social proof, zero conversions from cold traffic are expected.

## Decision Required

The PO must choose one of these strategies:

### Option 1: Beta Gratuito com Cap (RECOMENDADO)
- **Price:** R$0 por 90 dias (ou 100 buscas)
- **Goal:** Acumular 10-20 clientes reais, coletar depoimentos, validar product-market fit
- **Then:** Re-precificar baseado em feedback (provável R$399-799/mês)
- **Pros:** Remove barreira #1 (preço), gera social proof rápido
- **Cons:** Sem revenue por 3 meses
- **Implementation:** Extend trial to 90 days or 100 searches via config change

### Option 2: Tier de Entrada (R$497/mês) + Pro (R$1.999/mês)
- **SmartLic Essencial (R$497/mês):** 3 setores, 100 buscas, 5 UFs
- **SmartLic Pro (R$1.999/mês):** Tudo ilimitado (mantém)
- **Pros:** Revenue desde dia 1, upgrade path natural
- **Cons:** Requer implementação de limites por tier, Stripe products
- **Implementation:** 2-3 days (billing.py + quota.py + planos page)

### Option 3: Manter R$1.999 + Trial Estendido (30 dias)
- **Price:** R$1.999/mês mantido, trial de 7→30 dias
- **Pros:** Sem mudança de código, mais tempo para provar valor
- **Cons:** Não resolve o problema de preço vs mercado. Provavelmente zero conversões.
- **Implementation:** Config change only (TRIAL_DURATION_DAYS=30)

## Acceptance Criteria

### AC1: Pricing Decision Documented
- [ ] PO seleciona opção (1, 2, ou 3) com justificativa
- [ ] Decisão documentada em ADR (`docs/decisions/`)
- [ ] Impacto em code paths identificado

### AC2: Implementation (varies by option)

**If Option 1 (Beta Gratuito):**
- [ ] `config.py`: `TRIAL_DURATION_DAYS=90` ou `TRIAL_MAX_SEARCHES=100`
- [ ] `quota.py`: Adjust trial quota limits
- [ ] `frontend/app/planos/page.tsx`: Update messaging — "Acesso beta gratuito"
- [ ] Remove/hide Stripe checkout durante beta
- [ ] Landing page: "Acesso Gratuito por Tempo Limitado" CTA

**If Option 2 (Two Tiers):**
- [ ] `backend/services/billing.py`: Add `smartlic_essencial` plan
- [ ] `backend/quota.py`: Add tier-based limits (3 setores, 100 buscas, 5 UFs)
- [ ] `frontend/app/planos/page.tsx`: Two-card pricing layout
- [ ] Stripe: Create new product + price objects
- [ ] Migration: Update `PLAN_NAMES` and `PLAN_LIMITS`

**If Option 3 (Extended Trial):**
- [ ] `config.py`: `TRIAL_DURATION_DAYS=30`
- [ ] `frontend/app/planos/page.tsx`: Update trial duration copy
- [ ] Test quota enforcement at day 30

### AC3: Social Proof Placeholder
- [ ] Add "Empresas em beta" section to landing page (even if 0 initially)
- [ ] Create template for testimonial cards in `components/`
- [ ] Landing page: "Testado por X empresas no setor Y" (populate as beta users join)

## Dependencies

- Requires PO decision before implementation starts
- If Option 2: Stripe product setup required (DevOps)

## Risk

- **Option 1 risk:** No revenue validation — product could be "free-good but not pay-worthy"
- **Option 2 risk:** 2 days of implementation delays GTM
- **Option 3 risk:** Zero conversions at R$1,999 despite longer trial
