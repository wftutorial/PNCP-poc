# STORY-TD-004: Frontend Hardening — Hooks Decomposition e Filtros Salvos

**Story ID:** STORY-TD-004
**Epic:** EPIC-TD-2026
**Phase:** 3 (Hardening)
**Priority:** P1 (TD-050, TD-035) + P2 (TD-037)
**Estimated Hours:** 54h
**Agents:** @dev (implementation), @ux-design-expert (TD-037 UX design), @qa (regression testing)

## Objetivo

Decompor os dois maiores hooks da pagina de busca (useSearchExecution com 852 LOC e useSearchFilters com 607 LOC) em modulos menores e independentes, e implementar a feature de filtros salvos para power users. A pagina de busca e o coracao do produto — 3.775 LOC em 13 hooks acoplados torna qualquer mudanca arriscada e lenta. Apos esta story, nenhum hook tera mais de 400 LOC e o total cairia de 3.775 para < 2.500 linhas.

## Acceptance Criteria

### useSearchExecution Decomposition (TD-050)
- [ ] AC1: `useSearchExecution.ts` decomposto em 3 hooks: `useSearchAPI` (chamadas API + retry), `useSearchErrorHandling` (error states + recovery), `useSearchPartialResults` (SSE + partial data). Nenhum hook > 350 LOC.
- [ ] AC2: Hook original `useSearchExecution` exporta facade que compoe os 3 sub-hooks, mantendo backward compatibility — NENHUM import externo quebrado.
- [ ] AC3: Todos os testes existentes de busca passando sem modificacao de imports (facade pattern).
- [ ] AC4: `wc -l frontend/app/buscar/hooks/useSearchExecution*.ts` mostra total < 900 LOC (vs 852 monolitico, pode crescer levemente com boilerplate de separacao, mas nenhum arquivo individual > 350).

### useSearchFilters Decomposition (TD-035)
- [ ] AC5: `useSearchFilters.ts` decomposto em 5 hooks: `useFilterFormState` (form values), `useFilterValidation` (validation rules), `useFilterPersistence` (localStorage/URL sync), `useFilterAnalytics` (tracking events), `useSectorData` (sector fetching/caching). Nenhum hook > 200 LOC.
- [ ] AC6: Hook original `useSearchFilters` exporta facade que compoe os 5 sub-hooks, mantendo backward compatibility.
- [ ] AC7: Todos os testes existentes de filtros passando sem modificacao.
- [ ] AC8: `wc -l frontend/app/buscar/hooks/useSearchFilters*.ts` mostra total < 650 LOC (nenhum arquivo > 200).

### Saved Filter Presets (TD-037)
- [ ] AC9: Usuario pode salvar configuracao atual de filtros como preset nomeado (max 10 presets por usuario).
- [ ] AC10: Dropdown de presets visivel acima dos filtros na pagina de busca, com opcoes: salvar atual, carregar preset, deletar preset.
- [ ] AC11: Presets persistidos no Supabase (tabela `user_filter_presets` com RLS por user_id).
- [ ] AC12: Preset carregado preenche todos os campos de filtro corretamente (setor, UFs, modalidades, valor, periodo).
- [ ] AC13: Testes E2E cobrindo: salvar preset, carregar preset, deletar preset, limite de 10 presets.

### Quality Gates
- [ ] AC14: `npm test` passa com 0 failures (2681+ tests).
- [ ] AC15: `npm run build` compila sem erros.
- [ ] AC16: Total de linhas nos hooks de busca (`wc -l frontend/app/buscar/hooks/*.ts`) < 2.800 (meta final < 2.500 sera alcancada com TD-051 na Fase 5).

## Tasks

### Phase 3A: useSearchExecution Split (TD-050) — 18h
- [ ] Task 1: Mapear todas as responsabilidades de `useSearchExecution.ts` (API calls, error handling, SSE/partial results, retry logic, analytics).
- [ ] Task 2: Criar `useSearchAPI.ts` — extrair logica de chamada POST /buscar, retry, abort controller, response parsing.
- [ ] Task 3: Criar `useSearchErrorHandling.ts` — extrair error states, error classification (network/timeout/server/quota), recovery actions, user-facing messages.
- [ ] Task 4: Criar `useSearchPartialResults.ts` — extrair SSE connection, partial result accumulation, progress tracking, heartbeat handling.
- [ ] Task 5: Criar facade `useSearchExecution.ts` que importa e compoe os 3 hooks. Manter EXATAMENTE a mesma interface publica (return type, params).
- [ ] Task 6: Rodar todos os testes de busca. Se algum falhar, ajustar facade (NAO os testes).
- [ ] Task 7: Code review — verificar que nenhum hook faz import circular.

