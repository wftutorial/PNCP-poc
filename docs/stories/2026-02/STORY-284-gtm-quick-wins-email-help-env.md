# STORY-284: GTM Quick Wins — Email Links, Help Page & Env Hygiene

**Priority:** P1 (GTM Blocker Resolution)
**Effort:** XS (0.5 day)
**Squad:** @dev
**Fundamentacao:** GTM Readiness Audit 2026-02-26 — Score 84.3/100
**Status:** DONE
**Sprint:** GTM Sprint 1 (Quick Wins)

---

## Contexto

O audit de GTM readiness identificou 6 quick wins que podem ser corrigidos em <1 dia e tem impacto direto na experiencia do usuario e confiabilidade operacional.

---

## Acceptance Criteria

### AC1: Fix broken email links `/precos` → `/planos`
- [x] `backend/templates/emails/billing.py` line 114: alterar `/precos` para `/planos`
- [x] `backend/templates/emails/billing.py` line 162: alterar `/precos` para `/planos`
- [x] `backend/templates/emails/quota.py` line 63: alterar `/precos` para `/planos`
- [x] `backend/templates/emails/quota.py` line 123: alterar `/precos` para `/planos`
- [x] Grep codebase inteiro por `/precos` para garantir nenhum outro caso
- [x] Teste unitario verifica que URLs nos templates apontam para `/planos`

### AC2: Update `/ajuda` about Boleto status
- [x] `frontend/app/ajuda/page.tsx` line ~119: alterar "Boleto e PIX estao em fase de implementacao" para "Aceitamos cartao de credito e Boleto Bancario. O Boleto pode levar ate 3 dias uteis para confirmacao."
- [x] Remover mencao a PIX (nao suportado para subscriptions) ou adicionar "PIX em breve"
- [x] FAQ section sobre pagamento consistente com `/planos`

### AC3: Add `SUPABASE_JWT_SECRET` to `.env.example`
- [x] Adicionar `SUPABASE_JWT_SECRET=` em `.env.example` na secao de Supabase vars
- [x] Documentar: "Required. JWT secret from Supabase dashboard > Settings > API > JWT Secret"
- [x] Verificar que `backend/config.py` `validate_env_vars()` ja valida esta var

### AC4: Document CSP `unsafe-eval` as accepted risk
- [x] Criar comentario em `frontend/next.config.js` na linha do `script-src` explicando:
  - Por que `unsafe-inline` e `unsafe-eval` sao necessarios (Next.js + Stripe.js)
  - Risco aceito e documentado
  - Plan futuro: migrar para nonce-based CSP quando Next.js suportar
- [x] Adicionar entrada no CHANGELOG.md

### AC5: Confirm SENTRY_DSN active in Railway
- [x] Executar `railway variables` e confirmar SENTRY_DSN esta configurado (backend e frontend)
- [x] Se nao configurado, adicionar imediatamente
- [ ] Verificar no Sentry dashboard que eventos estao chegando
- [x] Documentar status no handoff da sessao

### AC6: Remove 3 deprecated banner components
- [x] Deletar `frontend/app/buscar/components/DegradationBanner.tsx`
- [x] Deletar `frontend/app/buscar/components/CacheBanner.tsx`
- [x] Deletar `frontend/app/buscar/components/OperationalStateBanner.tsx`
- [x] Grep para confirmar nenhuma importacao residual desses componentes
- [x] Verificar que `DataQualityBanner` e usado em todos os lugares necessarios
- [x] Rodar `npm test` para confirmar sem regressoes (170/170 suites, 3372/3372 tests)
- [x] Rodar `npm run build` — Turbopack Windows junction bug (pre-existing); tsc --noEmit clean

---

## Testes Requeridos

- [x] `pytest -k "test_email"` — templates de email com URLs corretas (29/29 passed)
- [x] `npm test` — frontend sem regressoes (170/170 suites, 3372/3372 tests, 0 failures)
- [x] `npm run build` — Turbopack Windows junction bug (pre-existing, unrelated); tsc --noEmit clean

---

## Arquivos Impactados

| Arquivo | Mudanca |
|---------|---------|
| `backend/templates/emails/billing.py` | Fix `/precos` → `/planos` |
| `backend/templates/emails/quota.py` | Fix `/precos` → `/planos` |
| `backend/tests/test_email_templates.py` | Fix assertion `/precos` → `/planos` |
| `frontend/app/ajuda/page.tsx` | Update Boleto status text |
| `.env.example` | Add SUPABASE_JWT_SECRET |
| `frontend/next.config.js` | Document unsafe-eval |
| `CHANGELOG.md` | Add v0.5.1 entry |
| `frontend/app/buscar/components/DegradationBanner.tsx` | DELETE |
| `frontend/app/buscar/components/CacheBanner.tsx` | DELETE |
| `frontend/app/buscar/components/OperationalStateBanner.tsx` | DELETE |
| `frontend/__tests__/buscar/stale-cache.test.tsx` | DELETE (tested deleted component) |
| `frontend/__tests__/buscar/cache-banner-enhanced.test.tsx` | DELETE (tested deleted component) |
| `frontend/__tests__/buscar/operational-state.test.tsx` | DELETE (tested deleted component) |
| `frontend/__tests__/crit-016-sentry-bugs.test.tsx` | Remove OperationalStateBanner tests |
| `frontend/__tests__/story-257b/ux-transparente.test.tsx` | Remove CacheBanner + DegradationBanner tests |

## AC5 Evidence

```
SENTRY_DSN = https://7f1c331d9ee3d514f9d9e54fd1c7355f@o4509666913091584.ingest.us.sentry.io
NEXT_PUBLIC_SENTRY_DSN = https://7f1c331d9ee3d514f9d9e54fd1c7355f@o4509666913091584.ingest.us.sentry.io
SENTRY_ORG = confenge
SENTRY_PROJECT = smartlic-frontend
SENTRY_AUTH_TOKEN = [configured]
```

Both backend and frontend SENTRY_DSN are active in Railway.
