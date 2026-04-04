# Auditoria de Seguranca — SmartLic

**Data:** 2026-04-04
**Commit:** `df3edeef`
**Escopo:** Resistencia a acesso direto ao backend (bypass frontend), manipulacao de banco via PostgREST, fraude em assinaturas, IDOR, privilege escalation

---

## Scorecard Geral

| Categoria | Status | Detalhe |
|-----------|--------|---------|
| JWT Auth & Validation | SEGURO | ES256/HS256, audience check, MFA para admin |
| CORS | SEGURO | Allowlist explicita, sem wildcard em producao |
| Input Validation (Pydantic) | SEGURO | Schemas validam todos os inputs, regex em datas/UUIDs |
| Stripe Webhook Signature | SEGURO | `construct_event()` + tabela de idempotencia |
| Log Sanitization | SEGURO | Emails, tokens, IPs, senhas mascarados |
| CSP Headers (Frontend) | SEGURO | Nonce-based, strict-dynamic, HSTS, X-Frame-Options DENY |
| XSS Prevention | SEGURO | Nenhum `dangerouslySetInnerHTML` com input de usuario |
| Rate Limiting | SEGURO | Redis + fallback in-memory, per-user/per-IP |
| SSRF | SEGURO | Nenhuma URL controlada pelo usuario em HTTP clients |
| RLS (Row Level Security) | SEGURO | Dual-client pattern (service_role vs user-scoped) |
| RPC Functions | CORRIGIDO | auth.uid() guards adicionados (era CRITICO) |
| Profiles Privilege Escalation | CORRIGIDO | Trigger bloqueia alteracao de is_admin/plan_type (era CRITICO) |
| IDOR em Search Endpoints | CORRIGIDO | Ownership check em 8 endpoints (era CRITICO) |
| Conversations p_is_admin bypass | CORRIGIDO | Verificacao interna de admin status (era CRITICO) |
| Admin Endpoints sem require_admin | CORRIGIDO | admin_trace.py agora usa require_admin (era ALTO) |
| Open Redirect no OAuth | CORRIGIDO | Whitelist de dominios no callback (era ALTO) |
| Circuit Breaker fail-open | CORRIGIDO | Default conservador free_trial (era ALTO) |
| Email/User Enumeration | CORRIGIDO | user_id removido da resposta auth/status (era ALTO) |
| Trial Multi-Account Abuse | CORRIGIDO | Rate limit 3 req/10min per IP nos endpoints de signup (era MEDIO) |
| Grace Period 7 dias | CORRIGIDO | Reduzido para 3 dias (era MEDIO) |
| Backend Dockerfile root | CORRIGIDO | USER appuser (uid 1001) adicionado (era MEDIO) |
| Dependencias Frontend CVEs | ACEITO | 8 low-severity em dev-dep transitiva (@lhci/cli→tmp); sem risco em producao |
| SENTRY_AUTH_TOKEN em runtime | N/A | Ja era ARG no builder stage, descartado no multi-stage final |

---

## O que foi feito (Commit df3edeef)

### Migration SQL: `20260404000000_security_hardening_rpc_rls.sql`

**Secao 1 — REVOKE em quota RPCs (CRIT-SEC-001)**

Funcoes `increment_quota_atomic`, `check_and_increment_quota` e `increment_quota_fallback_atomic` tiveram EXECUTE revogado para roles `PUBLIC` e `authenticated`. Apenas `service_role` pode chamar. Antes, qualquer usuario autenticado podia chamar via PostgREST direto e manipular quota de qualquer outro usuario.

**Secao 2 — auth.uid() guard em RPCs user-facing (CRIT-SEC-001/004)**

5 funcoes receberam validacao `IF auth.uid() IS NOT NULL AND p_user_id != auth.uid() THEN RAISE EXCEPTION`:

- `get_analytics_summary` — usuario so ve proprias analytics
- `get_conversations_with_unread_count` — p_is_admin agora verificado no DB (nao confia no parametro)
- `get_user_billing_period` — usuario so ve proprio billing
- `user_has_feature` — usuario so checa proprias features
- `get_user_features` — usuario so lista proprias features

Service role (backend) continua passando (auth.uid() retorna NULL).

**Secao 3 — Trigger prevent_privilege_escalation (CRIT-SEC-002)**

BEFORE UPDATE trigger em `profiles` que bloqueia alteracao de `is_admin`, `is_master` e `plan_type` quando o caller nao e `service_role`. Impede privilege escalation via PATCH direto no PostgREST.

**Secao 4 — REVOKE em RPCs admin-only**

Funcoes de sistema (`upsert_pncp_raw_bids`, `purge_old_bids`, `check_ingestion_orphans`, `check_pncp_raw_bids_bloat`, `pg_total_relation_size_safe`, `get_table_columns_simple`) tiveram EXECUTE revogado para usuarios comuns.

### Backend: IDOR Fix (CRIT-SEC-003)

**Arquivo:** `backend/routes/search_status.py`

Helper `_verify_search_ownership(search_id, user_id)` adicionada. Verifica no DB (`search_sessions.user_id`) que o search_id pertence ao usuario autenticado. Se a busca ainda esta em-flight (tracker in-memory, sem registro no DB), permite acesso.

Aplicada em 8 endpoints:
- `GET /v1/search/{id}/status`
- `GET /v1/search/{id}/timeline`
- `GET /v1/buscar-results/{id}`
- `GET /v1/search/{id}/results`
- `GET /v1/search/{id}/zero-match`
- `POST /v1/search/{id}/regenerate-excel`
- `POST /v1/search/{id}/cancel`

