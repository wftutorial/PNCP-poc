# STORY-353: Infraestrutura de SLA para mensagens de suporte

**Prioridade:** P1
**Tipo:** feature
**Sprint:** Sprint 3
**Estimativa:** L
**Origem:** Conselho CTO Advisory Board — Auditoria de Promessas (2026-03-01)
**Dependências:** STORY-352 (copy já ajustado)
**Bloqueado por:** —
**Bloqueia:** —
**Paralelo com:** STORY-358, STORY-359, STORY-360

---

## Contexto

O sistema promete "Resposta em até 24 horas úteis" em múltiplos locais (comparisons.ts, ajuda/page.tsx). Não existe: alerta de mensagem sem resposta, métrica de tempo de resposta, escalação automática, nem medição de compliance.

## Promessa Afetada

> "Resposta em até 24 horas úteis"

## Causa Raiz

Promessa de SLA sem medição, alertas, ou enforcement. Sem como garantir nem verificar cumprimento.

## Critérios de Aceite

- [x] AC1: Adicionar coluna `first_response_at` na tabela `conversations` (migração Supabase)
- [x] AC2: Calcular `response_time_hours` no backend ao registrar reply do admin
- [x] AC3: Criar cron job `check_unanswered_messages()` em `cron_jobs.py` que executa a cada 4h
- [x] AC4: Enviar email de alerta ao admin quando mensagem sem resposta completar 20h úteis
- [x] AC5: Criar Prometheus gauge `smartlic_support_pending_messages` e histogram `smartlic_support_response_time_hours`
- [x] AC6: Criar endpoint `GET /v1/admin/support-sla` retornando: `{ avg_response_hours, pending_count, breached_count }`
- [x] AC7: No admin dashboard, exibir card de SLA com métricas de resposta
- [x] AC8: Definir "horas úteis" como seg-sex 8h-18h BRT (configurável via env var `BUSINESS_HOURS_START`, `BUSINESS_HOURS_END`)
- [x] AC9: Testes: mock de horários úteis vs finais de semana

## Arquivos Afetados

- `supabase/migrations/20260301400000_add_first_response_at.sql` (AC1)
- `backend/business_hours.py` (AC8 — NEW)
- `backend/config.py` (AC8 — 4 config vars)
- `backend/metrics.py` (AC5 — gauge + histogram)
- `backend/routes/messages.py` (AC2 — first_response_at tracking)
- `backend/cron_jobs.py` (AC3+AC4 — cron job + email alert)
- `backend/main.py` (startup/shutdown for SLA task)
- `backend/admin.py` (AC6 — GET /admin/support-sla endpoint)
- `frontend/app/admin/page.tsx` (AC7 — SLA card)
- `backend/tests/test_support_sla.py` (AC9 — 28 tests)
- `frontend/__tests__/admin/support-sla-card.test.tsx` (AC7 — 3 tests)
- `frontend/__tests__/pages/AdminPage.test.tsx` (updated for SLA fetch)

## Validação

| Métrica | Threshold | Onde medir |
|---------|-----------|------------|
| `smartlic_support_response_time_hours` p95 | <24h úteis | Admin dashboard |
| `smartlic_support_pending_messages` | <3 por vez | Prometheus |
