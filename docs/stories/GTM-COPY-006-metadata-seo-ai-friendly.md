# GTM-COPY-006: Metadata SEO & Conteúdo AI-Friendly

**Épico:** GTM-COPY — Reposicionamento Estratégico de Comunicação
**Prioridade:** P1
**Tipo:** Enhancement
**Estimativa:** M (8-10 ACs)
**Depende de:** GTM-COPY-001 (metadata reflete nova copy)
**Status:** COMPLETED (2026-02-22)

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
- [x] Novo title reflete posicionamento de decisão estratégica (não busca)
- [x] Formato: "SmartLic — [promessa de valor em licitações]"
- [x] Máximo 60 caracteres para não truncar em SERPs
- [x] Arquivo: `layout.tsx`

**Implementado:** `SmartLic — Filtre Licitações por Viabilidade Real` (49 chars)

### AC2 — Meta Description Principal
- [x] Nova description orientada a resultado prático
- [x] Inclui: o que faz + para quem + diferencial
- [x] Máximo 155 caracteres
- [x] Remove claim de "500+ empresas" (não verificável)
- [x] Arquivo: `layout.tsx`

**Implementado:** "Analise a viabilidade de licitações antes de investir tempo. SmartLic cruza seu perfil com cada edital e recomenda apenas o que tem chance real de retorno." (155 chars)

### AC3 — Keywords Estratégicas
- [x] Migrar de keywords genéricas para território de decisão:
  - "como avaliar licitação antes de participar"
  - "filtrar licitações por viabilidade"
  - "quais licitações vale a pena participar"
  - "análise de viabilidade de licitação"
  - "priorizar editais por chance de vitória"
  - "como não perder tempo com licitação errada"
  - "filtro estratégico de licitações"
- [x] Keywords refletem intenção de quem já está sob pressão de decisão
- [x] Arquivo: `layout.tsx`

**Implementado:** 9 keywords de decisão (+ "inteligência de decisão em licitações", "avaliação objetiva de editais públicos")

### AC4 — Open Graph Tags
- [x] OG title e description alinhados com nova copy
- [x] OG image mantida (ou atualizada se existir nova arte)
- [x] Twitter cards atualizados (sem handles — SmartLic não tem Twitter)
- [x] Arquivo: `layout.tsx`

### AC5 — Per-Page Metadata
- [x] Cada página com title e description únicos e relevantes:
  - `/planos` → "Investimento SmartLic Pro — Quanto Custa Filtrar com Inteligência"
  - `/features` → "O Que Muda no Seu Resultado com Avaliação de Viabilidade"
  - `/ajuda` → "Perguntas Frequentes sobre Análise de Licitações"
  - `/login` → "Acesse Suas Análises"
  - `/signup` → "Comece a Filtrar Licitações por Viabilidade"
  - `/sobre` → N/A (GTM-COPY-005 não implementada)
- [x] Arquivos: respectivos `layout.tsx` (para "use client" pages) e `page.tsx` (server pages)

### AC6 — Structured Data (JSON-LD)
- [x] Schema `Organization` na homepage:
  - name: "SmartLic"
  - legalName: "CONFENGE Avaliações e Inteligência Artificial LTDA"
  - url, logo, contactPoint
- [x] Schema `SoftwareApplication` na homepage:
  - applicationCategory: "BusinessApplication"
  - operatingSystem: "Web"
  - AggregateOffer (R$1.599–R$1.999)
- [x] Schema `FAQPage` na `/ajuda`:
  - 15 perguntas/respostas em format JSON-LD via `FaqStructuredData.tsx`
- [x] Arquivo: `StructuredData.tsx` (Organization+WebSite+Software), `ajuda/FaqStructuredData.tsx` (FAQ)

### AC7 — Heading Hierarchy (H1-H6)
- [x] Auditar e corrigir hierarquia de headings em todas as páginas
- [x] Cada página tem exatamente 1 `<h1>` que responde a intenção de busca
- [x] H2s organizam seções logicamente
- [x] Nenhum heading skip (H1 → H3 sem H2)
- [x] H1 da landing = headline principal (AC1 de GTM-COPY-001)