### Phase 3B: useSearchFilters Split (TD-035) — 14h (apos TD-050)
- [ ] Task 8: Mapear responsabilidades de `useSearchFilters.ts` (form state, validation, persistence, analytics, sector data).
- [ ] Task 9: Criar `useFilterFormState.ts` — estado do formulario (setor, UFs, modalidades, valor, periodo).
- [ ] Task 10: Criar `useFilterValidation.ts` — regras de validacao (UF obrigatoria, periodo maximo, valor range).
- [ ] Task 11: Criar `useFilterPersistence.ts` — sync com localStorage e URL query params.
- [ ] Task 12: Criar `useFilterAnalytics.ts` — tracking de eventos de filtro (Mixpanel).
- [ ] Task 13: Criar `useSectorData.ts` — fetch de setores, cache, fallback SETORES_FALLBACK.
- [ ] Task 14: Criar facade `useSearchFilters.ts` com mesma interface publica.
- [ ] Task 15: Rodar todos os testes. Ajustar facade se necessario.

### Phase 3C: Saved Filter Presets (TD-037) — 22h (apos TD-035)
- [ ] Task 16: Criar migracao Supabase para tabela `user_filter_presets`:
  ```sql
  CREATE TABLE user_filter_presets (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    name TEXT NOT NULL,
    filters JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(user_id, name)
  );
  ALTER TABLE user_filter_presets ENABLE ROW LEVEL SECURITY;
  CREATE POLICY "Users manage own presets" ON user_filter_presets
    FOR ALL USING (auth.uid() = user_id);
  ```
- [ ] Task 17: Criar API routes: `GET /filter-presets`, `POST /filter-presets`, `DELETE /filter-presets/{id}`.
- [ ] Task 18: Criar hook `useFilterPresets.ts` — CRUD de presets, limite de 10, validacao.
- [ ] Task 19: Criar componente `FilterPresetDropdown` — dropdown com lista de presets, botao salvar, botao deletar.
- [ ] Task 20: Integrar dropdown na pagina de busca, acima do painel de filtros.
- [ ] Task 21: Implementar validacao: limite de 10 presets (mostrar toast se excedido), nome unico por usuario.
- [ ] Task 22: Escrever testes unitarios para hook e componente.
- [ ] Task 23: Escrever teste E2E (Playwright) para fluxo completo: salvar, carregar, deletar.

## Definition of Done

- [ ] Todos os ACs met e verificaveis
- [ ] Frontend tests passing (2681+ tests, 0 failures)
- [ ] Build sem erros (`npm run build`)
- [ ] Nenhum hook > 400 LOC (exceto facade que e thin wrapper)
- [ ] Testes E2E de filtros salvos passando
- [ ] Code reviewed por @architect
- [ ] Migracao de `user_filter_presets` aplicada

## Debt Items Covered

| ID | Item | Hours | Dependencias |
|----|------|-------|-------------|
| TD-050 | useSearchExecution 852 LOC -> 3 hooks | 18 | Nenhuma (executar primeiro) |
| TD-035 | useSearchFilters 607 LOC -> 5 hooks | 14 | TD-050 (shared patterns) |
| TD-037 | Saved filter presets feature | 22 | TD-035 (cleaner hook surface) |
| | **Total** | **54h** | |

## Notas Tecnicas

- **Ordem obrigatoria:** TD-050 -> TD-035 -> TD-037. O TD-050 estabelece o padrao de decomposicao (facade + sub-hooks) que TD-035 replica. TD-037 depende da superficie limpa de TD-035 para integrar presets com o form state.
- **Facade pattern:** O hook original exporta exatamente a mesma interface. Consumidores nao precisam mudar imports. Novos consumidores podem importar sub-hooks diretamente para uso mais granular.
- **TD-037 e a unica feature nova neste epic:** Justificada porque (1) foi solicitada por consultorias, (2) depende da decomposicao de hooks, e (3) tem valor direto de usuario. Presets sao salvos em JSONB, permitindo evolucao do schema de filtros sem migracao.
- **Risco principal:** Import cycles entre sub-hooks. Mitigacao: cada sub-hook recebe dados via parametros, nunca importa outro sub-hook diretamente. A composicao acontece apenas no facade.

---

*Story criada em 2026-04-08 por @pm (Morgan). Fase 3 do EPIC-TD-2026.*
