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

- [ ] AC1: Adicionar coluna `first_response_at` na tabela `conversations` (migração Supabase)
- [ ] AC2: Calcular `response_time_hours` no backend ao registrar reply do admin
- [ ] AC3: Criar cron job `check_unanswered_messages()` em `cron_jobs.py` que executa a cada 4h
- [ ] AC4: Enviar email de alerta ao admin quando mensagem sem resposta completar 20h úteis
- [ ] AC5: Criar Prometheus gauge `smartlic_support_pending_messages` e histogram `smartlic_support_response_time_hours`
- [ ] AC6: Criar endpoint `GET /v1/admin/support-sla` retornando: `{ avg_response_hours, pending_count, breached_count }`
- [ ] AC7: No admin dashboard, exibir card de SLA com métricas de resposta
- [ ] AC8: Definir "horas úteis" como seg-sex 8h-18h BRT (configurável via env var `BUSINESS_HOURS_START`, `BUSINESS_HOURS_END`)
- [ ] AC9: Testes: mock de horários úteis vs finais de semana

## Arquivos Afetados

- `supabase/migrations/` (nova migração)
- `backend/routes/messages.py`
- `backend/cron_jobs.py`
- `backend/metrics.py`
- `backend/routes/admin.py`
- `frontend/app/admin/page.tsx`

## Validação

| Métrica | Threshold | Onde medir |
|---------|-----------|------------|
| `smartlic_support_response_time_hours` p95 | <24h úteis | Admin dashboard |
| `smartlic_support_pending_messages` | <3 por vez | Prometheus |
