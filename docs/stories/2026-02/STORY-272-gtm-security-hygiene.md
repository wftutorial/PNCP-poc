# STORY-272: Security Hygiene — Passwords, CVEs, ToS

**GTM Audit Ref:** H2 (ToS phantom plans) + H8 (CVEs) + H11 (hardcoded passwords) + M17 (Mercado Pago)
**Priority:** P1
**Effort:** 1 day
**Squad:** @dev + @devops
**Source:** `docs/audits/gtm-validation-2026-02-25.md`, Track F + Track E

## Context

The security audit (Track F, score 8.9/10) found one HIGH and several MEDIUM items that must be fixed before GTM. These are all quick fixes.

## Acceptance Criteria

### AC1: Rotate Hardcoded Passwords (F-SEC-001 — HIGH)
- [ ] Immediately rotate passwords for:
  - `tiago.sasaki@gmail.com` (admin)
  - `marinalvabaron@gmail.com` (master)
- [x] Update `backend/seed_users.py` to read credentials from env vars or interactive prompt
- [x] Remove hardcoded passwords from source code (seed_users.py, CLAUDE.md, DEPLOYMENT-STATUS.md)
- [ ] Note: passwords remain in git history — consider BFG Repo-Cleaner for future cleanup
- [x] Update CLAUDE.md test credentials section if needed

### AC2: Update Starlette + python-multipart (H8)
- [x] Update `starlette` from 0.45.3 to >=0.47.2 (2 CVEs) — already at 0.52.1 (STORY-279)
- [x] Update `python-multipart` from 0.0.20 to >=0.0.22 (1 CVE) — already >=0.0.22 (STORY-279)
- [x] Update `cryptography` from 43.0.3 to >=46.0.5 (1 CVE) — already >=46.0.5 (STORY-279)
- [x] Run full backend test suite after updates — 5,732 passed (2 pre-existing failures unrelated to deps)
- [x] **File:** `backend/requirements.txt`

### AC3: Fix Terms of Service Phantom Plans (E-HIGH-001)
- [x] Section 3.2 of `/termos` references plans that DON'T EXIST:
  - "Free: 5 buscas/mês" (doesn't exist)
  - "Professional: buscas ilimitadas" (doesn't exist)
  - "Enterprise: API access, white-label, SLA 24/7" (doesn't exist)
- [x] Rewrite section 3.2 to reflect actual plan structure:
  - Período de avaliação: 7 dias de acesso completo
  - SmartLic Pro: acesso completo, R$1.999/mês
- [x] Also fixed: Section 6.1 removed "Mercado Pago" reference
- [x] Also fixed: Section 6.3 removed phantom "plano Free" downgrade reference
- [x] **File:** `frontend/app/termos/page.tsx`

### AC4: Fix Privacy Policy Mercado Pago Reference (M17)
- [x] Remove "Mercado Pago" from privacy policy (only Stripe is implemented)
- [x] Fixed in 2 locations: section 2.1 (line 45) and section 4 (line 90)
- [x] **File:** `frontend/app/privacidade/page.tsx`

### AC5: Run npm audit fix
- [x] Fix 2 frontend npm vulnerabilities (ajv ReDoS + minimatch ReDoS)
- [x] `cd frontend && npm audit fix` — resolved ajv, minimatch, basic-ftp, qs, rollup
- [x] 4 remaining low-severity vulns in `tmp` (requires `--force` breaking change to @lhci/cli — not worth it)
- [x] Verify frontend tests still pass — 3,372 passed, 0 failures

## Testing Strategy

- [x] Backend: `pytest` full suite — 5,732 passed, 2 pre-existing failures (co-occurrence + OpenAPI snapshot drift), 10 skipped
- [x] Frontend: `npm test` — 3,372 passed, 0 failures, 170 suites
- [ ] Manual: verify `/termos` page shows correct plan info
- [ ] Manual: verify `/privacidade` page no longer mentions Mercado Pago

## Files Modified

| File | Change | Status |
|------|--------|--------|
| `backend/seed_users.py` | Remove hardcoded passwords → env vars / getpass | Done |
| `backend/requirements.txt` | Already updated by STORY-279 | N/A |
| `frontend/app/termos/page.tsx` | Fix section 3.2 phantom plans + 6.1 Mercado Pago + 6.3 phantom Free | Done |
| `frontend/app/privacidade/page.tsx` | Remove Mercado Pago (2 locations) | Done |
| `frontend/package-lock.json` | npm audit fix (ajv, minimatch, basic-ftp, qs, rollup) | Done |
| `CLAUDE.md` | Remove hardcoded passwords from test credentials | Done |
| `DEPLOYMENT-STATUS.md` | Remove hardcoded passwords from test accounts | Done |

## Dependencies

- AC1: Requires Supabase admin access to change passwords
- AC2: May require FastAPI version bump if starlette >=0.47.2 needs it
