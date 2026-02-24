# STORY-258: Unicidade de Conta e Verificação de Identidade

## Metadata
| Field | Value |
|-------|-------|
| **ID** | STORY-258 |
| **Title** | Unicidade de Conta e Verificação de Identidade |
| **Type** | Security / Account Integrity |
| **Priority** | Alta |
| **Created** | 2026-02-23 |
| **Status** | Done |
| **Estimated Effort** | L (8-13 pontos) |
| **Tracks** | 3 paralelos (Email Hardening, Phone Uniqueness, Abuse Prevention) |

## Context & Problem Statement

### Estado Atual
O SmartLic usa Supabase Auth para autenticação. A análise do sistema atual revelou:

| Mecanismo | Status | Detalhes |
|-----------|--------|----------|
| **Email uniqueness** | ✅ OK | Supabase Auth enforce no `auth.users` |
| **Email confirmation** | ✅ OK | GTM-FIX-009: obrigatório para login, polling, resend |
| **Signup rate limit** | ✅ OK | 3 registros/IP/10min no proxy |
| **Phone uniqueness** | ❌ Ausente | Sem UNIQUE constraint em `profiles.phone_whatsapp` |
| **Phone verification** | ❌ Ausente | Apenas validação de formato (10-11 dígitos) |
| **Disposable email block** | ❌ Ausente | Aceita tempmail, guerrillamail, etc. |
| **Email change flow** | ❌ Ausente | Sem endpoint para alterar email pós-signup |
| **Account merge/recovery** | ❌ Ausente | Sem mecanismo para contas duplicadas |
| **OAuth + email dedup** | ⚠️ Parcial | Google OAuth cria conta separada se email já existir via signup |

### Riscos
1. **Contas fantasma**: Emails descartáveis geram trials sem valor
2. **Abuso de trial**: Mesmo telefone pode criar N contas com N emails
3. **Duplicação por OAuth**: Usuário com email+senha e Google OAuth = 2 perfis
4. **Sem barreira de telefone**: Phone é campo livre, sem verificação

### Decisão de Escopo
**NÃO inclui SMS/OTP nesta story** (custo operacional alto, ~R$0.05/SMS). Foco em mecanismos de baixo custo e alto impacto.

---

## Acceptance Criteria

### Track 1: Email Hardening (Backend + Frontend)

- [x] **AC1** — Criar lista de domínios descartáveis (`backend/utils/disposable_emails.py`) com ≥500 domínios conhecidos (tempmail, guerrillamail, yopmail, mailinator, etc.). Fonte: lista pública curada + top-50 brasileiros.
- [x] **AC2** — Validar domínio no `POST /auth/v1/signup` proxy (`frontend/app/api/auth/signup/route.ts`): rejeitar com HTTP 422 e mensagem `"Este provedor de email não é aceito. Use um email corporativo ou pessoal (Gmail, Outlook, etc.)"`.
- [x] **AC3** — Validar também no backend (`backend/routes/auth_email.py` ou middleware) como segunda barreira — defesa em profundidade.
- [x] **AC4** — Normalizar email antes de comparação: lowercase, trim, strip dots do Gmail (j.o.h.n@gmail.com = john@gmail.com), strip +alias (john+test@gmail.com = john@gmail.com).
- [x] **AC5** — Adicionar UNIQUE constraint em `profiles.email` via migration (defesa em profundidade, já que `auth.users` é source of truth).
- [x] **AC6** — Frontend: mostrar validação inline no campo email do signup quando domínio é descartável (antes do submit, no `onBlur`).

### Track 2: Phone Uniqueness (Backend + Database)

