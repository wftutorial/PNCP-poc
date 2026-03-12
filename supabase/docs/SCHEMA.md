# SmartLic - Database Schema: GTM Readiness Assessment

**Data:** 2026-03-12 | **Auditor:** @data-engineer | **Foco:** Prontidao para Go-To-Market
**Supabase Project:** fqqyovlzdzimiwfofdjk | **PostgreSQL:** 17
**Migrations:** 90 (supabase/) + 7 deprecated (backend/, bridged via DEBT-002)
**Versao:** 2.0 (sobrescreve auditoria 2026-03-10)

---

## 1. Resumo - Prontidao do Banco de Dados

| Area | Status GTM | Justificativa |
|------|-----------|---------------|
| Schema Design | PRONTO | 32 tabelas bem estruturadas, FK standardization completa |
| RLS (Row Level Security) | PRONTO | 100% das tabelas com RLS, 3 rounds de cleanup + runtime assertion |
| Indexes | PRONTO | 28+ indexes otimizados, partial indexes para queries hot |
| Data Retention | PRONTO | 13 pg_cron jobs configurados para cleanup automatico |
| Migrations | PARCIAL | 90 migrations (alto para v0.5), 3 naming conventions |
| Query Patterns | PARCIAL | 2 N+1 queries identificados (alerts, analytics) |
| Billing Tables | PRONTO | plan_billing_periods como source of truth, quota atomica |

**Veredito: PRONTO PARA GTM.** Nenhum bloqueador de banco de dados.

---

## 2. Inventario de Tabelas (32 tabelas)

### Core (Usuario/Auth) — 5 tabelas
| Tabela | PK | RLS | Retention |
|--------|----|----|-----------|
| `profiles` | uuid -> auth.users(id) | Sim | Indefinido |
| `user_subscriptions` | uuid | Sim | Indefinido |
| `monthly_quota` | uuid | Sim | Indefinido |
| `user_oauth_tokens` | uuid | Sim | Indefinido |
| `mfa_recovery_codes` | uuid | Sim | Indefinido |

### Produto (Search/Pipeline) — 5 tabelas
| Tabela | PK | RLS | Retention |
|--------|----|----|-----------|
| `search_sessions` | uuid | Sim | 12 meses |
| `search_state_transitions` | uuid | Sim | 30 dias |
| `search_results_cache` | uuid | Sim | 7d cold / 24h TTL |
| `search_results_store` | uuid | Sim | 24h |
| `pipeline_items` | uuid | Sim | Indefinido |

### Billing — 5 tabelas
| Tabela | PK | RLS | Retention |
|--------|----|----|-----------|
| `plans` | text | Sim (public read) | Indefinido |
| `plan_billing_periods` | uuid | Sim | Indefinido |
| `plan_features` | serial | Sim (public read) | Indefinido |
| `stripe_webhook_events` | varchar | Sim | SEM CLEANUP |
| `reconciliation_log` | uuid | Sim | Indefinido |

### Comunicacao — 6 tabelas
| Tabela | PK | RLS | Retention |
|--------|----|----|-----------|
| `conversations` | uuid | Sim | 24 meses |
| `messages` | uuid | Sim | 24 meses |
| `alerts` | uuid | Sim | Indefinido |
| `alert_preferences` | uuid | Sim | Indefinido |
| `alert_runs` | uuid | Sim | 90 dias |
| `alert_sent_items` | uuid | Sim | 180 dias |

### Multi-Tenant / Partners — 4 tabelas
| Tabela | PK | RLS | Retention |
|--------|----|----|-----------|
| `organizations` | uuid | Sim | Indefinido |
| `organization_members` | uuid | Sim | Indefinido |
| `partners` | uuid | Sim | Indefinido |
| `partner_referrals` | uuid | Sim | Indefinido |

### Operacional — 7 tabelas
| Tabela | PK | RLS | Retention |
|--------|----|----|-----------|
| `audit_events` | uuid | Sim | 12 meses |
| `health_checks` | uuid | Sim | 30 dias |
| `incidents` | uuid | Sim | 90 dias |
| `classification_feedback` | uuid | Sim | 24 meses |
| `trial_email_log` | uuid | Sim (service_role only) | Indefinido |
| `google_sheets_exports` | uuid | Sim | Indefinido |
| `mfa_recovery_attempts` | uuid | Sim | 30 dias |

---

## 3. GTM Strengths

### RLS Completo e Auditado
- 3 rounds de cleanup sistematico (016, TD-003, DEBT-009, DEBT-113)
- Runtime assertion: `RAISE EXCEPTION` se `auth.role()` reaparecer em policies
- Todas as policies usam `TO service_role` para ops internas

### Quota Atomica
- `check_and_increment_quota` RPC: `INSERT ... ON CONFLICT DO UPDATE` single-statement
- Zero race conditions, sem locking application-level

### Cache Inteligente
- `search_results_cache` com 16 campos: priority hot/warm/cold, access_count, fail_streak
- 2MB JSONB constraint, recovery epoch para invalidar cache de degradacao

### Data Retention Automatizado
- 13 pg_cron jobs cobrindo todas as tabelas com dados temporais

---

## 4. Items de Atencao (Nao Bloqueiam GTM)

| ID | Severidade | Issue | Fix Estimado |
|----|-----------|-------|-------------|
| DB-GTM-01 | Media | N+1 alert sent_counts (`alerts.py:254`) | 2h |
| DB-GTM-02 | Media | Python-side aggregation analytics (`analytics.py:218`) | 4h |
| DB-GTM-03 | Baixa | stripe_webhook_events sem cleanup job | 1h |
| DB-GTM-04 | Baixa | profiles.plan_type denormalized (webhook-only sync) | Aceitar risco |
| DB-GTM-05 | Baixa | 90 migrations com 3 naming conventions | Pos-GTM squash |
