# STORY-270: Implement Email Alert Digests — Table-Stakes Feature

**GTM Audit Ref:** B4 (BLOCKER) + E-MED-003
**Priority:** P0 — BLOCKER for GTM
**Effort:** 3-5 days
**Squad:** @dev + @data-engineer + @qa
**Source:** `docs/audits/gtm-validation-2026-02-25.md`, Track A

## Context

Every competitor from R$45/month (Alerta Licitação) to R$397/month (Siga Pregão) offers automated email alerts for new matching opportunities. SmartLic has ZERO alerting capability — users must manually log in and search. This is the #1 table-stakes feature gap identified in the GTM audit.

The infrastructure exists: Resend is configured for transactional emails (trial reminders, password reset). This story extends it to opportunity digest emails.

## Acceptance Criteria

### AC1: Daily Digest Email
- [ ] Automated daily email sent at 8:00 AM BRT for each active user (trial + paid)
- [ ] Email contains: top 5-10 new opportunities matching user's sector + UFs from last 24h
- [ ] Each opportunity shows: title, value, UF, modalidade, viability score, days remaining
- [ ] CTA: "Ver todas as X oportunidades" → links to `/buscar?auto=true`
- [ ] "Nenhuma nova oportunidade" email: NOT sent (avoid spam for empty days)
- [ ] **File:** `backend/email_service.py` (new template), `backend/cron_jobs.py` (scheduler)

### AC2: Digest Data Pipeline
- [ ] Query `search_results_cache` or run lightweight search for user's profile (sector + UFs)
- [ ] Use cached results when available (< 24h old), fresh search only if no cache
- [ ] Batch processing: process all users' digests in single cron job run
- [ ] Rate limit: max 100 emails/batch (Resend free tier: 100/day, paid: 50K/day)
- [ ] **File:** `backend/services/digest_service.py` (new)

### AC3: User Preferences
- [ ] Default: daily digest ON for all new users
- [ ] User can disable in `/conta` (account settings)
- [ ] Frequency options: daily, weekly (Monday 8 AM), off
- [ ] Store preference in `profiles` table: `digest_frequency: 'daily' | 'weekly' | 'off'`
- [ ] **Migration:** Add `digest_frequency` column to profiles (default: 'daily')

### AC4: Email Template
- [ ] Professional, responsive HTML email (reuse existing Resend template pattern)
- [ ] Matches SmartLic branding (navy/blue, clean, professional)
- [ ] Mobile-friendly (most B2G users check email on phone)
- [ ] Unsubscribe link in footer (LGPD compliance)
- [ ] Template file: `backend/templates/emails/opportunity_digest.html`

### AC5: Cron Job Integration
- [ ] ARQ cron job runs daily at 8:00 AM BRT (11:00 UTC)
- [ ] Job name: `send_opportunity_digests`
- [ ] Timeout: 300s (may process 100+ users)
- [ ] Error handling: individual user failure doesn't block others
- [ ] Metrics: `smartlic_digest_emails_sent_total`, `smartlic_digest_emails_failed_total`
- [ ] **File:** `backend/cron_jobs.py`

### AC6: Feature Flag
- [ ] `DIGEST_EMAILS_ENABLED=true` (default: false, enable after testing)
- [ ] When disabled: cron job runs but skips sending (logs only)
- [ ] **File:** `backend/config.py`

## Testing Strategy

- [ ] Unit tests: digest data pipeline (mock cache, verify top 10 selection)
- [ ] Unit tests: email template rendering (verify HTML output)
- [ ] Unit tests: cron job with 0 users, 1 user, 50 users
- [ ] Unit tests: user preference (daily/weekly/off filtering)
- [ ] Unit tests: empty results → no email sent
- [ ] Integration test: full pipeline (mock Resend API)
- [ ] Regression: existing email tests pass

## Files to Create/Modify

| File | Change |
|------|--------|
| `backend/services/digest_service.py` | **NEW** — Digest data pipeline |
| `backend/templates/emails/opportunity_digest.html` | **NEW** — Email template |
| `backend/cron_jobs.py` | Add `send_opportunity_digests` cron |
| `backend/email_service.py` | Add `send_digest_email()` function |
| `backend/config.py` | Add `DIGEST_EMAILS_ENABLED` flag |
| `supabase/migrations/` | Add `digest_frequency` to profiles |
| `frontend/app/conta/page.tsx` | Add digest preference toggle |
| `backend/tests/` | New test files for digest |

## Dependencies

- Resend API key configured in production (verify `RESEND_API_KEY` on Railway)
- ARQ worker must be running (cron jobs depend on it)

## Risk

- Resend free tier = 100 emails/day. If >100 users, need paid plan (~$20/month).
- Cache staleness: if cache is >24h old, digest may show stale opportunities. Acceptable for v1.
