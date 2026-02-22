# GTM-COPY-007: Páginas de Conteúdo Estratégico

**Épico:** GTM-COPY — Reposicionamento Estratégico de Comunicação
**Prioridade:** P2
**Tipo:** Feature
**Estimativa:** XL (12-15 ACs)
**Depende de:** GTM-COPY-001, GTM-COPY-005

## Objetivo

Criar **4-6 novas páginas de conteúdo** que respondam diretamente às perguntas que o público faz quando está sob pressão de decisão em licitações. Cada página trata um **problema específico com profundidade, linguagem direta e aplicação prática**, posicionando o SmartLic como autoridade no território de **decisão estratégica em licitações**.

## Contexto

O site atual é uma **landing page institucional** com páginas de suporte (login, planos, ajuda). Não existe conteúdo que responda perguntas reais do público. Isso limita:

1. **Tráfego orgânico** — sem páginas para ranquear em buscas de intenção informacional
2. **Autoridade de domínio** — sem conteúdo profundo, o site não é referência
3. **Recorrência** — sem motivo para o visitante voltar
4. **Conversão indireta** — sem conteúdo educativo que leve à percepção de necessidade

### Território Alvo

Perguntas que o público faz sob pressão:
- "Como sei se essa licitação vale a pena?" → `/como-avaliar-licitacao`
- "Como evitar prejuízo em licitações?" → `/como-evitar-prejuizo-licitacao`
- "Como filtrar editais irrelevantes?" → `/como-filtrar-editais`
- "Como identificar licitações com maior chance de vitória?" → `/como-priorizar-oportunidades`

## Acceptance Criteria

### Página 1: `/como-avaliar-licitacao`

#### AC1 — Estrutura da Página
- [ ] Título H1: diretamente a pergunta ("Como avaliar se uma licitação vale a pena?")
- [ ] Meta description: resposta direta em 155 chars
- [ ] 800-1200 palavras de conteúdo original
- [ ] Arquivo: `frontend/app/como-avaliar-licitacao/page.tsx` (**NOVO**)

#### AC2 — Conteúdo
- [ ] Introdução: o problema real (empresas participam de licitações erradas e perdem dinheiro)
- [ ] 4-5 critérios práticos de avaliação:
  1. Compatibilidade setorial (o edital é do seu segmento?)
  2. Faixa de valor (o valor justifica o investimento de preparo?)
  3. Prazo (há tempo suficiente para preparar a proposta?)
  4. Região (é viável operar nessa localidade?)
  5. Modalidade (pregão vs concorrência vs...)
- [ ] Para cada critério: o que é, por que importa, como avaliar
- [ ] Exemplo concreto: análise de uma licitação fictícia mas realista
- [ ] Conclusão: "Se fizer isso manualmente, leva X horas. O SmartLic faz em segundos."
- [ ] CTA contextual: "Veja quais licitações passam nesses critérios para seu setor"

#### AC3 — SEO & Estrutura
- [ ] Heading hierarchy correta (H1 → H2 → H3)
- [ ] Schema `Article` ou `HowTo` JSON-LD
- [ ] Internal links para `/features`, `/planos`, outras páginas de conteúdo
- [ ] Breadcrumb visual e em structured data

---

### Página 2: `/como-evitar-prejuizo-licitacao`

#### AC4 — Estrutura da Página
- [ ] Título H1: "Como evitar prejuízo em licitações públicas"
- [ ] 800-1200 palavras
- [ ] Arquivo: `frontend/app/como-evitar-prejuizo-licitacao/page.tsx` (**NOVO**)

#### AC5 — Conteúdo
- [ ] Introdução: "Participar da licitação errada custa mais do que não participar"
- [ ] 4-5 causas comuns de prejuízo:
  1. Participar sem avaliar viabilidade
  2. Subestimar custos de preparação da proposta
  3. Ignorar requisitos técnicos incompatíveis
  4. Competir fora da faixa de valor ideal
  5. Não considerar logística/região
- [ ] Para cada causa: exemplo prático + como evitar
- [ ] Seção: "Como um filtro estratégico reduz o risco"
- [ ] CTA contextual

---

### Página 3: `/como-filtrar-editais`

#### AC6 — Estrutura da Página
- [ ] Título H1: "Como filtrar editais de licitação e focar no que importa"
- [ ] 800-1200 palavras
- [ ] Arquivo: `frontend/app/como-filtrar-editais/page.tsx` (**NOVO**)

