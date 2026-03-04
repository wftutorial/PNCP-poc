-- SEC-001: Enable RLS on health_checks and incidents tables
-- Fixes Supabase Security Advisor error 0013 (RLS Disabled in Public)
-- Backend uses service_role which bypasses RLS — no policies needed.

ALTER TABLE public.health_checks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.incidents ENABLE ROW LEVEL SECURITY;
