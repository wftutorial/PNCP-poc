# STORY-311: Security Headers + Hardening

**Epic:** EPIC-PRE-GTM-2026-02
**Sprint:** Sprint 1 (Pre-GTM)
**Priority:** HIGH
**Story Points:** 3 SP
**Estimate:** 1-2 dias
**Owner:** @dev + @devops

---

## Problem

Headers de seguranca existem em modo Report-Only (CSP) e alguns sao redundantes entre `next.config.js` e `middleware.ts`. Para producao pre-launch, precisamos:
1. Promover CSP de Report-Only para Enforce
2. Auditar e unificar headers
3. Adicionar protecoes ausentes no backend
4. Rate limiting adequado para APIs publicas

## Solution

Auditoria e hardening completo de seguranca HTTP em frontend e backend, com CSP enforcement gradual e rate limiting reforçado.

---

## Acceptance Criteria

### Frontend — CSP Enforcement

- [x] **AC1:** Promover CSP de `Content-Security-Policy-Report-Only` para `Content-Security-Policy` em `middleware.ts` (next.config.js headers removidos por AC5)
- [x] **AC2:** Configurar CSP report-uri para endpoint de coleta:
  - `report-uri /api/csp-report`
  - `report-to` directive com Reporting API v1 + `Report-To` header com group definition
- [x] **AC3:** Criar endpoint `frontend/app/api/csp-report/route.ts` que:
  - Recebe violation reports (POST JSON) — legacy report-uri + Reporting API v1
  - Log estruturado com: `violated_directive`, `blocked_uri`, `document_uri`
  - Rate limit: max 100 reports/min via in-memory counter com cleanup
- [x] **AC4:** Auditar e whitelist todos os dominios necessarios no CSP:
  - `script-src`: self, unsafe-inline, unsafe-eval, Stripe.js, Cloudflare Insights, Sentry CDN
  - `connect-src`: self, Supabase (co/in), Stripe API, Railway, Sentry ingest, SmartLic, Mixpanel, Supabase WSS
  - `frame-src`: self, Stripe.js
  - `img-src`: self, data, https, blob
  - `style-src`: self, unsafe-inline (Tailwind)
- [x] **AC5:** Remover duplicacao de headers entre `next.config.js` e `middleware.ts` — unificado em middleware.ts (next.config.js headers() removido)

### Frontend — Headers Adicionais

- [x] **AC6:** Adicionar `Cross-Origin-Opener-Policy: same-origin` (previne Spectre-like attacks)
- [x] **AC7:** `Cross-Origin-Embedder-Policy: require-corp` — **SKIPPED**: quebraria iframe do Stripe Checkout (Stripe nao envia CORP headers). Documentado em middleware.ts.
- [x] **AC8:** Adicionar `X-DNS-Prefetch-Control: off` (previne DNS leak de links em emails)

### Backend — Security Middleware

- [x] **AC9:** Auditar `SecurityHeadersMiddleware` em `backend/middleware.py`:
  - Headers alinhados com frontend (HSTS com preload, X-Content-Type, X-Frame, Referrer-Policy, Permissions-Policy)
  - `Cache-Control: no-store` adicionado quando request tem Authorization header
- [x] **AC10:** Rate limiting por IP em endpoints publicos via `RateLimitMiddleware`:
  - `/health`, `/v1/health`, `/v1/health/cache`: 60 req/min
  - `/plans`, `/v1/plans`: 30 req/min
  - `/webhook/stripe`, `/v1/webhook/stripe`: exempt
  - `/buscar`: usa token bucket existente (Redis)
- [x] **AC11:** `Permissions-Policy: camera=(), microphone=(), geolocation=()` — confirmado alinhado frontend/backend

### Backend — Input Validation Hardening

