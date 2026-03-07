/**
 * CRIT-072: E2E — Async-First 202 Pattern
 *
 * AC11: Complete search via 202+SSE flow.
 *
 * Steps:
 * 1. POST /api/buscar returns 202 with search_id, status_url, results_url
 * 2. SSE stream delivers progress events + search_complete with results_url
 * 3. Frontend fetches results from results_url
 * 4. Results displayed to user
 */

import { test, expect } from '@playwright/test';
import { SearchPage } from './helpers/page-objects';
import {
  mockAsyncSearchFlow,
} from './helpers/smoke-helpers';
import {
  mockSetoresAPI,
  mockDownloadAPI,
  clearTestData,
} from './helpers/test-utils';

test.describe('CRIT-072: Async-First 202 Search Flow', () => {
  let searchPage: SearchPage;

  test.beforeEach(async ({ page }) => {
    searchPage = new SearchPage(page);

    // Setup common mocks
    await mockSetoresAPI(page);
    await mockDownloadAPI(page);
  });

  test('AC11: complete search via 202+SSE flow shows results', async ({ page }) => {
    // Setup 202 async search mocks (POST→202, SSE→events, GET→results)
    const searchId = await mockAsyncSearchFlow(page);

    // Navigate to search page
    await searchPage.goto();
    await clearTestData(page);

    // Select UFs
    await searchPage.clearUFSelection();
    await searchPage.selectUF('SC');
    await searchPage.selectUF('PR');

    // Execute search
    await searchPage.executeSearch();

    // Verify results are displayed (fetched via 202+SSE flow)
    await expect(searchPage.executiveSummary).toBeVisible({ timeout: 15000 });
    await expect(searchPage.resultsSection).toContainText(/15/); // total_oportunidades
  });

  test('AC11: 202 response shows progress via SSE before results', async ({ page }) => {
    // Track intercepted requests to verify flow
    const interceptedRequests: { url: string; status: number }[] = [];

    // Setup mocks with request tracking
    const searchId = await mockAsyncSearchFlow(page);

    page.on('response', (response) => {
      const url = response.url();
      if (url.includes('/api/buscar') && !url.includes('progress')) {
        interceptedRequests.push({ url, status: response.status() });
      }
    });

    await searchPage.goto();
    await clearTestData(page);

    await searchPage.clearUFSelection();
    await searchPage.selectUF('SC');

    await searchPage.executeSearch();

    // Wait for results to appear
    await expect(searchPage.executiveSummary).toBeVisible({ timeout: 15000 });

    // Verify POST /api/buscar returned 202
    const buscarResponse = interceptedRequests.find(
      (r) => r.url.includes('/api/buscar') && !r.url.includes('progress')
    );
    expect(buscarResponse).toBeDefined();
    expect(buscarResponse!.status).toBe(202);
  });

  test('AC11: SSE error triggers fallback (no crash)', async ({ page }) => {
    // Setup async search that fails via SSE
    await mockAsyncSearchFlow(page, { shouldFail: true });

    await searchPage.goto();
    await clearTestData(page);

    await searchPage.clearUFSelection();
    await searchPage.selectUF('SP');

    await searchPage.executeSearch();

    // Should show error message, not crash
    await expect(searchPage.errorMessage).toBeVisible({ timeout: 15000 });
  });
});
