# GTM Readiness Assessment -- DRAFT

**Project:** SmartLic | **Date:** 2026-03-10 | **Status:** PENDING SPECIALIST REVIEW
**Assessor:** @architect (Atlas) -- Phase 4 Consolidation
**Pricing target:** SmartLic Pro R$397/mo, Consultoria R$997/mo

---

## Overall GTM Readiness Score

### 7.5 / 10 -- YELLOW-GREEN: Proceed with targeted fixes

SmartLic is architecturally ready for paying customers. The system handles failures gracefully, billing is well-integrated with Stripe, auth is production-grade (JWT ES256+JWKS, RLS on all 32 tables), and the frontend provides a polished experience with comprehensive error handling. There are **no hard blockers** preventing launch.

However, there are **two security issues** (RLS policy gaps on `pipeline_items` and `search_results_cache`) that, while unlikely to be exploited by typical users, represent cross-user data exposure risk that is unacceptable for a paid B2G product. These are 10-line SQL fixes and should be deployed before the first paying customer.

**Key message:** Ship confidently after fixing the two RLS policies. Everything else is 30-90 day polish.

---

## Assessment Sources

| Source | Score | Verdict |
|--------|-------|---------|
| System Architecture (@architect) | 7.5/10 YELLOW | No blockers. CI gates advisory-only. Scaling ceiling at ~30 concurrent users. |
| Database (@data-engineer) | 7.8/10 YELLOW-GREEN | RLS on all tables but 2 service_role policies are overly permissive. LGPD cascade gaps. |
| Frontend/UX (@ux-design-expert) | 7.5/10 YELLOW-GREEN | Core loop polished. Landing page needs product screenshot. Trust signals need depth. |

---

## P0 -- GTM BLOCKERS (Must Fix Before First Paying Customer)

| ID | Finding | Domain | Impact | Effort | Owner |
|----|---------|--------|--------|--------|-------|
| P0-001 | `pipeline_items` RLS policy allows cross-user access | DB | Any authenticated user can read/modify other users' pipeline data | S (2h) | @data-engineer |
| P0-002 | `search_results_cache` RLS policy allows cross-user access | DB | Any authenticated user can read other users' cached search results | S (2h) | @data-engineer |

### P0 Detail

#### P0-001: pipeline_items service_role Policy Missing `TO service_role`

**What:** The policy `"Service role full access on pipeline_items"` uses `USING (true)` WITHOUT the `TO service_role` clause. In Supabase/PostgreSQL RLS, a policy without `TO` applies to ALL roles, meaning every authenticated user gets unrestricted access to every pipeline item in the system.

**Why this is P0:** Pipeline items contain business-sensitive data (which bids a company is pursuing, at what stage, with what notes). A competitor using SmartLic could read another company's pipeline strategy. For a product charging R$397-997/month to B2G companies, this is a trust-destroying scenario.

**How to fix:**
```sql
-- Migration: 20260310_fix_pipeline_rls.sql
DROP POLICY "Service role full access on pipeline_items" ON pipeline_items;
CREATE POLICY "service_role_all" ON pipeline_items
  FOR ALL TO service_role USING (true) WITH CHECK (true);
```

**Verification:** After applying, run as an authenticated (non-service-role) user:
```sql
SELECT count(*) FROM pipeline_items; -- Should return ONLY own items
```

**Source:** DB-AUDIT.md H-003, SCHEMA.md Table 11.

---

#### P0-002: search_results_cache service_role Policy Missing `TO service_role`

**What:** Same pattern as P0-001. The policy `"Service role full access on search_results_cache"` applies to all authenticated users, exposing every user's cached search results.

**Why this is P0:** Cached results contain the full search output (bids, values, classifications) for a user's specific sector/UF combination. Leaking this data means a competitor could see what sectors and regions another company is monitoring.

**How to fix:**
```sql
-- Same migration as P0-001
DROP POLICY "Service role full access on search_results_cache" ON search_results_cache;
CREATE POLICY "service_role_all" ON search_results_cache
  FOR ALL TO service_role USING (true) WITH CHECK (true);
```

**Source:** DB-AUDIT.md H-004, SCHEMA.md Table 9.

---

## P1 -- HIGH PRIORITY (First 30 Days)

