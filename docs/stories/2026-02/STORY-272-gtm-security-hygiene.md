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
- [ ] Update `backend/seed_users.py` to read credentials from env vars or interactive prompt
- [ ] Remove hardcoded passwords from source code
- [ ] Note: passwords remain in git history — consider BFG Repo-Cleaner for future cleanup
- [ ] Update CLAUDE.md test credentials section if needed

### AC2: Update Starlette + python-multipart (H8)
- [ ] Update `starlette` from 0.45.3 to >=0.47.2 (2 CVEs)
- [ ] Update `python-multipart` from 0.0.20 to >=0.0.22 (1 CVE)
- [ ] Update `cryptography` from 43.0.3 to >=46.0.5 (1 CVE)
- [ ] Run full backend test suite after updates — must pass
- [ ] **File:** `backend/requirements.txt`

### AC3: Fix Terms of Service Phantom Plans (E-HIGH-001)
- [ ] Section 3.2 of `/termos` references plans that DON'T EXIST:
  - "Free: 5 buscas/mês" (doesn't exist)
  - "Professional: buscas ilimitadas" (doesn't exist)
  - "Enterprise: API access, white-label, SLA 24/7" (doesn't exist)
- [ ] Rewrite section 3.2 to reflect actual plan structure:
  - Período de avaliação: 7 dias de acesso completo
  - SmartLic Pro: acesso completo, R$1.999/mês
  - (Legacy plans if needed)
- [ ] **File:** `frontend/app/termos/page.tsx` (lines ~71-75)

### AC4: Fix Privacy Policy Mercado Pago Reference (M17)
- [ ] Remove "Mercado Pago" from privacy policy (only Stripe is implemented)
- [ ] Or: replace with "processadores de pagamento como Stripe"
- [ ] **File:** `frontend/app/privacidade/page.tsx` (line ~46)

### AC5: Run npm audit fix
- [ ] Fix 2 frontend npm vulnerabilities (ajv ReDoS + minimatch ReDoS)
- [ ] `cd frontend && npm audit fix`
- [ ] Verify frontend tests still pass

## Testing Strategy

- [ ] Backend: `pytest` full suite after dependency updates (baseline: 5,549 pass)
- [ ] Frontend: `npm test` after audit fix (baseline: 3,473 pass)
- [ ] Manual: verify `/termos` page shows correct plan info
- [ ] Manual: verify `/privacidade` page no longer mentions Mercado Pago

## Files to Modify

| File | Change |
|------|--------|
| `backend/seed_users.py` | Remove hardcoded passwords |
| `backend/requirements.txt` | Update starlette, python-multipart, cryptography |
| `frontend/app/termos/page.tsx` | Fix section 3.2 plan references |
| `frontend/app/privacidade/page.tsx` | Remove Mercado Pago |
| `frontend/package-lock.json` | npm audit fix |

## Dependencies

- AC1: Requires Supabase admin access to change passwords
- AC2: May require FastAPI version bump if starlette >=0.47.2 needs it
