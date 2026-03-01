import { test, expect } from '@playwright/test';

/**
 * MKT-001 AC7: Rich Results / Structured Data Validation
 *
 * This file contains TWO approaches:
 *
 * 1. LOCAL VALIDATION (default, runs via `npm run test:e2e`)
 *    Navigates each blog post on localhost/production, extracts JSON-LD blocks,
 *    and validates schema presence without calling any external service.
 *
 * 2. GOOGLE RICH RESULTS TEST (manual only, tagged `@manual`)
 *    Opens Google's Rich Results Test in a real browser and submits each URL.
 *    Run with: npx playwright test mkt-001-rich-results.spec.ts --grep @manual --headed
 *    NOTE: Google may rate-limit or block automated headless access.
 *          Always run this in headed mode with a human nearby to solve CAPTCHAs.
 */

// ---------------------------------------------------------------------------
// Slug registry (sourced from frontend/lib/blog.ts)
// ---------------------------------------------------------------------------
const BLOG_SLUGS = [
  // B2G cluster
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
  // Consultorias cluster
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

const PRODUCTION_BASE = 'https://smartlic.tech';
const GOOGLE_RICH_RESULTS_URL = 'https://search.google.com/test/rich-results';

// ---------------------------------------------------------------------------
// Helper: extract all JSON-LD blocks from a page
// ---------------------------------------------------------------------------
type JsonLdBlock = Record<string, unknown>;

async function extractJsonLdBlocks(page: import('@playwright/test').Page): Promise<JsonLdBlock[]> {
  return page.evaluate(() => {
    const scripts = Array.from(
      document.querySelectorAll('script[type="application/ld+json"]')
    );
    return scripts.map((s) => {
      try {
        return JSON.parse(s.textContent || '{}');
      } catch {
        return {};
      }
    });
  });
}

// ---------------------------------------------------------------------------
// Helper: count words in a string (split on whitespace)
// ---------------------------------------------------------------------------
function wordCount(text: string): number {
  return text.trim().split(/\s+/).filter(Boolean).length;
}

// ---------------------------------------------------------------------------
// Helper: flatten @graph blocks into a flat list of schema objects
// ---------------------------------------------------------------------------
function flattenSchemas(blocks: JsonLdBlock[]): JsonLdBlock[] {
  const result: JsonLdBlock[] = [];
  for (const block of blocks) {
    if (Array.isArray(block['@graph'])) {
      result.push(...(block['@graph'] as JsonLdBlock[]));
    } else {
      result.push(block);
    }
  }
  return result;
}

// ---------------------------------------------------------------------------
// Helper: find a schema object by @type (case-insensitive partial match)
// ---------------------------------------------------------------------------
function findByType(schemas: JsonLdBlock[], type: string): JsonLdBlock | undefined {
  return schemas.find((s) => {
    const t = s['@type'];
    if (typeof t === 'string') return t.toLowerCase().includes(type.toLowerCase());
    if (Array.isArray(t)) return t.some((v) => String(v).toLowerCase().includes(type.toLowerCase()));
    return false;
  });
}

// ---------------------------------------------------------------------------
// LOCAL VALIDATION — runs against localhost or FRONTEND_URL
// ---------------------------------------------------------------------------
test.describe('MKT-001 AC7 — Local JSON-LD schema validation (all 30 posts)', () => {
  // Higher timeout per test since we navigate 30 pages
  test.setTimeout(90_000);

  for (const slug of BLOG_SLUGS) {
    test(`[${slug}] has required JSON-LD schemas`, async ({ page }) => {
      await page.goto(`/blog/${slug}`, { waitUntil: 'domcontentloaded' });

      const rawBlocks = await extractJsonLdBlocks(page);
      expect(rawBlocks.length, `No JSON-LD blocks found on /blog/${slug}`).toBeGreaterThan(0);

      const schemas = flattenSchemas(rawBlocks);

      // ── Article ───────────────────────────────────────────────────────────
      const article = findByType(schemas, 'Article');
      expect(article, `Missing Article schema on /blog/${slug}`).toBeDefined();

      // ── FAQPage ───────────────────────────────────────────────────────────
      const faqPage = findByType(schemas, 'FAQPage');
      expect(faqPage, `Missing FAQPage schema on /blog/${slug}`).toBeDefined();

      if (faqPage) {
        const entities = faqPage['mainEntity'];
        expect(Array.isArray(entities), `FAQPage.mainEntity is not an array on /blog/${slug}`).toBe(true);

        const questions = entities as JsonLdBlock[];
        expect(
          questions.length,
          `Expected exactly 5 FAQ questions, got ${questions.length} on /blog/${slug}`
        ).toBe(5);

        for (let i = 0; i < questions.length; i++) {
          const q = questions[i];
          const accepted = q['acceptedAnswer'] as JsonLdBlock | undefined;
          expect(accepted, `FAQ question ${i + 1} missing acceptedAnswer on /blog/${slug}`).toBeDefined();

          const answerText = String((accepted?.['text'] as string) ?? '');
          const wc = wordCount(answerText);
          expect(
            wc,
            `FAQ answer ${i + 1} has ${wc} words — expected 40–60 on /blog/${slug}`
          ).toBeGreaterThanOrEqual(40);
          expect(
            wc,
            `FAQ answer ${i + 1} has ${wc} words — expected 40–60 on /blog/${slug}`
          ).toBeLessThanOrEqual(60);
        }
      }

      // ── BreadcrumbList ────────────────────────────────────────────────────
      const breadcrumb = findByType(schemas, 'BreadcrumbList');
      expect(breadcrumb, `Missing BreadcrumbList schema on /blog/${slug}`).toBeDefined();
    });
  }
});

// ---------------------------------------------------------------------------
// MANUAL ONLY — Google Rich Results Test
// Tag: @manual  —  run with: npx playwright test mkt-001-rich-results --grep @manual --headed
// ---------------------------------------------------------------------------
test.describe('MKT-001 AC7 — Google Rich Results Test @manual', () => {
  test.skip(
    !process.env.RUN_GOOGLE_RICH_RESULTS,
    'Set RUN_GOOGLE_RICH_RESULTS=1 to run Google Rich Results tests. Requires --headed mode.'
  );

  // 3-minute timeout per test (Google RRT can be slow)
  test.setTimeout(180_000);

  for (const slug of BLOG_SLUGS) {
    const targetUrl = `${PRODUCTION_BASE}/blog/${slug}`;

    test(`@manual [${slug}] passes Google Rich Results Test`, async ({ page }) => {
      // Navigate to Google Rich Results Test
      await page.goto(GOOGLE_RICH_RESULTS_URL, { waitUntil: 'networkidle' });

      // Fill in the URL input
      const urlInput = page.locator('input[type="url"], input[aria-label*="URL"], input[placeholder*="URL"]').first();
      await urlInput.fill(targetUrl);

      // Submit the form
      const testButton = page.getByRole('button', { name: /test url|test/i }).first();
      await testButton.click();

      // Wait for results (Google can take 30-90s)
      await page.waitForSelector('[class*="result"], [class*="Result"], [aria-label*="result"]', {
        timeout: 120_000,
      });

      // Wait for the loading spinner to disappear
      await page.waitForFunction(
        () => !document.querySelector('[class*="loading"], [class*="spinner"]'),
        { timeout: 120_000 }
      );

      // Assert: 0 errors
      const errorCount = await page
        .locator('[class*="error-count"], [aria-label*="error"]')
        .textContent()
        .catch(() => '0');
      expect(
        parseInt(errorCount ?? '0', 10),
        `Expected 0 errors for ${targetUrl}, Google RRT reported errors`
      ).toBe(0);

      // Assert: FAQPage detected
      await expect(
        page.getByText(/FAQPage/i),
        `FAQPage schema not detected by Google for ${targetUrl}`
      ).toBeVisible({ timeout: 10_000 });

      // Assert: Article or NewsArticle detected
      await expect(
        page.getByText(/Article/i).first(),
        `Article schema not detected by Google for ${targetUrl}`
      ).toBeVisible({ timeout: 10_000 });

      // Assert: BreadcrumbList detected
      await expect(
        page.getByText(/BreadcrumbList/i),
        `BreadcrumbList schema not detected by Google for ${targetUrl}`
      ).toBeVisible({ timeout: 10_000 });
    });
  }
});