| ID | Finding | Domain | Impact | Effort | Owner |
|----|---------|--------|--------|--------|-------|
| P1-001 | CI vulnerability scan is non-blocking | Backend/CI | HIGH CVE could ship to production | S (2h) | @devops |
| P1-002 | 5 tables have FKs to auth.users instead of profiles | DB | LGPD "right to erasure" incomplete -- orphan rows after account deletion | M (4-8h) | @data-engineer |
| P1-003 | search_results_store FK possibly NOT VALID | DB | Orphan search results could exist silently | S (2h) | @data-engineer |
| P1-004 | No graceful shutdown for in-flight searches | Backend | Every deploy causes ~30s of search failures for active users | M (4h) | @dev |
| P1-005 | Landing page has no product screenshot/video | Frontend | B2G buyers cannot see the product before signup -- kills conversion | M (4-8h) | @ux-design-expert |
| P1-006 | Landing page missing testimonials section | Frontend | Social proof gap at consideration stage | S (2h) | @ux-design-expert |
| P1-007 | search_sessions.status CHECK may reject valid states | DB/Backend | State manager writes 'consolidating'/'partial' but CHECK may reject them | S (2h) | @data-engineer |
| P1-008 | ComprasGov v3 offline -- no customer communication | Backend/UX | 1/3 data sources offline with no transparency to users | S (2h) | @pm |
| P1-009 | Single-instance scaling ceiling (~30 concurrent users) | Backend/Infra | Heavy usage during trial campaigns could degrade experience | L (8-16h) | @devops |
| P1-010 | Missing retention on 4 operational tables | DB | health_checks, mfa_recovery_attempts, stripe_webhook_events, search_state_transitions grow unbounded | S (2h) | @data-engineer |
| P1-011 | Dashboard lacks actionable insights | Frontend | Analytics show data but no proactive recommendations for retention | M (8h) | @ux-design-expert |

### P1 Detail

#### P1-001: CI Gates Advisory-Only

**pip-audit** (vulnerability scan), **ruff** (linting), and **mypy** (type checking) all have `continue-on-error: true` in GitHub Actions. A HIGH severity CVE in a dependency would not block deployment.

**Fix:** Remove `continue-on-error` from pip-audit at minimum. For ruff and mypy, either fix existing violations or set baseline exceptions.

**Source:** system-architecture.md H1.

---

#### P1-002: FK References to auth.users Instead of profiles

**Tables affected:** `trial_email_log`, `mfa_recovery_codes`, `mfa_recovery_attempts`, `organization_members`, `organizations.owner_id`

When a user deletes their account (profiles row CASCADE-deleted), these tables retain orphan rows because their FKs point to `auth.users(id)`, not `profiles(id)`. This violates LGPD "right to erasure" for paying customers who cancel.

**Fix:** Migration to alter FKs from `auth.users(id)` to `profiles(id) ON DELETE CASCADE` (or RESTRICT for `organizations.owner_id`).

**Source:** DB-AUDIT.md H-001.

---

#### P1-003: search_results_store FK Validation

The FK on `search_results_store.user_id` was created `NOT VALID`. DEBT-100 attempted validation, but the target may have changed between validation and FK recreation. Must verify in production.

**Fix:** Run `SELECT conname, convalidated FROM pg_constraint WHERE conrelid = 'public.search_results_store'::regclass AND contype = 'f';` and validate if needed.

**Source:** DB-AUDIT.md H-002.

---

#### P1-004: No Graceful Shutdown

Railway deploys send SIGTERM but the app does not drain in-flight requests. Active searches fail mid-progress during deploys.

**Fix:** Implement SIGTERM handler with configurable drain period (30s). Use Gunicorn `on_exit` hook or FastAPI lifespan events to await in-flight search completion.

**Source:** system-architecture.md H4.

---

#### P1-005: Landing Page Product Screenshot

The landing page has 6 sections (Hero, OpportunityCost, BeforeAfter, HowItWorks, Stats, CTA) but zero product visuals. B2G buyers are risk-averse and need to see what they are buying. An annotated screenshot or 30-second demo video in the hero section is the single highest-impact conversion improvement.

**Source:** frontend-spec.md P1-1.

---

#### P1-007: search_sessions.status CHECK vs State Manager

DB CHECK allows `(created, processing, completed, failed, timed_out, cancelled)` but state manager also uses `consolidating` and `partial`. If these values are written to DB, inserts/updates will fail with a constraint violation -- silently breaking search state persistence.

**Fix:** Verify app code. Either add values to CHECK or confirm the state manager maps to allowed values before DB write.

**Source:** DB-AUDIT.md M-006.

---

## P2 -- MEDIUM (90 Days)