#### AC7 — Conteúdo
- [ ] Introdução: "O problema não é falta de licitações. É excesso de irrelevância."
- [ ] Seções:
  1. Por que a busca manual não funciona (volume, fontes dispersas, palavras-chave ambíguas)
  2. O que um bom filtro precisa considerar (setor, valor, região, prazo, modalidade)
  3. Filtro por palavra-chave vs. filtro por perfil (a diferença)
  4. Exemplo: "1.500 editais publicados hoje → 12 relevantes para seu setor"
  5. Como o SmartLic aborda isso (sem vender — explicar o mecanismo)
- [ ] CTA contextual

---

### Página 4: `/como-priorizar-oportunidades`

#### AC8 — Estrutura da Página
- [ ] Título H1: "Como identificar licitações com maior chance de vitória"
- [ ] 800-1200 palavras
- [ ] Arquivo: `frontend/app/como-priorizar-oportunidades/page.tsx` (**NOVO**)

#### AC9 — Conteúdo
- [ ] Introdução: "Encontrar licitações é fácil. Saber quais priorizar é o que gera resultado."
- [ ] Seções:
  1. Por que priorização importa mais que volume
  2. Critérios de priorização (aderência, viabilidade, competição estimada)
  3. Como avaliar a viabilidade de cada oportunidade
  4. Framework de decisão: participar / monitorar / descartar
  5. Exemplo prático: 3 licitações, qual priorizar e por quê
- [ ] CTA contextual

---

### Elementos Comuns

#### AC10 — Layout Compartilhado
- [ ] Todas as páginas de conteúdo usam layout consistente:
  - Header do site (com nav)
  - Breadcrumb: Home > [Página]
  - Conteúdo com max-width para legibilidade (prose)
  - Sidebar ou seção lateral com CTA + links para outras páginas
  - Footer
- [ ] Componente reutilizável `ContentPageLayout.tsx` (**NOVO**)

#### AC11 — Cross-Linking
- [ ] Cada página linka para pelo menos 2 outras páginas de conteúdo
- [ ] Cada página tem CTA para signup/trial
- [ ] Landing page linka para as páginas de conteúdo (seção ou footer)

#### AC12 — Exemplos com Dados Reais
- [ ] Cada página inclui pelo menos 1 exemplo concreto de análise
- [ ] Dados baseados em licitações reais (anonimizados se necessário)
- [ ] Exemplos demonstram como o SmartLic faria a análise
- [ ] Tom: "Veja como isso funciona na prática"

#### AC13 — Mobile & Dark Mode
- [ ] Todas as páginas responsivas (375px mínimo)
- [ ] Dark mode funcional
- [ ] Tipografia legível (font-size, line-height, contrast)

#### AC14 — Sitemap & Indexação
- [ ] Novas páginas adicionadas ao sitemap
- [ ] Internal linking a partir da landing e do footer
- [ ] Canonical URLs configuradas

#### AC15 — Zero Regressions
- [ ] TypeScript compila
- [ ] Testes frontend: zero novas falhas
- [ ] Todas as 4 páginas renderizam sem erros

## Arquivos Impactados

| Arquivo | Mudança |
|---------|---------|
| `frontend/app/como-avaliar-licitacao/page.tsx` | **NOVO** |
| `frontend/app/como-evitar-prejuizo-licitacao/page.tsx` | **NOVO** |
| `frontend/app/como-filtrar-editais/page.tsx` | **NOVO** |
| `frontend/app/como-priorizar-oportunidades/page.tsx` | **NOVO** |
| `frontend/app/components/ContentPageLayout.tsx` | **NOVO** — Layout compartilhado |
| `frontend/app/page.tsx` | Links para novas páginas |
| `frontend/app/layout.tsx` | Nav atualizado (se aplicável) |
| `frontend/app/sitemap.ts` | Novas URLs |

## Notas de Implementação

- Páginas são **estáticas** — sem API calls, sem autenticação
- Conteúdo deve ser **original** e **factual** — sem claims não verificáveis
- O tom é **profissional e direto** — como consultor sênior explicando para colega
- NÃO é blog — é conteúdo evergreen que responde perguntas permanentes
- Cada página deve ser **self-contained** (resolve a dúvida sem sair da página)
- Considerar `generateMetadata()` do Next.js para SEO per-page

## Evolução Futura (não nesta story)

- Sistema de conteúdo dinâmico com CMS headless
- Análises semanais de licitações reais publicadas automaticamente
- Páginas por setor: "/licitacoes-engenharia", "/licitacoes-saude"
- Calculadora de viabilidade interativa

## Definition of Done

- [ ] ACs 1-15 verificados
- [ ] 4 páginas publicáveis e indexáveis
- [ ] Conteúdo revisado por stakeholder
- [ ] Commit: `feat(frontend): GTM-COPY-007 — páginas de conteúdo estratégico`
