# Database Specialist Review

**Reviewer:** @data-engineer (Delta)
**Date:** 2026-03-21
**Input:** docs/prd/technical-debt-DRAFT.md (Brownfield Discovery Phase 5)
**Reference:** supabase/docs/DB-AUDIT.md, supabase/docs/SCHEMA.md, backend source code
**Supersedes:** db-specialist-review.md v2.0 (2026-03-20)

---

## Debitos Validados

| ID | Debito | Severidade Original | Severidade Ajustada | Horas | Complexidade | Notas |
|----|--------|---------------------|---------------------|-------|--------------|-------|
| DEBT-DB-001 | Dual subscription_status tracking (profiles vs user_subscriptions) | HIGH | **HIGH** (confirmed) | 3-4h | Medium | Real problem. `profiles.subscription_status` uses "canceling"/"trial" while `user_subscriptions` uses "canceled"/"trialing". No sync trigger since migration 030 removed it. `quota.py` reads from `profiles.plan_type` (not subscription_status) for gating decisions, but the drift still risks stale billing UI states. |
| DEBT-DB-002 | classification_feedback FK references auth.users on fresh install | HIGH | **HIGH** (confirmed) | 1h | Simple | Verified: DEBT-002 bridge migration CREATE TABLE has `REFERENCES auth.users(id)`. DEBT-113 fixes at runtime but is fragile. A single idempotent migration that unconditionally rewrites the FK is the correct fix. |
| DEBT-DB-003 | profiles table 20+ columns (wide table) | MEDIUM | **LOW** (downgraded) | 8-12h | Complex | At <1K users this is a non-issue. The `select("*")` pattern on profiles appears in ~8 backend call sites but all are single-row lookups by PK (index scan). No measurable perf impact. Splitting billing/marketing columns creates migration complexity and breaks 15+ backend modules. Defer to post-10K users. |
| DEBT-DB-004 | pipeline_items.search_id TEXT vs search_sessions.search_id UUID | MEDIUM | **MEDIUM** (confirmed) | 1-2h | Simple | Confirmed: `pipeline_items.search_id` is TEXT (DEBT-120), `search_sessions.search_id` is UUID. No FK possible. The TEXT type was intentional (may hold non-UUID values from PCP source), but this should be documented or enforced with a CHECK constraint for UUID format. |
| DEBT-DB-005 | user_subscriptions active index missing created_at for ORDER BY | MEDIUM | **LOW** (downgraded) | 0.5h | Simple | Confirmed pattern in billing.py: `ORDER BY created_at DESC LIMIT 1`. But with <1K users and typically 1-2 active subs per user, the sort-after-index-scan is sub-millisecond. The index improvement is correct but priority is negligible until 10K+ subscriptions. |
| DEBT-DB-006 | trial_email_log RLS enabled but no explicit policies | MEDIUM | **MEDIUM** (confirmed) | 0.5h | Simple | Confirmed: table has RLS ON but zero policies. Backend uses service_role (bypasses RLS) so no functional bug. But violates the project convention and could silently return empty results if any authenticated-role query touches this table. Quick fix, worth doing for consistency. |
| DEBT-DB-007 | handle_new_user() TOCTOU race on phone uniqueness | MEDIUM | **LOW** (downgraded) | 1h | Simple | The UNIQUE partial index `idx_profiles_phone_whatsapp_unique` is the real guard. The COUNT(*) check in the trigger is defense-in-depth. The TOCTOU race outcome is a constraint violation error (not data corruption). The only improvement is better error messaging. Low priority. |
| DEBT-DB-008 | 85 migrations with 7 handle_new_user redefinitions | MEDIUM | **MEDIUM** (confirmed) | 4-6h | Medium | Real problem for disaster recovery. Fresh replay is risky. A squash baseline is the right approach. Recommend CI validation (see below). |
| DEBT-DB-009 | Stripe price IDs hardcoded in 4 migrations | MEDIUM | **MEDIUM** (confirmed) | 3-4h | Medium | Verified: migrations 015, 029, 20260226120000, 20260301300000 contain production Stripe price IDs. The `plan_billing_periods` table is already the source of truth at runtime, so the migration values only matter on fresh install. The fix is to seed from env vars in a deployment script. |
| DEBT-DB-010 | JSONB columns without size governance | MEDIUM | **MEDIUM** (confirmed) | 2h | Simple | Confirmed: `stripe_webhook_events.payload`, `audit_events.details`, `alerts.filters`, `search_sessions.resumo_executivo` have no size constraints. The highest risk is `stripe_webhook_events.payload` -- Stripe events can be large (especially `invoice.payment_succeeded` with line items). Backend validation is primary defense but DB CHECK provides defense-in-depth. |
| DEBT-DB-011 | search_sessions 24 columns (wide table) | LOW | **LOW** (confirmed) | 16+h | Complex | Confirmed wide but acceptable. The `sessions.py` route does `select("*", count="exact")` which pulls all 24 columns for the history page. This is the only `SELECT *` on search_sessions in production routes; analytics routes use column projections. At current volume (<50K rows), this is not a problem. Deferring is correct. |
| DEBT-DB-012 | organizations.plan_type CHECK overly permissive | LOW | **LOW** (confirmed) | 0.5h | Simple | Feature not active in production. Fix when organizations feature ships. |
| DEBT-DB-013 | reconciliation_log no pg_cron retention | LOW | **LOW** (confirmed) | 0.5h | Simple | ~30 rows/month. Would take 3+ years to reach 1K rows. Negligible. |
| DEBT-DB-014 | backend/migrations/ directory redundant | LOW | **LOW** (confirmed) | 0.5h | Simple | Add a README.md or delete. Trivial. |
| DEBT-DB-015 | Legacy plans ON DELETE RESTRICT | LOW | **LOW** (confirmed) | 0.5h | Simple | Intentional design. The `is_active = false` filter works. No change needed. |
| DEBT-DB-016 | No CHECK on search_sessions.error_code | LOW | **LOW** (confirmed) | 1h | Simple | Confirmed: error_code accepts freeform text. Backend `SearchErrorCode` enum has 7 values. Adding a CHECK is good hygiene but low urgency. |
| DEBT-DB-017 | pg_cron scheduling collision at 4:00 UTC | LOW | **LOW** (confirmed) | 0.5h | Simple | Negligible at current volume. Two DELETEs on different tables at 4:00 UTC is not meaningful contention. |

