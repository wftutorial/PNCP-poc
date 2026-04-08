/**
 * DEBT-08 AC3: Chromatic configuration for Playwright integration.
 *
 * Defines the 10 critical screens for visual regression testing.
 * Uses @chromatic-com/playwright — no Storybook required.
 *
 * Setup:
 *   1. Create a Chromatic project at chromatic.com
 *   2. Add CHROMATIC_PROJECT_TOKEN to GitHub repo secrets:
 *      gh secret set CHROMATIC_PROJECT_TOKEN --body <token-from-chromatic>
 *   3. CI workflow (.github/workflows/chromatic.yml) runs automatically on PRs.
 */

import { defineConfig } from '@chromatic-com/playwright';

export default defineConfig({
  /** Path to Playwright tests directory */
  testDir: './tests/chromatic',

  /** Only match the visual regression spec */
  testMatch: '**/visual-regression.spec.ts',

  /** Chromatic snapshot options */
  snapshotOptions: {
    // Delay before capturing snapshot (ms) — allows animations to settle
    delay: 300,
    // Pixel diffing threshold (0 = exact match, 0.063 = ~6% tolerance for anti-aliasing)
    diffThreshold: 0.063,
  },
});
