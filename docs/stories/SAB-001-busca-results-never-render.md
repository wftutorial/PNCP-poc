# SAB-001: Busca trava em 70% — resultados nunca renderizam

**Origem:** UX Premium Audit P0-01
**Prioridade:** P0 — BLOQUEADOR
**Complexidade:** L (Large)
**Sprint:** SAB-P0 (imediato)
**Owner:** @dev
**Screenshots:** `ux-audit/17-busca-loading.png` → `21-busca-stuck-backend-done.png`

---

## Problema

Ao buscar "Vestuário e Uniformes" em SP (últimos 10 dias), o backend completa em ~14s (logs confirmam `llm_summary_job`, `excel_generation_job`, `bid_analysis_job` concluídos), mas o frontend fica preso em "Filtrando resultados" 70% com skeletons de loading por 145+ segundos. Resultados **nunca** renderizam.

A barra inferior mostra "8 relevantes de 594 analisadas — Filtragem concluída" mas os cards de resultado não aparecem.

**Causa provável:** Desconexão SSE ou race condition entre a resposta principal do `POST /buscar` e os eventos SSE de background jobs (`llm_ready`, `excel_ready`). Possível que o state machine do `useSearch` não transicione para `results` quando recebe a resposta POST.

**Impacto:** Funcionalidade CORE do produto está quebrada. Usuário não consegue ver resultados.

---

## Critérios de Aceite

### Diagnóstico

- [ ] **AC1:** Reproduzir o bug em ambiente de desenvolvimento com busca real (setor Vestuário, UF SP, 10 dias)
- [ ] **AC2:** Instrumentar `useSearch.ts` com console.log em cada transição de estado: `idle → searching → filtering → results/error`
- [ ] **AC3:** Verificar se a resposta do `POST /buscar` chega ao frontend (network tab) e se o JSON contém `resultados[]`

### Root Cause Fix

- [ ] **AC4:** Se race condition SSE vs POST: garantir que o estado `results` é setado quando POST retorna com dados, independente do SSE
- [ ] **AC5:** Se desconexão SSE: verificar que o `EventSource` reconecta ou que o frontend degrada gracefully para time-based progress
- [ ] **AC6:** Se estado do `useSearch` fica preso em `filtering`: adicionar timeout de segurança — após POST retornar com dados, forçar transição para `results` em no máximo 5s

### Validação

- [ ] **AC7:** Busca "Vestuário e Uniformes" SP 10 dias exibe resultados em < 30s
- [ ] **AC8:** Busca com 0 resultados mostra mensagem "Nenhuma licitação encontrada" (não skeleton infinito)
- [ ] **AC9:** Teste unitário cobrindo cenário: POST retorna antes do SSE completar → resultados renderizam

---

## Arquivos Prováveis

- `frontend/app/buscar/page.tsx` — orquestração da busca
- `frontend/hooks/useSearch.ts` — state machine da busca
- `frontend/components/SearchResults.tsx` — renderização de resultados
- `backend/routes/search.py` — endpoint `/buscar` e SSE

## Dependências

- SAB-005 (P1-02) — timeout/retry UX é fix complementar a este
- STORY-329 — progresso granular na filtragem (já concluída, mas pode ter introduzido regressão)

## Notas

- Os logs de backend confirmam que a busca completou com sucesso. O problema é exclusivamente frontend.
- Verificar se STORY-329 (filter progress events) não introduziu regressão na transição filtering→results.
