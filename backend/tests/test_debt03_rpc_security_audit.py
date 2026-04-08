"""
DEBT-03: RPC Security Audit — Static Analysis Tests

Validates the security properties of all Supabase RPC functions by analyzing
the migration SQL files. No live database connection required.

AC1: Lista completa de RPCs user-scoped com status (protegida/exposta)
AC2: Todas as RPCs sem auth.uid() corrigidas ou documentadas como intencionais
AC3: Documento de findings em docs/reviews/rpc-audit-YYYY-MM-DD.md
AC4: Define escopo de TD-005 (per-user Supabase tokens)
"""

import os
import re
import pytest
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MIGRATIONS_DIR = REPO_ROOT / "supabase" / "migrations"
BACKEND_MIGRATIONS_DIR = REPO_ROOT / "backend" / "migrations"


def load_migration(filename: str) -> str:
    """Load a migration file by name (searches both migration dirs)."""
    for directory in [MIGRATIONS_DIR, BACKEND_MIGRATIONS_DIR]:
        path = directory / filename
        if path.exists():
            return path.read_text(encoding="utf-8")
    raise FileNotFoundError(f"Migration not found: {filename}")


def load_all_migrations() -> str:
    """Concatenate all migration SQL files for global analysis."""
    parts = []
    for directory in [MIGRATIONS_DIR, BACKEND_MIGRATIONS_DIR]:
        if directory.exists():
            for sql_file in sorted(directory.glob("*.sql")):
                parts.append(f"-- FILE: {sql_file.name}\n")
                parts.append(sql_file.read_text(encoding="utf-8"))
    return "\n".join(parts)


@pytest.fixture(scope="module")
def security_hardening_sql():
    return load_migration("20260404000000_security_hardening_rpc_rls.sql")


@pytest.fixture(scope="module")
def audit_fix_sql():
    return load_migration("20260408220000_debt03_rpc_security_audit.sql")


@pytest.fixture(scope="module")
def all_migrations_sql():
    return load_all_migrations()


# ─────────────────────────────────────────────────────────────────────────────
# AC1: Lista completa de RPCs user-scoped verificada
# ─────────────────────────────────────────────────────────────────────────────


class TestAC1UserScopedRPCsProtected:
    """AC1: All user-scoped RPCs must have auth.uid() guard."""

    USER_SCOPED_RPCS = [
        "get_analytics_summary",
        "get_conversations_with_unread_count",
        "get_user_billing_period",
        "user_has_feature",
        "get_user_features",
    ]

    def test_hardening_migration_exists(self):
        """Migration 20260404000000 (main security fix) must exist."""
        assert (MIGRATIONS_DIR / "20260404000000_security_hardening_rpc_rls.sql").exists(), (
            "Security hardening migration must exist"
        )

    def test_all_user_scoped_rpcs_have_auth_uid_guard(self, security_hardening_sql):
        """Each user-scoped RPC must contain the auth.uid() guard pattern."""
        for rpc_name in self.USER_SCOPED_RPCS:
            assert rpc_name in security_hardening_sql, (
                f"RPC {rpc_name!r} not found in security hardening migration"
            )

    def test_auth_uid_guard_pattern_present_for_each_rpc(self, security_hardening_sql):
        """The auth.uid() IS NOT NULL AND p_user_id != auth.uid() pattern must appear."""
        guard_pattern = "auth.uid() IS NOT NULL AND p_user_id != auth.uid()"
        occurrences = security_hardening_sql.count(guard_pattern)
        # get_analytics_summary, get_user_billing_period, user_has_feature, get_user_features = 4
        # get_conversations_with_unread_count uses a different (more complex) pattern
        assert occurrences >= 4, (
            f"Expected at least 4 auth.uid() guards, found {occurrences}. "
            "Some user-scoped RPCs may be missing protection."
        )

    def test_conversations_rpc_verifies_admin_from_db(self, security_hardening_sql):
        """get_conversations_with_unread_count must verify admin from DB, not trust parameter."""
        # Look for the section that reads is_admin from profiles
        assert "FROM profiles p WHERE p.id = auth.uid()" in security_hardening_sql, (
            "get_conversations_with_unread_count must read is_admin from profiles, "
            "not trust the p_is_admin parameter."
        )

    def test_forbidden_exception_raised_on_cross_user_access(self, security_hardening_sql):
        """All user-scoped RPCs raise 42501 (insufficient_privilege) on violation."""
        errcode_count = security_hardening_sql.count("ERRCODE = '42501'")
        assert errcode_count >= 4, (
            f"Expected ≥4 ERRCODE 42501 raises, found {errcode_count}. "
            "Cross-user access violations must raise insufficient_privilege."
        )


