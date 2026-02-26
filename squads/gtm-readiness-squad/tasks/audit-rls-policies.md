---
task: "Audit RLS Policies"
responsavel: "@security-auditor"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - Supabase migrations (supabase/migrations/)
  - Database schema
Saida: |
  - RLS coverage report
  - Cross-user access test results
  - Policy gaps identified
Checklist:
  - "[ ] RLS enabled on all user-facing tables"
  - "[ ] profiles: user can only read/update own"
  - "[ ] searches: user-scoped"
  - "[ ] pipeline_items: user-scoped"
  - "[ ] feedback: user-scoped writes"
  - "[ ] No public tables without RLS"
---

# *audit-rls

Verify Row-Level Security policies on all database tables.

## Steps

1. List all tables from migrations
2. For each table, check if RLS is enabled
3. For user-facing tables, verify policies enforce user_id scoping
4. Check admin tables have admin-only access
5. Look for any tables missing RLS entirely

## Output

Score (0-10) + coverage report + gaps found