- [x] **AC7** — Criar migration adicionando UNIQUE constraint em `profiles.phone_whatsapp` (parcial: `WHERE phone_whatsapp IS NOT NULL`) — permitir múltiplos NULLs.
- [x] **AC8** — Normalizar telefone antes de salvar: remover espaços, parênteses, hífens, garantir formato `XXXXXXXXXXX` (11 dígitos com DDD) ou `XXXXXXXXXX` (10 dígitos fixo).
- [x] **AC9** — No signup, se `phone_whatsapp` já existir em outro perfil: retornar erro `"Este telefone já está associado a outra conta. Use outro número ou entre em contato com suporte."` (HTTP 409).
- [x] **AC10** — Atualizar trigger `handle_new_user()` para verificar unicidade do phone ANTES de inserir no `profiles`.
- [x] **AC11** — Frontend signup form: validar telefone em tempo real via debounce (300ms) chamando `GET /v1/auth/check-phone?phone=XXXXXXXXXXX` → `{ available: boolean }`.
- [x] **AC12** — Endpoint `GET /v1/auth/check-phone`: rate-limited (10 req/min/IP), retorna apenas boolean (não expor dados de outros usuários).

### Track 3: Abuse Prevention & Account Integrity

- [x] **AC13** — Implementar detecção de conta duplicada por fingerprint leve: se mesmo `phone_whatsapp` + mesmo `company` já existir (com email diferente), logar warning no audit log (não bloquear — apenas observabilidade).
- [x] **AC14** — Logar tentativas de signup com email descartável no `audit.py` com nível WARNING (para análise de padrões de abuso).
- [x] **AC15** — Endpoint `GET /v1/auth/check-email` para validação pre-signup: retorna `{ available: boolean, disposable: boolean }`. Rate-limited (10 req/min/IP). Não expor se email existe — retornar `available: true` para emails descartáveis (para não revelar que foram bloqueados vs já cadastrados).
- [x] **AC16** — Na tela de signup, mostrar badge visual "Email corporativo" (verde) ou "Email pessoal" (neutro) baseado no domínio — incentivo positivo sem bloqueio.

### Track 4: Testes

- [x] **AC17** — Testes unitários para `disposable_emails.py`: ≥15 domínios conhecidos + ≥5 domínios legítimos (gmail, outlook, hotmail, yahoo, empresa.com.br).
- [x] **AC18** — Testes unitários para normalização de email (Gmail dots, +alias, uppercase, trim).
- [x] **AC19** — Testes unitários para normalização e unicidade de telefone.
- [x] **AC20** — Teste de integração: signup com email descartável → 422.
- [x] **AC21** — Teste de integração: signup com telefone duplicado → 409.
- [x] **AC22** — Testes frontend: validação inline de email descartável e telefone duplicado.
- [x] **AC23** — Zero regressões nos testes existentes (backend baseline: ~35 fail, frontend baseline: ~50 fail).

---

## Technical Design

### Arquitetura

```
Signup Form (frontend)
    │
    ├─ onBlur(email) → GET /v1/auth/check-email → { available, disposable }
    ├─ onBlur(phone) → GET /v1/auth/check-phone → { available }
    │
    ▼
POST /api/auth/signup (Next.js proxy)
    │
    ├─ 1. Disposable email check (blocklist)
    ├─ 2. Email normalization (dots, +alias)
    ├─ 3. Rate limit (3/IP/10min — já existe)
    │
    ▼
Supabase Auth (auth.users)
    │
    ├─ Email uniqueness (enforced by Supabase)
    ├─ Email confirmation (já existe)
    │
    ▼
Trigger: handle_new_user()
    │
    ├─ Phone normalization
    ├─ Phone uniqueness check (UNIQUE constraint)
    ├─ Duplicate fingerprint detection (phone+company)
    │
    ▼
profiles (row created)
```

### Novos Arquivos

