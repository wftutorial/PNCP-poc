# GTM-COPY-003: Prova de Funcionamento na Primeira Dobra

**Épico:** GTM-COPY — Reposicionamento Estratégico de Comunicação
**Prioridade:** P0 (GTM-blocker)
**Tipo:** Feature
**Estimativa:** L (9-12 ACs)

## Objetivo

Incluir **prova de funcionamento real** logo na primeira dobra da landing page, por meio de exemplos concretos de recomendações geradas pelo sistema ou explicação clara de **por que determinada licitação foi priorizada** — reduzindo percepção de risco e aumentando confiança.

## Contexto

A landing atual não mostra o produto funcionando. O visitante vê promessas, comparações e depoimentos genéricos, mas **nunca vê uma recomendação real** ou entende concretamente como o sistema decide. Isso cria uma lacuna de confiança, especialmente para decisões financeiras (B2G).

### O que falta

1. **Exemplo visual** de uma recomendação gerada pelo sistema
2. **Justificativa objetiva** de por que aquela licitação foi priorizada
3. **Indicadores de aderência** ao perfil do usuário
4. **Contraste** mostrando uma licitação rejeitada e por quê

## Acceptance Criteria

### AC1 — Componente de Exemplo Real
- [ ] Novo componente `ProofOfValue.tsx` (ou similar) na landing
- [ ] Posicionado **abaixo do hero, acima do fold** (ou como segunda seção visível)
- [ ] Exibe 1-2 licitações reais com análise do sistema
- [ ] Arquivo: `frontend/app/components/landing/ProofOfValue.tsx`

### AC2 — Card de Licitação Recomendada
- [ ] Card visual mostrando uma licitação que o sistema **recomendaria**
- [ ] Campos visíveis: título resumido, valor estimado, UF, modalidade
- [ ] Badge de aderência: "Alta compatibilidade" (verde) com score visual
- [ ] Selo de viabilidade (se feature flag ativa)

### AC3 — Justificativa de Priorização
- [ ] Abaixo do card, lista de 2-3 critérios que justificam a recomendação
- [ ] Exemplos: "Setor compatível: engenharia", "Valor dentro da faixa ideal", "Prazo: 15 dias (viável)"
- [ ] Linguagem clara, sem jargão técnico
- [ ] Ícones ou badges visuais para cada critério

### AC4 — Contraste com Licitação Rejeitada (opcional mas recomendado)
- [ ] Segundo card (menor, esmaecido) mostrando uma licitação que o sistema **descartou**
- [ ] Motivo visível: "Fora do seu setor", "Valor abaixo do mínimo", "Prazo insuficiente"
- [ ] Reforça visualmente que o sistema **protege o tempo do usuário**

### AC5 — Dados Estáticos (não API call)
- [ ] Exemplos são **dados estáticos hardcoded** (não chamada à API)
- [ ] Dados baseados em licitações reais (podem ser anonimizados ou simplificados)
- [ ] Não exige autenticação para visualizar
- [ ] Atualizáveis manualmente (não auto-refresh)

### AC6 — Anotação de Transparência
- [ ] Texto pequeno abaixo dos exemplos: "Exemplo baseado em análise real do sistema"
- [ ] Se os dados forem simulados/anonimizados: "Exemplo ilustrativo baseado em análises reais"
- [ ] Sem claims falsos ("100% real-time" etc.)

### AC7 — Explicação do Mecanismo
- [ ] Texto curto (2-3 linhas) explicando **como o sistema decide**:
  - "O SmartLic cruza o perfil da sua empresa com cada edital publicado. Avalia setor, valor, prazo e região. Entrega apenas o que tem aderência — com a explicação do porquê."
- [ ] Posicionado como caption/annotation dos exemplos

### AC8 — Responsividade
- [ ] Cards responsivos: desktop (lado a lado), mobile (empilhados)
- [ ] Leitura confortável em 375px (mobile mínimo)
- [ ] Dark mode funcional

### AC9 — Integração na Landing
- [ ] Componente adicionado em `page.tsx` na posição estratégica
- [ ] Ordem sugerida: Hero → **ProofOfValue** → ValueProps → ...
- [ ] Transição visual suave com seções adjacentes

### AC10 — Dados de Exemplo
- [ ] Pelo menos 2 exemplos preparados (1 recomendado + 1 descartado)
- [ ] Exemplos cobrem setores diferentes (não setor-específico)
- [ ] Valores realistas (R$ 50k-500k range)
- [ ] UFs diversas

## Arquivos Impactados

| Arquivo | Mudança |
|---------|---------|
| `frontend/app/components/landing/ProofOfValue.tsx` | **NOVO** — Componente principal |
| `frontend/app/page.tsx` | Import e posicionamento do novo componente |
| `frontend/lib/copy/valueProps.ts` | Dados dos exemplos (opcional, pode ser inline) |

## Notas de Implementação

- Usar dados estáticos para MVP. Evolução futura: endpoint que retorna "exemplo do dia" com licitação real recente.
- O componente deve ser **self-contained** — não depender de auth, API, ou estado global
- Design: cards com sombra suave, badges coloridos, ícones de check/X
- Considerar animação sutil no scroll (fade-in) para chamar atenção
- NÃO mostrar dados de setor específico (vestuário, etc.) — usar setores genéricos

## Evolução Futura (não nesta story)

- Endpoint `/v1/exemplo-do-dia` que retorna licitação real recente com análise
- Auto-refresh diário dos exemplos
- Personalização por setor do visitante (se cookie de onboarding disponível)

## Definition of Done

- [ ] ACs 1-9 verificados (AC4 e AC10 são recomendados mas não bloqueantes)
- [ ] Componente visualmente integrado à landing
- [ ] Mobile 375px verificado
- [ ] Dark mode verificado
- [ ] Zero regressions
- [ ] Commit: `feat(frontend): GTM-COPY-003 — prova de funcionamento na primeira dobra`
