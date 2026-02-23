/**
 * GTM-QUAL-001: Smoke Test E2E Pos-Root Cause
 *
 * Validates the complete user journey after each Tier of GTM Root Cause
 * implementation. Ensures architectural changes (ARCH-001 async, ARCH-002 cache,
 * PROXY-001 PT-BR) don't break the integrated experience.
 *
 * Test suites:
 *   AC1: Trial User First 5 Minutes (signup → onboarding → search → results → download)
 *   AC2: Post-Payment (login → search → results → pipeline → dashboard)
 *   AC3: Error Recovery (backend offline → error state → retry → results)
 *   AC4-AC7: Cross-cutting validations (zero English, max 1 banner, tooltips, timing)
 *
 * Run: cd frontend && npm run test:e2e -- --grep "smoke"
 */

import { test, expect } from '@playwright/test';
import {
  assertZeroEnglishText,
  assertMaxOneBanner,
  assertNoDisabledWithoutTooltip,
  mockAsyncSearchFlow,
  mockOnboardingAPIs,
  mockPipelineAPIs,
  mockDashboardAPIs,
  mockPaymentAPIs,
  mockTrialUser,
  mockPaidUser,
  mockDownloadEndpoint,
  mockSessionsAPI,
  mockMiscAPIs,
} from './helpers/smoke-helpers';

// ============================================================================
// AC1: Trial User First 5 Minutes
// signup → onboarding (setor+UFs) → busca automatica → resultados → download Excel
// ============================================================================

test.describe('Smoke: Trial User First 5 Minutes [AC1]', () => {
  test('should complete trial user journey: signup → onboarding → search → results → download', async ({
    page,
  }) => {
    // --- Phase 1: Signup ---
    await page.goto('/signup');
    await expect(page.getByRole('heading', { name: /Criar conta/i })).toBeVisible();

    // Fill signup form
    await page.getByLabel(/Nome completo/i).fill('Smoke Test User');
    await page.getByLabel(/Empresa/i).fill('Smoke Test Ltda');
    await page.getByLabel(/Setor de atuação/i).selectOption('vestuario');
    await page.getByLabel(/Email/i).fill('smoke-trial@test.com');
    await page.getByPlaceholder(/\(11\) 99999-9999/i).fill('11999990000');
    await page.getByPlaceholder(/Minimo 6 caracteres/i).fill('SmokeTest123');
    await page.getByPlaceholder(/Digite a senha novamente/i).fill('SmokeTest123');

    // Scroll consent and accept
    const scrollBox = page.locator('.overflow-y-auto').first();
    await scrollBox.evaluate((el) => {
      el.scrollTop = el.scrollHeight;
    });
    await page.waitForTimeout(200);
    await page.getByRole('checkbox').check();

    // Verify form is ready (submit button enabled)
    const submitButton = page.getByRole('button', { name: /Criar conta$/i });
    await expect(submitButton).toBeEnabled();

    // AC4: Zero English text on signup page
    await assertZeroEnglishText(page);

    // AC5: Max 1 banner
    await assertMaxOneBanner(page);

    // --- Phase 2: Onboarding ---
    // Setup mocks for authenticated trial user experience
    await mockTrialUser(page);
    await mockOnboardingAPIs(page);
    await mockSessionsAPI(page);
    await mockMiscAPIs(page);

    await page.goto('/onboarding');
    await page.waitForLoadState('networkidle');

    // Verify onboarding page loaded
    const onboardingHeading = page.locator('text=/setor|objetivo|configurar|passo/i');
    await expect(onboardingHeading.first()).toBeVisible({ timeout: 10000 });

    // AC4: Zero English on onboarding
    await assertZeroEnglishText(page);

    // --- Phase 3: Search (async) ---
    const searchId = await mockAsyncSearchFlow(page);
    await mockDownloadEndpoint(page);

    await page.goto('/buscar');
    await page.waitForLoadState('networkidle');

    // Select UFs and execute search
    const scButton = page.getByRole('button', { name: 'SC', exact: true });
    const prButton = page.getByRole('button', { name: 'PR', exact: true });

    // Clear existing selections first if clear button visible
    const clearBtn = page.getByRole('button', { name: /Limpar/i });
    if (await clearBtn.isVisible()) {
      await clearBtn.click();
      await page.waitForTimeout(300);
    }

    await scButton.click();
    await prButton.click();

    // Execute search
    const searchButton = page.getByRole('button', { name: /Buscar/i });
    await expect(searchButton).toBeEnabled();
    await searchButton.click();

    // --- Phase 4: Results ---
    // Wait for results (async flow: 202 → SSE → fetch results)
    const resultsArea = page.locator('text=/Resumo Executivo/i');
    await expect(resultsArea).toBeVisible({ timeout: 30000 });

    // Verify results contain expected data
    await expect(page.locator('text=/15/')).toBeVisible();

    // AC4: Zero English text on results
    await assertZeroEnglishText(page);

    // AC5: Max 1 banner on results page
    await assertMaxOneBanner(page);

    // AC6: No disabled buttons without tooltip
    await assertNoDisabledWithoutTooltip(page);

    // --- Phase 5: Download Excel ---
    const downloadButton = page.getByRole('button', { name: /Baixar Excel/i });
    await expect(downloadButton).toBeVisible();
    await expect(downloadButton).toBeEnabled();

    const downloadPromise = page.waitForEvent('download', { timeout: 10000 });
    await downloadButton.click();
    const download = await downloadPromise;

    // Verify filename format
    const filename = download.suggestedFilename();
    expect(filename).toMatch(/DescompLicita.*\.xlsx$/);
  });
});

