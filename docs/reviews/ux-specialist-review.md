# UX Specialist Review — GTM Readiness

**Date:** 2026-03-12 | **Agent:** @ux-design-expert | **Reviewing:** technical-debt-DRAFT.md v2.0
**Versao:** 2.0 (sobrescreve review 2026-03-10)

---

## Gate Status: APPROVED (com 2 fixes obrigatorios)

---

## Bloqueadores Confirmados

| # | Issue | Severidade | Fix | Esforco |
|---|-------|-----------|-----|---------|
| 1 | CNPJ placeholder privacidade | BLOQUEADOR | Inserir CNPJ real CONFENGE | 5min |
| 2 | /pipeline sem auth middleware | BLOQUEADOR | Adicionar a PROTECTED_ROUTES | 5min |

---

## Debitos Validados

| ID | Debito | Severidade | Horas | Prioridade | Impacto UX |
|----|--------|-----------|-------|------------|------------|
| UX-01 | Icone errado BottomNav Dashboard | Alta | 0.1h | Pre-GTM | Confusao mobile |
| UX-02 | Framer ignora reduced-motion | Media | 2h | Pre-GTM ideal | WCAG 2.3.3 |
| UX-03 | FAQ sem aria-expanded | Media | 0.5h | Pre-GTM ideal | Pricing inacessivel |
| UX-04 | Pipeline modal sem aria-labelledby | Media | 0.25h | Pre-GTM ideal | Dialog sem nome |
| UX-05 | CSS tokens 3 sintaxes | Media | 4h | Pos-GTM | Manutencao |
| UX-06 | next/image em 1 pagina | Media | 3h | Pos-GTM | CLS, performance |
| UX-07 | God hook 40+ valores | Media | 6h | Pos-GTM | Manutencao |
| UX-08 | Loading spinner inline 3x | Baixa | 1h | Pos-GTM | Inconsistencia |
| UX-09 | /planos + /pricing duplicados | Baixa | 1h | Pos-GTM | SEO |
| UX-10 | 8 localStorage sem abstracao | Baixa | 2h | Pos-GTM | Manutencao |

## Respostas ao Architect

**P1: BottomNav icone errado — fix trivial?**
R: SIM. Linha unica: trocar `icons.search` por `icons.layoutDashboard` (ou equivalente do Lucide) em `BottomNav.tsx:48`. Zero risco de regressao.

**P2: Framer Motion reduced-motion — pre ou pos-GTM?**
R: **Pre-GTM ideal, mas nao bloqueador.** A porcentagem de usuarios com reduced-motion habilitado e baixa (~5%), e a experiencia funciona sem reduzir — apenas anima quando nao deveria. Recomendo incluir no sprint pre-GTM (2h), mas se o timeline for apertado, pode ser pos-GTM sem risco significativo.

## Recomendacoes de Design

1. **AGORA:** CNPJ + /pipeline middleware (10min)
2. **Pre-GTM (3.5h):** Icone BottomNav + reduced-motion + FAQ ARIA + pipeline modal ARIA
3. **Pos-GTM Sprint 1:** CSS tokens unificacao + next/image
4. **Pos-GTM Sprint 2:** God hook decomposicao + localStorage abstracao

## Selling Points UX para Marketing

- 17 banners de estado = transparencia total
- Carousel educativo durante loading = UX diferenciada
- Keyboard shortcuts = ferramenta profissional
- Cross-tab sync = power user feature
- Mobile-first com pull-to-refresh e BottomNav
