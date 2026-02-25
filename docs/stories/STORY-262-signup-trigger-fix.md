# STORY-262: Signup Trigger Fix — handle_new_user

## Metadata
- **Epic:** Enterprise Readiness (EPIC-ENT-001)
- **Priority:** P0 (Blocking)
- **Effort:** 1.5 hours
- **Area:** Database
- **Depends on:** STORY-261 (colunas devem existir antes do trigger referencia-las)
- **Risk:** HIGH — trigger afeta TODOS os novos signups
- **Assessment IDs:** T1-07

## Context

A migration `20260224000000` regrediu o trigger `handle_new_user()` para inserir apenas 4 campos (id, email, full_name, phone_whatsapp), **descartando silenciosamente** company, sector, whatsapp_consent, plan_type, avatar_url, e context_data em todo novo signup. Alem disso, nao tem `ON CONFLICT (id) DO NOTHING`, o que bloqueia completamente re-signups (unique violation).

## Acceptance Criteria

- [ ] AC1: Signup por email com metadata (company, sector, whatsapp_consent) — todos os campos propagados para `profiles`
- [ ] AC2: Signup por Google OAuth — `full_name` e `avatar_url` propagados para `profiles`
- [ ] AC3: Re-signup (profile ja existe) — nao levanta erro (ON CONFLICT DO NOTHING)
- [ ] AC4: Phone normalization funciona: `+5511999998888` -> `11999998888`
- [ ] AC5: Phone invalido (length != 10 ou 11) -> NULL
- [ ] AC6: `plan_type` default `'free_trial'` para novos usuarios
- [ ] AC7: `context_data` default `'{}'::jsonb` para novos usuarios
- [ ] AC8: Full backend test suite passa

## Tasks

- [ ] Task 1: Criar migration `supabase/migrations/20260225110000_fix_handle_new_user_trigger.sql`
- [ ] Task 2: Aplicar migration em staging PRIMEIRO
- [ ] Task 3: Testar signup email com metadata completa
- [ ] Task 4: Testar Google OAuth signup
- [ ] Task 5: Testar re-signup edge case (ON CONFLICT)
- [ ] Task 6: Testar phone normalization (5 cases)
- [ ] Task 7: Deploy em producao apos validacao

## Migration SQL

```sql
-- Migration: 20260225110000_fix_handle_new_user_trigger.sql
-- DEPENDS ON: 20260225100000_add_missing_profile_columns.sql

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
DECLARE
  _phone text;
BEGIN
  _phone := regexp_replace(COALESCE(NEW.raw_user_meta_data->>'phone_whatsapp', ''), '[^0-9]', '', 'g');
  IF length(_phone) > 11 AND left(_phone, 2) = '55' THEN _phone := substring(_phone from 3); END IF;
  IF left(_phone, 1) = '0' THEN _phone := substring(_phone from 2); END IF;
  IF length(_phone) NOT IN (10, 11) THEN _phone := NULL; END IF;

  INSERT INTO public.profiles (
    id, email, full_name, company, sector,
    phone_whatsapp, whatsapp_consent, plan_type,
    avatar_url, context_data
  )
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'full_name', ''),
    COALESCE(NEW.raw_user_meta_data->>'company', ''),
    COALESCE(NEW.raw_user_meta_data->>'sector', ''),
    _phone,
    COALESCE((NEW.raw_user_meta_data->>'whatsapp_consent')::boolean, FALSE),
    'free_trial',
    NEW.raw_user_meta_data->>'avatar_url',
    '{}'::jsonb
  )
  ON CONFLICT (id) DO NOTHING;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

## Test Plan

1. **Email signup:** Criar usuario com company="Test Corp", sector="software", whatsapp_consent=true -> verificar todos os campos em `profiles`
2. **Google OAuth signup:** Criar usuario via OAuth -> verificar full_name e avatar_url propagados
3. **Re-signup:** Tentar criar profile com ID ja existente -> verificar que nao levanta erro
4. **Phone normalization:** Testar +5511999998888 (valid), 011999998888 (valid), 999 (invalid->NULL), empty (->NULL), 5511999998888 (strip 55)
5. Full `pytest` suite

## Regression Risks

- **ALTO RISCO:** Se trigger tem syntax error ou mapeamento incorreto, TODOS os signups falham.
- **Mitigacao:** Deploy em staging primeiro. Testar 3 metodos de signup. Manter rollback SQL pronto (versao anterior do trigger).
- **Rollback:** `CREATE OR REPLACE FUNCTION` com a versao atual de producao.

## Files Changed

- `supabase/migrations/20260225110000_fix_handle_new_user_trigger.sql` (NEW)

## Definition of Done

- [ ] Migration criada e aplicada em staging
- [ ] 3 metodos de signup testados manualmente
- [ ] Phone normalization validada (5 cases)
- [ ] Re-signup edge case validado
- [ ] Deploy em producao
- [ ] Full pytest suite passing
