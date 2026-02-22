# GTM-COPY-002: CTAs Orientados a Ação Imediata

**Épico:** GTM-COPY — Reposicionamento Estratégico de Comunicação
**Prioridade:** P0 (GTM-blocker)
**Tipo:** Enhancement
**Estimativa:** S (5-7 ACs)

## Objetivo

Migrar **todos os CTAs do site** de um estado exploratório ("Descobrir", "Experimentar") para um estado orientado a **ação imediata** — o usuário quer validar rapidamente o valor prometido e enxergar oportunidades relevantes **agora**.

## Contexto

### CTAs Atuais

| Local | CTA Atual | Problema |
|-------|-----------|----------|
| Hero primário | "Descobrir minhas oportunidades" | Exploratório, sem urgência |
| Hero secundário | "Como funciona" | Informativo, não ação |
| Final CTA | "Descobrir minhas oportunidades" | Repetição do hero |
| Features | "Experimentar SmartLic Pro" | Foco no produto, não no resultado |
| Pricing | "Começar agora" | Genérico |
| Signup badge | "3 análises completas / Acesso a todos os recursos" | Foco em features |

### Direção Estratégica

O CTA deve levar o usuário a querer **validar rapidamente o valor prometido**, focando em **enxergar oportunidades relevantes naquele momento** — não em "experimentar" ou "descobrir".

## Acceptance Criteria

### AC1 — Hero CTA Primário
- [x] CTA comunica ação imediata + resultado esperado
- [x] Foco em "ver oportunidades relevantes agora" (não "descobrir" ou "explorar")
- [x] Arquivo: `HeroSection.tsx`

**Direção de copy (exemplos):**
- "Ver oportunidades para meu setor"
- "Filtrar licitações para minha empresa"
- "Mostrar o que vale a pena agora"

### AC2 — Hero CTA Secundário
- [x] Migra de "Como funciona" para algo que reforce confiança ou urgência
- [x] Pode ser: link para prova de funcionamento, ou âncora para exemplo real
- [x] Arquivo: `HeroSection.tsx`

**Direção:**
- "Ver exemplo de análise real"
- "Como o filtro funciona na prática"

### AC3 — Final CTA (Bottom of Page)
- [x] CTA diferente do hero (não repetir)
- [x] Incorpora urgência: licitações estão abrindo agora, perder tempo = perder oportunidade
- [x] Subtext reforça: "Licitações com prazo de hoje. Se não vir agora, pode perder."
- [x] Arquivo: `FinalCTA.tsx`

### AC4 — Features Page CTA
- [x] CTA orientado a resultado (não "experimentar produto")
- [x] Subtext conecta trial ao valor concreto
- [x] Arquivo: `features/page.tsx` ou `features/FeaturesContent.tsx`

### AC5 — Pricing Page CTA
- [x] CTA por billing period orientado a ação
- [x] Messaging de urgência sutil: "A cada dia sem filtro estratégico, oportunidades passam"
- [x] Arquivo: `planos/page.tsx`

### AC6 — Signup Page Messaging
- [x] Badge/tagline do signup reforça **resultado imediato** (não features do trial)
- [x] Atual: "3 análises completas / Acesso a todos os recursos / Sem cartão"
- [x] Desejado: "Veja quais licitações valem a pena para sua empresa — em 2 minutos"
- [x] Arquivo: `signup/page.tsx`

### AC7 — Consistência Cross-Page
- [x] Todos os CTAs seguem o mesmo tom: ação imediata + resultado esperado
- [x] Nenhum CTA usa "descobrir", "explorar", "experimentar" como verbo principal
- [x] Verbos preferidos: "ver", "filtrar", "analisar", "começar"
- [x] Auditoria de todos os CTAs documentada

## Arquivos Impactados

| Arquivo | Mudança |
|---------|---------|
| `frontend/app/components/landing/HeroSection.tsx` | AC1, AC2 |
| `frontend/app/components/landing/FinalCTA.tsx` | AC3 |
| `frontend/app/features/page.tsx` | AC4 |
| `frontend/app/features/FeaturesContent.tsx` | AC4 |
| `frontend/app/planos/page.tsx` | AC5 |
| `frontend/app/signup/page.tsx` | AC6 |

## Notas de Implementação

- CTAs devem manter o mesmo destino funcional (signup/login flow)
- O texto do botão pode mudar, a URL de destino não
- Manter acessibilidade: `aria-label` descritivo se texto do botão for curto
- Mobile: CTAs devem ser igualmente impactantes em telas pequenas

## Definition of Done

- [x] Todos os 7 ACs verificados
- [x] Auditoria de CTAs cross-page documentada
- [x] Zero regressions (testes + TypeScript)
- [x] Commit: `feat(frontend): GTM-COPY-002 — CTAs orientados a ação imediata`
