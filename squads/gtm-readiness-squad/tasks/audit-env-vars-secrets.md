---
task: "Audit Environment Variables & Secrets"
responsavel: "@infra-auditor"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - .env.example
  - backend/config.py
  - Railway env vars (via `railway variables`)
Saida: |
  - Env var completeness check
  - Secrets hygiene report
  - Missing/misconfigured vars list
Checklist:
  - "[ ] All .env.example vars present in Railway"
  - "[ ] No secrets in git (grep for sk_, key=, password)"
  - "[ ] OPENAI_API_KEY valid"
  - "[ ] STRIPE_SECRET_KEY is live mode"
  - "[ ] SUPABASE_SERVICE_ROLE_KEY present"
  - "[ ] SENTRY_DSN configured"
  - "[ ] Feature flags set correctly"
---

# *audit-env

Check environment variable completeness and secrets hygiene.

## Steps

1. Read `.env.example` — list all documented vars
2. Read `backend/config.py` — list all vars loaded with defaults
3. Compare against Railway vars (if accessible)
4. Grep codebase for hardcoded secrets
5. Verify critical vars: OPENAI_API_KEY, STRIPE_*, SUPABASE_*

## Output

Score (0-10) + findings list + recommendations
