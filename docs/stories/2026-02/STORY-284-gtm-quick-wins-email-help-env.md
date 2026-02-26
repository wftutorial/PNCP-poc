# STORY-284: GTM Quick Wins — Email Links, Help Page & Env Hygiene

**Priority:** P1 (GTM Blocker Resolution)
**Effort:** XS (0.5 day)
**Squad:** @dev
**Fundamentacao:** GTM Readiness Audit 2026-02-26 — Score 84.3/100
**Status:** TODO
**Sprint:** GTM Sprint 1 (Quick Wins)

---

## Contexto

O audit de GTM readiness identificou 6 quick wins que podem ser corrigidos em <1 dia e tem impacto direto na experiencia do usuario e confiabilidade operacional.

---

## Acceptance Criteria

### AC1: Fix broken email links `/precos` → `/planos`
- [ ] `backend/templates/emails/billing.py` line 114: alterar `/precos` para `/planos`
- [ ] `backend/templates/emails/billing.py` line 162: alterar `/precos` para `/planos`
- [ ] `backend/templates/emails/quota.py` line 63: alterar `/precos` para `/planos`
- [ ] `backend/templates/emails/quota.py` line 123: alterar `/precos` para `/planos`
- [ ] Grep codebase inteiro por `/precos` para garantir nenhum outro caso
- [ ] Teste unitario verifica que URLs nos templates apontam para `/planos`

### AC2: Update `/ajuda` about Boleto status
- [ ] `frontend/app/ajuda/page.tsx` line ~119: alterar "Boleto e PIX estao em fase de implementacao" para "Aceitamos cartao de credito e Boleto Bancario. O Boleto pode levar ate 3 dias uteis para confirmacao."
- [ ] Remover mencao a PIX (nao suportado para subscriptions) ou adicionar "PIX em breve"
- [ ] FAQ section sobre pagamento consistente com `/planos`

### AC3: Add `SUPABASE_JWT_SECRET` to `.env.example`
- [ ] Adicionar `SUPABASE_JWT_SECRET=` em `.env.example` na secao de Supabase vars
- [ ] Documentar: "Required. JWT secret from Supabase dashboard > Settings > API > JWT Secret"
- [ ] Verificar que `backend/config.py` `validate_env_vars()` ja valida esta var

### AC4: Document CSP `unsafe-eval` as accepted risk
- [ ] Criar comentario em `frontend/next.config.js` na linha do `script-src` explicando:
  - Por que `unsafe-inline` e `unsafe-eval` sao necessarios (Next.js + Stripe.js)
  - Risco aceito e documentado
  - Plan futuro: migrar para nonce-based CSP quando Next.js suportar
- [ ] Adicionar entrada no CHANGELOG.md

### AC5: Confirm SENTRY_DSN active in Railway
- [ ] Executar `railway variables` e confirmar SENTRY_DSN esta configurado (backend e frontend)
- [ ] Se nao configurado, adicionar imediatamente
- [ ] Verificar no Sentry dashboard que eventos estao chegando
- [ ] Documentar status no handoff da sessao

### AC6: Remove 3 deprecated banner components
- [ ] Deletar `frontend/app/buscar/components/DegradationBanner.tsx`
- [ ] Deletar `frontend/app/buscar/components/CacheBanner.tsx`
- [ ] Deletar `frontend/app/buscar/components/OperationalStateBanner.tsx`
- [ ] Grep para confirmar nenhuma importacao residual desses componentes
- [ ] Verificar que `DataQualityBanner` e usado em todos os lugares necessarios
- [ ] Rodar `npm test` para confirmar sem regressoes
- [ ] Rodar `npm run build` para confirmar build limpo

---

## Testes Requeridos

- [ ] `pytest -k "test_email"` — templates de email com URLs corretas
- [ ] `npm test` — frontend sem regressoes apos remocao de componentes
- [ ] `npm run build` — build limpo

---

## Arquivos Impactados

| Arquivo | Mudanca |
|---------|---------|
| `backend/templates/emails/billing.py` | Fix `/precos` → `/planos` |
| `backend/templates/emails/quota.py` | Fix `/precos` → `/planos` |
| `frontend/app/ajuda/page.tsx` | Update Boleto status text |
| `.env.example` | Add SUPABASE_JWT_SECRET |
| `frontend/next.config.js` | Document unsafe-eval |
| `frontend/app/buscar/components/DegradationBanner.tsx` | DELETE |
| `frontend/app/buscar/components/CacheBanner.tsx` | DELETE |
| `frontend/app/buscar/components/OperationalStateBanner.tsx` | DELETE |
