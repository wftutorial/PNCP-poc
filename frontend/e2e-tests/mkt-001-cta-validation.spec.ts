import { test, expect } from '@playwright/test';

/**
 * MKT-001 AC7: CTA and Internal Linking Validation
 *
 * For each of the 30 blog posts, validates:
 *   - Inline CTA (BlogInlineCTA component) exists with correct UTM params
 *   - Final CTA section mentions "14 dias" and "sem cartão"
 *   - UTM params: utm_source=blog, utm_medium=cta, utm_content=<slug>
 *   - At least 3 internal blog links exist on the page
 *   - At least 1 cross-cluster link exists (link to the other category's post)
 *
 * Run against localhost:  npx playwright test mkt-001-cta-validation
 * Run against production: FRONTEND_URL=https://smartlic.tech npx playwright test mkt-001-cta-validation
 */

// ---------------------------------------------------------------------------
// Slug registry (sourced from frontend/lib/blog.ts)
// ---------------------------------------------------------------------------
const BLOG_SLUGS = [
  // B2G cluster (15)
  'como-aumentar-taxa-vitoria-licitacoes',
  'erro-operacional-perder-contratos-publicos',
  'vale-a-pena-disputar-pregao',
  'clausulas-escondidas-editais-licitacao',
  'reduzir-tempo-analisando-editais-irrelevantes',
  'disputar-todas-licitacoes-matematica-real',
  'estruturar-setor-licitacao-5-milhoes',
  'custo-invisivel-disputar-pregoes-errados',
  'escolher-editais-maior-probabilidade-vitoria',
  'licitacao-volume-ou-inteligencia',
  'orgaos-risco-atraso-pagamento-licitacao',
  'empresas-vencem-30-porcento-pregoes',
  'pipeline-licitacoes-funil-comercial',
  'ata-registro-precos-como-escolher',
  'equipe-40-horas-mes-editais-descartados',
  // Consultorias cluster (15)
  'aumentar-retencao-clientes-inteligencia-editais',
  'analise-edital-diferencial-competitivo-consultoria',
  'entregar-mais-resultado-clientes-sem-aumentar-equipe',
  'clientes-perdem-pregoes-boa-documentacao',
  'usar-dados-provar-eficiencia-licitacoes',
  'consultorias-modernas-inteligencia-priorizar-oportunidades',
  'triagem-editais-vantagem-estrategica-clientes',
  'nova-geracao-ferramentas-mercado-licitacoes',
  'reduzir-ruido-aumentar-performance-pregoes',
  'inteligencia-artificial-consultoria-licitacao-2026',
  'escalar-consultoria-sem-depender-horas-tecnicas',
  'identificar-clientes-gargalo-operacional-licitacoes',
  'diagnostico-eficiencia-licitacao-servico-premium',
  'aumentar-taxa-sucesso-clientes-20-porcento',
  'consultorias-dados-retem-mais-clientes-b2g',
] as const;

// Which slugs belong to the B2G cluster (used for cross-cluster detection)
const B2G_SLUGS = new Set([
  'como-aumentar-taxa-vitoria-licitacoes',
  'erro-operacional-perder-contratos-publicos',
  'vale-a-pena-disputar-pregao',
  'clausulas-escondidas-editais-licitacao',
  'reduzir-tempo-analisando-editais-irrelevantes',
  'disputar-todas-licitacoes-matematica-real',
  'estruturar-setor-licitacao-5-milhoes',
  'custo-invisivel-disputar-pregoes-errados',
  'escolher-editais-maior-probabilidade-vitoria',
  'licitacao-volume-ou-inteligencia',
  'orgaos-risco-atraso-pagamento-licitacao',
  'empresas-vencem-30-porcento-pregoes',
  'pipeline-licitacoes-funil-comercial',
  'ata-registro-precos-como-escolher',
  'equipe-40-horas-mes-editais-descartados',
]);

const CONSULTORIAS_SLUGS = new Set([
  'aumentar-retencao-clientes-inteligencia-editais',
  'analise-edital-diferencial-competitivo-consultoria',
  'entregar-mais-resultado-clientes-sem-aumentar-equipe',
  'clientes-perdem-pregoes-boa-documentacao',
  'usar-dados-provar-eficiencia-licitacoes',
  'consultorias-modernas-inteligencia-priorizar-oportunidades',
  'triagem-editais-vantagem-estrategica-clientes',
  'nova-geracao-ferramentas-mercado-licitacoes',
  'reduzir-ruido-aumentar-performance-pregoes',
  'inteligencia-artificial-consultoria-licitacao-2026',
  'escalar-consultoria-sem-depender-horas-tecnicas',
  'identificar-clientes-gargalo-operacional-licitacoes',
  'diagnostico-eficiencia-licitacao-servico-premium',
  'aumentar-taxa-sucesso-clientes-20-porcento',
  'consultorias-dados-retem-mais-clientes-b2g',
]);

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Parse URL search params from a href string safely */
function parseHrefParams(href: string): URLSearchParams {
  try {
    const url = new URL(href, 'https://smartlic.tech');
    return url.searchParams;
  } catch {
    return new URLSearchParams();
  }
}

