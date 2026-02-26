---
task: "Audit Secrets Rotation"
responsavel: "@security-auditor"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - backend/seed_users.py
  - .gitignore
  - Git history (for leaked secrets)
Saida: |
  - Secrets hygiene report
  - Leaked secrets in git history
  - Rotation recommendations
Checklist:
  - "[ ] No passwords in seed_users.py"
  - "[ ] .env in .gitignore"
  - "[ ] No API keys in git history"
  - "[ ] Stripe keys rotated if exposed"
  - "[ ] Supabase service role key not in frontend"
---

# *audit-secrets

Check for hardcoded secrets and rotation hygiene.

## Steps

1. Read `backend/seed_users.py` — check for hardcoded passwords
2. Grep codebase for patterns: sk_, password=, secret=, key=
3. Check .gitignore includes .env, *.key, credentials
4. Review STORY-272 (Security Hygiene) completion status
5. Check if any secrets need rotation

## Output

Score (0-10) + leaked secrets list + rotation plan
