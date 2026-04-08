# DEBT-06: Search Hooks Refactor (3775 LOC -> <2500 LOC)

**Epic:** EPIC-TD-2026
**Fase:** 3 (Hardening)
**Horas:** 54h
**Agente:** @dev + @ux-design-expert
**Prioridade:** P1-P2

## Debitos Cobertos

| TD | Item | Horas |
|----|------|-------|
| TD-050 | useSearchExecution.ts 852 LOC -> 3 hooks (API, ErrorHandling, PartialResults) | 18h |
| TD-035 | useSearchFilters 607 LOC -> 5 hooks (FormState, Validation, Persistence, Analytics, SectorData) | 14h |
| TD-037 | Saved filter presets (Supabase table + dropdown UX + 10 preset limit) | 22h |

## Acceptance Criteria

- [ ] AC1: useSearchExecution splitado em useSearchAPI + useSearchErrorHandling + useSearchPartialResults
- [ ] AC2: useSearchFilters splitado em 5 hooks com responsabilidade unica
- [ ] AC3: Total de LOC em `frontend/app/buscar/hooks/` < 2500 (de 3775)
- [ ] AC4: Saved filter presets funcional com persistencia Supabase
- [ ] AC5: Zero regressao — todos os testes existentes passando
- [ ] AC6: `wc -l frontend/app/buscar/hooks/*.ts` < 2500

## Ordem de Execucao (OBRIGATORIA)

1. TD-050 primeiro (patterns compartilhados)
2. TD-035 depois (usa patterns de TD-050)
3. TD-037 por ultimo (depende de hooks limpos)
