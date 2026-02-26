---
task: "Audit Supabase Health"
responsavel: "@infra-auditor"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - Supabase project ref (fqqyovlzdzimiwfofdjk)
  - supabase/migrations/ directory
  - backend/auth.py
Saida: |
  - Supabase health assessment
  - Migration drift check
  - RLS coverage report
Checklist:
  - "[ ] Count local vs remote migrations"
  - "[ ] Check for migration drift"
  - "[ ] Verify JWT signing algorithm"
  - "[ ] Check connection pooling config"
  - "[ ] Verify backup schedule"
  - "[ ] Check database size and growth"
---

# *audit-supabase

Check Supabase health, migrations, and configuration.

## Steps

1. Count migrations in `supabase/migrations/` directory
2. Run `npx supabase db diff` to check for schema drift
3. Read `backend/auth.py` — check JWT algorithm handling
4. Verify RLS policies via Supabase dashboard or CLI
5. Check Supabase project health

## Key Validations

- All local migrations applied to production
- No schema drift between local and remote
- JWT algorithm matches (ES256 if Supabase rotated)
- Connection pooling enabled (pgBouncer)
- Point-in-time recovery configured

## Output

Score (0-10) + findings list + recommendations
