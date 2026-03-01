# MKT-001 AC7 — Google Search Console & Rich Results Validation Report

**Story:** MKT-001 — Blog SEO + Structured Data
**AC:** AC7 — Rich results validation (FAQPage + Article + BreadcrumbList + Organization)
**Date:** _fill in after validation run_
**Validator:** _fill in (name / tool)_
**Environment:** Production — `https://smartlic.tech`

---

## How to Run the Automated Validation

```bash
# Local schema validation (no external services)
cd frontend
npx playwright test mkt-001-schema-validation --project=chromium

# CTA + internal link validation
npx playwright test mkt-001-cta-validation --project=chromium

# Full rich results + local JSON-LD extraction
npx playwright test mkt-001-rich-results --project=chromium

# All MKT-001 specs together
npx playwright test mkt-001 --project=chromium

# Against production
FRONTEND_URL=https://smartlic.tech npx playwright test mkt-001 --project=chromium

# Google Rich Results Test (manual — requires headed browser + human)
RUN_GOOGLE_RICH_RESULTS=1 npx playwright test mkt-001-rich-results --grep @manual --headed --project=chromium
```

---

## Acceptance Criteria Checklist

- [ ] All 30 posts return HTTP 200
- [ ] All 30 posts have `<script type="application/ld+json">` blocks
- [ ] Article schema: `headline`, `author`, `datePublished`, `publisher`, `url` present
- [ ] Article author: "Equipe SmartLic" + "Especialistas em Inteligência de Licitações Públicas"
- [ ] FAQPage schema: exactly 5 questions per post
- [ ] FAQPage answers: each answer 40–60 words
- [ ] BreadcrumbList schema: exactly 4 items with sequential `position`
- [ ] Organization schema: `name` + `url` present
- [ ] Inline CTA links: `utm_source=blog`, `utm_medium=cta`, `utm_content=<slug>`
- [ ] Final CTA section: "14 dias" + "sem cartão" text visible
- [ ] Internal blog links: >= 3 unique links per post
- [ ] Cross-cluster link: >= 1 link pointing to the other category cluster
- [ ] Canonical URL: `<link rel="canonical">` present and correct
- [ ] Google Rich Results Test: 0 errors per post (manual validation)

---

## Validation Table — All 30 Posts