Nota: `POST /v1/search/{id}/retry` ja tinha `.eq("user_id", user["id"])` no DB query.

### Backend: admin_trace.py (HIGH-SEC-001)

**Arquivo:** `backend/routes/admin_trace.py`

`Depends(require_auth)` trocado por `Depends(require_admin)`. Endpoint `GET /v1/admin/search-trace/{id}` agora exige privilegio de admin.

### Frontend: Open Redirect (HIGH-SEC-002)

**Arquivo:** `frontend/app/api/auth/google/callback/route.ts`

Validacao de `location` header contra whitelist: `smartlic.tech`, `www.smartlic.tech`, `localhost`, `*.railway.app`. Dominios nao reconhecidos sao redirecionados para `/login?error=invalid_redirect`.

### Backend: CB Fail-Open Conservador (HIGH-SEC-003)

**Arquivo:** `backend/quota.py` (linha 842)

Default quando circuit breaker esta aberto e nao ha plano em cache: `smartlic_pro` (1000 req/mes) trocado por `free_trial` (10 req/mes).

### Backend: Email Enumeration (HIGH-SEC-004)

**Arquivo:** `backend/routes/auth_email.py`

Endpoint `GET /v1/auth/status` nao retorna mais `user_id` na resposta. Retorna apenas `confirmed: true/false`.

### Testes

- 5 novos testes IDOR em `test_search_ownership_security.py`
- `test_search_status_enriched.py` adaptado com mock de ownership check
- `test_auth_email.py` atualizado para nova resposta sem user_id
- **89 testes passaram, 0 regressoes**

---

## O que foi feito (Fase 3)

### MED-SEC-001: Trial Multi-Account Abuse — CORRIGIDO

**Solucao aplicada:** Rate limit 3 req/10min per IP via `FlexibleRateLimiter` (Redis + fallback in-memory) nos 4 endpoints de signup:
- `POST /auth/validate-signup-email` — rate limited
- `POST /auth/resend-confirmation` — rate limited
- `GET /auth/check-email` — migrado de rate limit artesanal para `require_rate_limit()`
- `GET /auth/check-phone` — migrado de rate limit artesanal para `require_rate_limit()`

Constante `SIGNUP_RATE_LIMIT_PER_10MIN = 3` (ja definida em `rate_limiter.py`, agora utilizada).
Config env-override: `SIGNUP_RATE_LIMIT_PER_10MIN=N`.

**Futuro:** device fingerprinting + deteccao de padroes (nao implementado nesta fase).

### MED-SEC-002: Grace Period 7→3 dias — CORRIGIDO

`SUBSCRIPTION_GRACE_DAYS` reduzido de 7 para 3 em `backend/quota.py`. Teste `test_grace_days_reduced_to_3()` atualizado.

### MED-SEC-003: Backend Dockerfile Non-Root — CORRIGIDO

User `appuser` (uid 1001) criado no `backend/Dockerfile`. `/tmp/smartlic_cache` com ownership correto. `USER appuser` antes do CMD.

### MED-SEC-004: Dependencias Frontend — ACEITO (RISCO BAIXO)

`npm audit fix` executado. 8 vulnerabilidades restantes sao todas **low severity** em dependencia transitiva dev-only (`@lhci/cli` → `tmp` → symbolic link write). Fix requer `--force` com breaking change no @lhci/cli. Sem risco em producao (pacote nao incluido no bundle).

### MED-SEC-005: SENTRY_AUTH_TOKEN — N/A (JA CORRETO)

Analise confirmou que `SENTRY_AUTH_TOKEN` ja e `ARG` (L66 do frontend Dockerfile), convertido a `ENV` apenas no builder stage (L89). O runner stage final (L114+) nao contem o token — multi-stage build descarta corretamente.

### NOTA: Migration SQL Pendente de Aplicacao

A migration `20260404000000_security_hardening_rpc_rls.sql` foi commitada e pusheada mas ainda precisa ser aplicada ao Supabase producao. Isso acontece automaticamente via CI/CD (`deploy.yml` → `supabase db push --include-all`) no proximo deploy, ou pode ser aplicada manualmente:

```bash
export SUPABASE_ACCESS_TOKEN=<token>
npx supabase db push --include-all
```

---

## Vetores de Ataque Validados como Seguros

| Vetor | Status | Como |
|-------|--------|------|
| Forjar JWT para escalar privilegios | Bloqueado | Assinatura verificada (ES256/HS256), claims sao read-only |
| Modificar plan_type via JWT | Bloqueado | plan_type nunca lido do JWT, sempre do DB |
| Chamar /buscar sem quota | Bloqueado | Atomic RPC + quota check antes do pipeline |
| SSRF via URL no request | Bloqueado | Nenhum HTTP client aceita URL do usuario |
| SQL Injection | Bloqueado | Pydantic valida inputs, queries via RPC parametrizado |
| XSS nos resultados de busca | Bloqueado | React escapa texto por default, sem dangerouslySetInnerHTML |
| Replay de webhook Stripe | Bloqueado | Signature verification + idempotency table |
| Clickjacking | Bloqueado | X-Frame-Options: DENY + CSP frame-src restrito |
| Token cache poisoning | Bloqueado | SHA256 hash do token completo, colisao criptograficamente inviavel |
