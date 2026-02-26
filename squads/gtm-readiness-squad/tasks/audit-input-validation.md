---
task: "Audit Input Validation"
responsavel: "@security-auditor"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - backend/schemas.py
  - backend/routes/*.py
  - frontend form components
Saida: |
  - Input validation coverage report
  - SQL injection risk assessment
  - XSS risk assessment
Checklist:
  - "[ ] All API inputs use Pydantic models"
  - "[ ] Date params have pattern validation"
  - "[ ] UF params validated against known list"
  - "[ ] No raw SQL queries"
  - "[ ] React escaping protects against XSS"
  - "[ ] File upload validation (if applicable)"
---

# *audit-validation

Review input validation across backend and frontend.

## Steps

1. Read `backend/schemas.py` — check Pydantic models
2. Grep for raw SQL or string interpolation in queries
3. Check route handlers for unvalidated inputs
4. Check frontend forms for client-side validation
5. Look for file upload endpoints and their validation

## Output

Score (0-10) + validation gaps + recommendations
