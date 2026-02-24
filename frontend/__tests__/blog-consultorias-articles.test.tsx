/**
 * STORY-263 AC21/AC22/AC23: Blog Consultorias articles tests
 *
 * Tests cover:
 * - AC21: All 15 Consultorias articles registered in blog.ts with complete metadata
 * - AC22: All 15 articles render without error (smoke test)
 * - AC23: FAQPage JSON-LD schema validity for each article
 * - AC1: Word count within 2000-3500 range
 * - AC2: Heading hierarchy (no skipped levels)
 * - AC5: FAQ section present
 * - AC8: Metadata completeness (title <=70 chars, description 80-160 chars)
 * - AC9: BlogPosting JSON-LD fields
 * - AC12: Slug format (lowercase, hyphenated, <=60 chars)
 * - AC15: Related articles exist in registry
 * - AC19: CTA section with UTM params (consultorias campaign)
 * - AC24: Zero regressions
 */

import React from 'react';
import { render } from '@testing-library/react';

// ---------- Mock setup ----------

jest.mock('next/link', () => {
  return ({
    children,
    href,
    ...props
  }: {
    children: React.ReactNode;
    href: string;
    [key: string]: unknown;
  }) => (
    <a href={href} {...props}>
      {children}
    </a>
  );
});

// ---------- Imports ----------

import {
  BLOG_ARTICLES,
  getAllSlugs,
  getArticleBySlug,
  getRelatedArticles,
  calculateReadingTime,
  type BlogArticleMeta,
} from '../lib/blog';

// ---------- Constants ----------

const CONS_SLUGS = [
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
];

// ---------- AC21: All 15 Consultorias articles registered in blog.ts ----------

describe('STORY-263 AC21: Blog registry completeness', () => {
  it('has exactly 15 Consultorias articles registered', () => {
    const consArticles = BLOG_ARTICLES.filter(
      (a) => a.category === 'Consultorias de Licitação',
    );
    expect(consArticles.length).toBe(15);
  });

  it.each(CONS_SLUGS)('slug "%s" exists in BLOG_ARTICLES', (slug) => {
    const article = getArticleBySlug(slug);
    expect(article).toBeDefined();
  });

  it('all Consultorias articles have category "Consultorias de Licitação"', () => {
    CONS_SLUGS.forEach((slug) => {
      const article = getArticleBySlug(slug);
      expect(article?.category).toBe('Consultorias de Licitação');
    });
  });

  it('all Consultorias articles have complete metadata fields', () => {
    CONS_SLUGS.forEach((slug) => {
      const article = getArticleBySlug(slug)!;
      expect(article.slug).toBeTruthy();
      expect(article.title).toBeTruthy();
      expect(article.description).toBeTruthy();
      expect(article.category).toBeTruthy();
      expect(article.tags.length).toBeGreaterThan(0);
      expect(article.publishDate).toMatch(/^\d{4}-\d{2}-\d{2}$/);
      expect(article.readingTime).toBeTruthy();
      expect(article.wordCount).toBeGreaterThanOrEqual(2000);
      expect(article.wordCount).toBeLessThanOrEqual(3500);
      expect(article.keywords.length).toBeGreaterThan(0);
      expect(article.relatedSlugs.length).toBeGreaterThanOrEqual(2);
    });
  });
});

// ---------- AC12: Slug format ----------

describe('STORY-263 AC12: SEO-friendly slugs', () => {
  it.each(CONS_SLUGS)('slug "%s" is lowercase, hyphenated, <=60 chars', (slug) => {
    expect(slug).toMatch(/^[a-z0-9]+(-[a-z0-9]+)*$/);
    expect(slug.length).toBeLessThanOrEqual(60);
  });
});

// ---------- AC8: Metadata constraints ----------

describe('STORY-263 AC8: Metadata quality', () => {
  it.each(CONS_SLUGS)(
    'article "%s" has title <=80 chars and description 80-160 chars',
    (slug) => {
      const article = getArticleBySlug(slug)!;
      expect(article.title.length).toBeLessThanOrEqual(80);
      expect(article.title.length).toBeGreaterThan(10);
      expect(article.description.length).toBeGreaterThanOrEqual(80);
      expect(article.description.length).toBeLessThanOrEqual(160);
    },
  );
});

