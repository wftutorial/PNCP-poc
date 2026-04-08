-- ╔══════════════════════════════════════════════════════════════════════════╗
-- ║  DEBT-03: RPC Security Audit — Findings & Fixes                        ║
-- ║  TD-059: Auditar todas as RPCs Supabase para validação auth.uid()      ║
-- ║                                                                          ║
-- ║  Auditoria conduzida em 2026-04-08.                                     ║
-- ║  Migration 20260404000000 já cobriu CRIT-SEC-001/002/004.              ║
-- ║  Este arquivo corrige os 2 achados residuais.                           ║
-- ╚══════════════════════════════════════════════════════════════════════════╝

-- ─────────────────────────────────────────────────────────────────────────────
-- FINDING-01: search_datalake acessível a authenticated (risco de bypass de quota)
--
-- A função search_datalake consulta pncp_raw_bids (dados públicos de licitações).
-- Não expõe PII, mas o acesso direto por usuários autenticados via PostgREST
-- permite contornar o sistema de quotas do backend.
-- Correção: REVOKE de authenticated — apenas service_role (backend) pode chamar.
-- ─────────────────────────────────────────────────────────────────────────────

DO $$ BEGIN
  REVOKE EXECUTE ON FUNCTION public.search_datalake(
    TEXT[], DATE, DATE, TEXT, INTEGER[], NUMERIC, NUMERIC, TEXT[], TEXT, INTEGER
  ) FROM PUBLIC;
  REVOKE EXECUTE ON FUNCTION public.search_datalake(
    TEXT[], DATE, DATE, TEXT, INTEGER[], NUMERIC, NUMERIC, TEXT[], TEXT, INTEGER
  ) FROM authenticated;
  GRANT EXECUTE ON FUNCTION public.search_datalake(
    TEXT[], DATE, DATE, TEXT, INTEGER[], NUMERIC, NUMERIC, TEXT[], TEXT, INTEGER
  ) TO service_role;
EXCEPTION WHEN undefined_function THEN NULL;
END $$;

-- ─────────────────────────────────────────────────────────────────────────────
-- FINDING-02: increment_share_view sem GRANT explícito
--
-- A função increment_share_view é chamada pelo backend (service_role) ao
-- renderizar páginas públicas de análise compartilhada (/analise/[hash]).
-- Por padrão em PostgreSQL, PUBLIC tem EXECUTE em funções novas.
-- Tornamos explícita a intenção: anon pode incrementar (página pública),
-- authenticated pode incrementar (usuário logado visualizando),
-- service_role pode incrementar (backend).
-- Não expõe nenhum dado de usuário — apenas incrementa um contador.
-- ─────────────────────────────────────────────────────────────────────────────

-- Revoke do public genérico, re-grant explícito com roles corretos
REVOKE EXECUTE ON FUNCTION public.increment_share_view(VARCHAR) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.increment_share_view(VARCHAR) TO anon;
GRANT EXECUTE ON FUNCTION public.increment_share_view(VARCHAR) TO authenticated;
GRANT EXECUTE ON FUNCTION public.increment_share_view(VARCHAR) TO service_role;

-- ─────────────────────────────────────────────────────────────────────────────
-- INVENTORY COMMENT: RPCs auditadas e confirmadas OK (sem mudança necessária)
--
-- USER-SCOPED (protegidas por auth.uid() guard — migration 20260404000000):
--   get_analytics_summary             — ✅ IF auth.uid() IS NOT NULL AND p_user_id != auth.uid() THEN RAISE
--   get_conversations_with_unread_count — ✅ verifica admin no DB, não confia no parâmetro
--   get_user_billing_period           — ✅ IF auth.uid() IS NOT NULL AND p_user_id != auth.uid() THEN RAISE
--   user_has_feature                  — ✅ IF auth.uid() IS NOT NULL AND p_user_id != auth.uid() THEN RAISE
--   get_user_features                 — ✅ IF auth.uid() IS NOT NULL AND p_user_id != auth.uid() THEN RAISE
--
-- SERVICE-ONLY (REVOKED de authenticated/public — migration 20260404000000):
--   check_and_increment_quota         — ✅ REVOKED, service_role only
--   increment_quota_atomic            — ✅ REVOKED, service_role only
--   increment_quota_fallback_atomic   — ✅ REVOKED, service_role only
--   upsert_pncp_raw_bids             — ✅ REVOKED, service_role only
--   purge_old_bids                    — ✅ REVOKED, service_role only
--   check_ingestion_orphans           — ✅ REVOKED, service_role only
--   check_pncp_raw_bids_bloat        — ✅ REVOKED, service_role only
--   pg_total_relation_size_safe       — ✅ REVOKED, service_role only
--   get_table_columns_simple          — ✅ REVOKED, service_role only
--
-- PUBLIC/ANON (dados públicos, sem PII — intencionais):
--   get_sitemap_cnpjs                 — ✅ GRANT anon/authenticated/service_role (SEO sitemap)
--   get_sitemap_orgaos                — ✅ GRANT anon/authenticated/service_role (SEO sitemap)
--   get_sitemap_cnpjs_json            — ✅ GRANT anon/authenticated/service_role (SEO sitemap)
--   get_sitemap_orgaos_json           — ✅ GRANT anon/authenticated/service_role (SEO sitemap)
--
-- UTILITY (sem acesso a dados de usuário):
--   generate_referral_code            — ✅ Retorna string aleatória, sem dados de usuário
--
-- TRIGGERS (não acessíveis via PostgREST):
--   cleanup_search_cache_per_user     — ✅ TRIGGER FUNCTION
--   prevent_privilege_escalation      — ✅ TRIGGER FUNCTION
--   handle_new_user                   — ✅ TRIGGER FUNCTION
--   set_updated_at / update_updated_at / update_pipeline_updated_at — ✅ TRIGGERS
--   pncp_raw_bids_tsv_trigger         — ✅ TRIGGER FUNCTION
--   sync_profile_plan_type            — ✅ TRIGGER FUNCTION
--   sync_subscription_status_to_profile — ✅ TRIGGER FUNCTION
-- ─────────────────────────────────────────────────────────────────────────────
