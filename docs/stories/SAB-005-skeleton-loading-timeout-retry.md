# SAB-005: Skeleton loading permanente sem timeout/retry

**Origem:** UX Premium Audit P1-02
**Prioridade:** P1 — Alto
**Complexidade:** M (Medium)
**Sprint:** SAB-P1
**Owner:** @dev
**Screenshots:** `ux-audit/18-busca-results-loading.png` → `ux-audit/21-busca-stuck-backend-done.png`

---

## Problema

Skeleton cards de resultado aparecem durante o loading da busca mas nunca são substituídos por resultados reais (vinculado ao SAB-001). Não há timeout nem fallback — fica em skeleton infinitamente.

**Esperado:** Após 30s sem dados novos, mostrar mensagem "Resultados demorando mais que o esperado" com botão de retry.

---

## Critérios de Aceite

### Timeout Defensivo

- [ ] **AC1:** Se skeletons visíveis por > 30s sem atualização de dados, exibir banner: "A busca está demorando mais que o esperado"
- [ ] **AC2:** Banner inclui botão "Tentar novamente" que re-executa a busca com mesmos parâmetros
- [ ] **AC3:** Banner inclui link secundário "Ver buscas anteriores" → `/historico`

### Busca sem Resultados

- [ ] **AC4:** Se `POST /buscar` retorna `resultados: []` (0 resultados), exibir empty state imediatamente (não skeleton)
- [ ] **AC5:** Empty state mostra: "Nenhuma licitação encontrada para [setor] em [UFs]. Tente ampliar o período ou os estados."

### Erro de Rede

- [ ] **AC6:** Se `POST /buscar` falha (network error, 5xx), exibir mensagem de erro com retry em vez de skeleton infinito
- [ ] **AC7:** Máximo 3 retries automáticos com backoff (já existe em `useSearch`? Verificar e alinhar)

### Testes

- [ ] **AC8:** Teste: mock POST que nunca resolve → após 30s aparece banner de timeout
- [ ] **AC9:** Teste: POST retorna `resultados: []` → empty state imediato

---

## Arquivos Prováveis

- `frontend/hooks/useSearch.ts` — lógica de timeout
- `frontend/app/buscar/page.tsx` — renderização condicional skeleton vs timeout vs results
- `frontend/components/SearchResults.tsx` — empty state

## Dependência

- SAB-001 (P0-01) — o root cause fix deve ser feito primeiro. SAB-005 é a camada defensiva de UX.
