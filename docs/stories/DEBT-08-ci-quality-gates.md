# DEBT-08: CI Quality Gates (Deps + A11y + Visual)

**Epic:** EPIC-TD-2026
**Fase:** 4 (Polish)
**Horas:** 36h
**Agente:** @devops + @qa
**Prioridade:** P2

## Debitos Cobertos

| TD | Item | Horas |
|----|------|-------|
| TD-058 | pip-audit + npm audit no CI (dependency vulnerability scanning) | 4h |
| TD-056 | jest-axe para top 10 components (a11y automated testing) | 14h |
| TD-036 | Chromatic visual regression (10 critical screens) | 18h |

## Acceptance Criteria

- [x] AC1: GitHub Actions workflow com `pip-audit` + `npm audit` — 0 high/critical = gate
- [x] AC2: jest-axe rodando em 10 componentes criticos (SearchResults, ResultCard, PricingCard, LoginForm, etc.)
- [x] AC3: Chromatic configurado com 10 screenshots de referencia
- [x] AC4: PRs bloqueados se dep scan ou a11y falhar
- [x] AC5: Visual diff review disponivel em PRs

## Notas

Podem rodar em paralelo. TD-058 e o mais rapido (4h) — comecar por ele.
