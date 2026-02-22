# GTM-COPY-005: Credibilidade & Autoridade Explícita

**Épico:** GTM-COPY — Reposicionamento Estratégico de Comunicação
**Prioridade:** P1
**Tipo:** Feature
**Estimativa:** M (7-8 ACs)

## Objetivo

Transmitir **credibilidade de forma explícita** no site, deixando claro quem está por trás da solução, qual a experiência envolvida e quais critérios são utilizados nas análises. Isso atende tanto à percepção de confiança do visitante quanto a sinais de E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness) para SEO.

## Contexto

O site atual não possui:
- Página "Sobre" ou "Quem somos"
- Informação sobre a empresa (CONFENGE) ou equipe
- Metodologia documentada para o visitante
- Explicação dos critérios de análise para o público leigo

Para decisões que envolvem investimento financeiro (licitações B2G), **autoridade e transparência são fatores determinantes** de conversão.

## Acceptance Criteria

### AC1 — Página "Sobre / Metodologia"
- [ ] Nova página acessível via header: `/sobre` ou `/metodologia`
- [ ] Estrutura:
  1. Quem somos (CONFENGE + propósito do SmartLic)
  2. O problema que resolvemos (desperdício em licitações)
  3. Como funciona nossa análise (metodologia acessível)
  4. Critérios utilizados
  5. Fontes de dados
- [ ] Tom: profissional, direto, sem jargão excessivo
- [ ] Arquivo: `frontend/app/sobre/page.tsx` (**NOVO**)

### AC2 — Seção "Quem Somos"
- [ ] Nome da empresa: CONFENGE Avaliações e Inteligência Artificial LTDA
- [ ] Propósito: "Transformar decisões em licitações de intuitivas para objetivas"
- [ ] Experiência: background em avaliações, IA aplicada, mercado B2G
- [ ] CNPJ visível (footer ou página sobre)
- [ ] Sem fotos pessoais obrigatórias (pode ser logo + texto)

### AC3 — Seção "Metodologia"
- [ ] Explica em linguagem acessível como o SmartLic avalia oportunidades
- [ ] 4-5 critérios documentados (setor, valor, prazo, região, modalidade)
- [ ] Para cada critério: o que é avaliado + por que importa + como impacta a recomendação
- [ ] Não revela detalhes de implementação (modelos, APIs, prompts)
- [ ] Reforça: "Critérios objetivos, não opinião"

### AC4 — Seção "Fontes de Dados"
- [ ] Explica que os dados vêm de **fontes oficiais públicas**
- [ ] Sem nomear portais específicos (PNCP, PCP) — usar "portais oficiais de contratações públicas"
- [ ] Menciona: cobertura nacional (27 UFs), atualização contínua, consolidação automática
- [ ] Reforça: "Dados verificados, não estimativas"

### AC5 — Footer Atualizado
- [ ] Footer de todas as páginas inclui:
  - Link para `/sobre`
  - CNPJ da CONFENGE
  - Email de contato
  - Links para termos e privacidade (já existem)
- [ ] Arquivo: componente de layout/footer

### AC6 — Landing Page — Menção de Credibilidade
- [ ] Em pelo menos 1 seção da landing, referência a "Desenvolvido pela CONFENGE" ou "Solução da CONFENGE"
- [ ] Pode ser sutil (no footer badge ou após How It Works)
- [ ] Não precisa ser seção inteira — apenas sinal de que existe uma empresa real por trás

### AC7 — FAQ — Perguntas sobre Confiança
- [ ] Adicionar 2-3 FAQs na página `/ajuda`:
  - "Como o SmartLic decide quais licitações recomendar?"
  - "De onde vêm os dados das licitações?"
  - "Quem está por trás do SmartLic?"
- [ ] Respostas diretas, 2-3 linhas cada
- [ ] Arquivo: `ajuda/page.tsx`

### AC8 — Zero Regressions
- [ ] Nova página `/sobre` renderiza sem erros
- [ ] Footer atualizado em todas as páginas
- [ ] TypeScript compila
- [ ] Testes: zero novas falhas

## Arquivos Impactados

| Arquivo | Mudança |
|---------|---------|
| `frontend/app/sobre/page.tsx` | **NOVO** — Página sobre/metodologia |
| `frontend/app/layout.tsx` | Footer com CNPJ e link |
| `frontend/app/ajuda/page.tsx` | AC7 — novas FAQs |
| `frontend/app/page.tsx` | AC6 — menção de credibilidade (opcional) |
| Componente de header/nav | Link para `/sobre` |

## Notas de Implementação

- A página `/sobre` deve ter boa SEO: `<title>`, `<meta description>`, `<h1>` otimizados
- Structured data: `Organization` schema para a CONFENGE
- A página deve ser **estática** (não requer autenticação ou API)
- Design consistente com o restante do site (Tailwind, dark mode)
- Conteúdo precisa ser validado com stakeholders antes de publicar

## Definition of Done

- [ ] ACs 1-8 verificados
- [ ] Página `/sobre` acessível e indexável
- [ ] Footer consistente em todas as páginas
- [ ] Commit: `feat(frontend): GTM-COPY-005 — credibilidade e autoridade explícita`
