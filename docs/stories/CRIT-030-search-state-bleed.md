# CRIT-030 — Busca: State Bleed entre Consultas Consecutivas

**Severity:** P1 — Blocker
**Origin:** UX Production Audit 2026-02-23 (Bug #2)
**Parent:** CRIT-027
**Status:** [ ] Pending

---

## Problema

Ao iniciar uma nova busca com setor diferente, o empty state da busca anterior permanece visível simultaneamente com o progresso da nova busca. O resultado antigo ("Analisamos 302 editais e nenhum correspondeu...") contamina a tela enquanto o grid de UFs da nova busca aparece acima.

**Comportamento observado:**
1. Buscar "Vestuário" → retorna 0 resultados com empty state
2. Trocar para "Engenharia" e buscar → UF grid aparece (nova busca)
3. Abaixo do grid, o empty state de Vestuário ("302 editais") permanece visível
4. Após UF grid desaparecer, empty state antigo continua

**Comportamento esperado:**
1. Ao iniciar nova busca, todo conteúdo anterior (results, empty state, banners) deve ser limpo
2. Apenas o loading/progress da nova busca deve ser visível

## Root Cause Provável

CRIT-027 adicionou `!loading` guards a 6 rendering blocks, mas o bloco de empty state (`SearchResults` quando `result.licitacoes.length === 0`) pode não ter o guard `!loading`, ou o `result` não é resetado para `null` antes do novo POST disparar.

Sequência de estado:
```
Busca 1: result={licitacoes:[]} → mostra empty state
Busca 2 inicia: loading=true, mas result ainda é {licitacoes:[]}
→ O empty state persiste porque result não é null (é um objeto com array vazio)
```

A correção de CRIT-027 reseta `result` para `null`, mas pode ser que o POST da busca 2 retorne tão rápido (cache) que `result` receba o novo valor (também empty) antes do loading guard ter efeito.

## Acceptance Criteria

- [ ] **AC1**: Ao clicar "Buscar", todo conteúdo de resultado anterior (cards, empty state, summary) desaparece imediatamente
- [ ] **AC2**: Durante loading, apenas o progress/loading component é visível (UF grid, progress bar, skeleton)
- [ ] **AC3**: O empty state só renderiza quando `!loading && result && result.licitacoes.length === 0`
- [ ] **AC4**: O "Atualizando dados em tempo real..." banner desaparece quando a busca conclui (com ou sem resultados)
- [ ] **AC5**: Teste: buscar setor A → buscar setor B → empty state de A não aparece durante loading de B
- [ ] **AC6**: Teste: empty state com "302 editais" não persiste após nova busca
- [ ] **AC7**: Zero regressão no baseline

## Arquivos Prováveis

- `frontend/app/buscar/page.tsx` — `buscar()` function, state resets
- `frontend/app/buscar/components/SearchResults.tsx` — rendering guards
- `frontend/hooks/useSearch.ts` — state management
- `frontend/__tests__/buscar/search-state-machine.test.tsx`

## Referência

- Screenshot: `audit-07-engenharia-30s.jpeg` (state bleed visível)
- Audit doc: `docs/sessions/2026-02/2026-02-23-ux-production-audit.md`
