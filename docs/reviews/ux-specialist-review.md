# UX Specialist Review

**Revisor:** @ux-design-expert (Uma)
**Data:** 2026-03-30
**Documento revisado:** docs/prd/technical-debt-DRAFT.md (Section 3 + Section 6)

---

## Resumo

A Secao 3 do DRAFT (Debitos de Frontend/UX) esta **direccionalmente correta**, mas contem **2 imprecisoes factuais** que alteram severidade e esforco. O codebase demonstra trabalho progressivo de acessibilidade (28+ usos de `aria-live`/`role="alert"` so no modulo de busca), e `prefers-reduced-motion` ja esta implementado globalmente em `globals.css`. A saude geral do frontend e **7.5/10** para um produto POC-to-production.

**Esforco total ajustado:** ~63h (vs ~71h no DRAFT, reducao de 8h por correcoes factuais).

---

## Debitos Validados

| ID | Debito | Severidade Original | Severidade Ajustada | Horas Orig. | Horas Ajust. | Impacto UX | Notas |
|----|--------|---------------------|---------------------|-------------|--------------|------------|-------|
| DEBT-FE-001 | useSearchOrchestration mega-hook | Alta | **Alta (confirmada)** | 12h | 12h | Risco de regressao na feature principal | 618 LOC, orquestra 12+ sub-hooks. Confirmado no codigo. |
| DEBT-FE-002 | ViabilityBadge usa `title` para dados criticos | Alta | **Alta (confirmada)** | 4h | 4h | Dados de viabilidade inacessiveis em mobile/touch | `title` attr confirmado em L105. `aria-label` existe mas so com nivel, nao breakdown. |
| DEBT-FE-003 | Sem `aria-live` para resultados de busca | Media | **Baixa** | 4h | **2h** | Parcialmente resolvido | **VER DETALHES ABAIXO** |
| DEBT-FE-004 | 12 banners na busca — cognitive overload | Media | **Media (confirmada)** | 8h | 8h | Sobrecarga cognitiva real | 12 banners confirmados no diretorio de componentes. |
| DEBT-FE-005 | /admin usa useState + fetch manual | Media | **Media (confirmada)** | 4h | 4h | Dados desatualizados para admin | 20+ chamadas fetch manuais confirmadas nos arquivos de admin. |
| DEBT-FE-006 | Landmarks HTML inconsistentes | Media | **Baixa** | 3h | **2h** | Menos grave do que reportado | **VER DETALHES ABAIXO** |
| DEBT-FE-007 | Campos sem `aria-describedby` | Media | **Media (confirmada)** | 2h | 2h | Falta de contexto para screen readers | Apenas ValorFilter tem `aria-describedby` parcial. |
| DEBT-FE-008 | Feature gates hardcoded | Media | **Media (confirmada)** | 6h | 6h | Nenhum impacto direto em UX | Impacto em DX e flexibilidade. |
| DEBT-FE-009 | SVGs inline vs lucide-react | Baixa | **Baixa (confirmada)** | 3h | 3h | Bundle size, manutencao | MobileDrawer tem 10+ SVGs inline. BottomNav ja migrou para lucide-react. |
| DEBT-FE-010 | Raw hex values vs tokens semanticos | Baixa | **Baixa (confirmada)** | 4h | 4h | Inconsistencia visual sutil | Hex encontrados em KeyboardShortcutsHelp, ProfileCongratulations, TestimonialSection. |
| DEBT-FE-011 | Tipo `any` em API proxy routes | Media | **Removido** | 4h | **0h** | Nenhum | **VER DETALHES ABAIXO** |
| DEBT-FE-012 | Focus order em BuscarModals | Baixa | **Baixa (confirmada)** | 2h | 2h | Edge case de acessibilidade | BuscarModals usa `<Dialog>` component; risco e de modais sobrepostos. |
| DEBT-FE-013 | Sem testes a11y automatizados | Media | **Baixa** | 6h | **3h** | Regressoes de a11y nao detectadas | **VER DETALHES ABAIXO** |
| DEBT-FE-014 | Sem prefers-reduced-motion | Baixa | **Removido** | 3h | **0h** | Nenhum — ja implementado | **VER DETALHES ABAIXO** |
| DEBT-FE-015 | SEO pages thin content | Baixa | **Baixa (confirmada)** | 4h | 4h | SEO | Sem impacto direto na UX do produto. |

