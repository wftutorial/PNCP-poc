# CRIT-FLT-003 — Valor Zero Distorce Viability Assessment

**Prioridade:** P1 — Falso Sinal de Viabilidade
**Estimativa:** 2h
**Origem:** Auditoria de Pipeline 2026-02-22
**Track:** Backend

## Problema

**25% dos itens PNCP têm `valorTotalEstimado = 0`** (dado real, auditoria 2026-02-22, amostra de 200 itens de SP/MG/RJ).

O Viability Assessment (D-04) calcula o fator `value_fit` (peso 25%) comparando o valor estimado com o `viability_value_range` do setor. Quando `valor = 0`:

```python
# viability.py — _calculate_value_fit()
if valor <= 0:
    return 30  # "sem informação suficiente" → score fixo 30/100
```

### Problema Concreto
- Score fixo de 30 → o fator `value_fit` puxa o score para baixo
- Bid com `valor=0` mas potencialmente altíssimo valor → marcado como "Baixa viabilidade"
- **25% de todos os bids** sofrem essa distorção

### Cenário Real
```
Objeto: "Registro de preços para aquisição de uniformes escolares para rede municipal"
Valor estimado: R$ 0,00 (não preenchido pelo órgão)
Viability value_fit: 30/100 (penalizado por "sem informação")
Viability overall: ~52 → Média
Realidade: Provavelmente R$ 200k-2M (faixa ideal do setor vestuario)
```

## Acceptance Criteria

- [ ] **AC1:** Quando `valor <= 0`, o fator `value_fit` deve retornar `50` (neutro) em vez de `30` (penalização)
- [ ] **AC2:** Adicionar campo `_value_source: "estimated" | "missing"` ao item para frontend exibir badge indicativo
- [ ] **AC3:** No `ViabilityBadge.tsx`, quando `_value_source == "missing"`, exibir tooltip: "Valor estimado não informado pelo órgão — viabilidade pode ser maior"
- [ ] **AC4:** Log de proporção de bids com valor zero por busca: `{zero_value_pct: 25.0}`
- [ ] **AC5:** Testes unitários para `_calculate_value_fit()` com valor=0 retornando 50

## Impacto

- **Cobertura:** 25% de todos os bids PNCP
- **Risco de regressão:** BAIXO (apenas muda score de 30→50 para valor zero)
- **UX:** Usuário entende que "viabilidade desconhecida" ≠ "baixa viabilidade"

## Arquivos

- `backend/viability.py` (`_calculate_value_fit()`)
- `frontend/app/buscar/components/ViabilityBadge.tsx` (tooltip)
- `backend/tests/test_viability.py`