---

## Debitos Removidos

| ID | Razao da Remocao |
|----|------------------|
| (none) | All 17 DEBT-DB items from the DRAFT are validated as real issues, though 3 were downgraded in severity. No items are false positives. |

---

## Debitos Adicionados

| ID | Debito | Severidade | Horas | Impacto | Justificativa |
|----|--------|-----------|-------|---------|---------------|
| DEBT-DB-018 | **Account deletion cascade misses tables.** `routes/user.py` delete_account() manually deletes from 5 tables (search_sessions, monthly_quota, user_subscriptions, user_oauth_tokens, messages) + profiles, then auth user. But it misses: `pipeline_items`, `conversations`, `classification_feedback`, `alerts`, `alert_preferences`, `search_results_cache`, `search_results_store`, `search_state_transitions`, `google_sheets_exports`, `audit_events`, `trial_email_log`. These rely on `ON DELETE CASCADE` from profiles FK, which fires when profiles row is deleted. **However**, the code deletes profiles BEFORE auth user, and deletes from individual tables BEFORE profiles. If the profiles delete succeeds but auth delete fails, orphan rows remain in auth.users. If profiles delete fails after partial table deletes, data is inconsistent. The entire operation lacks transaction wrapping. | HIGH | 3h | **Data integrity risk.** Non-transactional multi-table deletion can leave partially deleted accounts. The CASCADE from profiles FK handles most cases, but the manual per-table deletion before profiles delete is redundant AND potentially error-prone (partial failure mid-loop raises 500 and stops, leaving partial state). Fix: delete profiles row (CASCADE handles children), THEN delete auth user. Only manually delete user_subscriptions (to cancel Stripe first) and messages (non-FK path via conversations). |
| DEBT-DB-019 | **`select("*")` on search_sessions in sessions.py.** The `/sessions` endpoint fetches all 24 columns when users only need ~10 for the history UI (id, search_id, sectors, ufs, data_inicial, data_final, total_filtered, valor_total, status, created_at, resumo_executivo). The `resumo_executivo` TEXT column can be several KB of LLM output per row, and this is fetched for every row in the paginated list. | LOW | 1h | **Performance (future).** At current scale this is fine. When search_sessions passes 100K rows, the extra column bandwidth on paginated list queries will matter. Column projection is a 15-minute fix. |
| DEBT-DB-020 | **No index on `search_sessions(user_id, created_at DESC)` composite.** The most common query pattern across analytics.py and sessions.py is `WHERE user_id = X ORDER BY created_at DESC`. There is an individual index on user_id but the ORDER BY requires a sort step. | MEDIUM | 0.5h | **Performance.** This is the single most frequently executed query pattern in the application (every search history load, every analytics call). A composite index eliminates the sort step. Quick win. |
| DEBT-DB-021 | **`select("*")` on profiles in 8+ call sites.** `supabase_client.py` (lines 448, 451), `routes/user.py` (line 601), `routes/export_sheets.py`, `oauth.py`, and others all do `select("*")` on profiles when they typically need only 2-3 columns (plan_type, email, full_name). With 20+ columns, this transfers unnecessary data on every auth-gated request. | LOW | 2h | **Performance (future).** Each profiles `select("*")` pulls ~20 columns when callers need 2-3. Negligible now but becomes a pattern problem as more columns are added. Fix by creating query-specific projections: `select("id, plan_type, is_admin")` for auth, `select("id, email, full_name, company")` for user display, etc. |
| DEBT-DB-022 | **`quota.py` last-resort upsert fallback is not truly atomic.** Lines 567-579: when both RPC functions fail, the code does an upsert with `searches_count: 1` followed by a separate `get_monthly_quota_used()` read. The upsert always sets count to 1 on INSERT (correct) but on conflict does nothing useful -- it updates `updated_at` but does not increment. The subsequent read returns the current count, not the incremented count. Under concurrent requests with both RPCs unavailable, quota counting is unreliable. | MEDIUM | 2h | **Data integrity.** The two RPC functions are the real guards and work correctly. This last-resort path only activates when PostgreSQL functions are unavailable (fresh install without migrations). But the code is misleading -- it logs "incremented" but may not have incremented. Fix: make the upsert use raw SQL `ON CONFLICT DO UPDATE SET searches_count = monthly_quota.searches_count + 1` via a third RPC, or remove the misleading log. |

