# GTM-COPY-001: Headlines, Subheadlines & Narrativa da Landing

**Épico:** GTM-COPY — Reposicionamento Estratégico de Comunicação
**Prioridade:** P0 (GTM-blocker)
**Tipo:** Enhancement
**Estimativa:** M (8-13 ACs)

## Objetivo

Reescrever toda a copy da landing page para sair do discurso genérico de "inteligência" e assumir uma **promessa concreta de impacto financeiro**, com tom incisivo que posiciona o SmartLic como filtro estratégico — não ferramenta de busca.

## Contexto

A landing atual (GTM-001, commit e7bf18c) já migrou de "economia de tempo" para "decisão inteligente". Esta story é a **segunda evolução**: de "decisão inteligente" (ainda conceitual) para **"impacto financeiro direto + eliminação de desperdício"** (consequência prática).

### Copy Atual vs. Desejada

| Elemento | Atual | Desejado |
|----------|-------|----------|
| Headline | "Saiba Onde Investir para Ganhar Mais Licitações" | Afirmação direta de ganho financeiro OU redução de erro |
| Subheadline | "Inteligência que avalia oportunidades, prioriza..." | Mecanismo de valor: analisa compatibilidade, elimina ruído, destaca maior probabilidade |
| Tom geral | Informativo, apresenta capacidade | Incisivo, promete foco no que gera retorno |
| Narrativa | "Somos inteligentes" | "Sem nós, você opera no escuro" |

## Acceptance Criteria

### AC1 — Hero Headline
- [x] Headline afirma **diretamente** ganho financeiro ou redução de erro
- [x] Elimina abstrações ("inteligência", "automatizado", "inovador")
- [x] Tom incisivo: promete foco apenas no que tem real potencial de retorno
- [x] Arquivo: `HeroSection.tsx`

**Direção de copy (exemplos, não definitivos):**
- "Pare de perder dinheiro com licitações erradas."
- "Só o que vale a pena chega até você."
- "Licitações que realmente pagam. O resto, a gente descarta."

### AC2 — Hero Subheadline
- [x] Complementa explicando o **mecanismo de valor** (não repete a headline)
- [x] Evidencia: analisa compatibilidade com perfil do negócio + elimina ruído + destaca maior probabilidade de êxito
- [x] Reforça decisão fundamentada (não "busca")
- [x] Arquivo: `HeroSection.tsx`

**Direção de copy (exemplo):**
- "O SmartLic analisa cada edital contra o perfil da sua empresa. Elimina o que não faz sentido. Entrega só o que tem chance real de retorno — com justificativa objetiva."

### AC3 — Stats Badges
- [x] Badges do hero reforçam confiança prática (não métricas abstratas)
- [x] Atual: "15 setores | 1000+ regras | 27 estados" → Migrar para impacto ou prova
- [x] Sugestão: "X% de editais descartados por irrelevância | Y setores especializados | 27 UFs cobertas"
- [x] Arquivo: `HeroSection.tsx`

### AC4 — Value Props Section
- [x] Título de seção orientado a consequência (não "Por Que SmartLic?")
- [x] 4 value props reescritas com foco em **consequência prática** para o cliente
- [x] Cada prop: título = benefício tangível, descrição = como o sistema entrega
- [x] Elimina referências a "inteligência automatizada"
- [x] Arquivos: `ValuePropSection.tsx`, `valueProps.ts`

**Direção:**
| Atual | Desejado |
|-------|----------|
| "Priorização Inteligente" | "Foque só no que paga" |
| "Análise Automatizada" | "Descarte sem ler 100 páginas" |
| "Redução de Incerteza" | "Saiba por que cada edital foi selecionado" |
| "Cobertura Nacional" | "Nenhuma oportunidade invisível" |

### AC5 — Opportunity Cost Section
- [x] Copy mais específica e incisiva
- [x] Converte "custo de não usar" em **risco operacional explícito**
- [x] Linguagem: "continuar sem = operar no escuro"
- [x] Arquivo: `OpportunityCost.tsx`

