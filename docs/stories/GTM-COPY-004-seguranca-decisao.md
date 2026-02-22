# GTM-COPY-004: Elementos de Segurança na Decisão

**Épico:** GTM-COPY — Reposicionamento Estratégico de Comunicação
**Prioridade:** P1
**Tipo:** Enhancement
**Estimativa:** M (7-9 ACs)
**Depende de:** GTM-COPY-001

## Objetivo

Introduzir **elementos explícitos de segurança na decisão** ao longo do site, reforçando transparência dos critérios utilizados, indicação do nível de aderência de cada oportunidade e destaque de como o sistema reduz falsos positivos e negativos — transformando isso em **benefício tangível**.

## Contexto

O sistema já possui mecanismos robustos de filtragem (1000+ keywords, LLM arbiter, viability assessment), mas isso **não está comunicado** na landing. O visitante não sabe que:

1. Cada oportunidade tem um **score de aderência** ao perfil
2. O sistema usa **critérios objetivos** documentados (não heurísticas genéricas)
3. Existe redução ativa de **falsos positivos** (ruído) e **falsos negativos** (oportunidades perdidas)
4. A transparência dos critérios é um diferencial real

### Impacto Desejado

O visitante deve perceber que **continuar sem a ferramenta = operar no escuro**, enquanto usá-la = **decisões mais assertivas com maior previsibilidade de resultado**.

## Acceptance Criteria

### AC1 — Seção "Por que confiar nas recomendações"
- [ ] Nova seção ou expansão de seção existente na landing
- [ ] Título orientado a confiança: "Cada recomendação tem uma justificativa"
- [ ] Explica em 3-4 pontos como o sistema avalia (sem revelar propriedade intelectual)
- [ ] Arquivo: novo componente ou expansão de `DifferentialsGrid.tsx`

### AC2 — Critérios de Avaliação Visíveis
- [ ] Lista explícita dos critérios que o sistema usa para avaliar oportunidades:
  - Compatibilidade setorial (keywords + IA)
  - Faixa de valor adequada ao porte
  - Prazo viável para preparação
  - Região de atuação
  - Modalidade favorável
- [ ] Cada critério com ícone + descrição de 1 linha
- [ ] Posicionamento: próximo à prova de funcionamento (GTM-COPY-003) ou como seção independente

### AC3 — Indicador de Aderência Explicado
- [ ] Explicação visual de como o "nível de aderência" funciona
- [ ] Escala: Alta / Média / Baixa com cores (verde/amarelo/cinza)
- [ ] Cada nível tem descrição: "Alta = 3+ critérios atendem seu perfil"
- [ ] Conecta com ViabilityBadge existente (se feature flag ativa) ou usa linguagem similar

### AC4 — Redução de Falsos Positivos (Comunicação)
- [ ] Copy explícita sobre como o sistema **reduz ruído**
- [ ] Números ou proporções: "Em média, X% dos editais são descartados por irrelevância"
- [ ] Benefício tangível: "Você recebe 20 recomendações, não 2.000 resultados genéricos"
- [ ] Pode ser integrado à seção de comparação ou à prova de funcionamento

### AC5 — Redução de Falsos Negativos (Comunicação)
- [ ] Copy explícita sobre como o sistema **não perde oportunidades relevantes**
- [ ] Explica: cobertura de 27 UFs, múltiplas fontes oficiais, IA para editais ambíguos
- [ ] Benefício tangível: "Se existe algo compatível em qualquer lugar do Brasil, você sabe"
- [ ] Pode ser integrado à seção de cobertura

### AC6 — "Operar no Escuro" Narrative
- [ ] Em pelo menos 2 pontos da página, a narrativa reforça:
  - "Sem filtro estratégico, você decide com base em intuição"
  - "Com SmartLic, cada decisão é baseada em critérios objetivos documentados"
- [ ] O contraste deve ser **emocional mas factual** — não fear-mongering
- [ ] Integrado naturalmente nas seções BeforeAfter ou OpportunityCost

### AC7 — Trust Indicators Consolidados
- [ ] Revisar e consolidar todos os indicadores de confiança da página:
  - Fontes oficiais verificadas
  - Critérios objetivos (não opinião)
  - Cancelamento em 1 clique
  - Sem dados fabricados
- [ ] Posicionamento estratégico: próximo ao CTA principal e ao CTA final
- [ ] Arquivo: `FinalCTA.tsx` e/ou `HeroSection.tsx`

### AC8 — Features Page — Seção de Confiança
- [ ] Página `/features` recebe menção explícita à transparência de critérios
- [ ] Pode ser um card adicional ou expansão dos existentes
- [ ] Arquivo: `features/page.tsx` ou `FeaturesContent.tsx`

### AC9 — Zero Regressions
- [ ] TypeScript compila
- [ ] Testes frontend: zero novas falhas
- [ ] Layout visual preservado nas seções não alteradas

## Arquivos Impactados

| Arquivo | Mudança |
|---------|---------|
| `frontend/app/components/landing/TrustCriteria.tsx` | **NOVO** (ou expansão de existente) |
| `frontend/app/components/landing/DifferentialsGrid.tsx` | AC1 (possível expansão) |
| `frontend/app/components/landing/OpportunityCost.tsx` | AC6 |
| `frontend/app/components/landing/BeforeAfter.tsx` | AC6 |
| `frontend/app/components/landing/FinalCTA.tsx` | AC7 |
| `frontend/app/components/landing/HeroSection.tsx` | AC7 |
| `frontend/app/features/page.tsx` | AC8 |
| `frontend/app/page.tsx` | Import do novo componente |

## Notas de Implementação

- Os "critérios objetivos" referidos na copy são reais (keyword matching, value range, UF, modalidade, viability)
- Não revelar detalhes de implementação (LLM arbiter, GPT-4.1-nano) — linguagem acessível
- Percentuais de descarte podem ser estimados (ex: "70-90% dos editais são irrelevantes para qualquer setor específico")
- Manter copy library (`valueProps.ts`) como fonte centralizada

## Definition of Done

- [ ] ACs 1-9 verificados
- [ ] Narrativa de confiança coerente ao longo da página
- [ ] Commit: `feat(frontend): GTM-COPY-004 — elementos de segurança na decisão`