### Detalhes dos Ajustes

**DEBT-FE-003 (aria-live) -- REBAIXADA para Baixa, 2h**

O DRAFT afirma que "resultados de busca nao anunciam dinamicamente". Isso e **parcialmente incorreto**. Verificacao no codigo encontrou **28+ usos de `aria-live` e `role="alert"`** no modulo de busca:

- `ResultsHeader.tsx` — `aria-live="polite" aria-atomic="true"` no contador de resultados
- `EnhancedLoadingProgress.tsx` — `aria-live="polite"` no container de progresso
- `SearchStateManager.tsx` — 4x `aria-live="assertive"` para transicoes de estado
- `DataQualityBanner.tsx`, `ExpiredCacheBanner.tsx`, `RefreshBanner.tsx` — todos com `aria-live="polite"`
- `SearchErrorBanner.tsx`, `SearchErrorBoundary.tsx` — `role="alert" aria-live="assertive"`
- `EmptyResults.tsx`, `ResultsLoadingSection.tsx` — `aria-live="polite"`

O gap restante e estreito: (1) nem todos os 12 banners tem `aria-live` consistente (CacheBanner, FilterRelaxedBanner, TruncationWarningBanner, OnboardingBanner, SourcesUnavailable, PartialResultsPrompt faltam), e (2) o anuncio de "X oportunidades encontradas" apos conclusao da busca poderia ser mais explicitamente marcado. Isso e 2h de trabalho, nao 4h.

**DEBT-FE-006 (Landmarks) -- REBAIXADA para Baixa, 2h**

Verificacao no codigo encontrou `<main>` em **25+ paginas**, incluindo:
- `(protected)/layout.tsx` — `<main id="main-content">`
- `buscar/page.tsx` — `<main id="buscar-content">`
- `pipeline/page.tsx`, `alertas/page.tsx`, `status/page.tsx`, `conta/layout.tsx` — todos com `<main>`
- Todas as paginas de landing, blog, sobre — `<main>` presente

O gap real e menor: algumas paginas de `conta/equipe/` tem multiplos `<main>` em branches condicionais, e o `id` nao e padronizado (alguns `main-content`, outros `buscar-content`, outros sem id). Isso e 2h, nao 3h.

**DEBT-FE-011 (Tipo `any`) -- REMOVIDO, 0h**

Busca por `: any` nos arquivos de API proxy (`frontend/app/api/**/*.ts`) retornou **zero resultados**. O DRAFT usa linguagem especulativa ("potencial uso de any") e a verificacao no codigo nao confirma o problema. Se `any` existir em outros locais, deve ser catalogado como debito de type safety geral, nao especifico a API proxies.

**DEBT-FE-013 (Testes a11y) -- REBAIXADA para Baixa, 3h**

O DRAFT afirma "nao ha evidencia de uso sistematico". Isso e **parcialmente incorreto**. O arquivo `frontend/e2e-tests/accessibility-audit.spec.ts` existe e implementa auditorias axe-core em 5 paginas criticas (login, buscar, dashboard, pipeline, planos). O arquivo importa `AxeBuilder` de `@axe-core/playwright` e valida zero violacoes criticas.

O gap restante: expandir a cobertura para mais paginas (onboarding, conta, mensagens, admin) e integrar no CI pipeline se ainda nao estiver. Isso e 3h, nao 6h.

**DEBT-FE-014 (prefers-reduced-motion) -- REMOVIDO, 0h**

O DRAFT afirma que animacoes "nao verificam prefers-reduced-motion sistematicamente". Isso e **factualmente incorreto**. Verificacao no codigo encontrou:

1. `globals.css` L349-355: Media query global `@media (prefers-reduced-motion: reduce)` que desabilita **todas** as animacoes e transicoes via `animation-duration: 0.01ms !important` e `transition-duration: 0.01ms !important`.
2. `AnimateOnScroll.tsx`: Verifica `prefers-reduced-motion` via `window.matchMedia`.
3. `useInView.ts`: Verifica `prefers-reduced-motion` via `window.matchMedia`.
4. `SectorsGrid.tsx`: Documenta respeito a `prefers-reduced-motion`.