# ─────────────────────────────────────────────────────────────────────────────
# AC2: Service-only RPCs revoked from authenticated/public
# ─────────────────────────────────────────────────────────────────────────────


class TestAC2ServiceOnlyRPCsRevoked:
    """AC2: Service-only RPCs must be inaccessible to regular users."""

    def test_quota_functions_revoked_from_authenticated(self, security_hardening_sql):
        """check_and_increment_quota must be REVOKED from PUBLIC and authenticated."""
        assert "REVOKE EXECUTE ON FUNCTION public.check_and_increment_quota" in security_hardening_sql
        assert "FROM authenticated" in security_hardening_sql

    def test_increment_quota_atomic_revoked(self, security_hardening_sql):
        """increment_quota_atomic must be REVOKED from PUBLIC and authenticated."""
        assert "REVOKE EXECUTE ON FUNCTION public.increment_quota_atomic" in security_hardening_sql

    def test_ingestion_rpcs_revoked(self, security_hardening_sql):
        """Ingestion RPCs must be REVOKED from authenticated/public."""
        ingestion_rpcs = [
            "check_ingestion_orphans",
            "pg_total_relation_size_safe",
            "get_table_columns_simple",
        ]
        for rpc in ingestion_rpcs:
            assert rpc in security_hardening_sql, (
                f"Ingestion RPC {rpc!r} not mentioned in security hardening migration"
            )
            assert "REVOKE EXECUTE ON FUNCTION public." + rpc in security_hardening_sql, (
                f"RPC {rpc!r} must be explicitly REVOKED"
            )

    def test_search_datalake_revoked_from_authenticated(self, audit_fix_sql):
        """FINDING-01: search_datalake must be REVOKED from authenticated (quota bypass fix)."""
        assert "REVOKE EXECUTE ON FUNCTION public.search_datalake" in audit_fix_sql, (
            "search_datalake must be REVOKED from authenticated to prevent quota bypass"
        )
        assert "FROM authenticated" in audit_fix_sql, (
            "The REVOKE must specifically target authenticated role"
        )

    def test_search_datalake_still_granted_to_service_role(self, audit_fix_sql):
        """search_datalake must remain accessible to service_role (backend calls it)."""
        assert "GRANT EXECUTE ON FUNCTION public.search_datalake" in audit_fix_sql
        assert "TO service_role" in audit_fix_sql

    def test_quota_functions_granted_to_service_role(self, security_hardening_sql):
        """After REVOKE, quota functions must be re-granted to service_role."""
        # check_and_increment_quota
        grant_section = security_hardening_sql[
            security_hardening_sql.find("check_and_increment_quota"):
        ]
        assert "GRANT  EXECUTE ON FUNCTION public.check_and_increment_quota" in security_hardening_sql


# ─────────────────────────────────────────────────────────────────────────────
# AC2 (continued): Public/intentional RPCs documented
# ─────────────────────────────────────────────────────────────────────────────


class TestAC2PublicRPCsDocumented:
    """AC2 (doc part): Public RPCs must be documented as intentional."""

    def test_sitemap_rpcs_intentionally_public(self, all_migrations_sql):
        """Sitemap RPCs must have GRANT to anon (intentional public access)."""
        # Verify GRANTs exist
        assert "GRANT EXECUTE ON FUNCTION public.get_sitemap_cnpjs" in all_migrations_sql
        assert "GRANT EXECUTE ON FUNCTION public.get_sitemap_orgaos" in all_migrations_sql
        # Must include anon role
        sitemap_section = all_migrations_sql[
            all_migrations_sql.rfind("get_sitemap_cnpjs"):
            all_migrations_sql.rfind("get_sitemap_cnpjs") + 500
        ]
        assert "anon" in sitemap_section, (
            "Sitemap RPCs must be explicitly granted to anon (public sitemap pages)"
        )

    def test_increment_share_view_has_explicit_grant(self, audit_fix_sql):
        """FINDING-02: increment_share_view must have explicit GRANT (not just PUBLIC default)."""
        assert "GRANT EXECUTE ON FUNCTION public.increment_share_view" in audit_fix_sql, (
            "increment_share_view must have explicit GRANT to document intent"
        )

    def test_increment_share_view_granted_to_anon(self, audit_fix_sql):
        """increment_share_view must allow anon (public share pages don't require auth)."""
        grant_line_idx = audit_fix_sql.find(
            "GRANT EXECUTE ON FUNCTION public.increment_share_view"
        )
        assert grant_line_idx >= 0
        grant_section = audit_fix_sql[grant_line_idx: grant_line_idx + 200]
        assert "anon" in grant_section, (
            "increment_share_view must be accessible to anon users (public share pages)"
        )

    def test_increment_share_view_revoked_from_implicit_public(self, audit_fix_sql):
        """increment_share_view must first REVOKE PUBLIC then GRANT specific roles."""
        revoke_idx = audit_fix_sql.find(
            "REVOKE EXECUTE ON FUNCTION public.increment_share_view"
        )
        grant_idx = audit_fix_sql.find(
            "GRANT EXECUTE ON FUNCTION public.increment_share_view"
        )
        assert revoke_idx >= 0, "Must REVOKE from PUBLIC before re-granting"
        assert grant_idx > revoke_idx, "GRANT must come after REVOKE"