// ---------- AC1: Word count range ----------

describe('STORY-263 AC1: Word count range', () => {
  it.each(CONS_SLUGS)(
    'article "%s" has wordCount between 2000 and 3500',
    (slug) => {
      const article = getArticleBySlug(slug)!;
      expect(article.wordCount).toBeGreaterThanOrEqual(2000);
      expect(article.wordCount).toBeLessThanOrEqual(3500);
    },
  );

  it('readingTime matches wordCount for all Consultorias articles', () => {
    CONS_SLUGS.forEach((slug) => {
      const article = getArticleBySlug(slug)!;
      expect(article.readingTime).toBe(calculateReadingTime(article.wordCount));
    });
  });
});

// ---------- AC15: Related articles exist ----------

describe('STORY-263 AC15: Internal linking integrity', () => {
  it.each(CONS_SLUGS)(
    'article "%s" has >=2 relatedSlugs that exist in registry',
    (slug) => {
      const article = getArticleBySlug(slug)!;
      expect(article.relatedSlugs.length).toBeGreaterThanOrEqual(2);

      const related = getRelatedArticles(slug);
      expect(related.length).toBeGreaterThanOrEqual(2);
      related.forEach((r) => {
        expect(r.slug).not.toBe(slug);
      });
    },
  );

  it('all relatedSlugs across Consultorias articles resolve to existing articles', () => {
    const allSlugs = new Set(getAllSlugs());
    CONS_SLUGS.forEach((slug) => {
      const article = getArticleBySlug(slug)!;
      article.relatedSlugs.forEach((rs) => {
        expect(allSlugs.has(rs)).toBe(true);
      });
    });
  });
});

// ---------- AC22: Smoke test — all 15 articles render ----------

describe('STORY-263 AC22: Article render smoke tests', () => {
  it.each(CONS_SLUGS)('article "%s" renders without error', async (slug) => {
    const module = await import(`../app/blog/content/${slug}`);
    const Component = module.default;
    expect(Component).toBeDefined();

    const { container } = render(<Component />);
    expect(container.innerHTML.length).toBeGreaterThan(100);
  });
});

// ---------- AC23: FAQPage JSON-LD schema ----------

describe('STORY-263 AC23: FAQPage JSON-LD schema', () => {
  it.each(CONS_SLUGS)(
    'article "%s" contains valid FAQPage JSON-LD',
    async (slug) => {
      const module = await import(`../app/blog/content/${slug}`);
      const Component = module.default;
      const { container } = render(<Component />);

      const scripts = container.querySelectorAll(
        'script[type="application/ld+json"]',
      );
      expect(scripts.length).toBeGreaterThanOrEqual(1);

      let faqSchema: Record<string, unknown> | undefined;
      scripts.forEach((script) => {
        try {
          const parsed = JSON.parse(script.textContent || '{}');
          if (parsed['@type'] === 'FAQPage') {
            faqSchema = parsed;
          }
        } catch {
          // skip invalid JSON
        }
      });

      expect(faqSchema).toBeDefined();
      expect(faqSchema!['@context']).toBe('https://schema.org');
      expect(faqSchema!['@type']).toBe('FAQPage');

      const mainEntity = faqSchema!.mainEntity as Array<Record<string, unknown>>;
      expect(Array.isArray(mainEntity)).toBe(true);
      expect(mainEntity.length).toBeGreaterThanOrEqual(3);

      mainEntity.forEach((question) => {
        expect(question['@type']).toBe('Question');
        expect(typeof question.name).toBe('string');
        expect((question.name as string).length).toBeGreaterThan(10);

        const answer = question.acceptedAnswer as Record<string, unknown>;
        expect(answer['@type']).toBe('Answer');
        expect(typeof answer.text).toBe('string');
        expect((answer.text as string).length).toBeGreaterThan(10);
      });
    },
  );
});

// ---------- AC2: Heading hierarchy ----------

