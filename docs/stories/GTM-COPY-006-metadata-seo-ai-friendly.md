# GTM-COPY-006: Metadata SEO & Conteúdo AI-Friendly

**Épico:** GTM-COPY — Reposicionamento Estratégico de Comunicação
**Prioridade:** P1
**Tipo:** Enhancement
**Estimativa:** M (8-10 ACs)
**Depende de:** GTM-COPY-001 (metadata reflete nova copy)

## Objetivo

Reestruturar toda a metadata SEO do site e organizar o conteúdo para ser **facilmente interpretado por mecanismos de busca e sistemas de IA**, facilitando citação como fonte e ampliando relevância. Migrar o território semântico de "licitações" (genérico) para **"decisão estratégica + priorização + viabilidade de licitações"** (específico, menos concorrência).

## Contexto

### Metadata Atual

| Elemento | Valor Atual | Problema |
|----------|-------------|----------|
| Title | "SmartLic.tech - Como Encontrar e Vencer Licitações Públicas Facilmente" | Genérico, "facilmente" é fraco |
| Description | "Encontre oportunidades de licitações públicas filtradas por setor..." | "Encontre" = busca, não análise |
| OG Title | "...Encontre e Vença Licitações Públicas com Inteligência Artificial" | "IA" é buzzword saturado |
| Keywords | "como encontrar licitações públicas", "buscar editais"... | Território genérico, alta concorrência |
| Claim | "500+ empresas" | Não verificável neste estágio |

### Território Desejado

Sair de **"como encontrar licitações"** (busca genérica) → Dominar **"como avaliar se uma licitação vale a pena"** (decisão estratégica, menor concorrência, intenção mais qualificada).

## Acceptance Criteria

### AC1 — Title Tag Principal
- [ ] Novo title reflete posicionamento de decisão estratégica (não busca)
- [ ] Formato: "SmartLic — [promessa de valor em licitações]"
- [ ] Máximo 60 caracteres para não truncar em SERPs
- [ ] Arquivo: `layout.tsx`

**Direção:**
- "SmartLic — Filtre Licitações por Viabilidade, Não por Sorte"
- "SmartLic — Só Licitações com Real Potencial de Retorno"

### AC2 — Meta Description Principal
- [ ] Nova description orientada a resultado prático
- [ ] Inclui: o que faz + para quem + diferencial
- [ ] Máximo 155 caracteres
- [ ] Remove claim de "500+ empresas" (não verificável)
- [ ] Arquivo: `layout.tsx`

**Direção:**
- "Analise a viabilidade de licitações antes de investir tempo. SmartLic cruza seu perfil com cada edital e recomenda apenas o que tem chance real de retorno."

### AC3 — Keywords Estratégicas
- [ ] Migrar de keywords genéricas para território de decisão:
  - "como avaliar licitação antes de participar"
  - "filtrar licitações por viabilidade"
  - "quais licitações vale a pena participar"
  - "análise de viabilidade de licitação"
  - "priorizar editais por chance de vitória"
  - "como não perder tempo com licitação errada"
  - "filtro estratégico de licitações"
- [ ] Keywords refletem intenção de quem já está sob pressão de decisão
- [ ] Arquivo: `layout.tsx`

### AC4 — Open Graph Tags
- [ ] OG title e description alinhados com nova copy
- [ ] OG image mantida (ou atualizada se existir nova arte)
- [ ] Twitter cards atualizados
- [ ] Arquivo: `layout.tsx`

### AC5 — Per-Page Metadata
- [ ] Cada página com title e description únicos e relevantes:
  - `/planos` → "Investimento SmartLic Pro — Quanto custa filtrar licitações com inteligência"
  - `/features` → "O que muda no seu resultado com SmartLic"
  - `/ajuda` → "Perguntas frequentes sobre análise de licitações | SmartLic"
  - `/login` → "Acesse suas análises | SmartLic"
  - `/signup` → "Comece a filtrar licitações | SmartLic"
  - `/sobre` → "Quem somos e como avaliamos licitações | SmartLic" (se GTM-COPY-005 implementada)
- [ ] Arquivos: respectivos `page.tsx`

### AC6 — Structured Data (JSON-LD)
- [ ] Schema `Organization` na homepage:
  - name: "SmartLic"
  - legalName: "CONFENGE Avaliações e Inteligência Artificial LTDA"
  - url, logo, contactPoint
- [ ] Schema `SoftwareApplication` na homepage:
  - applicationCategory: "BusinessApplication"
  - operatingSystem: "Web"
- [ ] Schema `FAQPage` na `/ajuda`:
  - Todas as perguntas/respostas em format JSON-LD
- [ ] Arquivo: `layout.tsx` (Organization), `ajuda/page.tsx` (FAQ)

### AC7 — Heading Hierarchy (H1-H6)
- [ ] Auditar e corrigir hierarquia de headings em todas as páginas
- [ ] Cada página tem exatamente 1 `<h1>` que responde a intenção de busca
- [ ] H2s organizam seções logicamente
- [ ] Nenhum heading skip (H1 → H3 sem H2)
- [ ] H1 da landing = headline principal (AC1 de GTM-COPY-001)

### AC8 — Conteúdo AI-Friendly
- [ ] Textos estruturados com perguntas e respostas claras
- [ ] Parágrafos curtos (max 3 linhas)
- [ ] Listas com bullets para features/critérios
- [ ] FAQ com formato pergunta-resposta direta
- [ ] Facilita extração por LLMs para citação em respostas automáticas

### AC9 — Canonical URLs
- [ ] Cada página tem `<link rel="canonical">` correto
- [ ] Sem URLs duplicadas (trailing slash, query params)
- [ ] Arquivo: `layout.tsx` ou per-page

### AC10 — Robots & Sitemap
- [ ] Verificar `robots.txt` permite indexação das páginas públicas
- [ ] Bloqueia páginas autenticadas (`/dashboard`, `/pipeline`, `/conta`, etc.)
- [ ] Sitemap XML inclui todas as páginas públicas com lastmod
- [ ] Arquivos: `public/robots.txt`, `app/sitemap.ts` (se Next.js)

## Arquivos Impactados

| Arquivo | Mudança |
|---------|---------|
| `frontend/app/layout.tsx` | AC1-4, AC6, AC9 |
| `frontend/app/planos/page.tsx` | AC5 |
| `frontend/app/features/page.tsx` | AC5 |
| `frontend/app/ajuda/page.tsx` | AC5, AC6 |
| `frontend/app/login/page.tsx` | AC5 |
| `frontend/app/signup/page.tsx` | AC5 |
| `frontend/app/sobre/page.tsx` | AC5 (se existir) |
| `frontend/app/sitemap.ts` | AC10 (**NOVO** ou atualizado) |
| `frontend/public/robots.txt` | AC10 |
| Todos os componentes com headings | AC7 |

## Notas de Implementação

- Next.js 14 suporta `metadata` export nativo em cada `page.tsx` — usar isso
- Structured data via `<script type="application/ld+json">` no layout ou per-page
- Sitemap pode usar `generateStaticParams` do Next.js ou ser estático
- Testar com: Google Rich Results Test, Schema.org validator
- Claims não verificáveis ("500+ empresas") devem ser removidos ou substituídos

## Definition of Done

- [ ] ACs 1-10 verificados
- [ ] Schema validation (no errors)
- [ ] Mobile-friendly test (Google)
- [ ] Zero regressions
- [ ] Commit: `feat(frontend): GTM-COPY-006 — metadata SEO e conteúdo AI-friendly`
