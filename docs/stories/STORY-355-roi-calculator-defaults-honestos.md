# STORY-355: ROI calculator — defaults honestos e disclaimers

**Prioridade:** P1
**Tipo:** fix (copy + lógica)
**Sprint:** Sprint 2
**Estimativa:** M
**Origem:** Conselho CTO Advisory Board — Auditoria de Promessas (2026-03-01)
**Dependências:** Nenhuma
**Bloqueado por:** —
**Bloqueia:** —
**Paralelo com:** STORY-356, STORY-357

---

## Contexto

O ROI calculator usa defaults agressivos: 8.5h busca manual vs 0.05h SmartLic (170x multiplier). A copy "Investimento se paga na primeira licitação ganha" implica causalidade — SmartLic encontra licitações mas não ajuda a ganhar. Consultorias de licitação (público sofisticado) perceberão a inflação.

## Promessa Afetada

> "Investimento se paga na primeira licitação ganha"
> ROI calculator com 170x multiplier implícito

## Causa Raiz

ROI calculator usa `timeSavedPerSearch: 8.5` (horas) vs `smartlicTimePerSearch: 0.05` (horas). O "tempo manual" inclui atividades que SmartLic não substitui (leitura de edital completo, análise jurídica). SmartLic substitui apenas a etapa de descoberta e triagem inicial.

## Critérios de Aceite

- [ ] AC1: Adicionar disclaimer ao ROI calculator: "* Valores estimados. SmartLic auxilia na descoberta e priorização de oportunidades, não garante vitória em licitações."
- [ ] AC2: Ajustar `timeSavedPerSearch` de `8.5` para `3.0` em `roi.ts` (default mais conservador — busca + triagem inicial, não análise completa)
- [ ] AC3: Substituir "Investimento se paga na primeira licitação ganha" por "Economize horas de análise manual desde o primeiro uso" em `valueProps.ts:216`
- [ ] AC4: Ajustar `potentialReturn` para cálculo dinâmico baseado nos inputs reais (não hardcoded "500x")
- [ ] AC5: Adicionar cenário "conservador" ao lado do default na UI do calculator
- [ ] AC6: Adicionar "se paga na primeira licitação" ao BANNED_PHRASES
- [ ] AC7: Testes: verificar que disclaimer aparece em todos os cenários do calculator

## Arquivos Afetados

- `frontend/lib/copy/roi.ts`
- `frontend/lib/copy/valueProps.ts`
- `frontend/app/pricing/page.tsx`
- `frontend/app/planos/page.tsx`

## Validação

| Métrica | Threshold | Onde medir |
|---------|-----------|------------|
| Disclaimer visível | 100% dos cenários | E2E test |
| ROI multiplier default | <50x (era 170x) | Code review |

## Notas

- ROI calculators são ferramentas de persuasão, não predição. O disclaimer torna isso explícito.
- Consultorias de licitação (target audience) são sofisticadas — exagero perde credibilidade.
