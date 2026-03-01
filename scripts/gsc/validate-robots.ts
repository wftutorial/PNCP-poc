/**
 * MKT-002 AC7: Validate robots.txt via Playwright.
 *
 * Navigates to GSC robots.txt testing tool and verifies
 * no blog URLs are blocked.
 *
 * Usage:
 *   npx playwright test scripts/gsc/validate-robots.ts
 */

import { test, expect } from '@playwright/test';

const SITE_URL = 'https://smartlic.tech';
const BLOG_URLS = [
  '/blog',
  '/blog/como-aumentar-taxa-vitoria-licitacoes',
  '/blog/programmatic/vestuario',
  '/blog/programmatic/vestuario/sp',
  '/sitemap-blog.xml',
];

test.describe('Robots.txt Validation', () => {
  test('robots.txt is accessible and well-formed', async ({ page }) => {
    const response = await page.goto(`${SITE_URL}/robots.txt`);
    expect(response?.status()).toBe(200);

    const content = await page.textContent('body');
    expect(content).toContain('User-agent: *');
    expect(content).toContain('Allow: /');
    expect(content).toContain('Sitemap: https://smartlic.tech/sitemap-blog.xml');
    expect(content).not.toContain('Disallow: /blog');
  });

  test('blog URLs are not blocked by robots.txt', async ({ page }) => {
    const response = await page.goto(`${SITE_URL}/robots.txt`);
    const content = await response?.text() || '';

    // Parse Disallow rules
    const disallowRules = content
      .split('\n')
      .filter((line) => line.startsWith('Disallow:'))
      .map((line) => line.replace('Disallow:', '').trim());

    // Verify no blog URL matches any Disallow rule
    for (const blogUrl of BLOG_URLS) {
      for (const rule of disallowRules) {
        if (rule && blogUrl.startsWith(rule)) {
          throw new Error(
            `Blog URL ${blogUrl} is blocked by Disallow: ${rule}`,
          );
        }
      }
    }
  });

  test('sitemap-blog.xml is accessible', async ({ page }) => {
    const response = await page.goto(`${SITE_URL}/sitemap-blog.xml`);
    expect(response?.status()).toBe(200);

    const content = await page.textContent('body');
    expect(content).toContain('<?xml');
    expect(content).toContain('<urlset');
    expect(content).toContain('/blog/');
  });
});
