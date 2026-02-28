# STORY-322: Plano Consultoria R$997/mes — Multi-User para Consultorias

**Epic:** EPIC-TURBOCASH-2026-03
**Sprint:** Sprint 3 (Scalable Revenue)
**Priority:** P1 — HIGH
**Story Points:** 21 SP (Epic-sized)
**Estimate:** 10-15 dias
**Owner:** @architect + @dev + @data-engineer
**Origem:** TurboCash Playbook — Acao 7 (Scalable Revenue, dia 90-120)

---

## Problem

O SmartLic atualmente suporta apenas usuarios individuais. Consultorias de licitacao (Triunfo Legis, Concreta, Brasil Licitar, etc.) precisam de acesso multi-usuario com dashboard consolidado. Nao existe modelo de precos para este segmento. O TurboCash identifica consultorias como channel de receita escalavel (5-8 consultorias = R$4.985-7.976/mes).

## Solution

Criar "Plano Consultoria" com:
- 3-5 sub-usuarios por conta
- Dashboard consolidado (admin da consultoria ve buscas de todos)
- Logo da consultoria nos relatorios Excel/PDF
- Preco: R$997/mes (mensal), R$897/mes (semestral), R$797/mes (anual)
- Stripe product/price separado do SmartLic Pro

**Evidencia:** ConLicitacao tem 16K clientes a R$149/mes; Inovacao Assessoria opera franquia com margem 78.5%.

---

## Acceptance Criteria

### Backend — Modelo de Dados (Organization)

- [x] **AC1:** Migration para tabela `organizations`:
  ```sql
  CREATE TABLE organizations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    logo_url TEXT,
    owner_id UUID REFERENCES auth.users(id) NOT NULL,
    max_members INT DEFAULT 5,
    stripe_customer_id TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
  );
  ```
- [x] **AC2:** Migration para tabela `organization_members`:
  ```sql
  CREATE TABLE organization_members (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    role TEXT DEFAULT 'member' CHECK (role IN ('owner', 'admin', 'member')),
    invited_at TIMESTAMPTZ DEFAULT now(),
    accepted_at TIMESTAMPTZ,
    UNIQUE(org_id, user_id)
  );
  ```
- [x] **AC3:** RLS policies:
  - Owner/admin pode ver todos os membros
  - Member so ve propria membership
  - Owner pode convidar/remover
  - Dados de busca: admin ve de todos os membros da org

### Backend — Plan & Quota

- [x] **AC4:** Novo plan `consultoria` em `quota.py`:
  - `max_requests_per_month: 5000` (1000 x 5 membros)
  - `max_requests_per_min: 10` (rate limit por org)
  - `allow_excel: true`, `allow_pipeline: true`, `allow_summary: true`
  - `priority: "high"`
  - `max_history_days: 1825`
  - `max_members: 5`
- [x] **AC5:** Quota contabiliza no nivel da org (nao por usuario individual)
- [x] **AC6:** `check_and_increment_quota_atomic` identifica org do usuario e debita quota da org

### Backend — Stripe Integration

- [x] **AC7:** Criar product `SmartLic Consultoria` no Stripe com 3 prices:
  - Mensal: R$997/mes
  - Semestral: R$897/mes (`interval=month`, `interval_count=6`)
  - Anual: R$797/mes (`interval=year`)
- [x] **AC8:** Checkout session cria/atualiza `organizations.stripe_customer_id`
- [x] **AC9:** Webhook handlers sincronizam `org.plan_type` (mesma logica do Pro)
- [x] **AC10:** Boleto habilitado (PIX nao suporta subscription)

### Backend — API Endpoints

- [x] **AC11:** `POST /v1/organizations` — criar org (owner = usuario logado)
- [x] **AC12:** `GET /v1/organizations/{id}` — detalhes da org
- [x] **AC13:** `POST /v1/organizations/{id}/invite` — convidar membro (por email)
- [x] **AC14:** `POST /v1/organizations/{id}/accept` — aceitar convite
- [x] **AC15:** `DELETE /v1/organizations/{id}/members/{user_id}` — remover membro
- [x] **AC16:** `GET /v1/organizations/{id}/dashboard` — stats consolidados (buscas, oportunidades, valor)
- [x] **AC17:** `PUT /v1/organizations/{id}/logo` — upload logo

### Frontend — Gestao de Equipe

- [x] **AC18:** Nova pagina `/conta/equipe`:
  - Lista de membros (nome, email, role, status)
  - Botao "Convidar membro" (modal com input de email)
  - Botao "Remover" por membro (com confirmacao)
  - Indicador de slots usados: "3/5 membros"
- [x] **AC19:** Dashboard consolidado em `/dashboard`:
  - Se usuario e owner/admin de org: toggle "Meus dados" / "Dados da equipe"
  - Metricas: total buscas, total oportunidades, top setores (agregado)
- [x] **AC20:** Upload de logo em `/conta/equipe` (arrastar ou selecionar arquivo)

### Frontend — Pagina de Planos

- [x] **AC21:** Card "Plano Consultoria" na pagina `/planos`:
  - Destaque: "Para consultorias e assessorias"
  - Features: 5 usuarios, dashboard consolidado, logo nos relatorios, suporte prioritario
  - Toggle mensal/semestral/anual (reutilizar PlanToggle)
  - CTA: "Falar com vendas" ou "Assinar Consultoria"
- [x] **AC22:** Badge "Recomendado para consultorias" se UTM indica lead de consultoria

### Backend — Logo nos Relatorios

- [x] **AC23:** `excel.py` → incluir logo da org no header do Excel (se org existir)

### Testes

- [x] **AC25:** Testes: criar org, convidar membro, aceitar, remover
- [x] **AC26:** Testes: quota no nivel da org (debita de pool compartilhado)
- [x] **AC27:** Testes: RLS (member nao ve dados de outro member diretamente)
- [x] **AC28:** Testes: Stripe checkout + webhook para plano consultoria
- [x] **AC29:** Testes frontend: pagina de equipe (CRUD membros)
- [x] **AC30:** Zero regressions

---

## Files Esperados (Output)

**Novos:**
- `supabase/migrations/XXXXXXXX_create_organizations.sql`
- `backend/routes/organizations.py`
- `backend/services/organization_service.py`
- `backend/tests/test_organizations.py`
- `frontend/app/conta/equipe/page.tsx`
- `frontend/components/org/TeamMemberList.tsx`
- `frontend/components/org/InviteMemberModal.tsx`
- `frontend/__tests__/org/team-management.test.tsx`

**Modificados:**
- `backend/quota.py` (plano consultoria + quota por org)
- `backend/routes/billing.py` (checkout consultoria)
- `backend/webhooks/stripe.py` (sync org plan)
- `backend/excel.py` (logo no header)
- `frontend/app/planos/page.tsx` (card consultoria)
- `frontend/app/dashboard/page.tsx` (toggle equipe)

## Dependencias

- Nenhuma bloqueadora
- Stripe product/price criados manualmente ou via script

## Riscos

- Multi-tenancy e complexo → pode exigir refactor do auth flow
- RLS para org-level access pode ser lento em queries agregadas
- Consultorias podem querer mais de 5 membros → parametrizar `max_members`
- Pricing pode precisar de ajuste apos feedback do mercado