A implementacao global em CSS e a abordagem mais robusta possivel — afeta todas as animacoes CSS e Tailwind. Animacoes Framer Motion sao parcialmente cobertas (o CSS override funciona para `transition` mas nao para transforms puros do Framer). O gap residual e minimo e nao justifica um debito separado.

---

## Debitos Removidos

| ID | Debito | Justificativa |
|----|--------|---------------|
| DEBT-FE-011 | Tipo `any` em API proxy routes | Busca no codigo retornou zero ocorrencias de `: any` em `frontend/app/api/**/*.ts`. Debito especulativo nao confirmado. |
| DEBT-FE-014 | Sem prefers-reduced-motion | Implementacao global ja existe em `globals.css` + verificacoes em `AnimateOnScroll.tsx` e `useInView.ts`. |

---

## Debitos Adicionados

| ID | Debito | Severidade | Horas | Impacto UX |
|----|--------|-----------|-------|-----------|
| DEBT-FE-016 | IDs duplicados de main-content | Media | 1h | Skip navigation quebrado em /buscar |
| DEBT-FE-017 | Landing page com 13 child components "use client" | Alta | 10h | Performance de aquisicao degradada |
| DEBT-FE-018 | Indicadores de viabilidade apenas por cor | Media | 3h | WCAG 1.4.1 — informacao inacessivel para daltonicos |
| DEBT-FE-019 | Shepherd.js carregado eagerly em todas as paginas protegidas | Baixa | 2h | ~15KB JS desnecessario por pagina |
| DEBT-FE-020 | Pipeline kanban sem anuncios de drag para screen readers | Media | 4h | Drag-and-drop indescoberto para usuarios de screen reader |

### DEBT-FE-016: IDs duplicados de main-content (Media, 1h)

Tres arquivos definem `<main id="main-content">` ou similar: `(protected)/layout.tsx`, `page.tsx` (landing), e `buscar/page.tsx` usa `<main id="buscar-content">`. Quando `/buscar` renderiza fora do route group `(protected)`, pode criar conflito de landmarks. Solucao: unificar a estrategia de `id` para o skip navigation link.

### DEBT-FE-017: Landing page hydration excessiva (Alta, 10h)

A `page.tsx` da landing e um Server Component, mas **todos os 13 child components** usam `"use client"`. Apenas 3 realmente precisam de Framer Motion. Os outros 10 usam `"use client"` apenas para `useState`/`useEffect`/`useInView`. Isso forca hydration de todo o conteudo de marketing no client-side, degradando TTFB, LCP e SEO — a landing page e a principal superficie de aquisicao.

### DEBT-FE-018: Indicadores apenas por cor (Media, 3h)

ViabilityBadge ja exibe texto ("Viabilidade alta/media/baixa") ao lado da cor, o que e positivo. Porem, o `score` numerico e o breakdown de fatores so aparecem no `title` tooltip (inacessivel em mobile). Alem disso, ReliabilityBadge e LlmSourceBadge podem ter dependencia de cor sem texto complementar suficiente. Requer auditoria e ajuste WCAG 1.4.1.

### DEBT-FE-019: Shepherd.js eager loading (Baixa, 2h)

`shepherd.js` (~15KB) e importado em `useShepherdTour.ts` e `useOnboarding.tsx`, carregados em todas as paginas protegidas independente de o usuario ja ter completado o tour. Deveria usar `next/dynamic` para lazy-load apenas quando o tour e ativado.

### DEBT-FE-020: Pipeline kanban sem anuncios de drag (Media, 4h)

`PipelineKanban.tsx` ja configura `KeyboardSensor` com `sortableKeyboardCoordinates` (keyboard DnD funciona). O que falta: anuncios para screen readers via `accessibility` prop do `DndContext` (`onDragStart`, `onDragOver`, `onDragEnd`, `onDragCancel`) e `aria-roledescription="sortable"` nos cards.

---

## Respostas ao Architect

### 1. DEBT-FE-004 (12 banners): Hierarquia de prioridade recomendada

**Hierarquia proposta (alta para baixa):**

