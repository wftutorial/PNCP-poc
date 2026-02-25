# GTM-FIX-042 — Badge de Urgência Mostra Dias Negativos para Licitações Expiradas

**Status:** Open
**Priority:** P2 — Medium (informação confusa, não impede uso)
**Severity:** Frontend — cálculo de dias restantes não trata datas passadas
**Created:** 2026-02-25
**Sprint:** GTM Stabilization
**Relates to:** GTM-STAB-005 (filter zero results UX)
**Found:** Playwright E2E validation 2026-02-25

---

## Problema

Cards de licitações exibem badges de urgência com **dias negativos**:

```
"⚠️ Prefeitura Municipal de Franca: encerra em -21 dia(s) — ação imediata necessária"
"⚠️ Câmara Municipal de Santa Teresa: encerra em -1 dia(s)"
"Urgente: 25/02/2026 (0d)"
```

### Impacto:

- "-21 dias" é confuso — o usuário não entende que a licitação já encerrou
- Licitações expiradas não deveriam ter badge "Urgente" nem "ação imediata"
- Polui resultados com oportunidades que não podem mais receber propostas
- Reduz confiança: "por que o sistema me mostra licitações encerradas?"

### Causa raiz provável:

1. **Backend:** O filtro de status "Abertas" pode não estar funcionando corretamente para PCP v2 (onde status_inference é client-side)
2. **Frontend:** O cálculo de dias restantes (`dataEncerramentoProposta - now`) não trata resultado negativo
3. **Backend AI summary:** `gerar_resumo_fallback()` gera alertas sem verificar se a data já passou

---

## Acceptance Criteria

### AC1: Frontend — tratar dias negativos no badge
- [ ] Quando dias restantes < 0: exibir "Encerrada" em cinza (não "Urgente" em vermelho)
- [ ] Quando dias restantes = 0: exibir "Último dia" em vermelho
- [ ] Quando dias restantes = 1: exibir "Amanhã" em laranja
- [ ] Quando dias restantes > 1: exibir "X dias" com gradiente de cor

### AC2: Backend — filtrar licitações expiradas
- [ ] Verificar se `status_inference.py` está corretamente marcando licitações com `dataEncerramentoProposta` passada
- [ ] No filtro pipeline: rejeitar licitações onde data de encerramento < hoje (quando status = "Abertas")
- [ ] PCP v2: client-side filter deve checar data de encerramento

### AC3: Backend — AI summary não alertar sobre expiradas
- [ ] `gerar_resumo_fallback()` — não incluir licitações com data passada nos alertas "ação imediata"
- [ ] Se todas as licitações estão expiradas, não gerar seção de alertas

### AC4: Testes
- [ ] Frontend: test badge com dias negativos → mostra "Encerrada"
- [ ] Frontend: test badge com 0 dias → mostra "Último dia"
- [ ] Backend: test filtro rejeita licitações com data passada quando modo "Abertas"

---

## Arquivos Envolvidos

| Arquivo | Ação |
|---------|------|
| `frontend/app/buscar/components/SearchResults.tsx` | AC1: lógica de badge |
| `backend/status_inference.py` | AC2: verificar date-based filtering |
| `backend/filter.py` | AC2: rejeitar expiradas |
| `backend/search_pipeline.py` | AC3: gerar_resumo_fallback() sem expiradas |

---

## Estimativa
- **Esforço:** 3-4h
- **Risco:** Baixo-Médio (filtro de data pode impactar contagem de resultados)
- **Squad:** @dev (frontend + backend) + @qa (testes)