---

## Respostas ao Architect

### Question 1: DEBT-DB-001 (subscription status) -- Unify, sync trigger, or deprecate profiles.subscription_status?

**Recommendation: Option (c) with a migration path.**

Designate `user_subscriptions.subscription_status` as the canonical source for Stripe-originated state. However, do NOT remove `profiles.subscription_status` immediately -- it serves as a fast-read cache for the quota system.

Concrete plan:
1. **Unify enum values** (2h): Migrate `profiles.subscription_status` to use the same values as `user_subscriptions` ("trialing" not "trial", "canceled" not "canceling"). This requires a one-time UPDATE + ALTER CHECK.
2. **Add a sync trigger** (1h): ON UPDATE of `user_subscriptions.subscription_status`, propagate to `profiles.subscription_status`. This is lighter than removing the column (which touches quota.py, auth.py, and 5+ test files).
3. **Document**: `user_subscriptions` is source of truth. `profiles.subscription_status` is a denormalized cache, kept in sync by trigger. `profiles.plan_type` remains the primary field for quota gating (different purpose -- plan identity vs subscription lifecycle).

Why not pure option (c): `quota.py:check_quota()` reads `profiles.plan_type` (not subscription_status), so the quota system is already independent of subscription_status. But the frontend `/conta` page reads `profiles.subscription_status` directly for display. Removing it requires a join to user_subscriptions, which is feasible but adds a query hop to every account page load.

### Question 2: DEBT-DB-003 (profiles wide table) -- Extract now or defer?

**Defer.** At <1K users with all queries being PK lookups, there is zero measurable slowness today. I queried the actual patterns:
- `supabase_client.py` does `select("*").eq("id", uid)` -- single row by PK, <1ms regardless of column count.
- `routes/user.py` does the same for profile display.
- `quota.py` reads `profiles.plan_type` specifically (not `select("*")`).

The 8-12h effort would touch 15+ backend files and require migration + data backfill. The ROI is negative at current scale. **Revisit at 10K users or when profiles exceeds 30 columns.**

However, I DO recommend adding column projections to the most frequent call sites (DEBT-DB-021 above) as a lightweight optimization that takes 2h and prevents the wide-table problem from worsening.

### Question 3: DEBT-DB-008 (migration squash) -- Stale squash risk? CI validation?

**Yes, the squash will become stale.** But that is acceptable because it serves two purposes:
1. **Disaster recovery baseline** -- if we ever need to recreate the DB from scratch, the squash gives a known-good starting point.
2. **Developer onboarding** -- reading 1 file vs 85.

**CI validation approach (recommended):**
Add a GitHub Action that:
1. Spins up a clean PostgreSQL 17 container.
2. Applies `000_squashed_baseline.sql`.
3. Applies all migrations after the squash timestamp.
4. Runs `pg_dump --schema-only` and diffs against current production schema (obtained via `supabase db pull`).
5. Fails if diff is non-empty.