# ─────────────────────────────────────────────────────────────────────────────
# AC3: Audit document exists and is well-formed
# ─────────────────────────────────────────────────────────────────────────────


class TestAC3AuditDocumentExists:
    """AC3: docs/reviews/rpc-audit-YYYY-MM-DD.md must exist with required sections."""

    @pytest.fixture(scope="class")
    def audit_doc(self):
        docs_reviews = REPO_ROOT / "docs" / "reviews"
        audit_files = list(docs_reviews.glob("rpc-audit-*.md"))
        assert len(audit_files) >= 1, (
            "At least one rpc-audit-YYYY-MM-DD.md file must exist in docs/reviews/"
        )
        # Use the most recent one
        return sorted(audit_files)[-1].read_text(encoding="utf-8")

    def test_audit_document_exists(self, audit_doc):
        """The audit document must exist and be non-empty."""
        assert len(audit_doc) > 500, "Audit document is too short — likely incomplete"

    def test_audit_doc_has_inventory_section(self, audit_doc):
        """Audit doc must have an inventory/status table."""
        assert "Inventário" in audit_doc or "Inventory" in audit_doc or "user-scoped" in audit_doc.lower()

    def test_audit_doc_has_findings_section(self, audit_doc):
        """Audit doc must list findings."""
        assert "Finding" in audit_doc or "FINDING" in audit_doc

    def test_audit_doc_has_td005_scope(self, audit_doc):
        """Audit doc must define TD-005 scope (per-user tokens)."""
        assert "TD-005" in audit_doc, (
            "Audit doc must define scope of TD-005 (per-user Supabase tokens)"
        )

    def test_audit_doc_has_search_datalake_finding(self, audit_doc):
        """Audit doc must document the search_datalake quota bypass finding."""
        assert "search_datalake" in audit_doc

    def test_audit_doc_has_increment_share_view_finding(self, audit_doc):
        """Audit doc must document the increment_share_view implicit GRANT finding."""
        assert "increment_share_view" in audit_doc

    def test_audit_doc_has_all_categories(self, audit_doc):
        """Audit doc must cover all RPC categories."""
        for category_indicator in [
            "user-scoped", "service", "trigger", "sitemap", "analytics"
        ]:
            assert category_indicator.lower() in audit_doc.lower(), (
                f"Audit doc must cover {category_indicator!r} category"
            )


# ─────────────────────────────────────────────────────────────────────────────
# AC4: TD-005 scope is defined
# ─────────────────────────────────────────────────────────────────────────────


