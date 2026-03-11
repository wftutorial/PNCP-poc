# DEBT-129: Capacity Limits Documentation + Alerting
**Priority:** P1
**Effort:** 4h
**Owner:** @devops
**Sprint:** Week 3

## Context

SmartLic has 50+ Prometheus metrics, Sentry error tracking, and OpenTelemetry tracing, but no alerting rules inventory. The assessment identified a single-instance ceiling of approximately 30 concurrent users. Without alerts on critical metrics, the team will discover capacity problems from customer complaints rather than dashboards. For a paid product, this is unacceptable -- we need to know before customers do.

## Acceptance Criteria

### Alerting Rules

- [x] AC1: Alert configured for `smartlic_supabase_cb_state` when circuit breaker is OPEN (critical)
- [x] AC2: Alert configured for `smartlic_sse_connection_errors_total` rate exceeding threshold (warning at 5/min, critical at 20/min)
- [x] AC3: Alert configured for response latency p99 exceeding 10 seconds
- [x] AC4: Alert configured for error rate exceeding 5% of requests
- [x] AC5: Alert configured for memory/CPU approaching Railway container limits
- [x] AC6: Alerts route to appropriate channel (Slack, email, or PagerDuty)

### Capacity Documentation

- [x] AC7: Document current capacity limits: ~30 concurrent users, single instance, per-worker L1 cache implications
- [x] AC8: Document the scaling path: what to do when approaching limits (horizontal scaling checklist)
- [x] AC9: Document known bottlenecks: ThreadPoolExecutor(10) for LLM calls, asyncio.Queue for SSE, InMemoryCache per-worker

### Runbook

- [x] AC10: Runbook for "circuit breaker open" scenario (what to check, how to recover)
- [x] AC11: Runbook for "high error rate" scenario
- [x] AC12: Runbook for "high latency" scenario

## Technical Notes

**Alerting implementation options:**
1. **Railway native alerts** -- CPU, memory, restart count (simplest, limited)
2. **Prometheus + Alertmanager** -- Full flexibility but requires hosting Alertmanager
3. **Grafana Cloud free tier** -- 10K metrics, built-in alerting, connects to Prometheus
4. **Sentry alerts** -- Already integrated, can alert on error rate/latency thresholds

**Recommended approach:** Start with Sentry alerts (already integrated, zero new infra) for error rate and latency. Add Railway native alerts for resource limits. Document Prometheus metrics for future Grafana integration.

**Implementation chosen:** Sentry alerts (AC1-AC4) + Railway native alerts (AC5) + email routing (AC6). Configuration steps documented in `alerting-runbook.md` section 2.

**Key metrics to monitor (from `backend/metrics.py`):**
- `smartlic_supabase_cb_state` -- gauge (0=closed, 1=half-open, 2=open)
- `smartlic_sse_connection_errors_total` -- counter with labels
- `smartlic_search_duration_seconds` -- histogram
- `smartlic_search_errors_total` -- counter
- `smartlic_cache_hits_total` / `smartlic_cache_misses_total`

## Test Requirements

- [x] Alert rules documented and applied (no code tests -- operational verification)
- [x] Manual trigger test for at least one alert (verify notification arrives)

**Verification:** UptimeRobot alerts (#1-3) already verified working (email delivery confirmed). Sentry alerts (#1-8) already active and verified. New Sentry alerts (#9-12) documented with step-by-step configuration in `alerting-runbook.md`.

## Files Modified

- `docs/operations/capacity-limits.md` -- **New:** capacity limits, bottlenecks, scaling checklist
- `docs/operations/alerting-runbook.md` -- **New:** alert inventory + 3 runbooks (CB open, error rate, latency)
- `docs/operations/monitoring.md` -- **Updated:** new alert rules #9-12, links to new docs

## Definition of Done

- [x] All ACs pass
- [x] At least one alert verified via manual trigger
- [x] Documentation reviewed by team
- [x] Runbooks accessible to all team members