This runs weekly (not on every PR) to catch drift. Estimated effort: 3h for the CI job, included in the 4-6h total.

### Question 4: DEBT-DB-009 (Stripe price IDs) -- Staging Stripe account?

**Current staging workflow: there is none.** The project runs directly against production Supabase and production Stripe. This is a known gap.

Recommendation:
1. Create a Stripe test mode configuration (Stripe already provides test/live toggle -- no separate account needed). Generate test price IDs.
2. Modify the seed migrations to use `COALESCE(current_setting('app.stripe_price_monthly', true), 'price_test_default')` pattern, reading from PostgreSQL session variables set at migration time.
3. Alternatively (simpler): move all Stripe price ID seeding to a `scripts/seed_stripe_prices.py` that reads from env vars. Remove the INSERT statements from migrations entirely. The `plan_billing_periods` table exists -- seed it at deploy time, not migration time.

**Option 3 is fastest** (2h) and cleanest. Migrations should define schema, not data that varies by environment.

### Question 5: DEBT-DB-010 (JSONB limits) -- Measure before setting limits?

**Yes, measure first.** But I can give educated estimates:

- `stripe_webhook_events.payload`: Stripe events range from 2KB (customer.created) to 50KB (invoice.finalized with line items). A 256KB limit is safe with 5x headroom. **No existing payloads would violate this.**
- `audit_events.details`: Our audit logger (audit.py) constructs details dicts in-code with ~5 fields each. Max realistic size is ~2KB. A 64KB limit is extremely generous.
- `alerts.filters`: Schema is `{setor, ufs[], valor_min, valor_max, keywords[]}`. Max realistic size is ~1KB. 16KB limit is fine.
- `search_sessions.resumo_executivo`: LLM output with `max_summary_tokens=10000`. At ~4 chars/token, max is ~40KB. A 50KB limit with 25% headroom is safe.

**Recommendation:** Apply the CHECK constraints as documented in the audit. If any existing row violates (unlikely), the migration will fail cleanly and we adjust. Add `NOT VALID` to the CHECK for zero-downtime application on large tables (PostgreSQL validates new rows only, then `VALIDATE CONSTRAINT` in a follow-up).

---

## Dependencias Tecnicas

```
DEBT-DB-001 (subscription status enum unification)
  --> Must complete BEFORE DEBT-DB-008 (migration squash)
  --> Informational dependency on DEBT-SYS-007 (Stripe webhook -- writes subscription_status)
  --> Informational dependency on DEBT-SYS-009 (quota.py -- reads plan_type, not subscription_status)

DEBT-DB-002 (classification_feedback FK fix)
  --> Must complete BEFORE DEBT-DB-008 (migration squash)
  --> Independent of all other items

DEBT-DB-004 (pipeline_items.search_id type)
  --> Independent (no blockers, no dependents)

DEBT-DB-008 (migration squash)
  --> BLOCKED BY: DEBT-DB-001, DEBT-DB-002, DEBT-DB-009
  --> Should be the LAST database debt item resolved (captures clean state)

DEBT-DB-009 (Stripe price IDs in migrations)
  --> Must complete BEFORE DEBT-DB-008 (migration squash)
  --> Requires decision on staging environment

DEBT-DB-018 (account deletion cascade)
  --> Independent but should be reviewed alongside DEBT-SYS-007 (Stripe webhook)
  --> Benefits from DEBT-DB-001 (clean subscription state before deletion)

DEBT-DB-020 (search_sessions composite index)
  --> Independent (pure DDL, no code changes)

DEBT-DB-022 (quota upsert fallback)
  --> Independent but touches same module as DEBT-SYS-009 (quota.py split)
  --> Recommend fixing BEFORE the quota.py restructuring (fix the bug, then refactor)
```

**Execution order (critical path):**
```
DEBT-DB-002 (1h) --> DEBT-DB-001 (3h) --> DEBT-DB-009 (3h) --> DEBT-DB-008 (5h)
                                                                     ^
                                                                     |
All other items are independent and can run in parallel ──────────────┘
```

---

## Recomendacoes de Prioridade

### Sprint Imediato (esta semana)

