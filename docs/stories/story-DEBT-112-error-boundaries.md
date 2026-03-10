# DEBT-112: Error Boundaries em Páginas Autenticadas

**Prioridade:** GTM-BLOCKER
**Estimativa:** 4h
**Fonte:** Brownfield Discovery — @ux-design-expert (FE-NEW-03)
**Score Impact:** UX 8→9

## Contexto
Apenas `/buscar` tem `SearchErrorBoundary`. Dashboard, pipeline e historico usam apenas `error.tsx` (Next.js), que perde todo o estado da página (scroll, filtros, dados em formulário). Para usuários B2G pagantes, perder estado do pipeline em uma exceção é inaceitável.

## Acceptance Criteria

- [ ] AC1: Criar `PageErrorBoundary` genérico em `components/` que preserva NavigationShell (sidebar/bottom nav funcional)
- [ ] AC2: Wrap `/dashboard` page content com PageErrorBoundary
- [ ] AC3: Wrap `/pipeline` page content com PageErrorBoundary
- [ ] AC4: Wrap `/historico` page content com PageErrorBoundary
- [ ] AC5: ErrorBoundary mostra mensagem contextual ("Erro ao carregar o dashboard/pipeline/histórico")
- [ ] AC6: Botão "Tentar novamente" reseta o error boundary sem reload completo
- [ ] AC7: Sentry reporta o erro com contexto de página
- [ ] AC8: ErrorBoundary NÃO limpa localStorage nem SWR cache
- [ ] AC9: `role="alert" aria-live="assertive"` na UI de erro
- [ ] AC10: Testes unitários para PageErrorBoundary (render, reset, Sentry report)

## File List
- [ ] `components/PageErrorBoundary.tsx` (NEW)
- [ ] `app/dashboard/page.tsx` (EDIT — wrap content)
- [ ] `app/pipeline/page.tsx` (EDIT — wrap content)
- [ ] `app/historico/page.tsx` (EDIT — wrap content)
- [ ] `__tests__/components/PageErrorBoundary.test.tsx` (NEW)
