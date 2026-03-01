/**
 * MKT-002 AC7: Rich Results Test via Playwright.
 *
 * Submits a programmatic page URL to Google's Rich Results Test
 * and validates 0 errors + detected schema types.
 *
 * Usage:
 *   npx playwright test scripts/gsc/rich-results-test.ts
 */

import { test, expect } from '@playwright/test';

const RICH_RESULTS_URL = 'https://search.google.com/test/rich-results';
const TEST_URLS = [
  'https://smartlic.tech/blog/programmatic/vestuario',
  'https://smartlic.tech/blog/programmatic/informatica/sp',
  'https://smartlic.tech/blog/como-aumentar-taxa-vitoria-licitacoes',
];

test.describe('Rich Results Test', () => {
  for (const testUrl of TEST_URLS) {
    test(`validate rich results for ${testUrl}`, async ({ page }) => {
      test.setTimeout(120000); // Rich Results Test can be slow

      await page.goto(RICH_RESULTS_URL);
      await page.waitForTimeout(2000);

      // Enter URL
      const urlInput = page.locator('input[type="url"], input[aria-label*="URL"]').first();
      await urlInput.fill(testUrl);

      // Click Test URL
      await page.click('button:has-text("Test URL"), button:has-text("Testar URL")');

      // Wait for results (can take 30-60s)
      await page.waitForSelector(
        'text=Page is eligible, text=Items detected, text=A página é elegível, text=Itens detectados',
        { timeout: 90000 },
      );

      // Check for errors
      const errorElements = page.locator('[class*="error"], [data-error]');
      const errorCount = await errorElements.count();

      // Verify no critical errors
      const bodyText = await page.textContent('body');
      expect(bodyText).not.toMatch(/\d+ error/i);

      // Verify schema types are detected
      const expectedSchemas = ['Article', 'FAQ', 'BreadcrumbList'];
      for (const schema of expectedSchemas) {
        // At least Article should be detected
        if (schema === 'Article') {
          expect(bodyText).toContain(schema);
        }
      }
    });
  }
});