| # | Slug | HTTP | Article | FAQPage | BreadcrumbList | Organization | FAQ Count | FAQ Word Range | Inline CTA | Final CTA | Internal Links | Cross-Cluster | Canonical | GSC Status |
|---|------|------|---------|---------|----------------|--------------|-----------|----------------|------------|-----------|----------------|---------------|-----------|------------|
| 1 | `como-aumentar-taxa-vitoria-licitacoes` | — | — | — | — | — | — | — | — | — | — | — | — | pending |
| 2 | `erro-operacional-perder-contratos-publicos` | — | — | — | — | — | — | — | — | — | — | — | — | pending |
| 3 | `vale-a-pena-disputar-pregao` | — | — | — | — | — | — | — | — | — | — | — | — | pending |
| 4 | `clausulas-escondidas-editais-licitacao` | — | — | — | — | — | — | — | — | — | — | — | — | pending |
| 5 | `reduzir-tempo-analisando-editais-irrelevantes` | — | — | — | — | — | — | — | — | — | — | — | — | pending |
| 6 | `disputar-todas-licitacoes-matematica-real` | — | — | — | — | — | — | — | — | — | — | — | — | pending |
| 7 | `estruturar-setor-licitacao-5-milhoes` | — | — | — | — | — | — | — | — | — | — | — | — | pending |
| 8 | `custo-invisivel-disputar-pregoes-errados` | — | — | — | — | — | — | — | — | — | — | — | — | pending |
| 9 | `escolher-editais-maior-probabilidade-vitoria` | — | — | — | — | — | — | — | — | — | — | — | — | pending |
| 10 | `licitacao-volume-ou-inteligencia` | — | — | — | — | — | — | — | — | — | — | — | — | pending |
| 11 | `orgaos-risco-atraso-pagamento-licitacao` | — | — | — | — | — | — | — | — | — | — | — | — | pending |
| 12 | `empresas-vencem-30-porcento-pregoes` | — | — | — | — | — | — | — | — | — | — | — | — | pending |
| 13 | `pipeline-licitacoes-funil-comercial` | — | — | — | — | — | — | — | — | — | — | — | — | pending |
| 14 | `ata-registro-precos-como-escolher` | — | — | — | — | — | — | — | — | — | — | — | — | pending |
| 15 | `equipe-40-horas-mes-editais-descartados` | — | — | — | — | — | — | — | — | — | — | — | — | pending |
| 16 | `aumentar-retencao-clientes-inteligencia-editais` | — | — | — | — | — | — | — | — | — | — | — | — | pending |
| 17 | `analise-edital-diferencial-competitivo-consultoria` | — | — | — | — | — | — | — | — | — | — | — | — | pending |
| 18 | `entregar-mais-resultado-clientes-sem-aumentar-equipe` | — | — | — | — | — | — | — | — | — | — | — | — | pending |
| 19 | `clientes-perdem-pregoes-boa-documentacao` | — | — | — | — | — | — | — | — | — | — | — | — | pending |
| 20 | `usar-dados-provar-eficiencia-licitacoes` | — | — | — | — | — | — | — | — | — | — | — | — | pending |
| 21 | `consultorias-modernas-inteligencia-priorizar-oportunidades` | — | — | — | — | — | — | — | — | — | — | — | — | pending |
| 22 | `triagem-editais-vantagem-estrategica-clientes` | — | — | — | — | — | — | — | — | — | — | — | — | pending |
| 23 | `nova-geracao-ferramentas-mercado-licitacoes` | — | — | — | — | — | — | — | — | — | — | — | — | pending |
| 24 | `reduzir-ruido-aumentar-performance-pregoes` | — | — | — | — | — | — | — | — | — | — | — | — | pending |
| 25 | `inteligencia-artificial-consultoria-licitacao-2026` | — | — | — | — | — | — | — | — | — | — | — | — | pending |
| 26 | `escalar-consultoria-sem-depender-horas-tecnicas` | — | — | — | — | — | — | — | — | — | — | — | — | pending |
| 27 | `identificar-clientes-gargalo-operacional-licitacoes` | — | — | — | — | — | — | — | — | — | — | — | — | pending |
| 28 | `diagnostico-eficiencia-licitacao-servico-premium` | — | — | — | — | — | — | — | — | — | — | — | — | pending |
| 29 | `aumentar-taxa-sucesso-clientes-20-porcento` | — | — | — | — | — | — | — | — | — | — | — | — | pending |
| 30 | `consultorias-dados-retem-mais-clientes-b2g` | — | — | — | — | — | — | — | — | — | — | — | — | pending |

**Column legend:**
- **HTTP** — HTTP status code (expected: 200)
- **Article** — Article/BlogPosting schema detected (pass/fail)
- **FAQPage** — FAQPage schema detected (pass/fail)
- **BreadcrumbList** — BreadcrumbList schema detected (pass/fail)
- **Organization** — Organization schema detected (pass/fail)
- **FAQ Count** — Number of FAQ questions (expected: 5)
- **FAQ Word Range** — Min–max word count across all 5 answers (expected: 40–60)
- **Inline CTA** — BlogInlineCTA with correct UTM params (pass/fail)
- **Final CTA** — Section with "14 dias" + "sem cartão" (pass/fail)
- **Internal Links** — Count of unique internal blog links (expected: >= 3)
- **Cross-Cluster** — At least 1 link to the other category cluster (pass/fail)
- **Canonical** — Correct `<link rel="canonical">` present (pass/fail)
- **GSC Status** — Google Search Console indexing status (pending/indexed/error)

---

## Google Search Console Checklist

After all 30 posts are live and indexed, verify in GSC:

1. **Coverage report** — no "Excluded" or "Error" status for blog URLs
2. **Rich results** — navigate to Search Console > Enhancements > FAQ/Article
3. **Core Web Vitals** — LCP < 2.5s, CLS < 0.1, INP < 200ms for blog pages
4. **Mobile Usability** — 0 errors across all 30 blog posts
5. **Sitemaps** — `/sitemap.xml` includes all 30 blog URLs