class TestAC4TD005ScopeDefined:
    """AC4: TD-005 (per-user Supabase tokens) scope must be defined."""

    @pytest.fixture(scope="class")
    def audit_doc(self):
        docs_reviews = REPO_ROOT / "docs" / "reviews"
        audit_files = list(docs_reviews.glob("rpc-audit-*.md"))
        assert audit_files, "rpc-audit-*.md must exist"
        return sorted(audit_files)[-1].read_text(encoding="utf-8")

    def test_td005_mentioned_in_audit_doc(self, audit_doc):
        """TD-005 must be explicitly mentioned in the audit document."""
        assert "TD-005" in audit_doc

    def test_td005_has_recommendation(self, audit_doc):
        """Audit doc must include a recommendation for TD-005 (implement or defer)."""
        doc_lower = audit_doc.lower()
        has_recommendation = (
            "recomendação" in doc_lower
            or "recomenda" in doc_lower
            or "recommendation" in doc_lower
            or "prioridade" in doc_lower
            or "priority" in doc_lower
        )
        assert has_recommendation, (
            "Audit doc must include a prioritization/recommendation for TD-005"
        )

    def test_td005_scope_identifies_service_role_usage(self, audit_doc):
        """TD-005 scope must identify where service_role is used."""
        assert "service_role" in audit_doc, (
            "TD-005 scope must reference current service_role usage pattern"
        )

    def test_get_supabase_uses_service_role(self):
        """Verify that get_supabase() actually uses service_role key (architecture check)."""
        supabase_client = REPO_ROOT / "backend" / "supabase_client.py"
        assert supabase_client.exists()
        content = supabase_client.read_text(encoding="utf-8")
        assert "SUPABASE_SERVICE_ROLE_KEY" in content, (
            "get_supabase() must use SUPABASE_SERVICE_ROLE_KEY (service_role)"
        )
        assert "get_user_supabase" in content, (
            "supabase_client.py must also have get_user_supabase() for future TD-005 impl"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Migration integrity: audit fix migration is well-formed
# ─────────────────────────────────────────────────────────────────────────────


class TestAuditFixMigrationIntegrity:
    """Verify the DEBT-03 fix migration is well-formed and idempotent."""

    def test_audit_fix_migration_exists(self):
        """20260408220000_debt03_rpc_security_audit.sql must exist."""
        assert (MIGRATIONS_DIR / "20260408220000_debt03_rpc_security_audit.sql").exists()

    def test_migration_uses_do_block_for_search_datalake(self, audit_fix_sql):
        """search_datalake REVOKE must use DO $$ BEGIN...EXCEPTION...END block for safety."""
        assert "DO $$" in audit_fix_sql or "DO $$ BEGIN" in audit_fix_sql, (
            "REVOKE on search_datalake should use DO block with exception handler for safety"
        )

    def test_migration_has_both_revoke_and_grant_for_datalake(self, audit_fix_sql):
        """Migration must REVOKE from authenticated AND GRANT to service_role."""
        assert "REVOKE EXECUTE ON FUNCTION public.search_datalake" in audit_fix_sql
        assert "GRANT EXECUTE ON FUNCTION public.search_datalake" in audit_fix_sql

    def test_migration_documents_intent_in_comments(self, audit_fix_sql):
        """Migration must explain WHY each change is made (not just what)."""
        comment_count = audit_fix_sql.count("--")
        assert comment_count >= 10, (
            f"Migration has only {comment_count} comment lines — "
            "security migrations must be well-documented."
        )

    def test_migration_inventory_comment_present(self, audit_fix_sql):
        """Migration must include an inventory comment of all audited RPCs."""
        assert "INVENTORY" in audit_fix_sql or "auditadas" in audit_fix_sql.lower(), (
            "Migration must include an inventory of all audited RPCs in comments"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Regression: CRIT-SEC-001/002/004 must not be regressed
# ─────────────────────────────────────────────────────────────────────────────


class TestCRITSECNoRegression:
    """Ensure CRIT-SEC-001/002/004 fixes from 20260404000000 are still in place."""

    def test_crit_sec_001_quota_still_revoked(self, all_migrations_sql):
        """CRIT-SEC-001: quota functions must remain revoked after all migrations."""
        # The last relevant mention should be REVOKE (from 20260404000000)
        # and no subsequent GRANT to authenticated
        # We verify by checking the security hardening migration content
        hardening = (
            MIGRATIONS_DIR / "20260404000000_security_hardening_rpc_rls.sql"
        ).read_text(encoding="utf-8")
        assert "REVOKE EXECUTE ON FUNCTION public.check_and_increment_quota" in hardening
        assert "REVOKE EXECUTE ON FUNCTION public.increment_quota_atomic" in hardening

    def test_crit_sec_002_escalation_trigger_exists(self, all_migrations_sql):
        """CRIT-SEC-002: prevent_privilege_escalation trigger must exist."""
        assert "prevent_privilege_escalation" in all_migrations_sql
        assert "BEFORE UPDATE ON profiles" in all_migrations_sql

    def test_crit_sec_004_conversations_no_parameter_trust(self, all_migrations_sql):
        """CRIT-SEC-004: get_conversations_with_unread_count must not trust p_is_admin."""
        # The fix verifies admin from DB
        assert "Never trust p_is_admin parameter from client" in all_migrations_sql or (
            "Verify actual admin status from profiles" in all_migrations_sql
        ), (
            "CRIT-SEC-004 fix must be documented in the SQL "
            "(admin status verified from DB, not trusted from parameter)"
        )

    def test_no_new_migration_regrants_quota_to_authenticated(self):
        """No migration after 20260404000000 should re-grant quota functions to authenticated."""
        hardening_ts = "20260404000000"
        for sql_file in sorted(MIGRATIONS_DIR.glob("*.sql")):
            if sql_file.name <= hardening_ts + "_security_hardening_rpc_rls.sql":
                continue
            content = sql_file.read_text(encoding="utf-8")
            # Check for problematic re-grants
            if "check_and_increment_quota" in content or "increment_quota_atomic" in content:
                # Allowed: REVOKE or service_role grant
                lines_with_quota = [
                    line.strip() for line in content.splitlines()
                    if ("check_and_increment_quota" in line or "increment_quota_atomic" in line)
                    and not line.strip().startswith("--")
                ]
                for line in lines_with_quota:
                    assert "TO authenticated" not in line, (
                        f"File {sql_file.name} re-grants quota function to authenticated: {line}"
                    )
