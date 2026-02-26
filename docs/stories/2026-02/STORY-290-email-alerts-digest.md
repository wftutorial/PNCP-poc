# STORY-290: Email Alerts & Digest Notifications

**Priority:** P1 (Table-Stakes Feature)
**Effort:** L (3-5 days)
**Squad:** @dev + @architect
**Fundamentacao:** GTM Readiness Audit — feature gap analysis. Email alerts e a feature mais basica do mercado (Alerta Licitacao cobra R$45/mes so por isso).
**Status:** TODO
**Sprint:** GTM Sprint 3 (Feature Parity)
**Depende de:** STORY-270 (Email Digest — aprovada mas nao iniciada)

---

## Contexto

Todos os concorrentes oferecem algum tipo de alerta:
- Alerta Licitacao (R$45/mo): email alerts
- ConLicitacao (R$149/mo): email alerts
- Siga Pregao (R$397/mo): email + WhatsApp

SmartLic nao tem nenhum tipo de alerta. Usuarios precisam entrar na plataforma manualmente para ver novas oportunidades. Isso e inaceitavel para GTM.

---

## Acceptance Criteria

### AC1: Alert preferences UI
- [ ] Secao em `/conta`: "Configuracoes de Alerta"
- [ ] Toggle: email alerts ligado/desligado (default: ligado para novos usuarios)
- [ ] Frequencia: diario, semanal, ou ambos
- [ ] Horario preferido: manha (8h), tarde (14h), noite (20h)
- [ ] Setores para alertar (usa profile context existente)
- [ ] UFs para alertar (usa profile context existente)
- [ ] Minimo valor para alertar (opcional)
- [ ] Salvar em `profiles.alert_preferences` (JSONB)

### AC2: Daily digest cron job
- [ ] Cron job roda no horario configurado do usuario (agrupa por horario)
- [ ] Para cada usuario com alerts ativos:
  - Busca novas licitacoes das ultimas 24h nos setores/UFs do usuario
  - Aplica filtro de keywords do setor
  - Aplica LLM classification (se habilitado)
  - Seleciona top 10 por viability score
- [ ] Usa cache existente quando possivel (nao faz API calls redundantes)
- [ ] Envia email digest com template formatado

### AC3: Email digest template
- [ ] Template rico com:
  - Saudacao personalizada
  - Resumo: "X novas oportunidades no seu setor"
  - Top 5-10 oportunidades com: titulo, orgao, UF, valor, viabilidade badge
  - CTA: "Ver todas as oportunidades" → `/buscar?auto=true`
  - Link de unsubscribe
- [ ] Template base: estender `backend/templates/emails/digest.py` existente
- [ ] Responsive para mobile

### AC4: Weekly summary (opcional, mesmo sprint se tempo permitir)
- [ ] Email semanal com:
  - Total de oportunidades da semana
  - Top 3 por viability
  - Estatisticas: setores mais ativos, UFs com mais oportunidades
  - CTA para dashboard

### AC5: Metrics & tracking
- [ ] `smartlic_digest_emails_sent_total` metrica ja existe — usar
- [ ] Analytics: `email_digest_sent`, `email_digest_opened` (via Resend webhooks)
- [ ] Analytics: `email_digest_cta_clicked` (via UTM)
- [ ] Dashboard: taxa de abertura de digests em `/admin`

---

## Database Changes

```sql
-- Add alert_preferences to profiles
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS alert_preferences JSONB DEFAULT '{
  "enabled": true,
  "frequency": "daily",
  "preferred_time": "08:00",
  "min_value": null
}'::jsonb;
```

---

## Arquivos Impactados

| Arquivo | Mudanca |
|---------|---------|
| `supabase/migrations/` | ADD alert_preferences column |
| `backend/cron_jobs.py` | Daily digest cron job |
| `backend/templates/emails/digest.py` | Extend digest template |
| `backend/routes/user.py` | Alert preferences CRUD |
| `frontend/app/conta/page.tsx` | Alert preferences UI |
| `backend/schemas.py` | AlertPreferences Pydantic model |