### AC6 — Before/After Section
- [x] "Sem SmartLic" = lista de consequências concretas de operar sem filtro estratégico
- [x] "Com SmartLic" = lista de resultados práticos (não features)
- [x] Headline migra de "Da busca manual à decisão estratégica" para algo mais orientado a resultado
- [x] Arquivo: `BeforeAfter.tsx`

### AC7 — Differentials Grid
- [x] Headline reforça **resultado** ("empresas que vencem" está bom, pode ser mais incisivo)
- [x] Featured card enfatiza **redução de desperdício + foco em retorno**
- [x] Cards secundários: cada um = um risco eliminado
- [x] Arquivo: `DifferentialsGrid.tsx`

### AC8 — How It Works
- [x] 3 passos reescritos enfatizando **eliminação de ruído** em cada etapa
- [x] Step 1: perfil → sistema entende o que é relevante para VOCÊ
- [x] Step 2: filtragem → elimina X% de ruído, entrega Y recomendações priorizadas
- [x] Step 3: decisão → cada oportunidade com justificativa objetiva
- [x] Arquivo: `HowItWorks.tsx`

### AC9 — Comparison Table
- [x] Coluna "Outros" reforça **risco de usar alternativa** (não apenas desvantagem)
- [x] Coluna "SmartLic" reforça **resultado concreto** (não feature)
- [x] Arquivo: `ComparisonTable.tsx`, `comparisons.ts`

### AC10 — Narrativa Convergente
- [x] Toda a página converge para uma única mensagem: **filtro estratégico que direciona esforço para oportunidades com maior potencial de retorno**
- [x] A escolha de NÃO usar o SmartLic é percebida como **risco operacional**
- [x] Nenhuma seção usa "inteligência" como substantivo isolado
- [x] Nenhuma seção promete "busca rápida" ou "economia de tempo"

### AC11 — Copy Library Update
- [x] `valueProps.ts` atualizado com nova copy (single source of truth)
- [x] `comparisons.ts` atualizado com novas comparações orientadas a risco
- [x] Banned phrases list revisada e expandida
- [x] Preferred phrases list atualizada com novo vocabulário

### AC12 — Zero Regressions
- [x] TypeScript compila: `npx tsc --noEmit` limpo
- [x] Testes frontend: zero novas falhas vs baseline (40 fail / 2205 pass)
- [x] Layout visual preservado (mesmos componentes, nova copy)

## Arquivos Impactados

| Arquivo | Mudança |
|---------|---------|
| `frontend/app/components/landing/HeroSection.tsx` | AC1, AC2, AC3 |
| `frontend/app/components/ValuePropSection.tsx` | AC4 |
| `frontend/app/components/landing/OpportunityCost.tsx` | AC5 |
| `frontend/app/components/landing/BeforeAfter.tsx` | AC6 |
| `frontend/app/components/landing/DifferentialsGrid.tsx` | AC7 |
| `frontend/app/components/landing/HowItWorks.tsx` | AC8 |
| `frontend/app/components/ComparisonTable.tsx` | AC9 |
| `frontend/lib/copy/valueProps.ts` | AC4, AC11 |
| `frontend/lib/copy/comparisons.ts` | AC9, AC11 |

## Notas de Implementação

- Toda copy em português (pt-BR)
- Nunca usar: "plano", "assinatura", "tier", "pacote", "busca" como substantivo principal
- Nunca referenciar "BidIQ", setores específicos, ou fontes de dados por nome
- O tom pode ser incisivo mas não agressivo — profissional B2B
- Manter consistência com copy das páginas `/planos`, `/features`, `/signup`

## Definition of Done

- [x] Todos os 12 ACs verificados
- [ ] Review de copy por stakeholder
- [ ] Screenshots before/after documentados
- [x] Commit com mensagem: `feat(frontend): GTM-COPY-001 — headlines e narrativa orientada a impacto`
