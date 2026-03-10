/**
 * DEBT-108 AC10/AC11: Bundle size budget — 250 KB gzipped first load JS.
 *
 * Run locally: npx size-limit
 * CI: runs in frontend-tests.yml, fails build if exceeded.
 */
module.exports = [
  {
    name: 'First Load JS (total)',
    path: '.next/static/chunks/**/*.js',
    gzip: true,
    limit: '250 KB',
  },
];
