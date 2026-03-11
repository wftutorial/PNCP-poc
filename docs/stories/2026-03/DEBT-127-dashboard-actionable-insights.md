# DEBT-127: Dashboard Actionable Insights
**Priority:** P1
**Effort:** 8h
**Owner:** @dev
**Sprint:** Week 3

## Context

The current dashboard shows analytics (searches over time, top dimensions, trial value) but lacks actionable prompts that drive the user back into the product. Two specific retention levers were identified in the GTM assessment: pipeline deadline alerts ("3 editais vencem esta semana") and new opportunity notifications ("12 novas oportunidades desde sua ultima busca"). These transform the dashboard from a passive report into an active engagement surface.

## Acceptance Criteria

### Pipeline Deadline Alerts

- [x] AC1: Dashboard shows count of pipeline items with deadlines in the next 7 days
- [x] AC2: Alert card displays "X editais vencem esta semana" with a link to `/pipeline`
- [x] AC3: Items are sourced from `pipeline_items` where `deadline` is within 7 days and status is not `archived` or `won`
- [x] AC4: If no upcoming deadlines, card shows encouraging message ("Nenhum prazo urgente")
- [x] AC5: Backend endpoint `GET /v1/pipeline/alerts` returns deadline alerts (or extend existing endpoint)

### New Opportunities Since Last Search

- [x] AC6: Dashboard shows count of new opportunities since the user's last search
- [x] AC7: "X novas oportunidades desde sua ultima busca" with a CTA to `/buscar`
- [x] AC8: Count is derived from comparing latest search results against previous session
- [x] AC9: If no previous search exists, show onboarding prompt ("Faca sua primeira busca")

### General

- [x] AC10: Both insight cards are prominently positioned (top of dashboard, before charts)
- [x] AC11: Cards are visually distinct (use accent colors or icons to draw attention)
- [x] AC12: Mobile-responsive layout (cards stack vertically on mobile)

## Technical Notes

**Pipeline alerts (AC1-AC5):**
- Check if `GET /pipeline/alerts` already exists (assessment mentions it in routes)
- If not, add to `routes/pipeline.py` -- query `pipeline_items` with deadline filter
- Frontend: new `PipelineAlerts` component on dashboard page

**New opportunities (AC6-AC9):**
- Use `search_sessions` table to find user's last search timestamp
- Compare against current search results count or PNCP publication dates
- This is an approximation -- exact "new since last search" requires storing previous result IDs
- Simpler approach: "X editais publicados nos ultimos 3 dias" (uses PNCP publication dates, no per-user tracking needed)

**Dashboard page:** `frontend/app/dashboard/page.tsx`

## Test Requirements

- [x] Backend: `test_pipeline_alerts.py` -- deadline filtering, empty state, authorization
- [x] Frontend: Dashboard insight cards render with mock data
- [x] Frontend: CTA links navigate to correct pages
- [x] Existing dashboard tests pass

## Files to Modify

- `backend/routes/pipeline.py` -- Add/extend alerts endpoint
- `frontend/app/dashboard/page.tsx` -- Add insight cards section
- `frontend/app/dashboard/components/` -- New insight card components

## Definition of Done

- [x] All ACs pass
- [x] Tests pass (existing + new)
- [x] No regressions in CI
- [ ] Code reviewed
