/**
 * MKT-002 AC8: Weekly GSC health check via Playwright.
 *
 * Navigates to GSC, exports performance data for /blog/ pages,
 * checks indexation coverage, and generates weekly report.
 *
 * Usage:
 *   npx playwright test scripts/gsc/weekly-health-check.ts
 *
 * Output:
 *   docs/validation/gsc-weekly-{date}.md
 */

import { test, expect } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

const GSC_URL = 'https://search.google.com/search-console';
const SITE_URL = 'https://smartlic.tech';

interface HealthCheckReport {
  date: string;
  performance: {
    impressions: string;
    clicks: string;
    ctr: string;
    avgPosition: string;
  };
  indexation: {
    indexed: string;
    notIndexed: string;
    errors: string[];
  };
  crawlErrors: string[];
}

test.describe('Weekly GSC Health Check', () => {
  test('collect performance and indexation data', async ({ page }) => {
    const email = process.env.GSC_EMAIL;
    const password = process.env.GSC_PASSWORD;

    if (!email || !password) {
      test.skip(true, 'GSC_EMAIL and GSC_PASSWORD env vars required');
      return;
    }

    test.setTimeout(180000); // 3 min timeout

    // Login
    await page.goto('https://accounts.google.com/signin');
    await page.fill('input[type="email"]', email);
    await page.click('button:has-text("Next"), #identifierNext');
    await page.waitForTimeout(2000);
    await page.fill('input[type="password"]', password);
    await page.click('button:has-text("Next"), #passwordNext');
    await page.waitForTimeout(3000);

    const report: HealthCheckReport = {
      date: new Date().toISOString().split('T')[0],
      performance: {
        impressions: 'N/A',
        clicks: 'N/A',
        ctr: 'N/A',
        avgPosition: 'N/A',
      },
      indexation: {
        indexed: 'N/A',
        notIndexed: 'N/A',
        errors: [],
      },
      crawlErrors: [],
    };

    // Navigate to Performance → filter by /blog/
    try {
      await page.goto(
        `${GSC_URL}/performance/search-analytics?resource_id=${encodeURIComponent(SITE_URL)}&page=*%2Fblog%2F*`,
      );
      await page.waitForTimeout(5000);

      // Try to extract performance metrics from the page
      const metrics = await page.evaluate(() => {
        const cards = document.querySelectorAll('[class*="metric"], [class*="stat"]');
        const texts: string[] = [];
        cards.forEach((card) => {
          const text = card.textContent?.trim();
          if (text) texts.push(text);
        });
        return texts;
      });

      if (metrics.length >= 4) {
        report.performance = {
          impressions: metrics[0] || 'N/A',
          clicks: metrics[1] || 'N/A',
          ctr: metrics[2] || 'N/A',
          avgPosition: metrics[3] || 'N/A',
        };
      }
    } catch (e) {
      report.performance.impressions = `Error: ${e}`;
    }

    // Navigate to Pages (Indexation)
    try {
      await page.goto(
        `${GSC_URL}/index?resource_id=${encodeURIComponent(SITE_URL)}`,
      );
      await page.waitForTimeout(5000);

      const pageContent = await page.textContent('body');
      // Extract indexed count if visible
      const indexedMatch = pageContent?.match(/(\d+)\s*(indexed|indexada)/i);
      if (indexedMatch) {
        report.indexation.indexed = indexedMatch[1];
      }

      // Check for 404/5xx errors in blog URLs
      const errorElements = await page.locator('text=/blog/').allTextContents();
      report.crawlErrors = errorElements.filter(
        (text) => text.includes('404') || text.includes('5xx'),
      );
    } catch (e) {
      report.indexation.errors.push(`Error collecting indexation: ${e}`);
    }

    // Generate report
    const reportMd = generateReport(report);
    const outputDir = path.resolve('docs/validation');
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    const outputPath = path.join(outputDir, `gsc-weekly-${report.date}.md`);
    fs.writeFileSync(outputPath, reportMd, 'utf-8');

    // Verify report was created
    expect(fs.existsSync(outputPath)).toBe(true);
  });
});

function generateReport(report: HealthCheckReport): string {
  return `# GSC Weekly Health Check — ${report.date}

## Performance (last 28 days, /blog/ pages)

| Metric | Value |
|--------|-------|
| Impressions | ${report.performance.impressions} |
| Clicks | ${report.performance.clicks} |
| CTR | ${report.performance.ctr} |
| Avg Position | ${report.performance.avgPosition} |

## Indexation Status

| Metric | Value |
|--------|-------|
| Indexed Pages | ${report.indexation.indexed} |
| Not Indexed | ${report.indexation.notIndexed} |

${report.indexation.errors.length > 0 ? `### Errors\n${report.indexation.errors.map((e) => `- ${e}`).join('\n')}` : 'No indexation errors detected.'}

## Crawl Errors (/blog/ URLs)

${report.crawlErrors.length > 0 ? report.crawlErrors.map((e) => `- ${e}`).join('\n') : 'No crawl errors detected for blog URLs.'}

---
*Generated by MKT-002 AC8 Playwright health check script*
`;
}
