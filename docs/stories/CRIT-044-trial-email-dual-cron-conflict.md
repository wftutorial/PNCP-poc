# CRIT-044: Resolver Conflito de Dual Cron Trial Emails

**Epic:** Production Stability
**Sprint:** Sprint 4
**Priority:** P1 — HIGH
**Story Points:** 5 SP
**Estimate:** 3-4 horas
**Owner:** @dev

---

## Problem

Existem DOIS sistemas de trial emails rodando em paralelo, causando conflito:

### Sistema Legacy (STORY-266) — `cron_jobs.py:check_trial_reminders()`
- Milestones: `{3: "midpoint", 5: "expiring", 6: "last_day", 8: "expired"}`
- Feature flag: `TRIAL_EMAILS_ENABLED`
- Roda como cron dentro do backend
- NÃO verifica `profiles.marketing_emails_enabled`

### Sistema Novo (STORY-310) — `services/trial_email_sequence.py`
- Sequência: 8 emails nos dias 0/3/7/14/21/25/29/32
- Verifica `profiles.marketing_emails_enabled` (coluna que não existe em produção → erro 42703)
- Roda via ARQ job
- Mais sofisticado (unsubscribe HMAC, digest-style)

**Erros observados no Sentry (últimas 24h):**

| Issue | Origem | Eventos |
|---|---|---|
| SMARTLIC-BACKEND-1W | STORY-310: `profiles.marketing_emails_enabled` does not exist (42703) | 10 |
| SMARTLIC-BACKEND-1X | STORY-310: trial email #7 day=29 — CB open (consequência) | 6 |
| SMARTLIC-BACKEND-21 | STORY-266: trial milestone day=3/5/6/8 — CB open | 16 |

**Impacto:** Ambos os sistemas falham (um por coluna ausente, outro por CB open), e o usuário não recebe nenhum email de trial.

---

## Solution

1. Desativar sistema legacy (STORY-266) — substituído pelo STORY-310
2. Garantir que CRIT-039 aplique migração da coluna `marketing_emails_enabled`
3. Validar que o sistema novo funciona end-to-end após migração

---

## Acceptance Criteria

### Backend — Remoção do Legacy

- [ ] **AC1:** Em `cron_jobs.py:check_trial_reminders()`: remover completamente a função e seu registro no cron scheduler
  - Alternativa: se preferir manter como fallback, adicionar guard `if TRIAL_EMAIL_V2_ENABLED: return` no topo
- [ ] **AC2:** Remover `TRIAL_EMAIL_MILESTONES` dict de `cron_jobs.py`
- [ ] **AC3:** Verificar que `services/trial_email_sequence.py` tem ARQ job configurado em `job_queue.py`

### Backend — Validação do Sistema Novo

- [ ] **AC4:** Após CRIT-039 (migração aplicada), executar manualmente `trial_email_sequence` para um usuário de teste e confirmar que email é enviado
- [ ] **AC5:** Verificar que o `hmac.new()` em `trial_email_sequence.py` (~line 37) está usando a API correta do Python 3.12 (`hmac.new(key, msg, digestmod)`)
- [ ] **AC6:** Verificar que unsubscribe link funciona (POST endpoint existe e processa opt-out)

### Backend — Feature Flags

- [ ] **AC7:** Se `TRIAL_EMAILS_ENABLED=false` em Railway, o sistema novo (STORY-310) também deve respeitar este flag
- [ ] **AC8:** Documentar em `.env.example` qual flag controla cada sistema

### Testes

- [ ] **AC9:** Teste: com `marketing_emails_enabled=False` → email NÃO é enviado (skip)
- [ ] **AC10:** Teste: com `marketing_emails_enabled=True` → email É enviado
- [ ] **AC11:** Teste: cron legacy não roda mais (removido ou guarded)

---

## Dependências

- **Bloqueado por:** CRIT-039 (migração que cria coluna `marketing_emails_enabled`)

---

## Arquivos Impactados

| Arquivo | Mudança |
|---------|---------|
| `backend/cron_jobs.py` | Remover/guard `check_trial_reminders()` |
| `backend/services/trial_email_sequence.py` | Validar hmac, testar end-to-end |
| `backend/job_queue.py` | Verificar registro do ARQ job |
| `backend/.env.example` | Documentar feature flags |
