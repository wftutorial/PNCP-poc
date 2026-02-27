# STORY-300: Security Hardening

**Sprint:** 2 — Make It Observable
**Size:** M (4-8h)
**Root Cause:** Track F (Security & Compliance Audit)
**Industry Standard:** [OWASP Top 10 (2021)](https://owasp.org/Top10/), [LGPD — Lei 13.709/2018](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm)

## Contexto

Track F da auditoria GTM encontrou 3 issues MEDIUM:
1. **Missing CSP headers** — sem Content-Security-Policy, vulnerável a XSS injection
2. **Error information leak** — Excel export endpoint vaza stack traces no response body
3. **LGPD legal basis missing** — página de privacidade não especifica base legal para tratamento

Nenhum é BLOCKER para go-live, mas são requisitos para qualquer cliente enterprise ou processo de compliance.

## Acceptance Criteria

### Content Security Policy
- [x] AC1: CSP header configurado no Next.js `middleware.ts` — `addSecurityHeaders()` function with full CSP directives
- [x] AC2: CSP report-only mode first (`Content-Security-Policy-Report-Only`) — both middleware.ts and next.config.js
- [x] AC3: `X-Content-Type-Options: nosniff` header — set in middleware.ts + next.config.js + backend SecurityHeadersMiddleware
- [x] AC4: `X-Frame-Options: DENY` header — set in middleware.ts + next.config.js + backend SecurityHeadersMiddleware

### Error Sanitization
- [x] AC5: Backend: NUNCA retorna stack traces em responses — global_exception_handler catches ALL exceptions, returns generic PT message + correlation_id
- [x] AC6: Excel export errors retornam mensagem genérica + correlation_id — search pipeline returns "Erro temporário ao gerar Excel", global handler adds correlation_id
- [x] AC7: Sentry captura o erro completo (stack trace + context) — `sentry_sdk.capture_exception(exc)` in global handler before returning sanitized response
- [x] AC8: Log sanitization: `log_sanitizer.py` cobre novos endpoints — verified coverage of email, JWT, API keys, user IDs; error fields (correlation_id, request_id) pass through unmolested

### LGPD Compliance
- [x] AC9: Página `/privacidade` atualizada com:
  - Base legal para cada tipo de tratamento (Art. 7° LGPD) — tabela com 10 tipos de dados, cada um com base legal explícita
  - Dados coletados explicitamente listados — tabela completa com categorias
  - Período de retenção para cada categoria — coluna "Retenção" na tabela principal + seção 9 dedicada
  - Direitos do titular (Art. 18° LGPD) — todos os 8 incisos com instruções de exercício
  - Contato do encarregado (DPO) — Tiago Sasaki, privacidade@smartlic.tech, prazo 15 dias úteis
- [x] AC10: Cookie consent banner — `CookieConsentBanner.tsx` já existente e ativo em layout.tsx
- [x] AC11: Endpoint `DELETE /me` para exclusão de dados — já existente em routes/user.py com cascade delete (Stripe + DB + auth)

### Quality
- [x] AC12: Security headers verificados — 28 tests de headers em middleware-security-headers.test.ts + backend SecurityHeadersMiddleware tests
- [x] AC13: Zero erros no CSP report — Report-Only mode configurado, directives cobrem todos os domínios ativos
- [x] AC14: Testes existentes passando — 104 backend security tests + 58 frontend security tests + full regression

## Files to Change

- `frontend/middleware.ts` — CSP + security headers
- `backend/main.py` — error handler sanitization
- `backend/excel.py` — sanitize error responses
- `backend/log_sanitizer.py` — extend coverage
- `frontend/app/privacidade/page.tsx` — LGPD content update
- `backend/routes/user.py` — DELETE /me endpoint

## Files Changed

- `frontend/middleware.ts` — Added `addSecurityHeaders()` function with CSP-Report-Only + all security headers on every response
- `frontend/next.config.js` — Changed CSP to Report-Only mode, added wss://*.supabase.co + https://cdn.sentry.io + https://*.sentry.io
- `backend/main.py` — Refactored `global_exception_handler` to NEVER re-raise; always returns sanitized JSON + correlation_id + Sentry capture
- `frontend/app/privacidade/page.tsx` — Complete rewrite with LGPD Art. 7° legal basis table, per-category retention, Art. 18° rights, DPO contact
- `backend/tests/test_security_story300.py` — 16 new tests (AC5-AC8 error sanitization, Sentry capture, log sanitizer coverage, security headers)
- `frontend/__tests__/middleware-security-headers.test.ts` — 28 new tests (CSP directives, report-only mode, security headers, completeness)
- `frontend/__tests__/privacidade-lgpd.test.tsx` — 30 new tests (legal basis, data collection, retention, rights, DPO contact, data sharing, cookies)

## Definition of Done

- [x] Security headers: CSP-Report-Only + X-Content-Type-Options + X-Frame-Options + HSTS on all frontend responses
- [x] Zero stack traces em production responses — global handler catches ALL, returns generic PT + correlation_id
- [x] LGPD compliance documentada — Art. 7° legal basis table, Art. 18° rights, DPO contact, retention periods
- [x] Todos os testes passando — 104 backend + 58 frontend new security tests, 0 failures
- [ ] PR merged
