# STORY-319: Reduzir Trial de 30 para 14 Dias

**Epic:** EPIC-TURBOCASH-2026-03
**Sprint:** Sprint 1 (Quick Wins)
**Priority:** P0 — BLOCKER
**Story Points:** 5 SP
**Estimate:** 3-4 dias
**Owner:** @dev
**Origem:** TurboCash Playbook — Acao 5 (Otimizar Trial Funnel)

---

## Problem

O trial atual de 30 dias e longo demais. Benchmark de mercado (Chargebee/ProfitWell) mostra que trials de 14 dias convertem 40-60% mais que trials de 30 dias. Licita Ja (concorrente direto) usa trial de 14 dias. O periodo estendido reduz urgencia e permite que usuarios "esqueçam" a plataforma antes de converter.

## Solution

Reduzir o trial de 30 para 14 dias com migração adequada para usuarios existentes e ajuste de toda a copy/UX que referencia "30 dias".

**Evidencia:** Trial conversion (14d vs 30d): +40-60% lift — Chargebee/ProfitWell

---

## Acceptance Criteria

### Backend — Configuracao

- [x] **AC1:** Alterar `config.py` → `TRIAL_DURATION_DAYS` default de `30` para `14`
- [x] **AC2:** Alterar `quota.py` → qualquer referencia hardcoded a 30 dias de trial (auditado: nenhuma ref hardcoded a trial duration; `max_history_days=30` e sobre historico de buscas, nao trial)
- [x] **AC3:** Alterar email templates em `backend/templates/emails/trial.py`:
  - `render_trial_midpoint_email()` — ajustar copy de "15 dias" para "7 dias"
  - `render_trial_expiring_email()` — ajustar copy de "5 dias" para "3 dias"
  - `render_trial_last_day_email()` — manter (dia 13/14)
  - `render_trial_expired_email()` — manter
- [x] **AC4:** Endpoint `GET /v1/trial-status` retorna `days_remaining` correto (baseado em 14d) — calcula dinamicamente de `trial_expires_at`, que agora e `created_at + 14d` para novos usuarios

### Backend — Migracao de Usuarios Existentes

- [x] **AC5:** Criar migration SQL que:
  - Usuarios com trial ativo e `created_at` ha mais de 14 dias → manter trial ate completar 30d (grandfather clause)
  - Usuarios com trial ativo e `created_at` ha 14 dias ou menos → aplicar novo limite de 14d
  - Novos usuarios a partir da data da migration → 14 dias
  - Log: registrar quantos usuarios foram afetados em cada grupo
- [x] **AC6:** Feature flag `TRIAL_14_DAYS_ENABLED` para rollout gradual (default: true)

### Frontend — Copy e UX

- [x] **AC7:** Atualizar `TrialCountdown.tsx` — qualquer referencia a "30 dias" (nenhuma encontrada; cores ja funcionam para 14d)
- [x] **AC8:** Atualizar `TrialExpiringBanner.tsx` — threshold de exibicao (mostrar a partir do dia 8, nao dia 24)
- [x] **AC9:** Atualizar `TrialConversionScreen.tsx` — copy "30 dias" → "14 dias" (nenhuma ref hardcoded; usa valores dinamicos)
- [x] **AC10:** Atualizar pagina `/planos` — copy de trial
- [x] **AC11:** Atualizar pagina `/signup` — copy de trial ("14 dias gratis")
- [x] **AC12:** Atualizar landing page (`/`) — qualquer referencia a "30 dias gratis"
- [x] **AC13:** Atualizar onboarding — copy de trial (nenhuma ref a "30 dias" encontrada no onboarding)

### Testes

- [x] **AC14:** Testes backend: trial expira em 14d (nao 30d)
- [x] **AC15:** Testes backend: grandfather clause para usuarios existentes
- [x] **AC16:** Testes frontend: componentes exibem "14 dias"
- [x] **AC17:** Zero regressions

---

## Infraestrutura Existente

| Componente | Arquivo | Status |
|-----------|---------|--------|
| Trial duration config | `backend/config.py:381` | Existe (30d) |
| Trial status endpoint | `backend/routes/user.py` → GET /trial-status | Existe |
| Trial countdown | `frontend/app/components/TrialCountdown.tsx` | Existe |
| Trial expiring banner | `frontend/app/components/TrialExpiringBanner.tsx` | Existe |
| Trial conversion screen | `frontend/app/components/TrialConversionScreen.tsx` | Existe |
| Plan capabilities | `backend/quota.py:93-102` | Existe |
| Email templates | `backend/templates/emails/trial.py` | Existe |

## Files Esperados (Output)

**Modificados:**
- `backend/config.py` — TRIAL_DURATION_DAYS 30→14 + TRIAL_14_DAYS_ENABLED flag
- `backend/templates/emails/trial.py` — all email copy adjusted for 14-day trial
- `backend/services/trial_email_sequence.py` — schedule: days 0,3,5,7,10,11,13,16 (was 0,3,7,14,21,25,29,32)
- `frontend/app/components/TrialExpiringBanner.tsx` — threshold: show from day 8 (daysRemaining <= 6)
- `frontend/app/planos/page.tsx` — FAQ copy
- `frontend/app/planos/layout.tsx` — meta description
- `frontend/app/signup/layout.tsx` — meta description
- `frontend/app/components/landing/FinalCTA.tsx` — CTA copy
- `frontend/app/components/InstitutionalSidebar.tsx` — signup benefits
- `frontend/lib/copy/valueProps.ts` — guarantee copy
- `frontend/app/features/page.tsx` — CTA copy
- `frontend/app/sobre/page.tsx` — CTA copy
- `frontend/app/ajuda/page.tsx` — FAQ answers
- `frontend/app/ajuda/FaqStructuredData.tsx` — structured data
- `frontend/app/termos/page.tsx` — account types
- `frontend/app/admin/emails/page.tsx` — admin title
- `frontend/e2e-tests/institutional-pages.spec.ts` — e2e test assertions
- `frontend/__tests__/components/InstitutionalSidebar.test.tsx` — test assertions
- `frontend/__tests__/ux-359-mobile-signup-scroll.test.tsx` — test assertions
- `frontend/__tests__/trial-components.test.tsx` — threshold test
- `backend/tests/test_trial_email_sequence.py` — email copy/schedule assertions

**Novos:**
- `supabase/migrations/20260228170000_trial_14_days.sql` — grandfather clause migration
- `backend/tests/test_trial_14_days.py` — 21 tests (AC14/AC15)
- `frontend/__tests__/story-319-trial-14-days.test.tsx` — 13 tests (AC16)

## Dependencias

- Nenhuma bloqueadora
- STORY-321 (email sequence) depende desta story

## Riscos

- Usuarios existentes com trial de 30d podem reclamar se cortarmos → grandfather clause (AC5)
- Copy hardcoded em locais inesperados → search completo por "30 dias", "30 days", "30d"
- A/B testing futuro: manter feature flag para reverter se conversao cair
