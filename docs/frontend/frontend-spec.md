# SmartLic - Frontend/UX: GTM Readiness Assessment

**Data:** 2026-03-12 | **Auditor:** @ux-design-expert | **Foco:** Prontidao para Go-To-Market
**Stack:** Next.js 16, React 18, TypeScript 5.9, Tailwind CSS 3
**URL:** https://smartlic.tech
**Versao:** 2.0 (sobrescreve auditoria 2026-03-10)

---

## 1. Resumo - Prontidao do Frontend

| Area | Status GTM | Justificativa |
|------|-----------|---------------|
| Core UX (Search) | PRONTO | Pipeline completo, 17 banners de estado, SSE progress |
| Onboarding | PRONTO | Wizard 3 etapas com Zod validation |
| Billing/Pricing | PRONTO | 3 planos, toggle periodo, Stripe checkout |
| Dashboard | PRONTO | Analytics com retry backoff, 6 custom hooks |
| Pipeline Kanban | PRONTO | @dnd-kit code-split, mobile tabs alternativo |
| Design System | PARCIAL | Tokens CSS definidos, mas apenas 6 componentes UI base |
| Accessibility | PARCIAL | Skip link, ARIA em auth, mas gaps em FAQ e reduced-motion |
| Performance | PARCIAL | Code-split em pipeline, mas next/image em apenas 1 pagina |
| Mobile/Responsive | PRONTO | BottomNav + Sidebar, pull-to-refresh, touch targets 44px |
| SEO | PRONTO | Metadata, sitemap, OG tags, structured data, RSS |
| Tests | PRONTO | 2681+ testes, 60 E2E Playwright |

**Veredito: PRONTO PARA GTM** com 2 bloqueadores de baixo esforco.

---

## 2. Bloqueadores GTM

### BLOQ-UX-01: Pagina de Privacidade com CNPJ Placeholder (LEGAL)
- `app/privacidade/page.tsx:28` — "CNPJ sob o n. XX.XXX.XXX/0001-XX"
- **Impacto GTM:** Documento legal incompleto. RISCO JURIDICO
- **Esforco:** 5 minutos

### BLOQ-UX-02: Rota /pipeline Nao Protegida no Middleware
- `middleware.ts` — `/pipeline` ausente da lista de rotas protegidas
- Guard client-side existe mas middleware e a camada de seguranca
- **Esforco:** 1 linha

---

## 3. Fixes Rapidos Pre-GTM (< 4h total)

| # | Issue | Arquivo | Esforco |
|---|-------|---------|---------|
| 1 | CNPJ placeholder na privacidade | `privacidade/page.tsx:28` | 5min |
| 2 | /pipeline no middleware | `middleware.ts` | 5min |
| 3 | Icone errado Dashboard (BottomNav mobile) | `BottomNav.tsx:48` | 5min |
| 4 | `useReducedMotion()` em 9 arquivos Framer | 9 arquivos | 2h |
| 5 | `aria-expanded` no FAQ accordion | `planos/page.tsx:644` | 30min |
| 6 | `aria-labelledby` no pipeline modal | `pipeline/page.tsx:341` | 15min |

**Total estimado: ~3.5h para resolver todos os 6 items.**

---

## 4. Selling Points UX para GTM

### Resiliencia de UX (Diferencial Competitivo)
- 17 banners distintos cobrem CADA cenario de degradacao
- `SearchStateManager` com transicoes animadas entre fases
- `EnhancedLoadingProgress` com carousel educativo B2G
- SSE dual-connection: stream real + fallback time-based

### Billing UX Completa
- Trial 14d sem cartao com CTAs contextuais
- `PaymentFailedBanner`, `TrialPaywall`, `TrialUpsellCTA` — funil completo
- `CancelSubscriptionModal` com confirmacao
- `PlanToggle` com 3 periodos e calculo de economia

### Mobile-First
- `BottomNav` + `Sidebar` responsivos
- Pull-to-refresh na busca
- `PipelineMobileTabs` como alternativa ao kanban
- Touch targets >= 44px

### Power User Features
- Keyboard shortcuts: `Ctrl+K`, `Ctrl+Enter`, `Ctrl+A`, `/`, `Escape`
- Cross-tab sync via BroadcastChannel
- Onboarding tours com Shepherd.js
- 22 paginas, 33+ componentes de busca, 30+ componentes compartilhados

---

## 5. Debitos Pos-GTM (Nao Bloqueiam)

| ID | Issue | Prioridade |
|----|-------|------------|
| TD-M4 | CSS tokens em 3 sintaxes | Media |
| TD-M7 | next/image em 1 pagina apenas | Media |
| TD-H2 | God hook 40+ valores | Media |
| TD-M8 | Loading spinner inline 3x | Baixa |
| TD-L5 | 20+ `any` em prod | Baixa |
| TD-L6 | 8 localStorage sem abstracao | Baixa |
| TD-L9 | /planos + /pricing duplicados | Baixa |

---

## 6. Checklist GTM - Frontend

- [x] Fluxo de busca completo e funcional
- [x] Onboarding wizard operacional
- [x] Pricing page com 3 planos + Stripe checkout
- [x] Dashboard com analytics
- [x] Pipeline kanban funcional
- [x] Mobile responsive com BottomNav
- [x] SEO: metadata, sitemap, OG tags, structured data
- [x] Error boundaries hierarquicos (3 niveis)
- [x] Testes: 2681 unit + 60 E2E
- [x] 17 banners de resiliencia
- [x] Keyboard shortcuts
- [x] Cross-tab sync
- [ ] CNPJ na pagina de privacidade (5min)
- [ ] /pipeline no middleware (5min)
- [ ] Icone Dashboard no BottomNav (5min)
