# GTM-COPY-005: Credibilidade & Autoridade Explícita

**Épico:** GTM-COPY — Reposicionamento Estratégico de Comunicação
**Prioridade:** P1
**Tipo:** Feature
**Estimativa:** M (7-8 ACs)
**Status:** COMPLETED
**Commit:** `b9f5930` — 7 files changed, 396+/2-

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
- [x] Nova página acessível via header: `/sobre` ou `/metodologia`
- [x] Estrutura:
  1. Quem somos (CONFENGE + propósito do SmartLic)
  2. O problema que resolvemos (desperdício em licitações)
  3. Como funciona nossa análise (metodologia acessível)
  4. Critérios utilizados
  5. Fontes de dados
- [x] Tom: profissional, direto, sem jargão excessivo
- [x] Arquivo: `frontend/app/sobre/page.tsx` (**NOVO**)

### AC2 — Seção "Quem Somos"
- [x] Nome da empresa: CONFENGE Avaliações e Inteligência Artificial LTDA
- [x] Propósito: "Transformar decisões em licitações de intuitivas para objetivas"
- [x] Experiência: background em avaliações, IA aplicada, mercado B2G
- [x] CNPJ visível (footer ou página sobre)
- [x] Sem fotos pessoais obrigatórias (pode ser logo + texto)

### AC3 — Seção "Metodologia"
- [x] Explica em linguagem acessível como o SmartLic avalia oportunidades
- [x] 4-5 critérios documentados (setor, valor, prazo, região, modalidade)
- [x] Para cada critério: o que é avaliado + por que importa + como impacta a recomendação
- [x] Não revela detalhes de implementação (modelos, APIs, prompts)
- [x] Reforça: "Critérios objetivos, não opinião"

### AC4 — Seção "Fontes de Dados"
- [x] Explica que os dados vêm de **fontes oficiais públicas**
- [x] Sem nomear portais específicos (PNCP, PCP) — usar "portais oficiais de contratações públicas"
- [x] Menciona: cobertura nacional (27 UFs), atualização contínua, consolidação automática
- [x] Reforça: "Dados verificados, não estimativas"

### AC5 — Footer Atualizado
- [x] Footer de todas as páginas inclui:
  - Link para `/sobre`
  - CNPJ da CONFENGE
  - Email de contato
  - Links para termos e privacidade (já existem)
- [x] Arquivo: componente de layout/footer

### AC6 — Landing Page — Menção de Credibilidade
- [x] Em pelo menos 1 seção da landing, referência a "Desenvolvido pela CONFENGE" ou "Solução da CONFENGE"
- [x] Pode ser sutil (no footer badge ou após How It Works)
- [x] Não precisa ser seção inteira — apenas sinal de que existe uma empresa real por trás

### AC7 — FAQ — Perguntas sobre Confiança
- [x] Adicionar 2-3 FAQs na página `/ajuda`:
  - "Como o SmartLic decide quais licitações recomendar?"
  - "De onde vêm os dados das licitações?"
  - "Quem está por trás do SmartLic?"
- [x] Respostas diretas, 2-3 linhas cada
- [x] Arquivo: `ajuda/page.tsx`

### AC8 — Zero Regressions
- [x] Nova página `/sobre` renderiza sem erros
- [x] Footer atualizado em todas as páginas
- [x] TypeScript compila
- [x] Testes: zero novas falhas

## Arquivos Impactados

| Arquivo | Mudança |
|---------|---------|
| `frontend/app/sobre/page.tsx` | **NOVO** — Página sobre/metodologia |
| `frontend/app/components/Footer.tsx` | Footer com CNPJ, /sobre link, CONFENGE attribution |
| `frontend/app/ajuda/page.tsx` | AC7 — 3 novas FAQs (Confiança e Credibilidade) |
| `frontend/app/page.tsx` | AC6 — badge "Desenvolvido pela CONFENGE" |
| `frontend/app/components/landing/LandingNavbar.tsx` | Link "Sobre" no header desktop |
| `frontend/components/layout/MobileMenu.tsx` | Link "Sobre" no menu mobile |
| `frontend/__tests__/components/Footer.test.tsx` | 4 novos testes (9 total) |

## Notas de Implementação

- A página `/sobre` tem SEO: `<title>`, `<meta description>`, `<h1>` otimizados
- Structured data: `Organization` schema JSON-LD para a CONFENGE
- A página é **estática** (Server Component, sem autenticação)
- Design consistente: Tailwind, CSS variables, responsive (sm/md/lg)
- `id="metodologia"` com `scroll-mt-24` para anchor navigation
- Footer bottom bar: CNPJ + "Solução da CONFENGE" (substituiu "servidores públicos")
- Landing page: badge discreto entre TrustCriteria e FinalCTA
- FAQ: nova categoria "Confiança e Credibilidade" com 3 perguntas

## Definition of Done

- [x] ACs 1-8 verificados
- [x] Página `/sobre` acessível e indexável
- [x] Footer consistente em todas as páginas
- [x] Commit: `feat(frontend): GTM-COPY-005 — credibilidade e autoridade explícita`
