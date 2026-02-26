# STORY-289: Referral Program & Lead Magnets

**Priority:** P1 (Acquisition Gap)
**Effort:** L (3-5 days)
**Squad:** @dev + @pm
**Fundamentacao:** GTM Readiness Audit Track 8 — MKT-021, MKT-022
**Status:** TODO
**Sprint:** GTM Sprint 2 (Pre-Acquisition)

---

## Contexto

O audit identificou dois gaps criticos de aquisicao organica:

1. **Sem referral program** — no nicho B2G de licitacoes, word-of-mouth de usuarios satisfeitos e extremamente valioso. Nenhum mecanismo de indicacao existe.
2. **Sem lead magnets** — 30 artigos de blog de alta qualidade existem mas sem gated content ou captura de email. Todo conteudo e aberto sem CTA de conversao.

---

## Acceptance Criteria

### AC1: Referral program basico
- [ ] Modelo: "Indique um colega e ambos ganham 7 dias gratis adicionais"
- [ ] Gerar link unico de indicacao por usuario (`/signup?ref={user_id_hash}`)
- [ ] Rastrear indicacoes em tabela `referrals` (referrer_id, referred_id, status, created_at)
- [ ] Creditar 7 dias extras ao referrer quando referred completa signup
- [ ] UI: Secao "Indique e Ganhe" em `/conta` com link copiavel e contagem
- [ ] Email: notificacao ao referrer quando indicacao converte
- [ ] Analytics: track `referral_link_copied`, `referral_signup_completed`

### AC2: Lead magnet — Guia PDF
- [ ] Selecionar 3 melhores artigos do blog e compilar em PDF guia
- [ ] Titulo sugerido: "Guia Pratico: Como Avaliar se Uma Licitacao Vale a Pena"
- [ ] Componente `LeadMagnetCTA` com form de email capture
- [ ] Posicionar em: sidebar do blog, footer dos artigos, popup (nao exit-intent por ora)
- [ ] Backend endpoint: `POST /v1/lead-capture` (email, source, utm_*)
- [ ] Enviar PDF por email via Resend apos captura
- [ ] Salvar leads em tabela `leads` (email, source, utm_source, created_at)
- [ ] Analytics: track `lead_magnet_viewed`, `lead_captured`

### AC3: Email nurture basico para leads
- [ ] Welcome email com PDF anexo/link
- [ ] 3 dias depois: "Voce ja conhece o SmartLic?" com CTA trial
- [ ] Respeitar opt-out (unsubscribe link)

---

## Database Changes

```sql
-- Referrals table
CREATE TABLE referrals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  referrer_id UUID REFERENCES profiles(id),
  referred_id UUID REFERENCES profiles(id),
  referral_code TEXT UNIQUE NOT NULL,
  status TEXT DEFAULT 'pending', -- pending, completed, expired
  reward_granted BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE referrals ENABLE ROW LEVEL SECURITY;

-- Leads table
CREATE TABLE leads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT NOT NULL,
  source TEXT, -- blog, landing, popup
  utm_source TEXT,
  utm_medium TEXT,
  utm_campaign TEXT,
  lead_magnet TEXT, -- which PDF/guide
  created_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
```

---

## Arquivos Impactados

| Arquivo | Mudanca |
|---------|---------|
| `supabase/migrations/` | Nova migration para referrals + leads |
| `backend/routes/referral.py` | NOVO — endpoints de referral |
| `backend/routes/leads.py` | NOVO — endpoint de lead capture |
| `frontend/app/conta/page.tsx` | Secao "Indique e Ganhe" |
| `frontend/components/LeadMagnetCTA.tsx` | NOVO |
| `frontend/app/blog/` | Adicionar LeadMagnetCTA |
| `backend/templates/emails/referral.py` | NOVO |
| `backend/templates/emails/lead_nurture.py` | NOVO |
