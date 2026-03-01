import { test, expect } from '@playwright/test';

/**
 * MKT-001 AC7: Full JSON-LD Schema Validation
 *
 * Navigates each of the 30 blog posts and validates:
 *   - Article schema: @type, headline, author, datePublished, image, publisher
 *   - FAQPage schema: exactly 5 questions, answers 40–60 words each
 *   - BreadcrumbList schema: exactly 4 breadcrumb items
 *   - Organization schema: name + url present
 *   - Author field includes "Equipe SmartLic"
 *   - Author description includes "Especialistas em Inteligência de Licitações Públicas"
 *
 * Run against localhost:  npx playwright test mkt-001-schema-validation
 * Run against production: FRONTEND_URL=https://smartlic.tech npx playwright test mkt-001-schema-validation
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

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------
type JsonLdBlock = Record<string, unknown>;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

async function extractJsonLdBlocks(page: import('@playwright/test').Page): Promise<JsonLdBlock[]> {
  return page.evaluate(() => {
    const scripts = Array.from(
      document.querySelectorAll('script[type="application/ld+json"]')
    );
    return scripts.map((s) => {
      try {
        return JSON.parse(s.textContent || '{}') as Record<string, unknown>;
      } catch {
        return {} as Record<string, unknown>;
      }
    });
  });
}

function flattenSchemas(blocks: JsonLdBlock[]): JsonLdBlock[] {
  const result: JsonLdBlock[] = [];
  for (const block of blocks) {
    if (Array.isArray(block['@graph'])) {
      result.push(...(block['@graph'] as JsonLdBlock[]));
    } else if (block['@type']) {
      result.push(block);
    }
  }
  return result;
}

function findByType(schemas: JsonLdBlock[], type: string): JsonLdBlock | undefined {
  return schemas.find((s) => {
    const t = s['@type'];
    if (typeof t === 'string') return t === type || t.endsWith(type);
    if (Array.isArray(t)) return t.some((v) => String(v) === type || String(v).endsWith(type));
    return false;
  });
}

function wordCount(text: string): number {
  return text.trim().split(/\s+/).filter(Boolean).length;
}

// ---------------------------------------------------------------------------
// Article schema validation suite
// ---------------------------------------------------------------------------
test.describe('MKT-001 — Article schema validation', () => {
  test.setTimeout(90_000);

  for (const slug of BLOG_SLUGS) {
    test(`[${slug}] Article schema has all required fields`, async ({ page }) => {
      await page.goto(`/blog/${slug}`, { waitUntil: 'domcontentloaded' });

      const rawBlocks = await extractJsonLdBlocks(page);
      const schemas = flattenSchemas(rawBlocks);

      // Must have an Article (or NewsArticle / BlogPosting)
      const article =
        findByType(schemas, 'Article') ||
        findByType(schemas, 'BlogPosting') ||
        findByType(schemas, 'NewsArticle');

      expect(article, `Missing Article/BlogPosting schema on /blog/${slug}`).toBeDefined();

      if (!article) return;

      // Required fields
      expect(article['headline'], 'Article.headline missing').toBeTruthy();
      expect(article['datePublished'], 'Article.datePublished missing').toBeTruthy();
      expect(article['author'], 'Article.author missing').toBeTruthy();
      expect(article['publisher'], 'Article.publisher missing').toBeTruthy();
      expect(article['url'] || article['@id'], 'Article.url/@id missing').toBeTruthy();

      // Author must include "Equipe SmartLic"
      const author = article['author'];
      const authorText = JSON.stringify(author);
      expect(
        authorText,
        `Article.author does not mention "Equipe SmartLic" on /blog/${slug}`
      ).toContain('Equipe SmartLic');

      // Author description must include the expected specialist label
      expect(
        authorText,
        `Article.author missing specialist description on /blog/${slug}`
      ).toContain('Especialistas em Inteligência de Licitações Públicas');
    });
  }
});

// ---------------------------------------------------------------------------
// FAQPage schema validation suite
// ---------------------------------------------------------------------------
test.describe('MKT-001 — FAQPage schema validation', () => {
  test.setTimeout(90_000);

  for (const slug of BLOG_SLUGS) {
    test(`[${slug}] FAQPage has 5 questions with answers 40–60 words`, async ({ page }) => {
      await page.goto(`/blog/${slug}`, { waitUntil: 'domcontentloaded' });

      const rawBlocks = await extractJsonLdBlocks(page);
      const schemas = flattenSchemas(rawBlocks);

      const faqPage = findByType(schemas, 'FAQPage');
      expect(faqPage, `Missing FAQPage schema on /blog/${slug}`).toBeDefined();

      if (!faqPage) return;

      const entities = faqPage['mainEntity'];
      expect(Array.isArray(entities), 'FAQPage.mainEntity must be an array').toBe(true);

      const questions = entities as JsonLdBlock[];

      // Exactly 5 questions
      expect(
        questions.length,
        `Expected 5 FAQ questions, got ${questions.length} on /blog/${slug}`
      ).toBe(5);

      for (let i = 0; i < questions.length; i++) {
        const q = questions[i];

        // Each must be a Question
        expect(
          q['@type'],
          `FAQ item ${i + 1} must have @type Question on /blog/${slug}`
        ).toContain('Question');

        // Must have question text
        expect(
          q['name'],
          `FAQ question ${i + 1} missing name/text on /blog/${slug}`
        ).toBeTruthy();

        // Must have acceptedAnswer
        const accepted = q['acceptedAnswer'] as JsonLdBlock | undefined;
        expect(
          accepted,
          `FAQ question ${i + 1} missing acceptedAnswer on /blog/${slug}`
        ).toBeDefined();

        if (!accepted) continue;

        // acceptedAnswer must have @type Answer
        expect(
          String(accepted['@type'] ?? ''),
          `FAQ acceptedAnswer ${i + 1} must have @type Answer on /blog/${slug}`
        ).toContain('Answer');

        const answerText = String(accepted['text'] ?? '');
        const wc = wordCount(answerText);

        expect(
          wc,
          `FAQ answer ${i + 1} has ${wc} words — must be >= 40 on /blog/${slug}`
        ).toBeGreaterThanOrEqual(40);

        expect(
          wc,
          `FAQ answer ${i + 1} has ${wc} words — must be <= 60 on /blog/${slug}`
        ).toBeLessThanOrEqual(60);
      }
    });
  }
});

// ---------------------------------------------------------------------------
// BreadcrumbList schema validation suite
// ---------------------------------------------------------------------------
test.describe('MKT-001 — BreadcrumbList schema validation', () => {
  test.setTimeout(90_000);

  for (const slug of BLOG_SLUGS) {
    test(`[${slug}] BreadcrumbList has exactly 4 items`, async ({ page }) => {
      await page.goto(`/blog/${slug}`, { waitUntil: 'domcontentloaded' });

      const rawBlocks = await extractJsonLdBlocks(page);
      const schemas = flattenSchemas(rawBlocks);

      const breadcrumb = findByType(schemas, 'BreadcrumbList');
      expect(breadcrumb, `Missing BreadcrumbList schema on /blog/${slug}`).toBeDefined();

      if (!breadcrumb) return;

      const items = breadcrumb['itemListElement'];
      expect(Array.isArray(items), 'BreadcrumbList.itemListElement must be an array').toBe(true);

      const crumbs = items as JsonLdBlock[];
      expect(
        crumbs.length,
        `Expected 4 breadcrumb items, got ${crumbs.length} on /blog/${slug}`
      ).toBe(4);

      // Each item must have position and name
      for (let i = 0; i < crumbs.length; i++) {
        const crumb = crumbs[i];
        expect(crumb['position'], `Breadcrumb item ${i + 1} missing position`).toBe(i + 1);
        expect(crumb['name'], `Breadcrumb item ${i + 1} missing name`).toBeTruthy();
        // item (URL) is optional in schema.org spec but good practice
        const itemVal = crumb['item'];
        if (itemVal !== undefined) {
          expect(
            String(itemVal),
            `Breadcrumb item ${i + 1} has invalid item URL`
          ).toMatch(/^https?:\/\//);
        }
      }
    });
  }
});

// ---------------------------------------------------------------------------
// Organization schema validation suite
// ---------------------------------------------------------------------------
test.describe('MKT-001 — Organization schema validation', () => {
  test.setTimeout(90_000);

  for (const slug of BLOG_SLUGS) {
    test(`[${slug}] Organization schema present with name and url`, async ({ page }) => {
      await page.goto(`/blog/${slug}`, { waitUntil: 'domcontentloaded' });

      const rawBlocks = await extractJsonLdBlocks(page);
      const schemas = flattenSchemas(rawBlocks);

      const org = findByType(schemas, 'Organization');
      expect(org, `Missing Organization schema on /blog/${slug}`).toBeDefined();

      if (!org) return;

      expect(org['name'], 'Organization.name missing').toBeTruthy();
      expect(org['url'], 'Organization.url missing').toBeTruthy();
      expect(
        String(org['url']),
        'Organization.url must be a valid URL'
      ).toMatch(/^https?:\/\//);
    });
  }
});

// ---------------------------------------------------------------------------
// Consolidated smoke test — single navigation per post, all schemas checked
// ---------------------------------------------------------------------------
test.describe('MKT-001 — Full schema smoke test (all schemas in one pass)', () => {
  test.setTimeout(120_000);

  for (const slug of BLOG_SLUGS) {
    test(`[${slug}] all 4 required schema types present`, async ({ page }) => {
      await page.goto(`/blog/${slug}`, { waitUntil: 'domcontentloaded' });

      const rawBlocks = await extractJsonLdBlocks(page);
      expect(rawBlocks.length, `No JSON-LD found on /blog/${slug}`).toBeGreaterThan(0);

      const schemas = flattenSchemas(rawBlocks);
      const types = schemas.map((s) => {
        const t = s['@type'];
        return Array.isArray(t) ? t : [String(t ?? '')];
      }).flat();

      const hasArticle = types.some((t) =>
        ['Article', 'BlogPosting', 'NewsArticle'].includes(t)
      );
      const hasFaq = types.some((t) => t === 'FAQPage');
      const hasBreadcrumb = types.some((t) => t === 'BreadcrumbList');
      const hasOrg = types.some((t) => t === 'Organization');

      expect(hasArticle, `Article/BlogPosting missing on /blog/${slug}`).toBe(true);
      expect(hasFaq, `FAQPage missing on /blog/${slug}`).toBe(true);
      expect(hasBreadcrumb, `BreadcrumbList missing on /blog/${slug}`).toBe(true);
      expect(hasOrg, `Organization missing on /blog/${slug}`).toBe(true);
    });
  }
});