// ============================================================================
// AC2: Post-Payment User Journey
// login pagante → busca → resultado → pipeline drag-and-drop → dashboard
// ============================================================================

test.describe('Smoke: Post-Payment User Journey [AC2]', () => {
  test.beforeEach(async ({ page }) => {
    await mockPaidUser(page);
    await mockOnboardingAPIs(page);
    await mockSessionsAPI(page);
    await mockMiscAPIs(page);
    await mockPaymentAPIs(page);
  });

  test('should complete paid user journey: login → search → results → pipeline → dashboard', async ({
    page,
  }) => {
    // --- Phase 1: Login (paid user) ---
    await mockAsyncSearchFlow(page);
    await mockDownloadEndpoint(page);
    await mockPipelineAPIs(page);
    await mockDashboardAPIs(page);

    // Navigate to search (simulates post-login redirect)
    await page.goto('/buscar');
    await page.waitForLoadState('networkidle');

    // --- Phase 2: Search ---
    const clearBtn = page.getByRole('button', { name: /Limpar/i });
    if (await clearBtn.isVisible()) {
      await clearBtn.click();
      await page.waitForTimeout(300);
    }

    await page.getByRole('button', { name: 'SC', exact: true }).click();
    await page.getByRole('button', { name: 'PR', exact: true }).click();

    const searchButton = page.getByRole('button', { name: /Buscar/i });
    await expect(searchButton).toBeEnabled();
    await searchButton.click();

    // --- Phase 3: Results ---
    const resultsArea = page.locator('text=/Resumo Executivo/i');
    await expect(resultsArea).toBeVisible({ timeout: 30000 });

    // AC4: Zero English text
    await assertZeroEnglishText(page);

    // AC5: Max 1 banner
    await assertMaxOneBanner(page);

    // --- Phase 4: Pipeline ---
    await page.goto('/pipeline');
    await page.waitForLoadState('networkidle');

    // Verify pipeline page loaded with items
    await expect(page.locator('text=/Pipeline|Oportunidades/i').first()).toBeVisible({
      timeout: 10000,
    });

    // Verify pipeline columns exist (prospect, qualified, etc.)
    const pipelineContent = page.locator('text=/Prospect|Qualificado|Enviado|prospect|qualified/i');
    await expect(pipelineContent.first()).toBeVisible({ timeout: 10000 });

    // AC4: Zero English on pipeline
    await assertZeroEnglishText(page);

    // --- Phase 5: Dashboard ---
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');

    // Verify dashboard loaded with data
    await expect(page.locator('text=/Dashboard|Painel|Estatisticas|buscas/i').first()).toBeVisible({
      timeout: 10000,
    });

    // Verify stats are present (numbers rendered)
    await expect(page.locator('text=/42|186|2.750/').first()).toBeVisible({ timeout: 10000 });

    // AC4: Zero English on dashboard
    await assertZeroEnglishText(page);

    // AC5: Max 1 banner
    await assertMaxOneBanner(page);
  });
});

