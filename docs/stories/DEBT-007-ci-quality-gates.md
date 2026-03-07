# DEBT-007: CI Quality Gates & Test Infrastructure

**Sprint:** 1
**Effort:** 14h
**Priority:** HIGH
**Agent:** @devops (Gage) + @qa (Quinn)

## Context

The SmartLic CI pipeline lacks several critical quality gates: API contract validation between backend and frontend is not enforced (drift is actively occurring — `openapi_schema.diff.json` is uncommitted in git status), no dependency vulnerability scanning exists for 50+ Python deps and 40+ npm deps (including pinned `cryptography==46.0.5`), the `arq` package is mocked via `sys.modules` hacks causing test pollution, and neither pre-commit hooks nor backend linting are enforced in CI.

CROSS-002 (API contract CI) is a prerequisite for safe frontend refactoring in Sprint 2 and Backlog. CROSS-007 was specifically added by @qa as a gap finding.

## Scope

| ID | Debito | Horas |
|----|--------|-------|
| CROSS-002 | No API contract validation in CI — frontend TypeScript types can diverge from backend OpenAPI schema | 4h |
| CROSS-007 | No dependency vulnerability scanning in CI — no pip-audit, npm audit, or Snyk | 4h |
| CROSS-005 | Test pollution: `sys.modules["arq"]` mock leaks, Supabase CB singleton leak | 2h |
| SYS-031 | `arq` not installed locally — mocked via `sys.modules` in tests | (bundled with CROSS-005) |
| SYS-034 | No pre-commit hooks | 2h |
| SYS-035 | Backend linting (`ruff`, `mypy`) not enforced in CI | 2h |

## Tasks

### API Contract Validation (CROSS-002) — 4h

- [ ] Commit current `openapi_schema.diff.json` as baseline snapshot
- [ ] Add CI step to `.github/workflows/backend-tests.yml`: generate OpenAPI schema, compare against snapshot
- [ ] Fail PR if schema diff is uncommitted (forces explicit acknowledgment of API changes)
- [ ] Add `openapi-diff` or equivalent for semantic comparison (breaking vs non-breaking changes)
- [ ] Document process in PR template: "If this PR changes API, update `openapi_schema.diff.json`"

### Vulnerability Scanning (CROSS-007) — 4h

- [ ] Add `pip-audit` step to `.github/workflows/backend-tests.yml`
- [ ] Add `npm audit --audit-level=high` step to `.github/workflows/frontend-tests.yml`
- [ ] Configure to fail on HIGH+ vulnerabilities (warn on MEDIUM)
- [ ] Create allowlist file for known accepted vulnerabilities (if any)
- [ ] Document vulnerability response process

### Test Infrastructure (CROSS-005, SYS-031) — 2h

- [ ] Install `arq` as dev dependency in `requirements.txt` (pure Python, safe on Windows)
- [ ] Remove all `sys.modules["arq"]` hacks from test files
- [ ] Replace with proper `patch("arq.connections.RedisSettings")` per test
- [ ] Verify Supabase CB autouse fixture in `conftest.py` resets singleton between tests
- [ ] Run full test suite to confirm zero pollution-related failures

### Pre-commit & Linting (SYS-034, SYS-035) — 4h

- [ ] Create `.pre-commit-config.yaml` with ruff, mypy, prettier, eslint hooks
- [ ] Add `ruff check .` step to backend CI (non-blocking initially, blocking after 2 sprints)
- [ ] Add `mypy .` step to backend CI (non-blocking initially)
- [ ] Document setup in README: `pip install pre-commit && pre-commit install`

## Acceptance Criteria

- [ ] AC1: PR that changes API schema without updating snapshot fails CI
- [ ] AC2: `pip-audit` runs in backend CI; `npm audit` runs in frontend CI
- [ ] AC3: CI fails on HIGH+ vulnerability in any dependency
- [ ] AC4: `arq` is in `requirements.txt`; zero `sys.modules["arq"]` in test files
- [ ] AC5: `.pre-commit-config.yaml` exists with ruff + mypy + prettier hooks
- [ ] AC6: `ruff check .` runs in CI (non-blocking)
- [ ] AC7: All backend tests pass without `sys.modules` arq hacks (5774+ pass)
- [ ] AC8: All frontend tests pass (2681+ pass)

## Tests Required

- CI pipeline test: submit PR with API change but no snapshot update — verify failure
- CI pipeline test: introduce known vulnerable dep — verify failure
- Backend test suite: full run without `sys.modules["arq"]` — zero failures
- Pre-commit hook test: verify hooks run on `git commit`

## Definition of Done

- [ ] All tasks complete
- [ ] CI workflows updated and verified on a test PR
- [ ] Tests passing (backend 5774+ / frontend 2681+ / 0 fail)
- [ ] No regressions
- [ ] Code reviewed