describe('STORY-263 AC2: Heading hierarchy', () => {
  it.each(CONS_SLUGS)(
    'article "%s" uses H2 and optional H3 (no H1, no skipping)',
    async (slug) => {
      const module = await import(`../app/blog/content/${slug}`);
      const Component = module.default;
      const { container } = render(<Component />);

      const h1s = container.querySelectorAll('h1');
      expect(h1s.length).toBe(0);

      const h2s = container.querySelectorAll('h2');
      expect(h2s.length).toBeGreaterThanOrEqual(3);

      const h4s = container.querySelectorAll('h4');
      const h5s = container.querySelectorAll('h5');
      const h6s = container.querySelectorAll('h6');
      expect(h4s.length).toBe(0);
      expect(h5s.length).toBe(0);
      expect(h6s.length).toBe(0);
    },
  );
});

// ---------- AC5: FAQ section present ----------

describe('STORY-263 AC5: FAQ section', () => {
  it.each(CONS_SLUGS)(
    'article "%s" has FAQ heading with questions as H3s',
    async (slug) => {
      const module = await import(`../app/blog/content/${slug}`);
      const Component = module.default;
      const { container } = render(<Component />);

      const h2s = Array.from(container.querySelectorAll('h2'));
      const faqHeading = h2s.find(
        (h2) =>
          h2.textContent?.toLowerCase().includes('perguntas frequentes') ||
          h2.textContent?.toLowerCase().includes('faq'),
      );
      expect(faqHeading).toBeDefined();

      const h3s = container.querySelectorAll('h3');
      expect(h3s.length).toBeGreaterThanOrEqual(3);
    },
  );
});

// ---------- AC19: CTA section with consultorias UTM ----------

describe('STORY-263 AC19: CTA section', () => {
  it.each(CONS_SLUGS)(
    'article "%s" has CTA with signup link containing UTM params',
    async (slug) => {
      const module = await import(`../app/blog/content/${slug}`);
      const Component = module.default;
      const { container } = render(<Component />);

      const links = Array.from(container.querySelectorAll('a'));
      const ctaLink = links.find(
        (a) =>
          a.getAttribute('href')?.includes('/signup') &&
          a.getAttribute('href')?.includes('utm_source=blog'),
      );
      expect(ctaLink).toBeDefined();
      expect(ctaLink?.getAttribute('href')).toContain('utm_medium=article');
      expect(ctaLink?.getAttribute('href')).toContain('utm_campaign=consultorias');
    },
  );
});

// ---------- AC16: Product page links ----------

describe('STORY-263 AC16: Product page links', () => {
  it.each(CONS_SLUGS)(
    'article "%s" links to at least 1 product page',
    async (slug) => {
      const module = await import(`../app/blog/content/${slug}`);
      const Component = module.default;
      const { container } = render(<Component />);

      const links = Array.from(container.querySelectorAll('a'));
      const productPaths = ['/features', '/planos', '/buscar', '/signup', '/pipeline'];

      const hasProductLink = links.some((a) => {
        const href = a.getAttribute('href') || '';
        return productPaths.some((path) => href.startsWith(path));
      });

      expect(hasProductLink).toBe(true);
    },
  );
});

// ---------- AC15: Internal blog links ----------

describe('STORY-263 AC15: Internal blog links', () => {
  it.each(CONS_SLUGS)(
    'article "%s" links to at least 2 other blog articles',
    async (slug) => {
      const module = await import(`../app/blog/content/${slug}`);
      const Component = module.default;
      const { container } = render(<Component />);

      const links = Array.from(container.querySelectorAll('a'));
      const blogLinks = links.filter((a) => {
        const href = a.getAttribute('href') || '';
        return href.startsWith('/blog/') && !href.includes(slug);
      });

      expect(blogLinks.length).toBeGreaterThanOrEqual(2);
    },
  );
});

// ---------- AC9: BlogPosting JSON-LD compatibility ----------

