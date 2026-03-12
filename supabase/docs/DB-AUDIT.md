# SmartLic - Database Detailed Audit: GTM Readiness

**Data:** 2026-03-12 | **Auditor:** @data-engineer
**Versao:** 2.0 (sobrescreve auditoria 2026-03-10)

---

## 1. Query Performance Issues

### N+1: Alert Sent Counts (DB-GTM-01)
**Arquivo:** `backend/routes/alerts.py:254-264`
- Loop de N queries para contar sent items por alerta
- **Fix:** Single query com `ANY($1) GROUP BY alert_id`
- **Esforco:** 2h | **Impacto GTM:** Baixo (poucos usuarios com 10+ alertas no lancamento)

### Python-Side Aggregation (DB-GTM-02)
**Arquivo:** `backend/routes/analytics.py:218-248`
- Todas as sessoes fetched para Python para UNNEST de arrays
- **Fix:** PostgreSQL `UNNEST()` aggregation via RPC
- **Esforco:** 4h | **Impacto GTM:** Baixo (escala de lancamento < 500 sessoes/usuario)

### Admin Unread Count (DB-GTM-03)
**Arquivo:** `backend/routes/messages.py:379-389`
- 2 round-trips quando RPC `get_conversations_with_unread_count` ja existe
- **Esforco:** 1h | **Impacto GTM:** Negligivel (apenas admin)

---

## 2. Index Coverage Summary

28+ indexes cobrem todos os hot paths identificados:
- `profiles`: 5 indexes (admin, email trgm, email unique, phone unique, subscription status)
- `search_sessions`: 4 indexes (created, status, inflight, search_id)
- `search_results_cache`: 5 indexes (user, global_hash, priority, degraded, params_hash)
- `pipeline_items`: 2 indexes (user_stage, encerramento)
- `user_subscriptions`: 3 indexes (stripe_sub_id, active, billing)

**Missing indexes identificados (nao criticos para GTM):**
- `user_subscriptions(user_id)` non-partial — billing history
- `conversations(user_id, last_message_at DESC)` — inbox sort
- `partner_referrals(converted_at)` — revenue reporting

---

## 3. Data Integrity Validated

- [x] FK standardization: COMPLETA (DEBT-001, -002, -100, -104, -113)
- [x] RLS: COMPLETA (3 rounds + runtime assertion)
- [x] Quota atomicity: COMPLETA (single-statement RPC)
- [x] Cache size limits: COMPLETA (2MB JSONB constraint)
- [x] Retention policies: 13 pg_cron jobs ativos
- [x] Audit trail: LGPD-compliant com hash de PII
