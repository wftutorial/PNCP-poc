-- ============================================================================
-- Migration: 20260225110000_fix_handle_new_user_trigger.sql
-- Story: STORY-262 — Signup Trigger Fix — handle_new_user
-- Date: 2026-02-25
-- Depends on: 20260225100000_add_missing_profile_columns.sql (STORY-261)
--
-- Problem:
-- Migration 20260224000000 regressed handle_new_user() to only insert 4 fields
-- (id, email, full_name, phone_whatsapp), silently dropping company, sector,
-- whatsapp_consent, plan_type, avatar_url, and context_data on every new signup.
-- Also missing ON CONFLICT (id) DO NOTHING, which blocks re-signups.
--
-- Fix:
-- Restore all 10 fields in the INSERT + ON CONFLICT (id) DO NOTHING.
-- Phone normalization logic preserved. Phone uniqueness enforced by
-- idx_profiles_phone_whatsapp_unique (partial unique index from 20260224000000).
-- ============================================================================

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