/** Returns the other cluster's slugs for cross-cluster detection */
function getCrossClusterSlugs(currentSlug: string): Set<string> {
  if (B2G_SLUGS.has(currentSlug)) return CONSULTORIAS_SLUGS;
  return B2G_SLUGS;
}

// ---------------------------------------------------------------------------
// Inline CTA validation
// ---------------------------------------------------------------------------
test.describe('MKT-001 — Inline CTA (BlogInlineCTA component)', () => {
  test.setTimeout(90_000);

  for (const slug of BLOG_SLUGS) {
    test(`[${slug}] inline CTA exists with correct UTM params`, async ({ page }) => {
      await page.goto(`/blog/${slug}`, { waitUntil: 'domcontentloaded' });

      // BlogInlineCTA renders inside article body — look for CTA links with UTM params
      // The component wraps a signup/trial button with utm_source=blog
      const inlineCTALinks = page.locator(
        'a[href*="utm_source=blog"][href*="utm_medium=cta"]'
      );

      const count = await inlineCTALinks.count();
      expect(
        count,
        `No inline CTA links with utm_source=blog&utm_medium=cta found on /blog/${slug}`
      ).toBeGreaterThan(0);

      // Validate UTM params on the first inline CTA link
      const firstHref = await inlineCTALinks.first().getAttribute('href');
      expect(firstHref, 'Inline CTA href is null').not.toBeNull();

      const params = parseHrefParams(firstHref ?? '');

      expect(
        params.get('utm_source'),
        `utm_source must be "blog" on /blog/${slug}, got "${params.get('utm_source')}"`
      ).toBe('blog');

      expect(
        params.get('utm_medium'),
        `utm_medium must be "cta" on /blog/${slug}, got "${params.get('utm_medium')}"`
      ).toBe('cta');

      expect(
        params.get('utm_content'),
        `utm_content must be "${slug}", got "${params.get('utm_content')}"`
      ).toBe(slug);
    });
  }
});

// ---------------------------------------------------------------------------
// Final CTA section validation
// ---------------------------------------------------------------------------
test.describe('MKT-001 — Final CTA section', () => {
  test.setTimeout(90_000);

  for (const slug of BLOG_SLUGS) {
    test(`[${slug}] final CTA mentions "14 dias" and "sem cartão"`, async ({ page }) => {
      await page.goto(`/blog/${slug}`, { waitUntil: 'domcontentloaded' });

      // Scroll to the bottom to ensure final CTA is rendered
      await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
      await page.waitForTimeout(500);

      // Check for "14 dias" text (free trial mention)
      const diasText = page.getByText(/14 dias/i);
      expect(
        await diasText.count(),
        `"14 dias" not found on /blog/${slug} — final CTA may be missing`
      ).toBeGreaterThan(0);

      // Check for "sem cartão" text (no credit card required)
      const semCartao = page.getByText(/sem cart[aã]o/i);
      expect(
        await semCartao.count(),
        `"sem cartão" not found on /blog/${slug} — final CTA may be missing`
      ).toBeGreaterThan(0);
    });
  }
});

// ---------------------------------------------------------------------------
// UTM parameter completeness validation
// ---------------------------------------------------------------------------
test.describe('MKT-001 — UTM parameter completeness', () => {
  test.setTimeout(90_000);

  for (const slug of BLOG_SLUGS) {
    test(`[${slug}] all CTA links have complete UTM params`, async ({ page }) => {
      await page.goto(`/blog/${slug}`, { waitUntil: 'domcontentloaded' });

      // Collect all links that go to /signup or /cadastro with UTM params
      const ctaLinks = await page
        .locator('a[href*="utm_source=blog"]')
        .all();

      expect(
        ctaLinks.length,
        `No blog UTM links found on /blog/${slug}`
      ).toBeGreaterThan(0);

      for (const link of ctaLinks) {
        const href = await link.getAttribute('href');
        if (!href) continue;

        const params = parseHrefParams(href);

        // utm_source must always be "blog"
        expect(
          params.get('utm_source'),
          `CTA link on /blog/${slug} has wrong utm_source: "${params.get('utm_source')}"`
        ).toBe('blog');

        // utm_medium must be "cta"
        expect(
          params.get('utm_medium'),
          `CTA link on /blog/${slug} has wrong utm_medium: "${params.get('utm_medium')}"`
        ).toBe('cta');

        // utm_content must equal the slug
        expect(
          params.get('utm_content'),
          `CTA link on /blog/${slug} has wrong utm_content: "${params.get('utm_content')}"`
        ).toBe(slug);
      }
    });
  }
});