### Rich Results Test URLs (run manually)

```
https://search.google.com/test/rich-results?url=https://smartlic.tech/blog/como-aumentar-taxa-vitoria-licitacoes
https://search.google.com/test/rich-results?url=https://smartlic.tech/blog/erro-operacional-perder-contratos-publicos
https://search.google.com/test/rich-results?url=https://smartlic.tech/blog/vale-a-pena-disputar-pregao
https://search.google.com/test/rich-results?url=https://smartlic.tech/blog/clausulas-escondidas-editais-licitacao
https://search.google.com/test/rich-results?url=https://smartlic.tech/blog/reduzir-tempo-analisando-editais-irrelevantes
https://search.google.com/test/rich-results?url=https://smartlic.tech/blog/disputar-todas-licitacoes-matematica-real
https://search.google.com/test/rich-results?url=https://smartlic.tech/blog/estruturar-setor-licitacao-5-milhoes
https://search.google.com/test/rich-results?url=https://smartlic.tech/blog/custo-invisivel-disputar-pregoes-errados
https://search.google.com/test/rich-results?url=https://smartlic.tech/blog/escolher-editais-maior-probabilidade-vitoria
https://search.google.com/test/rich-results?url=https://smartlic.tech/blog/licitacao-volume-ou-inteligencia
https://search.google.com/test/rich-results?url=https://smartlic.tech/blog/orgaos-risco-atraso-pagamento-licitacao
https://search.google.com/test/rich-results?url=https://smartlic.tech/blog/empresas-vencem-30-porcento-pregoes
https://search.google.com/test/rich-results?url=https://smartlic.tech/blog/pipeline-licitacoes-funil-comercial
https://search.google.com/test/rich-results?url=https://smartlic.tech/blog/ata-registro-precos-como-escolher
https://search.google.com/test/rich-results?url=https://smartlic.tech/blog/equipe-40-horas-mes-editais-descartados
https://search.google.com/test/rich-results?url=https://smartlic.tech/blog/aumentar-retencao-clientes-inteligencia-editais
https://search.google.com/test/rich-results?url=https://smartlic.tech/blog/analise-edital-diferencial-competitivo-consultoria
https://search.google.com/test/rich-results?url=https://smartlic.tech/blog/entregar-mais-resultado-clientes-sem-aumentar-equipe
https://search.google.com/test/rich-results?url=https://smartlic.tech/blog/clientes-perdem-pregoes-boa-documentacao
https://search.google.com/test/rich-results?url=https://smartlic.tech/blog/usar-dados-provar-eficiencia-licitacoes
https://search.google.com/test/rich-results?url=https://smartlic.tech/blog/consultorias-modernas-inteligencia-priorizar-oportunidades
https://search.google.com/test/rich-results?url=https://smartlic.tech/blog/triagem-editais-vantagem-estrategica-clientes
https://search.google.com/test/rich-results?url=https://smartlic.tech/blog/nova-geracao-ferramentas-mercado-licitacoes
https://search.google.com/test/rich-results?url=https://smartlic.tech/blog/reduzir-ruido-aumentar-performance-pregoes
https://search.google.com/test/rich-results?url=https://smartlic.tech/blog/inteligencia-artificial-consultoria-licitacao-2026
https://search.google.com/test/rich-results?url=https://smartlic.tech/blog/escalar-consultoria-sem-depender-horas-tecnicas
https://search.google.com/test/rich-results?url=https://smartlic.tech/blog/identificar-clientes-gargalo-operacional-licitacoes
https://search.google.com/test/rich-results?url=https://smartlic.tech/blog/diagnostico-eficiencia-licitacao-servico-premium
https://search.google.com/test/rich-results?url=https://smartlic.tech/blog/aumentar-taxa-sucesso-clientes-20-porcento
https://search.google.com/test/rich-results?url=https://smartlic.tech/blog/consultorias-dados-retem-mais-clientes-b2g
```

---

## Notes / Issues

_Fill in during validation run._

---

## Sign-off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Developer | | | |
| QA | | | |
| Product Owner | | | |
