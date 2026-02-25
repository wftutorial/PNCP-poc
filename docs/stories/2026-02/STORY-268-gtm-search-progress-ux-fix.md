# STORY-268: Fix Search Progress UX — Progress Bar + Error Consolidation

**GTM Audit Ref:** B2 (BLOCKER) + B3 (BLOCKER) + H5 + H6 + H7 + M3 + M7
**Priority:** P0 — BLOCKER for GTM
**Effort:** 3 days
**Squad:** @dev + @ux-design-expert + @qa
**Source:** `docs/audits/gtm-validation-2026-02-25.md`

## Context

The GTM validation audit (screenshots 03-05 in `gtm-audit/`) revealed that the core search flow — the product's primary value delivery — has critical UX failures that WILL cause first-time trial users to leave:

1. **Progress bar stuck at 10% for 90+ seconds** even when 20/27 UFs have completed
2. **Two overlapping error messages** on search failure (red error box + grey "fontes indisponíveis" card)
3. **"Tentar novamente" button is red** (signals danger, not action)
4. **"Indisponível" states (red X)** have no explanation or per-state retry
5. **Default search is "Todo o Brasil" (27 UFs)** — maximizes wait time for first-time users
6. **Motivational banner says "só mais um instante!"** after 84 seconds — dishonest

These are confirmed by Sentry data: `AllSourcesFailedError` (3 events, regressed) and `WORKER TIMEOUT` (5 events) in last 14 days.

## Acceptance Criteria

### AC1: Progress Bar Reflects Real Per-UF Completion (BLOCKER)
- [ ] Progress bar percentage = (completed UFs / total UFs) × 100
- [ ] When 20/27 UFs are done, progress shows ~74%, NOT 10%
- [ ] Progress bar updates in real-time as each UF SSE event arrives
- [ ] Step labels ("Buscando dados", "Filtrando", etc.) advance based on actual pipeline phase
- [ ] **File:** `frontend/app/buscar/page.tsx` (search progress tracking)
- [ ] **File:** `frontend/app/buscar/components/SearchResults.tsx` or progress component

### AC2: Single Consolidated Error Message (BLOCKER)
- [ ] On search failure, show ONE error message (not two overlapping)
- [ ] Error message structure:
  - Title: "Busca não completada" (not "Não foi possível obter os resultados")
  - Body: Clear reason (e.g., "As fontes de dados governamentais estão temporariamente lentas. X de Y estados retornaram dados.")
  - Primary CTA: "Tentar novamente" in **brand blue** (NOT red)
  - Secondary: "Buscar com menos estados" as text link
  - Collapsed: "Detalhes técnicos" (keeps existing)
- [ ] Remove the separate grey "Fontes temporariamente indisponíveis" card
- [ ] If partial data exists (some UFs returned), show it with a yellow banner: "Resultados parciais — X estados responderam"
- [ ] **File:** `frontend/app/buscar/page.tsx` (error rendering logic)

### AC3: "Indisponível" States Get Explanation Tooltip
- [ ] Each UF showing "Indisponível" (red X) shows tooltip on hover/tap:
  "Fonte de dados temporariamente fora do ar para [UF]. Os resultados dos demais estados estão disponíveis."
- [ ] Optional: "Tentar [UF] novamente" link per-state (deferred if complex)
- [ ] **File:** UF Progress Grid component

### AC4: Default Search Scope = Onboarding UFs
- [ ] First-time users: default to UFs selected during onboarding (not "Todo o Brasil")
- [ ] If no onboarding UFs stored: default to user's profile UFs
- [ ] Fallback: "Todo o Brasil" only if no profile context exists
- [ ] Show clear indicator: "Buscando em SP, RJ, MG (seu perfil)" with "Alterar" link
- [ ] **File:** `frontend/app/buscar/page.tsx` (default UF selection)

### AC5: Remove Dishonest Motivational Banner
- [ ] Remove "Estamos trabalhando nisso, só mais um instante!" after 60+ seconds
- [ ] Replace with factual: "Finalizando coleta — X de Y estados processados"
- [ ] After 90s: "Busca demorou mais que o esperado. Você pode aguardar ou cancelar."
- [ ] **File:** `frontend/app/buscar/components/` (motivational banner)

### AC6: Retry Button in Brand Blue
- [ ] "Tentar novamente" button uses primary brand color (blue/navy), NOT red
- [ ] Red is reserved for destructive actions (cancelar, excluir)
- [ ] **File:** Search error state component

## Testing Strategy

- [ ] Unit tests: progress bar calculation with mock UF events (0/27, 13/27, 27/27)
- [ ] Unit tests: single error message rendering (no duplicate)
- [ ] Unit tests: tooltip on "Indisponível" state
- [ ] Unit tests: default UF from onboarding context
- [ ] E2E (Playwright): search with 3 UFs → progress bar advances to 100%
- [ ] E2E (Playwright): simulated failure → single error message → blue retry button
- [ ] Regression: all existing search tests pass (baseline: 3,473 FE pass)

## Files to Modify

| File | Change |
|------|--------|
| `frontend/app/buscar/page.tsx` | Progress calculation, default UFs, error rendering |
| `frontend/app/buscar/components/SearchResults.tsx` | Progress bar percentage source |
| `frontend/app/buscar/components/UfProgressGrid.tsx` | Tooltip on "Indisponível" |
| `frontend/app/buscar/components/ErrorDetail.tsx` | Consolidate error messages |
| `frontend/hooks/useSearch.ts` | Progress calculation from SSE events |
| `frontend/__tests__/` | New tests for all ACs |

## Dependencies

- None (pure frontend)

## Risk

- Progress bar calculation may need backend SSE event data that currently doesn't include a clear "phase" indicator — may need to add `phase: "collecting" | "filtering" | "analyzing"` to SSE events (backend change)