**Corrigido:**
- `InstitutionalSidebar.tsx`: H1 → H2 (sidebar headline é secundário à page H1)
- `buscar/page.tsx`: Nav-bar H1 "Buscar Licitacoes" → `<span>` (page H1 is "Busca de Licitações")
- `login/page.tsx`: H1 changed to "Acesse suas análises" (search-intent, not brand name)

### AC8 — Conteúdo AI-Friendly
- [x] Textos estruturados com perguntas e respostas claras
- [x] Parágrafos curtos (max 3 linhas)
- [x] Listas com bullets para features/critérios
- [x] FAQ com formato pergunta-resposta direta
- [x] Facilita extração por LLMs para citação em respostas automáticas

**Já existente:** FAQ accordion em `/ajuda` e `/planos`, bullet lists em features, short paragraphs throughout. FAQPage JSON-LD (AC6) potencializa extração por LLMs.

### AC9 — Canonical URLs
- [x] Cada página tem `<link rel="canonical">` correto
- [x] Sem URLs duplicadas (trailing slash, query params)
- [x] Arquivo: `layout.tsx` + per-page layouts

**Implementado:** Canonical em layout.tsx (root) + canonical em cada route layout (planos, ajuda, login, signup, features)

### AC10 — Robots & Sitemap
- [x] Verificar `robots.txt` permite indexação das páginas públicas
- [x] Bloqueia páginas autenticadas (`/dashboard`, `/pipeline`, `/conta`, etc.)
- [x] Sitemap XML inclui todas as páginas públicas com lastmod
- [x] Arquivos: `public/robots.txt`, `app/sitemap.ts`

**Implementado:**
- `robots.txt`: Allow public pages, Disallow /admin, /dashboard, /pipeline, /conta, /mensagens, /historico, /onboarding, /auth/callback, /api, /redefinir-senha
- `sitemap.ts`: 9 public pages (home, planos, features, ajuda, pricing, signup, login, termos, privacidade) with appropriate priorities

## Arquivos Impactados

| Arquivo | Mudança |
|---------|---------|
| `frontend/app/layout.tsx` | AC1-4, AC9 — new title, description, keywords, OG, Twitter |
| `frontend/app/components/StructuredData.tsx` | AC6 — updated Organization (legal name), SoftwareApplication (AggregateOffer), descriptions |
| `frontend/app/features/page.tsx` | AC5 — updated metadata + canonical |
| `frontend/app/planos/layout.tsx` | AC5 — **NEW** per-page metadata |
| `frontend/app/ajuda/layout.tsx` | AC5, AC6 — **NEW** per-page metadata + FaqStructuredData |
| `frontend/app/ajuda/FaqStructuredData.tsx` | AC6 — **NEW** FAQPage JSON-LD schema |
| `frontend/app/login/layout.tsx` | AC5 — **NEW** per-page metadata + noindex |
| `frontend/app/login/page.tsx` | AC7 — H1 text updated to "Acesse suas análises" |
| `frontend/app/signup/layout.tsx` | AC5 — **NEW** per-page metadata |
| `frontend/app/components/InstitutionalSidebar.tsx` | AC7 — H1 → H2 (unique H1 per page) |
| `frontend/app/buscar/page.tsx` | AC7 — nav-bar H1 → span (unique H1 per page) |
| `frontend/app/sitemap.ts` | AC10 — expanded to 9 public pages |
| `frontend/public/robots.txt` | AC10 — block authenticated pages |
| `frontend/__tests__/components/InstitutionalSidebar.test.tsx` | Tests — updated heading level 1 → 2 |

## Definition of Done

- [x] ACs 1-10 verificados
- [x] Schema validation (JSON-LD structures follow schema.org specs)
- [x] TypeScript clean (npx tsc --noEmit passes)
- [x] Zero regressions (42 fail / 2281 pass = pre-existing baseline)
- [x] Commit: `feat(frontend): GTM-COPY-006 — metadata SEO e conteúdo AI-friendly`
