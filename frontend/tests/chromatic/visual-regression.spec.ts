/**
 * DEBT-08 AC3 (TD-036): Chromatic visual regression — 10 critical screens.
 *
 * Uses @chromatic-com/playwright to capture snapshots of the 10 most critical
 * screens and submit them to Chromatic for baseline comparison.
 *
 * Screens:
 *  1.  Landing page (/)
 *  2.  Login page (/login)
 *  3.  Signup page (/signup)
 *  4.  Buscar page (/buscar) — main search UI
 *  5.  Dashboard page (/dashboard)
 *  6.  Pipeline page (/pipeline)
 *  7.  Planos page (/planos) — pricing
 *  8.  Conta page (/conta) — account settings
 *  9.  Ajuda page (/ajuda) — help center
 * 10.  Historico page (/historico) — search history
 *
 * On main branch: snapshots become new baselines (--auto-accept-changes flag).
 * On PRs: Chromatic posts a visual diff review link to the PR (AC5).
 *
 * To add CHROMATIC_PROJECT_TOKEN:
 *   gh secret set CHROMATIC_PROJECT_TOKEN --body <token>
 */

import { test } from '@chromatic-com/playwright';

// ─── Helpers ─────────────────────────────────────────────────────────────────

/**
 * Mock common API routes so pages render predictably without a live backend.
 */
async function mockCommonAPIs(page: Parameters<typeof test.use>[0] extends { page: infer P } ? P : never) {
  // Setores
  await (page as any).route('**/api/setores**', async (route: any) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        setores: [
          { id: 'construcao_civil', name: 'Construção Civil', description: 'Obras e infraestrutura' },
          { id: 'ti', name: 'TI e Software', description: 'Tecnologia da informação' },
        ],
      }),
    });
  });

  // Plans
  await (page as any).route('**/api/plans**', async (route: any) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        plans: [
          {
            id: 'smartlic_pro',
            name: 'SmartLic Pro',
            price_monthly: 39700,
            price_semiannual: 35700,
            price_annual: 29700,
            features: ['1000 buscas/mês', 'Excel export', 'Pipeline Kanban'],
          },
        ],
      }),
    });
  });

  // Me / user profile
  await (page as any).route('**/api/me**', async (route: any) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: 'usr-test-001',
        email: 'demo@smartlic.tech',
        plan_id: 'smartlic_pro',
        plan_name: 'SmartLic Pro',
        credits_remaining: 100,
        trial_active: false,
      }),
    });
  });
}

// ─── Screen 1: Landing page ───────────────────────────────────────────────────
test('Visual — 01: Landing page (/)', async ({ page, takeSnapshot }) => {
  await page.goto('/');
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(500); // Allow animations to settle
  await takeSnapshot(page, '01-landing');
});

// ─── Screen 2: Login page ────────────────────────────────────────────────────
test('Visual — 02: Login page (/login)', async ({ page, takeSnapshot }) => {
  await page.goto('/login');
  await page.waitForLoadState('domcontentloaded');
  await page.waitForSelector('form', { timeout: 10000 }).catch(() => {});
  await page.waitForTimeout(300);
  await takeSnapshot(page, '02-login');
});

// ─── Screen 3: Signup page ───────────────────────────────────────────────────
test('Visual — 03: Signup page (/signup)', async ({ page, takeSnapshot }) => {
  await page.goto('/signup');
  await page.waitForLoadState('domcontentloaded');
  await page.waitForSelector('form', { timeout: 10000 }).catch(() => {});
  await page.waitForTimeout(300);
  await takeSnapshot(page, '03-signup');
});

// ─── Screen 4: Buscar page (main search UI) ──────────────────────────────────
test('Visual — 04: Buscar page (/buscar)', async ({ page, takeSnapshot }) => {
  // Mock setores for search form to render
  await page.route('**/api/setores**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        setores: [
          { id: 'construcao_civil', name: 'Construção Civil' },
          { id: 'ti', name: 'TI e Software' },
        ],
      }),
    });
  });

  await page.goto('/buscar');
  await page.waitForLoadState('domcontentloaded');
  await page.waitForSelector('[data-testid="search-form"], form, main', { timeout: 10000 }).catch(() => {});
  await page.waitForTimeout(500);
  await takeSnapshot(page, '04-buscar');
});

