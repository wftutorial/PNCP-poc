# DEBT-123: Make CI Security Scans Blocking
**Priority:** P1
**Effort:** 4-8h
**Owner:** @devops
**Sprint:** Week 1 (phase 1) + Week 2 (phase 2)

## Context

25 instances of `continue-on-error: true` across 8 GitHub Actions workflows make security scans, linting, type checking, and even staging tests non-blocking. A HIGH severity CVE could ship to production undetected. This must be fixed before shipping other code changes to ensure the fix pipeline itself is secure.

## Acceptance Criteria

### Phase 1 — Day 1-2 (security-critical)

- [ ] AC1: `pip-audit` step in `backend-tests.yml` runs blocking (no `continue-on-error`)
- [ ] AC2: `npm audit` step in `frontend-tests.yml` runs blocking (no `continue-on-error`)
- [ ] AC3: Both audits pass locally before enabling in CI (no false-positive blocks)
- [ ] AC4: `--ignore-vuln` used for any accepted known risks (documented in workflow comments)
- [ ] AC5: `staging-deploy.yml` test steps run blocking (remove "TEMP" markers from STORY-165)

### Phase 2 — Week 2 (CI hardening)

- [ ] AC6: `pr-validation.yml` audited — security-relevant steps (at minimum) made blocking
- [ ] AC7: Relationship between `tests.yml` and `backend-tests.yml` clarified (remove duplicate if confirmed)
- [ ] AC8: `codeql.yml` `continue-on-error` removed (CodeQL is security-critical)
- [ ] AC9: Document which `continue-on-error` instances are intentionally kept and why (as inline comments)

## Technical Notes

**Full inventory (from assessment):**

| Workflow | Count | Steps | Security-Relevant |
|----------|-------|-------|-------------------|
| `backend-tests.yml` | 3 | pip-audit, ruff, mypy | YES (pip-audit) |
| `frontend-tests.yml` | 1 | npm audit | YES |
| `pr-validation.yml` | 8 | Multiple validation steps | YES |
| `staging-deploy.yml` | 2 | Tests + coverage (marked "TEMP") | YES |
| `tests.yml` | 5 | Multiple steps | Unclear |
| `deploy.yml` | 2 | Post-deploy checks | MEDIUM |
| `backend-ci.yml` | 1 | 1 step | LOW |
| `codeql.yml` | 1 | CodeQL analysis | YES |
| `load-test.yml` | 2 | Test execution | LOW |

**Before removing `continue-on-error`, run locally:**
```bash
cd backend && pip-audit -r requirements.txt
cd frontend && npm audit --audit-level=high
```

Fix or `--ignore-vuln` any findings before making CI blocking.

**Gotcha:** `ruff` and `mypy` are in `backend-tests.yml` with `continue-on-error`. These are linting, not security. Consider keeping them advisory or fixing all findings first. Do not let linting failures block security PRs.

## Test Requirements

- [ ] PR with a known-vulnerable dep (test branch) is blocked by CI
- [ ] PR with clean deps passes CI
- [ ] Existing PRs are not broken by false positives

## Files to Modify

- `.github/workflows/backend-tests.yml` -- remove `continue-on-error` from pip-audit
- `.github/workflows/frontend-tests.yml` -- remove `continue-on-error` from npm audit
- `.github/workflows/staging-deploy.yml` -- remove `continue-on-error` + TEMP markers
- `.github/workflows/pr-validation.yml` -- audit and selectively remove
- `.github/workflows/codeql.yml` -- remove `continue-on-error`
- `.github/workflows/tests.yml` -- clarify relationship to backend-tests.yml

## Definition of Done

- [ ] Phase 1 ACs pass (pip-audit, npm audit, staging blocking)
- [ ] Phase 2 ACs pass (pr-validation, codeql, tests.yml clarified)
- [ ] No false positives blocking legitimate PRs
- [ ] No regressions in CI
- [ ] Code reviewed