| ID | Finding | Domain | Impact | Effort | Owner |
|----|---------|--------|--------|--------|-------|
| P2-001 | Feature flag explosion (50+ flags) | Backend | Misconfiguration risk; no admin UI for management | L (8h) | @dev |
| P2-002 | 90 migrations, mixed naming conventions | DB | Migration apply time grows; fragile sort order | M (4h) | @data-engineer |
| P2-003 | No load testing baseline | Backend/Infra | Unknown breaking point for concurrent users | L (8h) | @devops |
| P2-004 | OpenAI single point of failure for classification | Backend | OpenAI outage = all zero-match classifications become REJECT | M (4h) | @dev |
| P2-005 | Minimal next/image usage (7 files) | Frontend | No image optimization infrastructure as product adds visuals | M (4h) | @dev |
| P2-006 | No bundle analyzer configured | Frontend | Can't monitor JS payload size growth | S (2h) | @dev |
| P2-007 | Prop drilling in SearchResults (40+ props) | Frontend | Maintainability risk as search features grow | M (8h) | @dev |
| P2-008 | Missing updated_at on 8 operational tables | DB | Harder to debug data issues; no change tracking | M (4h) | @data-engineer |
| P2-009 | search_results_cache cleanup trigger fires per-insert | DB | Potential bottleneck at 50K+ rows (mitigated by short-circuit) | S (2h) | @data-engineer |
| P2-010 | ARQ worker liveness detection cached (15s) | Backend | Background jobs silently fail for up to 15s after worker crash | S (2h) | @dev |
| P2-011 | No staging environment verified | Backend/Infra | No pre-production validation environment | L (16h) | @devops |
| P2-012 | Backup recovery process undocumented | DB/Infra | Supabase PITR enabled but never tested | M (4h) | @devops |
| P2-013 | 4 analytics tools loading (GA + Clarity + Mixpanel + Sentry) | Frontend | Page weight and LGPD consent surface area | S (2h) | @dev |
| P2-014 | Annual plan not defaulted on pricing page | Frontend | Users see highest price first (monthly), reducing conversion | S (2h) | @ux-design-expert |
| P2-015 | grpcio transitive dep removal is fragile | Backend | Any dep update could re-introduce fork-unsafe grpcio | S (2h) | @devops |

---

## P3 -- LOW (Backlog)

| ID | Finding | Domain | Effort |
|----|---------|--------|--------|
| P3-001 | mypy `disallow_untyped_defs = false` | Backend | M |
| P3-002 | Debug endpoint `/debug/pncp-test` in production | Backend | S |
| P3-003 | `health.py` uses `os.popen("python --version")` | Backend | S |
| P3-004 | Local file cache TTL disk accumulation untested at scale | Backend | S |
| P3-005 | Auth cache dual-hash transition window on every deploy | Backend | S |
| P3-006 | Inconsistent DB naming conventions (indexes, policies) | DB | S |
| P3-007 | google_sheets_exports GIN index possibly unused | DB | S |
| P3-008 | CSS variable + Tailwind class mixing | Frontend | M |
| P3-009 | Landing page sections tightly coupled (inline styles) | Frontend | M |
| P3-010 | Heading hierarchy unaudited on individual pages | Frontend | S |
| P3-011 | user_subscriptions lacks explicit service_role policy | DB | S |

---

## Cross-Domain Issues

These findings span multiple areas and require coordination:

### CD-001: Billing Quota Enforcement Chain (DB + Backend)
The quota system depends on: (1) `monthly_quota` RLS + atomic RPC functions (DB), (2) `quota.py` check+increment logic with Supabase circuit breaker fallback (Backend), (3) `profiles.plan_type` as billing fallback (DB + Backend). If the Supabase circuit breaker opens, billing defaults to cached plan -- this is correct behavior but the chain has 4 failure modes that interact.

**Risk:** LOW -- well-engineered with fail-open defaults. No action needed but document the chain for ops runbook.

### CD-002: Search Pipeline Timeout vs Railway Timeout (Backend + Infra)
Pipeline timeout (110s) < Railway hard timeout (300s). However, the SSE heartbeat (15s) must beat Railway idle timeout (60s). If heartbeat fails, Railway kills the connection even though the search is still running. The backend correctly handles this with heartbeat-during-wait, but monitoring should alert when heartbeat gaps exceed 30s.

**Risk:** LOW -- already mitigated by CRIT-012. Monitor via `smartlic_sse_connection_errors_total` metric.