| Prioridade | Banners | Comportamento |
|------------|---------|---------------|
| P0 — Bloqueante | SearchErrorBanner, SourcesUnavailable | Exibir SEMPRE, suprimir todos abaixo |
| P1 — Acao necessaria | PartialResultsPrompt, PartialTimeoutBanner, UfFailureDetail | Exibir se P0 ausente |
| P2 — Informativo importante | CacheBanner, ExpiredCacheBanner, DataQualityBanner | Exibir se P0 e P1 ausentes, maximo 1 |
| P3 — Informativo secundario | FilterRelaxedBanner, TruncationWarningBanner, RefreshBanner | Exibir em area separada (inline/tooltip) |
| P4 — Onboarding | OnboardingBanner | Exibir apenas para novos usuarios, dismissible permanente |

**Consolidacoes possiveis:**
- `CacheBanner` + `ExpiredCacheBanner` + `RefreshBanner` podem ser um unico `CacheStatusBanner` com 3 estados
- `PartialResultsPrompt` + `PartialTimeoutBanner` podem ser um unico `PartialBanner` com variantes

**Pode ser removido:** `OnboardingBanner` pode ser substituido pelo tour Shepherd.js que ja existe, evitando duplicacao de onboarding.

**Recomendacao:** Implementar um `BannerStack` component que recebe todos os banners e exibe apenas os de maior prioridade (maximo 2 simultaneos). Isso reduz cognitive overload sem perder informacao.

### 2. DEBT-FE-002 (ViabilityBadge): Padrao de tooltip acessivel

**Recomendacao: Radix Tooltip com fallback expandivel.**

Opcoes analisadas:

| Opcao | Pros | Contras | Veredicto |
|-------|------|---------|-----------|
| Radix Tooltip (`@radix-ui/react-tooltip`) | Acessivel (aria-describedby automatico), keyboard support, delay configuravel | Nao funciona em touch-only devices (requer hover intent) | **Melhor para desktop** |
| Popover customizado | Funciona em touch (tap to open), pode ter close button | Mais complexo, precisa gerenciar focus | **Melhor para mobile** |
| Expandir inline (click to toggle) | Funciona em todos os devices, sem overlay | Ocupa espaco, pode poluir a lista de resultados | **Melhor para a11y pura** |

**Recomendacao final:** Combinacao de Radix Tooltip (desktop hover) + tap-to-expand (mobile). O `@radix-ui/react-slot` ja e dependencia do projeto, entao adicionar `@radix-ui/react-tooltip` e trivial. Para mobile, ao detectar touch device, converter para `<details><summary>` pattern nativo que e totalmente acessivel.

O breakdown **precisa** estar visivel sem interacao em cenarios de comparacao (quando usuario esta decidindo entre oportunidades). Considerar adicionar um mini bar chart visual inline que mostra os 4 fatores sem precisar de tooltip.

### 3. DEBT-FE-001 (useSearchOrchestration): Decomposicao sugerida

**A decomposicao faz sentido do ponto de vista de UX.** Analise do hook (618 LOC):

| Bloco | LOC | Dependencias compartilhadas | Pode separar? |
|-------|-----|---------------------------|---------------|
| Trial/Plan state | ~80 | `planInfo`, `session` | **Sim** — `useTrialOrchestration` |
| Tours (search + results) | ~70 | `session`, `trackEvent` | **Sim** — `useSearchTours` |
| UI state (modais, drawer, tips) | ~40 | `planInfo` (upgrade modal) | **Sim** — `useSearchUIState` |
| PDF generation | ~40 | `session`, `search.searchId`, `filters.sectorName` | **Sim** — `usePdfGeneration` |
| Search core + cross-tab | ~60 | `filters`, `search` | **Nao** — core, manter |
| Computed searchResultsProps | ~120 | Tudo acima | **Nao** — aggregator, manter |
| Keyboard shortcuts | ~10 | `filters`, `search` | Ja e hook separado (useKeyboardShortcuts) |

**Estado compartilhado que impede separacao total:** `isTrialExpired` afeta tanto a logica de trial conversion quanto o `searchResultsProps`. `session` e usado por trial, tours, PDF, e busca. Porem, esses valores podem ser passados como parametros para os sub-hooks.

**Decomposicao recomendada:**
1. `useTrialOrchestration(planInfo, session)` — trial days, expired, conversion modal, grace period
2. `useSearchTours(session, trackEvent)` — search tour, results tour, onboarding coordination
3. `usePdfGeneration(session, searchId, sectorName)` — PDF modal, loading, download
4. `useSearchUIState()` — upgrade modal, keyboard help, customize panel, first use tip, drawer