| Rank | ID | Debito | Horas | Justificativa |
|------|----|--------|-------|---------------|
| 1 | DEBT-DB-018 | Account deletion non-transactional cascade | 3h | **Data integrity.** Partial account deletion leaves ghost data. Fix is straightforward: restructure to use CASCADE, wrap Stripe cancel + profiles delete in try/finally. |
| 2 | DEBT-DB-002 | classification_feedback FK to auth.users | 1h | **Disaster recovery.** Single migration, zero risk, blocks the squash. |
| 3 | DEBT-DB-020 | search_sessions composite index (user_id, created_at DESC) | 0.5h | **Performance quick win.** Most-executed query pattern. Single CREATE INDEX CONCURRENTLY. |
| 4 | DEBT-DB-006 | trial_email_log missing RLS policy | 0.5h | **Security consistency.** 5-minute migration. |
| 5 | DEBT-DB-001 | Dual subscription_status enum unification | 3h | **Data integrity.** Enum mismatch is a ticking bomb for billing bugs. |

**Sprint total: ~8h**

### Proximo Sprint

| Rank | ID | Debito | Horas | Justificativa |
|------|----|--------|-------|---------------|
| 6 | DEBT-DB-010 | JSONB size constraints | 2h | Defense-in-depth for unbounded columns. |
| 7 | DEBT-DB-009 | Stripe price IDs in migrations | 3h | Blocks squash. Requires staging env decision. |
| 8 | DEBT-DB-022 | quota.py upsert fallback not atomic | 2h | Misleading code path, low-frequency but real bug. |
| 9 | DEBT-DB-004 | pipeline_items.search_id TEXT vs UUID | 1h | Document or enforce with CHECK. |
| 10 | DEBT-DB-019 | select("*") on search_sessions in sessions.py | 1h | Column projection, easy win. |

**Sprint total: ~9h**

### Backlog

| ID | Debito | Horas | Justificativa |
|----|--------|-------|---------------|
| DEBT-DB-008 | Migration squash baseline | 5h | Wait until DB-001, DB-002, DB-009 are done. Then squash captures clean state. |
| DEBT-DB-021 | select("*") on profiles in 8+ sites | 2h | Low urgency, good hygiene. |
| DEBT-DB-016 | No CHECK on error_code | 1h | Nice to have. |
| DEBT-DB-017 | pg_cron collision at 4:00 UTC | 0.5h | Trivial, negligible impact. |
| DEBT-DB-013 | reconciliation_log retention | 0.5h | 30 rows/month, years from mattering. |
| DEBT-DB-014 | backend/migrations/ redundant directory | 0.5h | Add README or delete. |
| DEBT-DB-015 | Legacy plans ON DELETE RESTRICT | 0.5h | Working as designed. |
| DEBT-DB-012 | organizations.plan_type CHECK | 0.5h | Fix when feature ships. |
| DEBT-DB-003 | profiles wide table extraction | 10h | Defer to post-10K users. |
| DEBT-DB-011 | search_sessions 24 columns | 16h | Defer to post-1M rows. |
| DEBT-DB-005 | user_subscriptions index optimization | 0.5h | Defer to post-10K subscriptions. |
| DEBT-DB-007 | handle_new_user TOCTOU race | 1h | UNIQUE index is the real guard. |

---

## Metricas de Validacao

- Items confirmados sem ajuste: **12/17**
- Items com severidade ajustada: **3** (DB-003 MEDIUM->LOW, DB-005 MEDIUM->LOW, DB-007 MEDIUM->LOW)
- Items removidos: **0**
- Items adicionados: **5** (DB-018 through DB-022)
- **Total de items revisados: 22** (17 original + 5 novos)
- **Esforco total revisado: ~56h** (was ~43h for original 17 items, now ~56h with 5 new items)
- **Esforco sprint imediato: ~8h** (5 items, highest ROI)
- **Quick wins (< 1h): 7 items** totaling ~4.5h

---

## Notas Finais

### O que o architect acertou
The DRAFT accurately captures the core database debt. The severity assignments were mostly correct, and the dependency chain analysis (Section 6) correctly identifies that DB-001, DB-002, and DB-009 must precede DB-008 (squash).

### O que o architect subestimou
1. **Account deletion safety (DEBT-DB-018)** -- this is the most significant missing item. Non-transactional multi-table deletion with partial failure handling is a data integrity risk that should be HIGH priority.
2. **Query pattern inefficiencies (DEBT-DB-019, DB-020, DB-021)** -- not critical now but establish bad patterns that compound as data grows.

### O que o architect superestimou
1. **profiles wide table (DEBT-DB-003)** -- at <1K users with PK lookups, extracting columns into separate tables is negative ROI.
2. **user_subscriptions index (DEBT-DB-005)** -- sub-millisecond sort on <100 rows is not worth optimizing now.
3. **handle_new_user TOCTOU (DEBT-DB-007)** -- the UNIQUE index is the real guard; the trigger check is redundant defense.
