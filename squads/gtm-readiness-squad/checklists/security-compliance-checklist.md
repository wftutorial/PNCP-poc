# Security & Compliance Checklist

Use this checklist for security audit track validation.

## Authentication & Authorization

- [ ] JWT algorithm matches Supabase (ES256)
- [ ] Token expiry enforced (<1h access, <7d refresh)
- [ ] All API routes require authentication (except public)
- [ ] Admin routes check is_admin/is_master role
- [ ] OAuth (Google) callback validated
- [ ] Rate limiting active on auth endpoints
- [ ] Brute force protection (lockout after N failures)

## Data Protection

- [ ] RLS enabled on ALL user-facing tables
- [ ] No cross-user data leakage possible
- [ ] PII sanitized in logs (log_sanitizer.py)
- [ ] Encryption at rest (Supabase default)
- [ ] Encryption in transit (TLS 1.2+)
- [ ] Backup encryption enabled

## Input Validation

- [ ] All inputs via Pydantic (backend)
- [ ] Date format validation (YYYY-MM-DD pattern)
- [ ] UF validation against known list
- [ ] No raw SQL queries anywhere
- [ ] XSS protection (React escaping)
- [ ] CSRF protection (SameSite cookies)
- [ ] File upload validation (if applicable)

## Dependency Security

- [ ] No critical CVEs in Python deps
- [ ] No critical CVEs in Node deps
- [ ] cryptography >= 46.0.5
- [ ] python-multipart patched
- [ ] starlette patched
- [ ] Regular dependency update process

## Secrets Management

- [ ] No secrets in git history
- [ ] .env in .gitignore
- [ ] All keys in env vars (Railway)
- [ ] Stripe webhook secret configured
- [ ] Service role key not exposed to frontend
- [ ] API keys rotation policy defined

## LGPD Compliance

- [ ] Cookie consent dialog functional
- [ ] Privacy policy complete and published
- [ ] Terms of Service accurate (no Mercado Pago)
- [ ] User data deletion mechanism
- [ ] Data retention policy documented
- [ ] Third-party sharing disclosed
- [ ] Data processing records maintained

## Quick Security Check

For rapid validation:
- [ ] Auth endpoint returns 401 without token
- [ ] Admin endpoint returns 403 for non-admin
- [ ] XSS attempt in search query is escaped
- [ ] No secrets in latest 10 commits
