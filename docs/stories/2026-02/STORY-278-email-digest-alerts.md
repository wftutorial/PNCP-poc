# STORY-278: Email Digest Diario — Feature Table-Stakes Validada

**Priority:** P0 BLOCKER
**Effort:** 3-4 days
**Squad:** @dev + @data-engineer + @qa
**Replaces:** STORY-270 — agora com arquitetura validada

## Fundamentacao (Web Research Validada)

### Todos os concorrentes tem alerta por email

| Plataforma | Cadencia | Tipo |
|------------|---------|------|
| ConLicitacao | **3x/dia** (manha, tarde, noite) | Boletins filtrados por perfil CNAE |
| Siga Pregao | Diario | Jornal de licitacoes personalizado |
| Alerta Licitacao | **2 alertas/dia** (incluso no plano R$45/mes) | Email + SMS por localizacao |
| Licitei | Diario | Alertas por categoria |
| LicitaIA | Ilimitado (plano Ilimitado) | WhatsApp alerts |

Fonte: [ConLicitacao Boletins](https://conlicitacao.com.br/ferramentas/boletins-diarios/), [Alerta Licitacao](https://alertalicitacao.com.br/)

**SmartLic e o unico player do mercado SEM alerta por email.** Isso e inaceitavel para GTM.

### Resend API — Limites Validados

| Plano | Emails/mes | Limite diario | Preco |
|-------|-----------|--------------|-------|
| Free | 3.000 | **100/dia** | $0 |
| Pro | 50.000 | Sem limite | **$20/mes** |

- Rate limit: 2 req/s (compartilhado entre todos os API keys)
- Batch API: ate **100 emails por chamada** (`POST /emails/batch`)
- Fonte: [Resend Pricing](https://resend.com/pricing), [Resend Batch API](https://resend.com/docs/api-reference/emails/send-batch-emails)

**Decisao:** Resend Free basta para beta (<50 usuarios). Migrar para Pro ($20/mes) quando >50.

### Digest > Alertas Individuais (Pesquisa)

- Digest emails tem **35% mais engagement** que alertas individuais
- Reduzem opt-out em **28%**
- Fonte: Braze research via [Courier Blog](https://www.courier.com/blog/how-to-reduce-notification-fatigue-7-proven-product-strategies-for-saas)

## Arquitetura Validada

```
ARQ Cron (10:00 UTC = 7:00 BRT)
  └── daily_digest_job(ctx)
       ├── Query: profiles com digest_enabled=true
       ├── Para cada usuario:
       │    ├── Buscar oportunidades desde last_digest_sent_at
       │    │   (search_results_cache filtrado por setor+UFs do profile_context)
       │    ├── Top 10 por viability_score DESC
       │    ├── Render HTML (templates/emails/digest.py)
       │    └── Adicionar ao batch (max 100 por chamada)
       ├── resend.Batch.send(batch)  ← NEW function
       ├── Atualizar last_digest_sent_at por usuario
       └── Metric: smartlic_digest_emails_sent_total
```

SmartLic ja tem a infra ARQ cron pronta:
- `job_queue.py:961-979`: `_worker_cron_jobs` com `cache_refresh_job` e `cache_warming_job`
- `WorkerSettings:992-998`: functions + cron_jobs registrados
- `email_service.py`: `send_email()` com retry e backoff

## Acceptance Criteria

### AC1: Tabela alert_preferences
- [ ] Migration: `alert_preferences` (user_id FK profiles, frequency ENUM('daily','twice_weekly','weekly','off'), enabled BOOLEAN DEFAULT true, last_digest_sent_at TIMESTAMPTZ)
- [ ] RLS: usuario so ve/edita proprias preferences
- [ ] Default: `frequency='daily'`, `enabled=true` para novos usuarios

### AC2: Digest Service
- [ ] `backend/services/digest_service.py`: `build_digest_for_user(user_id)` → lista de oportunidades
- [ ] Busca em `search_results_cache` filtrado por setor+UFs do `profile_context`
- [ ] Top 10 oportunidades por viability_score (ou mais recentes se sem viability)
- [ ] Inclui: titulo, orgao, valor estimado, UF, viability badge, data publicacao

### AC3: Template de Email
- [ ] `backend/templates/emails/digest.py`: `render_daily_digest_email(user_name, opportunities, stats)`
- [ ] Diferencial SmartLic: viability badge (verde/amarelo/vermelho) por oportunidade — **nenhum concorrente faz isso**
- [ ] CTA unico: "Ver todas as oportunidades" → deeplink `/buscar?auto=true`
- [ ] Mobile-responsive (max-width 600px, inline CSS — mesmo padrao de `trial.py`)
- [ ] Stats resumo: "X novas oportunidades no seu setor hoje"

### AC4: Batch Sending via Resend
- [ ] `email_service.py`: `send_batch_email(messages: list[dict])` usando `resend.Batch.send()`
- [ ] Batch maximo: 100 por chamada (limite Resend)
- [ ] Idempotency key por batch para evitar duplicatas em retry
- [ ] Retry com backoff (mesmo padrao do `send_email` existente)

### AC5: ARQ Cron Job
- [ ] `job_queue.py`: registrar `daily_digest_job` em `WorkerSettings.functions`
- [ ] Cron: `cron(daily_digest_job, hour={10}, minute=0, timeout=1800)` (10:00 UTC = 7:00 BRT)
- [ ] Config: `DIGEST_ENABLED` (default false — ligar quando pronto)
- [ ] Config: `DIGEST_HOUR_UTC` (default 10)
- [ ] Config: `DIGEST_MAX_PER_EMAIL` (default 10)

### AC6: UI de Preferencias
- [ ] `/conta` page: toggle "Receber alerta diario por email" (on/off)
- [ ] Selector de frequencia: Diario / 2x por semana / Semanal
- [ ] Endpoint: `PUT /v1/profile/alert-preferences`
- [ ] Proxy: `frontend/app/api/profile/alert-preferences/route.ts`

### AC7: Metricas
- [ ] `smartlic_digest_emails_sent_total` (Prometheus counter)
- [ ] `smartlic_digest_job_duration_seconds` (Prometheus histogram)
- [ ] Log estruturado: `{"event": "digest_sent", "user_count": N, "batch_count": M}`

## Diferencial Competitivo no Email

O que TODO concorrente faz: lista de licitacoes matchadas.
O que so SmartLic pode fazer: **viability badge** (classificacao IA de relevancia setorial + avaliacao de viabilidade 4 fatores) em cada oportunidade do digest. Nenhum concorrente tem isso.

## Files to Create/Modify

| File | Change |
|------|--------|
| `supabase/migrations/XXXX_alert_preferences.sql` | **NEW** |
| `backend/services/digest_service.py` | **NEW** |
| `backend/templates/emails/digest.py` | **NEW** |
| `backend/email_service.py` | Add `send_batch_email()` |
| `backend/job_queue.py` | Register digest job + cron |
| `backend/config.py` | DIGEST_ENABLED, DIGEST_HOUR_UTC, DIGEST_MAX_PER_EMAIL |
| `backend/metrics.py` | Digest counters |
| `backend/routes/user.py` | PUT /v1/profile/alert-preferences |
| `frontend/app/conta/page.tsx` | Alert preferences UI |

## Custo

- Resend Free: $0 (ate ~50 usuarios com digest diario)
- Resend Pro: $20/mes (quando >50 usuarios)
- ARQ Worker: ja rodando, zero custo adicional
