# DEBT-119: Frontend Polish — Hex Colors, localStorage, Icons, A11y

**Prioridade:** POST-GTM
**Estimativa:** 15h
**Fonte:** Brownfield Discovery — @ux (FE-TD-008, FE-008, FE-009, FE-A11Y-01, FE-A11Y-03)
**Score Impact:** UX 9→9.5

## Contexto
5 items de polish frontend: 96 raw hex colors que deveriam usar Tailwind tokens, 6 arquivos usando raw localStorage sem safe wrappers, inline SVGs em conta/layout.tsx, loading spinners sem role="status", SVGs sem aria-hidden.

## Acceptance Criteria

### Hex Colors → Tailwind Tokens (6h)
- [ ] AC1: Auditar 96 raw hex colors em 20 TSX files
- [ ] AC2: Excluir ThemeProvider.tsx (hex colors corretos — definem CSS variables)
- [ ] AC3: Excluir social button colors (Google blue, GitHub black) — manter como constantes
- [ ] AC4: Substituir demais hex colors por Tailwind tokens ou var(--*) references
- [ ] AC5: Sem mudanças visuais (verificar visualmente páginas afetadas)

### localStorage Safe Wrappers (3h)
- [ ] AC6: Identificar 6 arquivos com raw localStorage.getItem/setItem
- [ ] AC7: Substituir por safeGetItem/safeSetItem de lib/storage.ts
- [ ] AC8: Testes existentes passam

### Inline SVGs → Lucide (4h)
- [ ] AC9: Substituir 5 inline SVGs em conta/layout.tsx por Lucide React icons
- [ ] AC10: Adicionar aria-hidden="true" aos novos ícones (decorativos)

### A11y Quick Wins (2h)
- [ ] AC11: Adicionar role="status" em loading spinners faltantes (login page, auth callback)
- [ ] AC12: Adicionar aria-hidden="true" em SVGs decorativos em planos/page.tsx
- [ ] AC13: npm test passa, 0 regressions

## File List
- [ ] Various TSX files (EDIT — hex → tokens)
- [ ] `app/buscar/hooks/useSearchFilters.ts` (EDIT — safe wrappers)
- [ ] `app/buscar/components/SearchResults.tsx` (EDIT — safe wrappers)
- [ ] `app/layout.tsx` (EDIT — safe wrappers)
- [ ] `app/components/GoogleAnalytics.tsx` (EDIT — safe wrappers)
- [ ] `app/conta/layout.tsx` (EDIT — Lucide icons + aria-hidden)
- [ ] `app/planos/page.tsx` (EDIT — aria-hidden on SVGs)
- [ ] `app/login/page.tsx` (EDIT — role="status")