| Arquivo | Propósito |
|---------|-----------|
| `backend/utils/disposable_emails.py` | Lista + checker de domínios descartáveis |
| `backend/utils/email_normalizer.py` | Normalização Gmail dots, +alias, trim |
| `backend/utils/phone_normalizer.py` | Normalização e formatação de telefone BR |
| `backend/routes/auth_check.py` | Endpoints check-email e check-phone |
| `supabase/migrations/XXX_phone_unique_email_unique.sql` | Constraints |
| `backend/tests/test_disposable_emails.py` | Testes blocklist |
| `backend/tests/test_email_normalizer.py` | Testes normalização |
| `backend/tests/test_phone_normalizer.py` | Testes telefone |
| `backend/tests/test_auth_check.py` | Testes endpoints |
| `frontend/__tests__/signup-validation.test.tsx` | Testes frontend |

### Arquivos Modificados

| Arquivo | Mudança |
|---------|---------|
| `frontend/app/api/auth/signup/route.ts` | Adicionar check de disposable email |
| `frontend/app/signup/page.tsx` | Validação inline email + phone |
| `backend/routes/auth_email.py` | Backend validation de disposable |
| `backend/main.py` | Registrar router `auth_check` |
| `supabase/migrations/007_*.sql` (trigger) | Atualizar `handle_new_user()` |

### Normalização de Email — Regras

```python
def normalize_email(email: str) -> str:
    """
    Normaliza email para detecção de duplicatas.

    Regras:
    1. lowercase + trim
    2. Gmail/Googlemail: remove dots do local part
    3. Gmail/Googlemail/Outlook/Hotmail: remove +alias
    4. googlemail.com → gmail.com
    """
```

### Disposable Email — Estratégia

- Lista estática embutida (≥500 domínios) — sem dependência externa
- Atualização manual periódica (a cada 3-6 meses)
- Estrutura: `set()` para O(1) lookup
- Fontes: `disposable-email-domains` (GitHub, 3k+ domínios) filtrado para top relevantes

### Phone Normalization — Regras

```python
def normalize_phone(phone: str) -> str:
    """
    Normaliza telefone brasileiro.

    Regras:
    1. Remove tudo que não é dígito
    2. Se começa com +55, remove
    3. Se começa com 0, remove (DDD antigo)
    4. Resultado: 10 ou 11 dígitos (DDD + número)
    """
```

---

## Security Considerations

1. **Information leakage**: `check-email` NÃO revela se email já existe (retorna `available: true` para descartáveis, evitando enumeration)
2. **Rate limiting**: Ambos endpoints check-email/check-phone limitados a 10 req/min/IP
3. **Timing attack**: Usar comparação constant-time onde possível
4. **Privacy (LGPD)**: Phone não exposto em respostas; apenas boolean `available`
5. **Audit trail**: Todas tentativas de signup com email descartável logadas

## Migration Safety

- UNIQUE constraint em `phone_whatsapp` é parcial (`WHERE NOT NULL`) — não afeta registros existentes sem telefone
- UNIQUE constraint em `profiles.email` — verificar se há duplicatas antes de aplicar (query: `SELECT email, COUNT(*) FROM profiles GROUP BY email HAVING COUNT(*) > 1`)
- Se houver duplicatas, resolver manualmente antes da migration
- Migration é reversível (DROP CONSTRAINT)

---

## Out of Scope (Futuro)

- [x] SMS/OTP phone verification (custo ~R$0.05/SMS — avaliar quando tiver revenue)
- [x] CAPTCHA no signup (reCAPTCHA/hCaptcha)
- [x] Account merge (unificar perfis duplicados)
- [x] Email change flow (alterar email pós-signup)
- [x] Multi-factor authentication (TOTP/WebAuthn)
- [x] IP geolocation blocking (signup apenas do Brasil)
- [x] Device fingerprinting avançado (FingerprintJS)

---

## Dependencies

- Supabase Auth (já configurado)
- Supabase migrations CLI (`npx supabase db push`)
- Nenhuma dependência externa nova (lista de emails é estática)

## Definition of Done

- [x] Todos os ACs marcados ✅
- [x] Zero regressões nos testes existentes
- [x] Migration aplicada em staging + production
- [x] Documentação em CHANGELOG.md atualizada
- [x] Handoff criado em `docs/sessions/`