// ─── Screen 5: Dashboard ─────────────────────────────────────────────────────
test('Visual — 05: Dashboard page (/dashboard)', async ({ page, takeSnapshot }) => {
  await mockCommonAPIs(page as any);

  // Analytics
  await page.route('**/api/analytics**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        total_searches: 42,
        total_results: 314,
        searches_over_time: [
          { date: '2026-04-01', count: 5 },
          { date: '2026-04-02', count: 8 },
          { date: '2026-04-03', count: 12 },
        ],
        top_sectors: [{ sector: 'Construção Civil', count: 20 }],
        top_ufs: [{ uf: 'SP', count: 15 }],
      }),
    });
  });

  await page.goto('/dashboard');
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(1000);
  await takeSnapshot(page, '05-dashboard');
});

// ─── Screen 6: Pipeline Kanban ───────────────────────────────────────────────
test('Visual — 06: Pipeline page (/pipeline)', async ({ page, takeSnapshot }) => {
  await mockCommonAPIs(page as any);

  await page.route('**/api/pipeline**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: [
          {
            id: 'pipe-001',
            user_id: 'usr-test-001',
            pncp_id: 'PNCP-001-2026',
            objeto: 'Aquisição de materiais de construção',
            orgao: 'Prefeitura Municipal de São Paulo',
            uf: 'SP',
            valor_estimado: 250000,
            data_encerramento: '2026-04-25',
            stage: 'descoberta',
            notes: null,
            search_id: null,
            created_at: '2026-04-01T10:00:00Z',
            updated_at: '2026-04-01T10:00:00Z',
            version: 1,
            link_pncp: null,
          },
        ],
        total: 1,
        limit: 50,
        offset: 0,
      }),
    });
  });

  await page.goto('/pipeline');
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(1000);
  await takeSnapshot(page, '06-pipeline');
});

// ─── Screen 7: Planos (Pricing) ──────────────────────────────────────────────
test('Visual — 07: Planos page (/planos)', async ({ page, takeSnapshot }) => {
  await mockCommonAPIs(page as any);
  await page.goto('/planos');
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(500);
  await takeSnapshot(page, '07-planos');
});

// ─── Screen 8: Conta (Account settings) ─────────────────────────────────────
test('Visual — 08: Conta page (/conta)', async ({ page, takeSnapshot }) => {
  await mockCommonAPIs(page as any);

  await page.route('**/api/subscription**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        status: 'active',
        plan_id: 'smartlic_pro',
        plan_name: 'SmartLic Pro',
        current_period_end: '2026-05-01',
      }),
    });
  });

  await page.goto('/conta');
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(1000);
  await takeSnapshot(page, '08-conta');
});

// ─── Screen 9: Ajuda (Help center) ───────────────────────────────────────────
test('Visual — 09: Ajuda page (/ajuda)', async ({ page, takeSnapshot }) => {
  await page.goto('/ajuda');
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(500);
  await takeSnapshot(page, '09-ajuda');
});

// ─── Screen 10: Histórico (Search history) ───────────────────────────────────
test('Visual — 10: Historico page (/historico)', async ({ page, takeSnapshot }) => {
  await mockCommonAPIs(page as any);

  await page.route('**/api/sessions**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        sessions: [
          {
            id: 'sess-001',
            termo: 'uniforme escolar',
            setor: 'Educação',
            ufs: ['SP', 'RJ'],
            created_at: '2026-04-05T14:30:00Z',
            total_results: 12,
          },
        ],
        total: 1,
      }),
    });
  });

  await page.goto('/historico');
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(1000);
  await takeSnapshot(page, '10-historico');
});