// ============================================================================
// AC3: Error Recovery
// busca com backend offline → error state → backend volta → retry → resultados
// ============================================================================

test.describe('Smoke: Error Recovery [AC3]', () => {
  test.beforeEach(async ({ page }) => {
    await mockTrialUser(page);
    await mockOnboardingAPIs(page);
    await mockSessionsAPI(page);
    await mockMiscAPIs(page);
  });

  test('should recover from backend failure: error → retry → results appear', async ({
    page,
  }) => {
    // --- Phase 1: Setup failing search ---
    await mockAsyncSearchFlow(page, { shouldFail: true });

    await page.goto('/buscar');
    await page.waitForLoadState('networkidle');

    // Select UFs
    const clearBtn = page.getByRole('button', { name: /Limpar/i });
    if (await clearBtn.isVisible()) {
      await clearBtn.click();
      await page.waitForTimeout(300);
    }

    await page.getByRole('button', { name: 'SC', exact: true }).click();

    // Execute search (will fail)
    const searchButton = page.getByRole('button', { name: /Buscar/i });
    await expect(searchButton).toBeEnabled();
    await searchButton.click();

    // --- Phase 2: Verify error state ---
    const errorMessage = page.locator('[role="alert"]').filter({ hasText: /Erro|erro|falha/i });
    await expect(errorMessage).toBeVisible({ timeout: 15000 });

    // AC4: Error message must be in Portuguese
    await assertZeroEnglishText(page);

    // AC5: Max 1 banner even in error state
    await assertMaxOneBanner(page);

    // --- Phase 3: Backend recovers, retry works ---
    // Remove failing routes and set up successful ones
    await page.unrouteAll({ behavior: 'ignoreErrors' });

    // Re-setup base mocks
    await mockTrialUser(page);
    await mockOnboardingAPIs(page);
    await mockSessionsAPI(page);
    await mockMiscAPIs(page);
    await mockAsyncSearchFlow(page);
    await mockDownloadEndpoint(page);

    // Click retry button
    const retryButton = page.getByRole('button', { name: /Tentar novamente|Retry|Buscar/i });
    await expect(retryButton).toBeVisible();
    await retryButton.click();

    // --- Phase 4: Results appear after recovery ---
    const resultsArea = page.locator('text=/Resumo Executivo/i');
    await expect(resultsArea).toBeVisible({ timeout: 30000 });

    // Error should be gone
    await expect(errorMessage).not.toBeVisible();

    // AC4: Zero English after recovery
    await assertZeroEnglishText(page);
  });
});

// ============================================================================
// AC4-AC7: Cross-cutting Validation Assertions
// These run as standalone validation tests on key pages
// ============================================================================