### CD-003: RLS Policy + Backend Auth Double-Check (DB + Backend)
Authentication is enforced at two layers: (1) RLS policies use `auth.uid()` to scope data, (2) Backend `require_auth` dependency validates JWT. If either layer fails, the other provides defense. However, the P0-001/P0-002 RLS gaps mean the backend auth layer is the ONLY protection for pipeline_items and search_results_cache.

**Risk:** HIGH until P0-001/P0-002 are fixed. After fix: LOW (defense in depth restored).

### CD-004: Search State Persistence vs Status CHECK (DB + Backend)
The backend state manager tracks search states (including `consolidating`, `partial`) that may not be in the DB CHECK constraint. If state writes fail, the search appears stuck to the user and SSE progress hangs. This affects both backend observability (state transitions not recorded) and frontend UX (stale progress indicators).

**Risk:** MEDIUM -- needs P1-007 investigation.

### CD-005: Cache Coherence Across Workers (Backend + Infra)
L1 InMemory cache is per-Gunicorn-worker. Two workers can have stale data for different users. Redis L2 compensates, but a user hitting different workers on successive requests may see cache flicker. This becomes more pronounced with horizontal scaling (P1-009).

**Risk:** LOW at current scale. MEDIUM if scaling to 2+ Railway instances.

---

## Dependency Map

```
P0-001/002 (RLS fixes)
  |
  v
P1-002 (FK standardization) -- can run in parallel with P0
  |
  v
P1-010 (retention policies) -- depends on P1-002 for mfa tables

P1-004 (graceful shutdown)
  |
  v
P1-009 (horizontal scaling) -- scaling without graceful shutdown causes more deploy failures

P1-005 (landing screenshot)
  |
  v
P2-005 (next/image infra) -- needs image optimization before adding many product visuals

P1-001 (CI gates)
  |
  v
P2-003 (load testing) -- meaningless to load test if CI doesn't block bad code

P2-011 (staging env)
  |
  v
P2-012 (backup testing) -- staging is where you test recovery
```

---

## Quick Wins (< 4 hours each, high impact)

Ordered by impact-to-effort ratio:

1. **P0-001 + P0-002: Fix 2 RLS policies** (2h) -- 10 lines of SQL. Closes the only data exposure risk. Deploy immediately.
2. **P1-001: Make pip-audit blocking in CI** (2h) -- Remove `continue-on-error: true` from one workflow file. Prevents CVEs from shipping.
3. **P1-006: Add testimonials to landing page** (2h) -- `TestimonialSection` component already exists and is used on `/planos`. Import it into the landing page.
4. **P2-014: Default pricing to annual billing** (2h) -- Change the default toggle state in `/planos/page.tsx`. Shows the lowest price first.
5. **P1-008: ComprasGov transparency** (2h) -- Add a data sources indicator showing "2/3 sources active" to set expectations. Or a one-line disclaimer in the search UI.
6. **P1-003: Verify FK validation** (1h) -- Single SQL query in production. Either confirms it is fine or reveals a quick fix.
7. **P1-010: Add 4 retention cron jobs** (2h) -- Four `SELECT cron.schedule(...)` statements. Prevents unbounded table growth.
8. **P2-006: Add bundle analyzer** (2h) -- `npm install @next/bundle-analyzer` + config. Baseline for monitoring.

---

## Questions for Specialist Review

### For @data-engineer

1. **P0-001/P0-002 verification:** Can you confirm via `SELECT polname, polroles FROM pg_policy WHERE polrelid IN ('pipeline_items'::regclass, 'search_results_cache'::regclass);` in production that these policies are indeed missing `TO service_role`? The migration code review is clear, but production state should be verified before and after the fix.

2. **P1-002 ordering:** For the auth.users -> profiles FK migration, should `organizations.owner_id` use `ON DELETE RESTRICT` (preventing account deletion while org exists) or `ON DELETE SET NULL` (orphaning the org)? The business rule is unclear -- does deleting an owner dissolve the organization?

3. **P1-007 investigation:** Can you query `search_sessions` for any rows where `status` contains values not in the CHECK constraint? If the state manager maps internally before DB writes, this is a non-issue. If it does not, we need to either add `consolidating` and `partial` to the CHECK or add a mapping layer.

4. **P1-003 production check:** Can you run the FK validation query on production Supabase and report whether `convalidated = true` for `search_results_store`?

5. **Scalability of search_state_transitions:** With no retention policy and ~5 transitions per search, this table will reach 6M rows/year at 100K searches/month. Should we add a 12-month retention cron job, or is this data valuable for long-term analytics?