O `useSearchOrchestration` final ficaria como **compositor** com ~200 LOC que importa esses 4 hooks + `useSearchFilters` + `useSearch` e monta o `searchResultsProps`. Reducao de 618 para ~200 LOC no hook principal.

### 4. DEBT-FE-014 (prefers-reduced-motion): Quais animacoes sao essenciais

**Debito removido** — ja implementado globalmente via `globals.css`. Porem, para referencia futura:

**Essenciais (manter com reduced-motion):**
- Loading spinners em botoes (feedback de acao em progresso)
- Progress bar da busca (feedback de operacao longa)
- Focus ring transitions (feedback de navegacao por teclado)

**Decorativas (desabilitar com reduced-motion):**
- Landing page scroll animations (fade-in-up, stagger)
- Gradient animations em hero
- Float/bounce animations em icones
- Slide-in de modais (pode substituir por fade instantaneo)

A implementacao atual em `globals.css` desabilita **todas** as animacoes com `animation-duration: 0.01ms !important`, o que e a abordagem mais segura. Para preservar animacoes essenciais, seria necessario exempta-las com `@media (prefers-reduced-motion: no-preference)` wrapper, mas isso e refinamento futuro, nao debito.

### 5. DEBT-FE-010 (tokens semanticos): Componentes com maiores inconsistencias

**Componentes com raw hex/var() confirmados:**

| Componente | Ocorrencias | Severidade Visual |
|-----------|-------------|-------------------|
| `KeyboardShortcutsHelp.tsx` | 2 (raw hex em bg e hover) | Baixa — modal pouco visivel |
| `ProfileCongratulations.tsx` | 5 (confetti colors com fallback hex) | Minima — animacao momentanea |
| `TestimonialSection.tsx` | 1 (badge bg com fallback hex) | Baixa — secao de marketing |
| `ViabilityBadge.tsx` | 0 (usa Tailwind tokens corretamente) | N/A |

**Inventory:** A maioria dos componentes criticos (SearchForm, ResultCard, FilterPanel, etc.) usam tokens semanticos corretamente via classes Tailwind (`text-ink`, `bg-canvas`, `border-strong`, etc.). As inconsistencias estao concentradas em componentes secundarios e usam `var()` com fallback hex, o que significa que **funcionam corretamente** mesmo sem o token — o hex e apenas fallback. Isso reduz a urgencia deste debito.

---

## Analise de Impacto UX

### Jornadas Afetadas

| Jornada | Debitos que Impactam | Severidade do Impacto |
|---------|---------------------|----------------------|
| **Primeiro acesso (landing -> signup)** | DEBT-FE-017 (hydration excessiva) | Alta — LCP degradado, conversao afetada |
| **Busca de licitacoes** | DEBT-FE-001 (mega-hook), DEBT-FE-002 (tooltip), DEBT-FE-004 (banners) | Media — funcional mas com riscos de regressao e sobrecarga |
| **Analise de resultados** | DEBT-FE-002 (viabilidade inacessivel), DEBT-FE-018 (cor-only) | Media — dados criticos dependem de hover |
| **Pipeline de oportunidades** | DEBT-FE-020 (drag a11y) | Baixa — funciona para 95%+ dos usuarios |
| **Administracao** | DEBT-FE-005 (stale data) | Baixa — afeta apenas admins internos |
| **Navegacao por screen reader** | DEBT-FE-003, DEBT-FE-006, DEBT-FE-007, DEBT-FE-016 | Media — gaps pontuais mas nao bloqueantes |

### Metricas de UX Esperadas apos Resolucao

| Metrica | Antes | Depois (estimado) | Debitos Relacionados |
|---------|-------|-------------------|---------------------|
| Landing LCP | ~3.5s (estimado) | ~2.0s | DEBT-FE-017 |
| Landing TTI | ~4.5s (estimado) | ~2.5s | DEBT-FE-017 |
| WCAG 2.1 AA compliance | ~85% | ~95% | DEBT-FE-002, FE-003, FE-007, FE-016, FE-018, FE-020 |
| Cognitive load score (busca) | 7/10 (alto) | 4/10 (medio) | DEBT-FE-004 |
| Risco de regressao (busca) | Alto | Medio | DEBT-FE-001 |

