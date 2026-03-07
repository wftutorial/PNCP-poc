# DEBT-005: Frontend Code Hygiene & Quarantine Resolution

**Sprint:** 1
**Effort:** 12.5h
**Priority:** MEDIUM
**Agent:** @dev + @qa (Quinn)

## Context

Multiple small code hygiene issues accumulate to create an unprofessional impression and reduce developer confidence. A Windows artifact file (`nul`) exists in the app directory. Console statements leak to production. A duplicated EmptyState component creates confusion. Brand colors are wrong in the global error page. The SearchErrorBoundary uses red (violating the "never red" guideline). Most importantly, 22 quarantined tests reduce confidence in the test suite and block frontend decomposition work in Sprint 2 (DEBT-011 depends on FE-026 resolution).

## Scope

| ID | Debito | Horas |
|----|--------|-------|
| FE-015 | Windows artifact file `nul` in app directory (0 bytes) | 0.5h |
| FE-009 | Console statements in production (buscar/page.tsx, auth/callback, AuthProvider) | 1h |
| FE-011 | EmptyState duplicated in 2 locations | 1h |
| FE-017 | `global-error.tsx` uses wrong brand colors (`#2563eb`/`#1e3a5f` vs `#116dff`/`#0a1e3f`) | 0.5h |
| FE-013 | SearchErrorBoundary uses hardcoded red — violates "never red" guideline | 1h |
| FE-026 | 22 quarantined tests — prerequisite for Sprint 2 decomposition | 8h |

## Tasks

### Quick Fixes (FE-015, FE-009, FE-011, FE-017, FE-013) — 4h

- [ ] Delete `frontend/app/nul` (Windows artifact, 0 bytes) (FE-015)
- [ ] Remove `console.log`/`console.warn`/`console.error` from production code: buscar/page.tsx (GTM-010 trial), auth/callback, AuthProvider (FE-009)
- [ ] Delete `app/components/EmptyState.tsx`; update all imports to use `components/EmptyState.tsx` as canonical (FE-011)
- [ ] Fix `global-error.tsx`: replace `#2563eb`/`#1e3a5f` with `#116dff`/`#0a1e3f` (SmartLic brand tokens) (FE-017)
- [ ] Fix SearchErrorBoundary: replace red class references (9 instances) with blue/amber per error-messages.ts conventions (FE-013)

### Quarantine Resolution (FE-026) — 8h

- [ ] Inventory all 22 quarantined tests: AuthProvider, ContaPage, DashboardPage, MensagensPage, useSearch, useSearchFilters, 4 free-user flow tests, GoogleSheetsExportButton, download-route, oauth-callback, + 10 others
- [ ] Diagnose root cause for each group (likely jsdom limitations, not real bugs)
- [ ] Fix or properly skip with documented reason for each test
- [ ] Target: 0 quarantined tests remaining
- [ ] If any test is genuinely unfixable in jsdom, document explicitly with `test.skip` + comment explaining why

## Acceptance Criteria

- [ ] AC1: `frontend/app/nul` file does not exist
- [ ] AC2: Zero `console.log`/`console.warn` in production code (grep verification)
- [ ] AC3: Only one EmptyState component exists (`components/EmptyState.tsx`)
- [ ] AC4: `global-error.tsx` uses `#116dff` and `#0a1e3f` (SmartLic brand colors)
- [ ] AC5: SearchErrorBoundary uses zero red class references
- [ ] AC6: 0 quarantined tests (all either fixed or explicitly documented as skipped)
- [ ] AC7: Frontend test count increases to 2700+ (quarantine resolution adds tests back)
- [ ] AC8: Zero regressions

## Tests Required

- Verify all previously quarantined tests pass (or have documented skip reason)
- Snapshot test for global-error.tsx with correct brand colors
- Import resolution test: no remaining imports from `app/components/EmptyState`
- ESLint rule or grep check: no console statements in non-test files

## Definition of Done

- [ ] All tasks complete
- [ ] Tests passing (frontend 2700+ / 0 fail — increased from quarantine resolution)
- [ ] No regressions
- [ ] Code reviewed
- [ ] grep confirms zero console statements in production code