- [x] **AC12:** Auditoria SQL injection: **SAFE** — todos os endpoints usam Supabase PostgREST ORM (parameterized queries). Zero raw SQL com string concatenation. Unico `cursor.execute()` em script offline (`validate_schema.py`) com query hardcoded.
- [x] **AC13:** `term_parser.py` protegido contra ReDoS:
  - `MAX_INPUT_LENGTH = 256` chars (trunca com warning log)
  - Regexes existentes sao simples (sem backtracking exponencial): `r"\s+"` e `unicodedata.normalize`
- [x] **AC14:** `log_sanitizer.py` cobre todos os campos sensiveis:
  - user_id (parcial: `550e8400-***`), email (mascarado: `u***@domain.com`)
  - access_token/JWT (nunca logado: `eyJ***[JWT]`), password (`[PASSWORD_REDACTED]`)
  - API keys, IP addresses, phone numbers — SENSITIVE_FIELDS inclui 20+ field names

### Infra — HTTPS / TLS

- [x] **AC15:** Railway fornece HTTPS automatico via Let's Encrypt para custom domains. Redirect HTTP→HTTPS configurado em middleware.ts (Railway nao forca redirect na infra).
- [x] **AC16:** HSTS preload eligibility verificada — `max-age=31536000; includeSubDomains; preload` adicionado em frontend (middleware.ts) e backend (middleware.py). Todos os requisitos atendidos.
- [x] **AC17:** Submissao a hstspreload.org: **ELEGIVEL** — submeter manualmente em https://hstspreload.org apos deploy. Processamento leva 1-4 semanas + propagacao via releases do Chrome. NOTA: inclusao e irreversivel.

### Testes

- [x] **AC18:** Teste automatizado que valida presenca de todos os headers esperados em responses — `test_security_headers.py` (41 tests) + `middleware-security-headers.test.ts` (42 tests)
- [x] **AC19:** Teste CSP violation report endpoint — `csp-report.test.ts` (6 tests): legacy format, Reporting API, rate limiting, IP isolation, structured logging
- [x] **AC20:** Zero regressions — backend 5774+ pass, frontend 2681+ pass (pendente confirmacao final)

---

## Infraestrutura Existente

| Componente | Arquivo | Status |
|-----------|---------|--------|
| CSP (Report-Only) | `frontend/next.config.js:57-73` | Existe, precisa enforce |
| Security headers (FE) | `frontend/middleware.ts:22-53` | Existe, duplicado |
| Security headers (FE) | `frontend/next.config.js:27-76` | Existe, duplicado |
| SecurityHeadersMiddleware (BE) | `backend/main.py:50` | Existe, auditar |
| Rate limiting (Redis) | `backend/auth.py` token bucket | Existe |
| Log sanitizer | `backend/log_sanitizer.py` | Existe |
| Header tests | `frontend/__tests__/middleware-security-headers.test.ts` | Existe |

## Files (Output)

**Novos:**
- `frontend/app/api/csp-report/route.ts` — CSP violation report collection endpoint
- `frontend/__tests__/csp-report.test.ts` — 6 tests for CSP report endpoint

**Modificados:**
- `frontend/middleware.ts` — CSP enforcement, report-uri, COOP, HSTS preload, X-DNS-Prefetch-Control
- `frontend/next.config.js` — Removed duplicate headers (unified in middleware.ts)
- `frontend/__tests__/middleware-security-headers.test.ts` — Updated for STORY-311 (42 tests)
- `backend/middleware.py` — HSTS preload, Cache-Control on auth, RateLimitMiddleware
- `backend/main.py` — Register RateLimitMiddleware
- `backend/term_parser.py` — MAX_INPUT_LENGTH = 256 (ReDoS protection)
- `backend/tests/test_security_headers.py` — Expanded to 41 tests (AC9-AC14, AC16, AC18)

## Dependencias

- Nenhuma (independente)

## Riscos

- CSP enforce pode quebrar funcionalidades se whitelist incompleta — monitorar CSP reports apos deploy
- `Cross-Origin-Embedder-Policy` pode bloquear iframe do Stripe Checkout — testar antes de enforce
- HSTS preload e irreversivel (requer HTTPS para sempre no dominio)