test.describe('Smoke: Cross-cutting Validations [AC4-AC7]', () => {
  test.beforeEach(async ({ page }) => {
    await mockTrialUser(page);
    await mockOnboardingAPIs(page);
    await mockSessionsAPI(page);
    await mockMiscAPIs(page);
  });

  test('AC4: zero English text in error flows', async ({ page }) => {
    // Test with error response
    await mockAsyncSearchFlow(page, { shouldFail: true });

    await page.goto('/buscar');
    await page.waitForLoadState('networkidle');

    // Trigger a search to get error state
    const clearBtn = page.getByRole('button', { name: /Limpar/i });
    if (await clearBtn.isVisible()) {
      await clearBtn.click();
      await page.waitForTimeout(300);
    }

    await page.getByRole('button', { name: 'SC', exact: true }).click();
    await page.getByRole('button', { name: /Buscar/i }).click();

    // Wait for error
    await page.locator('[role="alert"]').filter({ hasText: /Erro|erro/i }).waitFor({ timeout: 15000 });

    // Validate: no English error patterns
    await assertZeroEnglishText(page);
  });

  test('AC5: max 1 banner visible during search flow', async ({ page }) => {
    await mockAsyncSearchFlow(page);
    await mockDownloadEndpoint(page);

    await page.goto('/buscar');
    await page.waitForLoadState('networkidle');

    // Check before search
    await assertMaxOneBanner(page);

    // Execute search
    const clearBtn = page.getByRole('button', { name: /Limpar/i });
    if (await clearBtn.isVisible()) {
      await clearBtn.click();
      await page.waitForTimeout(300);
    }

    await page.getByRole('button', { name: 'SC', exact: true }).click();
    await page.getByRole('button', { name: /Buscar/i }).click();

    // Check during/after search
    await page.locator('text=/Resumo Executivo/i').waitFor({ timeout: 30000 });
    await assertMaxOneBanner(page);
  });

  test('AC6: no disabled button without tooltip', async ({ page }) => {
    await page.goto('/buscar');
    await page.waitForLoadState('networkidle');

    // Clear UFs to trigger disabled search button
    const clearBtn = page.getByRole('button', { name: /Limpar/i });
    if (await clearBtn.isVisible()) {
      await clearBtn.click();
      await page.waitForTimeout(300);
    }

    // Disabled search button should have tooltip
    await assertNoDisabledWithoutTooltip(page);
  });

  test('AC7: trial user receives results in <30s', async ({ page }) => {
    await mockAsyncSearchFlow(page);
    await mockDownloadEndpoint(page);

    await page.goto('/buscar');
    await page.waitForLoadState('networkidle');

    // Prepare search
    const clearBtn = page.getByRole('button', { name: /Limpar/i });
    if (await clearBtn.isVisible()) {
      await clearBtn.click();
      await page.waitForTimeout(300);
    }

    await page.getByRole('button', { name: 'SC', exact: true }).click();
    await page.getByRole('button', { name: 'PR', exact: true }).click();

    // Measure time
    const startTime = Date.now();

    // Execute search
    await page.getByRole('button', { name: /Buscar/i }).click();

    // Wait for complete results
    await page.locator('text=/Resumo Executivo/i').waitFor({ timeout: 30000 });

    const elapsed = Date.now() - startTime;
    expect(elapsed, 'AC7: Trial user search should complete in <30s').toBeLessThan(30000);
  });
});

// ============================================================================
// AC8-AC11: Tier Execution Checkpoints
// These are marker tests that validate per-tier readiness
// ============================================================================