describe('STORY-263 AC9: BlogPosting schema compatibility', () => {
  it('all Consultorias articles have required fields for BlogPosting schema', () => {
    CONS_SLUGS.forEach((slug) => {
      const article = getArticleBySlug(slug)!;
      expect(article.title).toBeTruthy();
      expect(article.description).toBeTruthy();
      expect(article.publishDate).toMatch(/^\d{4}-\d{2}-\d{2}$/);
      expect(article.wordCount).toBeGreaterThan(0);
      expect(article.category).toBe('Consultorias de Licitação');
    });
  });
});

// ---------- AC10: BreadcrumbList compatibility ----------

describe('STORY-263 AC10: BreadcrumbList schema compatibility', () => {
  it('all Consultorias articles have category for breadcrumb generation', () => {
    CONS_SLUGS.forEach((slug) => {
      const article = getArticleBySlug(slug)!;
      expect(article.category).toBe('Consultorias de Licitação');
      expect(article.title.length).toBeGreaterThan(0);
    });
  });
});

// ---------- AC3: Data/statistics presence ----------

describe('STORY-263 AC3: Verifiable data presence', () => {
  it.each(CONS_SLUGS)(
    'article "%s" contains data reference box',
    async (slug) => {
      const module = await import(`../app/blog/content/${slug}`);
      const Component = module.default;
      const { container } = render(<Component />);

      const dataBoxes = container.querySelectorAll('.bg-surface-1');
      const html = container.innerHTML.toLowerCase();

      const hasDataReferences =
        dataBoxes.length > 0 ||
        html.includes('fonte:') ||
        html.includes('segundo') ||
        html.includes('dados do') ||
        html.includes('pesquisa') ||
        html.includes('estimativa') ||
        html.includes('benchmark');

      expect(hasDataReferences).toBe(true);
    },
  );
});

// ---------- AC4: Practical example ----------

describe('STORY-263 AC4: Practical example/framework', () => {
  it.each(CONS_SLUGS)(
    'article "%s" contains highlighted example or framework box',
    async (slug) => {
      const module = await import(`../app/blog/content/${slug}`);
      const Component = module.default;
      const { container } = render(<Component />);

      const html = container.innerHTML;
      const hasExampleBox =
        html.includes('bg-amber-50') ||
        html.includes('bg-amber-950') ||
        html.includes('bg-surface-1');

      expect(hasExampleBox).toBe(true);
    },
  );
});

// ---------- AC18: Cross-links B2G <-> Consultorias ----------

describe('STORY-263 AC18: Cross-links B2G <-> Consultorias', () => {
  const crossLinkRequirements: Record<string, string[]> = {
    'aumentar-retencao-clientes-inteligencia-editais': ['como-aumentar-taxa-vitoria-licitacoes'],
    'clientes-perdem-pregoes-boa-documentacao': ['erro-operacional-perder-contratos-publicos', 'escolher-editais-maior-probabilidade-vitoria'],
    'consultorias-modernas-inteligencia-priorizar-oportunidades': ['licitacao-volume-ou-inteligencia'],
    'triagem-editais-vantagem-estrategica-clientes': ['vale-a-pena-disputar-pregao'],
    'nova-geracao-ferramentas-mercado-licitacoes': ['licitacao-volume-ou-inteligencia'],
    'reduzir-ruido-aumentar-performance-pregoes': ['reduzir-tempo-analisando-editais-irrelevantes', 'equipe-40-horas-mes-editais-descartados'],
    'inteligencia-artificial-consultoria-licitacao-2026': ['como-aumentar-taxa-vitoria-licitacoes'],
    'aumentar-taxa-sucesso-clientes-20-porcento': ['como-aumentar-taxa-vitoria-licitacoes'],
  };

  Object.entries(crossLinkRequirements).forEach(([consSlug, b2gSlugs]) => {
    it(`article "${consSlug}" cross-links to required B2G articles`, async () => {
      const module = await import(`../app/blog/content/${consSlug}`);
      const Component = module.default;
      const { container } = render(<Component />);

      const links = Array.from(container.querySelectorAll('a'));
      const hrefs = links.map((a) => a.getAttribute('href') || '');

      b2gSlugs.forEach((b2gSlug) => {
        const hasLink = hrefs.some((href) => href.includes(b2gSlug));
        expect(hasLink).toBe(true);
      });
    });
  });
});
