---
task: "Audit CI/CD Pipeline"
responsavel: "@infra-auditor"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - .github/workflows/ directory
  - backend/pyproject.toml (coverage config)
  - frontend/jest.config.js (coverage config)
Saida: |
  - CI/CD pipeline assessment
  - Quality gate validation
  - Deployment process review
Checklist:
  - "[ ] All workflow files parse correctly"
  - "[ ] backend-tests.yml enforces 70% coverage"
  - "[ ] frontend-tests.yml enforces 60% coverage"
  - "[ ] e2e.yml runs 60 Playwright tests"
  - "[ ] migration-check.yml validates migrations"
  - "[ ] codeql.yml runs security scanning"
  - "[ ] Deploy workflow is functional"
  - "[ ] No workflows failing on main branch"
---

# *audit-cicd

Validate all GitHub Actions workflows and quality gates.

## Steps

1. List all files in `.github/workflows/`
2. Read key workflows: backend-tests, frontend-tests, e2e, deploy
3. Check recent workflow runs via `gh run list`
4. Verify coverage thresholds match documentation
5. Check that blocking workflows actually block merges

## Output

Score (0-10) + findings list + recommendations