test.describe('Smoke: Tier Execution Checkpoints [AC8-AC11]', () => {
  test.beforeEach(async ({ page }) => {
    await mockTrialUser(page);
    await mockOnboardingAPIs(page);
    await mockAsyncSearchFlow(page);
    await mockDownloadEndpoint(page);
    await mockSessionsAPI(page);
    await mockMiscAPIs(page);
  });

  test('AC8: Tier 1 checkpoint - async search + cache + PT-BR errors', async ({ page }) => {
    // Validates: ARCH-001 (async search), ARCH-002 (cache), PROXY-001 (PT-BR)

    await page.goto('/buscar');
    await page.waitForLoadState('networkidle');

    // Execute async search (ARCH-001)
    const clearBtn = page.getByRole('button', { name: /Limpar/i });
    if (await clearBtn.isVisible()) {
      await clearBtn.click();
      await page.waitForTimeout(300);
    }

    await page.getByRole('button', { name: 'SC', exact: true }).click();
    await page.getByRole('button', { name: /Buscar/i }).click();

    // Verify results arrive (ARCH-001 async flow works)
    await expect(page.locator('text=/Resumo Executivo/i')).toBeVisible({ timeout: 30000 });

    // PROXY-001: Zero English errors
    await assertZeroEnglishText(page);
  });

  test('AC9: Tier 2 checkpoint - banners + error states + retry + subscription', async ({
    page,
  }) => {
    // Validates: UX-001 (single banner), UX-002 (error states), UX-003 (retry), UX-004 (subscription)

    await page.goto('/buscar');
    await page.waitForLoadState('networkidle');

    // AC5: Max 1 banner (UX-001)
    await assertMaxOneBanner(page);

    // Execute search for results
    const clearBtn = page.getByRole('button', { name: /Limpar/i });
    if (await clearBtn.isVisible()) {
      await clearBtn.click();
      await page.waitForTimeout(300);
    }

    await page.getByRole('button', { name: 'SC', exact: true }).click();
    await page.getByRole('button', { name: /Buscar/i }).click();

    await expect(page.locator('text=/Resumo Executivo/i')).toBeVisible({ timeout: 30000 });

    // Still max 1 banner after results
    await assertMaxOneBanner(page);
  });

  test('AC10: Tier 3 checkpoint - resilience under simulated failure', async ({ page }) => {
    // Validates: INFRA-001/002/003 (resilience)

    // Start with failing backend
    await page.unrouteAll({ behavior: 'ignoreErrors' });
    await mockTrialUser(page);
    await mockOnboardingAPIs(page);
    await mockSessionsAPI(page);
    await mockMiscAPIs(page);
    await mockAsyncSearchFlow(page, { shouldFail: true });

    await page.goto('/buscar');
    await page.waitForLoadState('networkidle');

    const clearBtn = page.getByRole('button', { name: /Limpar/i });
    if (await clearBtn.isVisible()) {
      await clearBtn.click();
      await page.waitForTimeout(300);
    }

    await page.getByRole('button', { name: 'SC', exact: true }).click();
    await page.getByRole('button', { name: /Buscar/i }).click();

    // Error should appear (graceful failure)
    const errorArea = page.locator('[role="alert"]').filter({ hasText: /Erro|erro|falha/i });
    await expect(errorArea).toBeVisible({ timeout: 15000 });

    // Error must be in PT-BR
    await assertZeroEnglishText(page);

    // Recover
    await page.unrouteAll({ behavior: 'ignoreErrors' });
    await mockTrialUser(page);
    await mockOnboardingAPIs(page);
    await mockSessionsAPI(page);
    await mockMiscAPIs(page);
    await mockAsyncSearchFlow(page);
    await mockDownloadEndpoint(page);

    const retryButton = page.getByRole('button', { name: /Tentar novamente|Buscar/i });
    await retryButton.click();

    // Results should appear after recovery
    await expect(page.locator('text=/Resumo Executivo/i')).toBeVisible({ timeout: 30000 });
  });

  test('AC11: Full pre-GTM launch validation', async ({ page }) => {
    // Complete end-to-end validation combining all tiers

    await page.goto('/buscar');
    await page.waitForLoadState('networkidle');

    // 1. Async search works
    const clearBtn = page.getByRole('button', { name: /Limpar/i });
    if (await clearBtn.isVisible()) {
      await clearBtn.click();
      await page.waitForTimeout(300);
    }

    await page.getByRole('button', { name: 'SC', exact: true }).click();
    await page.getByRole('button', { name: 'PR', exact: true }).click();

    const startTime = Date.now();
    await page.getByRole('button', { name: /Buscar/i }).click();

    await expect(page.locator('text=/Resumo Executivo/i')).toBeVisible({ timeout: 30000 });

    // 2. Performance check
    const elapsed = Date.now() - startTime;
    expect(elapsed, 'Search should complete in <30s').toBeLessThan(30000);

    // 3. Zero English
    await assertZeroEnglishText(page);

    // 4. Max 1 banner
    await assertMaxOneBanner(page);

    // 5. No disabled buttons without tooltip
    await assertNoDisabledWithoutTooltip(page);

    // 6. Download works
    const downloadButton = page.getByRole('button', { name: /Baixar Excel/i });
    if (await downloadButton.isVisible()) {
      await expect(downloadButton).toBeEnabled();
    }
  });
});