// ---------------------------------------------------------------------------
// Internal linking validation
// ---------------------------------------------------------------------------
test.describe('MKT-001 — Internal blog links', () => {
  test.setTimeout(90_000);

  for (const slug of BLOG_SLUGS) {
    test(`[${slug}] has at least 3 internal blog links`, async ({ page }) => {
      await page.goto(`/blog/${slug}`, { waitUntil: 'domcontentloaded' });

      // Count links pointing to /blog/* (excluding the current page itself)
      const blogLinks = await page
        .locator(`a[href*="/blog/"]:not([href*="/blog/${slug}"])`)
        .all();

      // Deduplicate hrefs
      const hrefs = new Set<string>();
      for (const link of blogLinks) {
        const href = await link.getAttribute('href');
        if (href && href.includes('/blog/')) {
          hrefs.add(href.split('?')[0]); // strip UTM params for dedup
        }
      }

      expect(
        hrefs.size,
        `Expected >= 3 internal blog links on /blog/${slug}, got ${hrefs.size}`
      ).toBeGreaterThanOrEqual(3);
    });
  }
});

// ---------------------------------------------------------------------------
// Cross-cluster linking validation
// ---------------------------------------------------------------------------
test.describe('MKT-001 — Cross-cluster internal links', () => {
  test.setTimeout(90_000);

  for (const slug of BLOG_SLUGS) {
    test(`[${slug}] has at least 1 cross-cluster blog link`, async ({ page }) => {
      await page.goto(`/blog/${slug}`, { waitUntil: 'domcontentloaded' });

      const crossClusterSlugs = getCrossClusterSlugs(slug);
      const allBlogLinks = await page.locator('a[href*="/blog/"]').all();

      let crossClusterCount = 0;
      for (const link of allBlogLinks) {
        const href = await link.getAttribute('href');
        if (!href) continue;

        // Extract slug from the href
        const match = href.match(/\/blog\/([^/?#]+)/);
        if (match && crossClusterSlugs.has(match[1])) {
          crossClusterCount++;
        }
      }

      expect(
        crossClusterCount,
        `Expected >= 1 cross-cluster link on /blog/${slug}, got ${crossClusterCount}`
      ).toBeGreaterThanOrEqual(1);
    });
  }
});

// ---------------------------------------------------------------------------
// Consolidated smoke test — all CTA/link checks in one navigation
// ---------------------------------------------------------------------------
test.describe('MKT-001 — CTA + linking smoke test (single nav per post)', () => {
  test.setTimeout(120_000);

  for (const slug of BLOG_SLUGS) {
    test(`[${slug}] CTA + links smoke`, async ({ page }) => {
      await page.goto(`/blog/${slug}`, { waitUntil: 'domcontentloaded' });

      // 1. Inline CTA with UTM params exists
      const inlineCTA = page.locator('a[href*="utm_source=blog"][href*="utm_medium=cta"]');
      expect(await inlineCTA.count(), 'Inline CTA missing').toBeGreaterThan(0);

      // 2. "14 dias" appears somewhere on the page
      const diasCount = await page.getByText(/14 dias/i).count();
      expect(diasCount, '"14 dias" not found').toBeGreaterThan(0);

      // 3. "sem cartão" appears somewhere on the page
      const semCartaoCount = await page.getByText(/sem cart[aã]o/i).count();
      expect(semCartaoCount, '"sem cartão" not found').toBeGreaterThan(0);

      // 4. At least 3 internal blog links
      const allBlogLinks = await page.locator(`a[href*="/blog/"]`).all();
      const uniqueInternalSlugs = new Set<string>();
      const crossClusterSlugs = getCrossClusterSlugs(slug);
      let hasCrossCluster = false;

      for (const link of allBlogLinks) {
        const href = await link.getAttribute('href');
        if (!href) continue;
        const match = href.match(/\/blog\/([^/?#]+)/);
        if (!match) continue;
        const linkedSlug = match[1];
        if (linkedSlug !== slug) {
          uniqueInternalSlugs.add(linkedSlug);
          if (crossClusterSlugs.has(linkedSlug)) hasCrossCluster = true;
        }
      }

      expect(uniqueInternalSlugs.size, `Expected >= 3 internal blog links, got ${uniqueInternalSlugs.size}`).toBeGreaterThanOrEqual(3);
      expect(hasCrossCluster, 'Missing at least 1 cross-cluster blog link').toBe(true);
    });
  }
});