6. **Migration squash:** With 86+ migrations and mixed sequential/timestamp naming, is it worth squashing to a baseline? What is the current `supabase db push` time?

### For @ux-design-expert

1. **P1-005 product screenshot:** What format would be most effective for B2G buyers -- a static annotated screenshot, an interactive carousel showing key screens, or a 30-second video walkthrough? Budget assumption: M (4-8h) for implementation.

2. **P1-011 dashboard insights:** What specific proactive recommendations would be most valuable? Options: (a) "X new opportunities since your last search," (b) "Pipeline item Y has deadline in Z days," (c) "You've analyzed R$XM in opportunities this month," (d) sector trend analysis. Which 1-2 should ship first?

3. **Trust signals depth:** The landing page has testimonials (4 users, first-name + initial format). For B2G buyers, would adding (a) company sector logos, (b) a "N+ empresas" counter, or (c) a brief case study be more effective at building trust?

4. **Annual plan default:** Defaulting pricing to annual view shows R$297/mo instead of R$397/mo. Is there a risk that users feel deceived when they discover the monthly price? Or does the anchoring effect outweigh this?

5. **Heading hierarchy audit:** The accessibility assessment flagged h1-h6 nesting as "needs review." Is this worth a dedicated audit pass, or should it be checked page-by-page as other P1 work touches each page?

---

## Sprint Planning Suggestion

### Week 1: P0 Blockers + Quick Wins (Days 1-5)

| Day | Task | Owner | Effort |
|-----|------|-------|--------|
| 1 | P0-001 + P0-002: Fix RLS policies (migration + verify) | @data-engineer | 2h |
| 1 | P1-001: Make pip-audit blocking in CI | @devops | 2h |
| 1 | P1-003: Verify FK validation in production | @data-engineer | 1h |
| 2 | P1-006: Add TestimonialSection to landing page | @dev | 2h |
| 2 | P2-014: Default pricing to annual billing | @dev | 2h |
| 2 | P1-010: Add 4 retention cron jobs | @data-engineer | 2h |
| 3 | P1-008: Add data sources transparency indicator | @dev | 2h |
| 3 | P1-007: Investigate search_sessions status CHECK | @data-engineer | 2h |
| 4-5 | P1-002: FK standardization migration (5 tables) | @data-engineer | 8h |

**Week 1 outcome:** All data exposure closed, CI hardened, quick UX wins shipped, LGPD gaps closed.

### Week 2-3: P1 High Priority (Days 6-15)

| Task | Owner | Effort |
|------|-------|--------|
| P1-004: SIGTERM graceful shutdown | @dev | 4h |
| P1-005: Landing page product screenshot/video | @ux-design-expert + @dev | 8h |
| P1-009: Horizontal scaling investigation + Redis SSE validation | @devops | 16h |
| P1-011: Dashboard actionable insights (phase 1) | @dev | 8h |

**Week 2-3 outcome:** Zero-downtime deploys, landing page conversion improved, scaling ceiling raised.

### Week 4-8: P2 Medium Priority

| Task | Owner | Effort |
|------|-------|--------|
| P2-001: Feature flag triage + categorization | @dev | 8h |
| P2-003: Load testing baseline | @devops | 8h |
| P2-004: Local model fallback for OpenAI outages | @dev | 4h |
| P2-005: next/image infrastructure | @dev | 4h |
| P2-011: Staging environment verification | @devops | 16h |
| P2-012: Backup recovery runbook + test | @devops | 4h |
| P2-002: Migration squash evaluation | @data-engineer | 4h |
| P2-007: SearchResults context provider refactor | @dev | 8h |

**Week 4-8 outcome:** Operational confidence for sustained growth. Known capacity limits. Recovery procedures documented.

---

## Appendix: Score Methodology

Each domain was assessed independently by its specialist agent. The consolidated score weights:

- **Security (30%):** 8.5/10 -- Excellent auth + RLS, minus P0-001/P0-002
- **Reliability (25%):** 8/10 -- Circuit breakers, SWR cache, graceful degradation
- **Conversion/UX (20%):** 7.5/10 -- Strong core loop, landing page needs product visuals
- **Scalability (15%):** 6.5/10 -- Single instance ceiling, per-worker cache
- **Observability (10%):** 8/10 -- 50+ Prometheus metrics, structured logging, Sentry

**Weighted score:** (8.5 * 0.30) + (8.0 * 0.25) + (7.5 * 0.20) + (6.5 * 0.15) + (8.0 * 0.10) = **7.73 ~ 7.5/10**