---

## Recomendacoes de Design

### Quick Wins (< 4h cada)

1. **DEBT-FE-016 — Unificar IDs de main-content** (1h): Padronizar `id="main-content"` em um unico local. Quick win com impacto real em acessibilidade.

2. **DEBT-FE-007 — Adicionar aria-describedby em campos de busca** (2h): Linkar hints existentes ("Selecione um setor", "Minimo 3 caracteres") aos inputs. Ja existem os textos, falta o atributo.

3. **DEBT-FE-003 — Completar aria-live nos banners faltantes** (2h): Adicionar `aria-live="polite"` nos 6 banners que ainda nao tem.

4. **DEBT-FE-019 — Lazy-load Shepherd.js** (2h): Envolver import em `next/dynamic` para carregar apenas quando tour e ativado.

5. **DEBT-FE-018 — Auditoria de cor-only nos badges** (3h): Verificar e adicionar texto complementar onde necessario.

### Melhorias Estruturais

6. **DEBT-FE-001 — Decompor useSearchOrchestration** (12h): Extrair 4 sub-hooks conforme analise acima. Reduzir hook principal de 618 para ~200 LOC. Requer cobertura de testes antes.

7. **DEBT-FE-004 — BannerStack com sistema de prioridade** (8h): Implementar hierarquia de banners. Consolidar CacheBanner + ExpiredCacheBanner + RefreshBanner. Limitar a 2 banners simultaneos.

8. **DEBT-FE-002 — Tooltip acessivel para ViabilityBadge** (4h): Radix Tooltip (desktop) + tap-to-expand (mobile). Considerar mini bar chart inline para comparacao rapida.

9. **DEBT-FE-017 — Landing page RSC islands** (10h): Converter 10 de 13 child components para Server Components. Manter 3 como client islands (HeroSection, SectorsGrid, AnalysisExamplesCarousel).

10. **DEBT-FE-020 — Pipeline drag announcements** (4h): Adicionar `accessibility` prop no `DndContext` + `aria-roledescription` nos cards.

### Design System Evolution

11. **Extrair Select/Modal como primitivos compartilhados** (7h): Usar Radix UI primitives. 3+ implementacoes inconsistentes de Select e 4+ de Modal no codebase. `@radix-ui/react-slot` ja e dependencia.

12. **Padronizar Badge component** (3h): Extrair variantes de ViabilityBadge, ReliabilityBadge, LlmSourceBadge, plan badges em um Badge generico com props de cor, icone e tamanho.

---

## Parecer

O frontend do SmartLic esta em **bom estado para um produto POC-to-production (v0.5)**. Os padroes de UX criticos estao bem implementados: loading states robustos, error handling multi-nivel, onboarding completo, responsividade mobile, e trabalho progressivo de acessibilidade.

Os debitos reais se dividem em 3 categorias:

1. **Performance de aquisicao** (DEBT-FE-017): A landing page com hydration excessiva e o debito de maior impacto no negocio. Resolucao direta em metricas de conversao.

2. **Acessibilidade pontual** (DEBT-FE-002, FE-003, FE-007, FE-016, FE-018, FE-020): Gaps reais mas nao bloqueantes. Nenhum viola WCAG criticamente — sao melhorias de AA para AAA. Priorizar se houver planos de vender para orgaos publicos.

3. **Manutencao e risco de regressao** (DEBT-FE-001, FE-004, FE-005): Debitos de codigo que nao afetam o usuario diretamente mas aumentam custo de mudanca e risco de bugs. Resolver oportunisticamente durante feature work.

**Recomendacao de execucao:**
- **Sprint 1 (16h):** DEBT-FE-017 (landing RSC) + quick wins (FE-016, FE-007, FE-003, FE-019)
- **Sprint 2 (16h):** DEBT-FE-001 (decomposicao hook) + DEBT-FE-004 (banner stack)
- **Sprint 3 (12h):** DEBT-FE-002 (tooltip acessivel) + DEBT-FE-020 (pipeline a11y) + DEBT-FE-018 (cor-only audit)
- **Backlog:** FE-005, FE-008, FE-009, FE-010, FE-012, FE-015 — resolver durante feature work

---

*Revisao completa. Pronto para Fase 7 (@qa gate).*
