# Feature Flags Reference — SmartLic Backend

Last updated: 2026-03-11

This document catalogs all feature flags in the SmartLic backend, organized by lifecycle category. It serves as the single source of truth for flag purpose, defaults, ownership, and toggle guidance.

---

## Table of Contents

- [Permanent (Operational Toggles)](#permanent-operational-toggles)
- [Experimental (Default false, actively being tested)](#experimental-default-false-actively-being-tested)
- [SHIP-002 Gates (Incomplete features, default false)](#ship-002-gates-incomplete-features-default-false)
- [Removed in DEBT-128](#removed-in-debt-128)
- [Adding New Feature Flags](#adding-new-feature-flags)

---

## Permanent (Operational Toggles)

These flags control operational behavior and should remain as toggleable configs. They are proven in production and expected to stay indefinitely.

| Flag | Default | Purpose | When to Toggle | Owner |
|------|---------|---------|----------------|-------|
| `ENABLE_NEW_PRICING` | `true` | Controls billing/quota enforcement (STORY-165) | Set `false` to disable billing (emergency) | billing |
| `LLM_ARBITER_ENABLED` | `true` | LLM classification for relevance scoring (STORY-179) | Set `false` if OpenAI API is down | ai-team |
| `LLM_ZERO_MATCH_ENABLED` | `true` | Zero-match LLM classification for 0% keyword density bids | Set `false` to reduce LLM costs | ai-team |
| `FILTER_DEBUG_MODE` | `false` | Verbose filter debug logging | Set `true` for debugging filter pipeline issues | dev |
| `WARMUP_ENABLED` | `true` | Startup cache warm-up | Set `false` if API pressure too high at boot | ops |
| `CACHE_WARMING_ENABLED` | `false` | Proactive cache warming on schedule | Set `true` when cache strategy stable | ops |
| `CACHE_REFRESH_ENABLED` | `false` | Background cache refresh for stale entries | Set `true` when ready | ops |
| `HEALTH_CANARY_ENABLED` | `true` | PNCP health canary checks | Set `false` if canary causes issues | ops |
| `METRICS_ENABLED` | `true` | Prometheus metrics collection | Set `false` if metrics cause overhead | ops |
| `DIGEST_ENABLED` | `false` | Email digests for users | Set `true` when feature ready | product |
| `ALERTS_ENABLED` | `true` | Pipeline alert emails | Set `false` to stop emails | ops |
| `ALERTS_SYSTEM_ENABLED` | `false` | Full alerts system (SHIP-002 gate) | Set `true` when alerts feature complete | product |
| `RECONCILIATION_ENABLED` | `true` | Daily billing reconciliation | Set `false` if causing issues | billing |
| `SEARCH_ASYNC_ENABLED` | varies | Async search via ARQ job queue | Controls sync vs async mode | ops |
| `USER_FEEDBACK_ENABLED` | `true` | User feedback collection | Set `false` to disable feedback | product |
| `BID_ANALYSIS_ENABLED` | `true` | Deep bid analysis with LLM | Set `false` to reduce LLM costs | ai-team |
| `TRIAL_EMAILS_ENABLED` | `true` | Automated trial lifecycle emails | Set `false` to stop trial emails | product |
| `TRIAL_PAYWALL_ENABLED` | `true` | Trial paywall after day 7 | Set `false` to remove paywall | product |
| `COMPRASGOV_ENABLED` | `false` | ComprasGov v3 data source | Set `true` when API back online | ops |
| `COMPRASGOV_CB_ENABLED` | `true` | ComprasGov circuit breaker | Set `false` to disable CB | ops |
| `USE_REDIS_CIRCUIT_BREAKER` | `true` | Redis-backed circuit breaker | Set `false` for in-memory fallback | ops |

---

## Experimental (Default false, actively being tested)

These flags gate features under active development or A/B testing. They default to `false` and should not be enabled in production without explicit validation.

| Flag | Default | Purpose |
|------|---------|---------|
| `ASYNC_ZERO_MATCH_ENABLED` | `false` | Async background zero-match via ARQ jobs |
| `TERM_SEARCH_LLM_AWARE` | `false` | LLM-aware term search quality parity |
| `TERM_SEARCH_SYNONYMS` | `false` | Synonym expansion for term search |
| `TERM_SEARCH_VIABILITY_GENERIC` | `false` | Generic viability for term search |
| `TERM_SEARCH_FILTER_CONTEXT` | `false` | Filter context for term search |

---

## SHIP-002 Gates (Incomplete features, default false)

These flags protect incomplete features that are partially built but not ready for users. They must remain `false` until the corresponding SHIP-002 work items are completed.

| Flag | Default | Purpose |
|------|---------|---------|
| `ORGANIZATIONS_ENABLED` | `false` | Multi-org support |
| `MESSAGES_ENABLED` | `false` | Messaging system |
| `PARTNERS_ENABLED` | `false` | Partner program |

---

## Removed in DEBT-128

These flags were always-on shipped features with no real conditional logic. Their code paths have been simplified by inlining the `True` branch and deleting the `False` branch.

| Flag | Was Default | Reason Removed | Commit |
|------|-------------|----------------|--------|
| `TRIAL_14_DAYS_ENABLED` | `true` | No conditional logic existed; purely decorative | DEBT-128 |
| `SYNONYM_MATCHING_ENABLED` | `true` | Not used in any conditional; real control is `TERM_SEARCH_SYNONYMS` | DEBT-128 |
| `LLM_STRUCTURED_OUTPUT_ENABLED` | `true` | Legacy binary mode dead code; structured output is standard | DEBT-128 |
| `LLM_ZERO_MATCH_BATCH_ENABLED` | `true` | Individual fallback mode unused; batch is standard | DEBT-128 |
| `VIABILITY_ASSESSMENT_ENABLED` | `true` | Always-on in pipeline; confidence-only fallback kept for simplified searches | DEBT-128 |

---

## Adding New Feature Flags

### Naming Convention

- Use `SCREAMING_SNAKE_CASE`.
- Boolean toggles: `FEATURE_NAME_ENABLED`
- Configuration values: `FEATURE_NAME_VALUE`

### Required Steps

1. Add to `config/features.py` (or appropriate config module) with env var and default.
2. Add to `_FEATURE_FLAG_REGISTRY` in `config/features.py` for runtime reload support.
3. Add to `config/__init__.py` re-exports.
4. Add description to `_FLAG_DESCRIPTIONS` in `routes/feature_flags.py`.
5. Document in this file with category, purpose, and toggle guidance.
6. Add tests covering both `True` and `False` paths.

### Lifecycle

```
EXPERIMENTAL (default false)
    |
    | proven stable in production
    v
PERMANENT (default true or false, toggleable)
    |
    | True for 30+ days with no toggles
    v
REMOVED — inline the True path, delete the False path
```

- **New flags** start as EXPERIMENTAL (default `false`).
- **Stable flags** are promoted to PERMANENT when proven in production.
- **Shipped flags** (`true` for 30+ days with no toggles) should be REMOVED: inline the `True` path and delete the `False` path.
- Review this file monthly for cleanup candidates.
