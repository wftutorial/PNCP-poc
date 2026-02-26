---
task: "Audit JWT Authentication"
responsavel: "@security-auditor"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - backend/auth.py
  - backend/authorization.py
  - Supabase JWT config
Saida: |
  - JWT auth assessment
  - Algorithm compatibility check
  - Token validation report
Checklist:
  - "[ ] JWT algorithm matches Supabase (ES256 vs HS256)"
  - "[ ] JWKS or public key configured for ES256"
  - "[ ] Token expiry enforced"
  - "[ ] All protected endpoints require valid token"
  - "[ ] Admin endpoints check role"
  - "[ ] 401 returned cleanly (not stack trace)"
---

# *audit-jwt

Validate JWT authentication chain end-to-end.

## P0 KNOWN BLOCKER

Supabase rotated JWT signing from HS256 to ES256 (~11 days ago). Backend auth.py may still use HS256, causing ALL authenticated requests to return 401.

## Steps

1. Read `backend/auth.py` — check algorithm parameter in jwt.decode()
2. Read `backend/authorization.py` — check require_auth dependency
3. Verify what algorithm Supabase is using (ES256 expected)
4. Test: call `/me` with valid Supabase token — expect 200, not 401
5. Test: call `/me` without token — expect 401

## Fix if broken

Update auth.py to support ES256 via:
- Option A: JWKS endpoint (auto-rotates)
- Option B: Supabase public key (manual rotation)

## Output

Score (0-10) + P0 blocker status + recommendations
